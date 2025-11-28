# src/persistencia.py
import csv
import os
from datetime import datetime

def guardar_puntuacion(nombre, tiempo, errores, pistas, puntaje, estado):
    archivo = 'scores.csv'
    nuevo_header = ['Nombre', 'Tiempo', 'Errores', 'Pistas', 'Puntaje', 'Estado', 'Fecha']
    filas_existentes = []
    header_actual = []

    if os.path.isfile(archivo):
        try:
            with open(archivo, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    header_actual = next(reader)
                    filas_existentes = list(reader)
                except StopIteration:
                    pass
        except Exception as e:
            print(f"Error al leer archivo: {e}")

    # Migración si el header es antiguo
    if header_actual and 'Puntaje' not in header_actual:
        print("Migrando archivo de puntuaciones al nuevo formato...")
        filas_migradas = []
        for fila in filas_existentes:
            # Asumimos formato antiguo: Nombre, Tiempo, Errores, Pistas, Fecha
            if len(fila) == 5:
                # Insertamos Puntaje=0 y Estado='N/A' antes de la Fecha
                fila.insert(4, 0) 
                fila.insert(5, 'N/A')
            filas_migradas.append(fila)
        filas_existentes = filas_migradas
    
    try:
        with open(archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(nuevo_header)
            writer.writerows(filas_existentes)
            writer.writerow([nombre, f"{tiempo:.2f}", errores, pistas, puntaje, estado, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        print("Puntuación guardada.")
    except Exception as e:
        print(f"Error al guardar puntuación: {e}")

def cargar_puntuaciones(nombre_filtro=None):
    archivo = 'scores.csv'
    puntuaciones = []
    if os.path.isfile(archivo):
        try:
            with open(archivo, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if nombre_filtro:
                        if row['Nombre'] == nombre_filtro:
                            puntuaciones.append(row)
                    else:
                        puntuaciones.append(row)
        except Exception as e:
            print(f"Error al cargar puntuaciones: {e}")
    return puntuaciones
