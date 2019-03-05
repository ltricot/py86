from dataclasses import dataclass
from typing import Union
from binascii import hexlify
import struct

from sly import Parser

from .lexer import Y86Lexer


@dataclass
class Instruction:
    code: bytes
    rega: str = None
    regb: str = None
    cons: int = None

    _registers = {
        '%rax': 0, '%rbx': 3, '%rcx': 1, '%rdx': 2,
        '%rsp': 4, '%rbp': 5, '%rsi': 6, '%rdi': 7,
        '%r8':  8, '%r9':  9, '%r10': 10, '%r11': 11,
        '%r12': 12, '%r13': 13, '%r14': 14, None: 0x0F,
    }

    def encode(self):
        code = bytearray([self.code])
        if self.rega is not None or self.regb is not None:
            rega = self._registers[self.rega]
            regb = self._registers[self.regb]
            code.append((rega << 4) | regb)
        if self.cons is not None:
            code.extend(struct.pack(f'<q', self.cons))
        return code


@dataclass
class Directive:
    which: str  # in { 'pos', 'align', 'quad', 'long', 'byte', 'identifier' }
    label: str = None  # for identifiers
    data:  int = None  # for data & pos & align

    def encode(self):  # only relevant if directive stores data
        if self.which not in ['byte', 'word', 'long', 'quad']:
            raise ValueError(f'directive {self} does not store data')

        ln = {'byte': 'b', 'word': 'h', 'long': 'l', 'quad': 'q'}[self.which]
        return struct.pack(f'<{ln}', self.data)


@dataclass
class Address:
    offset:   Union[int, str]
    register: str


class Y86Assembler(Parser):
    # debugfile = 'parser.out'
    tokens = Y86Lexer.tokens

    _max_addr  = 1 << 16
    _addresses = None

    start = 'program'

    _lens = {
        'halt': 1, 'nop': 1, 'rrmovq': 2, 'irmovq': 10, 'rmmovq': 10,
        'mrmovq': 10, 'andq': 2, 'xorq': 2, 'addq': 2, 'subq': 2,
        'jmp': 9, 'jle': 9, 'jl': 9, 'je': 9, 'jne': 9, 'jge': 9,
        'jg': 9, 'cmovle': 2, 'cmovl': 2, 'cmove': 2, 'cmovne': 2,
        'cmovge': 2, 'cmovg': 2, 'call': 9, 'ret': 1, 'pushq': 2,
        'popq': 2,
    }

    @staticmethod
    def _get_addresses(toks):
        addresses, cur, _lens = {}, 0, Y86Assembler._lens
        for tok in toks:
            # add instruction length to cursor
            if tok.type.lower() in _lens:
               cur += _lens[tok.type.lower()]

            # align cursor on `al` byte boundary
            elif tok.type == 'ALIGN':
                al = next(toks).value
                cur += (al - (cur % al)) % al

            # pos give an absolute address
            elif tok.type == 'POS':
                cur = next(toks).value

            elif tok.type in ['BYTE', 'WORD', 'LONG', 'QUAD']:
                cur += {
                    'BYTE': 1, 'WORD': 2,
                    'LONG': 4, 'QUAD': 8,
                }[tok.type]

            # add identifier to addresses
            # must make sure this is indeed a label
            # and not used as an immediate
            elif tok.type == 'IDENTIFIER':
                try:
                    nt = next(toks)
                except:
                    break

                if not nt.type == ':': continue
                addresses[tok.value] = cur
        return addresses

    @_('')
    def empty(self, p):
        ...

    # `program` rules interpret the `Instructions` and
    # `Directives` returned by other rules and assemble
    # them into bytes
    @_('program statement')
    def program(self, p):
        p.program.extend(p.statement.encode())
        return p.program

    @_('program pos')
    def program(self, p): 
        if p.pos.data < len(p.program):
            raise ValueError(
                'py86 does not support overwriting previous code '
                'through a nonsensical .pos directive'
            )

        p.program.extend(b'\x00' * (p.pos.data - len(p.program)))
        return p.program

    @_('program align')
    def program(self, p):
        imm = p.align.data
        p.program.extend(
            b'\x00' * ((imm - (len(p.program) % imm)) % imm))
        return p.program

    @_('program label')
    def program(self, p):
        self._addresses[p.label.label] = len(p.program)
        return p.program

    @_('program static')
    def program(self, p):
        p.program.extend(p.static.encode())
        return p.program

    @_('empty')
    def program(self, p):
        return bytearray([])

    @_('IDENTIFIER "(" REGISTER ")"',
       '"(" REGISTER ")"', 'IDENTIFIER')
    def address(self, p):
        try: offset = p.IDENTIFER
        except: offset = 0
        try: register = p.REGISTER
        except: register = None
        return Address(
            offset=offset,
            register=register
        )

    @_('IMMEDIATE "(" REGISTER ")"')
    def address(self, p):
        return Address(offset=p.IMMEDIATE, register=p.REGISTER)

    for _i, _tok in enumerate(['RRMOVQ', 'CMOVLE', 'CMOVL', 'CMOVE',
        'CMOVNE', 'CMOVGE', 'CMOVG']):

        @_(f'{_tok} REGISTER "," REGISTER')
        def statement(self, p, _i=_i):
            return Instruction(
                code=0x20 + _i,
                rega=p.REGISTER0,
                regb=p.REGISTER1
            )

    @_('IRMOVQ IDENTIFIER "," REGISTER')
    def statement(self, p):
        return Instruction(
            code=0x30,
            regb=p.REGISTER,
            cons=self._addresses[p.IDENTIFIER]
        )

    @_('IRMOVQ IMMEDIATE "," REGISTER')
    def statement(self, p):
        return Instruction(
            code=0x30,
            regb=p.REGISTER,
            cons=p.IMMEDIATE
        )

    @_('RMMOVQ REGISTER "," address',
       'MRMOVQ address "," REGISTER')
    def statement(self, p):
        addroff = p.address.offset
        offset = addroff if isinstance(addroff, int) \
            else self._addresses[addroff]

        return Instruction(
            code=0x40 if p[0] == 'rmmovq' else 0x50,
            rega=p.REGISTER,
            regb=p.address.register,
            cons=offset,
        )

    for _i, _tok in enumerate(['JMP', 'JLE', 'JL', \
        'JE', 'JNE', 'JGE', 'JG']):

        @_(f'{_tok} IMMEDIATE')
        def statement(self, p, _i=_i):
            return Instruction(
                code=0x70 + _i,
                cons=p.IMMEDIATE,
            )

        @_(f'{_tok} IDENTIFIER')
        def statement(self, p, _i=_i):
            return Instruction(
                code=0x70 + _i,
                cons=self._addresses[p.IDENTIFIER],
            )

    @_('HALT')
    def statement(self, p):
        return Instruction(0x00)

    @_('NOP')
    def statement(self, p):
        return Instruction(0x10)

    @_('PUSHQ REGISTER')
    def statement(self, p):
        return Instruction(code=0xA0, rega=p.REGISTER)

    @_('POPQ REGISTER')
    def statement(self, p):
        return Instruction(code=0xB0, rega=p.REGISTER)

    @_('CALL IDENTIFIER')
    def statement(self, p):
        return Instruction(code=0x80, cons=self._addresses[p.IDENTIFIER])

    @_('CALL IMMEDIATE')
    def statement(self, p):
        return Instruction(code=0x80, cons=p.IMMEDIATE)

    @_('RET')
    def statement(self, p):
        return Instruction(code=0x90)

    @_('POS IMMEDIATE')
    def pos(self, p):
        return Directive('pos', data=p.IMMEDIATE)

    @_('ALIGN IMMEDIATE')
    def align(self, p):
        if p.IMMEDIATE not in (2, 4, 8):
            raise ValueError(
                f'align value ({p.IMMEDIATE}) must be 2, 4 or 8'
            )

        return Directive('align', data=p.IMMEDIATE)

    @_('IDENTIFIER ":"')
    def label(self, p):
        return Directive('identifier', label=p.IDENTIFIER)

    for _tok in ['BYTE', 'WORD', 'LONG', 'QUAD']:
        @_(f'{_tok} IMMEDIATE')
        def static(self, p, _tok=_tok.lower()):
            return Directive(_tok, data=p.IMMEDIATE)

    for _i, _tok in enumerate(['ADDQ', 'SUBQ', 'ANDQ', 'XORQ']):
        @_(f'{_tok} REGISTER "," REGISTER')
        def statement(self, p, _i=_i):
            return Instruction(
                code=0x60 + _i,
                rega=p.REGISTER0,
                regb=p.REGISTER1,
            )

    @_('IADDQ IMMEDIATE "," REGISTER')
    def statement(self, p):
        return Instruction(
            code=0xC0,
            regb=p.REGISTER,
            cons=p.IMMEDIATE,
        )


def assemble(src):
    lexer = Y86Lexer()
    parser = Y86Assembler()
    parser._addresses = parser._get_addresses(lexer.tokenize(src))
    return parser.parse(lexer.tokenize(src))


if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as f:
        res = assemble(f.read())
    print(hexlify(res))

