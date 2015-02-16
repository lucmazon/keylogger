#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep, time, strftime
import keylogger
import json
import atexit
from os import path
import argparse
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser(description='Creates a heatmap on multiple layers in JSON format.')
parser.add_argument('mapper', help='the json file linking keycodes to their displayable counterparts')
parser.add_argument('output', help='the output file to store the heatmap')
parser.add_argument('--debug', action='store_true', help='debug mode')

#init
args = parser.parse_args()
heatmap_output_file = args.output
mapper_file = args.mapper
heatmap_object = {'count' : {}, 'modifiers' : []}

#definitions
@atexit.register
def exit_handler():
    dump()

def load_mapper():
    with open(mapper_file, 'r') as f:
        return json.load(f)

def dump():
    with open(heatmap_output_file, 'w') as outfile:
        print '\nStoring heatmap in: %s at date: %s' % (heatmap_output_file, strftime("%d/%m/%y %H:%M:%S"))
        json.dump(heatmap_object, outfile, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

def create_dict(count, key, list, modifiers):
    if modifiers:
        heatmap_object['modifiers'] = modifiers.keys()
    if not list:
        count[key]= count.get(key, 0)+1
    else:
        if list[0] not in count:
            count[list[0]] = {}
        create_dict(count[list[0]], key, list[1:], [])

def update_count(t, active_modifiers, display_key, chosen_key, modifiers):
    if display_key:
        create_dict(heatmap_object['count'], unicode(chosen_key), active_modifiers, modifiers)
        if args.debug:
            print "key pressed: %s" %display_key

# MAIN
if path.exists(heatmap_output_file):
    with open(heatmap_output_file, 'r') as input:
        count = json.load(input)

keylogger.set_mapper(load_mapper())

try:
    while 1:
        now = time()
        done = lambda: time() > now + 60
        keylogger.log(done, update_count)
        dump()
except KeyboardInterrupt:
    print "exiting program"
