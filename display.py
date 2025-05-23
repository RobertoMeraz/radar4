import colors
import pygame
import math
import time

def draw(radarDisplay, targets, angle, distance, fontRenderer):
    """Renderiza la pantalla del radar con el estilo original"""
    try:
        # Fondo
        radarDisplay.fill(colors.black)
        
        # Círculos concéntricos
        for radius in [150, 300, 450, 550, 650]:
            pygame.draw.circle(radarDisplay, colors.green, (700, 800), radius, 1)
        
        # Líneas guía
        pygame.draw.line(radarDisplay, colors.green, (30, 780), (1370, 780), 1)  # 0°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (205, 285), 1)  # 45°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700, 80), 1)   # 90°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (1195, 285), 1) # 135°

        # Panel de información
        pygame.draw.rect(radarDisplay, colors.blue, [20, 20, 270, 100], 2)
        
        # Marcadores de ángulo
        angle_texts = [
            ("0", (10, 780)), ("45", (180, 260)), ("90", (690, 55)),
            ("135", (1205, 270)), ("180", (1365, 780))
        ]
        for text, pos in angle_texts:
            rendered = fontRenderer.render(text, 1, colors.green)
            radarDisplay.blit(rendered, pos)
        
        # Línea de barrido
        a = math.sin(math.radians(angle)) * 700.0
        b = math.cos(math.radians(angle)) * 700.0
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700 - int(b), 780 - int(a)), 3)

        # Información de ángulo y distancia
        angle_text = fontRenderer.render(f"Angle: {angle}°", 1, colors.white)
        radarDisplay.blit(angle_text, (40, 40))
        
        dist_text = fontRenderer.render(
            "Distance: Out Of Range" if distance == -1 else f"Distance: {distance} cm",
            1, colors.white
        )
        radarDisplay.blit(dist_text, (40, 80))
        
        # Dibujar objetivos (seguro para hilos)
        target_keys = list(targets.keys())  # Copia para iteración segura
        for angle_key in target_keys:
            target = targets.get(angle_key)
            if not target:
                continue
                
            try:
                # Cálculo de posición (ajustado para 60cm)
                c = math.sin(math.radians(target.angle)) * 800.0
                d = math.cos(math.radians(target.angle)) * 800.0
                e = math.sin(math.radians(target.angle)) * (700 / 60) * target.distance
                f = math.cos(math.radians(target.angle)) * (700 / 60) * target.distance
                
                # Dibujar línea del objetivo
                pygame.draw.line(
                    radarDisplay,
                    target.color,
                    (700 - int(f), 780 - int(e)),
                    (700 - int(d), 780 - int(c)),
                    3
                )
                
                # Efecto de desvanecimiento
                elapsed = time.time() - target.time
                if elapsed > 3.0:
                    del targets[angle_key]
                    
            except Exception as e:
                print(f"Error renderizando objetivo: {e}")
                continue

        pygame.display.update()
        
    except Exception as e:
        print(f"Error en renderizado: {e}")
        raise