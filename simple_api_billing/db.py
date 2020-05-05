import enum
from datetime import datetime

from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, DateTime, Enum, Boolean, Numeric
)


class CurrencyChoicesEnum(enum.Enum):
    RUB = 'RUB'
    EUR = 'EUR'
    USD = 'USD'


meta = MetaData()


account = Table(
    'account', meta,

    Column('id', Integer, primary_key=True),
    Column('currency',
           Enum(CurrencyChoicesEnum),
           default=CurrencyChoicesEnum.RUB, nullable=False),
    Column('overdraft', Boolean, default=False, nullable=False),
    Column('balance', Numeric(10, 2), nullable=True),
    Column('create_date',
           DateTime, nullable=False,
           default=datetime.strftime(datetime.today(), "%b %d %Y"))
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
