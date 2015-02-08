import keylogger
import time

now = time.time()
done = lambda: time.time() > now + 600
def print_keys(t, modifiers, keys): print "%s\t\t%r" % (keys, modifiers)

keylogger.log(done, print_keys)
