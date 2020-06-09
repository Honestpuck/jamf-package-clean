#! /usr/bin/env python3

# package_list.py
# v0.1 2020-05-20
#
# List all unused packages
#
# ARW 2020-06-09 Added prefs handling for either format

import sys
from os import path
import plistlib
import requests
import xml.etree.ElementTree as ET

# the array of used packages. Preloaded with any used in
# prestage. (These change so rarely and are only accessible
# via the new API)
used = [
    '484',  # DEPNotify-Suncorp-DEP-JC-1.9.0.pkg
]

# Which pref format to use, autopkg or jss_importer
autopkg = False
if autopkg:
    plist = path.expanduser(
        '~/Library/Preferences/com.github.autopkg..plist')
    fp = open(plist, 'rb')
    prefs = plistlib.load(fp)
    base = prefs['JSS_URL'] + '/JSSResource/'
    auth = (prefs['API_USERNAME'], prefs['API_PASSWORD'])
else:
    plist = path.expanduser('~/Library/Preferences/JPCImporter.plist')
    fp = open(plist, 'rb')
    prefs = plistlib.load(fp)
    base = prefs['url'] + '/JSSResource/'
    auth = (prefs['user'], prefs['password'])
hdrs = {'Accept': 'application/json'}

url = base + 'patchpolicies'
ret = requests.get(url, auth=auth, headers=hdrs)
if ret.status_code != 200:
    print("Failed to get patch policies")
    exit(1)
patchpolicies = ret.json()['patch_policies']

url = base + 'patchsoftwaretitles'
ret = requests.get(url, auth=auth, headers=hdrs)
if ret.status_code != 200:
    print("Failed to get patchsoftwaretitles")
    exit(1)
patchsoftwaretitles = ret.json()['patch_software_titles']

url = base + 'policies'
ret = requests.get(url, auth=auth, headers=hdrs)
if ret.status_code != 200:
    print("Failed to get patchsoftwaretitles")
    exit(1)
policies = ret.json()['policies']

for title in patchsoftwaretitles:
    url = base + 'patchsoftwaretitles/id/' + str(title['id'])
    # we get XML due to API bug :(
    ret = requests.get(url, auth=auth)
    if ret.status_code != 200:
        print("Failed to get title for %s:" % title['name'])
        continue
    root = ET.fromstring(ret.text)
    print(root.findtext('name'), file=sys.stderr)
    # get the patches for this title
    url = base + 'patchpolicies/softwaretitleconfig/id/' + str(title['id'])
    ret = requests.get(url, auth=auth, headers=hdrs)
    if ret.status_code != 200:
        print("Failed to get patchpolicies for %s:" % title['name'])
        continue
    for patch in ret.json()['patch policies']:
        url = base + 'patchpolicies/id/' + str(patch['id'])
        this = requests.get(url, auth=auth, headers=hdrs)
        target = this.json()['patch_policy']['general']['target_version']
        # now find the package for that version
        for v in root.findall('versions/version'):
            if v.findtext('software_version') == target:
                try:
                    used.append(int(v.findtext('package/id')))
                except:
                    False
                continue

for policy in policies:
    url = base + 'policies/id/' + str(policy['id'])
    ret = requests.get(url, auth=auth, headers=hdrs)
    if ret.status_code != 200:
        print("Failed to get policy %s %s", (policy['id'], policy['name']))
        exit(1)
    packages_used = ret.json()['policy']['package_configuration']['packages']
    for package in packages_used:
        used.append(package['id'])

url = base + 'packages'
ret = requests.get(url, auth=auth, headers=hdrs)
if ret.status_code != 200:
    print("Failed to get packages")
    exit(1)
packages = ret.json()['packages']

for package in packages:
    if not package['id'] in used:
        print("%s\t%s" % (package['id'], package['name']))
