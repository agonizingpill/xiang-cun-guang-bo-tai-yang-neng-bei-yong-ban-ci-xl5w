import logging
from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine, inspect, text

from core.config import DATABASE_URL

metadata = MetaData()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
log = logging.getLogger('uvicorn.error')

# 既有部署里 create_all 不会补列；这里幂等地补齐后续新增的可空字段。
LATE_COLUMNS = {
    'reserves': [('meter', 'VARCHAR(160)'), ('hour', 'INTEGER'),
                 ('actual_wh', 'FLOAT'), ('short_wh', 'FLOAT'), ('state', 'VARCHAR(160)')],
}


def ensure_schema():
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    for table, columns in LATE_COLUMNS.items():
        if table not in tables:
            continue
        present = {c['name'] for c in inspector.get_columns(table)}
        for name, sqltype in columns:
            if name in present:
                continue
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {name} {sqltype} NULL'))
            log.info('added column %s.%s', table, name)
    if 'battery_logs' in tables:
        names = {c['name'] for c in inspector.get_indexes('battery_logs')}
        if 'uq_battery_logs_meter_hour' not in names:
            try:
                with engine.begin() as conn:
                    conn.execute(text('CREATE UNIQUE INDEX uq_battery_logs_meter_hour '
                                      'ON battery_logs (meter, hour)'))
            except Exception:
                log.exception('could not add battery_logs meter/hour unique index')

@contextmanager
def transaction():
    with engine.begin() as conn:
        yield conn
