"""
Pruebas unitarias para el módulo gestor_puntuaciones.py
Valida el guardado y carga de puntuaciones de jugadores
"""

import unittest
import csv
import os
import sys
from datetime import datetime

# Agregar src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from datos.gestor_puntuaciones import (
    guardar_puntuacion_jugador,
    cargar_puntuaciones_jugador
)


class TestGestorPuntuaciones(unittest.TestCase):
    """Suite de pruebas para el gestor de puntuaciones"""
    
    def setUp(self):
        """Configura el entorno de prueba"""
        # Archivo de prueba temporal
        self.archivo_prueba = 'puntuaciones_test.csv'
        # Guarda el nombre del archivo original
        self.archivo_original = 'puntuaciones.csv'
        
        # Cambia temporalmente el archivo en el módulo
        import datos.gestor_puntuaciones as gp
        self.gp_module = gp
        # Guarda la referencia original
        self.archivo_backup = None
        if os.path.exists(self.archivo_original):
            # Hace backup del archivo original
            self.archivo_backup = self.archivo_original + '.backup'
            if os.path.exists(self.archivo_backup):
                os.remove(self.archivo_backup)
            os.rename(self.archivo_original, self.archivo_backup)

    def tearDown(self):
        """Limpia el entorno después de cada prueba"""
        # Elimina el archivo de prueba si existe
        if os.path.exists(self.archivo_prueba):
            os.remove(self.archivo_prueba)
        
        # Elimina el archivo temporal creado por las funciones
        if os.path.exists(self.archivo_original):
            os.remove(self.archivo_original)
        
        # Restaura el archivo original si existía
        if self.archivo_backup and os.path.exists(self.archivo_backup):
            os.rename(self.archivo_backup, self.archivo_original)

    # ==================== TESTS DE GUARDADO ====================
    
    def test_guardar_puntuacion_crea_archivo(self):
        """Verifica que crea el archivo CSV si no existe"""
        # Asegura que no existe
        if os.path.exists(self.archivo_original):
            os.remove(self.archivo_original)
        
        # Guarda una puntuación
        guardar_puntuacion_jugador('TestUser', 120.5, 3, 2, 850, 'Ganado')
        
        # Verifica que se creó el archivo
        self.assertTrue(os.path.exists(self.archivo_original),
                       "Debe crear el archivo CSV")

    def test_guardar_puntuacion_estructura_correcta(self):
        """Verifica que guarda con la estructura correcta"""
        guardar_puntuacion_jugador('TestUser', 120.5, 3, 2, 850, 'Ganado')
        
        # Lee el archivo
        with open(self.archivo_original, 'r') as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            
            # Verifica el encabezado
            expected_header = ['Nombre', 'Tiempo', 'Errores', 'Pistas', 'Puntaje', 'Estado', 'Fecha']
            self.assertEqual(header, expected_header,
                           "El encabezado debe tener la estructura correcta")

    def test_guardar_puntuacion_datos_correctos(self):
        """Verifica que guarda los datos correctamente"""
        nombre = 'TestUser'
        tiempo = 120.5
        errores = 3
        pistas = 2
        puntaje = 850
        estado = 'Ganado'
        
        guardar_puntuacion_jugador(nombre, tiempo, errores, pistas, puntaje, estado)
        
        # Lee el archivo
        with open(self.archivo_original, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Debe haber exactamente 1 fila
            self.assertEqual(len(rows), 1, "Debe haber una fila de datos")
            
            # Verifica los datos
            row = rows[0]
            self.assertEqual(row['Nombre'], nombre)
            self.assertEqual(row['Tiempo'], f"{tiempo:.2f}")
            self.assertEqual(row['Errores'], str(errores))
            self.assertEqual(row['Pistas'], str(pistas))
            self.assertEqual(row['Puntaje'], str(puntaje))
            self.assertEqual(row['Estado'], estado)
            # Verifica que tiene fecha
            self.assertIn('Fecha', row)
            self.assertIsNotNone(row['Fecha'])

    def test_guardar_multiples_puntuaciones(self):
        """Verifica que puede guardar múltiples puntuaciones"""
        # Guarda 3 puntuaciones
        guardar_puntuacion_jugador('User1', 100.0, 1, 0, 900, 'Ganado')
        guardar_puntuacion_jugador('User2', 150.0, 5, 3, 700, 'Ganado')
        guardar_puntuacion_jugador('User3', 200.0, 10, 5, 500, 'Perdido')
        
        # Lee el archivo
        with open(self.archivo_original, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Debe haber 3 filas
            self.assertEqual(len(rows), 3, "Debe haber 3 filas de datos")
            
            # Verifica los nombres
            nombres = [row['Nombre'] for row in rows]
            self.assertEqual(nombres, ['User1', 'User2', 'User3'])

    # ==================== TESTS DE CARGA ====================
    
    def test_cargar_puntuaciones_archivo_vacio(self):
        """Verifica que retorna lista vacía si no hay archivo"""
        # Asegura que no existe el archivo
        if os.path.exists(self.archivo_original):
            os.remove(self.archivo_original)
        
        puntuaciones = cargar_puntuaciones_jugador()
        
        self.assertEqual(puntuaciones, [], 
                        "Debe retornar lista vacía si no existe el archivo")

    def test_cargar_puntuaciones_todas(self):
        """Verifica que carga todas las puntuaciones sin filtro"""
        # Guarda varias puntuaciones
        guardar_puntuacion_jugador('User1', 100.0, 1, 0, 900, 'Ganado')
        guardar_puntuacion_jugador('User2', 150.0, 5, 3, 700, 'Ganado')
        guardar_puntuacion_jugador('User1', 120.0, 2, 1, 850, 'Ganado')
        
        # Carga todas
        puntuaciones = cargar_puntuaciones_jugador()
        
        self.assertEqual(len(puntuaciones), 3,
                        "Debe cargar las 3 puntuaciones")

    def test_cargar_puntuaciones_filtradas(self):
        """Verifica que filtra por nombre de jugador"""
        # Guarda varias puntuaciones
        guardar_puntuacion_jugador('User1', 100.0, 1, 0, 900, 'Ganado')
        guardar_puntuacion_jugador('User2', 150.0, 5, 3, 700, 'Ganado')
        guardar_puntuacion_jugador('User1', 120.0, 2, 1, 850, 'Ganado')
        
        # Carga solo de User1
        puntuaciones = cargar_puntuaciones_jugador('User1')
        
        self.assertEqual(len(puntuaciones), 2,
                        "Debe cargar solo las 2 puntuaciones de User1")
        
        # Verifica que todas son de User1
        for p in puntuaciones:
            self.assertEqual(p['Nombre'], 'User1')

    def test_cargar_puntuaciones_estructura(self):
        """Verifica que las puntuaciones cargadas tienen la estructura correcta"""
        guardar_puntuacion_jugador('TestUser', 120.5, 3, 2, 850, 'Ganado')
        
        puntuaciones = cargar_puntuaciones_jugador()
        
        self.assertEqual(len(puntuaciones), 1)
        
        # Verifica las claves del diccionario
        p = puntuaciones[0]
        expected_keys = {'Nombre', 'Tiempo', 'Errores', 'Pistas', 'Puntaje', 'Estado', 'Fecha'}
        self.assertEqual(set(p.keys()), expected_keys,
                        "Debe tener todas las claves esperadas")

    # ==================== TESTS DE MIGRACIÓN ====================
    
    def test_migracion_formato_antiguo(self):
        """Verifica que migra archivos del formato antiguo (sin Puntaje/Estado)"""
        # Crea un archivo con formato antiguo (5 columnas)
        with open(self.archivo_original, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Nombre', 'Tiempo', 'Errores', 'Pistas', 'Fecha'])
            writer.writerow(['OldUser', '100.00', '2', '1', '2025-12-01 10:00:00'])
        
        # Guarda una nueva puntuación (esto debería migrar el archivo)
        guardar_puntuacion_jugador('NewUser', 120.0, 3, 2, 850, 'Ganado')
        
        # Lee el archivo migrado
        with open(self.archivo_original, 'r') as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            rows = list(reader)
            
            # Verifica que tiene el nuevo formato
            expected_header = ['Nombre', 'Tiempo', 'Errores', 'Pistas', 'Puntaje', 'Estado', 'Fecha']
            self.assertEqual(header, expected_header,
                           "Debe tener el nuevo formato después de migración")
            
            # Verifica que hay 2 filas (la antigua migrada + la nueva)
            self.assertEqual(len(rows), 2)
            
            # Verifica que la fila antigua tiene valores por defecto
            old_row = rows[0]
            self.assertEqual(old_row['Nombre'], 'OldUser')
            self.assertEqual(old_row['Puntaje'], '0')
            self.assertEqual(old_row['Estado'], 'N/A')

    def test_formato_fecha(self):
        """Verifica que la fecha se guarda en el formato correcto"""
        guardar_puntuacion_jugador('TestUser', 120.5, 3, 2, 850, 'Ganado')
        
        puntuaciones = cargar_puntuaciones_jugador()
        fecha_str = puntuaciones[0]['Fecha']
        
        # Intenta parsear la fecha
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            # Si llega aquí, el formato es correcto
            self.assertIsInstance(fecha, datetime)
        except ValueError:
            self.fail("La fecha no tiene el formato esperado 'YYYY-MM-DD HH:MM:SS'")


if __name__ == '__main__':
    unittest.main(verbosity=2)
