"""
Componente de Reloj Digital Reutilizable
Widget independiente que se puede integrar en cualquier aplicación PySide6
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QTimeEdit, QSpinBox, QLineEdit, QMessageBox
from PySide6.QtCore import Signal, QTimer, QTime, Qt
from PySide6.QtGui import QPalette, QColor
from RESOURCES.traduciones.translations import translate

try:
    from PySide6.QtWidgets import QLCDNumber
except ImportError:
    QLCDNumber = None


class DigitalClockWidget(QWidget):
    """
    Componente reutilizable de reloj digital.
    Puede funcionar como:
    - Reloj (muestra hora actual)
    - Cronómetro (cuenta hacia arriba)
    - Temporizador (cuenta hacia abajo desde un tiempo)
    - Modo Fútbol (cronómetro especial para partidos)
    """
    
    # Señales del componente
    alarmTriggered = Signal(str)      # Emite cuando se activa una alarma
    timerFinished = Signal()          # Emite cuando el temporizador termina
    timeUpdated = Signal(str)         # Emite cada actualización de tiempo
    matchTimeUpdated = Signal(int)    # Emite minutos transcurridos en modo fútbol
    goalScored = Signal(str)          # Emite cuando se marca un gol ("local" o "visitante")
    
    # Modos de funcionamiento
    MODE_CLOCK = 0
    MODE_CHRONOMETER = 1
    MODE_TIMER = 2
    MODE_FOOTBALL = 3
    MODE_ALARM = 4
    
    def __init__(self, parent=None, mode=MODE_CLOCK):
        super().__init__(parent)
        
        self.current_mode = mode
        self.is_running = False
        self.is_paused = False
        self.elapsed_seconds = 0
        self.timer_duration = 0
        self.format_24h = True
        self.alarm_time = None
        self.alarm_set = False
        self.alarm_message = "¡Alarma activada!"
        self.score_local = 0
        self.score_visitante = 0
        
        # Timer interno
        self.internal_timer = QTimer(self)
        self.internal_timer.timeout.connect(self._on_timer_tick)
        # Control para visibilidad externa del botón start
        self._show_start_button = True

        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz del usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Selector de modo
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo:"))
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItem(translate("Clock"), self.MODE_CLOCK)
        self.mode_combo.addItem(translate("Chronometer"), self.MODE_CHRONOMETER)
        self.mode_combo.addItem(translate("Timer"), self.MODE_TIMER)
        self.mode_combo.addItem(translate("Football"), self.MODE_FOOTBALL)
        self.mode_combo.addItem(translate("Alarm"), self.MODE_ALARM)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        # Configuración de alarma (solo visible en modo alarma)
        self.alarm_widget = QWidget(self)
        alarm_layout = QVBoxLayout(self.alarm_widget)  # Cambiar a VBox para mejor layout
        
        # Primera fila: hora
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora de alarma:"))
        self.alarm_time_edit = QTimeEdit(self.alarm_widget)
        self.alarm_time_edit.setTime(QTime.currentTime().addSecs(3600))  # 1 hora por defecto
        time_layout.addWidget(self.alarm_time_edit)
        alarm_layout.addLayout(time_layout)
        
        # Segunda fila: mensaje
        message_layout = QHBoxLayout()
        message_layout.addWidget(QLabel("Mensaje:"))
        self.alarm_message_edit = QLineEdit(self.alarm_widget)
        self.alarm_message_edit.setText("¡Alarma activada!")
        self.alarm_message_edit.setPlaceholderText("Ingresa el mensaje de la alarma")
        message_layout.addWidget(self.alarm_message_edit)
        alarm_layout.addLayout(message_layout)
        
        # Tercera fila: botón
        self.btn_set_alarm = QPushButton(translate("Set Alarm"), self.alarm_widget)
        self.btn_set_alarm.clicked.connect(self.on_set_alarm)
        alarm_layout.addWidget(self.btn_set_alarm)
        
        layout.addWidget(self.alarm_widget)
        self.alarm_widget.setVisible(False)  # Oculto por defecto
        
        # Configuración de temporizador (solo visible en modo temporizador)
        self.timer_widget = QWidget(self)
        timer_layout = QHBoxLayout(self.timer_widget)
        self.timer_label = QLabel(translate("Duration (min):"))
        timer_layout.addWidget(self.timer_label)
        self.timer_spin = QSpinBox(self.timer_widget)
        self.timer_spin.setRange(1, 120)
        self.timer_spin.setValue(90)
        self.timer_spin.valueChanged.connect(self.on_timer_duration_changed)
        timer_layout.addWidget(self.timer_spin)
        layout.addWidget(self.timer_widget)
        self.timer_widget.setVisible(False)  # Oculto por defecto
        
        # Display LCD (si está disponible) o Label alternativo
        if QLCDNumber:
            self.lcd_display = QLCDNumber(self)
            self.lcd_display.setDigitCount(8)
            self.lcd_display.setSegmentStyle(QLCDNumber.Flat)
            self.lcd_display.setMinimumHeight(80)
            # Estilo rojo
            palette = self.lcd_display.palette()
            palette.setColor(QPalette.WindowText, QColor(220, 20, 60))
            self.lcd_display.setPalette(palette)
            layout.addWidget(self.lcd_display)
            self.label_display = None
        else:
            # Fallback si QLCDNumber no está disponible
            self.label_display = QLabel("00:00:00", self)
            self.label_display.setAlignment(Qt.AlignCenter)
            self.label_display.setStyleSheet("""
                QLabel {
                    font-size: 48pt;
                    font-weight: bold;
                    color: #DC143C;
                    background-color: #000000;
                    padding: 20px;
                    border-radius: 10px;
                }
            """)
            layout.addWidget(self.label_display)
            self.lcd_display = None
        
        # Botones de control
        controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton(" " + translate("Start"), self)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_start.clicked.connect(self.on_start)
        
        self.btn_pause = QPushButton(" " + translate("Pause"), self)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #000;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_pause.clicked.connect(self.on_pause)
        
        self.btn_reset = QPushButton(" " + translate("Reset"), self)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.btn_reset.clicked.connect(self.on_reset)
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_reset)
        layout.addLayout(controls_layout)
        
        # Controles específicos para modo fútbol (ocultos por defecto)
        self.football_controls = QWidget(self)
        football_layout = QHBoxLayout(self.football_controls)
        
        # Marcador actual
        self.score_label = QLabel("0 - 0", self.football_controls)
        self.score_label.setStyleSheet("""
            QLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #DC143C;
                padding: 10px;
            }
        """)
        football_layout.addWidget(QLabel("Marcador:"))
        football_layout.addWidget(self.score_label)
        football_layout.addStretch()
        
        # Botones de goles
        self.btn_goal_local = QPushButton(" " + translate("Goal Local"), self.football_controls)
        self.btn_goal_local.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.btn_goal_local.clicked.connect(lambda: self.on_goal_scored("local"))
        football_layout.addWidget(self.btn_goal_local)
        
        self.btn_goal_visitante = QPushButton(" " + translate("Goal Visitor"), self.football_controls)
        self.btn_goal_visitante.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        self.btn_goal_visitante.clicked.connect(lambda: self.on_goal_scored("visitante"))
        football_layout.addWidget(self.btn_goal_visitante)
        
        layout.addWidget(self.football_controls)
        self.football_controls.setVisible(False)
        
        # Label de estado
        self.lbl_status = QLabel("Listo", self)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 5px;
                color: #495057;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.lbl_status)
        
        # Inicializar display
        self._update_display()
        
        # Inicializar duración del temporizador
        self.on_timer_duration_changed(self.timer_spin.value())
        
        # Inicializar visibilidad de controles según el modo actual
        self.on_mode_changed(self.mode_combo.findData(self.current_mode))
        
    def on_mode_changed(self, index):
        """Maneja el cambio de modo."""
        mode = self.mode_combo.itemData(index)
        self.set_mode(mode)
        
        # Mostrar/ocultar controles específicos
        self.alarm_widget.setVisible(mode == self.MODE_ALARM)
        self.timer_widget.setVisible(mode == self.MODE_TIMER)
        self.football_controls.setVisible(mode == self.MODE_FOOTBALL)
        
        # Actualizar botones según el modo
        if mode == self.MODE_CLOCK or mode == self.MODE_ALARM:
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_reset.setEnabled(False)
        else:
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_reset.setEnabled(True)
        # Actualizar visibilidad del botón start según el modo y override externo
        self._update_start_button_visibility()
        
    def set_mode(self, mode):
        """Establece el modo de funcionamiento."""
        self.current_mode = mode
        self.on_reset()
        
        # Iniciar timer para modos que lo necesitan
        if mode == self.MODE_CLOCK or mode == self.MODE_ALARM:
            self.internal_timer.start(1000)
        else:
            self.internal_timer.stop()
        
        # Actualizar combo box
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == mode:
                self.mode_combo.setCurrentIndex(i)
                break
        
    def on_set_alarm(self):
        """Configura la alarma."""
        self.alarm_time = self.alarm_time_edit.time()
        self.alarm_message = self.alarm_message_edit.text().strip()
        if not self.alarm_message:
            self.alarm_message = "¡Alarma activada!"
        self.alarm_set = True
        self.lbl_status.setText(f"Alarma configurada para {self.alarm_time.toString('hh:mm:ss')} - \"{self.alarm_message}\"")
    
    def on_goal_scored(self, team):
        """Registra un gol para el equipo especificado."""
        if team == "local":
            self.score_local += 1
        elif team == "visitante":
            self.score_visitante += 1
        
        self._update_score_display()
        self.goalScored.emit(team)
        self.lbl_status.setText(f"¡Gol del {team}! Marcador: {self.score_local}-{self.score_visitante}")
    
    def on_timer_duration_changed(self, value):
        """Actualiza la duración del temporizador."""
        self.timer_duration = value * 60  # Convertir minutos a segundos
        if not self.is_running:
            self.elapsed_seconds = self.timer_duration
            self._update_display()
    
    def set_format_24h(self, is_24h):
        """Establece formato de 12 o 24 horas (solo para modo CLOCK)."""
        self.format_24h = is_24h
        if self.current_mode == self.MODE_CLOCK:
            self._update_display()
    
    def on_start(self):
        """Maneja el inicio/reanudación."""
        if self.is_paused:
            # Reanudar
            self.is_paused = False
            self.is_running = True
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.lbl_status.setText(translate("Running"))
            self.internal_timer.start(1000)
        else:
            # Iniciar
            if self.current_mode == self.MODE_TIMER and self.timer_duration == 0:
                self.lbl_status.setText(translate("Configure timer duration"))
                return
                
            self.is_running = True
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.lbl_status.setText(translate("Running"))
            self.internal_timer.start(1000)
    
    def on_pause(self):
        """Maneja la pausa."""
        if self.is_running:
            self.is_paused = True
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.lbl_status.setText(translate("Paused"))
            self.internal_timer.stop()
            
            # Mostrar mensaje de tiempo transcurrido en modo cronómetro
            if self.current_mode == self.MODE_CHRONOMETER:
                hours = self.elapsed_seconds // 3600
                minutes = (self.elapsed_seconds % 3600) // 60
                seconds = self.elapsed_seconds % 60
                tiempo_formateado = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                mensaje = translate("Time elapsed") + f": {tiempo_formateado}"
                QMessageBox.information(self, translate("Chronometer Paused"), mensaje)
    
    def on_reset(self):
        """Reinicia el cronómetro/temporizador."""
        self.is_running = False
        self.is_paused = False
        self.internal_timer.stop()
        
        if self.current_mode == self.MODE_TIMER:
            self.elapsed_seconds = self.timer_duration
        else:
            self.elapsed_seconds = 0
        
        # Resetear marcador en modo fútbol
        if self.current_mode == self.MODE_FOOTBALL:
            self.score_local = 0
            self.score_visitante = 0
            self._update_score_display()
        
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.lbl_status.setText(translate("Ready"))
        self._update_display()
    
    def _on_timer_tick(self):
        """Actualización cada segundo."""
        current_time = QTime.currentTime()
        
        if self.current_mode == self.MODE_CLOCK:
            # Modo reloj: mostrar hora actual
            self._update_display()
            
            # Verificar alarma
            if self.alarm_set and self.alarm_time and current_time >= self.alarm_time:
                self._show_alarm_notification(self.alarm_message)
                self.alarmTriggered.emit(self.alarm_message)
                self.alarm_set = False
                self.lbl_status.setText("¡ALARMA!")
            
        elif self.current_mode == self.MODE_CHRONOMETER or self.current_mode == self.MODE_FOOTBALL:
            # Modo cronómetro: incrementar
            self.elapsed_seconds += 1
            self._update_display()
            
            # En modo fútbol, emitir minutos
            if self.current_mode == self.MODE_FOOTBALL:
                minutes = self.elapsed_seconds // 60
                self.matchTimeUpdated.emit(minutes)
            
        elif self.current_mode == self.MODE_TIMER:
            # Modo temporizador: decrementar
            if self.elapsed_seconds > 0:
                self.elapsed_seconds -= 1
                self._update_display()
                
                if self.elapsed_seconds == 0:
                    # Temporizador terminado
                    self.internal_timer.stop()
                    self.is_running = False
                    self.btn_start.setEnabled(True)
                    self.btn_pause.setEnabled(False)
                    self.lbl_status.setText(translate("Finished"))
                    # Mostrar mensaje de tiempo finalizado
                    hours = self.timer_duration // 3600
                    minutes = (self.timer_duration % 3600) // 60
                    seconds = self.timer_duration % 60
                    tiempo_formateado = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    mensaje = translate("Time finished") + f": {tiempo_formateado}"
                    QMessageBox.information(self, translate("Timer Finished"), mensaje)
                    self.timerFinished.emit()
        
        elif self.current_mode == self.MODE_ALARM:
            # Modo alarma: mostrar hora actual y verificar alarma
            self._update_display()
            
            if self.alarm_set and self.alarm_time and current_time >= self.alarm_time:
                self._show_alarm_notification(self.alarm_message)
                self.alarmTriggered.emit(self.alarm_message)
                self.alarm_set = False
                self.lbl_status.setText("¡ALARMA!")
    
    def _update_display(self):
        """Actualiza el display con el tiempo actual."""
        if self.current_mode == self.MODE_CLOCK or self.current_mode == self.MODE_ALARM:
            # Mostrar hora actual del sistema para reloj y alarma
            current_time = QTime.currentTime()
            if self.format_24h:
                time_text = current_time.toString("HH:mm:ss")
            else:
                time_text = current_time.toString("hh:mm:ss AP")
        else:
            # Mostrar tiempo del cronómetro/temporizador
            hours = self.elapsed_seconds // 3600
            minutes = (self.elapsed_seconds % 3600) // 60
            seconds = self.elapsed_seconds % 60
            time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Actualizar display
        if self.lcd_display:
            self.lcd_display.display(time_text)
        elif self.label_display:
            self.label_display.setText(time_text)
        
        # Emitir señal de actualización
        self.timeUpdated.emit(time_text)
    
    def _show_alarm_notification(self, message):
        """Muestra una notificación de alarma."""
        QMessageBox.information(self, " Alarma", message)
    
    def _update_score_display(self):
        """Actualiza el display del marcador."""
        self.score_label.setText(f"{self.score_local} - {self.score_visitante}")
    
    def set_timer_duration(self, seconds):
        """Establece la duración del temporizador en segundos."""
        self.timer_duration = seconds
        if not self.is_running:
            self.elapsed_seconds = seconds
            self._update_display()
        """Retorna el tiempo transcurrido en segundos."""
        return self.elapsed_seconds
    
    def get_elapsed_minutes(self):
        """Retorna los minutos transcurridos (útil para modo fútbol)."""
        return self.elapsed_seconds // 60

    def set_show_start_button(self, show: bool):
        """Permite mostrar u ocultar el botón de inicio desde código externo.

        Útil cuando el widget se inserta en otra vista que ya proporciona
        su propio control de inicio (por ejemplo, la vista de partidos).
        """
        self._show_start_button = bool(show)
        self._update_start_button_visibility()

    def _update_start_button_visibility(self):
        """Actualiza la visibilidad del botón de inicio en función del modo actual
        y del override externo (`set_show_start_button`). Solo se muestra en
        `MODE_CHRONOMETER` y `MODE_TIMER`.
        """
        try:
            visible_by_mode = self.current_mode in (self.MODE_CHRONOMETER, self.MODE_TIMER)
            self.btn_start.setVisible(self._show_start_button and visible_by_mode)
        except Exception:
            pass
    
    def refresh_ui(self):
        """Actualiza todos los textos del componente según el idioma actual."""
        # Actualizar textos de botones
        self.btn_start.setText(" " + translate("Start"))
        self.btn_pause.setText(" " + translate("Pause"))
        self.btn_reset.setText(" " + translate("Reset"))
        self.btn_set_alarm.setText(translate("Set Alarm"))
        self.btn_goal_local.setText(" " + translate("Goal Local"))
        self.btn_goal_visitante.setText(" " + translate("Goal Visitor"))
        
        # Actualizar etiquetas
        if hasattr(self, 'timer_label'):
            self.timer_label.setText(translate("Duration (min):"))
        
        # Actualizar opciones del combo de modo
        current_mode = self.current_mode
        self.mode_combo.clear()
        self.mode_combo.addItem(translate("Clock"), self.MODE_CLOCK)
        self.mode_combo.addItem(translate("Chronometer"), self.MODE_CHRONOMETER)
        self.mode_combo.addItem(translate("Timer"), self.MODE_TIMER)
        self.mode_combo.addItem(translate("Football"), self.MODE_FOOTBALL)
        self.mode_combo.addItem(translate("Alarm"), self.MODE_ALARM)
        
        # Restaurar el modo seleccionado
        index = self.mode_combo.findData(current_mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)