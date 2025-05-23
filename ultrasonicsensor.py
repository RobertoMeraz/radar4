import time
import statistics

def ultrasonicRead(GPIO, TRIG, ECHO, samples=3, max_distance=60):
    """
    Versión mejorada con:
    - Múltiples muestras para reducir ruido
    - Filtro de mediana
    - Timeout dinámico
    - Validación de rangos
    """
    measurements = []
    
    for _ in range(samples):
        try:
            # Estabilización del sensor
            GPIO.output(TRIG, False)
            time.sleep(0.01)
            
            # Envío del pulso
            GPIO.output(TRIG, True)
            time.sleep(0.0001)
            GPIO.output(TRIG, False)
            
            # Timeout basado en la distancia máxima (4ms por cm * 60cm = 240ms)
            timeout = time.time() + 0.24
            
            # Espera por el eco
            while GPIO.input(ECHO) == 0:
                if time.time() > timeout:
                    raise TimeoutError("Timeout en espera de eco")
                pulse_start = time.time()
            
            while GPIO.input(ECHO) == 1:
                if time.time() > timeout:
                    raise TimeoutError("Timeout en recepción de eco")
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2  # Velocidad del sonido (343 m/s)
            
            # Filtro de datos inválidos
            if 2 <= distance <= max_distance:  # Ignorar medidas <2cm (ruido típico)
                measurements.append(round(distance, 2))
                
            time.sleep(0.02)  # Intervalo entre muestras
            
        except Exception as e:
            print(f"Error en medición: {str(e)}")
            continue
    
    # Retorna la mediana de las mediciones válidas
    if measurements:
        return statistics.median(measurements)
    return -1