# src/logica_nucleo.py

import numpy as np

# Define el tipo de dato para las matrices de Sudoku (entero de 8 bits)
TIPO_MATRIZ = np.dtype('int8')

# Función Pura: Colocar un número (Garantizando Inmutabilidad)
def colocar_numero(matriz: np.ndarray, fila: int, columna: int, numero: int) -> np.ndarray:
    """
    Devuelve una NUEVA matriz con el número colocado en la posición (fila, columna).
    Asegura la inmutabilidad al trabajar sobre una copia de la matriz original.
    """
    # Verifica que las coordenadas y el número estén dentro de los rangos válidos
    if not (0 <= fila < 9 and 0 <= columna < 9 and 0 <= numero <= 9):
        raise ValueError("Coordenadas o número fuera de rango.")
    
    # Crea una copia de la matriz de entrada para evitar la mutación de datos
    nueva_matriz = matriz.copy()
    
    # Asigna el nuevo valor a la celda en la copia
    nueva_matriz[fila, columna] = numero
    
    # Retorna la nueva matriz con el cambio aplicado
    return nueva_matriz

# Funciones Puras Iniciales para la validación
def es_valido_en_fila(matriz: np.ndarray, fila: int, numero: int) -> bool:
    """Verifica si el número dado no se repite en la fila especificada de la matriz."""
    return numero not in matriz[fila, :]

# Función Pura: Mapeo de Coordenadas (Interacción UI)
def obtener_coordenadas_matriz(pos_mouse: tuple, offset_x: int, offset_y: int, tamano_celda: int) -> tuple:
    """
    Convierte la posición del mouse (x, y) en coordenadas de matriz (fila, columna).
    Retorna (fila, columna) si el clic es válido dentro de la grilla, o None si está fuera.
    """
    mouse_x, mouse_y = pos_mouse
    
    # Calcula la columna y fila relativas
    columna = (mouse_x - offset_x) // tamano_celda
    fila = (mouse_y - offset_y) // tamano_celda
    
    # Verifica si las coordenadas están dentro del rango 0-8
    if 0 <= fila < 9 and 0 <= columna < 9:
        return (int(fila), int(columna))
    else:
        return None