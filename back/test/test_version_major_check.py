import pytest

from flaskapp.mpa_analysis_tool import create_app
from dao.dao_base import DAOBaseClass

URL = 'http://localhost:5000'


@pytest.fixture
def api():
    dao = DAOBaseClass()
    dao.execute(
        '''
        update settings.information set value='1.0.0' where key='version'
        '''
    )

    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_version_check(api):
    dao = DAOBaseClass(table_name='settings.information')

    row = dao.fetch_one()

    print(row['value'])

    assert row['value'] == '0.0.1'