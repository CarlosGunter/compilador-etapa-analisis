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

Análisis semántico:
- Verificación de tipos.
- Resolución de nombres.
- Análisis de contexto.

> [!NOTE]
> - No se permiten agrupaciones en las expresiones.
> - Solo se permite una condición en las estructuras.
