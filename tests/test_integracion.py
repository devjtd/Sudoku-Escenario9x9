"""
Pruebas de integración para el sistema Sudoku
Valida la interacción entre múltiples módulos y el flujo completo del juego
"""

import unittest
import numpy as np
import sys
import os
import csv

# Agregar src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from nucleo.logica_sudoku import (
    colocar_numero,
    es_tablero_valido,
    es_tablero_completo,
    TIPO_MATRIZ
)
from nucleo.generador_tableros import (
    generar_sudoku,
    crear_puzzle
)
from datos.gestor_puntuaciones import (
    guardar_puntuacion_jugador,
    cargar_puntuaciones_jugador
)


class TestIntegracionSudoku(unittest.TestCase):
    """Suite de pruebas de integración para el sistema completo"""
    
    def setUp(self):
        """Configura el entorno de prueba"""
        # Backup del archivo de puntuaciones
        self.archivo_puntuaciones = 'puntuaciones.csv'
        self.archivo_backup = 'puntuaciones.csv.backup'
        
        if os.path.exists(self.archivo_puntuaciones):
            if os.path.exists(self.archivo_backup):
                os.remove(self.archivo_backup)
            os.rename(self.archivo_puntuaciones, self.archivo_backup)

    def tearDown(self):
        """Limpia el entorno después de cada prueba"""
        # Elimina el archivo temporal
        if os.path.exists(self.archivo_puntuaciones):
            os.remove(self.archivo_puntuaciones)
        
        # Restaura el archivo original
        if os.path.exists(self.archivo_backup):
            os.rename(self.archivo_backup, self.archivo_puntuaciones)

    # ==================== TESTS DE FLUJO COMPLETO DE JUEGO ====================
    
    def test_flujo_completo_juego_ganado(self):
        """
        Simula un flujo completo de juego:
        1. Generar puzzle
        2. Colocar números
        3. Validar tablero
        4. Guardar puntuación
        5. Cargar puntuación
        """
        # 1. Generar puzzle
        resultado = generar_sudoku('facil')
        self.assertIsNotNone(resultado, "Debe generar un puzzle")
        
        puzzle, solucion = resultado
        
        # 2. Simular que el jugador completa el puzzle con la solución
        tablero_jugador = puzzle.copy()
        
        # Llenar todas las celdas vacías con la solución
        for i in range(9):
            for j in range(9):
                if tablero_jugador[i, j] == 0:
                    tablero_jugador = colocar_numero(
                        tablero_jugador, i, j, solucion[i, j]
                    )
        
        # 3. Validar que el tablero está completo y es válido
        self.assertTrue(es_tablero_completo(tablero_jugador),
                       "El tablero debe estar completo")
        self.assertTrue(es_tablero_valido(tablero_jugador),
                       "El tablero debe ser válido")
        
        # 4. Guardar puntuación
        nombre = 'TestPlayer'
        tiempo = 180.5
        errores = 2
        pistas = 1
        puntaje = 850
        estado = 'Ganado'
        
        guardar_puntuacion_jugador(nombre, tiempo, errores, pistas, puntaje, estado)
        
        # 5. Cargar y verificar puntuación
        puntuaciones = cargar_puntuaciones_jugador(nombre)
        
        self.assertEqual(len(puntuaciones), 1, "Debe haber una puntuación guardada")
        self.assertEqual(puntuaciones[0]['Nombre'], nombre)
        self.assertEqual(puntuaciones[0]['Estado'], estado)

    def test_flujo_juego_con_errores(self):
        """
        Simula un juego con movimientos incorrectos:
        1. Generar puzzle
        2. Intentar colocar número inválido
        3. Verificar que el tablero sigue siendo inválido
        """
        # 1. Generar puzzle
        puzzle, solucion = generar_sudoku('medio')
        
        # 2. Encontrar una celda vacía
        celda_vacia = None
        for i in range(9):
            for j in range(9):
                if puzzle[i, j] == 0:
                    celda_vacia = (i, j)
                    break
            if celda_vacia:
                break
        
        self.assertIsNotNone(celda_vacia, "Debe haber al menos una celda vacía")
        
        fila, col = celda_vacia
        numero_correcto = solucion[fila, col]
        
        # Encuentra un número incorrecto (diferente al correcto)
        numero_incorrecto = (numero_correcto % 9) + 1
        if numero_incorrecto == numero_correcto:
            numero_incorrecto = (numero_incorrecto % 9) + 1
        
        # 3. Coloca el número incorrecto
        tablero_con_error = colocar_numero(puzzle, fila, col, numero_incorrecto)
        
        # Llena el resto con la solución
        for i in range(9):
            for j in range(9):
                if tablero_con_error[i, j] == 0:
                    tablero_con_error = colocar_numero(
                        tablero_con_error, i, j, solucion[i, j]
                    )
        
        # 4. Verifica que el tablero es inválido
        self.assertTrue(es_tablero_completo(tablero_con_error),
                       "El tablero debe estar completo")
        self.assertFalse(es_tablero_valido(tablero_con_error),
                        "El tablero debe ser inválido debido al error")

    # ==================== TESTS DE GENERACIÓN Y VALIDACIÓN ====================
    
    def test_integracion_generacion_validacion(self):
        """
        Verifica que todos los puzzles generados son válidos
        y que sus soluciones son correctas
        """
        dificultades = ['facil', 'medio', 'dificil']
        
        for dificultad in dificultades:
            with self.subTest(dificultad=dificultad):
                # Genera puzzle
                puzzle, solucion = generar_sudoku(dificultad)
                
                # Verifica que la solución es válida
                self.assertTrue(es_tablero_valido(solucion),
                               f"La solución de dificultad {dificultad} debe ser válida")
                
                # Verifica que la solución está completa
                self.assertTrue(es_tablero_completo(solucion),
                               f"La solución de dificultad {dificultad} debe estar completa")
                
                # Verifica que el puzzle es consistente con la solución
                for i in range(9):
                    for j in range(9):
                        if puzzle[i, j] != 0:
                            self.assertEqual(puzzle[i, j], solucion[i, j],
                                           f"Celda [{i},{j}] del puzzle debe coincidir con solución")

    def test_integracion_multiples_puzzles(self):
        """
        Genera múltiples puzzles y verifica que todos son únicos y válidos
        """
        num_puzzles = 3
        puzzles = []
        
        for _ in range(num_puzzles):
            puzzle, solucion = generar_sudoku('facil')
            puzzles.append((puzzle, solucion))
            
            # Verifica validez
            self.assertTrue(es_tablero_valido(solucion),
                           "Cada solución debe ser válida")
        
        # Verifica que los puzzles son diferentes
        # (muy probable con generación aleatoria)
        for i in range(len(puzzles)):
            for j in range(i + 1, len(puzzles)):
                puzzle1, _ = puzzles[i]
                puzzle2, _ = puzzles[j]
                
                # Al menos deben diferir en alguna celda
                diferentes = not np.array_equal(puzzle1, puzzle2)
                self.assertTrue(diferentes,
                               "Los puzzles generados deben ser diferentes")

    # ==================== TESTS DE PERSISTENCIA ====================
    
    def test_integracion_multiples_jugadores(self):
        """
        Simula múltiples jugadores guardando y cargando puntuaciones
        """
        jugadores = [
            ('Player1', 100.0, 1, 0, 950, 'Ganado'),
            ('Player2', 150.0, 3, 2, 800, 'Ganado'),
            ('Player1', 120.0, 2, 1, 900, 'Ganado'),
            ('Player3', 200.0, 5, 3, 700, 'Perdido'),
            ('Player2', 180.0, 4, 2, 750, 'Ganado'),
        ]
        
        # Guarda todas las puntuaciones
        for nombre, tiempo, errores, pistas, puntaje, estado in jugadores:
            guardar_puntuacion_jugador(nombre, tiempo, errores, pistas, puntaje, estado)
        
        # Verifica puntuaciones de Player1
        puntuaciones_p1 = cargar_puntuaciones_jugador('Player1')
        self.assertEqual(len(puntuaciones_p1), 2,
                        "Player1 debe tener 2 puntuaciones")
        
        # Verifica puntuaciones de Player2
        puntuaciones_p2 = cargar_puntuaciones_jugador('Player2')
        self.assertEqual(len(puntuaciones_p2), 2,
                        "Player2 debe tener 2 puntuaciones")
        
        # Verifica puntuaciones de Player3
        puntuaciones_p3 = cargar_puntuaciones_jugador('Player3')
        self.assertEqual(len(puntuaciones_p3), 1,
                        "Player3 debe tener 1 puntuación")
        
        # Verifica todas las puntuaciones
        todas = cargar_puntuaciones_jugador()
        self.assertEqual(len(todas), 5,
                        "Debe haber 5 puntuaciones en total")

    def test_integracion_juego_completo_con_persistencia(self):
        """
        Simula un juego completo desde generación hasta guardado de puntuación
        """
        # 1. Generar puzzle
        puzzle, solucion = generar_sudoku('medio')
        
        # 2. Simular jugador resolviendo (con algunos errores)
        tablero = puzzle.copy()
        errores = 0
        pistas_usadas = 0
        
        # Resolver el puzzle
        for i in range(9):
            for j in range(9):
                if tablero[i, j] == 0:
                    # Simula uso de pista cada 10 celdas
                    if (i * 9 + j) % 10 == 0:
                        pistas_usadas += 1
                    
                    tablero = colocar_numero(tablero, i, j, solucion[i, j])
        
        # 3. Verificar que está completo y válido
        self.assertTrue(es_tablero_completo(tablero))
        self.assertTrue(es_tablero_valido(tablero))
        
        # 4. Calcular puntaje (fórmula simplificada)
        tiempo = 200.0
        puntaje = max(0, 1000 - errores * 50 - pistas_usadas * 20 - int(tiempo / 10))
        
        # 5. Guardar puntuación
        guardar_puntuacion_jugador('IntegrationTest', tiempo, errores, 
                                  pistas_usadas, puntaje, 'Ganado')
        
        # 6. Verificar que se guardó correctamente
        puntuaciones = cargar_puntuaciones_jugador('IntegrationTest')
        self.assertEqual(len(puntuaciones), 1)
        
        p = puntuaciones[0]
        self.assertEqual(p['Nombre'], 'IntegrationTest')
        self.assertEqual(p['Errores'], str(errores))
        self.assertEqual(p['Pistas'], str(pistas_usadas))
        self.assertEqual(p['Estado'], 'Ganado')

    # ==================== TESTS DE INMUTABILIDAD EN FLUJO COMPLETO ====================
    
    def test_integracion_inmutabilidad_flujo(self):
        """
        Verifica que la inmutabilidad se mantiene en todo el flujo del juego
        """
        # Genera puzzle
        puzzle_original, solucion_original = generar_sudoku('facil')
        
        # Guarda copias para verificar inmutabilidad
        puzzle_backup = puzzle_original.copy()
        solucion_backup = solucion_original.copy()
        
        # Simula jugadas
        tablero = puzzle_original
        for i in range(9):
            for j in range(9):
                if tablero[i, j] == 0:
                    # Coloca número (debe retornar nueva matriz)
                    tablero = colocar_numero(tablero, i, j, solucion_original[i, j])
        
        # Verifica que los originales NO cambiaron
        np.testing.assert_array_equal(puzzle_original, puzzle_backup,
                                     "El puzzle original no debe modificarse")
        np.testing.assert_array_equal(solucion_original, solucion_backup,
                                     "La solución original no debe modificarse")
        
        # Verifica que el tablero final es diferente
        self.assertFalse(np.array_equal(tablero, puzzle_original),
                        "El tablero final debe ser diferente al puzzle original")


if __name__ == '__main__':
    unittest.main(verbosity=2)
