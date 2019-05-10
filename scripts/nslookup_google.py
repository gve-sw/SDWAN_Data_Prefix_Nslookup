#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses
               
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""
# NOTE: Make sure dnspython package is installed before running this script

import dns.resolver
import re
import sys
import requests
import json

predefined_list_ip = ['35.190.247.0/24', '64.233.160.0/19', '66.102.0.0/20', '66.249.80.0/20', '72.14.192.0/18', '74.125.0.0/16', '108.177.8.0/21', '173.194.0.0/16', '209.85.128.0/17', '216.58.192.0/19', '216.239.32.0/19', '172.217.0.0/19', '172.217.32.0/20', '172.217.128.0/19', '172.217.160.0/20', '172.217.192.0/19', '108.177.96.0/19', '35.191.0.0/16', '130.211.0.0/22']
list_ip = ['34.190.247.0/20']  # Added an IP for testing, can be removed as required


def login(vmanage_ip, username, password):
    # Login to vmanage
    session = {}

    base_url_str = 'https://%s/'%vmanage_ip

    login_action = '/j_security_check'

    # Format data for loginForm
    login_data = {'j_username' : username, 'j_password' : password}

    # Url for posting login data
    login_url = base_url_str + login_action

    url = base_url_str + login_url

    sess = requests.session()

    # If the vmanage has a certificate signed by a trusted authority change verify to True
    login_response = sess.post(url=login_url, data=login_data, verify=False)
    try:
        if login_response.status_code == 200:
            session[vmanage_ip] = sess
            # global sessions
            # sessions = session[vmanage_ip]
            return session[vmanage_ip]
        elif '<html>' in login_response.content:
            print "Login Failed"
            sys.exit(0)
        else:
            print("Unknown exception")
    except Exception as err:
        return


def get_ip_prefix(domain_name):
    # Function to get the list of prefixes

    dns_details_blocks = dns.resolver.query(domain_name, 'TXT')

    for rdata in dns_details_blocks:
        ip_data_blocks = rdata.to_text()

    list_data_blocks = ip_data_blocks.split()
    list_data_blocks = list_data_blocks.__getslice__(1,list_data_blocks.__len__()-1)

    for i in list_data_blocks:
        list_ip.append(re.sub('ip.*?:', '', i))


def put_prefix_list_builder():
    # Function to update the prefix list

    lst = [] # List of IP Prefixes
    for pn in list_ip:
        d = {}
        d['ipPrefix'] = pn
        lst.append(d)
    json.dumps(lst)
    payload = {
                  "name": "google_prefixes_copy",
                  "type": "dataPrefix",
                  "entries": lst
                }
    test = json.dumps(payload)
    headers = {'Content-Type': 'application/json'}
    sessions = login("Your vManage IP", "username", "password") # Enter your vManage credentials
    url = 'https://Your vManage IP/dataservice/template/policy/list/dataprefix/your data prefix list id'
    r = sessions.put(url, data=test, headers=headers, verify=False)
    print(r.status_code)


if __name__ == "__main__":

    # Used google.com as an example
    domain_list = ["_netblocks.google.com","_netblocks3.google.com"]

    for domain_name in domain_list:
        get_ip_prefix(domain_name) # Call the function to fetch list of IP Prefix

    if list_ip == predefined_list_ip:
        print("Updation of prefix list not required!!!")
    else:
        put_prefix_list_builder()  # Call the function to update the prefix list

    print("Process Completed!!")
