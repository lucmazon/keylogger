#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from time import sleep, time
import ctypes as ct
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
shift_keys = ((6,4), (7,64))
alt_key = (13,16)
modifiers = {
    "left shift": (6,4),
    "right shift": (7,64),
    "left ctrl": (4,32),
    "right ctrl": (13,2),
    "left alt": (8,1),
    "right alt": (13,16),
    "left super": (16,32),
    "right super": (16,64)
}
last_pressed = set()
last_pressed_adjusted = set()
last_modifier_state = {}
caps_lock_state = 0

# key is byte number, value is a dictionary whose
# keys are values for that byte, and values are the
# keys corresponding to those byte values
key_mapping = {
    1: {
        0b00000010: "<esc>",
        0b00000100: ("\"", "1", "—", "„"),
        0b00001000: ("«", "2", "<", "“"),
        0b00010000: ("»", "3", ">", "”"),
        0b00100000: ("(", "4", "[", "≤"),
        0b01000000: (")", "5", "]", "≥"),
        0b10000000: ("@", "6", "^", " "),
    },
    2: {
        0b00000001: ("+", "7", "±", "¬"),
        0b00000010: ("-", "8", "−", "¼"),
        0b00000100: ("/", "9", "×", "¾"),
        0b00001000: ("*", "0", "×", "¾"),
        0b00010000: ("=", "°", "≠", "′"),
        0b00100000: ("%", "`", "‰", "″"),
        0b01000000: "<backspace>",
        0b10000000: "<tab>",
    },
    3: {
        0b00000001: ("b", "B", "|", "¦"),
        0b00000010: ("é", "É", " ", " "),
        0b00000100: ("p", "P", "&", "§"),
        0b00001000: ("o", "O", "œ", "Œ"),
        0b00010000: ("è", "T"),
        0b00100000: ("^", "!", "¡", " "),
        0b01000000: ("v", "V", " ", " "),
        0b10000000: ("d", "D", "ð", "Ð"),
    },
    4: {
        0b00000001: ("l", "L", " ", " "),
        0b00000010: ("j", "J", "ĳ", "Ĳ"),
        0b00000100: ("z", "Z", "ə", "Ə"),
        0b00001000: ("w", "W", " ", " "),
        0b00010000: "<enter>",
        #0b00100000: "<left ctrl>",
        0b01000000: ("a", "A", "æ", "Æ"),
        0b10000000: ("u", "U", "ù", "Ù"),
    },
    5: {
        0b00000001: ("i", "I", "\"", " "),
        0b00000010: ("e", "E", "€", " "),
        0b00000100: (",", ";", "’", " "),
        0b00001000: ("c", "C", "©", "ſ"),
        0b00010000: ("t", "T", "þ", "Þ"),
        0b00100000: ("s", "S", "ß", "ẞ"),
        0b01000000: ("r", "R", "®", "™"),
        0b10000000: ("n", "N", "~", " "),
    },
    6: {
        0b00000001: ("m", "M", " ", "º"),
        0b00000010: ("$", "#", "–", "¶"),
        #0b00000100: "<left shift>",
        0b00001000: ("ç", "Ç", " ", " "),
        0b00010000: ("à", "À", "\\", " "),
        0b00100000: ("y", "Y", "{", "‘"),
        0b01000000: ("x", "X", "}", "’"),
        0b10000000: (".", ":", "…", "·"),
    },
    7: {
        0b00000001: ("k", "K", "~", " "),
        0b00000010: ("'", "?", "¿", " "),
        0b00000100: ("q", "Q", "Â", " "),
        0b00001000: ("g", "G", " ", " "),
        0b00010000: ("h", "H", "†", "‡"),
        0b00100000: ("f", "F", " ", "ª"),
        #0b01000000: "<right shift>",
    },
    8: {
        #0b00000001: "<left alt>",
        0b00000010: "<space>",
        0b00000100: "<caps lock>",
        0b00001000: "<f1>",
        0b00010000: "<f2>",
        0b00100000: "<f3>",
        0b01000000: "<f4>",
        0b10000000: "<f5>",
    },
    9: {
        0b00000001: "<f6>",
        0b00000010: "<f7>",
        0b00000100: "<f8>",
        0b00001000: "<f9>",
        0b00010000: "<f10>",
        0b00100000: "<ver num>",
        0b01000000: "<arret defil>",
        0b10000000: "<7 num>",
    },
    10: {
        0b00000001: "<8 num>",
        0b00000010: "<9 num>",
        0b00000100: "<- num>",
        0b00001000: "<4 num>",
        0b00010000: "<5 num>",
        0b00100000: "<6 num>",
        0b01000000: "<+ num>",
        0b10000000: "<1 num>",
    },
    11: {
        0b00000001: "<2 num>",
        0b00000010: "<3 num>",
        0b00000100: "<0 num>",
        0b00001000: "<. num>",
        0b10000000: "<f11>",
    },
    12: {
        0b00000001: "<f12>",
    },
    13: {
        #0b00000010: "<right ctrl>",
        0b00000100: "</ num>",
        0b00001000: "<print screen>",
        #0b00010000: "<right alt>",
        0b01000000: "<home>",
        0b10000000: "<up>",
    },
    14: {
        0b00000001: "<pgup>",
        0b00000010: "<left>",
        0b00000100: "<right>",
        0b00001000: "<end>",
        0b00010000: "<down>",
        0b00100000: "<pgdown>",
        0b01000000: "<insert>",
        0b10000000: "<del>",
    },
    15: {
        0b10000000: "<pause>",
    },
    16: {
        # 0b00100000: "<left super>",
        # 0b01000000: "<right super>",
        0b10000000: "<right click>",
    }
}




def fetch_keys_raw():
    x11.XQueryKeymap(display, keyboard)
    return keyboard



def fetch_keys():
    global caps_lock_state, last_pressed, last_pressed_adjusted, last_modifier_state
    keypresses_raw = fetch_keys_raw()


    # check modifier states (ctrl, alt, shift keys)
    modifier_state = {}
    for mod, (i, byte) in modifiers.iteritems():
        modifier_state[mod] = bool(ord(keypresses_raw[i]) & byte)
    
    # shift pressed?
    shift = 0
    for i, byte in shift_keys:
        if ord(keypresses_raw[i]) & byte:
            shift = 1
            break

    # alt gr pressed?
    alt = 0
    if ord(keypresses_raw[alt_key[0]]) & alt_key[1]:
        alt = 2


    # caps lock state
    if ord(keypresses_raw[8]) & 4: caps_lock_state = int(not caps_lock_state)


    # aggregate the pressed keys
    pressed = []
    for i, k in enumerate(keypresses_raw):
        o = ord(k)
        if o:
            for byte,key in key_mapping.get(i, {}).iteritems():
                if byte & o:
                    if isinstance(key, tuple): key = key[(shift or caps_lock_state) + alt]
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

    return state_changed, active_modifiers, pressed




def log(done, callback, sleep_interval=.005):
    while not done():
        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
        if changed: callback(time(), modifiers, keys)




if __name__ == "__main__":
    now = time()
    done = lambda: time() > now + 60
    def print_keys(t, modifiers, keys): print "%.2f   %s   %r" % (t, keys, modifiers)

    log(done, print_keys)
