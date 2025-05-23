import time
import statistics
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        """Inicializa el sensor con filtros avanzados"""
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        self.last_valid_distance = -1
        self.consecutive_errors = 0
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.output(self.TRIG, False)
        time.sleep(1)  # Tiempo inicial de estabilización

    def _clean_measurement(self, distance, max_distance):
        """Filtra mediciones erróneas conocidas"""
        # Filtro específico para falsas lecturas de ~3cm
        if 2.5 <= distance <= 3.5:
            return -1
            
        # Rango válido aumentado (5cm a max_distance)
        if not (5 <= distance <= max_distance):
            return -1
            
        return distance

    def get_distance(self, max_distance=60, samples=7, required_valid=5):
        """Obtiene distancia con múltiples capas de filtrado"""
        measurements = []
        
        for _ in range(samples):
            try:
                # Limpieza previa al pulso
                GPIO.output(self.TRIG, False)
                time.sleep(0.05)  # Mayor tiempo entre pulsos
                
                # Disparo ultrasónico
                GPIO.output(self.TRIG, True)
                time.sleep(0.0001)
                GPIO.output(self.TRIG, False)

                # Espera eco con timeout
                timeout = time.time() + 0.1  # 100ms máximo
                
                while GPIO.input(self.ECHO) == 0:
                    if time.time() > timeout:
                        raise TimeoutError()
                pulse_start = time.time()
                
                while GPIO.input(self.ECHO) == 1:
                    if time.time() > timeout:
                        raise TimeoutError()
                pulse_end = time.time()

                # Cálculo y filtrado
                distance = round((pulse_end - pulse_start) * 17150, 2)
                clean_dist = self._clean_measurement(distance, max_distance)
                
                if clean_dist != -1:
                    measurements.append(clean_dist)
                    
            except Exception:
                continue

        # Validación estadística
        if len(measurements) >= required_valid:
            median_dist = statistics.median(measurements)
            
            # Filtro de consistencia con última lectura válida
            if self.last_valid_distance != -1:
                if abs(median_dist - self.last_valid_distance) > 20:  # Cambio máximo permitido
                    self.consecutive_errors += 1
                    return -1
                    
            self.consecutive_errors = 0
            self.last_valid_distance = median_dist
            return median_dist
        else:
            self.consecutive_errors += 1
            # Resetear después de muchos errores consecutivos
            if self.consecutive_errors > 10:
                self.last_valid_distance = -1
            return -1

    def cleanup(self):
        """Limpia los GPIO"""
        GPIO.output(self.TRIG, False)
        time.sleep(0.1)