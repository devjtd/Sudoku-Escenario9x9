# src/generador_sudoku.py

import numpy as np
import random
from logica_nucleo import TIPO_MATRIZ
from logica_prolog import validar_numero_prolog

def es_valido_python(matriz, fila, col, num):
    """
    Validación en Python (fallback si Prolog falla).
    Verifica si un número puede colocarse en una posición específica.
    
    Args:
        matriz: Matriz NumPy 9x9 del tablero actual
        fila: Índice de fila (0-8)
        col: Índice de columna (0-8)
        num: Número a validar (1-9)
    
    Returns:
        bool: True si el movimiento es válido, False en caso contrario
    """
    # Verifica la fila
    if num in matriz[fila, :]:
        return False
    
    # Verifica la columna
    if num in matriz[:, col]:
        return False
    
    # Verifica el bloque 3x3
    fila_bloque = (fila // 3) * 3
    col_bloque = (col // 3) * 3
    bloque = matriz[fila_bloque:fila_bloque + 3, col_bloque:col_bloque + 3]
    if num in bloque:
        return False
    
    return True

def resolver_sudoku(matriz):
    """
    Resuelve un tablero de Sudoku usando backtracking.
    
    Args:
        matriz: Matriz NumPy 9x9 del tablero a resolver
    
    Returns:
        bool: True si se resolvió exitosamente, False en caso contrario
    """
    # Busca la primera celda vacía (valor 0)
    for fila in range(9):
        for col in range(9):
            if matriz[fila, col] == 0:
                # Intenta números del 1 al 9
                for num in range(1, 10):
                    # Primero intenta validar con Prolog
                    if validar_numero_prolog(matriz, fila, col, num):
                        # Coloca el número
                        matriz[fila, col] = num
                        
                        # Recursivamente intenta resolver el resto
                        if resolver_sudoku(matriz):
                            return True
                        
                        # Si no funciona, retrocede (backtracking)
                        matriz[fila, col] = 0
                    # Si Prolog falla, usa validación Python como fallback
                    elif es_valido_python(matriz, fila, col, num):
                        matriz[fila, col] = num
                        
                        if resolver_sudoku(matriz):
                            return True
                        
                        matriz[fila, col] = 0
                
                # Si ningún número funciona, retorna False
                return False
    
    # Si no hay celdas vacías, el tablero está resuelto
    return True

def generar_tablero_completo():
    """
    Genera un tablero de Sudoku 9x9 completo y válido.
    Usa backtracking con números aleatorios para crear variedad.
    
    Returns:
        np.ndarray: Matriz NumPy 9x9 con un tablero de Sudoku completo
    """
    print("Generando tablero de Sudoku completo...")
    
    # Crea una matriz vacía
    matriz = np.zeros((9, 9), dtype=TIPO_MATRIZ)
    
    # Función auxiliar para llenar el tablero con backtracking
    def llenar_tablero(fila, col):
        # Si llegamos al final del tablero, terminamos
        if fila == 9:
            return True
        
        # Calcula la siguiente posición
        siguiente_fila = fila if col < 8 else fila + 1
        siguiente_col = (col + 1) % 9
        
        # Crea una lista de números del 1 al 9 en orden aleatorio
        numeros = list(range(1, 10))
        random.shuffle(numeros)
        
        # Intenta cada número
        for num in numeros:
            # Valida con Prolog primero
            if validar_numero_prolog(matriz, fila, col, num):
                matriz[fila, col] = num
                
                # Recursivamente llena el resto del tablero
                if llenar_tablero(siguiente_fila, siguiente_col):
                    return True
                
                # Backtracking
                matriz[fila, col] = 0
            # Fallback a validación Python
            elif es_valido_python(matriz, fila, col, num):
                matriz[fila, col] = num
                
                if llenar_tablero(siguiente_fila, siguiente_col):
                    return True
                
                matriz[fila, col] = 0
        
        # Si ningún número funciona, retrocede
        return False
    
    # Inicia el llenado desde la posición (0, 0)
    if llenar_tablero(0, 0):
        print("Tablero completo generado exitosamente.")
        return matriz
    else:
        print("ERROR: No se pudo generar el tablero.")
        return None

def crear_puzzle(tablero_completo, dificultad='medio'):
    """
    Crea un puzzle de Sudoku removiendo números de un tablero completo.
    
    Args:
        tablero_completo: Matriz NumPy 9x9 con un tablero completo
        dificultad: Nivel de dificultad ('facil', 'medio', 'dificil')
    
    Returns:
        np.ndarray: Matriz NumPy 9x9 con el puzzle (algunos números removidos)
    """
    # Define cuántos números remover según la dificultad
    niveles_dificultad = {
        'facil': (35, 40),    # 35-40 números removidos
        'medio': (45, 50),    # 45-50 números removidos
        'dificil': (55, 60)   # 55-60 números removidos
    }
    
    # Obtiene el rango de números a remover
    if dificultad not in niveles_dificultad:
        print(f"Advertencia: Dificultad '{dificultad}' no reconocida. Usando 'medio'.")
        dificultad = 'medio'
    
    min_remover, max_remover = niveles_dificultad[dificultad]
    num_remover = random.randint(min_remover, max_remover)
    
    print(f"Creando puzzle de dificultad '{dificultad}' (removiendo {num_remover} números)...")
    
    # Crea una copia del tablero completo
    puzzle = tablero_completo.copy()
    
    # Crea una lista de todas las posiciones (81 celdas)
    posiciones = [(fila, col) for fila in range(9) for col in range(9)]
    random.shuffle(posiciones)
    
    # Remueve números de posiciones aleatorias
    removidos = 0
    for fila, col in posiciones:
        if removidos >= num_remover:
            break
        
        # Guarda el valor original
        valor_original = puzzle[fila, col]
        
        # Remueve el número (lo pone en 0)
        puzzle[fila, col] = 0
        removidos += 1
    
    print(f"Puzzle creado con {removidos} números removidos.")
    return puzzle

def generar_sudoku(dificultad='medio'):
    """
    Función principal para generar un puzzle de Sudoku completo.
    
    Args:
        dificultad: Nivel de dificultad ('facil', 'medio', 'dificil')
    
    Returns:
        np.ndarray: Matriz NumPy 9x9 con el puzzle de Sudoku
    """
    # Genera un tablero completo
    tablero_completo = generar_tablero_completo()

    # Muestra la matriz completa en consola (Solución)
    if tablero_completo is not None:
        print("\n" + "="*40)
        print("TABLERO COMPLETO (SOLUCIÓN):")
        print(tablero_completo)
        print("="*40 + "\n")
    
    if tablero_completo is None:
        return None
    
    # Crea el puzzle removiendo números
    puzzle = crear_puzzle(tablero_completo, dificultad)
    
    return puzzle
