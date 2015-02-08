#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import keylogger
import time
import json
import atexit
from os import path
import argparse
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser(description='Creates a heatmap on multiple layers in JSON format.')
parser.add_argument('output', help='the output file to store the heatmap')
parser.add_argument('--debug', action='store_true', help='debug mode')

#init
args = parser.parse_args()
heatmap_output_file = args.output
count = {}
done = lambda: False

#definitions
def exit_handler():
    print '\nStoring heatmap in: %s' % heatmap_output_file
    dump()

def dump():
    with open(heatmap_output_file, 'w') as outfile:
        json.dump(count, outfile, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

def create_dict(count, key, list):
    if not list:
        count[key]= count.get(key, 0)+1
    else:
        if list[0] not in count:
            count[list[0]] = {}
        create_dict(count[list[0]], key, list[1:])

def update_count(t, modifiers, keys, display_key):
    if keys:
        create_dict(count, unicode(display_key), modifiers)
        if args.debug:
            print "key pressed: %s" %keys
            dump()

# MAIN
if path.exists(heatmap_output_file):
    with open(heatmap_output_file, 'r') as input:
        count = json.load(input)

atexit.register(exit_handler)
keylogger.log(done, update_count)
