"""
Pruebas unitarias para el módulo generador_tableros.py
Valida la generación de tableros, validación y creación de puzzles
"""

import unittest
import numpy as np
import sys
import os

# Agregar src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from nucleo.generador_tableros import (
    es_valido_python,
    resolver_sudoku,
    generar_tablero_completo,
    crear_puzzle,
    generar_sudoku
)
from nucleo.logica_sudoku import TIPO_MATRIZ, es_tablero_valido


class TestGeneradorTableros(unittest.TestCase):
    """Suite de pruebas para el generador de tableros"""
    
    def setUp(self):
        """Configura los datos de prueba"""
        # Tablero vacío
        self.tablero_vacio = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        
        # Tablero parcialmente lleno válido
        self.tablero_parcial = np.array([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ], dtype=TIPO_MATRIZ)
        
        # Tablero completo válido
        self.tablero_completo = np.array([
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ], dtype=TIPO_MATRIZ)

    # ==================== TESTS DE VALIDACIÓN ====================
    
    def test_es_valido_python_fila_valida(self):
        """Verifica que acepta números válidos en fila"""
        tablero = self.tablero_parcial.copy()
        # Intenta colocar 4 en posición [0, 2] (vacía)
        self.assertTrue(es_valido_python(tablero, 0, 2, 4),
                       "Debe aceptar número válido en fila")

    def test_es_valido_python_fila_invalida(self):
        """Verifica que rechaza números duplicados en fila"""
        tablero = self.tablero_parcial.copy()
        # Intenta colocar 5 en [0, 2], pero 5 ya está en [0, 0]
        self.assertFalse(es_valido_python(tablero, 0, 2, 5),
                        "Debe rechazar número duplicado en fila")

    def test_es_valido_python_columna_invalida(self):
        """Verifica que rechaza números duplicados en columna"""
        tablero = self.tablero_parcial.copy()
        # Intenta colocar 5 en [1, 0], pero 5 ya está en [0, 0]
        self.assertFalse(es_valido_python(tablero, 1, 0, 5),
                        "Debe rechazar número duplicado en columna")

    def test_es_valido_python_bloque_invalido(self):
        """Verifica que rechaza números duplicados en bloque 3x3"""
        tablero = self.tablero_parcial.copy()
        # Intenta colocar 5 en [1, 1], pero 5 ya está en el mismo bloque [0, 0]
        self.assertFalse(es_valido_python(tablero, 1, 1, 5),
                        "Debe rechazar número duplicado en bloque 3x3")

    def test_es_valido_python_posicion_valida(self):
        """Verifica validación completa (fila, columna, bloque)"""
        tablero = self.tablero_parcial.copy()
        # 2 es válido en [0, 2]: no está en fila 0, columna 2, ni bloque superior-izquierdo
        self.assertTrue(es_valido_python(tablero, 0, 2, 2),
                       "Debe aceptar número válido en todas las dimensiones")

    # ==================== TESTS DE GENERACIÓN DE TABLEROS ====================
    
    def test_generar_tablero_completo_estructura(self):
        """Verifica que genera un tablero 9x9"""
        tablero = generar_tablero_completo()
        
        self.assertIsNotNone(tablero, "Debe generar un tablero")
        self.assertEqual(tablero.shape, (9, 9), 
                        "Debe ser una matriz 9x9")

    def test_generar_tablero_completo_validez(self):
        """Verifica que el tablero generado es válido"""
        tablero = generar_tablero_completo()
        
        self.assertIsNotNone(tablero, "Debe generar un tablero")
        self.assertTrue(es_tablero_valido(tablero),
                       "El tablero generado debe ser válido según reglas de Sudoku")

    def test_generar_tablero_completo_sin_ceros(self):
        """Verifica que el tablero generado está completamente lleno"""
        tablero = generar_tablero_completo()
        
        self.assertIsNotNone(tablero, "Debe generar un tablero")
        self.assertFalse(np.any(tablero == 0),
                        "El tablero completo no debe tener celdas vacías (ceros)")

    def test_generar_tablero_completo_rango_valores(self):
        """Verifica que todos los valores están en el rango [1-9]"""
        tablero = generar_tablero_completo()
        
        self.assertIsNotNone(tablero, "Debe generar un tablero")
        self.assertTrue(np.all(tablero >= 1) and np.all(tablero <= 9),
                       "Todos los valores deben estar entre 1 y 9")

    # ==================== TESTS DE CREACIÓN DE PUZZLES ====================
    
    def test_crear_puzzle_estructura(self):
        """Verifica que crea un puzzle con la estructura correcta"""
        puzzle = crear_puzzle(self.tablero_completo, 'facil')
        
        self.assertIsNotNone(puzzle, "Debe crear un puzzle")
        self.assertEqual(puzzle.shape, (9, 9), "Debe ser una matriz 9x9")

    def test_crear_puzzle_inmutabilidad(self):
        """Verifica que NO modifica el tablero original"""
        original = self.tablero_completo.copy()
        puzzle = crear_puzzle(original, 'facil')
        
        # El tablero original no debe cambiar
        np.testing.assert_array_equal(original, self.tablero_completo,
                                     "No debe modificar el tablero original")

    def test_crear_puzzle_dificultad_facil(self):
        """Verifica que la dificultad fácil remueve la cantidad correcta"""
        puzzle = crear_puzzle(self.tablero_completo, 'facil')
        
        # Cuenta cuántos ceros hay (números removidos)
        ceros = np.count_nonzero(puzzle == 0)
        
        # Dificultad fácil: 35-40 números removidos
        self.assertGreaterEqual(ceros, 35, 
                               "Dificultad fácil debe remover al menos 35 números")
        self.assertLessEqual(ceros, 40, 
                            "Dificultad fácil debe remover máximo 40 números")

    def test_crear_puzzle_dificultad_medio(self):
        """Verifica que la dificultad media remueve la cantidad correcta"""
        puzzle = crear_puzzle(self.tablero_completo, 'medio')
        
        ceros = np.count_nonzero(puzzle == 0)
        
        # Dificultad medio: 45-50 números removidos
        self.assertGreaterEqual(ceros, 45,
                               "Dificultad medio debe remover al menos 45 números")
        self.assertLessEqual(ceros, 50,
                            "Dificultad medio debe remover máximo 50 números")

    def test_crear_puzzle_dificultad_dificil(self):
        """Verifica que la dificultad difícil remueve la cantidad correcta"""
        puzzle = crear_puzzle(self.tablero_completo, 'dificil')
        
        ceros = np.count_nonzero(puzzle == 0)
        
        # Dificultad difícil: 55-60 números removidos
        self.assertGreaterEqual(ceros, 55,
                               "Dificultad difícil debe remover al menos 55 números")
        self.assertLessEqual(ceros, 60,
                            "Dificultad difícil debe remover máximo 60 números")

    def test_crear_puzzle_dificultad_invalida(self):
        """Verifica que usa 'medio' como default para dificultad inválida"""
        puzzle = crear_puzzle(self.tablero_completo, 'super_dificil')
        
        ceros = np.count_nonzero(puzzle == 0)
        
        # Debe usar 'medio' por defecto: 45-50 números removidos
        self.assertGreaterEqual(ceros, 45)
        self.assertLessEqual(ceros, 50)

    # ==================== TESTS DE GENERACIÓN COMPLETA ====================
    
    def test_generar_sudoku_retorna_tupla(self):
        """Verifica que generar_sudoku retorna puzzle y solución"""
        resultado = generar_sudoku('facil')
        
        self.assertIsNotNone(resultado, "Debe retornar un resultado")
        self.assertIsInstance(resultado, tuple, "Debe retornar una tupla")
        self.assertEqual(len(resultado), 2, 
                        "Debe retornar tupla de 2 elementos (puzzle, solución)")

    def test_generar_sudoku_puzzle_valido(self):
        """Verifica que el puzzle generado tiene estructura válida"""
        puzzle, solucion = generar_sudoku('medio')
        
        self.assertIsNotNone(puzzle, "Puzzle no debe ser None")
        self.assertIsNotNone(solucion, "Solución no debe ser None")
        self.assertEqual(puzzle.shape, (9, 9), "Puzzle debe ser 9x9")
        self.assertEqual(solucion.shape, (9, 9), "Solución debe ser 9x9")

    def test_generar_sudoku_solucion_valida(self):
        """Verifica que la solución generada es válida"""
        puzzle, solucion = generar_sudoku('facil')
        
        self.assertTrue(es_tablero_valido(solucion),
                       "La solución debe ser un tablero válido de Sudoku")

    def test_generar_sudoku_puzzle_incompleto(self):
        """Verifica que el puzzle tiene celdas vacías"""
        puzzle, solucion = generar_sudoku('medio')
        
        self.assertTrue(np.any(puzzle == 0),
                       "El puzzle debe tener celdas vacías (ceros)")

    def test_generar_sudoku_consistencia(self):
        """Verifica que los números del puzzle coinciden con la solución"""
        puzzle, solucion = generar_sudoku('facil')
        
        # Todas las celdas no-vacías del puzzle deben coincidir con la solución
        for i in range(9):
            for j in range(9):
                if puzzle[i, j] != 0:
                    self.assertEqual(puzzle[i, j], solucion[i, j],
                                   f"Celda [{i},{j}] del puzzle debe coincidir con solución")

    # ==================== TESTS DE RESOLVER SUDOKU ====================
    
    def test_resolver_sudoku_tablero_parcial(self):
        """Verifica que puede resolver un tablero parcial"""
        tablero = self.tablero_parcial.copy()
        resultado = resolver_sudoku(tablero)
        
        self.assertTrue(resultado, "Debe poder resolver el tablero")
        self.assertTrue(es_tablero_valido(tablero),
                       "El tablero resuelto debe ser válido")
        self.assertFalse(np.any(tablero == 0),
                        "El tablero resuelto no debe tener ceros")


if __name__ == '__main__':
    unittest.main(verbosity=2)
