# Metodo principal que se encarga de pedor el archivo de entrada
# Llama a la clase semantic para obtener el analisis
import sys
from itertools import groupby
from operator import itemgetter
from tkinter import filedialog
from lexer import Lexer
from semantic import Semantic

def select():
    option = input("Ingresa el numero de la opcion deseada: ")
    option = int(option) if option.isdigit() else select()
    if option == 1:
        file_input()
    elif option == 2:
        console_input()
    else:
        print("Opcion no valida. Intentalo de nuevo.")
        select()

def file_input():
    # Pedir el archivo de entrada
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo",
        initialdir="./",
        filetypes=(("Python files", "*.py"), ("Text files", "*.txt"))
    )
    # Verificar si el archivo fue seleccionado o si existe
    if not file_path:
        print("No se selecciono ningun archivo")
        sys.exit(0)
    with open(file_path, 'r') as file:
        print("-----------------------------------")
        # Leer el archivo
        input_string = file.read()
        # Obtener tabla de tokens
        table = list(Lexer.lex(input_string))
        # Realizar analisis semantico
        tokens, ambitMap, errors = Semantic().analyze(table)
        print_table(tokens) # Imprimir tabla de tokens
        print_tree(ambitMap) # Imprimir arbol de ambitos
        # Verificar si hay errores
        if not errors:
            print("-----------------------------------")
            print("El código ha sido aceptado satisfactoriamente.")
            return
        print("-----------------------------------")
        print("Errores encontrados:")
        for error in errors:
            print(error)

def console_input():
    print("-----------------------------------")
    print("Ingresa el codigo. (Salto de linea, Ctrl + Z, luego Enter para finalizar):")
    inp = []
    while True:
        try:
            line = input()
            inp.append(line)
        except EOFError:
            break
    code = "\n".join(inp)
    # Obtener tabla de tokens
    table = list(Lexer.lex(code))
    # Realizar analisis semantico
    tokens, ambitMap, errors = Semantic().analyze(table)
    print_table(tokens) # Imprimir tabla de tokens
    print_tree(ambitMap) # Imprimir arbol de ambitos
    # Verificar si hay errores
    if not errors:
        print("-----------------------------------")
        print("El código ha sido aceptado satisfactoriamente.")
        return
    print("-----------------------------------")
    print("Errores encontrados:")
    for error in errors:
        print(error)

def print_table(table):
    max_i = max([len(str(x['i'])) for x in table])
    max_t = max([len(str(x['type'])) for x in table])
    max_v = max([len(str(x['value'])) for x in table])
    max_idn = max([len(str(x['ident'])) for x in table])
    print("-"*(max_i + max_t + max_v + max_idn + 15))
    print(f"{'i'.rjust(max_i)} | {'type'.ljust(max_t)} | {'value'.ljust(max_v)} | {'ident'.rjust(max_idn)}")
    print("-"*(max_i + max_t + max_v + max_idn + 15))
    for sym in table:
        i , t , v, idn = sym.values()
        if t == 'LINE_END':
            v = '\\n'
        print(f"{str(i).rjust(max_i)} | {t.ljust(max_t)} | {v.ljust(max_v)} | {str(idn).rjust(max_idn)}")

def print_tree(ambitMap):
    print("-----------------------------------")
    print("Arbol de Ambitos:")
    for ambit, props in ambitMap.items():
        print(f"  Ambito: {ambit}")
        parents, vars = props['parent'], props['vars']
        if not parents: continue
        print(f"    - Padres: {', '.join(parents)}")
        if not vars: continue
        print(f"    - Variables:")
        for var, var_props in vars.items():
            print(f"      * {var}: {var_props['value']}({var_props['type']})")

if __name__ == '__main__':
    # Dar especificaciones
    print("-----------------------------------")
    print("Compiladores - Etapa de analisis")
    print("Soporte:")
    print(" - Variables (int, float, string, bool)")
    print(" - Funciones (con parametros)")
    print(" - Estructuras de control (if, elif, else, for, while)")
    print(" - Operadores:")
    print("   * Aritmeticos: +, -, *, /, %")
    print("   * Relacionales: ==, !=, <, >, <=, >=")
    print("   * Logicos: and, or")
    print(" - Asignaciones")
    print(" - Comentarios")
    print("-----------------------------------")
    print("INSTRUCCIONES:")
    print("    1. Seleccionar un archivo de entrada")
    print("    2. Introducir el codigo fuente")
    select()