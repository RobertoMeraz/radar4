import time
import colors

class Target:
    def __init__(self, angle, distance):
        """Inicializa un objetivo detectado"""
        self.angle = angle
        self.distance = distance
        self.time = time.time()
        self.color = colors.red3L  # Inicia semitransparente
        self.valid_readings = 1    # Contador de lecturas válidas
        
    def update(self, new_distance):
        """Actualiza el objetivo con nueva información"""
        # Filtro de consistencia (rechaza cambios bruscos)
        if abs(new_distance - self.distance) > 20:  # Máximo 20cm de diferencia
            return
            
        # Suavizado exponencial
        self.distance = (self.distance * 0.6) + (new_distance * 0.4)
        self.time = time.time()
        self.valid_readings += 1
        
        # Actualizar color basado en confianza
        if self.valid_readings > 3:
            self.color = colors.red  # Rojo sólido cuando está confirmado
        elif self.valid_readings > 2:
            self.color = colors.red1L
        else:
            self.color = colors.red3L  # Semitransparente al inicio
            
    def should_remove(self):
        """Determina si el objetivo debe ser eliminado"""
        return (time.time() - self.time) > 5.0  # 5 segundos sin actualizarse
        
    def __str__(self):
        return f"Target({self.angle}°, {self.distance:.1f}cm, conf:{self.valid_readings})"