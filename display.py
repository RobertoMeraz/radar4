import colors
import pygame
import math
import time
import copy  # Nuevo import para manejar copias seguras

""" This module draws the radar screen """

def draw(radarDisplay, targets, angle, distance, fontRenderer):
    try:
        # draw initial screen
        radarDisplay.fill(colors.black)

        # Dibujar círculos de radar
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 650, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 550, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 450, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 300, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 150, 1)

        # Dibujar área inferior
        radarDisplay.fill(colors.black, [0, 785, 1400, 20])

        # Dibujar líneas guía
        pygame.draw.line(radarDisplay, colors.green, (30, 780), (1370, 780), 1)  # Horizontal
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (205, 285), 1)  # 45°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700, 80), 1)   # 90°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (1195, 285), 1) # 135°

        # Panel de estadísticas
        pygame.draw.rect(radarDisplay, colors.blue, [20, 20, 270, 100], 2)

        # Marcadores de ángulo
        angles = [
            ("0", (10, 780)),
            ("45", (180, 260)),
            ("90", (690, 55)),
            ("135", (1205, 270)),
            ("180", (1365, 780))
        ]
        for text, pos in angles:
            rendered_text = fontRenderer.render(text, 1, colors.green)
            radarDisplay.blit(rendered_text, pos)

        # Línea de barrido
        a = math.sin(math.radians(angle)) * 700.0
        b = math.cos(math.radians(angle)) * 700.0
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700 - int(b), 780 - int(a)), 3)

        # Mostrar ángulo actual
        angle_text = fontRenderer.render(f"Angle: {angle}°", 1, colors.white)
        radarDisplay.blit(angle_text, (40, 40))

        # Mostrar distancia
        dist_text = fontRenderer.render(
            "Distance: Out Of Range" if distance == -1 else f"Distance: {distance} cm", 
            1, colors.white
        )
        radarDisplay.blit(dist_text, (40, 80))

        # Dibujar objetivos - USAMOS UNA COPIA PARA EVITAR MODIFICACIONES DURANTE ITERACIÓN
        for angle_key in list(targets.keys()):  # Convertimos a lista para iteración segura
            target = targets.get(angle_key)
            if not target:  # Verificación de existencia
                continue

            try:
                # Cálculo de coordenadas
                c = math.sin(math.radians(target.angle)) * 800.0
                d = math.cos(math.radians(target.angle)) * 800.0
                e = math.sin(math.radians(target.angle)) * (700 / 60) * target.distance  # Cambiado a 60
                f = math.cos(math.radians(target.angle)) * (700 / 60) * target.distance  # Cambiado a 60

                # Dibujar línea del objetivo
                pygame.draw.line(
                    radarDisplay, 
                    target.color, 
                    (700 - int(f), 780 - int(e)), 
                    (700 - int(d), 780 - int(c)), 
                    3
                )

                # Efecto de desvanecimiento
                diff_time = time.time() - target.time
                
                if diff_time <= 0.5:
                    target.color = colors.red1L
                elif 0.5 < diff_time <= 1.0:
                    target.color = colors.red2L
                elif 1.0 < diff_time <= 1.5:
                    target.color = colors.red3L
                elif 1.5 < diff_time <= 2.0:
                    target.color = colors.red4L
                elif 2.0 < diff_time <= 2.5:
                    target.color = colors.red5L
                elif 2.5 < diff_time <= 3.0:
                    target.color = colors.red6L
                elif diff_time > 3.0:
                    del targets[angle_key]  # Eliminación segura

            except (AttributeError, KeyError) as e:
                print(f"Error dibujando objetivo: {e}")
                continue

        pygame.display.update()

    except Exception as e:
        print(f"Error crítico en renderizado: {e}")
        raise  # Relanzamos la excepción para manejo externo