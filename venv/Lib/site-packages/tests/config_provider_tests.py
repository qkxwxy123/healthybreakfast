__author__ = 'bcullen'

import unittest
from app_config.app_config import AppConfig


class TestConfigProvider(unittest.TestCase):
    """
    Test ability to get config JSON from DynamoDB
    """

    @classmethod
    def setUpClass(self):
        self._config_provider = AppConfig('us-east-1', 'unit_test')

    # Test lookup code without integration to persistent storage
    def test_val_in_stubbed_dictionary(self):
        test_dict = {"username": "unittestuser"}
        self._config_provider._resources['unit_test_comp'] = test_dict

        val = self._config_provider['unit_test_comp']['username']
        self.assertEqual(val, 'unittestuser')

    def test_env_doesnt_exist(self):
        default_config_provider = AppConfig('us-east-1', 'foo-env-doesnt-exist')
        username = default_config_provider['unit_test_comp']['username']
        self.assertEqual(username, 'testuser')
        password = default_config_provider['unit_test_comp']['password']
        self.assertEqual(password, 'testpass')

    def test_env_override(self):
        username = self._config_provider['unit_test_comp']['username']
        self.assertEqual(username, 'testuser')
        password = self._config_provider['unit_test_comp']['password']
        self.assertEqual(password, 'envtestpass')

    def helper_test_resource_not_found(self):
        return self._config_provider['foo-doesnt-exist']['username']

    def test_resource_not_found(self):
        self.assertRaises(KeyError, self.helper_test_resource_not_found)

    def helper_test_attribute_not_found(self):
        return self._config_provider['unit_test_comp']['bar-doesnt-exist']

    def test_attribute_not_found(self):
        self.assertRaises(KeyError, self.helper_test_attribute_not_found)

    def test_creation_with_bad_env_name(self):
        c = AppConfig('us-east-1', "foo_barrr")
        self.assertEqual(c["unit_test_comp"]["password"], "testpass")

    def test_creation_with_good_env_name(self):
        c = AppConfig('us-east-1', "unit_test")
        self.assertEqual(c["unit_test_comp"]["password"], "envtestpass")

    def tearDown(self):
        pass


def get_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestConfigProvider)
