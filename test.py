#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import keylogger
import time
import json
import atexit
from os import path

heatmap = "/home/kluck/heatmap.json"

done = lambda: False

count = {}

if path.exists(heatmap):
    with open(heatmap, 'r') as input:
        count = json.load(input)

def update_count(t, modifiers, keys):
    if keys:
        if modifiers:
            key = "%s %s" % (keys, tuple(modifiers))
        else:
            key = "%s" % keys
        count[key] = count.get(key, 0)+1
        # print count

keylogger.log(done, update_count)

def exit_handler():
    print '\nEnregistrement des données sur : %s' % heatmap
    with open(heatmap, 'w') as outfile:
        json.dump(count, outfile, sort_keys=True, indent=4, separators=(',', ': '))

atexit.register(exit_handler)
