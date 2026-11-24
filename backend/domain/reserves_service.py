from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.airslots_model import airslots
from domain.battery_logs_model import battery_logs
from domain.reserves_model import reserves
from domain.switchcards_model import switchcards

SEALED = '已封存'
SETTLED = '已结算'
UNVERIFIABLE = '无法核对'


def target_hour(slot):
    """次日同一钟点在两日读数中的整点。"""
    return slot['hour'] + 24


def _reading_at(conn, meter, hour):
    return next((x for x in scan(conn, battery_logs) if x['meter'] == meter and x['hour'] == hour), None)


def forecast_wh(conn, user, data):
    slot = get(conn, airslots, data.airslot)
    target = target_hour(slot)
    rows = sorted([x for x in scan(conn, battery_logs)
                   if x['meter'] == data.meter and x['verified'] and x['hour'] < target],
                  key=lambda x: x['hour'])
    need(len(rows) >= 36 and all(y['hour'] - x['hour'] == 1 for x, y in zip(rows, rows[1:])),
         '要有目标小时前连续三十六小时审签读数')
    return submit(user, {'window': slot, 'rows': rows, 'clear': data.clear, 'meter': data.meter})


def save_reserve(conn, user, data):
    run = result(user, data.token)
    window = run['input']['window']
    meter = run['input'].get('meter')
    stats = run['result']
    # 与目标小时的晚到抄表互斥：先取得节目时段锁者先落账。
    slot = get(conn, airslots, window['code'], lock=True)
    need(slot['hour'] == window['hour'], '节目时间已变')
    need(bool(meter), '此计算缺少电表，不能封存')
    target = target_hour(slot)
    need(_reading_at(conn, meter, target) is None, '目标小时已有同表读数，不能封存')
    return insert(conn, reserves, code=data.code, airslot=slot['code'], plan_wh=stats['plan_wh'],
                  fallback='本地优先' if slot['offline'] else '受控中继', mae=stats['mae'], token=data.token,
                  meter=meter, hour=target, state=SEALED)


def settle(conn, reading):
    """审签通过后，按原电表、原小时结算已封存备案；封存量保留，仅记实耗与少备。"""
    for item in [x for x in scan(conn, reserves)
                 if x['state'] == SEALED and x['meter'] == reading['meter'] and x['hour'] == reading['hour']]:
        update(conn, reserves, item['code'], actual_wh=reading['load_wh'],
               short_wh=round(max(reading['load_wh'] - item['plan_wh'], 0.0), 3), state=SETTLED)


def visible(row):
    """缺原电表或原小时的旧备案无法核对。"""
    if row['meter'] is None or row['hour'] is None:
        return dict(row, state=UNVERIFIABLE)
    return row
