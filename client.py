#Requirements:
#   - requests
#   - psycopg2  (to pass to postgres)

import psycopg2
import requests
import re
import sys
import options
import argparse
from requests.auth import HTTPBasicAuth # For user authentication

def fetch_nodes(arguments):
    connection = psycopg2.connect(
                                  database = options.postgres_database,
                                  host     = options.postgres_host,
                                  port     = options.postgres_port,
                                  user     = options.postgres_user,
                                  password = options.postgres_password)

    cur = connection.cursor()
    nodes = []

    for arg in arguments:
        """ Finds any occurance of the string in postgres"""
        command = \
        'SELECT * FROM nodes WHERE lower(nodename) LIKE \'%{}%\''.format(arg)

        cur.execute(command)
        nodes += list(cur.fetchall())

    cur.close()
    connection.close()

    return nodes

def switch_light(nodes, state = None):
    # For now: IP Adress Hardcoded
    server_ip = options.LightBaseIP
    authentication = HTTPBasicAuth(options.http_user, options.http_pass)

    # creating regular expression search word
    find = re.compile('formatted="\w{2,3}"')

    """
    So, the nodes that are being brought back are in a list.
    The list is structured as follows:
        Nodes (list)
            - node (touple)
                - name      (string)
                - address   (string)
                - node type (string)
                - pnode     (string)
    """
    try:
        for node in nodes:
            # if state has a boolean value, then swith light according to the bool
            if (state != None):
                if (state == True):
                    power = 'DON'
                if (state == False):
                    power = 'DOF'
            # else, switch light according to it's current state
            else:
                # find the status of each node
                stat_url = 'http://'+ server_ip +'/rest/status/' + node[1]
                status = requests.get(stat_url, auth=authentication).text
                state = re.search(find, status).group()

                # switch from off to on; and vice versa
                if (state == 'formatted="On"'):    power = 'DOF'
                elif (state == 'formatted="Off"'): power = 'DON'

            # Get request to light's host
            url = 'http://'+ server_ip +'/rest/nodes/{0}/cmd/{1}'.format(node[1], power)
            req = requests.get(url, auth = authentication)

            # Print response
            print (node[0],': ', req)
    except TypeError:
        print('ERROR: Recieved Nothing...')

def parse_args():
    parser = argparse.ArgumentParser()
    """
        Current Arguments
        -s, --switch: to give IP of server that they are using
        -o, --on    : to turn on a list of lights [by name]
        -f, --off   : to turn off any light [by name]

        Future Arguments
        -ip,        : to switch ip listing
    """

    parser.add_argument('-s','--switch',
                        metavar='IP_Address',
                        nargs='*',
                        help='Automatically switch given light',
                        type=str)
    parser.add_argument('-ip',
                        metavar='IP_Address',
                        nargs='*',
                        help='Give IP of Server',
                        type=str)
    parser.add_argument('-o', '--on',
                        metavar='Node',
                        nargs='*',
                        help='List of Names to turn on',
                        type=str)
    parser.add_argument('-f', '--off',
                        metavar='Node',
                        nargs='*',
                        help='List of Names to turn off',
                        type=str)

    return parser.parse_args()

def main():
    args  = parse_args()
    state = None
    nodes = None

    try:
        if (args.switch != None) and (args.switch != []):
            nodes = fetch_nodes(args.switch)

        if (args.on  != None) and (args.on != []):
            nodes = fetch_nodes(args.on)
            state = True

        if (args.off != None) and (args.off != []):
            nodes = fetch_nodes(args.off)
            state = False
    except Exception as e:
        print ('ERROR! ', e)


    try:
        switch_light(nodes, state)
    except Exception as e:
        print (e)

if __name__ == "__main__":
    main()
