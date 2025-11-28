# src/nucleo/validacion_prolog.py

from pyswip import Prolog
import numpy as np

# Inicialización del motor de Prolog
motor_prolog = Prolog()

# --- Funciones de Conversión de Datos ---

def matriz_numpy_a_lista(matriz_numpy: np.ndarray) -> list:
    # Convierte matriz NumPy (9x9) a lista de listas de Python
    return matriz_numpy.tolist()

def lista_a_matriz_numpy(lista_de_listas: list, tipo_matriz) -> np.ndarray:
    # Convierte lista de listas de Python a matriz NumPy
    return np.array(lista_de_listas, dtype=tipo_matriz)

# --- Funciones de Validación de Sudoku ---

def configurar_reglas_sudoku_validacion():
    # Define las reglas de Prolog para validar movimientos en Sudoku
    # Regla: Verifica si un número NO está en una fila
    motor_prolog.assertz("""
        valido_en_fila(Matriz, Fila, Numero) :-
            nth0(Fila, Matriz, FilaLista),
            \\+ member(Numero, FilaLista)
    """)
    
    # Regla: Verifica si un número NO está en una columna
    motor_prolog.assertz("""
        valido_en_columna(Matriz, Columna, Numero) :-
            findall(Elem, (member(Fila, Matriz), nth0(Columna, Fila, Elem)), ColumnaLista),
            \\+ member(Numero, ColumnaLista)
    """)
    
    # Regla: Verifica si un número NO está en el bloque 3x3
    motor_prolog.assertz("""
        valido_en_bloque(Matriz, Fila, Columna, Numero) :-
            FilaBloque is Fila // 3,
            ColumnaBloque is Columna // 3,
            FilaInicio is FilaBloque * 3,
            ColumnaInicio is ColumnaBloque * 3,
            findall(Elem,
                (between(0, 2, I),
                 between(0, 2, J),
                 FilaActual is FilaInicio + I,
                 ColumnaActual is ColumnaInicio + J,
                 nth0(FilaActual, Matriz, FilaLista),
                 nth0(ColumnaActual, FilaLista, Elem)),
                BloqueLista),
            \\+ member(Numero, BloqueLista)
    """)
    
    # Regla: Combina las tres validaciones
    motor_prolog.assertz("""
        es_movimiento_valido(Matriz, Fila, Columna, Numero) :-
            valido_en_fila(Matriz, Fila, Numero),
            valido_en_columna(Matriz, Columna, Numero),
            valido_en_bloque(Matriz, Fila, Columna, Numero)
    """)

    print("Reglas de validación de Sudoku cargadas en Prolog.")

def validar_numero_prolog(matriz, fila, col, num):
    # Valida si un número puede colocarse en una posición usando Prolog
    try:
        # Convierte la matriz NumPy a lista de listas para Prolog
        matriz_lista = matriz_numpy_a_lista(matriz)
        
        # Construye la consulta Prolog
        consulta = f"es_movimiento_valido({matriz_lista}, {fila}, {col}, {num})"
        
        # Ejecuta la consulta
        resultado = list(motor_prolog.query(consulta))
        
        # Si hay resultados, el movimiento es válido
        return len(resultado) > 0
        
    # Captura errores de validación
    except Exception as e:
        print(f"Error en validación Prolog: {e}")
        # En caso de error, retorna False por seguridad
        return False

# Configura las reglas de validación al cargar el módulo
configurar_reglas_sudoku_validacion()

