from datetime import datetime
import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, DateTime, Enum, Boolean, Numeric
)


meta = MetaData()


account = Table(
    'account', meta,

    Column('id', Integer, primary_key=True),
    Column('currency',
           Enum('RUB', 'EUR', 'USD', name='currency_choices'),
           nullable=False),
    Column('overdraft', Boolean, default=False, nullable=False),
    Column('balance', Numeric(10, 2), nullable=True, default=0),
    Column('create_date',
           DateTime, nullable=False,
           default=datetime.utcnow)
)

invoice = Table(
    'invoice', meta,

    Column('id', Integer, primary_key=True),
    Column('account_id_from',
           Integer,
           ForeignKey('account.id', ondelete='CASCADE')),
    Column('account_id_to',
           Integer,
           ForeignKey('account.id', ondelete='CASCADE')),
    Column('amount', Numeric(10, 2), nullable=True),
    Column('transfer_status', Boolean, default=False, nullable=False),
    Column('create_date',
           DateTime, nullable=False,
           default=datetime.utcnow)
)


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
