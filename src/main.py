# src/main.py

import pygame
import sys
import numpy as np
import random
import time

# Importa módulos propios refactorizados
from config import *
from ui import Boton, CajaTexto
from renderizado import (
    dibujar_grilla, dibujar_seleccion, dibujar_numeros, 
    dibujar_victoria, dibujar_derrota, dibujar_tabla_puntuaciones
)
from persistencia import guardar_puntuacion, cargar_puntuaciones
from manejador_datos import cargar_y_limpiar_datos
from logica_nucleo import (
    TIPO_MATRIZ, obtener_coordenadas_matriz, colocar_numero, 
    actualizar_errores, es_tablero_completo, es_tablero_valido, resolver_tablero
)
from logica_prolog import validar_numero_prolog

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

    # Estado del juego (Variables locales en lugar de globales)
    estado_actual = ESTADO_MENU
    nombre_usuario = "Jugador"
    tiempo_inicio = 0
    errores_contador = 0
    pistas_contador = 0
    estadisticas_partida_actual = {}
    
    matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
    matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
    matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
    celda_seleccionada = None

    # --- FUNCIONES DE ACCIÓN (Closures para manejar estado local) ---
    def accion_iniciar_juego():
        nonlocal estado_actual, tiempo_inicio, errores_contador, pistas_contador
        print("Transición a la pantalla de JUEGO.")
        estado_actual = ESTADO_JUEGO
        tiempo_inicio = time.time()
        errores_contador = 0
        pistas_contador = 0

    def accion_salir_juego():
        nonlocal estado_actual
        print("Saliendo del juego.")
        estado_actual = ESTADO_SALIR

    def accion_ver_puntuaciones():
        nonlocal estado_actual
        print("Viendo puntuaciones.")
        estado_actual = ESTADO_PUNTUACIONES

    def accion_reiniciar():
        nonlocal matriz_actual, matriz_errores, tiempo_inicio, errores_contador, pistas_contador
        matriz_actual = matriz_fija.copy().astype(TIPO_MATRIZ)
        matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        tiempo_inicio = time.time()
        errores_contador = 0
        pistas_contador = 0
        print("Tablero reiniciado.")

    def accion_nuevo_juego():
        nonlocal matriz_actual, matriz_fija, matriz_errores, matriz_inicial, matriz_solucion
        nonlocal tiempo_inicio, errores_contador, pistas_contador
        nueva_matriz, nueva_solucion = cargar_y_limpiar_datos()
        if nueva_matriz is not None:
            matriz_inicial = nueva_matriz
            matriz_solucion = nueva_solucion
            matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            tiempo_inicio = time.time()
            errores_contador = 0
            pistas_contador = 0
            print("Nuevo juego generado.")

    def accion_pista():
        nonlocal matriz_actual, matriz_solucion, matriz_errores, pistas_contador
        if matriz_solucion is None: return
        celdas_vacias = [(f, c) for f in range(9) for c in range(9) if matriz_actual[f, c] == 0]
        if not celdas_vacias: return
        fila, col = random.choice(celdas_vacias)
        matriz_actual[fila, col] = matriz_solucion[fila, col]
        matriz_errores[fila, col] = 0
        pistas_contador += 1
        print(f"Pista dada en ({fila}, {col})")

    def accion_resolver():
        nonlocal matriz_actual, matriz_solucion, matriz_errores
        if matriz_solucion is not None:
            matriz_actual = resolver_tablero(matriz_solucion)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            print("Tablero resuelto.")

    def accion_volver_menu():
        nonlocal estado_actual
        estado_actual = ESTADO_MENU

    # --- ELEMENTOS UI ---
    ANCHO_BOTON = 250
    ALTO_BOTON = 70 
    ESPACIO_Y = 100
    POSICION_X_BOTON = (ANCHO_PANTALLA - ANCHO_BOTON) // 2
    POSICION_Y_INICIO = ALTO_PANTALLA // 2 + 20

    boton_jugar = Boton(POSICION_X_BOTON, POSICION_Y_INICIO, ANCHO_BOTON, ALTO_BOTON, "Jugar", COLOR_JUGAR_BASE, COLOR_JUGAR_HOVER, accion_iniciar_juego)
    boton_puntuaciones = Boton(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y, ANCHO_BOTON, ALTO_BOTON, "Ver Puntuaciones", COLOR_MENU_BASE, COLOR_MENU_HOVER, accion_ver_puntuaciones)
    boton_salir = Boton(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y * 2, ANCHO_BOTON, ALTO_BOTON, "Salir", COLOR_SALIR_BASE, COLOR_SALIR_HOVER, accion_salir_juego)
    botones_menu = [boton_jugar, boton_puntuaciones, boton_salir]
    
    caja_texto_usuario = CajaTexto(POSICION_X_BOTON, POSICION_Y_INICIO - 80, 250, 50, nombre_usuario)

    # Botones Juego
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

    # --- BUCLE PRINCIPAL ---
    while estado_actual != ESTADO_SALIR: 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                estado_actual = ESTADO_SALIR
            
            if estado_actual == ESTADO_MENU:
                for boton in botones_menu: boton.manejar_evento(evento)
                
                # Actualizar nombre usuario
                nuevo_texto = caja_texto_usuario.manejar_evento(evento)
                if nuevo_texto is not None:
                    nombre_usuario = nuevo_texto
            
            elif estado_actual == ESTADO_JUEGO:
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
                                    errores_contador += 1
                                    
                                    # Verificar derrota
                                    if errores_contador >= MAX_ERRORES:
                                        print("¡DERROTA!")
                                        tiempo_total = time.time() - tiempo_inicio
                                        estadisticas_partida_actual = {
                                            'tiempo': tiempo_total,
                                            'errores': errores_contador,
                                            'pistas': pistas_contador
                                        }
                                        guardar_puntuacion(nombre_usuario, tiempo_total, errores_contador, pistas_contador, 0, "Derrota")
                                        estado_actual = ESTADO_DERROTA
                                
                                if not es_error and es_tablero_completo(matriz_actual):
                                    if es_tablero_valido(matriz_actual):
                                        print("¡VICTORIA!")
                                        tiempo_total = time.time() - tiempo_inicio
                                        
                                        # Calcular puntaje
                                        base_score = 10000
                                        score = base_score - (tiempo_total * 2) - (errores_contador * 100) - (pistas_contador * 200)
                                        score = max(0, int(score))
                                        
                                        estadisticas_partida_actual = {
                                            'tiempo': tiempo_total,
                                            'errores': errores_contador,
                                            'pistas': pistas_contador,
                                            'puntaje': score
                                        }
                                        guardar_puntuacion(nombre_usuario, tiempo_total, errores_contador, pistas_contador, score, "Victoria")
                                        estado_actual = ESTADO_VICTORIA
                            except ValueError as e:
                                print(f"Error: {e}")

            elif estado_actual == ESTADO_VICTORIA:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    estado_actual = ESTADO_JUEGO

            elif estado_actual == ESTADO_DERROTA:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # Reiniciar juego al hacer clic en pantalla de derrota
                    accion_nuevo_juego()
                    estado_actual = ESTADO_JUEGO
            
            elif estado_actual == ESTADO_PUNTUACIONES:
                if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                    estado_actual = ESTADO_MENU

        # Renderizado
        if estado_actual == ESTADO_MENU:
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

        elif estado_actual == ESTADO_JUEGO:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_seleccion(pantalla, celda_seleccionada)
            dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores)
            for boton in botones_juego: boton.dibujar(pantalla)

        elif estado_actual == ESTADO_VICTORIA:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores)
            dibujar_victoria(pantalla, estadisticas_partida_actual)

        elif estado_actual == ESTADO_DERROTA:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores)
            dibujar_derrota(pantalla, estadisticas_partida_actual)

        elif estado_actual == ESTADO_PUNTUACIONES:
            puntuaciones = cargar_puntuaciones(nombre_usuario)
            dibujar_tabla_puntuaciones(pantalla, puntuaciones, nombre_usuario)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    ejecutar_juego()