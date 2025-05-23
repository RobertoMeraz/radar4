import time
import RPi.GPIO as GPIO

def ultrasonicRead(GPIO, TRIG, ECHO, max_distance=60):
    """
    Versión mejorada con:
    - Mayor tiempo de estabilización
    - Timeout ajustado
    - Filtro de ruido
    - Manejo de errores robusto
    """
    
    # 1. Estabilización del sensor (tiempo aumentado)
    GPIO.output(TRIG, False)
    time.sleep(0.02)  # Aumentado de 0.01 a 0.02 segundos
    
    # 2. Envío del pulso ultrasónico
    GPIO.output(TRIG, True)
    time.sleep(0.0001)  # Pulso de 10μs
    GPIO.output(TRIG, False)
    
    timeout_start = time.time()
    
    # 3. Medición del tiempo de eco (con timeout)
    try:
        # Espera por el inicio del eco
        while GPIO.input(ECHO) == 0:
            if time.time() - timeout_start > 0.1:  # Timeout de 100ms
                return -1
        pulse_start = time.time()
        
        # Espera por el fin del eco
        while GPIO.input(ECHO) == 1:
            if time.time() - timeout_start > 0.1:  # Timeout de 100ms
                return -1
        pulse_end = time.time()
        
        # 4. Cálculo de distancia
        pulse_duration = pulse_end - pulse_start
        distance = (34300 * pulse_duration) / 2  # Velocidad del sonido (343 m/s)
        distance = round(distance, 2)
        
        # 5. Filtrado de resultados
        if 2 <= distance <= max_distance:  # Ignora valores <2cm (ruido) y >max_distance
            return distance
        return -1
    
    except Exception as e:
        print(f"Error en medición: {str(e)}")
        return -1