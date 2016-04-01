#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import functools

DEFAULT = object();

class AutoVivification(dict):

    """
    Returns a copy of this object without empty leaves
    see: https://stackoverflow.com/questions/27973988/python-how-to-remove-all-empty-fields-in-a-nested-dict/35263074
    """
    def clean_empty(self, d=DEFAULT):
        if d is DEFAULT:
            d = self
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [v for v in (self.clean_empty(v) for v in d) if v]
        return type(self)({k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v})

    """
    merges b into a recursively, if a is not given: merges into self
    also merges lists and :
        * merge({a:a},{a:b}) = {a:[a,b]}
        * merge({a:[a]},{a:b}) = {a:[a,b]}
        * merge({a:a},{a:[b]}) = {a:[a,b]}
        * merge({a:[a]},{a:[b]}) = {a:[a,b]}
    """
    def merge(self, b, a=DEFAULT, path=None, compress_data=False):
        if a is DEFAULT:
            a = self
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(b[key], a[key], path + [str(key)])
                else:
                    if type(a[key]) is list and type(b[key]) is list:
                        a[key] += b[key]
                    elif type(a[key]) is list and type(b[key]) is not list:
                        a[key] += [b[key]]
                    elif type(a[key]) is not list and type(b[key]) is list:
                        a[key] = [a[key]] + b[key]
                    elif type(a[key]) is not list and type(b[key]) is not list:
                        a[key] = [a[key]] + [b[key]]
                    if compress_data:
                        # remove duplicates
                        a[key] = list(set(a[key]))
            else:
                a[key] = b[key]
        return a


    """
    Implementation of perl's autovivification feature.
    see: https://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    """
    def __getitem__(self, item):
        # if the item is a list we autoexpand it
        if type(item) is list:
            return functools.reduce(lambda d, k: d[k], item, self)
        else:
            try:
                return dict.__getitem__(self, item)
            except KeyError:
                value = self[item] = type(self)()
                return value
