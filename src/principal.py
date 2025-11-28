# src/principal.py

import pygame
import sys
import numpy as np
import random
import time

# Importa módulos del proyecto
from interfaz.constantes_visuales import *
from interfaz.componentes_graficos import BotonInteractivo, CampoTexto, SelectorDificultad
from interfaz.renderizador_juego import (dibujar_grilla, dibujar_seleccion, dibujar_numeros, dibujar_victoria, dibujar_derrota, dibujar_tabla_puntuaciones)
from datos.gestor_puntuaciones import guardar_puntuacion_jugador, cargar_puntuaciones_jugador
from datos.cargador_tableros import generar_tablero_nuevo
from nucleo.logica_sudoku import (TIPO_MATRIZ, obtener_coordenadas_matriz, colocar_numero, actualizar_errores, es_tablero_completo, es_tablero_valido, resolver_tablero)
from nucleo.validacion_prolog import validar_numero_prolog
from utilidades.estados_juego import *

def ejecutar_juego():
    # Inicializa Pygame y crea la ventana principal
    print("\n" + "="*60)
    print("[INIT] Inicializando Sudoku Escenario 9x9")
    print("="*60)
    pygame.init()
    print("[PYGAME] Sistema Pygame inicializado correctamente")
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption(TITULO_JUEGO)
    
    # Intenta cargar el icono de la ventana (ignora si no existe)
    try:
        icono_imagen = pygame.image.load(RUTA_ICONO)
        pygame.display.set_icon(icono_imagen)
        print("[PYGAME] Icono de ventana cargado")
    except:
        print("[DEBUG] Icono no encontrado, usando icono por defecto")
    
    # Intenta cargar la imagen de fondo del menú
    fondo_menu_imagen = None
    try:
        fondo_menu_imagen = pygame.image.load(RUTA_FONDO_MENU).convert()
        fondo_menu_imagen = pygame.transform.scale(fondo_menu_imagen, (ANCHO_PANTALLA, ALTO_PANTALLA))
        print("[PYGAME] Imagen de fondo del menú cargada")
    except:
        print("[DEBUG] Fondo de menú no encontrado, usando color sólido")
    
    # Intenta cargar la imagen del título
    titulo_imagen = None
    try:
        titulo_imagen = pygame.image.load(RUTA_TITULO_IMAGEN).convert_alpha()
        print("[PYGAME] Imagen de título cargada")
    except:
        print("[DEBUG] Título no encontrado, usando texto por defecto")

    # Variables de estado del juego
    estado_actual = ESTADO_MENU
    nombre_usuario = "Jugador"
    dificultad_seleccionada = 'medio'  # Dificultad seleccionada por el usuario
    tiempo_inicio = 0
    errores_contador = 0
    pistas_contador = 0
    estadisticas_partida_actual = {}
    
    # INMUTABILIDAD: Inicializa las matrices como None
    # Se generarán cuando el usuario presione "Jugar" por primera vez
    matriz_inicial = None
    matriz_solucion = None
    matriz_fija = None
    matriz_actual = None
    matriz_errores = None
    celda_seleccionada = None

    # Funciones de acción para botones (closures con estado local)
    def accion_iniciar_juego():
        # Cambia al estado de juego, genera nuevo tablero y resetea contadores
        nonlocal estado_actual, tiempo_inicio, errores_contador, pistas_contador
        nonlocal matriz_actual, matriz_fija, matriz_errores, matriz_inicial, matriz_solucion
        print("\n" + "-"*60)
        print("[JUEGO] Transición: MENU -> JUEGO")
        print(f"[JUEGO] Generando nuevo tablero con dificultad: {dificultad_seleccionada.upper()}")
        
        # Genera un tablero completamente nuevo con la dificultad seleccionada
        nueva_matriz, nueva_solucion = generar_tablero_nuevo(dificultad_seleccionada)
        
        # Si la generación fue exitosa, actualiza todas las matrices
        if nueva_matriz is not None:
            # INMUTABILIDAD: Asigna nuevas matrices en lugar de modificar las existentes
            matriz_inicial = nueva_matriz
            matriz_solucion = nueva_solucion
            # Crea copias independientes para cada propósito
            matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            print("[SUCCESS] Nuevo tablero generado correctamente")
        
        print("[JUEGO] Iniciando nueva partida...")
        print("-"*60)
        estado_actual = ESTADO_JUEGO
        tiempo_inicio = time.time()
        errores_contador = 0
        pistas_contador = 0

    def accion_salir_juego():
        nonlocal estado_actual
        print("\n[JUEGO] Cerrando aplicación...")
        estado_actual = ESTADO_SALIR

    def accion_ver_puntuaciones():
        nonlocal estado_actual
        print("\n[JUEGO] Transición: MENU -> PUNTUACIONES")
        estado_actual = ESTADO_PUNTUACIONES

    def accion_reiniciar():
        # Reinicia el tablero actual al estado inicial
        nonlocal matriz_actual, matriz_errores, tiempo_inicio, errores_contador, pistas_contador, matriz_fija
        # Valida que exista un juego iniciado
        if matriz_fija is None:
            print("[DEBUG] No hay juego iniciado para reiniciar")
            return
        # INMUTABILIDAD: Crea nuevas copias en lugar de modificar las existentes
        matriz_actual = matriz_fija.copy().astype(TIPO_MATRIZ)
        matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
        tiempo_inicio = time.time()
        errores_contador = 0
        pistas_contador = 0
        print("[USUARIO] Tablero reiniciado al estado inicial")

    def accion_nuevo_juego():
        # Genera un tablero completamente nuevo
        nonlocal matriz_actual, matriz_fija, matriz_errores, matriz_inicial, matriz_solucion
        nonlocal tiempo_inicio, errores_contador, pistas_contador
        print(f"\n[USUARIO] Solicitando nuevo tablero con dificultad: {dificultad_seleccionada.upper()}")
        nueva_matriz, nueva_solucion = generar_tablero_nuevo(dificultad_seleccionada)
        # Si la generación fue exitosa, actualiza todas las matrices
        if nueva_matriz is not None:
            # INMUTABILIDAD: Asigna nuevas matrices en lugar de modificar las existentes
            matriz_inicial = nueva_matriz
            matriz_solucion = nueva_solucion
            # Crea copias independientes para cada propósito
            matriz_fija = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_actual = matriz_inicial.copy().astype(TIPO_MATRIZ)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            tiempo_inicio = time.time()
            errores_contador = 0
            pistas_contador = 0
            print("[SUCCESS] Nuevo juego iniciado correctamente")

    def accion_pista():
        # Revela un número aleatorio de la solución
        nonlocal matriz_actual, matriz_solucion, matriz_errores, pistas_contador
        if matriz_solucion is None: return
        # Encuentra todas las celdas vacías
        celdas_vacias = [(f, c) for f in range(9) for c in range(9) if matriz_actual[f, c] == 0]
        if not celdas_vacias:
            print("[DEBUG] No hay celdas vacías para dar pista")
            return
        # Selecciona una celda aleatoria y revela su valor
        fila, col = random.choice(celdas_vacias)
        numero = matriz_solucion[fila, col]
        matriz_actual[fila, col] = numero
        matriz_errores[fila, col] = 0
        pistas_contador += 1
        print(f"[USUARIO] Pista solicitada -> Celda ({fila}, {col}) = {numero}")

    def accion_resolver():
        # Muestra la solución completa del tablero
        nonlocal matriz_actual, matriz_solucion, matriz_errores
        if matriz_solucion is not None:
            matriz_actual = resolver_tablero(matriz_solucion)
            matriz_errores = np.zeros((9, 9), dtype=TIPO_MATRIZ)
            print("[USUARIO] Solución completa mostrada")

    def accion_volver_menu():
        nonlocal estado_actual
        print("\n[JUEGO] Transición: JUEGO -> MENU")
        estado_actual = ESTADO_MENU

    # Elementos de interfaz de usuario
    ANCHO_BOTON = 250
    ALTO_BOTON = 70 
    ESPACIO_Y = 100
    POSICION_X_BOTON = (ANCHO_PANTALLA - ANCHO_BOTON) // 2
    POSICION_Y_INICIO = ALTO_PANTALLA // 2 + 20

    boton_jugar = BotonInteractivo(POSICION_X_BOTON, POSICION_Y_INICIO, ANCHO_BOTON, ALTO_BOTON, "Jugar", COLOR_JUGAR_BASE, COLOR_JUGAR_HOVER, accion_iniciar_juego)
    boton_puntuaciones = BotonInteractivo(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y, ANCHO_BOTON, ALTO_BOTON, "Ver Puntuaciones", COLOR_MENU_BASE, COLOR_MENU_HOVER, accion_ver_puntuaciones)
    boton_salir = BotonInteractivo(POSICION_X_BOTON, POSICION_Y_INICIO + ESPACIO_Y * 2, ANCHO_BOTON, ALTO_BOTON, "Salir", COLOR_SALIR_BASE, COLOR_SALIR_HOVER, accion_salir_juego)
    botones_menu = [boton_jugar, boton_puntuaciones, boton_salir]
    
    # Selector de dificultad
    selector_dificultad = SelectorDificultad(
        POSICION_X_BOTON, 
        POSICION_Y_INICIO - 200,  
        ANCHO_BOTON, 
        50, 
        COLOR_DIFICULTAD_BASE, 
        COLOR_DIFICULTAD_HOVER, 
        COLOR_DIFICULTAD_SELECCIONADO
    )
    
    caja_texto_usuario = CampoTexto(POSICION_X_BOTON, POSICION_Y_INICIO - 80, 250, 50, nombre_usuario)

    # Botones del juego
    X_BOTONES_JUEGO = 950
    Y_INICIO_BOTONES = 200
    ANCHO_BOTON_JUEGO = 200
    ALTO_BOTON_JUEGO = 60
    ESPACIO_BOTONES = 80

    boton_reiniciar = BotonInteractivo(X_BOTONES_JUEGO, Y_INICIO_BOTONES, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Reiniciar", COLOR_REINICIAR_BASE, COLOR_REINICIAR_HOVER, accion_reiniciar)
    boton_nuevo = BotonInteractivo(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Nuevo Juego", COLOR_NUEVO_BASE, COLOR_NUEVO_HOVER, accion_nuevo_juego)
    boton_pista = BotonInteractivo(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 2, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Pista", COLOR_PISTA_BASE, COLOR_PISTA_HOVER, accion_pista)
    boton_resolver = BotonInteractivo(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 3, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Resolver", COLOR_RESOLVER_BASE, COLOR_RESOLVER_HOVER, accion_resolver)
    boton_menu_juego = BotonInteractivo(X_BOTONES_JUEGO, Y_INICIO_BOTONES + ESPACIO_BOTONES * 4, ANCHO_BOTON_JUEGO, ALTO_BOTON_JUEGO, "Menú", COLOR_MENU_BASE, COLOR_MENU_HOVER, accion_volver_menu)
    botones_juego = [boton_reiniciar, boton_nuevo, boton_pista, boton_resolver, boton_menu_juego]

    # Bucle principal del juego
    while estado_actual != ESTADO_SALIR: 
        # Procesa todos los eventos de Pygame
        for evento in pygame.event.get():
            # Detecta si el usuario cierra la ventana
            if evento.type == pygame.QUIT:
                estado_actual = ESTADO_SALIR
            
            # Maneja eventos del menú principal
            if estado_actual == ESTADO_MENU:
                for boton in botones_menu: boton.manejar_evento(evento)
                
                # Maneja eventos del selector de dificultad
                selector_dificultad.manejar_evento(evento)
                dificultad_seleccionada = selector_dificultad.obtener_seleccion()
                
                # Actualiza el nombre de usuario
                nuevo_texto = caja_texto_usuario.manejar_evento(evento)
                if nuevo_texto is not None:
                    nombre_usuario = nuevo_texto
            
            # Maneja eventos durante el juego
            elif estado_actual == ESTADO_JUEGO:
                for boton in botones_juego: boton.manejar_evento(evento)
                # Detecta clic del mouse para seleccionar celda
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # FUNCIÓN PURA: obtener_coordenadas_matriz no modifica evento.pos
                    celda_seleccionada = obtener_coordenadas_matriz(evento.pos, OFFSET_GRILLA_X, OFFSET_GRILLA_Y, TAMANO_CELDA)
                    if celda_seleccionada:
                        print(f"[USUARIO] Celda seleccionada: {celda_seleccionada}")
                # Detecta teclas presionadas si hay una celda seleccionada
                if evento.type == pygame.KEYDOWN and celda_seleccionada and matriz_fija is not None:
                    fila, columna = celda_seleccionada
                    # Solo permite editar celdas que no son fijas
                    if matriz_fija[fila, columna] == 0:
                        numero = None
                        # Mapea las teclas numéricas a valores
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
                        
                        # Si se presionó una tecla válida
                        if numero is not None:
                            print(f"[USUARIO] Número ingresado: {numero} en celda ({fila}, {columna})")
                            try:
                                # Valida el número antes de colocarlo
                                # FUNCIÓN PURA: colocar_numero retorna NUEVA matriz, no modifica matriz_actual
                                matriz_para_validar = colocar_numero(matriz_actual, fila, columna, 0)
                                if numero != 0:
                                    es_valido = validar_numero_prolog(matriz_para_validar, fila, columna, numero)
                                    es_error = not es_valido
                                else:
                                    # Borrar no es un error
                                    es_error = False
                                
                                # INMUTABILIDAD: Cada llamada retorna una NUEVA matriz
                                # matriz_actual original nunca se modifica, se reemplaza por una nueva
                                matriz_actual = colocar_numero(matriz_actual, fila, columna, numero)
                                # FUNCIÓN PURA: actualizar_errores retorna nueva matriz de errores
                                matriz_errores = actualizar_errores(matriz_errores, fila, columna, es_error)
                                # Si es un error, incrementa el contador
                                if es_error:
                                    errores_contador += 1
                                    
                                    # Verifica si se alcanzó el límite de errores (derrota)
                                    if errores_contador >= MAXIMO_ERRORES:
                                        tiempo_total = time.time() - tiempo_inicio
                                        print("\n" + "="*60)
                                        print("[DERROTA] Límite de errores alcanzado")
                                        print(f"[STATS] Tiempo: {tiempo_total:.2f}s | Errores: {errores_contador} | Pistas: {pistas_contador}")
                                        print("="*60)
                                        estadisticas_partida_actual = {
                                            'tiempo': tiempo_total,
                                            'errores': errores_contador,
                                            'pistas': pistas_contador
                                        }
                                        guardar_puntuacion_jugador(nombre_usuario, tiempo_total, errores_contador, pistas_contador, 0, "Derrota")
                                        estado_actual = ESTADO_DERROTA
                                
                                # Verifica si el jugador completó el tablero correctamente
                                if not es_error and es_tablero_completo(matriz_actual):
                                    if es_tablero_valido(matriz_actual):
                                        tiempo_total = time.time() - tiempo_inicio
                                        
                                        # Calcula el puntaje basado en tiempo, errores y pistas
                                        base_score = 10000
                                        score = base_score - (tiempo_total * 2) - (errores_contador * 100) - (pistas_contador * 200)
                                        score = max(0, int(score))
                                        
                                        print("\n" + "="*60)
                                        print("[SUCCESS] ¡VICTORIA! Tablero completado correctamente")
                                        print(f"[STATS] Tiempo: {tiempo_total:.2f}s | Errores: {errores_contador} | Pistas: {pistas_contador} | Puntaje: {score}")
                                        print("="*60)
                                        
                                        estadisticas_partida_actual = {
                                            'tiempo': tiempo_total,
                                            'errores': errores_contador,
                                            'pistas': pistas_contador,
                                            'puntaje': score
                                        }
                                        guardar_puntuacion_jugador(nombre_usuario, tiempo_total, errores_contador, pistas_contador, score, "Victoria")
                                        estado_actual = ESTADO_VICTORIA
                            # Captura errores de validación
                            except ValueError as e:
                                print(f"Error: {e}")

            # Maneja eventos en la pantalla de victoria
            elif estado_actual == ESTADO_VICTORIA:
                # Clic para volver al tablero
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    estado_actual = ESTADO_JUEGO

            # Maneja eventos en la pantalla de derrota
            elif estado_actual == ESTADO_DERROTA:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # Reinicia el juego al hacer clic
                    accion_nuevo_juego()
                    estado_actual = ESTADO_JUEGO
            
            # Maneja eventos en la pantalla de puntuaciones
            elif estado_actual == ESTADO_PUNTUACIONES:
                # Clic o tecla para volver al menú
                if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                    print("[JUEGO] Transición: PUNTUACIONES -> MENU")
                    estado_actual = ESTADO_MENU

        # Renderiza la pantalla según el estado actual
        if estado_actual == ESTADO_MENU:
            # Dibuja el fondo del menú (imagen o color sólido)
            if fondo_menu_imagen: pantalla.blit(fondo_menu_imagen, (0, 0))
            else: pantalla.fill(COLOR_FONDO_MENU)
            # Dibuja el título (imagen o texto)
            if titulo_imagen: pantalla.blit(titulo_imagen, (ANCHO_PANTALLA // 2 - titulo_imagen.get_width() // 2, 80))
            else:
                fuente = pygame.font.Font(None, 80)
                pantalla.blit(fuente.render(TITULO_JUEGO, True, BLANCO), (ANCHO_PANTALLA // 2 - 200, 80))
            
            for boton in botones_menu: boton.dibujar(pantalla)
            
            # Dibuja el selector de dificultad
            selector_dificultad.dibujar(pantalla)
            fuente_dif = pygame.font.Font(None, 30)
            lbl_dif = fuente_dif.render("Dificultad:", True, BLANCO)
            pantalla.blit(lbl_dif, (selector_dificultad.x, selector_dificultad.y - 30))
            
            caja_texto_usuario.dibujar(pantalla)
            
            # Etiqueta de usuario
            fuente_lbl = pygame.font.Font(None, 30)
            lbl = fuente_lbl.render("Usuario:", True, BLANCO)
            pantalla.blit(lbl, (caja_texto_usuario.rect.x, caja_texto_usuario.rect.y - 30))

        elif estado_actual == ESTADO_JUEGO:
            pantalla.fill(COLOR_FONDO_JUEGO)
            dibujar_grilla(pantalla)
            dibujar_seleccion(pantalla, celda_seleccionada)
            # Solo dibuja el tablero si las matrices están inicializadas
            if matriz_actual is not None and matriz_fija is not None and matriz_errores is not None:
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
            puntuaciones = cargar_puntuaciones_jugador(nombre_usuario)
            dibujar_tabla_puntuaciones(pantalla, puntuaciones, nombre_usuario)

        # Actualiza la pantalla
        pygame.display.flip()

    # Cierra Pygame y termina el programa
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    ejecutar_juego()
