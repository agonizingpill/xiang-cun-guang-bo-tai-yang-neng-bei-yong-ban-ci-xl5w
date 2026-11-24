from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


reserves = Table('reserves', metadata,
    Column('code', String(64), primary_key=True),
    Column('airslot', String(160), ForeignKey('airslots.code'), nullable=False),
    Column('plan_wh', Float, nullable=False),
    Column('fallback', String(160), nullable=False),
    Column('mae', Float, nullable=False),
    Column('token', String(64), nullable=False, unique=True),
    # 封存时锁定的原电表与目标小时；旧备案可能缺少这两项。
    Column('meter', String(160), nullable=True),
    Column('hour', Integer, nullable=True),
    # 审签晚到实测后结算：实耗与少备电量，封存量 plan_wh 保持不变。
    Column('actual_wh', Float, nullable=True),
    Column('short_wh', Float, nullable=True),
    Column('state', String(160), nullable=True),
)
