# Copyright (c) 2012 NTT DOCOMO, INC.
# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Manage hosts in the current zone.
"""

from nova import flags
from nova.openstack.common import log as logging
from nova.scheduler import host_manager


FLAGS = flags.FLAGS
LOG = logging.getLogger(__name__)


class BaremetalNodeState(host_manager.HostState):
    """Mutable and immutable information tracked for a host.
    This is an attempt to remove the ad-hoc data structures
    previously used and lock down access.
    """

    def update_from_compute_node(self, compute):
        """Update information about a host from its compute_node info."""
        LOG.debug(_("in Update from computei baremetal %(compute)s") %
                locals())
        all_ram_mb = compute['memory_mb']

        free_disk_mb = compute['free_disk_gb'] * 1024
        free_ram_mb = compute['free_ram_mb']

        self.free_ram_mb = free_ram_mb
        self.total_usable_ram_mb = all_ram_mb
        self.free_disk_mb = free_disk_mb
        self.vcpus_total = compute['vcpus']
        self.vcpus_used = compute['vcpus_used']

    def consume_from_instance(self, instance):
        self.free_ram_mb = 0
        self.free_disk_mb = 0
        self.vcpus_used = self.vcpus_total


def new_host_state(self, host, topic, capabilities=None, service=None,
                   nodename=None):
    """Returns an instance of BaremetalHostState or HostState according to
    capabilities. If 'baremetal_driver' is in capabilities, it returns an
    instance of BaremetalHostState. If not, returns an instance of HostState.
    """
    if capabilities is None:
        capabilities = {}
    cap = capabilities.get(topic, {})
    if bool(cap.get('baremetal_driver')):
        LOG.debug(_("in new_host_state baremetal %(nodename)s ,and cap is: %(cap)s") %
                locals())
        return BaremetalNodeState(host, topic, capabilities, service,
                                  nodename=nodename)
    else:
        LOG.debug(_("in else new_host_state baremetal %(nodename)s ,and cap is: %(cap)s") %
                locals())
        return host_manager.HostState(host, topic, capabilities, service,
                                      nodename=nodename)


class BaremetalHostManager(host_manager.HostManager):
    """Bare-Metal HostManager class."""

    # Override.
    # Yes, this is not a class, and it is OK
    host_state_cls = new_host_state

    def __init__(self):
        super(BaremetalHostManager, self).__init__()
