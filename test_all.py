#!/usr/bin/env python3
# coding: utf-8

__author__ = "gboulant, may 2021"

import unittest

from test_svgsketcher import TestSvgSketcher
from test_telecran import TestTelecran

def runtest():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSvgSketcher))
    suite.addTests(loader.loadTestsFromTestCase(TestTelecran))
    
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    runtest()
