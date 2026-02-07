"""
Controlador principal de la aplicación
Gestiona la interacción entre la vista principal, el reloj digital y la aplicación
"""
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QTime
from VIEWS.main_window import MainWindow
from COMPONENTS.reloj_digital import DigitalClockWidget


class MainWindowController:
    """
    Controlador principal que coordina la ventana principal y el reloj digital
    """
    
    def __init__(self, main_window: MainWindow, clock_widget, app: QApplication):
        self.main_window = main_window
        self.clock_widget = clock_widget
        self.app = app
        
        # Configurar el reloj en modo reloj por defecto
        self.mode = 'clock'  # 'clock', 'timer', 'stopwatch'
        self.timer_value = 0
        self.is_running = False
        
        if self.clock_widget:
            # Conectar el widget del reloj al controlador
            self.clock_widget.set_controller(self)
            # Iniciar el reloj
            self.start_clock()
    
    def set_clock_widget(self, clock_widget):
        """Asigna el widget del reloj después de la creación"""
        self.clock_widget = clock_widget
        self.clock_widget.set_controller(self)
        self.start_clock()
    
    def start_clock(self):
        """Inicia el modo reloj"""
        self.mode = 'clock'
        self.clock_widget.start_internal_timer()
        self.clock_widget.update_status("Reloj activo")
        self.clock_widget.set_controls_enabled(False, False, False)
    
    def on_timer_tick(self):
        """Manejador del tick del timer interno"""
        if self.mode == 'clock':
            current_time = QTime.currentTime()
            time_str = current_time.toString("hh:mm:ss")
            self.clock_widget.update_display(time_str)
            self.clock_widget.emit_time_updated(time_str)
        elif self.mode == 'stopwatch':
            if self.is_running:
                self.timer_value += 1
                hours = self.timer_value // 3600
                minutes = (self.timer_value % 3600) // 60
                seconds = self.timer_value % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.clock_widget.update_display(time_str)
        elif self.mode == 'timer' or self.mode == 'football':
            if self.is_running and self.timer_value > 0:
                self.timer_value -= 1
                hours = self.timer_value // 3600
                minutes = (self.timer_value % 3600) // 60
                seconds = self.timer_value % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.clock_widget.update_display(time_str)
                if self.timer_value == 0:
                    self.on_timer_finished()
    
    def on_start(self):
        """Manejador del botón Start"""
        if self.mode == 'stopwatch':
            self.is_running = True
            self.clock_widget.update_status("Cronómetro en marcha")
            self.clock_widget.set_controls_enabled(False, True, True)
        elif self.mode == 'timer' or self.mode == 'football':
            if self.timer_value > 0:
                self.is_running = True
                status = "Temporizador activo" if self.mode == 'timer' else "Partido en curso"
                self.clock_widget.update_status(status)
                self.clock_widget.set_controls_enabled(False, True, True)
    
    def on_pause(self):
        """Manejador del botón Pause"""
        if self.is_running:
            self.is_running = False
            self.clock_widget.update_status("Pausado")
            self.clock_widget.set_controls_enabled(True, False, True)
    
    def on_reset(self):
        """Manejador del botón Reset"""
        self.is_running = False
        self.timer_value = 0
        self.clock_widget.update_display("00:00:00")
        self.clock_widget.update_status("Listo")
        self.clock_widget.set_controls_enabled(True, False, True)
    
    def on_timer_finished(self):
        """Manejador cuando el temporizador llega a cero"""
        self.is_running = False
        self.clock_widget.update_status("¡Temporizador finalizado!")
        self.clock_widget.emit_timer_finished()
        self.clock_widget.set_controls_enabled(True, False, True)
    
    def set_mode(self, mode: str):
        """Cambia el modo del reloj"""
        self.mode = mode
        self.on_reset()
        if mode == 'clock':
            self.start_clock()
        elif mode == 'football':
            # Modo fútbol: temporizador con 90 minutos
            self.set_timer_value(90)
            self.clock_widget.update_status("Modo Fútbol - 90 minutos")
        else:
            self.clock_widget.stop_internal_timer()
            self.clock_widget.update_status(f"Modo {mode}")
    
    def set_timer_value(self, minutes: int):
        """Establece el valor del temporizador en minutos"""
        self.timer_value = minutes * 60
        hours = self.timer_value // 3600
        mins = (self.timer_value % 3600) // 60
        secs = self.timer_value % 60
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        self.clock_widget.update_display(time_str)