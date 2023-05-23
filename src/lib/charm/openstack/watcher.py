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

import collections

import charms_openstack.adapters as openstack_adapters
import charms_openstack.charm as openstack_charm
import charms_openstack.ip as os_ip

from charmhelpers.contrib.openstack.utils import config_flags_parser
from charmhelpers.core.hookenv import (
    config,
    log,
    WARNING
)

WATCHER_CONF = '/etc/watcher/watcher.conf'
WATCHER_WSGI_CONF = '/etc/apache2/sites-available/watcher-api.conf'

openstack_charm.use_defaults('charm.default-select-release')


@openstack_adapters.config_property
def planner_weights(cls):
    conf = config('planner')
    if conf in ['weight', 'workload_stabilization']:
        conf = config_flags_parser(config('planner-config'))
        weights = conf.get('weights', None)
        if not weights:
            log('Provided planner-config dictionary does not contain key '
                'weights - ignoring', level=WARNING)
        else:
            return weights


@openstack_adapters.config_property
def planner_parallelization(cls):
    conf = config('planner')
    if conf == 'weight':
        conf = config_flags_parser(config('planner-config'))
        parallelization = conf.get('parallelization', None)
        if not parallelization:
            log('Provided planner-config dictionary does not contain key '
                'parallelization - ignoring', level=WARNING)
        else:
            return parallelization


@openstack_adapters.config_property
def planner_check_optimize_metadata(cls):
    conf = config('planner')
    if conf == 'basic':
        conf = config_flags_parser(config('planner-config'))
        check_optimize_metadata = conf.get('check_optimize_metadata', None)
        if not check_optimize_metadata:
            log('Provided planner-config dictionary does not contain key '
                'check_optimize_metadata - ignoring', level=WARNING)
        else:
            return check_optimize_metadata


@openstack_adapters.config_property
def planner_ex_pools(cls):
    conf = config('planner')
    if conf == 'storage_capacity_balance':
        conf = config_flags_parser(config('planner-config'))
        ex_pools = conf.get('ex_pools', None)
        if not ex_pools:
            log('Provided planner-config dictionary does not contain key '
                'ex_pools - ignoring', level=WARNING)
        else:
            return ex_pools


class WatcherCharm(openstack_charm.HAOpenStackCharm):
    service_name = name = 'watcher'

    release = 'train'

    packages = [
        'watcher-common', 'watcher-api', 'watcher-decision-engine',
        'watcher-applier', 'python3-watcher', 'libapache2-mod-wsgi-py3',
        'python3-apt',  # NOTE: workaround for hacluster subordinate
    ]

    python_version = 3

    api_ports = {
        'watcher-api': {
            os_ip.PUBLIC: 9322,
            os_ip.ADMIN: 9322,
            os_ip.INTERNAL: 9322,
        }
    }

    group = 'watcher'
    service_type = 'watcher'
    default_service = 'watcher-api'
    services = ['watcher-api', 'watcher-decision-engine', 'watcher-applier']

    required_relations = ['shared-db', 'amqp', 'identity-service']

    restart_map = {
        WATCHER_CONF: services,
        WATCHER_WSGI_CONF: services,
    }

    ha_resources = ['vips', 'haproxy', 'dnsha']

    release_pkg = 'watcher-common'

    package_codenames = {
        'watcher-common': collections.OrderedDict([
            ('3', 'train'),
            ('4', 'ussuri'),
            ('5', 'victoria'),
        ]),
    }

    sync_cmd = ['watcher-db-manage', '--config-file', WATCHER_CONF, 'upgrade']

    def get_amqp_credentials(self):
        return 'watcher', 'openstack'

    def get_database_setup(self):
        return [
            dict(database='watcher',
                 username='watcher',)
        ]

    def grafana_configuration_complete(self):
        """Determine whether sufficient configuration has been provided
        via charm config options when Grafana datasource is chosen.
        :returns: boolean indicating whether configuration is complete
        """
        required_config = [
            self.options.grafana_auth_token,
            self.options.grafana_base_url,
            self.options.grafana_project_id_map,
            self.options.grafana_database_map,
            self.options.grafana_attribute_map,
            self.options.grafana_translator_map,
            self.options.grafana_query_map,
            self.options.grafana_retention_periods
        ]

        return all(required_config)

    def custom_assess_status_check(self):
        """Verify that the configuration provided is valid and thus the service
        is ready to go.  This will return blocked if the configuration is not
        valid for the service.
        :returns (status: string, message: string): the status, and message if
            there is a problem. Or (None, None) if there are no issues.
        """
        datasources = self.options.datasources
        if not datasources:
            return 'blocked', 'datasources not set'
        if not set(datasources.split(',')).issubset(
                ['gnocchi', 'ceilometer', 'grafana']):
            return ('blocked',
                    'Provided datasources {} does not contain valid options'
                    .format(datasources))
        if 'grafana' in datasources:
            if not self.grafana_configuration_complete():
                return ('blocked',
                        'grafana datasource requires all grafana related '
                        'options to be set')
        planner = self.options.planner
        if planner not in [
            'weight', 'workload_stabilization', 'basic',
                'storage_capacity_balance']:
            return ('blocked',
                    'Invalid planner: {}. Available options are: '
                    'weights, workload_stabilization, basic, '
                    'storage_capacity_balance'.format(planner))
        planner_config = config_flags_parser(self.options.planner_config)
        planner_config_values = {
            'weight': {'weights', 'parallelization'},
            'workload_stabilization': {'weights'},
            'basic': {'check_optimize_metadata'},
            'storage_capacity_balance': {'ex_pools'},
        }
        if planner_config.keys() != planner_config_values[planner]:
            return ('blocked',
                    'Provided planner {} must contain only the following '
                    'configuration attributes: {}'.format(
                        planner, ', '.join(planner_config_values[planner])))

        return None, None
