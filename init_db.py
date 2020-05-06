from sqlalchemy import create_engine, MetaData

from simple_api_billing.settings import config as main_config, config_test
from simple_api_billing.db import account, invoice


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='localhost', port=5432
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG = main_config
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)

TEST_CONFIG = config_test
TEST_DB_URL = DSN.format(**TEST_CONFIG['postgres'])
test_engine = create_engine(TEST_DB_URL)


def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine=test_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[account, invoice])


def sample_data(engine=test_engine):
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


def drop_tables(engine=test_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[account, invoice])


if __name__ == '__main__':
    db_url = DSN.format(**main_config['postgres'])
    # engine = create_engine(db_url)

    create_tables(user_engine)
    sample_data(user_engine)
