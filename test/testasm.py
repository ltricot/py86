import unittest
import os

from py86 import assemble


fdir = os.path.dirname(__file__)
ydir = os.path.join(fdir, 'y86-code')


class TestAssembler(unittest.TestCase):
    def test_assemble(self):
        for path, dirnames, fnames in os.walk(ydir):
            for fname in fnames:
                if not fname.endswith('.ys'):
                    continue
    
                fpath = os.path.join(path, fname)
                with open(fpath) as f:
                    text = f.read()
    
                with self.subTest(file=fname):
                    assemble(text)

