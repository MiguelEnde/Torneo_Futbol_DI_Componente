from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QLabel, QComboBox, QMessageBox, QDialog,
                               QFormLayout, QDialogButtonBox, QDateTimeEdit,
                               QTabWidget, QTreeWidget, QTreeWidgetItem,
                               QSpinBox, QGroupBox, QListWidget, QFileDialog)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtSql import QSqlQuery
from CONTROLLERS.partidos_controller import PartidosController
from COMPONENTS.reloj_digital import DigitalClockWidget  # ← NUEVO IMPORT
from RESOURCES.traduciones.translations import translate
from RESOURCES.traduciones.language_selector import LanguageSelector
from RESOURCES.traduciones.language_manager import language_manager
import csv
import os

class PartidosView(QWidget):
    """Vista principal para gestión de partidos."""
    
    def __init__(self):
        super().__init__()
        self.partido_actual_id = None  # ← Para tracking del partido en curso
        # Conectar a cambios de idioma global
        language_manager.language_changed.connect(self.refresh_ui)
        self.init_ui()
        self.cargar_partidos()
    
    def refresh_ui(self):
        """Actualiza los textos de la UI según el idioma actual."""
        # Actualizar título
        if hasattr(self, 'title_label'):
            self.title_label.setText(translate("Match Management"))
        
        # Actualizar botones
        if hasattr(self, 'btn_nuevo'):
            text = translate("New Match")
            self.btn_nuevo.setText("➕ " + text)
        if hasattr(self, 'btn_iniciar'):
            text = translate("Start Match")
            self.btn_iniciar.setText(" " + text)
        if hasattr(self, 'btn_finalizar'):
            text = translate("End Match")
            self.btn_finalizar.setText(" " + text)
        if hasattr(self, 'btn_eliminar'):
            text = translate("Delete")
            self.btn_eliminar.setText("🗑️ " + text)
        if hasattr(self, 'btn_refrescar'):
            text = translate("Refresh")
            self.btn_refrescar.setText("🔄 " + text)
        if hasattr(self, 'btn_exportar'):
            text = translate("Export to CSV")
            self.btn_exportar.setText("📥 " + text)
        
        # Actualizar reloj digital
        if hasattr(self, 'reloj'):
            self.reloj.refresh_ui()
        
        # Actualizar pestaña de calendario
        if hasattr(self, 'combo_filtro_eliminatoria'):
            # Guardar índice actual antes de actualizar
            current_index = self.combo_filtro_eliminatoria.currentIndex()
            self.combo_filtro_eliminatoria.clear()
            self.combo_filtro_eliminatoria.addItems([
                translate("All"), translate("Octavos"), translate("Cuartos"), 
                translate("Semifinal"), translate("Final")
            ])
            # Restaurar el índice después de actualizar
            if current_index >= 0:
                self.combo_filtro_eliminatoria.setCurrentIndex(current_index)
        
        # Actualizar encabezados de tabla
        if hasattr(self, 'tabla_partidos'):
            headers = [
                "ID", translate("Date/Time"), translate("Local Team"), 
                translate("Visiting Team"), translate("Referee"), 
                translate("Eliminatory"), translate("Status")
            ]
            self.tabla_partidos.setHorizontalHeaderLabels(headers)
        
        # Actualizar encabezados de tabla de resultados
        if hasattr(self, 'tabla_resultados'):
            headers = [
                translate("Date"), translate("Local Team"), translate("Result"), 
                translate("Visiting Team"), translate("Eliminatory"), 
                translate("Referee")
            ]
            self.tabla_resultados.setHorizontalHeaderLabels(headers)
        
        # Actualizar pestañas
        if hasattr(self, 'tabs'):
            self.tabs.setTabText(0, "📅 " + translate("Calendar"))
            self.tabs.setTabText(1, "🏆 " + translate("Knockout Bracket"))
            self.tabs.setTabText(2, "📊 " + translate("Results"))
        
        # Recargar datos de partidos (para mostrar datos con textos traducidos)
        if hasattr(self, 'tabla_partidos'):
            self.cargar_partidos()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        self.title_label = QLabel(translate("Match Management"))
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #DC143C;")
        layout.addWidget(self.title_label)
        
        # ============ NUEVO: Reloj Digital ============
        self.reloj = DigitalClockWidget(self, mode=DigitalClockWidget.MODE_FOOTBALL)
        self.reloj.setVisible(True)  # Visible por defecto
        # El widget `DigitalClockWidget` controla la visibilidad del botón
        # `btn_start` según el modo (solo muestra en Cronómetro/Temporizador).
        
        # Conectar señales del reloj
        self.reloj.matchTimeUpdated.connect(self.actualizar_minuto_partido)
        # timerFinished desconectado: el reloj ya muestra su propio mensaje de finalización
        self.reloj.btn_start.clicked.connect(self.iniciar_partido_desde_reloj)
        self.reloj.goalScored.connect(self.registrar_gol_en_partido)
        
        layout.addWidget(self.reloj)
        # ==============================================
        
        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        self.btn_nuevo = QPushButton("➕ " + translate("New Match"))
        self.btn_nuevo.setToolTip(translate("New Match"))
        self.btn_nuevo.clicked.connect(self.nuevo_partido)
        
        self.btn_iniciar = QPushButton(" " + translate("Start Match"))  # ← NUEVO BOTÓN
        self.btn_iniciar.setToolTip(translate("Start Match"))
        self.btn_iniciar.clicked.connect(self.iniciar_partido_cronometro)
        self.btn_iniciar.setEnabled(False)
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.btn_finalizar = QPushButton(" " + translate("End Match"))  # ← NUEVO BOTÓN
        self.btn_finalizar.setToolTip(translate("End Match"))
        self.btn_finalizar.clicked.connect(self.finalizar_partido)
        self.btn_finalizar.setEnabled(False)
        self.btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # Botón de registrar resultado eliminado (se gestiona vía reloj)
        
        self.btn_eliminar = QPushButton("🗑️ " + translate("Delete"))
        self.btn_eliminar.setToolTip(translate("Delete"))
        self.btn_eliminar.clicked.connect(self.eliminar_partido)
        self.btn_eliminar.setEnabled(False)
        
        self.btn_refrescar = QPushButton("🔄 " + translate("Refresh"))
        self.btn_refrescar.setToolTip(translate("Refresh"))
        self.btn_refrescar.clicked.connect(self.cargar_partidos)
        
        self.btn_exportar = QPushButton("📥 " + translate("Export to CSV"))
        self.btn_exportar.setToolTip(translate("Export to CSV"))
        self.btn_exportar.clicked.connect(self.exportar_resultados)
        
        # Selector de idioma
        self.language_selector = LanguageSelector()
        
        toolbar_layout.addWidget(self.btn_nuevo)
        toolbar_layout.addWidget(self.btn_iniciar)  # ← NUEVO
        toolbar_layout.addWidget(self.btn_finalizar)  # ← NUEVO
        toolbar_layout.addWidget(self.btn_eliminar)
        toolbar_layout.addWidget(self.btn_refrescar)
        toolbar_layout.addWidget(self.btn_exportar)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.language_selector)
        
        layout.addLayout(toolbar_layout)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de calendario
        tab_calendario = self.crear_tab_calendario()
        self.tabs.addTab(tab_calendario, "📅 " + translate("Calendar"))
        
        # Pestaña de eliminatorias
        tab_eliminatorias = self.crear_tab_eliminatorias()
        self.tabs.addTab(tab_eliminatorias, "🏆 " + translate("Knockout Bracket"))
        
        # Pestaña de resultados
        tab_resultados = self.crear_tab_resultados()
        self.tabs.addTab(tab_resultados, "📊 " + translate("Results"))
        
        layout.addWidget(self.tabs)
        
    def crear_tab_calendario(self):
        """Crea la pestaña de calendario."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Filtro por eliminatoria
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Filtrar por:"))
        
        self.combo_filtro_eliminatoria = QComboBox()
        self.combo_filtro_eliminatoria.addItems([
            "Todas", "Octavos", "Cuartos", "Semifinal", "Final"
        ])
        self.combo_filtro_eliminatoria.currentTextChanged.connect(self.cargar_partidos)
        filtro_layout.addWidget(self.combo_filtro_eliminatoria)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)
        
        # Tabla de partidos
        self.tabla_partidos = QTableWidget()
        self.tabla_partidos.setColumnCount(7)
        self.tabla_partidos.setHorizontalHeaderLabels([
            "ID", "Fecha/Hora", "Equipo Local", "Equipo Visitante", 
            "Árbitro", "Eliminatoria", "Estado"
        ])
        self.tabla_partidos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_partidos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_partidos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_partidos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_partidos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_partidos.hideColumn(0)
        self.tabla_partidos.itemSelectionChanged.connect(self.partido_seleccionado)
        layout.addWidget(self.tabla_partidos)
        
        return widget
        
    def crear_tab_eliminatorias(self):
        """Crea la pestaña del cuadro de eliminatorias."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        info_label = QLabel("🏆 Cuadro de Eliminatorias del Torneo")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-bottom: 10px; color: #DC143C;")
        layout.addWidget(info_label)
        
        # Árbol de eliminatorias
        self.tree_eliminatorias = QTreeWidget()
        self.tree_eliminatorias.setHeaderLabels(["Eliminatoria", "Enfrentamientos"])
        self.tree_eliminatorias.setColumnWidth(0, 200)
        layout.addWidget(self.tree_eliminatorias)
        
        return widget
        
    def crear_tab_resultados(self):
        """Crea la pestaña de resultados."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        info_label = QLabel("📊 Partidos Finalizados")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-bottom: 10px; color: #DC143C;")
        layout.addWidget(info_label)
        
        # Tabla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(6)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Fecha", "Equipo Local", "Resultado", "Equipo Visitante", 
            "Eliminatoria", "Árbitro"
        ])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_resultados.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_resultados)
        
        return widget
        
    # ============ NUEVAS FUNCIONES DEL RELOJ ============
    def iniciar_partido_cronometro(self):
        """Inicia el cronómetro del partido seleccionado."""
        selected_row = self.tabla_partidos.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un partido primero")
            return
        
        # Obtener datos del partido
        partido_id = int(self.tabla_partidos.item(selected_row, 0).text())
        local = self.tabla_partidos.item(selected_row, 2).text()
        visitante = self.tabla_partidos.item(selected_row, 3).text()
        
        # Confirmar inicio
        reply = QMessageBox.question(
            self,
            "Iniciar Partido",
            f"¿Iniciar cronómetro para el partido?\n\n{local} vs {visitante}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.partido_actual_id = partido_id

            # Verificar que el partido no esté finalizado antes de iniciar
            partido = PartidosController.obtener_partido(partido_id)
            if partido and getattr(partido, 'finalizado', 0):
                QMessageBox.information(self, "Partido Finalizado", "Partido ya finalizado")
                return
            
            # Para modo fútbol, no necesitamos configurar duración de timer
            # El cronómetro cuenta hacia arriba desde 0
            duracion_minutos = 90
            # self.reloj.set_timer_duration(duracion_minutos * 60)
            
            # Cambiar reloj al modo Fútbol
            self.reloj.set_mode(DigitalClockWidget.MODE_FOOTBALL)
            
            # Mostrar y resetear reloj
            self.reloj.setVisible(True)
            self.reloj.on_reset()
            self.reloj.on_start()
            
            # Deshabilitar botón de iniciar y habilitar finalizar
            self.btn_iniciar.setEnabled(False)
            self.btn_finalizar.setEnabled(True)
            
            QMessageBox.information(
                self,
                "Partido Iniciado",
                f"Cronómetro iniciado para:\n{local} vs {visitante}\n\nDuración: {duracion_minutos} minutos"
            )
    
    def iniciar_partido_desde_reloj(self):
        """Inicia el partido cuando se hace clic en el botón iniciar del reloj."""
        # Si hay un partido seleccionado, iniciar ese partido
        selected_row = self.tabla_partidos.currentRow()
        if selected_row >= 0 and self.partido_actual_id is None:
            self.iniciar_partido_cronometro()
    
    def finalizar_partido(self):
        """Finaliza el partido en curso y registra el resultado."""
        if self.partido_actual_id is None:
            QMessageBox.warning(self, "Error", "No hay partido en curso")
            return
        
        # Confirmar finalización
        reply = QMessageBox.question(
            self,
            "Finalizar Partido",
            "¿Está seguro de finalizar el partido?\n\nSe detendrá el cronómetro y se registrará el resultado final.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Calcular los goles actuales desde la tabla de goles
            query = QSqlQuery()
            query.prepare("""
                SELECT 
                    COUNT(CASE WHEN ep.equipo_id = p.equipo_local_id THEN 1 END) as goles_local,
                    COUNT(CASE WHEN ep.equipo_id = p.equipo_visitante_id THEN 1 END) as goles_visitante
                FROM partidos p
                LEFT JOIN goles g ON g.partido_id = p.id AND g.partido_id IS NOT NULL
                LEFT JOIN participantes par ON par.id = g.participante_id
                LEFT JOIN equipo_participante ep ON ep.participante_id = par.id
                WHERE p.id = ?
            """)
            query.addBindValue(self.partido_actual_id)
            
            goles_local = 0
            goles_visitante = 0
            
            if query.exec() and query.next():
                goles_local = query.value(0) or 0
                goles_visitante = query.value(1) or 0
            
            # Finalizar el partido usando el controlador
            from CONTROLLERS.partidos_controller import PartidosController
            if PartidosController.finalizar_partido(self.partido_actual_id, goles_local, goles_visitante):
                # Detener el reloj
                self.reloj.on_pause()
                
                # Limpiar estado del partido
                partido_actual_id = self.partido_actual_id
                self.partido_actual_id = None
                
                # Actualizar botones
                self.btn_iniciar.setEnabled(True)
                self.btn_finalizar.setEnabled(False)
                
                # Ocultar reloj
                self.reloj.setVisible(False)
                self.reloj.on_reset()
                
                # Recargar la tabla para mostrar el estado actualizado
                self.cargar_partidos()
                
                # Mostrar mensaje
                QMessageBox.information(
                    self,
                    "Partido Finalizado",
                    f"El partido ha sido finalizado.\n\nResultado final: {goles_local}-{goles_visitante}"
                )
            else:
                QMessageBox.warning(self, "Error", "No se pudo finalizar el partido")
    
    def registrar_gol_en_partido(self, equipo):
        """Registra un gol en el partido actual."""
        if self.partido_actual_id is None:
            QMessageBox.warning(self, "Error", "No hay partido en curso")
            return
        
        # Obtener el minuto actual del partido
        minuto_actual = self.reloj.get_elapsed_minutes()
        
        # Mostrar diálogo para seleccionar goleador
        dialog = GoleadorDialog(self, self.partido_actual_id, equipo, minuto_actual)
        if dialog.exec() == QDialog.Accepted:
            participante_id = dialog.get_participante_id()
            if participante_id:
                # Registrar el gol usando el controlador
                if PartidosController.registrar_gol(self.partido_actual_id, participante_id, minuto_actual):
                    QMessageBox.information(self, "Gol Registrado", 
                                          f"Gol registrado para el participante seleccionado al minuto {minuto_actual}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo registrar el gol")
            else:
                QMessageBox.warning(self, "Selección requerida", 
                                  "Por favor, seleccione un participante de la lista para registrar el gol.")
    
    def actualizar_minuto_partido(self, minuto):
        """Se ejecuta cada minuto del partido."""
        # Notificaciones cada 15 minutos
        if minuto > 0 and minuto % 15 == 0:
            QMessageBox.information(
                self,
                f"Minuto {minuto}",
                f"Han transcurrido {minuto} minutos de partido"
            )
        
        # Medio tiempo a los 45 minutos
        if minuto == 45:
            QMessageBox.information(
                self,
                "¡Medio Tiempo!",
                "Primer tiempo completado. ¡Descanso!"
            )
    

    def cargar_partidos(self):
        """Carga los partidos desde la base de datos."""
        self.tabla_partidos.setRowCount(0)
        
        filtro = self.combo_filtro_eliminatoria.currentText()
        # Comparar con el valor traducido
        all_text = translate("All")
        
        query = QSqlQuery()
        sql = """
            SELECT p.id, p.fecha_hora, 
                   el.nombre as local, ev.nombre as visitante,
                   COALESCE(a.nombre, 'Sin asignar') as arbitro,
                   p.eliminatoria, p.finalizado,
                   p.goles_local, p.goles_visitante
            FROM partidos p
            INNER JOIN equipos el ON p.equipo_local_id = el.id
            INNER JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes a ON p.arbitro_id = a.id
            WHERE 1=1
        """
        
        if filtro != all_text:
            sql += f" AND p.eliminatoria = '{filtro}'"
            
        sql += " ORDER BY p.fecha_hora ASC"
        
        query.exec(sql)
        
        row = 0
        while query.next():
            self.tabla_partidos.insertRow(row)
            
            # ID
            self.tabla_partidos.setItem(row, 0, QTableWidgetItem(str(query.value(0))))
            
            # Fecha/Hora
            fecha_hora = QDateTime.fromString(query.value(1), "yyyy-MM-dd HH:mm")
            fecha_texto = fecha_hora.toString("dd/MM/yyyy HH:mm")
            self.tabla_partidos.setItem(row, 1, QTableWidgetItem(fecha_texto))
            
            # Equipos
            self.tabla_partidos.setItem(row, 2, QTableWidgetItem(query.value(2)))
            self.tabla_partidos.setItem(row, 3, QTableWidgetItem(query.value(3)))
            
            # Árbitro
            self.tabla_partidos.setItem(row, 4, QTableWidgetItem(query.value(4)))
            
            # Eliminatoria
            self.tabla_partidos.setItem(row, 5, QTableWidgetItem(query.value(5)))
            
            # Estado
            finalizado = query.value(6)
            if finalizado:
                goles_local = query.value(7)
                goles_visitante = query.value(8)
                estado_texto = f"✅ Finalizado ({goles_local}-{goles_visitante})"
            else:
                estado_texto = "⏳ Pendiente"
            self.tabla_partidos.setItem(row, 6, QTableWidgetItem(estado_texto))
            
            row += 1
            
        self.cargar_eliminatorias()
        self.cargar_resultados()
        
    def cargar_eliminatorias(self):
        """Carga el árbol de eliminatorias."""
        self.tree_eliminatorias.clear()
        
        eliminatorias = ["Octavos", "Cuartos", "Semifinal", "Final"]
        
        for eliminatoria in eliminatorias:
            item_elim = QTreeWidgetItem(self.tree_eliminatorias, [eliminatoria])
            item_elim.setExpanded(True)
            
            # Icono según eliminatoria
            if eliminatoria == "Final":
                item_elim.setText(0, "🏆 " + eliminatoria)
            elif eliminatoria == "Semifinal":
                item_elim.setText(0, "🥈 " + eliminatoria)
            else:
                item_elim.setText(0, "⚽ " + eliminatoria)
            
            # Cargar partidos de esta eliminatoria
            query = QSqlQuery()
            query.prepare("""
                SELECT el.nombre, ev.nombre, p.goles_local, p.goles_visitante, p.finalizado
                FROM partidos p
                INNER JOIN equipos el ON p.equipo_local_id = el.id
                INNER JOIN equipos ev ON p.equipo_visitante_id = ev.id
                WHERE p.eliminatoria = ?
                ORDER BY p.fecha_hora
            """)
            query.addBindValue(eliminatoria)
            query.exec()
            
            contador = 0
            while query.next():
                contador += 1
                local = query.value(0)
                visitante = query.value(1)
                goles_l = query.value(2)
                goles_v = query.value(3)
                finalizado = query.value(4)
                
                if finalizado:
                    ganador = local if goles_l > goles_v else visitante
                    partido_texto = f"{local} {goles_l} - {goles_v} {visitante} (Gana: {ganador})"
                else:
                    partido_texto = f"{local} vs {visitante}"
                    
                QTreeWidgetItem(item_elim, [partido_texto])
            
            if contador == 0:
                QTreeWidgetItem(item_elim, ["No hay partidos programados"])
                
    def cargar_resultados(self):
        """Carga la tabla de resultados."""
        self.tabla_resultados.setRowCount(0)
        
        query = QSqlQuery()
        query.exec("""
            SELECT p.fecha_hora, el.nombre, p.goles_local, p.goles_visitante,
                   ev.nombre, p.eliminatoria, COALESCE(a.nombre, 'Sin asignar')
            FROM partidos p
            INNER JOIN equipos el ON p.equipo_local_id = el.id
            INNER JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes a ON p.arbitro_id = a.id
            WHERE p.finalizado = 1
            ORDER BY p.fecha_hora DESC
        """)
        
        row = 0
        while query.next():
            self.tabla_resultados.insertRow(row)
            
            # Fecha
            fecha_hora = QDateTime.fromString(query.value(0), "yyyy-MM-dd HH:mm")
            fecha_texto = fecha_hora.toString("dd/MM/yyyy")
            self.tabla_resultados.setItem(row, 0, QTableWidgetItem(fecha_texto))
            
            # Local
            self.tabla_resultados.setItem(row, 1, QTableWidgetItem(query.value(1)))
            
            # Resultado
            resultado = f"{query.value(2)} - {query.value(3)}"
            self.tabla_resultados.setItem(row, 2, QTableWidgetItem(resultado))
            
            # Visitante
            self.tabla_resultados.setItem(row, 3, QTableWidgetItem(query.value(4)))
            
            # Eliminatoria
            self.tabla_resultados.setItem(row, 4, QTableWidgetItem(query.value(5)))
            
            # Árbitro
            self.tabla_resultados.setItem(row, 5, QTableWidgetItem(query.value(6)))
            
            row += 1
            
    def partido_seleccionado(self):
        """Maneja la selección de un partido."""
        has_selection = self.tabla_partidos.currentRow() >= 0
        self.btn_eliminar.setEnabled(has_selection)
        self.btn_iniciar.setEnabled(has_selection and self.partido_actual_id is None)  # Solo si no hay partido en curso
        self.btn_finalizar.setEnabled(self.partido_actual_id is not None)  # Solo si hay partido en curso
        
    def nuevo_partido(self):
        """Abre el diálogo para crear un nuevo partido."""
        dialog = PartidoDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_partidos()
            QMessageBox.information(self, "Éxito", "Partido creado correctamente")
            
    def registrar_resultado(self):
        """Abre el diálogo para registrar el resultado del partido."""
        selected_row = self.tabla_partidos.currentRow()
        if selected_row < 0:
            return
            
        partido_id = int(self.tabla_partidos.item(selected_row, 0).text())
        
        dialog = ResultadoDialog(self, partido_id)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_partidos()
            QMessageBox.information(self, "Éxito", "Resultado registrado correctamente")
            
            # Ocultar reloj si estaba visible
            self.reloj.setVisible(False)
            self.reloj.on_reset()
            
    def eliminar_partido(self):
        """Elimina el partido seleccionado."""
        selected_row = self.tabla_partidos.currentRow()
        if selected_row < 0:
            return
            
        partido_id = self.tabla_partidos.item(selected_row, 0).text()
        local = self.tabla_partidos.item(selected_row, 2).text()
        visitante = self.tabla_partidos.item(selected_row, 3).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el partido '{local} vs {visitante}'?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM partidos WHERE id = ?")
            query.addBindValue(partido_id)
            
            if query.exec():
                self.cargar_partidos()
                QMessageBox.information(self, "Éxito", "Partido eliminado correctamente")
            else:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar: {query.lastError().text()}")

    def exportar_resultados(self):
        """Exporta los resultados de los partidos a un archivo CSV."""
        # Diálogo para seleccionar ubicación
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar resultados como...",
            os.path.expanduser("~\\Desktop\\resultados.csv"),
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            query = QSqlQuery()
            query.exec("""
                SELECT 
                    p.id,
                    e1.nombre as equipo_local,
                    e2.nombre as equipo_visitante,
                    p.goles_local,
                    p.goles_visitante,
                    p.eliminatoria,
                    p.fecha_hora,
                    CASE WHEN p.finalizado = 1 THEN 'Finalizado' ELSE 'Pendiente' END as estado
                FROM partidos p
                INNER JOIN equipos e1 ON p.equipo_local_id = e1.id
                INNER JOIN equipos e2 ON p.equipo_visitante_id = e2.id
                ORDER BY p.fecha_hora DESC
            """)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "ID", "Equipo Local", "Equipo Visitante", 
                    "Goles Local", "Goles Visitante", "Eliminatoria", 
                    "Fecha/Hora", "Estado"
                ])
                
                while query.next():
                    writer.writerow([
                        query.value(0),
                        query.value(1),
                        query.value(2),
                        query.value(3),
                        query.value(4),
                        query.value(5),
                        query.value(6),
                        query.value(7)
                    ])
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Resultados exportados correctamente a:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo exportar los resultados:\n{str(e)}"
            )


# Los diálogos se mantienen igual
class PartidoDialog(QDialog):
    """Diálogo para crear partidos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Partido")
        self.setMinimumWidth(500)
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QFormLayout(self)
        
        # Equipo local
        self.combo_local = QComboBox()
        self.cargar_equipos(self.combo_local)
        layout.addRow("Equipo Local:", self.combo_local)
        
        # Equipo visitante
        self.combo_visitante = QComboBox()
        self.cargar_equipos(self.combo_visitante)
        layout.addRow("Equipo Visitante:", self.combo_visitante)
        
        # Árbitro
        self.combo_arbitro = QComboBox()
        self.cargar_arbitros()
        layout.addRow("Árbitro:", self.combo_arbitro)
        
        # Fecha y hora
        self.datetime_partido = QDateTimeEdit()
        self.datetime_partido.setCalendarPopup(True)
        self.datetime_partido.setDateTime(QDateTime.currentDateTime())
        self.datetime_partido.setDisplayFormat("dd/MM/yyyy HH:mm")
        layout.addRow("Fecha y Hora:", self.datetime_partido)
        
        # Eliminatoria
        self.combo_eliminatoria = QComboBox()
        self.combo_eliminatoria.addItems(["Octavos", "Cuartos", "Semifinal", "Final"])
        layout.addRow("Eliminatoria:", self.combo_eliminatoria)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.aceptar)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def cargar_equipos(self, combo):
        """Carga los equipos en el combo box."""
        query = QSqlQuery()
        query.exec("SELECT id, nombre FROM equipos ORDER BY nombre")
        
        while query.next():
            combo.addItem(query.value(1), query.value(0))
            
    def cargar_arbitros(self):
        """Carga los árbitros en el combo box."""
        self.combo_arbitro.addItem("Sin asignar", None)
        
        query = QSqlQuery()
        query.exec("""
            SELECT id, nombre FROM participantes 
            WHERE es_arbitro = 1 AND activo = 1 
            ORDER BY nombre
        """)
        
        while query.next():
            self.combo_arbitro.addItem(query.value(1), query.value(0))
            
    def aceptar(self):
        """Valida y guarda los datos."""
        local_id = self.combo_local.currentData()
        visitante_id = self.combo_visitante.currentData()
        
        if local_id == visitante_id:
            QMessageBox.warning(self, "Error", "Debe seleccionar equipos diferentes")
            return
            
        arbitro_id = self.combo_arbitro.currentData()
        fecha_hora = self.datetime_partido.dateTime().toString("yyyy-MM-dd HH:mm")
        eliminatoria = self.combo_eliminatoria.currentText()
        
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO partidos (equipo_local_id, equipo_visitante_id, arbitro_id, fecha_hora, eliminatoria)
            VALUES (?, ?, ?, ?, ?)
        """)
        query.addBindValue(local_id)
        query.addBindValue(visitante_id)
        query.addBindValue(arbitro_id)
        query.addBindValue(fecha_hora)
        query.addBindValue(eliminatoria)
        
        if query.exec():
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"No se pudo guardar: {query.lastError().text()}")


class GoleadorDialog(QDialog):
    """Diálogo para seleccionar el goleador de un gol."""
    
    def __init__(self, parent=None, partido_id=None, equipo=None, minuto=None):
        super().__init__(parent)
        self.partido_id = partido_id
        self.equipo = equipo
        self.minuto = minuto
        self.setWindowTitle(f"Seleccionar Goleador - Gol {equipo.title()}")
        self.setModal(True)
        self.init_ui()
        self.cargar_participantes()
        
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Info del gol
        info_label = QLabel(f"Gol del equipo {self.equipo.title()} al minuto {self.minuto}")
        info_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # Lista de participantes
        layout.addWidget(QLabel("Seleccione el goleador:"))
        self.participantes_list = QListWidget(self)
        self.participantes_list.setMinimumHeight(150)
        layout.addWidget(self.participantes_list)
        
        # Botones
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
    def validate_and_accept(self):
        """Valida la selección antes de aceptar."""
        if self.get_participante_id() is None:
            QMessageBox.warning(self, "Selección requerida", 
                              "Por favor, seleccione un participante de la lista para registrar el gol.")
            return
        self.accept()
        
    def cargar_participantes(self):
        """Carga los participantes del equipo correspondiente."""
        query = QSqlQuery()
        
        # Determinar si es local o visitante
        equipo_col = "p.equipo_local_id" if self.equipo == "local" else "p.equipo_visitante_id"
        
        query.prepare(f"""
            SELECT par.id, par.nombre
            FROM participantes par
            JOIN equipo_participante ep ON ep.participante_id = par.id
            JOIN partidos p ON p.id = ?
            WHERE ep.equipo_id = ({equipo_col})
            ORDER BY par.nombre
        """)
        query.addBindValue(self.partido_id)
        
        if query.exec():
            count = 0
            while query.next():
                participante_id = query.value(0)
                nombre = query.value(1)
                nombre_completo = nombre
                
                from PySide6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(nombre_completo)
                item.setData(Qt.UserRole, participante_id)
                self.participantes_list.addItem(item)
                count += 1
            
            if count == 0:
                # No hay participantes
                item = QListWidgetItem("No hay participantes registrados en este equipo")
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # No seleccionable
                self.participantes_list.addItem(item)
            elif count == 1:
                # Solo un participante, seleccionarlo automáticamente
                self.participantes_list.setCurrentRow(0)
    
    def get_participante_id(self):
        """Retorna el ID del participante seleccionado."""
        current_item = self.participantes_list.currentItem()
        if current_item and current_item.flags() & Qt.ItemIsSelectable:
            return current_item.data(Qt.UserRole)
        return None


def actualizar_minuto_partido(self, minuto):
    """Se ejecuta cada minuto del partido."""
    # Notificaciones cada 15 minutos
    if minuto > 0 and minuto % 15 == 0:
        QMessageBox.information(
            self,
            "Tiempo del Partido",
            f"Minuto {minuto} del partido"
        )


class ResultadoDialog(QDialog):
    """Diálogo para registrar resultados de partidos."""
    
    def __init__(self, parent=None, partido_id=None):
        super().__init__(parent)
        self.partido_id = partido_id
        self.setWindowTitle("Registrar Resultado")
        self.setMinimumWidth(400)
        self.init_ui()
        self.cargar_datos_partido()
        
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Info del partido
        self.label_info = QLabel()
        self.label_info.setStyleSheet("font-weight: bold; font-size: 11pt; padding: 10px;")
        layout.addWidget(self.label_info)
        
        # Formulario de goles
        form_layout = QFormLayout()
        
        self.spin_goles_local = QSpinBox()
        self.spin_goles_local.setMinimum(0)
        self.spin_goles_local.setMaximum(20)
        form_layout.addRow("Goles Local:", self.spin_goles_local)
        
        self.spin_goles_visitante = QSpinBox()
        self.spin_goles_visitante.setMinimum(0)
        self.spin_goles_visitante.setMaximum(20)
        form_layout.addRow("Goles Visitante:", self.spin_goles_visitante)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.aceptar_resultado)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def cargar_datos_partido(self):
        """Carga los datos del partido y calcula los goles actuales."""
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                p.id,
                el.nombre as local,
                ev.nombre as visitante,
                p.goles_local,
                p.goles_visitante,
                p.finalizado
            FROM partidos p
            JOIN equipos el ON p.equipo_local_id = el.id
            JOIN equipos ev ON p.equipo_visitante_id = ev.id
            WHERE p.id = ?
        """)
        query.addBindValue(self.partido_id)
        
        if query.exec() and query.next():
            local = query.value(1)
            visitante = query.value(2)
            goles_local = query.value(3) or 0
            goles_visitante = query.value(4) or 0
            finalizado = query.value(5) or 0
            
            self.label_info.setText(f"{local} vs {visitante}")
            
            # Si ya está finalizado, mostrar los goles guardados
            if finalizado:
                self.spin_goles_local.setValue(goles_local)
                self.spin_goles_visitante.setValue(goles_visitante)
            else:
                # Calcular goles desde la tabla de goles
                query_goles = QSqlQuery()
                query_goles.prepare("""
                    SELECT 
                        COUNT(CASE WHEN ep.equipo_id = p.equipo_local_id THEN 1 END) as goles_local,
                        COUNT(CASE WHEN ep.equipo_id = p.equipo_visitante_id THEN 1 END) as goles_visitante
                    FROM partidos p
                    LEFT JOIN goles g ON g.partido_id = p.id AND g.partido_id IS NOT NULL
                    LEFT JOIN participantes par ON par.id = g.participante_id
                    LEFT JOIN equipo_participante ep ON ep.participante_id = par.id
                    WHERE p.id = ?
                """)
                query_goles.addBindValue(self.partido_id)
                
                if query_goles.exec() and query_goles.next():
                    self.spin_goles_local.setValue(query_goles.value(0))
                    self.spin_goles_visitante.setValue(query_goles.value(1))
    
    def aceptar_resultado(self):
        """Guarda el resultado y finaliza el partido."""
        from CONTROLLERS.partidos_controller import PartidosController
        
        goles_local = self.spin_goles_local.value()
        goles_visitante = self.spin_goles_visitante.value()
        
        if PartidosController.finalizar_partido(self.partido_id, goles_local, goles_visitante):
            QMessageBox.information(self, "Éxito", "Resultado registrado y partido finalizado correctamente")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo registrar el resultado")