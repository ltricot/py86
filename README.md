# Y86 assembler written in python

A python-written assembler for the toy Y86 assembly language. Created for educational purposes.

## Installing as a package

Use the familiar `git clone https://github.com/ltricot/py86`, then:
```sh
cd py86
python setup.py install
```

## Use

You may then use the installed command as follows:
```sh
py86 code.ys -o code.yo
```

The assembler is accessible from python if needed:
```python
from py86 import assemble

with open('code.ys') as f:
    bytecode = assemble(f.read())

print(bytecode)
```


## Running the tests

To discover the current bugs, you may run the tests:
```sh
python setup.py test
```

## License

See the [license](./LICENSE) for py86's license and the [sly license](https://github.com/dabeaz/sly/blob/master/LICENSE) for the SLY license. SLY is a python library used for parsing.
