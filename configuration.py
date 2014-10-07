"""
Configuration settings for the interface applications

See README.md for documentation and instructions.
"""

__author__ = 'Cosmo Harrigan'

from requests import *
import json
import csv
import pymongo
from os.path import expanduser
from time import sleep

try:
    import vagrant
    from fabric.api import task, run, settings
except:
    print "Optional Vagrant functionality not enabled; to enable, install " \
          "python-vagrant, fabric"

# Configure the OpenCog REST API client
IP_ADDRESS = '127.0.0.1'
PORT = '5000'
uri = 'http://' + IP_ADDRESS + ':' + PORT + '/api/v1.1/'
headers = {'content-type': 'application/json'}

# If you are running OpenCog in a Vagrant VM and running the Python Client API
# on the host machine, then set the following parameter 'USE_VAGRANT' to True
# and specify the ID of your Vagrant VM
USE_VAGRANT = True
VAGRANT_ID = "cb9fa8c"

# Configure the path of the OpenCog source folder relative to the user's
# home directory, including parameters to allow automatic bootstrapping of the
# CogServer
OPENCOG_SOURCE_FOLDER = expanduser("~") + "/opencog/opencog/"
OPENCOG_SUBFOLDER = expanduser("~") + '/opencog/build'
OPENCOG_INIT_DELAY = 5
OPENCOG_RESTAPI_START = 'echo "restapi.Start" | nc localhost 17001'

VAGRANT_PREFIX = "vagrant ssh " + VAGRANT_ID + " -c "
if not USE_VAGRANT:
    OPENCOG_COGSERVER_START = './opencog/server/cogserver'
    OPENCOG_COGSERVER_STOP = 'pkill cogserver'
else:
    OPENCOG_COGSERVER_START = "cd ~/opencog/build && ./opencog/server/cogserver"
    OPENCOG_COGSERVER_STOP = VAGRANT_PREFIX + """'pkill cogserver'"""

# Configure MongoDB parameters
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017"
MONGODB_DATABASE = 'attention-timeseries'


# Allows bash commands to be sent to a specific Vagrant VM
@task
def run_vagrant_command(machine_name, command):
    v = vagrant.Vagrant()
    with settings(host_string=v.user_hostname_port(vm_name=machine_name),
                  key_filename=v.keyfile(vm_name=machine_name),
                  disable_known_hosts=True):
        run(command)
