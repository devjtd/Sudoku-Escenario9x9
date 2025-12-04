"""
Pruebas unitarias para el módulo logica_sudoku.py
Valida funciones puras, inmutabilidad y lógica de validación del Sudoku
"""

import unittest
import numpy as np
import sys
import os

# Agregar src al path para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from nucleo.logica_sudoku import (
    colocar_numero, 
    es_valido_en_fila, 
    obtener_coordenadas_matriz,
    actualizar_errores, 
    es_tablero_completo,
    es_tablero_valido,
    es_grupo_valido,
    resolver_tablero,
    TIPO_MATRIZ
)


class TestLogicaSudoku(unittest.TestCase):
    """Suite de pruebas para la lógica del Sudoku"""
    
    def setUp(self):
        """Configura los datos de prueba antes de cada test"""
        # Tablero vacío 9x9
        self.tablero_vacio = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        
        # Tablero válido completo (solución válida de Sudoku)
        self.tablero_valido = np.array([
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
        
        # Tablero parcialmente lleno
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

    # ==================== TESTS DE INMUTABILIDAD ====================
    
    def test_colocar_numero_inmutabilidad(self):
        """Verifica que colocar_numero NO modifica la matriz original"""
        original = self.tablero_vacio.copy()
        nuevo = colocar_numero(original, 0, 0, 5)
        
        # La matriz original NO debe cambiar
        self.assertEqual(original[0, 0], 0, 
                        "La matriz original no debe modificarse (inmutabilidad)")
        # La nueva matriz SÍ debe tener el cambio
        self.assertEqual(nuevo[0, 0], 5, 
                        "La nueva matriz debe tener el valor actualizado")
        # Deben ser objetos diferentes en memoria
        self.assertIsNot(original, nuevo, 
                        "Debe retornar un nuevo objeto ndarray")

    def test_actualizar_errores_inmutabilidad(self):
        """Verifica que actualizar_errores NO modifica la matriz original"""
        errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        nuevos_errores = actualizar_errores(errores, 0, 0, True)
        
        # Matriz original no debe cambiar
        self.assertEqual(errores[0, 0], 0, 
                        "Matriz de errores original no debe cambiar")
        # Nueva matriz debe marcar el error
        self.assertEqual(nuevos_errores[0, 0], 1, 
                        "Nueva matriz debe marcar el error")
        # Deben ser objetos diferentes
        self.assertIsNot(errores, nuevos_errores)

    def test_resolver_tablero_inmutabilidad(self):
        """Verifica que resolver_tablero retorna una copia"""
        solucion = self.tablero_valido.copy()
        copia = resolver_tablero(solucion)
        
        # Deben ser objetos diferentes
        self.assertIsNot(solucion, copia, 
                        "Debe retornar una copia, no la misma referencia")
        # Pero con el mismo contenido
        np.testing.assert_array_equal(solucion, copia, 
                                     "El contenido debe ser idéntico")

    # ==================== TESTS DE VALIDACIÓN ====================
    
    def test_es_valido_en_fila_numero_repetido(self):
        """Verifica que detecta números repetidos en fila"""
        tablero = self.tablero_vacio.copy()
        tablero[0, 0] = 5
        
        # 5 ya está en la fila 0, debe ser inválido
        self.assertFalse(es_valido_en_fila(tablero, 0, 5), 
                        "No debe permitir repetir número en fila")

    def test_es_valido_en_fila_numero_nuevo(self):
        """Verifica que acepta números nuevos en fila"""
        tablero = self.tablero_vacio.copy()
        tablero[0, 0] = 5
        
        # 6 no está en la fila 0, debe ser válido
        self.assertTrue(es_valido_en_fila(tablero, 0, 6), 
                       "Debe permitir número nuevo en fila")

    def test_es_tablero_valido_completo(self):
        """Verifica que reconoce un tablero válido completo"""
        self.assertTrue(es_tablero_valido(self.tablero_valido), 
                       "Debe validar un tablero correcto")

    def test_es_tablero_invalido_fila_duplicada(self):
        """Verifica que detecta duplicados en fila"""
        tablero_invalido = self.tablero_valido.copy()
        # Introduce error: duplica el 5 en la primera fila
        tablero_invalido[0, 1] = 5  # Ya hay un 5 en [0, 0]
        
        self.assertFalse(es_tablero_valido(tablero_invalido), 
                        "Debe rechazar tablero con duplicados en fila")

    def test_es_tablero_invalido_columna_duplicada(self):
        """Verifica que detecta duplicados en columna"""
        tablero_invalido = self.tablero_valido.copy()
        # Introduce error: duplica el 5 en la primera columna
        tablero_invalido[1, 0] = 5  # Ya hay un 5 en [0, 0]
        
        self.assertFalse(es_tablero_valido(tablero_invalido), 
                        "Debe rechazar tablero con duplicados en columna")

    def test_es_tablero_completo_vacio(self):
        """Verifica que detecta tablero incompleto"""
        self.assertFalse(es_tablero_completo(self.tablero_vacio), 
                        "Tablero vacío no debe estar completo")

    def test_es_tablero_completo_lleno(self):
        """Verifica que detecta tablero completo"""
        self.assertTrue(es_tablero_completo(self.tablero_valido), 
                       "Tablero válido debe estar completo")

    def test_es_tablero_completo_parcial(self):
        """Verifica que detecta tablero parcialmente lleno"""
        self.assertFalse(es_tablero_completo(self.tablero_parcial), 
                        "Tablero parcial no debe estar completo")

    def test_es_grupo_valido_correcto(self):
        """Verifica que valida grupos correctos"""
        grupo_valido = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=TIPO_MATRIZ)
        self.assertTrue(es_grupo_valido(grupo_valido), 
                       "Debe validar grupo con todos los números del 1 al 9")

    def test_es_grupo_valido_incorrecto(self):
        """Verifica que rechaza grupos incorrectos"""
        grupo_invalido = np.array([1, 1, 3, 4, 5, 6, 7, 8, 9], dtype=TIPO_MATRIZ)
        self.assertFalse(es_grupo_valido(grupo_invalido), 
                        "Debe rechazar grupo con números duplicados")

    # ==================== TESTS DE COORDENADAS ====================
    
    def test_obtener_coordenadas_matriz_validas(self):
        """Verifica conversión correcta de coordenadas del mouse"""
        # Simula click en celda (0, 0) con offset 50 y tamaño 60
        pos_mouse = (50, 50)  # Justo en el inicio
        coords = obtener_coordenadas_matriz(pos_mouse, 50, 50, 60)
        
        self.assertIsNotNone(coords, "Debe retornar coordenadas válidas")
        self.assertEqual(coords, (0, 0), "Debe retornar (0, 0)")

    def test_obtener_coordenadas_matriz_centro(self):
        """Verifica conversión de coordenadas en el centro del tablero"""
        # Simula click en celda (4, 4) - centro del tablero
        pos_mouse = (50 + 4*60 + 30, 50 + 4*60 + 30)  # Centro de la celda
        coords = obtener_coordenadas_matriz(pos_mouse, 50, 50, 60)
        
        self.assertEqual(coords, (4, 4), "Debe retornar coordenadas del centro")

    def test_obtener_coordenadas_matriz_fuera_rango(self):
        """Verifica que retorna None para clicks fuera del tablero"""
        # Click fuera del tablero
        pos_mouse = (10, 10)  # Antes del offset
        coords = obtener_coordenadas_matriz(pos_mouse, 50, 50, 60)
        
        self.assertIsNone(coords, "Debe retornar None para clicks fuera del tablero")

    def test_obtener_coordenadas_matriz_limite_superior(self):
        """Verifica que retorna None para coordenadas >= 9"""
        # Click más allá de la celda (8, 8)
        pos_mouse = (50 + 9*60, 50 + 9*60)
        coords = obtener_coordenadas_matriz(pos_mouse, 50, 50, 60)
        
        self.assertIsNone(coords, "Debe retornar None para coordenadas >= 9")

    # ==================== TESTS DE VALIDACIÓN DE PARÁMETROS ====================
    
    def test_colocar_numero_fila_invalida(self):
        """Verifica que rechaza fila fuera de rango"""
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, -1, 0, 5)
        
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, 9, 0, 5)

    def test_colocar_numero_columna_invalida(self):
        """Verifica que rechaza columna fuera de rango"""
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, 0, -1, 5)
        
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, 0, 9, 5)

    def test_colocar_numero_valor_invalido(self):
        """Verifica que rechaza números fuera de rango [0-9]"""
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, 0, 0, -1)
        
        with self.assertRaises(ValueError):
            colocar_numero(self.tablero_vacio, 0, 0, 10)

    # ==================== TESTS DE ACTUALIZACIÓN DE ERRORES ====================
    
    def test_actualizar_errores_marcar_error(self):
        """Verifica que marca errores correctamente"""
        errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        nuevos = actualizar_errores(errores, 3, 3, True)
        
        self.assertEqual(nuevos[3, 3], 1, "Debe marcar la celda como error")

    def test_actualizar_errores_limpiar_error(self):
        """Verifica que limpia errores correctamente"""
        errores = np.ones((9, 9), dtype=TIPO_MATRIZ)
        nuevos = actualizar_errores(errores, 3, 3, False)
        
        self.assertEqual(nuevos[3, 3], 0, "Debe limpiar el error de la celda")


if __name__ == '__main__':
    unittest.main(verbosity=2)
