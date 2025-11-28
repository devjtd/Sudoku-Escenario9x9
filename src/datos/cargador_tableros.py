# src/datos/cargador_tableros.py

import numpy as np
from nucleo.generador_tableros import generar_sudoku

def generar_tablero_nuevo(dificultad='medio'):
    # Genera un tablero de Sudoku con el nivel de dificultad especificado
    matriz_inicial, matriz_solucion = generar_sudoku(dificultad)
    
    if matriz_inicial is None:
        print("ERROR: No se pudo generar el tablero de Sudoku.")
        return None, None
    
    print("Tablero generado exitosamente.")
    return matriz_inicial, matriz_solucion
