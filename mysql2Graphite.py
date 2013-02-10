#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2013:
#    Olivier Hanesse, olivier.hanesse@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import MySQLdb
import datetime
import time
import cPickle
import struct
import argparse
import logging
from socket import socket
from mysql2GraphiteConfig import config, carbon_server, carbon_port, loglevel


def main(mysql_server, mysql_user, mysql_password, carbon_server):

    # Init logger
    logger = logging.getLogger("mysql2graphite")
    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    fmtr = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(fmtr)
    logger.addHandler(ch)

    # Connection to Mysql and Carbon server
    try:
        logger.debug("Try to open a MySQL connection to %s" % mysql_server)
        con_mysql = MySQLdb.connect(host=mysql_server,
                                    user=mysql_user,
                                    passwd=mysql_password)
    except MySQLdb.Error, e:
        logger.error("MySQL Module: Error %d: %s" % (e.args[0], e.args[1]))
        exit(2)
    cursor = con_mysql.cursor(MySQLdb.cursors.DictCursor)
    logger.debug("Connection to Mysql successful")

    logger.debug("Try to open a Carbon  connection to %s" % carbon_server)
    con_carbon = socket()
    try:
        con_carbon.connect((carbon_server, int(carbon_port)))
    except IOError:
        logger.error("Error connecting to carbon server %s" % carbon_server)
        exit(2)
    logger.debug("Connection to Carbon successful")

    # Mysql and Carbon connection are OK
    data_t_s = []
    result_set = {}

    for r in config:
        logger.debug("Launching %s " % r['request'])

        try:
            cursor.execute(r['request'])
            result_set = cursor.fetchall()
        except MySQLdb.Error, e:
            logger.error("MySQL Module: Error %d: %s" % (e.args[0], e.args[1]))

        time_s = time.time()
        for row in result_set:
            for v in r['value']:
                if isinstance(r['key'], list):
                    metricName = 'mysql.' + mysql_server + '.' + '.'.join(row[i] for i in r['key']) + '.' + v
                else:
                    metricName = 'mysql.' + mysql_server + '.' + r['key'] + '.' + v
                # [(path, (timestamp, value)), ...]
                data_t_s.append(("%s" % (metricName), ("%d" % time_s, "%s" % str(row[v]))))

    cursor.close()
    con_mysql.close()

    logger.debug("Sending data to graphite %s" % data_t_s)
    # Format the data
    payload = cPickle.dumps(data_t_s)
    header = struct.pack("!L", len(payload))
    packet = header + payload
    # Fire !
    con_carbon.sendall(packet)
    print("OK %s lines have been sent to Graphite" % len(data_t_s))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", dest='mysql_server',
                        default='localhost',
                        help="Mysql Server to query.")
    parser.add_argument("-u", "--user", dest='mysql_user',
                      default='mysql',
                      help="User to log in")
    parser.add_argument("-p", "--password", dest='mysql_password',
                      default='mysql',
                      help="User password")
    parser.add_argument("-g", "--graphite", dest='carbon_server',
                      default=carbon_server,
                      help="Graphite Carbon Server")

    args = parser.parse_args()

    main(**vars(args))
