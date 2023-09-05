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

import charms.reactive as reactive

import charms_openstack.bus
import charms_openstack.charm

charms_openstack.bus.discover()


charms_openstack.charm.use_defaults(
    'charm.installed',
    'amqp.connected',
    'shared-db.connected',
    'identity-service.connected',
    'identity-service.available',
    'config.changed',
    'update-status',
    'upgrade-charm',
    'certificates.available',
)


@reactive.when_not('is-update-status-hook')
def auto_upgrade(*args):
    with charms_openstack.charm.provide_charm_instance() as watcher_charm:
        watcher_charm.upgrade_if_available(args)


@reactive.when('shared-db.available')
@reactive.when('identity-service.available')
@reactive.when('amqp.available')
def render_config(*args):
    with charms_openstack.charm.provide_charm_instance() as watcher_charm:
        watcher_charm.render_with_interfaces(args)
        watcher_charm.assess_status()
    reactive.set_state('config.rendered')


@reactive.when_not('is-update-status-hook')
@reactive.when_not('db.synced')
@reactive.when('config.rendered')
def init_db():
    """Run initial DB migrations when config is rendered."""
    with charms_openstack.charm.provide_charm_instance() as watcher_charm:
        watcher_charm.db_sync()
        watcher_charm.restart_all()
        reactive.set_state('db.synced')
        watcher_charm.assess_status()


@reactive.when_not('is-update-status-hook')
@reactive.when('ha.connected')
def cluster_connected(hacluster):
    """Configure HA resources in corosync"""
    with charms_openstack.charm.provide_charm_instance() as watcher_charm:
        watcher_charm.configure_ha_resources(hacluster)
        watcher_charm.assess_status()
