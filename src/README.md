# Overview

This charm provides the Watcher service for an OpenStack Cloud. It is comprised
of three different services. The API, the Decision Engine and the Applier. This
charm takes care of all three, bundled as a single application.

# Usage

The OpenStack Watcher charm requires a running OpenStack deployment and relation
with mysql database, rabbitmq-server and keystone identity service.

A simple deployment requires only four commands:

    juju deploy --series bionic --config openstack-origin=cloud:bionic-train watcher
    juju add-relation watcher mysql
    juju add-relation watcher rabbitmq-server
    juju add-relation watcher keystone

The charm also support High Availability by relating it to hacluster charm:

    juju deploy hacluster watcher-hacluster
    juju add-unit watcher
    juju set watcher vip=<VIP FOR ACCESS>
    juju add-relation watcher-hacluster watcher

# Bugs

Please report bugs on [GitHub](https://github.com/grnet/charm-watcher/issues).
For general questions please refer to the OpenStack [Charm Guide](https://docs.openstack.org/charm-guide/latest/).

# Configuration

The configuration options will be listed on the charm store, however If you're
making assumptions or opinionated decisions in the charm (like setting a default
administrator password), you should detail that here so the user knows how to
change it immediately, etc.

# Contact Information

Though this will be listed in the charm store itself don't assume a user will
know that, so include that information here:

## OpenStack Watcher

- [Watcher](https://wiki.openstack.org/wiki/Watcher)
- [Watcher Bugs](https://launchpad.net/watcher)
- Watcher IRC on freenode at #openstack-watcher
