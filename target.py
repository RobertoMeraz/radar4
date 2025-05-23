import time
import colors

class Target:
    def __init__(self, angle, distance):
        self.angle = angle
        self.distance = distance
        self.time = time.time()
        self.color = colors.red
        self.confidence = 1.0
        self.last_update = time.time()
        
    def update(self, new_distance):
        """Actualiza el target con nuevo dato"""
        now = time.time()
        time_diff = now - self.last_update
        
        # Filtro de suavizado (menor peso a cambios bruscos)
        smoothing_factor = min(0.7, time_diff * 0.5)  # Ajuste dinámico
        self.distance = (self.distance * (1-smoothing_factor)) + (new_distance * smoothing_factor)
        
        # Actualizar propiedades
        self.last_update = now
        self.time = now  # Resetear timer de vida
        self.confidence = min(1.0, self.confidence + 0.2)  # Aumentar confianza
        
        # Ajustar color basado en confianza
        if self.confidence > 0.8:
            self.color = colors.red
        elif self.confidence > 0.6:
            self.color = colors.red1L
        elif self.confidence > 0.4:
            self.color = colors.red2L
        else:
            self.color = colors.red3L
    
    def should_remove(self):
        """Determina si el target debe ser eliminado"""
        return (time.time() - self.time) > 5.0  # 5 segundos sin actualizaciones
        
    def __str__(self):
        return f"Target({self.angle}°, {self.distance:.1f}cm, conf: {self.confidence:.1f})"