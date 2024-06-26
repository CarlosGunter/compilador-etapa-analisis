import re

# Definir tokens usando expresiones regulares
tokens = [
    ('LINE_COMMENT', r'#.*'),
    ('KEYWORD', r'def|in|print|:'),
    ('STRUCT_C', r'if|else|elif|while|for'),
    ('AR_OP', r'[+\-*/%]'),
    ('REL_OP', r'[<>=!]=|<|>'),
    ('LOG_OP', r'and|or'),
    ('ASSIGN', r'='),
    ('IDENT', r"(?<=\n)\s+"),
    ('STRING', r'".*?"'),
    ('FLOAT', r'\d+\.\d+'),
    ('INT', r'\d+'),
    ('BOOL', r'True|False'),
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('PAREN', r'[()]'),
    ('COMMA', r','),
    ('LINE_END', r'\n'),
    ('WS', r'\s+'),  # Ignorar espacios en blanco
    ('UNRECOGNIZED', r'.'),  # Caracteres no reconocidos
]
class Lexer:
    # Función para escanear la entrada y producir tokens
    def lex(input_str):
        token_exprs = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
        regex = re.compile(token_exprs)
        i = 0
        ident = 0
        pos = 0
        while pos < len(input_str):
            match = regex.match(input_str, pos)
            token_type = match.lastgroup
            token_value = match.group(token_type)
            if token_type == 'IDENT': ident = len(token_value)
            if token_type == 'LINE_END': ident = 0
            if not token_type in ['WS', 'LINE_COMMENT', 'IDENT']:
                yield {
                    "i": i,
                    "type": token_type,
                    "value": token_value,
                    "ident": ident
                }
                i += 1
            pos = match.end()

# Ejemplo de uso
if __name__ == '__main__':
    input_string = '''
    x = 1.125
    y = 2
    a = "12"
    def my_func(x, y):
        b = "x"
        z = x + y
    '''
    
    input_string = '''
(a,(b,c))
def my_func(x, y):
    print(x + y)
    '''

    input_string = '''z = 1 + 2 - 3'''
    
    table = Lexer.lex(input_string)
    print(len(list(table)))
    for token in table:
        print(token)