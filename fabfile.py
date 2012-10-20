#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from fabric.api import *


def up(path):
    return os.path.split(path)[0]

SMEWT_ROOT = up(os.path.abspath(__file__))

SMEWT_ROOT_PARENT = up(SMEWT_ROOT)

# first add paths to local smewt and pygoo repositories
relative_modules = [ 'smewt',
                     #'pygoo',
                     'guessit',
                     'subliminal'
                     ]

py_path = [ os.path.join(SMEWT_ROOT_PARENT, module)
            for module in relative_modules ]

py_path = 'PYTHONPATH=%s:$PYTHONPATH ' % (':'.join(py_path))


@task
def profile():
    """Run Smewt and profile it, write the resulting data into /tmp/profstats."""
    local(py_path + 'python -m cProfile -o /tmp/profstats bin/run_dev_smewg')
    print 'Wrote profile results in /tmp/profstats'
    print 'You can visualize them with "runsnake /tmp/profstats"'

@task
def smewt():
    """Run Smewt."""
    local(py_path + 'python bin/run_dev_smewg')
