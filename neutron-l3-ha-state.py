#!/usr/bin/env python
#
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Author: Sylvain Afchain <sylvain.afchain@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import eventlet
import socket
import sys

from oslo.config import cfg

from neutron.common import config as common_config
from neutron.common import rpc as n_rpc
from neutron.common import topics
from neutron import context as n_context
from neutron.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class L3HAPluginApi(n_rpc.RpcProxy):
    """API for plugin to notify L3 agent."""

    BASE_RPC_API_VERSION = '1.2'

    def __init__(self, host, topic=topics.L3PLUGIN):
        super(L3HAPluginApi, self).__init__(
            topic=topic, default_version=self.BASE_RPC_API_VERSION)
        self.host = host

    def update_router_state(self, context, router_id, state):
        return self.call(context,
                         self.make_msg('update_router_state', host=self.host,
                                       router_id=router_id, state=state),
                         topic=self.topic)


def main(router_id, state):
    """Handles HA status changes."""
    LOG.debug("Starting....")
    eventlet.monkey_patch()

    l3_plugin_api = L3HAPluginApi(socket.gethostname())
    l3_plugin_api.update_router_state(
        n_context.get_admin_context_without_session(), router_id, state)


if __name__ == "__main__":
    product_name = "neutron-l3-ha-state"

    cfg.CONF.register_cli_opt(cfg.StrOpt('ha_state', metavar='state',
                                         help='the new current state',
                                         positional=True,
                                         required=True))

    cfg.CONF.register_cli_opt(cfg.StrOpt('router_id', metavar='router_id',
                                         help='id of the router',
                                         positional=True,
                                         required=True))
    common_config.init(sys.argv[1:])
    logging.setup(product_name)
    main(cfg.CONF.router_id, cfg.CONF.ha_state)
