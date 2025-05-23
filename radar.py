import RPi.GPIO as GPIO
import pygame
import math
import time
import colors
import sys
from target import Target
from display import draw
from ultrasonicsensor import ultrasonicRead

# Configuración mejorada
SENSOR_TRIG = 16  # GPIO23 (Pin 16)
SENSOR_ECHO = 18  # GPIO24 (Pin 18)
SERVO_PIN = 12    # GPIO18 (Pin 12)
MAX_DISTANCE = 60 # cm

def setup_hardware():
    """Configuración robusta de hardware"""
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Configuración del servo
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
        servo.start(7)  # Posición inicial (90°)
        
        # Configuración del sensor ultrasónico
        GPIO.setup(SENSOR_TRIG, GPIO.OUT)
        GPIO.setup(SENSOR_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        return servo
    
    except Exception as e:
        print(f"Error en configuración de hardware: {str(e)}")
        GPIO.cleanup()
        sys.exit(1)

def main():
    print('=== Sistema de Radar Iniciado ===')
    
    # Inicialización de pygame
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption(f'Radar (Rango: {MAX_DISTANCE}cm)')
    
    # Configuración de hardware
    servo = setup_hardware()
    targets = {}
    
    try:
        while True:
            # Barrido de 0° a 180°
            for angle in range(0, 181, 2):  # Paso de 2° para mayor fluidez
                # Medición con filtrado
                distance = ultrasonicRead(GPIO, SENSOR_TRIG, SENSOR_ECHO, samples=3, max_distance=MAX_DISTANCE)
                
                # Registro de objetivos
                if distance != -1:
                    targets[angle] = Target(angle, distance)
                    print(f"Objeto: {distance}cm @ {angle}°")  # Debug
                
                # Renderizado
                draw(screen, targets, angle, distance, font)
                
                # Control del servo
                servo_angle = 180 - angle  # Conversión para servo
                duty_cycle = (servo_angle / 18.0) + 2
                servo.ChangeDutyCycle(duty_cycle)
                
                time.sleep(0.01)  # Pausa para estabilidad
                
                # Manejo de eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
            
            # Barrido de retorno (180° a 0°)
            for angle in range(180, -1, -2):
                distance = ultrasonicRead(GPIO, SENSOR_TRIG, SENSOR_ECHO, samples=3, max_distance=MAX_DISTANCE)
                
                if distance != -1:
                    targets[angle] = Target(angle, distance)
                
                draw(screen, targets, angle, distance, font)
                servo_angle = 180 - angle
                duty_cycle = (servo_angle / 18.0) + 2
                servo.ChangeDutyCycle(duty_cycle)
                time.sleep(0.01)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n=== Deteniendo radar ===")
    
    finally:
        servo.stop()
        GPIO.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()