#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys

from .conf import Conf

def debug(*args):
    # import here because of circular dependencies
    from .flow import Flow
    if Conf.DEBUG:
        print(
            '[Debug: {}] '.format(
                Flow.newest_overall_frame_time
            ),
            *args,
            file=Conf.OUT_DEBUG
        )

def warning(*args):
    # import here because of circular dependencies
    from .flow import Flow
    print(
        '[Warning: {}] '.format(
            Flow.newest_overall_frame_time
        ),
        *args,
        file=Conf.OUT_WARNING
    )

def error(*args):
    # import here because of circular dependencies
    from .flow import Flow
    print(
        '[Error: {}] '.format(
            Flow.newest_overall_frame_time
        ),
        *args,
        file=Conf.OUT_ERROR
    )

