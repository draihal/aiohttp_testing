import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / 'config' / 'api_billing.yaml'
config_path_test = BASE_DIR / 'config' / 'api_billing_test.yaml'


def get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


config = get_config(config_path)
config_test = get_config(config_path_test)
