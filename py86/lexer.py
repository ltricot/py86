from sly import Lexer



_instr_keys = [
    'rrmovq', 'cmovle', 'cmovl', 'cmove', 'cmovne', 'cmovge',
    'cmovg', 'rmmovq', 'mrmovq', 'irmovq', 'addq', 'subq', 'andq',
    'xorq', 'jmp', 'jle', 'jl', 'je', 'jne', 'jge', 'jg', 'call', 'ret',
    'pushq', 'popq', '.byte', '.word', '.long', '.quad',
    '.pos', '.align', 'halt', 'nop', 'iaddq',
]

instructions = {k: k.upper().lstrip('.') for k in _instr_keys}


class Y86Lexer(Lexer):
    tokens = {
        IDENTIFIER, IMMEDIATE, REGISTER, NEWLINE,

        # instructions
        RRMOVQ, CMOVLE, CMOVL, CMOVE, CMOVNE, CMOVGE, CMOVG, RMMOVQ,
        MRMOVQ, IRMOVQ, ADDQ, SUBQ, ANDQ, XORQ, JMP, JLE, JL, JE,
        JNE, JGE, JG, CALL, RET, PUSHQ, POPQ, BYTE, WORD, LONG, QUAD,
        POS, ALIGN, HALT, NOP, IADDQ,
    }

    literals = { '(', ')', ',', ':' }

    ignore = ' \t'
    ignore_comment = r'\#.*|/\*.*\*/'
    REGISTER = \
        (r'%rax|%rcx|%rdx|%rbx|%rsi|%rdi|%rsp|%rbp'
         r'|%r8|%r9|%r10|%r11|%r12|%r13|%r14')

    @_(r'[\r\n]')
    def ignore_NEWLINE(self, t):
        self.lineno += 1

    @_(r'[\.]?[a-zA-Z]\w+')
    def IDENTIFIER(self, t):
        t.type = instructions.get(t.value, t.type)
        if t.value.startswith('.') and t.type == 'IDENTIFIER':
            raise SyntaxError('Identifier cannot start with \'.\'')
        return t

    @_(r'\$?((0[xX][0-9a-fA-F]+)|([-]?\d+))')
    def IMMEDIATE(self, t):
        b = 10
        val = t.value.lstrip('$')
        if val.startswith('0x') or val.startswith('0X'):
            b = 16
        t.value = int(val, b)
        return t


if __name__ == '__main__':
    import sys

    lexer = Y86Lexer()
    with open(sys.argv[1]) as f:
        tokens = lexer.tokenize(f.read())

    for tok in tokens:
        print(tok)

