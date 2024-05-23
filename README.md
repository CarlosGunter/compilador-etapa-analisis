# Compilador - Etapa de análisis.
Este condigo realiza una análisis general de un código con la sintaxis de python.
Se obtiene la tabla de tokens realizando un análisis sintáctico y esta se utiliza para el análisis semántico.

**Realiza**:
Análisis sintáctico:
- Tabla de tokens:
  * Numero de token.
  * Tipo.
  * Valor.
  * Sangria.

Análisis sintáctico y semántico:
- Verificación de tipos.
- Resolución de nombres.
- Análisis de contexto.
- Mapa de ámbitos.

**Soporte**
  - Variables (int, float, string, bool)"
  - Funciones (con parámetros)"
  - Estructuras de control (if, elif, else, for, while)"
  - Operadores:"
    * Aritméticos: +, -, *, /, %"
    * Relacionales: ==, !=, <, >, <=, >="
    * Lógicos: and, or"
  - Asignaciones"
  - Comentarios"

> [!NOTE]
> - No se permiten agrupaciones en las expresiones.
> - La estructura for solo permite parámetro range con inicio y final.
