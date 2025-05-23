import time
import statistics
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        """Inicializa el sensor ultrasónico con filtrado avanzado"""
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        self.last_valid_distance = -1
        self.consecutive_detections = 0
        self.measurement_history = []
        
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.output(self.TRIG, False)
        time.sleep(1)  # Tiempo de estabilización inicial

    def _take_measurement(self, max_distance):
        """Toma una única medición con timeout controlado"""
        try:
            GPIO.output(self.TRIG, True)
            time.sleep(0.0001)
            GPIO.output(self.TRIG, False)

            timeout = time.time() + (max_distance * 0.004) + 0.1  # 4ms/cm + margen
            
            while GPIO.input(self.ECHO) == 0:
                if time.time() > timeout:
                    return -1
            pulse_start = time.time()
            
            while GPIO.input(self.ECHO) == 1:
                if time.time() > timeout:
                    return -1
            pulse_end = time.time()

            distance = round((pulse_end - pulse_start) * 17150, 2)
            return distance if 2 <= distance <= max_distance else -1
            
        except Exception:
            return -1

    def get_distance(self, max_distance=60, samples=5, threshold=15, required_consecutive=3):
        """
        Obtiene distancia filtrada con múltiples capas de validación
        Args:
            max_distance: Distancia máxima válida (cm)
            samples: Número de muestras por medición
            threshold: Máxima variación permitida entre lecturas (cm)
            required_consecutive: Confirmaciones necesarias para detección
        """
        measurements = []
        
        # Toma múltiples muestras
        for _ in range(samples):
            dist = self._take_measurement(max_distance)
            if dist != -1:
                measurements.append(dist)
            time.sleep(0.01)
        
        if not measurements:
            self.consecutive_detections = 0
            return -1

        median_dist = statistics.median(measurements)
        
        # Filtro de consistencia con historial
        if self.last_valid_distance != -1:
            if abs(median_dist - self.last_valid_distance) > threshold:
                self.consecutive_detections = 0
                return -1
        
        # Actualiza historial (máximo 5 registros)
        self.measurement_history.append(median_dist)
        if len(self.measurement_history) > 5:
            self.measurement_history.pop(0)
        
        # Requiere confirmaciones consecutivas
        self.consecutive_detections += 1
        if self.consecutive_detections >= required_consecutive:
            self.last_valid_distance = median_dist
            return median_dist
        
        return -1

    def cleanup(self):
        """Limpia los GPIO"""
        GPIO.output(self.TRIG, False)