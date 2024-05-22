# Metodo principal que se encarga de pedor el archivo de entrada
# Llama a la clase semantic para obtener el analisis
import sys
from tkinter import filedialog
from semantic import semantic

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        input_string = file.read()
        table = semantic(input_string)
        print(table)
        # print(np.asarray(table))
        # print("***********************************************************")
        # print(np.asarray(table))
        # print("***********************************************************")
        # semantic(table)