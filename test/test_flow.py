# vim: set fenc=utf8 ts=4 sw=4 et :
from .testcase import TestCase

from pdml2flow.conf import Conf
from pdml2flow.autovivification import AutoVivification
from pdml2flow.flow import Flow

class TestFlow(TestCase):

    def test_get_flow_id(self):
        Conf.FLOW_DEF = [ ['def1'], ['def2'] ]

        frame = AutoVivification({
            'def1': 1,
            'def2': 2,
        })
        self.assertEqual(Flow.get_flow_id(frame), '[1, 2]')

        frame = AutoVivification({
            'def1': 1,
        })
        self.assertEqual(Flow.get_flow_id(frame), '[1, {}]')

        frame = AutoVivification({
            'def3': 3,
        })
        self.assertEqual(Flow.get_flow_id(frame), None)

    def test_id(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]

        frame = AutoVivification({
            't' : 0,
            'def1': 1,
        })
        self.assertEqual(
            Flow(frame).id,
            Flow.get_flow_id(frame),
        )

        frame2 = AutoVivification({
            't' : 0,
            'def1': 2,
        })
        self.assertNotEqual(
            Flow(frame2).id,
            Flow.get_flow_id(frame),
        )

    def test__eq__(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        self.assertEqual(
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 1,
                })
            ),
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 1,
                })
            ),
        )
        self.assertNotEqual(
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 1,
                })
            ),
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 2,
                })
            ),
        )
        self.assertEqual(
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 1,
                    'unimportant': 1,
                })
            ),
            Flow(
                AutoVivification({
                    't' : 0,
                    'def1': 1,
                    'unimportant': 2,
                })
            ),
        )

    def test___hash__(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'], ['def2'] ]

        frame = AutoVivification({
            't' : 0,
            'def1': 1,
            'def2': 2,
        })
        self.assertEqual(
            hash(Flow(frame)),
            hash('[1, 2]')
        )

    def test_frames(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        f0 = AutoVivification({
            't' : 0,
            'def1': 1,
            'unimportant': 1,
        })
        f1 = AutoVivification({
            't' : 0,
            'def1': 1,
            'unimportant': 1,
        })

        f = Flow(f0)

        self.assertEqual(
            f.frames,
            f0
        )

        f.add_frame(f1)

        self.assertEqual(
            f.frames,
            f0.merge(f1)
        )

    def test_frames_returns_copy(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        f = Flow(
            AutoVivification({
                't' : 0,
                'def1': 1,
                'unimportant': 1,
            })
        )
        f.add_frame(
            AutoVivification({
                't' : 0,
                'def1': 1,
                'unimportant': 1,
            })
        )

        frames_before_add = f.frames
        f.frames['add'] = 'something'

        self.assertEqual(
            frames_before_add,
            f.frames,
        )


    def test_first_frame_time(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        f0 = AutoVivification({
            't' : 1,
            'def1': 1,
            'unimportant': 1,
        })
        f1 = AutoVivification({
            't' : 0,
            'def1': 1,
            'unimportant': 1,
        })
        f2 = AutoVivification({
            't' : 2,
            'def1': 1,
            'unimportant': 1,
        })

        f = Flow(f0)
        f.add_frame(f1)
        f.add_frame(f2)

        self.assertEqual(
            f.first_frame_time,
            f1['t']
        )

    def test_newest_frame_time(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        f0 = AutoVivification({
            't' : 2,
            'def1': 1,
            'unimportant': 1,
        })
        f1 = AutoVivification({
            't' : 0,
            'def1': 1,
            'unimportant': 1,
        })
        f2 = AutoVivification({
            't' : 1,
            'def1': 1,
            'unimportant': 1,
        })

        f = Flow(f0)
        f.add_frame(f1)
        f.add_frame(f2)

        self.assertEqual(
            f.newest_frame_time,
            f0['t']
        )

    def test_framecount(self):
        Conf.FRAME_TIME = [ 't' ]
        Conf.FLOW_DEF = [ ['def1'] ]
        f0 = AutoVivification({
            't' : 2,
            'def1': 1,
            'unimportant': 1,
        })
        f1 = AutoVivification({
            't' : 0,
            'def1': 1,
            'unimportant': 1,
        })

        f = Flow(f0)
        f.add_frame(f1)

        self.assertEqual(
            f.framecount,
            2
        )

    def test_not_expired(self):
        frame = AutoVivification({
            'frame': { 'time_epoch': { 'raw' : [123] } }
        })
        flow = Flow(frame)
        self.assertEqual(flow.not_expired(), True)
        Flow.newest_overall_frame_time = 123
        self.assertEqual(flow.not_expired(), True)
        Flow.newest_overall_frame_time = 123 + Conf.FLOW_BUFFER_TIME
        self.assertEqual(flow.not_expired(), False)
