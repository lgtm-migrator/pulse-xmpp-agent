# -*- coding: utf-8 -*-
#
# (c) 2020 siveo, http://www.siveo.net
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
# file : plugin_updatefusion.py

import sys
import os
from distutils.version import StrictVersion
import logging
import shutil
from lib import utils

BOOTSTRAP = '3.1.1'
JQUERY = '3.5.1'
JQUERYUI = '1.12.1'
DATATABLE = '1.10.21'

list_modules = ["bootstrap", "jquery", "jqueryui", "datatables"]

logger = logging.getLogger()

plugin = {"VERSION": "1.21", "NAME": "updatefileviewer", "TYPE": "machine"}


def action(xmppobject, action, sessionid, data, message, dataerreur):
    logger.debug("###################################################")
    logger.debug("call %s from %s" % (plugin, message['from']))
    logger.debug("###################################################")
    try:
        # Update if version is lower
        bootstrap_installed_version = checkbootstrapversion()
        if StrictVersion(bootstrap_installed_version) < StrictVersion(BOOTSTRAP):
            updatebootstrap(xmppobject)
    except Exception:
        pass

def fileviewer_path():
    if sys.platform.startswith('win'):
        destpath = os.path.join("c:\\", "Python27", "Lib",
                                "site-packages", "pulse_xmpp_agent", "lib",
                                 "ressources", "fileviewer")
    elif sys.platform.startswith('linux'):
        #FIXME: Do not hardcode python path
        destpath = "/usr/lib/python2.7/dist-packages/pulse_xmmp_agent/lib/ressources/fileviewer"
    elif sys.platform.startswith('darwin'):
        print "Not implemented yet"

    return destpath

def checkbootstrapversion():
    installed_path = fileviewer_path()
    bootstrap_version_file = os.path.join(installed_path, "bootstrap.version")

    if not os.path.isdir(installed_path) or not os.path.isfile(bootstrap_version_file):
        bootstrapversion = '0.1'
    else:
        bootstrapversion = file_get_contents(bootstrap_version_file).strip()

    return bootstrapversion

def get_version_file(deps_module):
    installed_path = fileviewer_path()

    if deps_module == "bootstrap":
        version_file = os.path.join(installed_path, "bootstrap.version")
    elif deps_module == "jquery":
        version_file = os.path.join(installed_path, "jquery.version")
    elif deps_module == "jqueryui":
        version_file = os.path.join(installed_path, "jqueryui.version")
    elif deps_module == "datatables":
        version_file = os.path.join(installed_path, "datatables.version")
    else:
        logger.error("The module %s is not supported" % deps_module)

    return version_file

def checkversion(deps_module):

    version_file = get_version_file(deps_module)
    installed_path = fileviewer_path()

    if not os.path.isdir(installed_path) or not os.path.isfile(version_file):
        module_version = '0.1'
    else:
        module_version = file_get_contents(version_file).strip()

    return module_version

def write_version_in_file(deps_module, version_module):
    version_file = get_version_file(deps_module)

    with open(version_file, "w") as filout:
        filout.write(version_module)

def updatebootstrap(xmppobject):
    logger.info("Updating Bootstrap to version %s" % BOOTSTRAP)

    installed_path = fileviewer_path()


    if not os.path.isdir(installed_path):
        os.makedirs(installed_path, 0o755)

    filename_css = 'bootstrap.css'
    filename_js = 'bootstrap.js'

    if sys.platform.startswith('win'):
        architecture = "win"
    elif sys.platform.startswith('linux'):
        architecture = "lin"
    elif sys.platform.startswith('darwin'):
        architecture = "mac"


    dl_url_css = 'http://%s/downloads/%s/downloads/%s' % (
        xmppobject.config.Server, architecture, filename_css)

    result_css, txtmsg_css = utils.downloadfile(dl_url_css).downloadurl()
    if result_css:
        # Download success
        logger.debug("%s" % txtmsg_css)
        # Run installer
        try:
            shutil.copyfile(filename_css, installed_path)
        except Exception as e:
            logger.error("Error while copying the file, with the error: %s" % e)
    else:
        # Download error
        logger.debug("%s" % txtmsg_css)

    dl_url_js = 'http://%s/downloads/%s/downloads/%s' % (
        xmppobject.config.Server, architecture, filename_js)

    result_js, txtmsg_js = utils.downloadfile(dl_url_js).downloadurl()
    if result_js:
        # Download success
        logger.debug("%s" % txtmsg_js)
        # Run installer
        try:
            shutil.copyfile(filename_js, installed_path)
        except Exception as e:
            logger.error("Error while copying the file, with the error: %s" % e)
    else:
        # Download error
        logger.error("%s" % txtmsg_js)

    write_version_in_file("bootstrap", BOOTSTRAP)

def updatejquery(xmppobject):
    logger.info("Updating JQuery to version %s" % JQUERY)

    installed_path = fileviewer_path()


    if not os.path.isdir(installed_path):
        os.makedirs(installed_path, 0o755)


    filename_js = 'jquery.js'

    if sys.platform.startswith('win'):
        architecture = "win"
    elif sys.platform.startswith('linux'):
        architecture = "lin"
    elif sys.platform.startswith('darwin'):
        architecture = "mac"


    dl_url_js = 'http://%s/downloads/%s/downloads/%s' % (
        xmppobject.config.Server, architecture, filename_js)

    result_js, txtmsg_js = utils.downloadfile(dl_url_js).downloadurl()
    if result_js:
        # Download success
        logger.debug("%s" % txtmsg_js)
        # Run installer
        try:
            shutil.copyfile(filename_js, installed_path)
        except Exception as e:
            logger.error("Error while copying the file, with the error: %s" % e)
    else:
        # Download error
        logger.error("%s" % txtmsg_js)

    write_version_in_file("jquery", JQUERY)

def updatejqueryui(xmppobject):
    logger.info("Updating JQuery UI to version %s" % JQUERY)

    installed_path = fileviewer_path()

    if not os.path.isdir(installed_path):
        os.makedirs(installed_path, 0o755)

    filename_js = 'query-ui.js'
    filename_css = 'query-ui.css'

    if sys.platform.startswith('win'):
        architecture = "win"
    elif sys.platform.startswith('linux'):
        architecture = "lin"
    elif sys.platform.startswith('darwin'):
        architecture = "mac"

    dl_url_css = 'http://%s/downloads/%s/downloads/%s' % (
        xmppobject.config.Server, architecture, filename_css)

    result_css, txtmsg_css = utils.downloadfile(dl_url_css).downloadurl()
    if result_css:
        # Download success
        logger.debug("%s" % txtmsg_css)
        # Run installer
        try:
            shutil.copyfile(filename_css, installed_path)
        except Exception as e:
            logger.error("Error while copying the file, with the error: %s" % e)

    else:
        # Download error
        logger.error("%s" % txtmsg_css)

    dl_url_js = 'http://%s/downloads/%s/downloads/%s' % (
        xmppobject.config.Server, architecture, filename_js)
    result_js, txtmsg_js = utils.downloadfile(dl_url_js).downloadurl()
    if result_js:
        # Download success
        logger.debug("%s" % txtmsg_js)
        # Run installer
        try:
            shutil.copyfile(filename_js, installed_path)
        except Exception as e:
            logger.error("Error while copying the file, with the error: %s" % e)
    else:
        # Download error
        logger.error("%s" % txtmsg_js)

    write_version_in_file("jqueryui", JQUERYUI)
