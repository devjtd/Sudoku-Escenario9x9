# src/renderizado.py
import pygame
from config import *

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

def dibujar_derrota(pantalla, estadisticas=None):
    superficie_transparente = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    superficie_transparente.set_alpha(200)
    superficie_transparente.fill(NEGRO)
    pantalla.blit(superficie_transparente, (0, 0))
    
    fuente_derrota = pygame.font.Font(None, 100)
    texto_derrota = fuente_derrota.render("¡GAME OVER!", True, (255, 0, 0))
    rect_derrota = texto_derrota.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 100))
    pantalla.blit(texto_derrota, rect_derrota)

    if estadisticas:
        fuente_stats = pygame.font.Font(None, 40)
        y_offset = ALTO_PANTALLA // 2
        textos = [
            f"Has cometido {estadisticas['errores']} errores",
            "Suerte para la próxima"
        ]
        for texto in textos:
            surf = fuente_stats.render(texto, True, BLANCO)
            rect = surf.get_rect(center=(ANCHO_PANTALLA // 2, y_offset))
            pantalla.blit(surf, rect)
            y_offset += 40

    texto_instruccion = pygame.font.Font(None, 30).render("Haz clic para reiniciar", True, (200, 200, 200))
    rect_inst = texto_instruccion.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50))
    pantalla.blit(texto_instruccion, rect_inst)

def dibujar_tabla_puntuaciones(pantalla, puntuaciones, nombre_usuario):
    pantalla.fill(COLOR_FONDO_JUEGO)
    fuente_titulo = pygame.font.Font(None, 60)
    titulo = fuente_titulo.render(f"Puntuaciones de {nombre_usuario}", True, BLANCO)
    pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 50))

    if not puntuaciones:
        fuente_msg = pygame.font.Font(None, 40)
        msg = fuente_msg.render("No hay puntuaciones registradas.", True, BLANCO)
        pantalla.blit(msg, (ANCHO_PANTALLA // 2 - msg.get_width() // 2, 200))
    else:
        # Cabecera
        y = 150
        fuente_fila = pygame.font.Font(None, 30)
        # Ajustamos el espaciado para las nuevas columnas
        cabecera = f"{'Fecha':<19} {'Tiempo':<8} {'Err':<5} {'Pistas':<6} {'Puntaje':<8} {'Estado':<10}"
        surf_cab = fuente_fila.render(cabecera, True, (200, 200, 0))
        pantalla.blit(surf_cab, (ANCHO_PANTALLA // 2 - 350, y))
        y += 40
        
        # Filas (mostrar ultimas 10)
        for p in puntuaciones[-10:]:
            # Manejo seguro de claves para compatibilidad
            fecha = p.get('Fecha', 'N/A')
            tiempo = p.get('Tiempo', '0')
            errores = p.get('Errores', '0')
            pistas = p.get('Pistas', '0')
            puntaje = p.get('Puntaje', '0')
            estado = p.get('Estado', 'N/A')
            
            fila_str = f"{fecha:<19} {tiempo:<8} {errores:<5} {pistas:<6} {puntaje:<8} {estado:<10}"
            surf_fila = fuente_fila.render(fila_str, True, BLANCO)
            pantalla.blit(surf_fila, (ANCHO_PANTALLA // 2 - 350, y))
            y += 30

    # Instrucción para volver
    texto_volver = pygame.font.Font(None, 30).render("Presiona ESC o clic para volver", True, (200, 200, 200))
    pantalla.blit(texto_volver, (ANCHO_PANTALLA // 2 - texto_volver.get_width() // 2, ALTO_PANTALLA - 50))
