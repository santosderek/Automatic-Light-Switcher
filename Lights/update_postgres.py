#Requirements:
#   - requests
#   - xmltodict (for xml parsing)
#   - psycopg2  (to pass to postgres)

import xmltodict
import psycopg2
import requests
import options
from requests.auth import HTTPBasicAuth # For user authentication


""" Grabbing The XML Page With Correct User And Password """
def page(url = 'http://' + options.LightBaseIP + '/rest/nodes/'):
    authentication = HTTPBasicAuth(options.http_user, options.http_pass)
    return ( requests.get(url, auth=authentication) )

""" Paring The Request Into An Object To Use """
def xml(text = page().text):
    obj = xmltodict.parse(text)
    return ( obj )

""" Update Postgres With Data Collected """
#TODO: Fix Command Argument
def sendToPostgres(listOfNodes = xml()['nodes']['node']):
    """ Start Connection To Postgres Server """
    connection  = psycopg2.connect(
                          database = options.postgres_database,
                          host     = options.postgres_host,
                          port     = options.postgres_port,
                          user     = options.postgres_user,
                          password = options.postgres_password)

    cur = connection.cursor() # allows navigation through the database
    cur.execute('DELETE FROM nodes') #clear the table

    for node in listOfNodes:
        nodeName    = str(node['name'])
        address     = str(node['address'])
        nodeType    = str(node['type'])
        pnode       = str(node['pnode'])

        cur.execute("""INSERT INTO nodes (nodeName, address, nodeType, pnode)
                        VALUES (%s,%s,%s,%s );""", (nodeName, address, nodeType, pnode ))

    connection.commit()
    cur.close()
    connection.close()

if __name__ == "__main__":
    sendToPostgres()
