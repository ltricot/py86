import unittest
import os

from py86 import assemble


fdir = os.path.dirname(__file__)
ydir = os.path.join(fdir, 'y86-code')
yas  = os.path.join(fdir, 'yas')


def _read_yo(text):
    code = bytearray()
    for line in text.split('\n'):
        if not line: continue
        addr, *tail = line.split(':')
        
        try:
            addr = int(addr, 16)
        except:
            continue

        code.extend(b'\x00' * (addr - len(code)))
        instr = tail[0].split('|')[0].strip(' \t')
        code.extend(bytes.fromhex(instr))
    return code

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
                    pyasm = assemble(text)

                    os.system(f'{yas} {fpath}')
                    yop = fpath.replace('.ys', '.yo')
                    with open(yop) as y:
                        yot = y.read()
                    yoasm = _read_yo(yot)
                    os.remove(yop)

                    self.assertEqual(pyasm, yoasm)


if __name__ == '__main__':
    import sys
    from binascii import hexlify
    with open(sys.argv[1]) as f:
        bytecode = _read_yo(f.read())

    print(hexlify(bytecode))


