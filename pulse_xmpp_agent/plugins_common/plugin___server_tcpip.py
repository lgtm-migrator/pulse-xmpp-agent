# -*- coding: utf-8 -*-
#
# (c) 2016-2020 siveo, http://www.siveo.net
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
#
# plugin register machine dans presence table xmpp.
# file : plugin___server_tcpip.py
#
import base64
import traceback
import os
import logging
from slixmpp import jid
import re
import configparser

# this import will be used later
import time
import sys
import asyncio
import socket
import select
import threading
import ast
import json
import pickle

from lib.agentconffile import directoryconffile
from lib.utils import DateTimebytesEncoderjson, simplecommand

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "__server_tcpip", "TYPE": "all", "INFO" : "code" }# fmt: skip

def action(xmppobject, action):
    try:
        logger.debug("=====================================================")
        logger.debug("call plugin code %s " % (plugin))
        logger.debug("=====================================================")
        compteurcallplugin = getattr(xmppobject, "num_call%s" % action)

        if compteurcallplugin == 0:
            logger.debug("====================================")
            logger.debug("========== INITIALIZATION ==========")
            logger.debug("====================================")
            read_conf_server_tcpip_agent_machine(xmppobject)
            logger.debug("====================================")
            asyncio.run(run_server(xmppobject))
    except Exception as e:
        logger.error("Plugin load_TCIIP, we encountered the error %s" % str(e))
        logger.error("We obtained the backtrace %s" % traceback.format_exc())

def read_conf_server_tcpip_agent_machine(xmppobject):
    xmppobject.port_tcp_kiosk = 8765
    prefixe_agent = ""
    if xmppobject.config.agenttype in ["relayserver"]:
        prefixe_agent = "ars_"
        if "ars_local_port" in vars(xmppobject.config) and  xmppobject.config()["ars_local_port"] != None:
            xmppobject.port_tcp_kiosk = xmppobject.config.ars_local_port
            logger.warning("paraneter tcp_ip port in section [kiosk]/ars_local_port in relayconf.ini : %s" % xmppobject.port_tcp_kiosk)
    elif xmppobject.config.agenttype in ["machine"]:
        prefixe_agent = "am_"
        if "am_local_port" in vars(xmppobject.config) and  xmppobject.config()["am_local_port"] != None:
            xmppobject.port_tcp_kiosk = xmppobject.config.am_local_port
            logger.warning("paraneter tcp_ip port in section [kiosk]/am_local_port in agentconf.ini : %s" % xmppobject.port_tcp_kiosk)
    configfilename = os.path.join(directoryconffile(), prefixe_agent+plugin["NAME"] + ".ini")
    logger.info("optionel config file local for plugin___server_tcpip is : %s" % configfilename)
    if os.path.isfile(configfilename):
        logger.info("config file local %s exist" % configfilename)
        # lit la configuration
        Config = configparser.ConfigParser()
        Config.read(configfilename)
        if os.path.isfile(configfilename + ".local"):
            Config.read(configfilename + ".local")
            if Config.has_option("server_tcpip", "port_tcpip"):
                xmppobject.port_tcp_kiosk = Config.getint("server_tcpip", "port_tcpip")
                logger.warning("config local redefini paraneter tcp_ip port in section [server_tcpip]/port_tcpip")
    else:
        logger.warning("local file configuration %s of plugin %s no exist" % (configfilename, plugin["NAME"]))
    logger.warning("port_tcp_kiosk is %s " % xmppobject.port_tcp_kiosk)

def client_info(client, show_info=False):
    #logger.debug("id socket %s" % client.fd)
    addresslisten, portlisten = client.getsockname()
    adressrecept,  portrecept = client.getpeername()
    adressfamily = str(client.family)
    clienttype = str(client.type)
    proto = client.proto
    if show_info:
        logger.debug("socket Information")
        logger.debug("AddressFamily socket %s" % str(client.family))
        logger.debug("type STREAM socket %s" % str(client.type))
        logger.debug("proto socket %s" % client.proto)
        logger.debug("listen adress %s %s" % (addresslisten, portlisten))
        logger.debug("recept adress %s %s" % (adressrecept, portrecept))
    return {"adressfamily" : adressfamily,
            "typesocket" : clienttype,
            "proto" : proto,
            "adress_listen" : addresslisten,
            "port_listen" : portlisten,
            "adress_recept" : adressrecept,
            "port_recept" : portrecept,
        }

def _convert_string(data):
    """
        cettte fonction convertit data bytes recu sur la socket en 1 objet dict ou string
        data peut-etre:
          1 bytes representant 1 json string,
          1 bytes representant 1 pickle object
          1 bytes representant 1 yaml string
          1 bytes representant 1 string
    """
    if isinstance(data, (bytes)):
        try:
            requestdata =  pickle.loads(data)
            return requestdata
        except:
            try:
                data = data.decode('utf8', "ignore")
            except:
                return None
    if isinstance(data, (str)):
        try:
            # convertion sting
            requestdata = ast.literal_eval(data)
            if isinstance(requestdata, (list, dict, tuple, set)):
                return requestdata
        except:
            # error dans le format de l'object passer
            # on regarde si c'est 1 string json
            try:
                requestdata = json.loads(data)
                return requestdata
            except:
                # error dans json peut etre serialisation picle
                try:
                    requestdata = yaml.load(data, Loader=yaml.Loader)
                    return requestdata
                except:
                    return data
    return data

async def handle_client(client, xmppobject):
    loop = asyncio.get_event_loop()
    request = None
    try:
        infoclient = client_info(client, show_info = True)
        if infoclient["adress_recept"] != "127.0.0.1":
            logger.error("error inet_resource_not_found:\n"\
                "Only local client for client")
            return
        while request != '':
            # break pour clore la connexion du client connexion, suite a l'action de la requette.
            request = (await loop.sock_recv(client, 1048576))
            requestobj = _convert_string(request)

            if requestobj is None:
                break
            if isinstance(requestobj, (str)):
                testresult =  requestobj[0:4].lower()
                if requestobj == "" or \
                    requestobj == "quit_server_kiosk" or \
                        testresult == "quit" or \
                            testresult == "exit" or \
                                testresult == "end":
                    logger.warning("reception connexion end")
                    break
                else:
                    logger.warning("reception data : %s "\
                        "no action for string" % requestobj)
                    break
            if isinstance(requestobj, (dict)):
                try:
                    # creation action
                    codeerror, result = xmppobject.handle_client_connection(json.dumps(requestobj))
                    logger.warning("reception data : __%s__ __%s__" %(codeerror, result))

                    if not result:
                        await loop.sock_sendall(client,"aucun resultat".encode('utf-8'))
                    if isinstance(result, (list, dict, set, tuple)):
                        await loop.sock_sendall(client, json.dumps(result, cls=DateTimebytesEncoderjson, indent=4).encode('utf-8'))
                    elif isinstance(result, (str))
                        await loop.sock_sendall(client,result.encode('utf-8') )
                    elif isinstance(result, (bytes)):
                        await loop.sock_sendall(client,result)
                    else:
                        try:
                            strdata=str(result).encode('utf-8')
                            await loop.sock_sendall(client,result)
                        except Exception as e:
                            await loop.sock_sendall(client,str(e).encode('utf-8'))

                        logger.warning("type reception data %s" % type(result))
                    break # suivant type de connexion desire
                except Exception as e:
                    await loop.sock_sendall(client,str(e).encode('utf-8'))
                    break
    except Exception:
        logger.error("backtrace handle_client %s" % traceback.format_exc())
    logger.warning("handle_client : close")
    client.close()

async def run_server(xmppobject):
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        # --listening --numeric-hosts --tcp --program
        linux_command = 'netstat -lnt4p | grep python | grep ":%s"' % xmppobject.port_tcp_kiosk
        logger.warning("linux command : %s" % linux_command)
        result = simplecommand(linux_command)

        logger.warning("len :%s" %  len(result["result"]))
        if len(result["result"]) > 0:
            logger.warning("server tcp_ip kiosk exist localhost:%s" % xmppobject.port_tcp_kiosk)
            return
    elif sys.platform.startswith("win"):
        windows_command = 'netstat -aof -p TCP | findstr LISTENING | findstr ":%s"' % xmppobject.port_tcp_kiosk
        # verify process from pid tasklist /fi "PID eq 560"
        result = simplecommand(windows_command)
        if len(result["result"]) > 0:
            logger.warning("server tcp_ip kiosk exist localhost:%s" % xmppobject.port_tcp_kiosk)
            return
    else:
        logger.error("os system error %s" %  sys.platform)
        return
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('localhost', xmppobject.port_tcp_kiosk))
        server.listen(8)
    except Exception as e:
        logger.error("message error %s" % str(e))
        logger.error("backtrace handle_client %s" % traceback.format_exc())
        return
    server.setblocking(False)

    loop = asyncio.get_event_loop()

    while True:
        logger.warning("Start Server")
        client, client_address = await loop.sock_accept(server)
        loop.create_task(handle_client(client, xmppobject))
        logger.warning("fin dede")
