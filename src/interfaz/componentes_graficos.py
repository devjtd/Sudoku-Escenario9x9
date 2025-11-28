# src/interfaz/componentes_graficos.py
import pygame
from interfaz.constantes_visuales import NEGRO

class BotonInteractivo:
    # Botón con efectos hover y acción al hacer clic
    
    def __init__(self, x, y, ancho, alto, texto, color_base, color_hover, accion=None):
        # Inicializa las propiedades del botón
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_actual = color_base
        self.accion = accion
        
        # Calcula el tamaño de fuente óptimo basado en el ancho del botón
        # y la longitud del texto para que siempre quepa
        self.fuente = self._calcular_fuente_optima(texto, ancho, alto)

    def _calcular_fuente_optima(self, texto, ancho_boton, alto_boton):
        # Calcula el tamaño de fuente que mejor se ajusta al botón
        # Comienza con un tamaño grande y reduce hasta que quepa
        tamano_max = 48
        tamano_min = 20
        margen = 20  # Margen horizontal dentro del botón
        
        for tamano in range(tamano_max, tamano_min - 1, -2):
            fuente_prueba = pygame.font.Font(None, tamano)
            ancho_texto = fuente_prueba.size(texto)[0]
            alto_texto = fuente_prueba.size(texto)[1]
            
            # Verifica si el texto cabe con margen
            if ancho_texto <= (ancho_boton - margen) and alto_texto <= (alto_boton - 10):
                return fuente_prueba
        
        # Si no cabe ni con el tamaño mínimo, usa el mínimo
        return pygame.font.Font(None, tamano_min)

    def dibujar(self, pantalla):
        # Dibuja el botón con bordes redondeados
        pygame.draw.rect(pantalla, self.color_actual, self.rect, 0, 8) 
        # Renderiza y centra el texto
        superficie_texto = self.fuente.render(self.texto, True, NEGRO)
        posicion_texto = (
            self.rect.x + (self.rect.width - superficie_texto.get_width()) // 2,
            self.rect.y + (self.rect.height - superficie_texto.get_height()) // 2
        )
        pantalla.blit(superficie_texto, posicion_texto)

    def manejar_evento(self, evento):
        # Cambia el color cuando el mouse está sobre el botón
        if evento.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(evento.pos):
                self.color_actual = self.color_hover
            else:
                self.color_actual = self.color_base
        
        # Ejecuta la acción cuando se hace clic
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos) and self.accion:
                self.accion()

class CampoTexto:
    # Campo de texto editable para entrada del usuario
    
    def __init__(self, x, y, ancho, alto, texto=''):
        # Inicializa las propiedades del campo de texto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_inactivo = pygame.Color('lightskyblue3')
        self.color_activo = pygame.Color('dodgerblue2')
        self.color = self.color_inactivo
        self.texto = texto
        self.fuente = pygame.font.Font(None, 32)
        self.txt_surface = self.fuente.render(texto, True, self.color)
        self.activo = False

    def manejar_evento(self, evento):
        # Maneja eventos de mouse y teclado, retorna el texto actualizado o None
        texto_actualizado = None
        
        # Activa/desactiva el campo al hacer clic
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                self.activo = not self.activo
            else:
                self.activo = False
            self.color = self.color_activo if self.activo else self.color_inactivo
        
        # Procesa entrada de teclado si el campo está activo
        if evento.type == pygame.KEYDOWN:
            if self.activo:
                # Enter desactiva el campo
                if evento.key == pygame.K_RETURN:
                    self.activo = False
                    self.color = self.color_inactivo
                # Backspace borra el último carácter
                elif evento.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1]
                else:
                    # Añade el carácter si no excede el límite
                    if len(self.texto) < 15:
                        self.texto += evento.unicode
                
                # Actualiza la superficie de texto
                self.txt_surface = self.fuente.render(self.texto, True, self.color)
                texto_actualizado = self.texto
                
        return texto_actualizado
                
    def dibujar(self, pantalla):
        # Dibuja el texto y el borde del campo
        pantalla.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(pantalla, self.color, self.rect, 2)

class SelectorDificultad:
    # Selector visual de dificultad con tres opciones: Fácil, Medio, Difícil
    
    def __init__(self, x, y, ancho_total, alto, color_base, color_hover, color_seleccionado):
        # Inicializa el selector con tres botones horizontales
        self.x = x
        self.y = y
        self.ancho_total = ancho_total
        self.alto = alto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_seleccionado = color_seleccionado
        
        # Opciones de dificultad
        self.opciones = ['facil', 'medio', 'dificil']
        self.textos = ['Fácil', 'Medio', 'Difícil']
        self.seleccionado = 'medio'  # Dificultad por defecto
        
        # Calcula dimensiones de cada botón
        self.ancho_boton = ancho_total // 3
        self.espaciado = 5
        
        # Crea los rectángulos para cada botón
        self.rectangulos = []
        for i in range(3):
            rect = pygame.Rect(
                x + i * self.ancho_boton + (i * self.espaciado),
                y,
                self.ancho_boton - self.espaciado,
                alto
            )
            self.rectangulos.append(rect)
        
        # Fuente para el texto
        self.fuente = pygame.font.Font(None, 28)
        
        # Estado de hover
        self.hover_index = -1
    
    def obtener_seleccion(self):
        # Retorna la dificultad seleccionada actual
        return self.seleccionado
    
    def manejar_evento(self, evento):
        # Maneja eventos de mouse para cambiar la selección
        if evento.type == pygame.MOUSEMOTION:
            # Detecta sobre qué botón está el mouse
            self.hover_index = -1
            for i, rect in enumerate(self.rectangulos):
                if rect.collidepoint(evento.pos):
                    self.hover_index = i
                    break
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Cambia la selección al hacer clic
            for i, rect in enumerate(self.rectangulos):
                if rect.collidepoint(evento.pos):
                    self.seleccionado = self.opciones[i]
                    print(f"[MENU] Dificultad seleccionada: {self.textos[i]}")
                    break
    
    def dibujar(self, pantalla):
        # Dibuja los tres botones con el estado visual apropiado
        for i, rect in enumerate(self.rectangulos):
            # Determina el color del botón
            if self.opciones[i] == self.seleccionado:
                color = self.color_seleccionado
            elif i == self.hover_index:
                color = self.color_hover
            else:
                color = self.color_base
            
            # Dibuja el botón con bordes redondeados
            pygame.draw.rect(pantalla, color, rect, 0, 6)
            
            # Renderiza y centra el texto
            superficie_texto = self.fuente.render(self.textos[i], True, NEGRO)
            posicion_texto = (
                rect.x + (rect.width - superficie_texto.get_width()) // 2,
                rect.y + (rect.height - superficie_texto.get_height()) // 2
            )
            pantalla.blit(superficie_texto, posicion_texto)
