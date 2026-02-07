"""
Vista de la ventana de gestión de torneos
Carga su interfaz desde un archivo .ui
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from translations import translate
import os


class TournamentWindow(QMainWindow):
    """Ventana principal de gestión de torneos de fútbol"""
    
    def __init__(self):
        super().__init__()
        
        # Cargar la interfaz desde el archivo .ui
        self.load_ui()
        
        # Referencias a widgets
        self.setup_widget_references()
        
        # Placeholder para el reloj digital
        self.clock_widget = None
        
        # Aplicar traducciones iniciales (en español por defecto)
        self.retranslateUi('es')
        
    def load_ui(self):
        """Carga la interfaz desde el archivo .ui"""
        ui_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'ui_files',
            'tournament_window.ui'
        )
        
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_file_path}")
        
        loader = QUiLoader()
        # Cargar sin pasar self como parent para evitar problemas con QMainWindow
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        # Copiar propiedades de la ventana cargada
        if self.ui:
            self.setCentralWidget(self.ui.findChild(QWidget, "centralwidget"))
            menubar = self.ui.findChild(QWidget, "menubar")
            if menubar:
                self.setMenuBar(menubar)
            statusbar = self.ui.findChild(QWidget, "statusbar")
            if statusbar:
                self.setStatusBar(statusbar)
            self.setWindowTitle(self.ui.windowTitle())
            self.resize(self.ui.size())
        
    def setup_widget_references(self):
        """Configura referencias a los widgets del UI"""
        # Primero buscar en self.ui donde se cargó la interfaz
        # Los widgets están allí inicialmente
        if self.ui:
            # Buscar acciones en self.ui (están asociadas al QMainWindow cargado)
            self.actionExit = self.ui.findChild(QAction, "actionExit")
            self.actionEnglish = self.ui.findChild(QAction, "actionEnglish")
            self.actionSpanish = self.ui.findChild(QAction, "actionSpanish")
        
        # Buscar widgets en self porque después de setCentralWidget están aquí
        self.lblTitle = self.findChild(QWidget, "lblTitle")
        self.groupBoxMatch = self.findChild(QWidget, "groupBoxMatch")
        self.txtTeam1 = self.findChild(QWidget, "txtTeam1")
        self.txtTeam2 = self.findChild(QWidget, "txtTeam2")
        self.spinMatchDuration = self.findChild(QWidget, "spinMatchDuration")
        self.btnStartMatch = self.findChild(QWidget, "btnStartMatch")
        self.btnEndMatch = self.findChild(QWidget, "btnEndMatch")
        self.lblMatchStatus = self.findChild(QWidget, "lblMatchStatus")
        self.txtMatchLog = self.findChild(QWidget, "txtMatchLog")
        self.lblNotification = self.findChild(QWidget, "lblNotification")
    
    def add_clock_widget(self, clock_widget):
        """Añade el widget del reloj a la interfaz"""
        self.clock_widget = clock_widget
        
        # Insertar el reloj después del grupo de partido
        central_widget = self.centralWidget()
        layout = central_widget.layout()
        layout.insertWidget(2, clock_widget)  # Después del groupBoxMatch y lblMatchStatus
    
    def set_controller(self, controller):
        """Establece el controlador"""
        self.controller = controller
        
        # Conectar señales
        if self.btnStartMatch:
            self.btnStartMatch.clicked.connect(controller.start_match)
        if self.btnEndMatch:
            self.btnEndMatch.clicked.connect(controller.end_match)
        if self.actionExit:
            self.actionExit.triggered.connect(self.close)
        if self.actionEnglish:
            self.actionEnglish.triggered.connect(lambda: controller.change_language('en'))
        if self.actionSpanish:
            self.actionSpanish.triggered.connect(lambda: controller.change_language('es'))
    
    def get_match_data(self):
        """Obtiene los datos del partido de los controles"""
        return {
            'team1': self.txtTeam1.text(),
            'team2': self.txtTeam2.text(),
            'duration': self.spinMatchDuration.value()
        }
    
    def set_match_controls_enabled(self, start_enabled: bool, end_enabled: bool):
        """Habilita/deshabilita los controles del partido"""
        if self.btnStartMatch:
            self.btnStartMatch.setEnabled(start_enabled)
        if self.btnEndMatch:
            self.btnEndMatch.setEnabled(end_enabled)
        if self.txtTeam1:
            self.txtTeam1.setEnabled(start_enabled)
        if self.txtTeam2:
            self.txtTeam2.setEnabled(start_enabled)
        if self.spinMatchDuration:
            self.spinMatchDuration.setEnabled(start_enabled)
    
    def update_match_status(self, status: str):
        """Actualiza el estado del partido"""
        if self.lblMatchStatus:
            self.lblMatchStatus.setText(status)
    
    def add_log_entry(self, entry: str):
        """Añade una entrada al log del partido"""
        if self.txtMatchLog:
            self.txtMatchLog.append(entry)
    
    def clear_log(self):
        """Limpia el log del partido"""
        if self.txtMatchLog:
            self.txtMatchLog.clear()
    
    def show_message(self, title: str, message: str):
        """Muestra un cuadro de mensaje"""
        QMessageBox.information(self, title, message)
    
    def show_error(self, title: str, message: str):
        """Muestra un cuadro de error"""
        QMessageBox.critical(self, title, message)
    
    def show_notification(self, message: str):
        """Muestra una notificación en la etiqueta"""
        if self.lblNotification:
            self.lblNotification.setText(message)
    
    def retranslateUi(self, language: str = 'es'):
        """Retraduce los textos del UI"""
        self.setWindowTitle(translate('Football Tournament Manager', language))
        
        if self.lblTitle:
            self.lblTitle.setText(translate('Football Tournament Manager', language))
        
        if self.groupBoxMatch:
            self.groupBoxMatch.setTitle(translate('Current Match', language))
        
        if self.btnStartMatch:
            self.btnStartMatch.setText(translate('Start Match', language))
        
        if self.btnEndMatch:
            self.btnEndMatch.setText(translate('End Match', language))
        
        # Retranslate labels
        label_translations = {
            "lblTeam1": "Team 1:",
            "lblTeam2": "Team 2:",
            "lblMatchDuration": "Match Duration (minutes):",
            "lblMatchStatus": "Match Status:",
            "lblNotification": "Notifications will appear here",
        }
        
        for label_name, text in label_translations.items():
            label = self.findChild(QWidget, label_name)
            if label and hasattr(label, 'setText'):
                label.setText(translate(text, language))
        
        # Retranslate placeholder
        if self.txtMatchLog:
            self.txtMatchLog.setPlaceholderText(translate('Match events will be logged here...', language))
        
        # Retranslate menu items
        if self.actionExit:
            self.actionExit.setText(translate('Exit', language))
        if self.actionEnglish:
            self.actionEnglish.setText(translate('English', language))
        if self.actionSpanish:
            self.actionSpanish.setText(translate('Español', language))
        
        # Forzar actualización visual
        self.update()
