import RPi.GPIO as GPIO
import pygame
import time
import sys
from ultrasonicsensor import UltrasonicSensor
from target import Target
from display import draw

# Configuración
SERVO_PIN = 12       # Pin físico para el servo
TRIG_PIN = 16        # Pin físico para TRIG
ECHO_PIN = 18        # Pin físico para ECHO
MAX_DISTANCE = 60    # cm (rango máximo de detección)
SWEEP_STEP = 2       # Paso de barrido en grados
SWEEP_DELAY = 0.02   # Tiempo entre pasos (ajustable)

def setup():
    """Configura hardware y pygame"""
    try:
        # Inicializar GPIO (modo BOARD para consistencia)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Configurar servo
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)  # Frecuencia 50Hz
        servo.start(7.5)  # Posición inicial (90°)
        time.sleep(0.5)   # Tiempo para estabilizar
        
        # Inicializar pygame
        pygame.init()
        screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption(f'Radar Ultrasónico (Rango: {MAX_DISTANCE}cm)')
        font = pygame.font.SysFont('Arial', 20)
        
        # Inicializar sensor con modo BOARD
        sensor = UltrasonicSensor(TRIG_PIN, ECHO_PIN, GPIO.BOARD)
        
        return servo, screen, font, sensor
        
    except Exception as e:
        print(f"Error en setup: {str(e)}")
        GPIO.cleanup()
        sys.exit(1)

def main():
    """Función principal del radar"""
    servo, screen, font, sensor = setup()
    targets = {}  # Diccionario para almacenar objetivos
    clock = pygame.time.Clock()
    
    try:
        while True:
            # Barrido de ida (0° a 180°)
            for angle in range(0, 181, SWEEP_STEP):
                handle_sweep(angle, servo, sensor, targets, screen, font)
                
            # Barrido de vuelta (180° a 0°)
            for angle in range(180, -1, -SWEEP_STEP):
                handle_sweep(angle, servo, sensor, targets, screen, font)
                
    except KeyboardInterrupt:
        print("\nDeteniendo radar...")
    finally:
        cleanup(servo, sensor)

def handle_sweep(angle, servo, sensor, targets, screen, font):
    """Maneja un paso del barrido"""
    # Control servo (convertir ángulo a ciclo de trabajo)
    servo_angle = 180 - angle  # Invertir para orientación correcta
    duty_cycle = (servo_angle / 18.0) + 2.5  # Fórmula ajustada
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(SWEEP_DELAY)
    
    # Obtener distancia con filtro de rango
    distance = sensor.get_distance(max_distance=MAX_DISTANCE)
    
    # Actualizar targets si hay detección válida
    if distance != -1:
        if angle in targets:
            targets[angle].update(distance)
        else:
            targets[angle] = Target(angle, distance)
    
    # Limpieza de targets antiguos
    current_time = time.time()
    targets_to_remove = [
        angle_key for angle_key, target in targets.items()
        if current_time - target.time > 5.0  # 5 segundos sin actualización
    ]
    for angle_key in targets_to_remove:
        del targets[angle_key]
    
    # Renderizar pantalla
    draw(screen, targets, angle, distance, font)
    
    # Manejar eventos pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt
    
    # Control de FPS
    clock.tick(30)

def cleanup(servo, sensor):
    """Limpia recursos de manera segura"""
    try:
        # Regresar servo a posición central
        servo.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        servo.stop()
        
        # Limpiar sensor y GPIO
        sensor.cleanup()
        
        # Cerrar pygame
        pygame.quit()
        
    except Exception as e:
        print(f"Error en cleanup: {str(e)}")
    finally:
        sys.exit()

if __name__ == "__main__":
    main()