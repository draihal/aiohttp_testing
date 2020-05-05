from sqlalchemy import create_engine, MetaData

from simple_api_billing.settings import config
from simple_api_billing.db import account, invoice


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[account, invoice])


def sample_data(engine):
    conn = engine.connect()
    conn.execute(account.insert(), [
        {'currency': 'USD',
         'overdraft': True,
         'balance': 10.05}
    ])
    conn.execute(account.insert(), [
        {'currency': 'EUR',
         'overdraft': False,
         'balance': 10000.05}
    ])
    conn.execute(account.insert(), [
        {'currency': 'RUB',
         'overdraft': False,
         'balance': 100000.05}
    ])
    conn.execute(invoice.insert(), [
        {'account_id_from': 2, 'account_id_to': 1, 'amount': 10.05},
        {'account_id_from': 2, 'account_id_to': 1, 'amount': 10},
        {'account_id_from': 1, 'account_id_to': 2, 'amount': 10.05},
    ])
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
