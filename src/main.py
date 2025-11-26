# src/main.py

import pygame
import sys
import numpy as np
import random
import time
import csv
import os
from datetime import datetime

# Importa módulos propios de la lógica de datos y el núcleo del juego
from manejador_datos import cargar_y_limpiar_datos
from logica_nucleo import TIPO_MATRIZ, obtener_coordenadas_matriz, colocar_numero, actualizar_errores, es_tablero_completo, es_tablero_valido, resolver_tablero

import logica_prolog
from logica_prolog import validar_numero_prolog

# --- CONFIGURACIÓN DE PYGAME (INTERFAZ DE USUARIO) ---
ANCHO_PANTALLA = 1200
ALTO_PANTALLA = 750 
TITULO_JUEGO = "Escenario 9x9"

# --- RUTAS DE ASSETS (IMÁGENES) ---
RUTA_ICONO = 'assets/icono.png'
RUTA_FONDO_MENU = 'assets/fondo_menu.jpg'
RUTA_TITULO_IMAGEN = 'assets/titulo_logo.png'

# --- CONSTANTES DE COLOR ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLOR_FONDO_MENU = NEGRO 
COLOR_FONDO_JUEGO = (50, 50, 50) 

# --- COLORES DE BOTONES ---
COLOR_JUGAR_BASE = (60, 120, 220)
COLOR_JUGAR_HOVER = (90, 150, 250)
COLOR_SALIR_BASE = (255, 215, 0)
COLOR_SALIR_HOVER = (255, 230, 80)

# --- COLORES DE BOTONES JUEGO ---
COLOR_REINICIAR_BASE = (220, 100, 60)
COLOR_REINICIAR_HOVER = (250, 130, 90)
COLOR_NUEVO_BASE = (60, 180, 100)
COLOR_NUEVO_HOVER = (90, 210, 130)
COLOR_MENU_BASE = (100, 100, 200)
COLOR_MENU_HOVER = (130, 130, 230)
COLOR_PISTA_BASE = (147, 112, 219)
COLOR_PISTA_HOVER = (186, 85, 211)
COLOR_RESOLVER_BASE = (255, 140, 0)
COLOR_RESOLVER_HOVER = (255, 165, 0)

# --- ESTADOS DE JUEGO ---
ESTADO_MENU = "MENU"
ESTADO_JUEGO = "JUEGO"
ESTADO_VICTORIA = "VICTORIA"
ESTADO_SALIR = "SALIR"
ESTADO_PUNTUACIONES = "PUNTUACIONES"

# --- VARIABLES GLOBALES DE PUNTUACIÓN ---
NOMBRE_USUARIO = "Jugador"
TIEMPO_INICIO = 0
ERRORES_CONTADOR = 0
PISTAS_CONTADOR = 0
ESTADISTICAS_PARTIDA_ACTUAL = {}

# --- GESTIÓN DE ESTADOS ---
ESTADO_ACTUAL = ESTADO_MENU 

# --- CONFIGURACIÓN DEL TABLERO ---
TAMANO_GRILLA = 540
TAMANO_CELDA = TAMANO_GRILLA // 9
GROSOR_LINEA_FINA = 1
GROSOR_LINEA_GRUESA = 3
OFFSET_GRILLA_X = (ANCHO_PANTALLA - TAMANO_GRILLA) // 2 
OFFSET_GRILLA_Y = 150 

# --- COLORES DEL TABLERO (ESTILO) ---
COLOR_FIJO = (0, 0, 150)
COLOR_GRILLA_FINA = (150, 150, 150)
COLOR_GRILLA_GRUESA = (0, 0, 0)
COLOR_SELECCION = (100, 200, 255)
COLOR_ERROR = (255, 0, 0)

# --- CLASE DE BOTÓN BÁSICA ---
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_base, color_hover, accion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_actual = color_base
        self.accion = accion
        self.fuente = pygame.font.Font(None, 48)

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_actual, self.rect, 0, 8) 
        superficie_texto = self.fuente.render(self.texto, True, NEGRO)
        posicion_texto = (
            self.rect.x + (self.rect.width - superficie_texto.get_width()) // 2,
            self.rect.y + (self.rect.height - superficie_texto.get_height()) // 2
        )
        pantalla.blit(superficie_texto, posicion_texto)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(evento.pos):
                self.color_actual = self.color_hover
            else:
                self.color_actual = self.color_base
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos) and self.accion:
                self.accion()

class CajaTexto:
    def __init__(self, x, y, ancho, alto, texto=''):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_inactivo = pygame.Color('lightskyblue3')
        self.color_activo = pygame.Color('dodgerblue2')
        self.color = self.color_inactivo
        self.texto = texto
        self.fuente = pygame.font.Font(None, 32)
        self.txt_surface = self.fuente.render(texto, True, self.color)
        self.activo = False

    def manejar_evento(self, evento):
        global NOMBRE_USUARIO
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                self.activo = not self.activo
            else:
                self.activo = False
            self.color = self.color_activo if self.activo else self.color_inactivo
        
        if evento.type == pygame.KEYDOWN:
            if self.activo:
                if evento.key == pygame.K_RETURN:
                    self.activo = False
                    self.color = self.color_inactivo
                elif evento.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1]
                else:
                    if len(self.texto) < 15:
                        self.texto += evento.unicode
                
                self.txt_surface = self.fuente.render(self.texto, True, self.color)
                NOMBRE_USUARIO = self.texto

    def dibujar(self, pantalla):
        pantalla.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(pantalla, self.color, self.rect, 2)

# --- FUNCIONES DE ACCIÓN ---
def iniciar_juego():
    global ESTADO_ACTUAL, TIEMPO_INICIO, ERRORES_CONTADOR, PISTAS_CONTADOR
    print("Transición a la pantalla de JUEGO.")
    ESTADO_ACTUAL = ESTADO_JUEGO
    TIEMPO_INICIO = time.time()
    ERRORES_CONTADOR = 0
    PISTAS_CONTADOR = 0

def salir_juego():
    global ESTADO_ACTUAL
    print("Saliendo del juego.")
    ESTADO_ACTUAL = ESTADO_SALIR

def ver_puntuaciones():
    global ESTADO_ACTUAL
    print("Viendo puntuaciones.")
    ESTADO_ACTUAL = ESTADO_PUNTUACIONES

def guardar_puntuacion(nombre, tiempo, errores, pistas):
    archivo = 'scores.csv'
    existe = os.path.isfile(archivo)
    try:
        with open(archivo, 'a', newline='') as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(['Nombre', 'Tiempo', 'Errores', 'Pistas', 'Fecha'])
            writer.writerow([nombre, f"{tiempo:.2f}", errores, pistas, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
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

# --- FUNCIONES DE RENDERIZADO ---
def dibujar_grilla(pantalla):
    pygame.draw.rect(pantalla, BLANCO, (OFFSET_GRILLA_X, OFFSET_GRILLA_Y, TAMANO_GRILLA, TAMANO_GRILLA))
    for i in range(10): 
        grosor_linea = GROSOR_LINEA_GRUESA if i % 3 == 0 else GROSOR_LINEA_FINA
        color_linea = COLOR_GRILLA_GRUESA if i % 3 == 0 else COLOR_GRILLA_FINA
        posicion = OFFSET_GRILLA_X + i * TAMANO_CELDA
        pygame.draw.line(pantalla, color_linea, (posicion, OFFSET_GRILLA_Y), (posicion, OFFSET_GRILLA_Y + TAMANO_GRILLA), grosor_linea)
        posicion = OFFSET_GRILLA_Y + i * TAMANO_CELDA
        pygame.draw.line(pantalla, color_linea, (OFFSET_GRILLA_X, posicion), (OFFSET_GRILLA_X + TAMANO_GRILLA, posicion), grosor_linea)

def dibujar_seleccion(pantalla, celda_seleccionada):
    if celda_seleccionada:
        fila, columna = celda_seleccionada
        x = OFFSET_GRILLA_X + columna * TAMANO_CELDA
        y = OFFSET_GRILLA_Y + fila * TAMANO_CELDA
        pygame.draw.rect(pantalla, COLOR_SELECCION, (x, y, TAMANO_CELDA, TAMANO_CELDA), 4)

def dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores):
    fuente_numero = pygame.font.Font(None, 40)
    for fila in range(9):
        for columna in range(9):
            numero = matriz_actual[fila, columna]
            if numero != 0:
                es_fijo = matriz_fija[fila, columna] != 0
                es_error = matriz_errores[fila, columna] != 0
                color_texto = COLOR_ERROR if es_error else (COLOR_FIJO if es_fijo else NEGRO)
                texto_superficie = fuente_numero.render(str(numero), True, color_texto)
                pos_x = OFFSET_GRILLA_X + columna * TAMANO_CELDA + (TAMANO_CELDA - texto_superficie.get_width()) // 2
                pos_y = OFFSET_GRILLA_Y + fila * TAMANO_CELDA + (TAMANO_CELDA - texto_superficie.get_height()) // 2
                pantalla.blit(texto_superficie, (pos_x, pos_y))

def dibujar_victoria(pantalla, estadisticas=None):
    superficie_transparente = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    superficie_transparente.set_alpha(200)
    superficie_transparente.fill(NEGRO)
    pantalla.blit(superficie_transparente, (0, 0))
    
    fuente_victoria = pygame.font.Font(None, 100)
    texto_victoria = fuente_victoria.render("¡FELICIDADES!", True, (0, 255, 0))
    rect_victoria = texto_victoria.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 100))
    pantalla.blit(texto_victoria, rect_victoria)

    if estadisticas:
        fuente_stats = pygame.font.Font(None, 40)
        y_offset = ALTO_PANTALLA // 2
        textos = [
            f"Tiempo: {estadisticas['tiempo']:.2f}s",
            f"Errores: {estadisticas['errores']}",
            f"Pistas: {estadisticas['pistas']}"
        ]
        for texto in textos:
            surf = fuente_stats.render(texto, True, BLANCO)
            rect = surf.get_rect(center=(ANCHO_PANTALLA // 2, y_offset))
            pantalla.blit(surf, rect)
            y_offset += 40

    texto_instruccion = pygame.font.Font(None, 30).render("Haz clic para volver al tablero", True, (200, 200, 200))
    rect_inst = texto_instruccion.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50))
    pantalla.blit(texto_instruccion, rect_inst)

def dibujar_tabla_puntuaciones(pantalla, puntuaciones):
    pantalla.fill(COLOR_FONDO_JUEGO)
    fuente_titulo = pygame.font.Font(None, 60)
    titulo = fuente_titulo.render(f"Puntuaciones de {NOMBRE_USUARIO}", True, BLANCO)
    pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 50))

    if not puntuaciones:
        fuente_msg = pygame.font.Font(None, 40)
        msg = fuente_msg.render("No hay puntuaciones registradas.", True, BLANCO)
        pantalla.blit(msg, (ANCHO_PANTALLA // 2 - msg.get_width() // 2, 200))
    else:
        # Cabecera
        y = 150
        fuente_fila = pygame.font.Font(None, 30)
        cabecera = f"{'Fecha':<20} {'Tiempo':<10} {'Errores':<10} {'Pistas':<10}"
        surf_cab = fuente_fila.render(cabecera, True, (200, 200, 0))
        pantalla.blit(surf_cab, (ANCHO_PANTALLA // 2 - 200, y))
        y += 40
        
        # Filas (mostrar ultimas 10)
        for p in puntuaciones[-10:]:
            fila_str = f"{p['Fecha']:<20} {p['Tiempo']:<10} {p['Errores']:<10} {p['Pistas']:<10}"
            surf_fila = fuente_fila.render(fila_str, True, BLANCO)
            pantalla.blit(surf_fila, (ANCHO_PANTALLA // 2 - 200, y))
            y += 30

    # Instrucción para volver
    texto_volver = pygame.font.Font(None, 30).render("Presiona ESC o clic para volver", True, (200, 200, 200))
    pantalla.blit(texto_volver, (ANCHO_PANTALLA // 2 - texto_volver.get_width() // 2, ALTO_PANTALLA - 50))

# --- FUNCIÓN DE EJECUCIÓN PRINCIPAL ---
def ejecutar_juego():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption(TITULO_JUEGO)
    
    try:
        icono_imagen = pygame.image.load(RUTA_ICONO)
        pygame.display.set_icon(icono_imagen)
    except: pass
    
    fondo_menu_imagen = None
    try:
        fondo_menu_imagen = pygame.image.load(RUTA_FONDO_MENU).convert()
        fondo_menu_imagen = pygame.transform.scale(fondo_menu_imagen, (ANCHO_PANTALLA, ALTO_PANTALLA))
    except: pass
    
    titulo_imagen = None
    try:
        titulo_imagen = pygame.image.load(RUTA_TITULO_IMAGEN).convert_alpha()
    except: pass

    matriz_inicial, matriz_solucion = cargar_y_limpiar_datos()
    if matriz_inicial is None:
        pygame.quit()
        sys.exit()

    matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
    matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
    matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
    celda_seleccionada = None

    # UI Elements
    ANCHO_BOTON = 250
    ALTO_BOTON = 70 
    ESPACIO_Y = 100
    POSICION_X_BOTON = (ANCHO_PANTALLA - ANCHO_BOTON) // 2
    POSICION_Y_INICIO = ALTO_PANTALLA // 2 + 20

    boton_jugar = Boton(POSICION_X_BOTON, POSICION_Y_INICIO, ANCHO_BOTON, ALTO_BOTON, "Jugar", COLOR_JUGAR_BASE, COLOR_JUGAR_HOVER, iniciar_juego)
    boton_puntuaciones = Boton(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y, ANCHO_BOTON, ALTO_BOTON, "Ver Puntuaciones", COLOR_MENU_BASE, COLOR_MENU_HOVER, ver_puntuaciones)
    boton_salir = Boton(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y * 2, ANCHO_BOTON, ALTO_BOTON, "Salir", COLOR_SALIR_BASE, COLOR_SALIR_HOVER, salir_juego)
    botones_menu = [boton_jugar, boton_puntuaciones, boton_salir]
    
    caja_texto_usuario = CajaTexto(POSICION_X_BOTON, POSICION_Y_INICIO - 80, 250, 50, NOMBRE_USUARIO)

    # Game Buttons
    def accion_reiniciar():
        nonlocal matriz_actual, matriz_errores
        global TIEMPO_INICIO, ERRORES_CONTADOR, PISTAS_CONTADOR
        matriz_actual = matriz_fija.copy().astype(TIPO_MATRIZ)
        matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        TIEMPO_INICIO = time.time()
        ERRORES_CONTADOR = 0
        PISTAS_CONTADOR = 0
        print("Tablero reiniciado.")

    def accion_nuevo_juego():
        nonlocal matriz_actual, matriz_fija, matriz_errores, matriz_inicial, matriz_solucion
        global TIEMPO_INICIO, ERRORES_CONTADOR, PISTAS_CONTADOR
        nueva_matriz, nueva_solucion = cargar_y_limpiar_datos()
        if nueva_matriz is not None:
            matriz_inicial = nueva_matriz
            matriz_solucion = nueva_solucion
            matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            TIEMPO_INICIO = time.time()
            ERRORES_CONTADOR = 0
            PISTAS_CONTADOR = 0
            print("Nuevo juego generado.")

    def accion_pista():
        nonlocal matriz_actual, matriz_solucion, matriz_errores
        global PISTAS_CONTADOR
        if matriz_solucion is None: return
        celdas_vacias = [(f, c) for f in range(9) for c in range(9) if matriz_actual[f, c] == 0]
        if not celdas_vacias: return
        fila, col = random.choice(celdas_vacias)
        matriz_actual[fila, col] = matriz_solucion[fila, col]
        matriz_errores[fila, col] = 0
        PISTAS_CONTADOR += 1
        print(f"Pista dada en ({fila}, {col})")

    def accion_resolver():
        nonlocal matriz_actual, matriz_solucion, matriz_errores
        if matriz_solucion is not None:
            matriz_actual = resolver_tablero(matriz_solucion)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            print("Tablero resuelto.")

    def accion_volver_menu():
        global ESTADO_ACTUAL
        ESTADO_ACTUAL = ESTADO_MENU

    X_BOTONES_JUEGO = 950
    Y_INICIO_BOTONES = 200
    ANCHO_BOTON_JUEGO = 200
    ALTO_BOTON_JUEGO = 60
    ESPACIO_BOTONES = 80

    boton_reiniciar = Boton(X_BOTONES_JUEGO, Y_INICIO_BOTONES, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Reiniciar", COLOR_REINICIAR_BASE, COLOR_REINICIAR_HOVER, accion_reiniciar)
    boton_nuevo = Boton(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Nuevo Juego", COLOR_NUEVO_BASE, COLOR_NUEVO_HOVER, accion_nuevo_juego)
    boton_pista = Boton(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 2, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Pista", COLOR_PISTA_BASE, COLOR_PISTA_HOVER, accion_pista)
    boton_resolver = Boton(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 3, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Resolver", COLOR_RESOLVER_BASE, COLOR_RESOLVER_HOVER, accion_resolver)
    boton_menu_juego = Boton(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 4, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Menú", COLOR_MENU_BASE, COLOR_MENU_HOVER, accion_volver_menu)
    botones_juego = [boton_reiniciar, boton_nuevo, boton_pista, boton_resolver, boton_menu_juego]

    global ESTADO_ACTUAL, ESTADISTICAS_PARTIDA_ACTUAL
    while ESTADO_ACTUAL != ESTADO_SALIR: 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ESTADO_ACTUAL = ESTADO_SALIR
            
            if ESTADO_ACTUAL == ESTADO_MENU:
                for boton in botones_menu: boton.manejar_evento(evento)
                caja_texto_usuario.manejar_evento(evento)
            
            elif ESTADO_ACTUAL == ESTADO_JUEGO:
                for boton in botones_juego: boton.manejar_evento(evento)
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    celda_seleccionada = obtener_coordenadas_matriz(evento.pos, OFFSET_GRILLA_X, OFFSET_GRILLA_Y, TAMANO_CELDA)
                if evento.type == pygame.KEYDOWN and celda_seleccionada:
                    fila, columna = celda_seleccionada
                    if matriz_fija[fila, columna] == 0:
                        numero = None
                        if evento.key in [pygame.K_1, pygame.K_KP1]: numero = 1
                        elif evento.key in [pygame.K_2, pygame.K_KP2]: numero = 2
                        elif evento.key in [pygame.K_3, pygame.K_KP3]: numero = 3
                        elif evento.key in [pygame.K_4, pygame.K_KP4]: numero = 4
                        elif evento.key in [pygame.K_5, pygame.K_KP5]: numero = 5
                        elif evento.key in [pygame.K_6, pygame.K_KP6]: numero = 6
                        elif evento.key in [pygame.K_7, pygame.K_KP7]: numero = 7
                        elif evento.key in [pygame.K_8, pygame.K_KP8]: numero = 8
                        elif evento.key in [pygame.K_9, pygame.K_KP9]: numero = 9
                        elif evento.key in [pygame.K_BACKSPACE, pygame.K_DELETE]: numero = 0
                        
                        if numero is not None:
                            try:
                                matriz_para_validar = colocar_numero(matriz_actual, fila, columna, 0)
                                if numero != 0:
                                    es_valido = validar_numero_prolog(matriz_para_validar, fila, columna, numero)
                                    es_error = not es_valido
                                else:
                                    es_error = False
                                
                                matriz_actual = colocar_numero(matriz_actual, fila, columna, numero)
                                matriz_errores = actualizar_errores(matriz_errores, fila, columna, es_error)
                                if es_error:
                                    global ERRORES_CONTADOR
                                    ERRORES_CONTADOR += 1
                                
                                if not es_error and es_tablero_completo(matriz_actual):
                                    if es_tablero_valido(matriz_actual):
                                        print("¡VICTORIA!")
                                        tiempo_total = time.time() - TIEMPO_INICIO
                                        ESTADISTICAS_PARTIDA_ACTUAL = {
                                            'tiempo': tiempo_total,
                                            'errores': ERRORES_CONTADOR,
                                            'pistas': PISTAS_CONTADOR
                                        }
                                        guardar_puntuacion(NOMBRE_USUARIO, tiempo_total, ERRORES_CONTADOR, PISTAS_CONTADOR)
                                        ESTADO_ACTUAL = ESTADO_VICTORIA
                            except ValueError as e:
                                print(f"Error: {e}")

            elif ESTADO_ACTUAL == ESTADO_VICTORIA:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    ESTADO_ACTUAL = ESTADO_JUEGO
            
            elif ESTADO_ACTUAL == ESTADO_PUNTUACIONES:
                if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                    ESTADO_ACTUAL = ESTADO_MENU

        # Renderizado
        if ESTADO_ACTUAL == ESTADO_MENU:
            if fondo_menu_imagen: pantalla.blit(fondo_menu_imagen, (0, 0))
            else: pantalla.fill(COLOR_FONDO_MENU)
            if titulo_imagen: pantalla.blit(titulo_imagen, (ANCHO_PANTALLA // 2 - titulo_imagen.get_width() // 2, 80))
            else:
                fuente = pygame.font.Font(None, 80)
                pantalla.blit(fuente.render(TITULO_JUEGO, True, BLANCO), (ANCHO_PANTALLA // 2 - 200, 80))
            
            for boton in botones_menu: boton.dibujar(pantalla)
            caja_texto_usuario.dibujar(pantalla)
            
            # Etiqueta Usuario
            fuente_lbl = pygame.font.Font(None, 30)
            lbl = fuente_lbl.render("Usuario:", True, BLANCO)
            pantalla.blit(lbl, (caja_texto_usuario.rect.x, caja_texto_usuario.rect.y - 30))

        elif ESTADO_ACTUAL == ESTADO_JUEGO:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_seleccion(pantalla, celda_seleccionada)
            dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores)
            for boton in botones_juego: boton.dibujar(pantalla)

        elif ESTADO_ACTUAL == ESTADO_VICTORIA:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores)
            dibujar_victoria(pantalla, ESTADISTICAS_PARTIDA_ACTUAL)

        elif ESTADO_ACTUAL == ESTADO_PUNTUACIONES:
            puntuaciones = cargar_puntuaciones(NOMBRE_USUARIO)
            dibujar_tabla_puntuaciones(pantalla, puntuaciones)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    ejecutar_juego()