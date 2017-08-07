#!/usr/bin/env python

import os

def is_homepage(x):
    return os.path.isfile(x)

def test_homepage():
    assert is_homepage('./output/index.html')
