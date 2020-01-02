# Copyright 2020 GRNET SA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function
from collections import OrderedDict

from unittest import mock

import charmhelpers

import charm.openstack.watcher as watcher

import charms_openstack.test_utils as test_utils


class Helper(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()
        self.patch_release(watcher.WatcherCharm.release)


class TestWatcherCharmConfigProperties(Helper):
    def test_planner_weights(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = [
            'weight',
            '{"weights": "change_node_power_state:9,'
            'change_nova_service_state:50"}']
        conf_dict = OrderedDict()
        conf_dict['weights'] = \
            'change_node_power_state:9,change_nova_service_state:50'
        self.config_flags_parser.return_value = conf_dict

        self.assertEqual(
            watcher.planner_weights(cls),
            'change_node_power_state:9,change_nova_service_state:50')

    def test_planner_weights_invalid(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch('charm.openstack.watcher.WARNING', 'WARNING')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = ['weight', '{}']
        self.config_flags_parser.return_value = OrderedDict()

        self.assertEqual(watcher.planner_weights(cls), None)
        self.log.assert_called_once_with(
            'Provided planner-config dictionary does not contain '
            'key weights - ignoring', level=self.WARNING)

    def test_planner_parallelization(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = [
            'weight',
            '{"parallelization": "change_node_power_state:9,'
            'change_nova_service_state:50"}']
        conf_dict = OrderedDict()
        conf_dict['parallelization'] = \
            'change_node_power_state:9,change_nova_service_state:50'
        self.config_flags_parser.return_value = conf_dict

        self.assertEqual(
            watcher.planner_parallelization(cls),
            'change_node_power_state:9,change_nova_service_state:50')

    def test_planner_parallelization_invalid(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch('charm.openstack.watcher.WARNING', 'WARNING')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = ['weight', '{}']
        self.config_flags_parser.return_value = OrderedDict()

        self.assertEqual(watcher.planner_parallelization(cls), None)
        self.log.assert_called_once_with(
            'Provided planner-config dictionary does not contain '
            'key parallelization - ignoring', level=self.WARNING)

    def test_planner_check_optimize_metadata(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = [
            'basic', '{"check_optimize_metadata": "true"}']
        conf_dict = OrderedDict()
        conf_dict['check_optimize_metadata'] = 'true'
        self.config_flags_parser.return_value = conf_dict

        self.assertEqual(
            watcher.planner_check_optimize_metadata(cls), 'true')

    def test_planner_check_optimize_metadata_invalid(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch('charm.openstack.watcher.WARNING', 'WARNING')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = ['basic', '{}']
        self.config_flags_parser.return_value = OrderedDict()

        self.assertEqual(watcher.planner_check_optimize_metadata(cls), None)
        self.log.assert_called_once_with(
            'Provided planner-config dictionary does not contain '
            'key check_optimize_metadata - ignoring', level=self.WARNING)

    def test_planner_ex_pools(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = [
            'storage_capacity_balance', '{"ex_pools": "local_vstorage"}']
        conf_dict = OrderedDict()
        conf_dict['ex_pools'] = 'local_vstorage'
        self.config_flags_parser.return_value = conf_dict

        self.assertEqual(
            watcher.planner_ex_pools(cls), 'local_vstorage')

    def test_planner_ex_pools_invalid(self):
        cls = mock.MagicMock()
        self.patch('charm.openstack.watcher.config', 'config')
        self.patch('charm.openstack.watcher.log', 'log')
        self.patch('charm.openstack.watcher.WARNING', 'WARNING')
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config.side_effect = ['storage_capacity_balance', '{}']
        self.config_flags_parser.return_value = OrderedDict()

        self.assertEqual(watcher.planner_ex_pools(cls), None)
        self.log.assert_called_once_with(
            'Provided planner-config dictionary does not contain key ex_pools '
            '- ignoring', level=self.WARNING)


class TestWatcherCharm(Helper):
    def _patch_config_and_charm(self, config):
        self.patch_object(charmhelpers.core.hookenv, 'config')

        def cf(key=None):
            if key is not None:
                return config[key]
            return config

        self.config.side_effect = cf
        c = watcher.WatcherCharm()
        return c

    def _patch_get_adapter(self, c):
        self.patch_object(c, 'get_adapter')

        def _helper(x):
            self.var = x
            return self.out

        self.get_adapter.side_effect = _helper

    def test_get_amqp_credentials(self):
        c = watcher.WatcherCharm()
        result = c.get_amqp_credentials()

        self.assertEqual(result, ('watcher', 'openstack'))

    def test_get_database_setup(self):
        c = watcher.WatcherCharm()
        result = c.get_database_setup()

        self.assertEqual(result, [{'database': 'watcher',
                                   'username': 'watcher'}])

    def test_custom_assess_status_check1(self):
        config = {
            'datasources': 'gnocchi',
            'planner': 'weight',
            'planner-config': '{"weights": "42", "parallelization": "42"}'
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        conf_dict = OrderedDict()
        conf_dict['weights'] = '42'
        conf_dict['parallelization'] = '42'
        self.config_flags_parser.return_value = conf_dict

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(c.options.planner, config['planner'])
        self.assertEqual(c.options.planner_config, config['planner-config'])
        self.assertEqual(c.custom_assess_status_check(), (None, None))

    def test_custom_assess_status_check2(self):
        config = {
            'datasources': 'gnocchi',
            'planner': 'invalid',
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(c.options.planner, config['planner'])
        self.assertEqual(
            c.custom_assess_status_check(),
            ('blocked',
             'Invalid planner: {}. Available options are: '
             'weights, workload_stabilization, basic, '
             'storage_capacity_balance'.format(config['planner'])))

    def test_custom_assess_status_check3(self):
        config = {
            'datasources': 'gnocchi',
            'planner': 'basic',
            'planner-config': 'invalid'
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)
        self.patch(
            'charm.openstack.watcher.config_flags_parser',
            'config_flags_parser')
        self.config_flags_parser.return_value = OrderedDict()

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(c.options.planner, config['planner'])
        self.assertEqual(c.options.planner_config, config['planner-config'])
        self.assertEqual(
            c.custom_assess_status_check(),
            ('blocked',
             'Provided planner {} must contain only the following '
             'configuration attributes: check_optimize_metadata'.format(
                 config['planner'])))

    def test_custom_assess_status_check4(self):
        config = {
            'datasources': None,
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(
            c.custom_assess_status_check(),
            ('blocked',
             'datasources not set'))

    def test_custom_assess_status_check5(self):
        config = {
            'datasources': 'invalid',
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(
            c.custom_assess_status_check(),
            ('blocked',
             'Provided datasources {} does not contain valid options'.format(
                 config['datasources'])))

    def test_custom_assess_status_check6(self):
        config = {
            'datasources': 'grafana',
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)
        self.patch_object(c, 'grafana_configuration_complete')
        self.grafana_configuration_complete.return_value = False

        self.assertEqual(c.options.datasources, config['datasources'])
        self.assertEqual(
            c.custom_assess_status_check(),
            ('blocked',
             'grafana datasource requires all grafana related options to be '
             'set'))

    def test_grafana_configuration_complete(self):
        config = {
            'grafana-auth-token': 1,
            'grafana-base-url': 2,
            'grafana-project-id-map': 3,
            'grafana-database-map': 4,
            'grafana-attribute-map': 5,
            'grafana-translator-map': 6,
            'grafana-query-map': 7,
            'grafana-retention-periods': 8,
        }
        c = self._patch_config_and_charm(config)
        self._patch_get_adapter(c)

        self.assertEqual(c.options.grafana_auth_token, 1)
        self.assertEqual(c.options.grafana_base_url, 2)
        self.assertEqual(c.options.grafana_project_id_map, 3)
        self.assertEqual(c.options.grafana_database_map, 4)
        self.assertEqual(c.options.grafana_attribute_map, 5)
        self.assertEqual(c.options.grafana_translator_map, 6)
        self.assertEqual(c.options.grafana_query_map, 7)
        self.assertEqual(c.options.grafana_retention_periods, 8)
        self.assertEqual(c.grafana_configuration_complete(), True)
