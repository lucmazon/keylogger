#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import ctypes as ct
import math
from time import sleep, time
from ctypes.util import find_library


# linux only!
assert("linux" in sys.platform)


x11 = ct.cdll.LoadLibrary(find_library("X11"))
display = x11.XOpenDisplay(None)


# this will hold the keyboard state.  32 bytes, with each
# bit representing the state for a single key.
keyboard = (ct.c_char * 32)()

# these are the locations (byte, byte value) of special
# keys to watch
modifiers = {
    "left shift": 50,
    "right shift": 62,
    "left ctrl": 37,
    "right ctrl": 105,
    "alt": 64,
    "altGr": 108,
    "❖": 133
}

last_pressed = set()
last_pressed_adjusted = set()
last_modifier_state = {}
caps_lock_state = 0

mapper = {}

def set_mapper(mapper_source):
    global mapper
    mapper = mapper_source

def keycode_to_keypress_tuple(keycode):
    return (keycode/8, int(math.pow(2, keycode%8)))

def keypress_tuple_to_keycode(index, byte_value):
    return index*8 + int(math.log(byte_value, 2))

def fetch_keys_raw():
    x11.XQueryKeymap(display, keyboard)
    return keyboard

def fetch_keys():
    global caps_lock_state, last_pressed, last_pressed_adjusted, last_modifier_state
    keypresses_raw = fetch_keys_raw()


    # check modifier states (ctrl, alt, shift keys)
    modifier_state = {}
    for mod, keycode in modifiers.iteritems():
        keypress_tuple = keycode_to_keypress_tuple(keycode)
        modifier_state[mod] = bool(ord(keypresses_raw[keypress_tuple[0]]) & keypress_tuple[1])
    
    # shift pressed?
    shift = 0
    if modifier_state["left shift"] or modifier_state["right shift"]:
        shift = 1

    # alt gr pressed?
    altgr = 0
    if modifier_state["altGr"]:
        altgr = 2


    # caps lock state
    if ord(keypresses_raw[8]) & 4: caps_lock_state = int(not caps_lock_state)

    # aggregate the pressed keys
    key = 'unknown'
    display_key = key
    pressed = []
    for index, value in enumerate(keypresses_raw):
        o = ord(value)
        if o:
            keycode = keypress_tuple_to_keycode(index, o)
            if str(keycode) in mapper and mapper[str(keycode)] not in modifiers.keys():
                key = mapper[str(keycode)]
                display_key = key[0] if isinstance(key, list) else key
                id = (shift or caps_lock_state) + altgr
                if isinstance(key, list):
                    if id < len(key):
                        key = key[id]
                    else:
                        key = key[0]
                pressed.append(key)

    
    tmp = pressed
    pressed = list(set(pressed).difference(last_pressed))
    state_changed = tmp != last_pressed and (pressed or last_pressed_adjusted)
    last_pressed = tmp
    last_pressed_adjusted = pressed

    if pressed: pressed = pressed[0]
    else: pressed = None


    state_changed = last_modifier_state and (state_changed or modifier_state != last_modifier_state)
    last_modifier_state = modifier_state

    active_modifiers = []
    for key, value in modifier_state.iteritems():
        if value:
            active_modifiers.append(key)

    return state_changed, active_modifiers, pressed, display_key, modifiers

def log(done, callback, sleep_interval=.005):
    while not done():
        sleep(sleep_interval)
        changed, active_modifiers, keys, display_key, modifiers = fetch_keys()
        if changed: callback(time(), active_modifiers, keys, display_key, modifiers)

if __name__ == "__main__":
    now = time()
    done = lambda: time() > now + 60
    def print_keys(t, modifiers, keys, display_key): print "%.2f   %s\t\t%r" % (t, keys, modifiers)

    log(done, print_keys)
