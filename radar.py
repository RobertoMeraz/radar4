import RPi.GPIO as GPIO
import pygame
import time
import sys
from ultrasonicsensor import UltrasonicSensor
from target import Target
from display import draw

# Configuración
SERVO_PIN = 12
TRIG_PIN = 16
ECHO_PIN = 18
MAX_DISTANCE = 60  # cm
SWEEP_STEP = 2     # Paso de barrido en grados

def setup():
    """Configura hardware y pygame"""
    try:
        # Inicializar GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Configurar servo
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)
        servo.start(7)  # Posición inicial (90°)
        
        # Inicializar pygame
        pygame.init()
        screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption(f'Radar Ultrasónico (Rango: {MAX_DISTANCE}cm)')
        font = pygame.font.SysFont('Arial', 20)
        
        # Inicializar sensor
        sensor = UltrasonicSensor(TRIG_PIN, ECHO_PIN)
        
        return servo, screen, font, sensor
        
    except Exception as e:
        print(f"Error inicializando: {str(e)}")
        GPIO.cleanup()
        sys.exit(1)

def main():
    servo, screen, font, sensor = setup()
    targets = {}
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
    # Control servo
    servo_angle = 180 - angle
    duty_cycle = (servo_angle / 18.0) + 2
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)  # Pequeña pausa para el servo
    
    # Obtener distancia con filtros estrictos
    distance = sensor.get_distance(
        max_distance=MAX_DISTANCE,
        samples=7,
        required_valid=5
    )
    
    # Actualizar targets solo si es una detección válida
    if distance != -1:
        if angle in targets:
            targets[angle].update(distance)
        else:
            targets[angle] = Target(angle, distance)
    
    # Eliminar targets antiguos
    current_time = time.time()
    for angle_key in list(targets.keys()):
        if current_time - targets[angle_key].time > 5.0:  # 5 segundos sin actualización
            del targets[angle_key]
    
    # Renderizar
    draw(screen, targets, angle, distance, font)
    
    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt

def cleanup(servo, sensor):
    """Limpia recursos"""
    servo.stop()
    sensor.cleanup()
    GPIO.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()