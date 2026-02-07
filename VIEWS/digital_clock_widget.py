"""
Vista del componente de Reloj Digital
Widget reutilizable que carga su interfaz desde un archivo .ui
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QTimer, QTime, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from RESOURCES.traduciones.translations import translate
import os


class DigitalClockWidget(QWidget):
    """
    Componente reutilizable de reloj digital
    Puede funcionar como reloj, cronómetro o temporizador
    """
    
    # Señales propias del componente
    alarmTriggered = Signal(str)  # Emite el mensaje de alarma
    timerFinished = Signal()       # Emite cuando el temporizador termina
    timeUpdated = Signal(str)      # Emite cada vez que se actualiza el tiempo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Cargar la interfaz desde el archivo .ui
        self.load_ui()
        
        # Timer interno para actualizar el reloj
        self.internal_timer = QTimer(self)
        self.internal_timer.timeout.connect(self._on_timer_tick)
        
        # Referencias a los widgets del UI
        self.setup_widget_references()
        
        # Conectar señales de los botones
        self.connect_signals()
        
    def load_ui(self):
        """Crea la interfaz manualmente"""
        from PySide6.QtWidgets import QLCDNumber, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
        
        # Crear layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Combo para modos
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo:"))
        self.comboMode = QComboBox(self)
        self.comboMode.addItems(["Reloj", "Cronómetro", "Temporizador"])
        mode_layout.addWidget(self.comboMode)
        layout.addLayout(mode_layout)
        
        # LCD Display
        self.lcdDisplay = QLCDNumber(self)
        self.lcdDisplay.setDigitCount(8)
        self.lcdDisplay.display("00:00:00")
        layout.addWidget(self.lcdDisplay)
        
        # Status
        self.lblStatus = QLabel("Listo", self)
        self.lblStatus.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lblStatus)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btnStart = QPushButton("Start", self)
        button_layout.addWidget(self.btnStart)
        
        self.btnPause = QPushButton("Pause", self)
        button_layout.addWidget(self.btnPause)
        
        self.btnReset = QPushButton("Reset", self)
        button_layout.addWidget(self.btnReset)
        
        layout.addLayout(button_layout)
        
    def setup_widget_references(self):
        """Los widgets ya están creados en load_ui"""
        pass
        
    def connect_signals(self):
        """Conecta las señales de los botones"""
        if self.btnStart:
            self.btnStart.clicked.connect(self.on_start_clicked)
        if self.btnPause:
            self.btnPause.clicked.connect(self.on_pause_clicked)
        if self.btnReset:
            self.btnReset.clicked.connect(self.on_reset_clicked)
        if hasattr(self, 'comboMode'):
            self.comboMode.currentTextChanged.connect(self.on_mode_changed)
    
    def set_controller(self, controller):
        """Establece el controlador para este widget"""
        self.controller = controller
        
    def update_display(self, text: str):
        """Actualiza el display LCD"""
        if self.lcdDisplay:
            self.lcdDisplay.display(text)
    
    def update_status(self, text: str):
        """Actualiza el label de estado"""
        if self.lblStatus:
            self.lblStatus.setText(text)
    
    def set_controls_enabled(self, start: bool, pause: bool, reset: bool):
        """Habilita/deshabilita los controles"""
        if self.btnStart:
            self.btnStart.setEnabled(start)
        if self.btnPause:
            self.btnPause.setEnabled(pause)
        if self.btnReset:
            self.btnReset.setEnabled(reset)
    
    def start_internal_timer(self):
        """Inicia el timer interno (actualización cada segundo)"""
        if not self.internal_timer.isActive():
            self.internal_timer.start(1000)  # 1 segundo
    
    def stop_internal_timer(self):
        """Detiene el timer interno"""
        if self.internal_timer.isActive():
            self.internal_timer.stop()
    
    def _on_timer_tick(self):
        """Callback interno cuando el timer hace tick"""
        if hasattr(self, 'controller'):
            self.controller.on_timer_tick()
    
    # Métodos de control que delegan al controlador
    def on_mode_changed(self, mode_text):
        """Maneja el cambio de modo"""
        mode_map = {
            "Reloj": "clock",
            "Cronómetro": "stopwatch", 
            "Temporizador": "timer",
            "Modo Fútbol": "football"
        }
        mode = mode_map.get(mode_text, "clock")
        if hasattr(self, 'controller'):
            self.controller.set_mode(mode)
    
    def on_timer_duration_changed(self, value):
        """Maneja el cambio de duración del temporizador"""
        if hasattr(self, 'controller'):
            self.controller.set_timer_value(value)
    
    def on_alarm_changed(self, state):
        """Maneja el cambio del estado de la alarma"""
        # Aquí se podría implementar lógica de alarma
        pass
    
    def on_language_changed(self):
        """Maneja el cambio de idioma"""
        # Cambiar entre ES y EN
        current_text = self.btnLanguage.text()
        if current_text == "ES/EN":
            self.btnLanguage.setText("EN/ES")
            self.retranslateUi("en")
        else:
            self.btnLanguage.setText("ES/EN")
            self.retranslateUi("es")
    
    def emit_alarm(self, message: str):
        """Emite la señal de alarma"""
        self.alarmTriggered.emit(message)
    
    def emit_timer_finished(self):
        """Emite la señal de temporizador finalizado"""
        self.timerFinished.emit()
    
    def emit_time_updated(self, time_str: str):
        """Emite la señal de tiempo actualizado"""
        self.timeUpdated.emit(time_str)
    
    # Métodos de control que delegan al controlador
    def on_start_clicked(self):
        """Maneja el clic en el botón Start"""
        if hasattr(self, 'controller'):
            self.controller.on_start()
    
    def on_pause_clicked(self):
        """Maneja el clic en el botón Pause"""
        if hasattr(self, 'controller'):
            self.controller.on_pause()
    
    def on_reset_clicked(self):
        """Maneja el clic en el botón Reset"""
        if hasattr(self, 'controller'):
            self.controller.on_reset()
    
    def on_mode_changed(self, mode_text):
        """Maneja el cambio de modo"""
        mode_map = {
            "Reloj": "clock",
            "Cronómetro": "stopwatch", 
            "Temporizador": "timer"
        }
        mode = mode_map.get(mode_text, "clock")
        if hasattr(self, 'controller'):
            self.controller.set_mode(mode)
    
    def retranslateUi(self, language: str = 'es'):
        """Retraduce los textos del UI (para el sistema de traducciones)"""
        # Este método será llamado cuando cambie el idioma
        if self.btnStart:
            self.btnStart.setText(translate("Start", language))
        if self.btnPause:
            self.btnPause.setText(translate("Pause", language))
        if self.btnReset:
            self.btnReset.setText(translate("Reset", language))
