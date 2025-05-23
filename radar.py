import RPi.GPIO as GPIO
import pygame
import time
import sys
import traceback
from ultrasonicsensor import UltrasonicSensor
from target import Target
from display import draw

# Configuración
SERVO_PIN = 12       # Pin físico para el servo (GPIO18)
TRIG_PIN = 16        # Pin físico para TRIG (GPIO23)
ECHO_PIN = 18        # Pin físico para ECHO (GPIO24)
MAX_DISTANCE = 60    # cm
SWEEP_STEP = 2       # Paso de barrido
SWEEP_DELAY = 0.03   # Tiempo entre pasos

def setup_gpio():
    """Configuración segura de GPIO"""
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Configurar servo
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
        servo.start(0)
        time.sleep(0.5)
        
        return servo
    except Exception as e:
        print(f"Error configurando GPIO: {str(e)}")
        raise

def setup_pygame():
    """Configuración segura de Pygame"""
    try:
        pygame.init()
        screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption(f'Radar Ultrasónico (Rango: {MAX_DISTANCE}cm)')
        font = pygame.font.SysFont('Arial', 20)
        return screen, font
    except Exception as e:
        print(f"Error configurando Pygame: {str(e)}")
        raise

def setup():
    """Configuración completa del sistema"""
    try:
        # Inicializar componentes en orden seguro
        servo = setup_gpio()
        screen, font = setup_pygame()
        sensor = UltrasonicSensor(TRIG_PIN, ECHO_PIN, GPIO.BOARD)
        
        print("Todos los componentes inicializados correctamente")
        return servo, screen, font, sensor
        
    except Exception as e:
        print("\nError durante la inicialización:")
        traceback.print_exc()
        cleanup(None, None)
        sys.exit(1)

def main():
    """Función principal"""
    print("Iniciando radar...")
    servo, screen, font, sensor = setup()
    targets = {}
    clock = pygame.time.Clock()
    
    try:
        print("Iniciando barrido...")
        while True:
            # Barrido de ida
            for angle in range(0, 181, SWEEP_STEP):
                handle_sweep(angle, servo, sensor, targets, screen, font)
            
            # Barrido de vuelta
            for angle in range(180, -1, -SWEEP_STEP):
                handle_sweep(angle, servo, sensor, targets, screen, font)
                
    except KeyboardInterrupt:
        print("\nDetención solicitada por usuario")
    except Exception as e:
        print("\nError durante la ejecución:")
        traceback.print_exc()
    finally:
        cleanup(servo, sensor)

def handle_sweep(angle, servo, sensor, targets, screen, font):
    """Manejo seguro de cada paso del barrido"""
    try:
        # Control servo
        duty_cycle = 2.5 + (angle / 18.0)
        servo.ChangeDutyCycle(duty_cycle)
        time.sleep(SWEEP_DELAY)
        
        # Lectura del sensor
        distance = sensor.get_distance(max_distance=MAX_DISTANCE)
        
        # Actualización de targets
        if distance != -1:
            if angle in targets:
                targets[angle].update(distance)
            else:
                targets[angle] = Target(angle, distance)
        
        # Limpieza de targets antiguos
        current_time = time.time()
        targets_to_remove = [k for k, t in targets.items() if current_time - t.time > 5.0]
        for k in targets_to_remove:
            del targets[k]
        
        # Renderizado
        draw(screen, targets, angle, distance, font)
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
                
        clock.tick(30)
        
    except Exception as e:
        print(f"Error en handle_sweep: {str(e)}")
        raise

def cleanup(servo, sensor):
    """Limpieza segura de recursos"""
    print("\nLimpiando recursos...")
    try:
        if servo:
            servo.ChangeDutyCycle(7.5)  # Centrar servo
            time.sleep(0.3)
            servo.stop()
            
        if sensor:
            sensor.cleanup()
            
        pygame.quit()
        GPIO.cleanup()
        print("Recursos liberados correctamente")
    except Exception as e:
        print(f"Error durante cleanup: {str(e)}")
    finally:
        sys.exit()

if __name__ == "__main__":
    main()