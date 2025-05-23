import time
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        """Inicializa el sensor ultrasónico"""
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        
        # Configuración de GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        
        # Estabilizar el sensor
        GPIO.output(self.TRIG, False)
        time.sleep(0.5)
        print("Sensor ultrasónico inicializado")

    def get_distance(self):
        """Obtiene la distancia en cm"""
        try:
            # Enviar pulso de trigger
            GPIO.output(self.TRIG, True)
            time.sleep(0.00001)  # 10 microsegundos
            GPIO.output(self.TRIG, False)
            
            # Esperar el eco (pulso HIGH)
            timeout = time.time() + 0.1  # Timeout de 100ms
            
            # Esperar inicio del pulso
            while GPIO.input(self.ECHO) == 0 and time.time() < timeout:
                pulse_start = time.time()
            
            if time.time() >= timeout:
                print("Timeout esperando inicio de pulso")
                return -1
            
            # Esperar fin del pulso
            while GPIO.input(self.ECHO) == 1 and time.time() < timeout:
                pulse_end = time.time()
            
            if time.time() >= timeout:
                print("Timeout esperando fin de pulso")
                return -1
            
            # Calcular distancia
            pulse_duration = pulse_end - pulse_start
            distance = round((pulse_duration * 34300) / 2, 2)  # Velocidad del sonido: 34300 cm/s
            
            # Validar rango razonable (2cm a 400cm)
            if 2 <= distance <= 50:
                return distance
            else:
                print(f"Distancia fuera de rango: {distance}cm")
                return -1
                
        except Exception as e:
            print(f"Error al leer sensor: {str(e)}")
            return -1

    def cleanup(self):
        """Limpia los recursos GPIO"""
        GPIO.cleanup()
        print("GPIO limpiado")

# Ejemplo de uso
if __name__ == "__main__":
    try:
        # Configura tus pines aquí (BCM numbering)
        sensor = UltrasonicSensor(trig_pin=23, echo_pin=24)
        
        while True:
            distance = sensor.get_distance()
            if distance != -1:
                print(f"Distancia: {distance} cm")
            else:
                print("Objeto no detectado o fuera de rango")
            
            time.sleep(1)  # Espera 1 segundo entre lecturas
            
    except KeyboardInterrupt:
        print("\nDeteniendo el programa...")
    finally:
        sensor.cleanup()