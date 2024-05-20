# Autor: Carlos Alberto Gutierrez Trejo
# Compiladores - Analizador semanico
from lexer import lex
from semantic import semantic

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
    x
        '''
    }
]

if __name__ == '__main__':
    for test in test_list:
        print("------------------------------------------------------------")
        print(f"{test['name']}:")
        table = list(lex(test["input"]))
        # print(table)
        semantic(table)
