import time
import RPi.GPIO as GPIO

def ultrasonicRead(GPIO, TRIG, ECHO):
    """Versión balanceada con mejor sensibilidad"""
    
    # 1. Estabilización del sensor
    GPIO.output(TRIG, False)
    time.sleep(0.02)  # Tiempo equilibrado
    
    # 2. Pulso ultrasónico
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10μs (óptimo para HC-SR04)
    GPIO.output(TRIG, False)
    
    timeout = time.time() + 0.04  # Timeout para ~60cm (40ms)
    
    # 3. Detección de eco mejorada
    try:
        # Espera inicio del eco
        start_time = None
        while GPIO.input(ECHO) == 0:
            start_time = time.time()
            if time.time() > timeout:
                return -1
        
        # Espera fin del eco
        end_time = None
        while GPIO.input(ECHO) == 1:
            end_time = time.time()
            if time.time() > timeout:
                return -1
        
        # 4. Validación básica
        if start_time is None or end_time is None:
            return -1
            
        # 5. Cálculo y filtrado inteligente
        duration = end_time - start_time
        distance = round((duration * 34300) / 2, 2)
        
        # Filtros mejorados:
        if distance <= 2:  # Ignorar ruido muy cercano
            return -1
        elif 2 < distance <= 60:  # Rango útil aumentado
            return distance
        else:  # Fuera de rango
            return -1
            
    except Exception:
        return -1