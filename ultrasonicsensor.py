import time
import RPi.GPIO as GPIO

def ultrasonicRead(GPIO, TRIG, ECHO):
    """Versión mejorada con protección contra falsas detecciones"""
    
    # 1. Estabilización más robusta del sensor
    GPIO.output(TRIG, False)
    time.sleep(0.05)  # Tiempo aumentado para mayor estabilidad
    
    # 2. Pulso más preciso
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10μs exactos (reducido de 100μs)
    GPIO.output(TRIG, False)
    
    timeout = time.time() + 0.1  # Timeout de 100ms (para ~1.7m máximo)
    
    # 3. Medición con protección mejorada
    try:
        # Espera por el inicio del eco (mejorado)
        pulse_start = None
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if time.time() > timeout:
                return -1
        
        # Espera por el fin del eco (mejorado)
        pulse_end = None
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if time.time() > timeout:
                return -1
        
        # 4. Validación básica de tiempos
        if pulse_start is None or pulse_end is None:
            return -1
            
        # 5. Cálculo de distancia con filtros
        duration = pulse_end - pulse_start
        distance = round((duration * 34300) / 2, 2)
        
        # Filtros combinados:
        # - Ignorar distancias menores a 5cm (ruido típico)
        # - Ignorar el rango problemático de 2-4cm
        # - Mantener el rango máximo de 50cm
        if (distance >= 5 and distance <= 50 and 
            not (2 <= distance <= 4)):  # Bloqueo específico para falsos 3cm
            return distance
            
        return -1
        
    except Exception:
        return -1  # En caso de cualquier error