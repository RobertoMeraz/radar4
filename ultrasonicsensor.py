import time
import RPi.GPIO as GPIO

def ultrasonicRead(GPIO, TRIG, ECHO):
    """Versión mejorada con filtrado de ruido y timeout controlado"""
    
    # 1. Estabilización del sensor (tiempo aumentado)
    GPIO.output(TRIG, False)
    time.sleep(0.05)  # Tiempo aumentado para mayor estabilidad
    
    # 2. Envío del pulso ultrasónico
    GPIO.output(TRIG, True)
    time.sleep(0.0001)  # Pulso de 10μs
    GPIO.output(TRIG, False)
    
    timeout_start = time.time()
    timeout_max = 0.1  # 100ms máximo (para 50cm)
    
    # 3. Medición del tiempo de eco (con timeout mejorado)
    try:
        # Espera por el inicio del eco
        while GPIO.input(ECHO) == 0:
            if time.time() - timeout_start > timeout_max:
                return -1
        pulse_start = time.time()
        
        # Espera por el fin del eco
        while GPIO.input(ECHO) == 1:
            if time.time() - timeout_start > timeout_max:
                return -1
        pulse_end = time.time()
        
        # 4. Cálculo de distancia
        pulse_duration = pulse_end - pulse_start
        distance = (34300 * pulse_duration) / 2  # Velocidad del sonido (343 m/s)
        distance = round(distance, 2)
        
        # 5. Filtrado avanzado
        if distance <= 2.5:  # Ignorar lecturas muy cortas (ruido típico)
            return -1
        elif 2.5 < distance <= 3.5:  # Bloqueo específico para falsos 3cm
            return -1
        elif 3.5 < distance <= 50:   # Rango válido
            return distance
        else:                        # Fuera de rango
            return -1
            
    except Exception:
        return -1  # En caso de cualquier error