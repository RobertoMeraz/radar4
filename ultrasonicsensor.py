import time
import RPi.GPIO as GPIO
from collections import deque

# Configuración del filtro
READING_HISTORY_SIZE = 5  # Número de lecturas para el promedio
MIN_VALID_DISTANCE = 5    # Distancia mínima válida (cm)
MAX_VALID_DISTANCE = 60   # Distancia máxima válida (cm)
NOISE_THRESHOLD = 3.5     # Ignorar lecturas menores a este valor (cm)
MAX_DIFF_CONSECUTIVE = 20 # Máxima diferencia permitida entre lecturas consecutivas (cm)

# Estado global para el filtrado (sin necesidad de modificar radar.py)
_distance_history = deque(maxlen=READING_HISTORY_SIZE)
_last_valid_distance = -1
_consecutive_errors = 0

def ultrasonicRead(GPIO, TRIG, ECHO):
    """Versión mejorada con filtrado de ruido y detección de falsos positivos"""
    global _distance_history, _last_valid_distance, _consecutive_errors
    
    # 1. Estabilización del sensor
    GPIO.output(TRIG, False)
    time.sleep(0.02)  # Tiempo aumentado para mayor estabilidad
    
    # 2. Envío del pulso ultrasónico
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # Pulso preciso de 10μs
    GPIO.output(TRIG, False)
    
    # 3. Medición del tiempo de eco con timeout
    timeout = time.time() + 0.1  # 100ms máximo (para ~1.7m)
    try:
        # Espera por el inicio del eco
        while GPIO.input(ECHO) == 0:
            if time.time() > timeout:
                raise TimeoutError()
        pulse_start = time.time()
        
        # Espera por el fin del eco
        while GPIO.input(ECHO) == 1:
            if time.time() > timeout:
                raise TimeoutError()
        pulse_end = time.time()
        
        # 4. Cálculo de distancia
        pulse_duration = pulse_end - pulse_start
        current_distance = round((pulse_duration * 34300) / 2, 2)
        
        # 5. Filtrado en múltiples capas
        # Capa 1: Filtro de rango absoluto
        if not (MIN_VALID_DISTANCE <= current_distance <= MAX_VALID_DISTANCE):
            _consecutive_errors += 1
            return -1
        
        # Capa 2: Filtro de ruido específico (3cm)
        if current_distance <= NOISE_THRESHOLD:
            _consecutive_errors += 1
            return -1
        
        # Capa 3: Filtro de consistencia con lectura anterior
        if _last_valid_distance != -1:
            if abs(current_distance - _last_valid_distance) > MAX_DIFF_CONSECUTIVE:
                _consecutive_errors += 1
                return -1
        
        # Capa 4: Filtro histórico (promedio móvil)
        _distance_history.append(current_distance)
        if len(_distance_history) == READING_HISTORY_SIZE:
            avg_distance = sum(_distance_history) / READING_HISTORY_SIZE
            if abs(current_distance - avg_distance) > (MAX_DIFF_CONSECUTIVE / 2):
                _consecutive_errors += 1
                return -1
        
        # Si pasa todos los filtros
        _consecutive_errors = 0
        _last_valid_distance = current_distance
        return current_distance
        
    except Exception:
        _consecutive_errors += 1
        # Resetear después de 10 errores consecutivos
        if _consecutive_errors > 10:
            _distance_history.clear()
            _last_valid_distance = -1
        return -1