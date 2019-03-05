#!/usr/bin/env python -W ignore

from binascii import hexlify
import argparse
import os, sys

from py86 import assemble


def asm():
    argp = argparse.ArgumentParser(description='assemble a .ys file')
    argp.add_argument('file', type=str, help='path to .ys file')
    argp.add_argument('-o', '--out', type=str, help='path to output file', default=False)
    args = argp.parse_args()

    if not os.path.exists(args.file):
        print(f'path {args.file} does not exist')
        sys.exit()
    
    try:
        f = open(args.file)
    except IOError as e:
        print(f'could not read {args.file}:')
        print(e)
        sys.exit()
    
    with f:
        text = f.read()
    
    try:
        bytecode = assemble(text)
    except Exception as e:  # general af
        print(f'could not assemble {args.file}:')
        print(e)
        sys.exit()
    
    if args.out != False:
        with open(args.out, 'wb') as f:
            f.write(bytecode)
    else:
        print(hexlify(bytecode).decode())

