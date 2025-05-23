import colors
import pygame
import math
import time

""" This module draws the radar screen """

def draw(radarDisplay, targets, angle, distance, fontRenderer):
    try:
        # draw initial screen
        radarDisplay.fill(colors.black)

        # draw radar circles
        pygame.draw.circle(radarDisplay, colors.green, (700,800), 650, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700,800), 550, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700,800), 450, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700,800), 300, 1)
        pygame.draw.circle(radarDisplay, colors.green, (700,800), 150, 1)

        # draw bottom area
        radarDisplay.fill(colors.black, [0, 785, 1400, 20])

        # draw guide lines
        pygame.draw.line(radarDisplay, colors.green, (30, 780), (1370, 780), 1)  # 0°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (205, 285), 1)   # 45°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700, 80), 1)    # 90°
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (1195, 285), 1)  # 135°

        # draw stats board
        pygame.draw.rect(radarDisplay, colors.blue, [20, 20, 270, 100], 2)

        # draw angle markers
        angle_markers = [
            ("0", (10,780)), ("45", (180,260)), ("90", (690,55)),
            ("135", (1205,270)), ("180", (1365,780))
        ]
        for text, pos in angle_markers:
            rendered_text = fontRenderer.render(text, 1, colors.green)
            radarDisplay.blit(rendered_text, pos)

        # draw sweep line
        a = math.sin(math.radians(angle)) * 700.0
        b = math.cos(math.radians(angle)) * 700.0
        pygame.draw.line(radarDisplay, colors.green, (700, 780), (700 - int(b), 780 - int(a)), 3)

        # draw angle info
        angle_text = fontRenderer.render("Angle : " + str(angle), 1, colors.white)
        radarDisplay.blit(angle_text, (40,40))

        # draw distance info
        dist_text = fontRenderer.render(
            "Distance : Out Of Range" if distance == -1 else f"Distance : {distance} cm",
            1, colors.white
        )
        radarDisplay.blit(dist_text, (40,80))

        # draw targets - using safe iteration
        for angle_key in list(targets.keys()):  # Create a copy of keys for safe iteration
            target = targets.get(angle_key)
            if not target:  # Skip if target was removed
                continue

            try:
                # calculate target position (updated for 60cm range)
                c = math.sin(math.radians(target.angle)) * 800.0
                d = math.cos(math.radians(target.angle)) * 800.0
                e = math.sin(math.radians(target.angle)) * (700 / 60) * target.distance
                f = math.cos(math.radians(target.angle)) * (700 / 60) * target.distance

                # draw target line
                pygame.draw.line(
                    radarDisplay, 
                    target.color, 
                    (700 - int(f), 780 - int(e)), 
                    (700 - int(d), 780 - int(c)), 
                    3
                )

                # fading effect
                diffTime = time.time() - target.time
                
                if diffTime <= 0.5:
                    target.color = colors.red1L
                elif 0.5 < diffTime <= 1.0:
                    target.color = colors.red2L
                elif 1.0 < diffTime <= 1.5:
                    target.color = colors.red3L
                elif 1.5 < diffTime <= 2.0:
                    target.color = colors.red4L
                elif 2.0 < diffTime <= 2.5:
                    target.color = colors.red5L
                elif 2.5 < diffTime <= 3.0:
                    target.color = colors.red6L
                elif diffTime > 3.0:
                    del targets[angle_key]  # Remove old targets

            except (AttributeError, KeyError) as e:
                print(f"Error drawing target: {e}")
                continue

        pygame.display.update()

    except Exception as e:
        print(f"Display error: {e}")
        raise