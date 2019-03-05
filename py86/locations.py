import argparse
import os, sys

from .parser import Y86Assembler, Y86Lexer


def locate():
    argp = argparse.ArgumentParser(description='find label addresses of .ys file')
    argp.add_argument('file', type=str, help='input .ys file')
    args = argp.parse_args()

    if not os.path.exists(args.file):
        print('path {args.file} does not exist')
        sys.exit()

    try:
        f = open(args.file)
    except IOError as e:
        print('could not read {args.file}:')
        print(e)
        sys.exit()

    with f:
        text = f.read()

    try:
        toks = Y86Lexer().tokenize(text)
        addrs = Y86Assembler._get_addresses(toks)
    except Exception as e:
        print('could not find locations for {args.file}:')
        print(e)
        sys.exit()

    print(addrs)

