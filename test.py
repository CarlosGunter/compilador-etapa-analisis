# Autor: Carlos Alberto Gutierrez Trejo
# Compiladores - Analizador semanico
from lexer import lex
from semantic import semantic
import numpy as np

test_list = [
    {
        'name': "Expresiones con asignacion",
        'input': '''
x = 1
y = 2
z = x + y
        '''
    },
    {
        'name': "Expresiones",
        'input': '''
125 - 2.5
1 + 2
1 > 2
        '''
    },
    {
        'name': "Funciones",
        'input': '''
def my_func(x, y):
    z = 0
        '''
    },
    {
        'name': "Estructura for",
        'input': '''
for i in range(0, 10):
    i
        '''
    },
    {
        'name': "Estructura while",
        'input': '''
x = 0
while x > 10:
    x = x + 1
        '''
    },
    {
        'name': "Estructura if",
        'input': '''
if 15 > 10:
    x = 1
        '''
    }
]

if __name__ == '__main__':
    for test in test_list:
        print("------------------------------------------------------------")
        print(f"{test['name']}:")
        table = list(lex(test["input"]))
        print("***********************************************************")
        print(np.asarray(table))
        print("***********************************************************")
        semantic(table)
