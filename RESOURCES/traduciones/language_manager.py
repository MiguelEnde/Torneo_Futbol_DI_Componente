"""
Gestor global de idiomas para la aplicación.
Proporciona un sistema de señales para notificar a todas las vistas cuando cambia el idioma.
"""

from PySide6.QtCore import QObject, Signal
from .config_idioma import set_language, get_language


class LanguageManager(QObject):
    """Gestor global de idiomas con sistema de señales."""
    
    # Señal que se emite cuando cambia el idioma
    language_changed = Signal(str)  # Emite el código de idioma
    
    _instance = None  # Singleton
    _initialized = False  # Flag de inicialización
    
    def __new__(cls):
        """Implementar patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el gestor de idiomas."""
        # Solo inicializar una vez
        if LanguageManager._initialized:
            return
        
        super().__init__()
        LanguageManager._initialized = True
    
    def set_language(self, language_code: str):
        """
        Cambia el idioma de la aplicación y emite señal de cambio.
        
        Args:
            language_code: Código de idioma ('es' o 'en')
        """
        if set_language(language_code):
            self.language_changed.emit(language_code)
    
    def get_language(self) -> str:
        """
        Obtiene el código del idioma actual.
        
        Returns:
            str: Código de idioma ('es' o 'en')
        """
        return get_language()


# Instancia global del gestor
language_manager = LanguageManager()
