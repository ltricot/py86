# Y86 assembler written in python

A python-written assembler for the toy Y86 assembly language. Created for educational purposes.

## Installing as a package

Use the familiar `git clone https://github.com/ltricot/py86`, then:
```sh
cd py86
python setup.py install
```

You may then use py86 from python code as follows:
```python
from py86 import assemble

with open('code.ys') as f:
    bytecode = assemble(f.read())

print(bytecode)
```

A script is provided for convenience (this will be better in the future, WIP):
```sh
python py86/parser.py code.ys
```

To discover the current bugs, you may run the tests:
```sh
cd test
python -m unittest
```

