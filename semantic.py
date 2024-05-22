# Autor: Carlos Alberto Gutierrez Trejo
# Compiladores - Analizador semantico
from lexer import lex

class semantic:
    def __init__(self, tokens):
        # Mapa de identificadores
        self.ambitMap = {
            'GLOBAL': {
                'parent': [],
                'ident': 0,
                'vars': {}
            }
        }
        self.currScope = 'GLOBAL'
        self.prevIdent = 0
        self.line = 1

        self.analyze(tokens)

    # Funcion principal
    def analyze(self, tokens):
        global ambitMap
        ambitMap = self.ambitMap
        currScope = 'GLOBAL'
        prevIdent = 0
        line= 1
        # Recorrido de tokens
        iT = 0
        while iT < len(tokens)-1:
            # Obtener token
            token = tokens[iT]
            i, group, value, ident = token["i"], token["type"], token["value"], token["ident"]
            # print(f"{value} -> {group}, {ident}")
            # Verificar identacion
            if currScope == 'GLOBAL' and ident > 0:
                print(f"No se esperaba identacion en ambito global. Linea {line}")
            if ident < prevIdent and prevIdent != 0 and group != 'LINE_END':
                # Buscar identacion padre
                for pnt in ambitMap[currScope]["parent"]:
                    if ambitMap[pnt]["ident"] == ident:
                        currScope = pnt
                        print(f"{currScope} -> Ambito padre. Linea {line}")
                        break
                    if pnt == ambitMap[currScope]["parent"][-1]:
                        print(f"Identacion no valida. Linea {line}")
                        break
            # Verificar si el token es una funcion
            if value == 'def':
                # Crear ambito de la funcion
                iT, currScope = functions(tokens, token, currScope, line)
            # Verificar si el token es una estructura de control
            elif group == 'STRUCT_C':
                # Crear ambito de la estructura
                iT, currScope = structure(tokens, token, currScope, line)
            # Verificar si el token es una asignacion
            elif group == 'ASSIGN':
                # Verificar si el token anterior es un ID
                if tokens[i - 1]["type"] != 'ID':
                    print(f"Se esperaba un ID para asignar. Linea {line}")
                    iT, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
                else:
                    # Realizar asignacion
                    iT = assign(tokens, token, currScope, line, tokens[i - 1]["value"])
            # Verificar si el token es un operador aritmetico o relacional
            elif group in ['AR_OP', 'REL_OP']:
                # Realizar operacion
                iT, _ = expression(tokens, token, currScope, line)
            # Verificar si el token es un salto de linea
            # Incrementar contador de lineas
            elif group == 'LINE_END': line += 1; iT += 1
            # Incrementar contador de tokens
            else: iT += 1
            # Guardar identacion sin contar los saltos de linea
            if group != 'LINE_END': prevIdent = ident
            # Imprimir mapa de ambitos
        print(ambitMap)

# Cada analisis debe retornar el salto de linea al final del lexema
def functions(tokens, token, parent, line):
    # Lexema: def ID (ID, ID, ...):
    i, ident = token["i"], token["ident"]
    # ID de la funcion
    if tokens[i + 1]["type"] == 'ID': funcID = tokens[i + 1]["value"]
    else: # Si no hay ID -> Error
        print(f"Se esperaba un ID. Linea {line}")
        pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
        return pos, parent
    # Crear ambito de la funcion
    newParent = ambitMap[parent]["parent"][:] # Copiar scope padre
    newParent.insert(0, parent) # Agregar padre
    ambitMap[funcID] = {
        'parent': newParent,
        'vars': {},
    }
    print(f"{funcID} -> Ambito creado. Linea {line} (Resolucion de nombres)")
    # Parametros de la funcion
    if tokens[i + 2]["value"] != '(': # Si no hay '(' -> Error
        print(f"Se esperaba '('. Linea {line}")
        pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
        return pos, parent
    # Si hay parametros
    else:
        # Buscar cierre de parentesis
        pos, findFound = findEnd(tokens, i+2, line, end=('value', ')'))
        if not findFound: return pos, parent # Si no se encuentra -> Error
        # Recorrer parametros
        for j in range(i + 3, pos, 2):
            # Verificar si hay parametros y agregarlos al mapa
            if tokens[j]["type"] == 'ID':
                ambitMap[funcID]["vars"][tokens[j]["value"]] = {
                    'type': 'Any',
                    'value': None,
                }
                print(f"{tokens[j]['value']} -> tipo: PARAM, ambito: {funcID}")
            # Si no hay ID -> Error
            else:
                print(f"Se esperaba un ID. Linea {line}")
                break
            # Verificar si los parametros estan separados por coma
            if not tokens[j+1]["value"] in [',', ')']:
                print(f"Se esperaba coma. Linea {line}")
    # Verificar si hay ':'
    pos, findFound = findEnd(tokens, i, line, end=('value', ':'))
    if findFound: pos += 1 # Posicionar en el salto de linea
    else: print(f"Se esperaba ':'. Linea {line}") # Si no se encuentra -> Error
    # Verificar indentacion
    if pos+1 < len(tokens) and tokens[pos + 1]["ident"] <= ident:
        print(f"Se esperaba bloque indentado. Linea {line}")
    # Agregar indentacion
    else: ambitMap[funcID]["ident"] = tokens[pos + 2]["ident"]
    # Retornar posicion y nuevo scope
    return pos, funcID

def assign(tokens, token, currScope, line, assignID):
    # Lexema: ID = EXPRESION
    i = token["i"]
    pos = i
    currType = 'Any'
    # Verificar si la asignacion dispone solo de un factor
    # ID = factor
    if tokens[i + 2]["type"] == 'LINE_END':
        # Verificar si el factor es valido
        # ID = ID | INT | FLOAT | STRING | BOOL
        if not tokens[i+1]["type"] in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            print(f"Dato no valido. Linea {line}")
            return pos+2
        # Verificar si el factor es un ID y esta inicializado
        # ID = ID -> Verificar si el ID esta inicializado
        if tokens[i + 1]["type"] == 'ID' and not findVar(tokens[i + 1]["value"], currScope):
            print(f"'{tokens[i + 1]['value']}' aun no inicializada. Linea {line}")
            return pos+2
        pos += 2
        # Determinar el tipo de la variable
        currType = findVar(tokens[i + 1]["value"], currScope)["type"] if tokens[i + 1]["type"] == 'ID' else tokens[i + 1]["type"]
    # Resolver la expresion
    # Lexema -> ID = TERMINOS
    elif tokens[i + 2]["type"] in ['REL_OP', 'AR_OP']: # Buscar operadores
        pos, currType = expression(tokens, tokens[i+2], currScope, line)
    # Si no hay operadores
    else:
        print(f"Se esperaba un operador. Linea {line}")
        # Buscar siguinte salto de linea
        while tokens[pos]["type"] != 'LINE_END': pos += 1
        pos += 1
    # Agregar variable al mapa
    if not findVar(assignID, currScope):
        ambitMap[currScope]["vars"][assignID] = {
            'type': currType,
            'value': None,
        }
    print(f"{assignID} -> tipo: {findVar(assignID, currScope)['type']}, ambito: {currScope}")
    return pos

def expression(tokens, token, currScope, line, end=('type', 'LINE_END')):
    # Lexema: FACTOR OPERADOR FACTOR... OPERADOR FACTOR
    # Token actual -> OPERADOR
    i, value, type = token["i"], token["value"], token["type"]
    pos = i
    currType = 'Any'
    end_eval, end_value = end
    # Recorrer operadores
    for j in range(i, len(tokens), 2):
        pos = j # Actualizar posicion
        evalType = True # Bandera para evaluar tipos
        # Romper si termina la expresion
        if tokens[j][end_eval] == end_value: break
        if tokens[j]["type"] in ('LINE_END', 'PAREN'): break # Borrar
        elif tokens[j]["value"] == ':': break # Borrar
        # Verificar operador
        if tokens[j]["type"] not in ['AR_OP', 'REL_OP']:
            print(f"Operador {tokens[j]["value"]} no valido. Linea {line}")
            pos += 1
            break
        # Obtener factores
        pv_v, pv_t = tokens[i - 1]["value"], tokens[i - 1]["type"]
        nx_v, nx_t = tokens[i + 1]["value"], tokens[i + 1]["type"]
        # Verificar si los factores son validos
        if not pv_t in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            print(f"'{pv_t}' no se puede operar. Linea {line}")
            evalType = False
        if not nx_t in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            print(f"'{nx_t}' no se puede operar. Linea {line}")
            evalType = False
        # Verificar si los factores son IDs y estan declarados
        if pv_t == 'ID' and not findVar(pv_v, currScope):
            print(f"'{pv_v}' aun no inicializada. Linea {line}")
            evalType = False
        if nx_t == 'ID' and not findVar(nx_v, currScope):
            print(f"'{nx_v}' aun no inicializada. Linea {line}")
            evalType = False
        # Verificar si se pueden evaluar los tipos
        if not evalType: continue
        # Obtener tipos de los factores
        prev = findVar(pv_v, currScope)["type"] if pv_t == "ID" else pv_t
        next = findVar(nx_v, currScope)["type"] if nx_t == "ID" else nx_t
        # Verificar si la variable es un parametro en una funcion
        if 'Any' in [prev, next]: continue
        # Verificar si los tipos son compatibles
        if prev != next and not prev in ['INT', 'FLOAT'] and not next in ['INT', 'FLOAT']:
            print(f"Tipos incompatibles '{pv_v}'({prev}) y '{nx_v}'({next}). Linea {line}")
        else:
            currType = "FLOAT" if value in ['/', '%'] else prev
            currType = "BOOL" if type == 'REL_OP' else currType
    return pos, currType

def structure(tokens, token, parent, line):
    # Lexema: While | If | For | EXPRESIN:
    i, value, ident = token["i"], token["value"], token["ident"]
    currScope = f'{value}_{line}'
    # Crear ambito
    newParent = ambitMap[parent]["parent"][:] # Copiar scope padre
    newParent.insert(0, parent) # Agregar padre
    ambitMap[currScope] = {
        'parent': newParent,
        'vars': {},
    }
    print(f"{currScope} -> Ambito creado. Linea {line} (Resolucion de nombres)")
    # While o If -> While | if | elif EXPRESION:
    if value in ['while', 'if', 'elif']:
        # Buscar ':'
        pos, findFound = findEnd(tokens, i, line, end=('value', ':'))
        end = ('value', ':') if findFound else ('type', 'LINE_END')
        # Si hay solo un factor
        if pos - i <= 2 and not tokens[i + 1]["type"] in ['ID', 'INT', 'FLOAT', 'STRING', 'BOOL']:
            print(f"Se esperaba una expresion. Linea {line}")
            return pos, parent
        else:
            # Verificar si hay operadores
            if tokens[i + 2]["type"] in ['REL_OP', 'AR_OP', 'LOG_OP']:
                pos, _ = expression(tokens, tokens[i+2], parent, line, end=end)
        # lex = [ # Lexema del while o if
        #     ('type', ['ID', 'INT', 'FLOAT', 'STRING', 'BOOL']),
        #     ('type', ['REL_OP']),
        #     ('type', ['ID', 'INT', 'FLOAT', 'STRING', 'BOOL']),
        #     ('value', [':'])
        # ]
        # for j in range(len(lex)):
        #     k, v = lex[j]
        #     pos = i+j+1
        #     if tokens[pos]['type'] == 'LINE_END':
        #         print(f"Expresion incompleta. Linea {line}")
        #         break
        #     if not tokens[pos][k] in v:
        #         print(f"Se esperaba '{v}'. Linea {line}")
        # # Verificar si hay un operador
        # if tokens[i + 3]["type"] == 'REL_OP':
        #     pos, _ = expression(tokens, tokens[i+1], parent, line)
    # For ID in EXPRESION:
    elif value == 'for':
        lex = [ # Lexema del for
            ('type', ['ID']),
            ('value', ['in']),
            ('value', ['range']),
            ('value', ['(']),
            ('type', ['INT', 'ID']),
            ('value', [',']),
            ('type', ['INT', 'ID']),
            ('value', [')']),
            ('value', [':'])
        ]
        for j in range(len(lex)):
            k, v = lex[j]
            pos = i+j+1
            if tokens[pos]['type'] == 'LINE_END':
                print(f"Expresion incompleta. Linea {line}")
                break
            if not tokens[pos][k] in v:
                print(f"Se esperaba '{v}'. Linea {line}")
        # Verificar si hay un ID
        if tokens[i + 1]["type"] == 'ID':
            # Agregar ID al mapa
            ambitMap[currScope]["vars"][tokens[i + 1]["value"]] = {
                'type': '',
                'value': None,
            }
            print(f"{tokens[i + 1]['value']} -> tipo: {'INT'}, ambito: {currScope}")
    # Else:
    elif value == 'else':
        if tokens[i + 1]["value"] != ':':
            print(f"Se esperaba ':'. Linea {line}")
        if tokens[i + 2]['type'] != 'LINE_END':
            print(f"Se esperaba una nueva linea. Linea {line}")
    # Buscar salto de linea
    pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
    # Verificar identacion en siguiente linea
    if tokens[pos]["type"] == 'LINE_END' and tokens[pos + 1]["ident"] <= ident:
        print(f"Se esperaba identacion de bloque. Linea {line+1}")
    # Agregar identacion
    ambitMap[currScope]["ident"] = tokens[pos + 1]["ident"]
    # Retornar posicion y nuevo scope
    return pos, currScope

# Buscar las variables desde el ambito actual hasta los padres
def findVar(var, scope):
    # Buscar variable en el ambito actual
    if var in ambitMap[scope]["vars"]: return ambitMap[scope]["vars"][var]
    # Buscar variable en el ambito padre
    for pnt in ambitMap[scope]["parent"]:
        if var in ambitMap[pnt]["vars"]: return ambitMap[pnt]["vars"][var]
    return None

# Buscar el final de la expresion
def findEnd(tokens, i, line, end):
    endEval, endValue = end
    if len(tokens) <= i: return i, False
    while tokens[i][endEval] != endValue:
        if i+1 >= len(tokens) or tokens[i]["type"] == 'LINE_END': break
        i += 1
    # Verificar errores
    if (
    # Si el token actual es un salto de linea pero no es el buscado
    endValue != 'LINE_END' and
    tokens[i]["type"] == 'LINE_END'
    ) or (
    # Si el token actual es el ultimo pero no es el buscado
    i == len(tokens) - 1 and
    tokens[i]["type"] != 'LINE_END'
    ):
        print(f"Se esperaba '{endValue}'. Linea {line}")
        return i, False
    return i, True

if __name__ == '__main__':
    print("Ingresa el codigo. (Presiona Ctrl + Z + Enter para finalizar):")
    inp = []
    while True:
        try:
            line = input()
            inp.append(line)
        except EOFError:
            break
    inp.append("\n  ")
    code = "\n".join(inp)
    table = lex(code)
    semantic(list(table))