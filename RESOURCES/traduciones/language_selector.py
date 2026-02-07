"""
Widget para seleccionar idioma de la aplicación
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal
from .config_idioma import get_available_languages, get_language
from .translations import translate
from .language_manager import language_manager


class LanguageSelector(QWidget):
    """Widget para cambiar el idioma de la aplicación."""
    
    language_changed = Signal(str)  # Emite el código de idioma cuando cambia
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz del selector de idioma."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Etiqueta
        label = QLabel(translate("Language:"))
        layout.addWidget(label)
        
        # ComboBox de idiomas
        self.combo_languages = QComboBox()
        
        # Cargar idiomas disponibles
        available_langs = get_available_languages()
        for code, name in available_langs.items():
            self.combo_languages.addItem(name, code)
        
        # Establecer el idioma actual
        current_lang = get_language()
        index = self.combo_languages.findData(current_lang)
        if index >= 0:
            self.combo_languages.setCurrentIndex(index)
        
        # Conectar señal
        self.combo_languages.currentIndexChanged.connect(self._on_language_changed)
        
        layout.addWidget(self.combo_languages)
        layout.addStretch()
        
    def _on_language_changed(self, index):
        """Maneja el cambio de idioma."""
        language_code = self.combo_languages.itemData(index)
        # Usar el gestor global para cambiar el idioma
        language_manager.set_language(language_code)
        self.language_changed.emit(language_code)
        
    def get_selected_language(self) -> str:
        """Retorna el código de idioma seleccionado."""
        return self.combo_languages.currentData()
