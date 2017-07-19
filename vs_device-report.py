#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: Report mapping a virtual server to a BIGIP
#@Product: BIGIQ
#@VersionIntroduced: 5.x

"""
Copyright 2017 by F5 Networks Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License a
xc
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import simplejson as json
import base64
import string
import os.path

def device_report(config):
    print "\n"
    print '####Show virtual servers and its corresponding BIGIP device name####'

    ## If config file is defiend we will use requests else we will assume running on BIGIQ and use httplib
    try:
        import requests
        requests.packages.urllib3.disable_warnings()
        uri = 'https://' + config['bigiq'] + '/mgmt/cm/adc-core/working-config/ltm/virtual'

        response = requests.get(uri, auth=(config['username'], config['password']), verify=False)
        parsed_response = response.json()
    
    except:
        import httplib
        ## Header used in the connection request
        headers = {}    
        headers['Authorization'] = 'Basic ' + string.strip(base64.b64encode(config['username'] + ':' + config['password']))
    
    
        try:
            connection = httplib.HTTPConnection(config['bigiq'] + ':8100')
            ## Request GET virtuals
            connection.request('GET', '/cm/adc-core/working-config/ltm/virtual', None, headers)
            ## Parse Response
            response = connection.getresponse()
    
            ## If not successful then print response and exit.
            if response.status != 200:
                print response.status
                print response.reason
                return False

            response = response.read()
            parsed_response = json.loads(response)
        except:
            print 'ERROR: Using {0} assumes you are running in the BIGIQ shell. Http GET using httplib failed.'.format(config['bigiq'])
            return False

    ## Lets take a look at the virtuals and the BIGIP device it belongs to.
    count = 1
    for item in parsed_response['items']:
        print str(count) + ". Virtual Server=" + item['name'] + " belongs to BIGIP=" + item['deviceReference']['name']
	count+=1

    print "\n"
    return True

if __name__ == '__main__':
    #==========================
    # Help
    #==========================
    config={}
    try:
        import argparse

        parser = argparse.ArgumentParser(description='List all virutals and devices each live on.')
        parser.add_argument('--config', type=str, help='Configuration,IQ-IP address, user, pass.')

        args = parser.parse_args()
        #==========================
        # Read config file
        #==========================    
        file = args.config
    
        infile = open (file, 'r')
        for line in infile:
            (key, val) = line.split(' = ')
            config[str(key)] = val.strip('\n')
        
    except:
        print "Using localhost, admin, admin for network address, username, password. Assuming running directly on BIGIQ"
        config['username'] = 'admin'
        config['password'] = 'admin'
        config['bigiq'] = 'localhost'
            

    #==========================
    # Report
    #==========================
    result = device_report(config) 
    if result == True: 
        print 'INFO: Virtuals to Device reference report - COMPLETE.'
    else:
        print 'FAIL: Virtuals to Device reference report - NOT-COMPLETE'
