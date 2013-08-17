#!/usr/bin/env python
#
# Copyright 2012 Jose Cortez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""HTCondor cluster on Google Computer Engine (GCE) helper class

Use this class to:
- Start a simple condor custer, given the number of nodes
- Terminate all nodes in the cluster

Google's Getting Started example python code for was used as a starting
point for this class.
"""

__author__ = 'jose.cortez@gmail.com (Jose Cortez)'

import sys
from time import sleep
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.discovery import build
import argparse


CLIENT_SECRETS = 'client_secrets.json'
OAUTH2_STORAGE = 'oauth2.dat'
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'
PROJECT_ID = 'cool-plasma-234'
API_VERSION = 'v1beta15'
GCE_URL = 'https://www.googleapis.com/compute/%s/projects/' % (API_VERSION)
DEFAULT_ZONE = 'us-central1-a'

# New instance properties
DEFAULT_MACHINE_TYPE = 'n1-standard-1'
DEFAULT_IMAGE = 'debian'
DEFAULT_IMAGES = {
    'debian': 'debian-7-wheezy-v20130617',
}
DEFAULT_NETWORK = 'default'
DEFAULT_SERVICE_EMAIL = 'default'
DEFAULT_SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control',
                  'https://www.googleapis.com/auth/compute']

MASTER_IMAGE_NAME = 'masterv3'
NODE_IMAGE_NAME = 'nodev3'

MASTER_CONDOR_DEBCONF = 'master_00debconf'
NODE_CONDOR_DEBCONF = 'node_00debconf'

MASTER_INSTANCE_NAME = 'master'
NODE_INSTANCE_NAME = 'node'

CS_BUCKET = 'gce_condor'
STARTUP_SCRIPT = 'startup.sh'


class GceCondor(object):
    def __init__(self, auth_http, project_id):
        """Initialize the GceCondor object

            Args:
            auth_http: an authorized instance of Http
            project_id: the API console
        """

        self.service = build('compute', API_VERSION)
        self.auth_http = auth_http
        self.project_id = project_id
        self.project_url = '%s%s' % (GCE_URL, self.project_id)

    def start_cluster(self, node_count, from_image=False):
        """Start a GCE condor cluster given the number of nodes

        node_count: the number of nodes in the cluster. includes master
        from_image: build the cluster from image?  If False, the cluster is
            built from scratch, using the start_cluster-up script and debconf for config.
            If True, this will use MASTER_IMAGE_NAME and NODE_IMAGE_NAME. To use this
            functionality, you should first run this as False to build the master
            and node images, save them to your GCE project, and
            set MASTER_IMAGE_NAME and NODE_IMAGE_NAME to the name of the
            respective images.

        """

        # Construct URLs
        if not from_image:
            image_url = '%s%s/global/images/%s' % (
                GCE_URL, 'debian-cloud', DEFAULT_IMAGES['debian'])
            startup_script_url = 'gs://%s/%s' % (CS_BUCKET, STARTUP_SCRIPT)
        else:
            image_url = '%s%s/global/images/%s' % (
                GCE_URL, self.project_id, MASTER_IMAGE_NAME)
        machine_type_url = '%s/zones/%s/machineTypes/%s' % (
            self.project_url, DEFAULT_ZONE, DEFAULT_MACHINE_TYPE)
        network_url = '%s/global/networks/%s' % (self.project_url, DEFAULT_NETWORK)

        # Construct the master request body
        instance = {
            'name': MASTER_INSTANCE_NAME,
            'machineType': machine_type_url,
            'image': image_url,
            'networkInterfaces': [{
                                      'accessConfigs': [{
                                                            'type': 'ONE_TO_ONE_NAT',
                                                            'name': 'External NAT'
                                                        }],
                                      'network': network_url
                                  }],
            'serviceAccounts': [{
                                    'email': DEFAULT_SERVICE_EMAIL,
                                    'scopes': DEFAULT_SCOPES
                                }]
        }

        if not from_image:

            instance['metadata'] = [{
                                        'items': [{
                                                      'key': 'startup-script-url',
                                                      'value': startup_script_url
                                                  }, {
                                                      'key': 'cs-bucket',
                                                      'value': CS_BUCKET
                                                  }, {
                                                      'key': 'condor-debconf',
                                                      'value': MASTER_CONDOR_DEBCONF
                                                  }]
                                    }]

        # Create the master instance
        request = self.service.instances().insert(
            project=self.project_id, body=instance, zone=DEFAULT_ZONE)
        response = request.execute(self.auth_http)
        response_list = [response]
        response_names = {response['name']: MASTER_INSTANCE_NAME}

        if node_count > 1:
            if from_image:
                image_url = '%s%s/global/images/%s' % (
                    GCE_URL, self.project_id, NODE_IMAGE_NAME)

            instance['image'] = image_url
            if from_image:
                instance['metadata'] = []
            else:
                instance['metadata'] = [{
                                            'items': [{
                                                          'key': 'startup-script-url',
                                                          'value': startup_script_url
                                                      }, {
                                                          'key': 'cs-bucket',
                                                          'value': CS_BUCKET
                                                      }, {
                                                          'key': 'condor-debconf',
                                                          'value': NODE_CONDOR_DEBCONF
                                                      }]
                                        }]

            for i in range(1, node_count):
                node_name = NODE_INSTANCE_NAME + '00' + str(i)
                instance['name'] = node_name
                # Create the node instance
                request = self.service.instances().insert(
                    project=self.project_id, body=instance, zone=DEFAULT_ZONE)
                response = request.execute(self.auth_http)
                response_list.append(response)
                response_names[response['name']] = node_name

        self.__wait_for_all(response_list, response_names)

    def __wait_for_all(self, response_list, response_names):
        """Blocks until the operation status is done for all the operations.

        Args:
            response_list: the list of the operation responses to wait on
            response_names: a dictionary mapping the response id to an instance name
        """

        while len(response_list) > 0:
            for response in response_list[:]:
                response_name = response['name']
                # Identify if this is a per-zone resource
                if 'zone' in response:
                    zone_name = response['zone'].split('/')[-1]
                    request = self.service.zoneOperations().get(
                        project=self.project_id,
                        operation=response_name,
                        zone=zone_name)
                else:
                    request = self.service.globalOperations().get(
                        project=self.project_id, operation=response_name)
                status_response = request.execute(self.auth_http)
                if status_response:
                    status = status_response['status']
                if status == "DONE":
                    response_list.remove(response)
                else:
                    print "Waiting for instance ", response_names[response_name], \
                        ". Current status: ", status, ". Sleeping 3s."
            sleep(3)

    def delete_all_in_project(self):
        """Deletes all instances in the project.  This is a quick and dirty way to shutdown
            the cluster. Will need to be refined.
        """

        request = self.service.instances().list(project=self.project_id, filter=None,
                                                zone=DEFAULT_ZONE)
        response = request.execute(self.auth_http)

        if response and 'items' in response:
            instances = response['items']
            response_list = []
            response_names = {}
            for instance in instances:
                # Delete an Instance
                request = self.service.instances().delete(
                    project=self.project_id, instance=instance['name'], zone=DEFAULT_ZONE)
                response = request.execute(self.auth_http)
                response_list.append(response)
                response_names[response['name']] = instance['name']

            self.__wait_for_all(response_list, response_names)
        else:
            print 'No instances in project.'


    def start(self, args):
        """wrapper method for start_cluster used by argparser
        """
        self.start_cluster(args.node_count, args.image)

    def terminate(self, args):
        """wrapper method for delete_all_in_project used by argparser
        """
        self.delete_all_in_project()


def main(argv):
    # Perform OAuth 2.0 authorization.
    flow = flow_from_clientsecrets(CLIENT_SECRETS, scope=GCE_SCOPE)
    storage = Storage(OAUTH2_STORAGE)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)
    http = httplib2.Http()
    auth_http = credentials.authorize(http)

    gce_cluster = GceCondor(auth_http, PROJECT_ID)

    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the "start_cluster" command
    parser_start = subparsers.add_parser('start', help="start a condor cluster")
    parser_start.add_argument('node_count', type=int, default=1, help="the number of nodes, including master")
    parser_start.add_argument('-i', '--image', action="store_true", help="create instance from predefined image")
    parser_start.set_defaults(func=gce_cluster.start)

    # create the parser for the "terminate" command
    parser_terminate = subparsers.add_parser('terminate',
                                             help="shutdown cluster, ie terminate all instances in project")
    parser_terminate.set_defaults(func=gce_cluster.terminate)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main(sys.argv[1:])