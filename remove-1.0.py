#!/usr/bin/env python3

import sys
from os import path
import plistlib
import requests
import xml.etree.ElementTree as ET

plist = path.expanduser('~/Library/Preferences/JPCImporter.plist')
fp = open(plist, 'rb')
prefs = plistlib.load(fp)
base = prefs['url'] + '/JSSResource/'
auth = (prefs['user'], prefs['password'])
hdrs = {'Accept': 'application/json'}

for line in sys.stdin:
    print('Doing %s' % line)
    parts = line.rstrip().split('\t')
    url = base + 'packages/id/' + parts[0]
    # sanity check
    ret = requests.get(url, auth=auth, headers=hdrs)
    if ret.status_code != 200:
        print("Failed to get %s" % line)
        continue
    if ret.json()['package']['name'] != parts[1]:
        print("Sanity 1 fail %s %s %s" %
              (line, ret.json()['package']['name'], parts[1]))
        continue
    ret = requests.delete(url, auth=auth)
    if ret.status_code != 200:
        print("Failed to delete %s" % line)
        continue
    root = ET.fromstring(ret.text)
    if root.findtext('id') == parts[1]:
        print("Failed delete sanity %s" % line)
        continue
