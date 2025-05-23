import colors
import pygame
import math
import time

""" This module draws the radar screen with points instead of lines """

def draw(radarDisplay, targets, angle, distance, fontRenderer):
    try:
        # Dibujar pantalla inicial
        radarDisplay.fill(colors.black)

        # Dibujar círculos concéntricos del radar
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 650, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 550, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 450, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 300, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700, 800), 150, 1)

        # Dibujar área inferior
        radarDisplay.fill(colors.black, [0, 785, 1400, 20])

        # Dibujar líneas guía (ejes)
        pygame.draw.line(radarDisplay, colors.green, (30, 780), (1370, 780), 1)  # Horizontal (0°)
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (205, 285), 1)  # 45°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700, 80), 1)   # 90°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (1195, 285), 1) # 135°

        # Panel de información
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

        # Línea de barrido actual
        a = math.sin(math.radians(angle)) * 700.0
        b = math.cos(math.radians(angle)) * 700.0
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700 - int(b), 780 - int(a)), 3)

        # Mostrar información de ángulo y distancia
        angle_text = fontRenderer.render(f"Angle: {angle}°", 1, colors.white)
        radarDisplay.blit(angle_text, (40, 40))

        dist_text = fontRenderer.render(
            "Distance: Out Of Range" if distance == -1 else f"Distance: {distance} cm", 
            1, colors.white
        )
        radarDisplay.blit(dist_text, (40, 80))

        # Dibujar objetivos como puntos en lugar de líneas
        for angle_key in list(targets.keys()):  # Iteración segura
            target = targets.get(angle_key)
            if not target:
                continue

            try:
                # Calcular posición del punto (coordenadas polares a cartesianas)
                radius = (700 / 60) * target.distance  # Escala para 60cm máximo
                x = 700 - radius * math.cos(math.radians(target.angle))
                y = 780 - radius * math.sin(math.radians(target.angle))

                # Dibujar punto (círculo relleno) con efecto de desvanecimiento
                point_size = 6  # Tamaño base del punto
                
                # Determinar color basado en el tiempo transcurrido
                diff_time = time.time() - target.time
                
                if diff_time <= 0.5:
                    color = colors.red1L
                    point_size = 8  # Más grande cuando es reciente
                elif 0.5 < diff_time <= 1.0:
                    color = colors.red2L
                    point_size = 7
                elif 1.0 < diff_time <= 1.5:
                    color = colors.red3L
                    point_size = 6
                elif 1.5 < diff_time <= 2.0:
                    color = colors.red4L
                    point_size = 5
                elif 2.0 < diff_time <= 2.5:
                    color = colors.red5L
                    point_size = 4
                elif 2.5 < diff_time <= 3.0:
                    color = colors.red6L
                    point_size = 3
                elif diff_time > 3.0:
                    del targets[angle_key]  # Eliminar objetivo después de 3 segundos
                    continue
                
                # Dibujar el punto (círculo relleno)
                pygame.draw.circle(radarDisplay, color, (int(x), int(y)), point_size)

            except Exception as e:
                print(f"Error dibujando objetivo: {e}")
                continue

        pygame.display.update()

    except Exception as e:
        print(f"Error crítico en renderizado: {e}")
        raise