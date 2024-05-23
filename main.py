# Metodo principal que se encarga de pedor el archivo de entrada
# Llama a la clase semantic para obtener el analisis
import sys
import numpy as np
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
        Semantic(table)
        print(np.array(table))
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
    # inp.append("\n  ")
    code = "\n".join(inp)
    table = list(Lexer.lex(code))
    Semantic(table)
    print(np.array(table))

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