import math
import time

def get_universal_time():
    return time.time()

def plural(n, word):
    return word if n == 1 else word + "s"

age_units = [("year", 365.25 * 24 * 60 * 60),
             ("week", 7 * 24 * 60 * 60),
             ("day",  24 * 60 * 60),
             ("hour", 60 * 60),
             ("minute", 60),
             ("second", 1)]

def friendly_age(time):
    age = math.floor(get_universal_time() - time)
    units = list(age_units)
    while(units and age < units[0][1]):
        units = units[1:]

    name, value = units[0] if units else (None, None)
    if not name:
        return 'now'

    v = math.floor(age / value)
    return '%G %s' % (v, plural(v, name))

