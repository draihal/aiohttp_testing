import pytest
import pathlib

from simple_api_billing.main import init_app
from simple_api_billing.settings import get_config
from init_db import (
    setup_db,
    teardown_db,
    create_tables,
    sample_data,
    drop_tables
)

BASE_DIR = pathlib.Path(__file__).parent.parent
TEST_CONFIG_PATH = BASE_DIR / 'config' / 'api_billing_test.yaml'


@pytest.fixture
async def cli(loop, test_client, db):
    app = await init_app()
    return await test_client(app)


@pytest.fixture(scope='module')
def db():
    test_config = get_config(TEST_CONFIG_PATH)

    setup_db(test_config['postgres'])
    yield
    teardown_db(test_config['postgres'])


@pytest.fixture
def tables_and_data():
    create_tables()
    sample_data()
    yield
    drop_tables()


async def test_get_exist_account(cli):
    resp = await cli.get('/account?id=1')
    assert resp.status == 200


async def test_get_account_wrong_arg(cli):
    resp = await cli.get('/account?id=vfnjgcf')
    assert resp.status == 400


async def test_not_exist_account(cli):
    resp = await cli.get('/account?id=100')
    assert resp.status == 404
    assert 'Not found.' in await resp.text()


async def test_delete_account(cli):
    resp = await cli.delete('/account?id=1')
    assert resp.status == 405


async def test_create_account(cli):
    resp = await cli.post('/account?currency=USD&overdraft=False')
    assert resp.status == 201


async def test_create_account_wrong_args(cli):
    resp = await cli.post('/account?currency=BYR&overdraft=12')
    assert resp.status == 400


async def test_create_invoice(cli):
    resp = await cli.post('/invoice?account_id_from=3&account_id_to=2&amount=10')
    assert resp.status == 201


async def test_create_invoice_wrong_args(cli):
    resp = await cli.post('/invoice?account_id_from=dfht&account_id_to=2&amount=10')
    assert resp.status == 400


async def test_create_invoice_wrong_amount(cli):
    resp = await cli.post('/invoice?account_id_from=2&account_id_to=1&amount=1000000000000000')
    assert resp.status == 403
    assert 'Not enough balance.' in await resp.text()


async def test_create_invoice_not_exist_account(cli):
    resp = await cli.post('/invoice?account_id_from=9999999&account_id_to=2&amount=10')
    assert resp.status == 404
    assert 'Not found this accounts.' in await resp.text()


async def test_invoice_wrong_method(cli):
    resp = await cli.get('/invoice?account_id_from=9999999&account_id_to=2&amount=10')
    assert resp.status == 405
