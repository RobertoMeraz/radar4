import time
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin, mode=GPIO.BOARD):
        """Inicializa el sensor ultrasónico"""
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        
        # Configuración de GPIO (consistente con radar.py)
        GPIO.setmode(mode)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        
        # Estabilizar el sensor
        GPIO.output(self.TRIG, False)
        time.sleep(0.5)
        print(f"Sensor ultrasónico inicializado (TRIG: {trig_pin}, ECHO: {echo_pin})")

    def get_distance(self, max_distance=60):
        """Versión mejorada basada en el código original"""
        try:
            # settling the sensor
            GPIO.output(self.TRIG, False)
            time.sleep(0.0001)

            # send a signal (como en el original)
            GPIO.output(self.TRIG, True)
            time.sleep(0.0001)  # 100μs como en el original
            GPIO.output(self.TRIG, False)

            # catch a signal (con timeout mejorado)
            timeout_start = time.time()
            while GPIO.input(self.ECHO) == 0:
                start_time = time.time()
                if time.time() - timeout_start > 0.1:  # Timeout de 100ms
                    return -1

            end_time = time.time()
            timeout_start = time.time()
            while GPIO.input(self.ECHO) == 1:
                end_time = time.time()
                if time.time() - timeout_start > 0.1:  # Timeout de 100ms
                    return -1

            # calculate the distance (igual que el original)
            total_time = end_time - start_time
            distance = (34300 * total_time) / 2
            distance = round(distance, 2)
            
            # Ajustado al max_distance definido en radar.py
            if 2 <= distance <= max_distance:
                return distance
            return -1
                
        except Exception as e:
            print(f"Error en get_distance: {str(e)}")
            return -1

    def cleanup(self):
        """Limpia los recursos GPIO"""
        GPIO.cleanup()
        print("GPIO limpiado")