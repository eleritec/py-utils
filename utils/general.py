import os
import logging
import time

def http_host(hostname):
    if not hostname:
      return ''

    host = hostname.split('://')[-1].split('/')[0]
    return 'https://' + host

def first(array):
    if array:
        for item in array:
            if item:
                return item
    return None

def sub_dict(dictionary, keys):
    matches = {}
    for key in keys:
        if key in dictionary:
            matches[key] = dictionary[key]
    return matches

def build_dict(list, key_name):
    d = {}
    for item in list:
        key = item.get(key_name, None)
        if key:
            d[key] = item
    return d

def from_dict(dictionary, key, creator):
    value = dictionary.get(key, None)
    if not value:
        value = creator()
        dictionary[key] = value
    return value

def dict_list(dictionary, key):
    return from_dict(dictionary, key, new_list)

def dict_set(dictionary, key):
    return from_dict(dictionary, key, new_set)

def new_list():
    return []

def new_set():
    return set([])

def set_attr(obj, attr, value):
    if obj and attr:
        obj[attr] = value

def get_attr(obj, attr, default=None):
    if obj and attr:
        return obj.get(attr, default)
    return default

def first_match(items, matcher, default_value=None):
    matches = list(filter(matcher, items))
    return matches[0] if matches else default_value

def get_json_attr(blob, key, default_value):
    if not key:
        return default_value

    parent = blob
    for k in key.split('.'):
        if not parent:
            return default_value
        value = parent.get(k, None)
        parent = value

    return value if value else default_value

def read_file(path, default=None):
    if not path or not os.path.isfile(path):
        return default

    file = open(path, 'r')
    text = file.read()
    file.close()
    return text

def write_file(path, content, overwrite=True):
    if not overwrite and os.path.isfile(path):
        return

    if os.path.isdir(path):
        return

    content = content if content else ''
    file = open(path, 'w')
    file.write(content)
    file.close()

def get_logger(obj=None):
    if type(obj) is str:
        return logging.getLogger(obj)
    return logging.getLogger(obj.__class__.__name__) if obj else logging.getLogger(__name__)

def time_call(function):
    started = time.perf_counter()
    result = function()
    elapsed = time.perf_counter() - started
    return result, elapsed

def usable(*args):
    items = args
    if len(items) == 1 and type(items[0]) is list:
        items = items[0]

    return [item for item in items if item]

def contains_any(collection, *items):
    if not collection:
        return False

    items = flatten(items)
    for item in items:
        if item in collection:
            return True

    return False

def flatten(iterable, sublist_attr=None, criteria=None): 
    return flatten_sublists(iterable, sublist_attr, criteria) if sublist_attr else flatten_simple(iterable)

def flatten_simple(iterable):
    if not iterable:
        return []

    flat = []
    for entry in iterable:
        if type(entry) is list:
            flat.extend(entry)
        else:
            flat.append(entry)
    return flat

def flatten_sublists(owners, sublist_attr, criteria=None):
    flat = []
    for owner in owners:
        sublist = owner.get(sublist_attr, [])
        if type(sublist) is not list:
            sublist = [sublist]
        filtered = [entry for entry in sublist if criteria(entry)] if criteria else sublist
        flat.extend(filtered)
    return flat

def lsplit(array, block_size):
    if not array:
        return []

    blocks = []
    total = len(array)
    block_size = max(1, block_size)

    for start in range(0, total + block_size, block_size):
        end = min(total, start + block_size)
        blocks.append(array[start:end])

    return blocks
