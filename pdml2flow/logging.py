#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .conf import Conf

def debug(*objs):
    if Conf.DEBUG:
        print("[Debug: {}] ".format(Flow.newest_overall_frame_time), *objs, file=sys.stderr)

def warning(*objs):
    print("[Warning: {}] ".format(Flow.newest_overall_frame_time), *objs, file=sys.stderr)

