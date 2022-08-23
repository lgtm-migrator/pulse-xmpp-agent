#!/usr/bin/python3
#
# (c) 2022 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
This plugin is called to update the agent system (application, security)
"""
import base64
import json
import os
import logging
from lib.utils import ipfromdns, AESCipher, subnetnetwork

try:
    from lib.localisation import Point

    errorlocalisation = False
except ModuleNotFoundError:
    errorlocalisation = True
from lib.plugins.xmpp import XmppMasterDatabase
from lib.plugins.admin import AdminMasterDatabase
from random import randint
import operator
import traceback
import configparser
import netaddr

try:
    from lib.stat import statcallplugin

    statfuncton = True
except BaseException:
    statfuncton = False

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25
plugin = {"VERSION": "1.0","NAME": "updatemachinesystem","TYPE": "substitute","FEATURE":"update_remote_machine",}  # fmt: skip


def action(objectxmpp, action, sessionid, data, msg, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, msg["from"]))
    logger.debug("=====================================================")
    try:
        compteurcallplugin = getattr(objectxmpp, "num_call%s" % action)
        if compteurcallplugin == 0:
            if statfuncton:
                objectxmpp.stat_updatemachinesystem = statcallplugin(
                    objectxmpp, plugin["NAME"]
                )
            read_conf_updatemachinesystem(objectxmpp)
        else:
            if statfuncton:
                objectxmpp.stat_updatemachinesystem.statutility()

    except Exception as e:
        logger.error("\n%s" % (traceback.format_exc()))


def msg_log(msg_header, hostname, user, result, objectxmpp, data):
    if (
        data["machine"].split(".")[0]
        in objectxmpp.updatemachinesystem_agent_showinfomachine
    ):
        logger.info(
            "%s Rule selects "
            "the relay server for machine "
            "%s user %s \n %s" % (msg_header, hostname, user, result)
        )
        pass


def read_conf_updatemachinesystem(objectxmpp):
    """
    It reads the configuration of the plugin
    The folder where the configuration MUST be is stored in the variable `objectxmpp.config.pathdirconffile`
    """
    conf_filename = plugin["NAME"] + ".ini"
    objectxmpp.pathfileconf = os.path.join(
        objectxmpp.config.pathdirconffile, conf_filename
    )
    if not os.path.isfile(objectxmpp.pathfileconf):
        logger.error(
            "The configuration for the plugin %s is missing. \n Please look into the folder %s"
            % (plugin["NAME"], objectxmpp.pathfileconf)
        )
        open(objectxmpp.pathfileconf, "a").close()
        message_config(plugin["NAME"], objectxmpp.pathfileconf)
        if statfuncton:
            objectxmpp.stat_updatemachinesystem.display_param_config(msg="DEFAULT")
        return False

    Config = configparser.ConfigParser()
    Config.read(objectxmpp.pathfileconf)
    if os.path.exists(objectxmpp.pathfileconf + ".local"):
        Config.read(objectxmpp.pathfileconf + ".local")
        # We read the parameters here. Do not forget to update the messages on the "message_config" configuration
        if statfuncton:
            objectxmpp.stat_updatemachinesystem.display_param_config("DEFAULT")
    return True


def message_config(nameplugin, pathfileconf):
    """
    It shows an error message.
    This is used when we hit a configuration error.
    """
    msg = (
        "The configuration for the plugin %s is missing. \n Please look into the folder %s"
        % (plugin["NAME"], objectxmpp.pathfileconf)
    )

    logger.error("%s" % msg)
