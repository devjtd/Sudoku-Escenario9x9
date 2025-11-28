# src/interfaz/renderizador_juego.py
import pygame
from interfaz.constantes_visuales import *

def dibujar_grilla(pantalla):
    # Dibuja la grilla del tablero con líneas finas y gruesas
    # Dibuja el fondo blanco
    pygame.draw.rect(pantalla, BLANCO, (OFFSET_GRILLA_X, OFFSET_GRILLA_Y, TAMANO_GRILLA, TAMANO_GRILLA))
    # Dibuja las líneas horizontales y verticales
    for i in range(10): 
        grosor_linea = GROSOR_LINEA_GRUESA if i % 3 == 0 else GROSOR_LINEA_FINA
        color_linea = COLOR_GRILLA_GRUESA if i % 3 == 0 else COLOR_GRILLA_FINA
        # Líneas verticales
        posicion = OFFSET_GRILLA_X + i * TAMANO_CELDA
        pygame.draw.line(pantalla, color_linea, (posicion, OFFSET_GRILLA_Y), (posicion, OFFSET_GRILLA_Y + TAMANO_GRILLA), grosor_linea)
        # Líneas horizontales
        posicion = OFFSET_GRILLA_Y + i * TAMANO_CELDA
        pygame.draw.line(pantalla, color_linea, (OFFSET_GRILLA_X, posicion), (OFFSET_GRILLA_X + TAMANO_GRILLA, posicion), grosor_linea)

def dibujar_seleccion(pantalla, celda_seleccionada):
    # Dibuja un borde alrededor de la celda seleccionada
    if celda_seleccionada:
        fila, columna = celda_seleccionada
        # Calcula la posición de la celda
        x = OFFSET_GRILLA_X + columna * TAMANO_CELDA
        y = OFFSET_GRILLA_Y + fila * TAMANO_CELDA
        # Dibuja el borde de selección
        pygame.draw.rect(pantalla, COLOR_SELECCION, (x, y, TAMANO_CELDA, TAMANO_CELDA), 4)

def dibujar_numeros(pantalla, matriz_actual, matriz_fija, matriz_errores):
    # Dibuja los números del tablero con colores según su estado (fijo, error, normal)
    fuente_numero = pygame.font.Font(None, 40)
    # Recorre todas las celdas del tablero
    for fila in range(9):
        for columna in range(9):
            numero = matriz_actual[fila, columna]
            # Solo dibuja si la celda no está vacía
            if numero != 0:
                # Determina el color según el estado
                es_fijo = matriz_fija[fila, columna] != 0
                es_error = matriz_errores[fila, columna] != 0
                color_texto = COLOR_ERROR if es_error else (COLOR_FIJO if es_fijo else NEGRO)
                # Renderiza el número
                texto_superficie = fuente_numero.render(str(numero), True, color_texto)
                # Calcula la posición centrada
                pos_x = OFFSET_GRILLA_X + columna * TAMANO_CELDA + (TAMANO_CELDA - texto_superficie.get_width()) // 2
                pos_y = OFFSET_GRILLA_Y + fila * TAMANO_CELDA + (TAMANO_CELDA - texto_superficie.get_height()) // 2
                pantalla.blit(texto_superficie, (pos_x, pos_y))

def dibujar_victoria(pantalla, estadisticas=None):
    # Muestra la pantalla de victoria con estadísticas de la partida
    # Crea una capa semi-transparente
    superficie_transparente = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    superficie_transparente.set_alpha(200)
    superficie_transparente.fill(NEGRO)
    pantalla.blit(superficie_transparente, (0, 0))
    
    # Dibuja el título de victoria
    fuente_victoria = pygame.font.Font(None, 100)
    texto_victoria = fuente_victoria.render("¡FELICIDADES!", True, (0, 255, 0))
    rect_victoria = texto_victoria.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 100))
    pantalla.blit(texto_victoria, rect_victoria)

    # Muestra las estadísticas si están disponibles
    if estadisticas:
        fuente_stats = pygame.font.Font(None, 40)
        y_offset = ALTO_PANTALLA // 2
        textos = [
            f"Tiempo: {estadisticas['tiempo']:.2f}s",
            f"Errores: {estadisticas['errores']}",
            f"Pistas: {estadisticas['pistas']}"
        ]
        # Dibuja cada línea de estadísticas
        for texto in textos:
            surf = fuente_stats.render(texto, True, BLANCO)
            rect = surf.get_rect(center=(ANCHO_PANTALLA // 2, y_offset))
            pantalla.blit(surf, rect)
            y_offset += 40

    # Dibuja la instrucción para continuar
    texto_instruccion = pygame.font.Font(None, 30).render("Haz clic para volver al tablero", True, (200, 200, 200))
    rect_inst = texto_instruccion.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50))
    pantalla.blit(texto_instruccion, rect_inst)

def dibujar_derrota(pantalla, estadisticas=None):
    # Muestra la pantalla de derrota con estadísticas de la partida
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
    pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 30))

    if not puntuaciones:
        fuente_msg = pygame.font.Font(None, 40)
        msg = fuente_msg.render("No hay puntuaciones registradas.", True, BLANCO)
        pantalla.blit(msg, (ANCHO_PANTALLA // 2 - msg.get_width() // 2, 200))
    else:
        # Ordena las puntuaciones por fecha (más recientes primero)
        puntuaciones_ordenadas = sorted(puntuaciones, key=lambda x: x.get('Fecha', ''), reverse=True)
        
        # Muestra tabla de puntuaciones
        y = 120
        fuente_cabecera = pygame.font.Font(None, 28)
        fuente_fila = pygame.font.Font(None, 24)
        
        # Define anchos de columna para mejor alineación
        x_inicio = 80
        col_fecha = x_inicio
        col_tiempo = col_fecha + 150
        col_errores = col_tiempo + 90
        col_pistas = col_errores + 80
        col_puntaje = col_pistas + 80
        col_estado = col_puntaje + 100
        
        # Dibuja cabecera con color destacado
        cabeceras = [
            ("Fecha", col_fecha),
            ("Tiempo", col_tiempo),
            ("Errores", col_errores),
            ("Pistas", col_pistas),
            ("Puntaje", col_puntaje),
            ("Estado", col_estado)
        ]
        
        for texto, x_pos in cabeceras:
            surf_cab = fuente_cabecera.render(texto, True, (255, 215, 0))  # Color dorado
            pantalla.blit(surf_cab, (x_pos, y))
        
        # Línea separadora debajo de la cabecera
        pygame.draw.line(pantalla, (255, 215, 0), (x_inicio, y + 30), (col_estado + 100, y + 30), 2)
        y += 45
        
        # Muestra las últimas 12 partidas (más espacio eficiente)
        for i, p in enumerate(puntuaciones_ordenadas[:12]):
            # Obtiene datos de cada puntuación con valores por defecto
            fecha_completa = p.get('Fecha', 'N/A')
            # Acorta la fecha: "2025-11-28 15:30:45" -> "28/11 15:30"
            try:
                if fecha_completa != 'N/A' and len(fecha_completa) >= 16:
                    # Extrae día/mes hora:minuto
                    fecha_corta = f"{fecha_completa[8:10]}/{fecha_completa[5:7]} {fecha_completa[11:16]}"
                else:
                    fecha_corta = fecha_completa
            except:
                fecha_corta = fecha_completa
            
            tiempo = p.get('Tiempo', '0')
            errores = p.get('Errores', '0')
            pistas = p.get('Pistas', '0')
            puntaje = p.get('Puntaje', '0')
            estado = p.get('Estado', 'N/A')
            
            # Color alternado para mejor legibilidad
            color_fila = BLANCO if i % 2 == 0 else (200, 200, 200)
            
            # Color especial para victorias/derrotas
            if estado == 'Victoria':
                color_estado = (0, 255, 0)  # Verde
            elif estado == 'Derrota':
                color_estado = (255, 100, 100)  # Rojo claro
            else:
                color_estado = color_fila
            
            # Dibuja cada columna
            datos = [
                (fecha_corta, col_fecha, color_fila),
                (f"{tiempo}s", col_tiempo, color_fila),
                (str(errores), col_errores, color_fila),
                (str(pistas), col_pistas, color_fila),
                (str(puntaje), col_puntaje, color_fila),
                (estado, col_estado, color_estado)
            ]
            
            for texto, x_pos, color in datos:
                surf_fila = fuente_fila.render(str(texto), True, color)
                pantalla.blit(surf_fila, (x_pos, y))
            
            y += 32

    # Instrucción para volver al menú
    texto_volver = pygame.font.Font(None, 28).render("Presiona ESC o clic para volver al menú", True, (200, 200, 200))
    pantalla.blit(texto_volver, (ANCHO_PANTALLA // 2 - texto_volver.get_width() // 2, ALTO_PANTALLA - 40))
