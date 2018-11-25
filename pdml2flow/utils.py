#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :

def boolify(string):
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('Not a bool')

def autoconvert(string):
    """Try to convert variables into datatypes."""
    for fn in (boolify, int, float):
        try:
            return fn(string)
        except ValueError:
            pass
    return string

def call_plugin(plugin, f, *args, **kwargs):
    """Calls function f from plugin, returns None if plugin does not implement f."""
    try:
        getattr(plugin, f)
    except AttributeError:
        return None
    if kwargs:
        getattr(plugin, f)(
            *args,
            **kwargs
        )
    else:
        return getattr(plugin, f)(
            *args
        )

def make_argparse_help_safe(s):
    """Make strings safe for argparse's help.

    Argparse supports %{} - templates. This is sometimes not needed.
    Make user supplied strings safe for this.
    """
    return s.replace('%', '%%').replace('%%%', '%%')
