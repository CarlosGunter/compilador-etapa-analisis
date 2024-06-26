# Autor: Carlos Alberto Gutierrez Trejo
# Compiladores - Analizador semantico

class Semantic:
    def __init__(self):
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

    # Funcion principal
    def analyze(self, tokens):
        global ambitMap, errors
        ambitMap = self.ambitMap
        errors = []
        currScope = 'GLOBAL'
        prevIdent = 0
        line= 1
        # Recorrido de tokens
        iT = 0
        while iT < len(tokens):
            # Obtener token
            token = tokens[iT]
            i, group, value, ident = token["i"], token["type"], token["value"], token["ident"]
            # Verificar identacion
            if currScope == 'GLOBAL' and ident > 0:
                errors.append(f"No se esperaba identacion en ambito global. Linea {line}")
            if ident < prevIdent and prevIdent != 0 and group != 'LINE_END':
                # Buscar identacion padre
                for pnt in ambitMap[currScope]["parent"]:
                    if ambitMap[pnt]["ident"] == ident:
                        currScope = pnt
                        break
                    if pnt == ambitMap[currScope]["parent"][-1]:
                        errors.append(f"Identacion no valida. Linea {line}")
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
                    errors.append(f"Se esperaba un ID para asignar. Linea {line}")
                    iT, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
                else:
                    # Realizar asignacion
                    iT = assign(tokens, token, currScope, line, tokens[i - 1]["value"])
            # Verificar si el token es un operador aritmetico o relacional
            elif group in ['AR_OP', 'REL_OP', 'LOG_OP']:
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
        return tokens, ambitMap, errors

# Cada analisis debe retornar el salto de linea al final del lexema
def functions(tokens, token, parent, line):
    # Lexema: def ID (ID, ID, ...):
    i, ident = token["i"], token["ident"]
    # ID de la funcion
    if tokens[i + 1]["type"] == 'ID': funcID = tokens[i + 1]["value"]
    else: # Si no hay ID -> Error
        errors.append(f"Se esperaba un ID. Linea {line}")
        pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
        return pos, parent
    # Verificar si la funcion ya existe
    if funcID in ambitMap:
        errors.append(f"Funcion '{funcID}' ya declarada. Linea {line}")
        pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
        return pos, parent
    # Crear ambito de la funcion
    newParent = ambitMap[parent]["parent"][:] # Copiar scope padre
    newParent.insert(0, parent) # Agregar padre
    ambitMap[funcID] = {
        'parent': newParent,
        'vars': {},
    }
    # Parametros de la funcion
    if tokens[i + 2]["value"] != '(': # Si no hay '(' -> Error
        errors.append(f"Se esperaba '('. Linea {line}")
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
            # Si no hay ID -> Error
            else:
                errors.append(f"Se esperaba un ID. Linea {line}")
                break
            # Verificar si los parametros estan separados por coma
            if not tokens[j+1]["value"] in [',', ')']:
                errors.append(f"Se esperaba coma. Linea {line}")
    # Verificar si hay ':'
    pos, findFound = findEnd(tokens, i, line, end=('value', ':'))
    if findFound: pos += 1 # Posicionar en el salto de linea
    else:
        # Si no se encuentra -> Error
        errors.append(f"Se esperaba ':'. Linea {line}")
    # Verificar indentacion
    if pos+1 < len(tokens) and tokens[pos + 1]["ident"] <= ident:
        errors.append(f"Se esperaba bloque indentado. Linea {line}")
    # Agregar indentacion
    else: ambitMap[funcID]["ident"] = tokens[pos + 2]["ident"]
    # Retornar posicion y nuevo scope
    return pos, funcID

def assign(tokens, token, currScope, line, assignID):
    # Lexema: ID = EXPRESION
    i = token["i"]
    pos = i + 1
    currType = 'Any'
    # Verificar si la asignacion dispone solo de un factor
    # ID = factor
    if tokens[i + 2]["type"] == 'LINE_END':
        # Verificar si el factor es valido
        # ID = ID | INT | FLOAT | STRING | BOOL
        if not tokens[i+1]["type"] in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            errors.append(f"Dato no valido. Linea {line}")
            pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
            return pos
        # Verificar si el factor es un ID y esta inicializado
        # ID = ID -> Verificar si el ID esta inicializado
        if tokens[i + 1]["type"] == 'ID' and not findVar(tokens[i + 1]["value"], currScope):
            errors.append(f"'{tokens[i + 1]['value']}' aun no inicializada. Linea {line}")
            pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
            return pos
        # Determinar el tipo de la variable
        currType = findVar(tokens[i + 1]["value"], currScope)["type"] if tokens[i + 1]["type"] == 'ID' else tokens[i + 1]["type"]
    # Resolver la expresion
    # Lexema -> ID = TERMINOS
    elif tokens[i + 2]["type"] in ['REL_OP', 'AR_OP', 'LOG_OP']:
        pos, currType = expression(tokens, tokens[i+2], currScope, line)
    # Si no hay operadores
    else:
        errors.append(f"Se esperaba un operador. Linea {line}")
        # Buscar siguinte salto de linea
        while tokens[pos]["type"] != 'LINE_END': pos += 1
        pos, _ = findEnd(tokens, pos, line, end=('type', 'LINE_END'))
    # Agregar variable al mapa
    if not findVar(assignID, currScope):
        ambitMap[currScope]["vars"][assignID] = {
            'type': currType,
            'value': None,
        }
    return pos

def expression(tokens, token, currScope, line, end=('type', 'LINE_END')):
    # Lexema: FACTOR OPERADOR FACTOR... OPERADOR FACTOR
    # Token actual -> OPERADOR
    i, value, type = token["i"], token["value"], token["type"]
    currType = 'Any'
    end_eval, end_value = end
    # Buscar final de la expresion
    pos, _ = findEnd(tokens, i, line, end)
    # Recorrer operadores
    for j in range(i, pos, 2):
        evalType = True # Bandera para evaluar tipos
        if tokens[j][end_eval] == end_value: break
        # Verificar operador
        if not tokens[j]["type"] in ['AR_OP', 'REL_OP', 'LOG_OP']:
            errors.append(f"Operador {tokens[j]["value"]} no valido. Linea {line}")
            pos, _ = findEnd(tokens, j, line, end=('type', 'LINE_END'))
            break
        # Verificar si el indice siguiente se encuentra en el rango
        if j + 1 >= len(tokens):
            errors.append(f"Se esperaba un factor. Linea {line}")
            break
        # Obtener factores
        pv_v, pv_t = tokens[j - 1]["value"], tokens[j - 1]["type"]
        nx_v, nx_t = tokens[j + 1]["value"], tokens[j + 1]["type"]
        # Verificar si los factores son validos
        if not pv_t in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            errors.append(f"'{pv_v}' no se puede operar. Linea {line}")
            evalType = False
        if not nx_t in ['INT', 'FLOAT', 'STRING', 'BOOL', 'ID']:
            errors.append(f"'{nx_v}' no se puede operar. Linea {line}")
            evalType = False
        # Verificar si los factores son IDs y estan declarados
        if pv_t == 'ID' and not findVar(pv_v, currScope):
            errors.append(f"'{pv_v}' aun no inicializada. Linea {line}")
            evalType = False
        if nx_t == 'ID' and not findVar(nx_v, currScope):
            errors.append(f"'{nx_v}' aun no inicializada. Linea {line}")
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
            errors.append(f"Tipos incompatibles '{pv_v}'({prev}) y '{nx_v}'({next}). Linea {line}")
        else:
            currType = "FLOAT" if value in ['/', '%'] else prev
            currType = "BOOL" if type in ['REL_OP', 'LOG_OP'] else currType
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
    # While o If -> While | if | elif EXPRESION:
    if value in ['while', 'if', 'elif']:
        # Buscar ':'
        pos, findFound = findEnd(tokens, i, line, end=('value', ':'))
        end = ('value', ':') if findFound else ('type', 'LINE_END')
        # Si hay solo un factor
        if pos - i <= 2 and not tokens[i + 1]["type"] in ['ID', 'INT', 'FLOAT', 'STRING', 'BOOL']:
            errors.append(f"Se esperaba una expresion. Linea {line}")
            return pos, parent
        else:
            # Verificar si hay operadores
            if tokens[i + 2]["type"] in ['REL_OP', 'AR_OP', 'LOG_OP']:
                pos, _ = expression(tokens, tokens[i+2], parent, line, end=end)
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
                errors.append(f"Expresion incompleta. Linea {line}")
                break
            if not tokens[pos][k] in v:
                errors.append(f"Se esperaba '{v}'. Linea {line}")
        # Verificar si hay un ID
        if tokens[i + 1]["type"] == 'ID':
            # Agregar ID al mapa
            ambitMap[currScope]["vars"][tokens[i + 1]["value"]] = {
                'type': '',
                'value': None,
            }
    # Else:
    elif value == 'else':
        if tokens[i + 1]["value"] != ':':
            errors.append(f"Se esperaba ':'. Linea {line}")
        if tokens[i + 2]['type'] != 'LINE_END':
            errors.append(f"Se esperaba una nueva linea. Linea {line}")
    # Buscar salto de linea
    pos, _ = findEnd(tokens, i, line, end=('type', 'LINE_END'))
    # Verificar identacion en siguiente linea
    if tokens[pos]["type"] == 'LINE_END' and tokens[pos + 1]["ident"] <= ident:
        errors.append(f"Se esperaba identacion de bloque. Linea {line+1}")
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
    if not i+1 <= len(tokens): return len(tokens), False
    while i+1 < len(tokens) and tokens[i][endEval] != endValue:
        if i >= len(tokens) or tokens[i]["type"] == 'LINE_END': break
        i += 1
    # Verificar errores
    if (
    # Si el token actual es un salto de linea pero no es el buscado
    endValue != 'LINE_END' and
    tokens[i]["type"] == 'LINE_END'
    ) and (
    # Si el token actual es el ultimo pero no es el buscado
    i == len(tokens) - 1 and
    tokens[i]["type"] != 'LINE_END'
    ):
        errors.append(f"Se esperaba '{endValue}'. Linea {line}")
        return i, False
    return i, True
