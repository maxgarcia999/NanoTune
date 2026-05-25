import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog, QSlider)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class NanoTune(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoTune")
        self.setGeometry(100, 100, 420, 580)
        
        self.player = QMediaPlayer()
        self.player.positionChanged.connect(self.actualizar_posicion_barra)
        self.player.durationChanged.connect(self.actualizar_duracion_barra)
        self.player.stateChanged.connect(self.detectar_fin_cancion)
        
        self.usuario_arrastrando = False
        self.lista_canciones = []
        self.indice_actual = -1
        
        self.init_ui()
        self.escanear_carpeta_descargas()

    def init_ui(self):
        self.widget_central = QWidget()
        self.widget_central.setObjectName("VentanaPrincipal")
        self.setCentralWidget(self.widget_central)
        
        layout_principal = QVBoxLayout(self.widget_central)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(16)

        self.setStyleSheet("""
            QWidget#VentanaPrincipal {
                background-color: #121620;
            }
            QLabel {
                color: #e1e5f2;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QListWidget {
                background-color: rgba(255, 255, 255, 0.03);
                border: none;
                border-radius: 12px;
                color: #cbd5e1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background-color: rgba(38, 151, 245, 0.12);
                color: #3b82f6;
                font-weight: 600;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin-top: -4px;
                border-radius: 6px;
            }
        """)

        layout_superior = QHBoxLayout()
        self.lbl_titulo = QLabel("NanoTune")
        self.lbl_titulo.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
        
        self.btn_fondo = QPushButton("+")
        self.btn_fondo.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
                border: none;
                min-width: 28px; max-width: 28px; min-height: 28px; max-height: 28px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.08); color: #ffffff; }
        """)
        self.btn_fondo.setToolTip("Personalizar imagen de fondo")
        self.btn_fondo.clicked.connect(self.cambiar_imagen_fondo)
        
        layout_superior.addWidget(self.lbl_titulo)
        layout_superior.addStretch()
        layout_superior.addWidget(self.btn_fondo)
        layout_principal.addLayout(layout_superior)

        self.lbl_estado = QLabel("Buscando pistas...")
        self.lbl_estado.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout_principal.addWidget(self.lbl_estado)

        self.lista_widget = QListWidget()
        self.lista_widget.setFocusPolicy(Qt.NoFocus)
        self.lista_widget.itemDoubleClicked.connect(self.reproducir_seleccionada)
        layout_principal.addWidget(self.lista_widget)

        layout_progreso = QHBoxLayout()
        self.lbl_tiempo_actual = QLabel("00:00")
        self.lbl_tiempo_actual.setStyleSheet("color: #64748b; font-size: 11px;")
        
        self.slider_progreso = QSlider(Qt.Horizontal)
        self.slider_progreso.setRange(0, 0)
        self.slider_progreso.setFocusPolicy(Qt.NoFocus)
        self.slider_progreso.setCursor(Qt.PointingHandCursor)
        self.slider_progreso.sliderPressed.connect(self.bloquear_actualizacion_automatica)
        self.slider_progreso.sliderReleased.connect(self.cambiar_tiempo_cancion)
        
        self.lbl_tiempo_total = QLabel("00:00")
        self.lbl_tiempo_total.setStyleSheet("color: #64748b; font-size: 11px;")
        
        layout_progreso.addWidget(self.lbl_tiempo_actual)
        layout_progreso.addWidget(self.slider_progreso)
        layout_progreso.addWidget(self.lbl_tiempo_total)
        layout_principal.addLayout(layout_progreso)

        layout_controles = QHBoxLayout()
        layout_controles.setAlignment(Qt.AlignCenter)
        layout_controles.setSpacing(20)

        self.btn_anterior = QPushButton("|<")
        self.btn_anterior.setFocusPolicy(Qt.NoFocus)
        self.btn_anterior.setCursor(Qt.PointingHandCursor)
        self.btn_anterior.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #cbd5e1;
                font-size: 11px;
                font-weight: bold;
                border: none;
                min-width: 38px; max-width: 38px; min-height: 38px; max-height: 38px;
                border-radius: 19px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.12); color: #ffffff; }
        """)
        self.btn_anterior.clicked.connect(self.cancion_anterior)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFocusPolicy(Qt.NoFocus)
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                font-size: 16px;
                border: none;
                min-width: 52px; max-width: 52px; min-height: 52px; max-height: 52px;
                border-radius: 26px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.btn_play.clicked.connect(self.control_play_pausa)
        
        self.btn_siguiente = QPushButton(">|")
        self.btn_siguiente.setFocusPolicy(Qt.NoFocus)
        self.btn_siguiente.setCursor(Qt.PointingHandCursor)
        self.btn_siguiente.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #cbd5e1;
                font-size: 11px;
                font-weight: bold;
                border: none;
                min-width: 38px; max-width: 38px; min-height: 38px; max-height: 38px;
                border-radius: 19px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.12); color: #ffffff; }
        """)
        self.btn_siguiente.clicked.connect(self.cancion_siguiente)

        layout_controles.addWidget(self.btn_anterior)
        layout_controles.addWidget(self.btn_play)
        layout_controles.addWidget(self.btn_siguiente)
        layout_principal.addLayout(layout_controles)

        self.btn_mas = QPushButton("📁  Añadir carpeta local")
        self.btn_mas.setFocusPolicy(Qt.NoFocus)
        self.btn_mas.setCursor(Qt.PointingHandCursor)
        self.btn_mas.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.08); color: #ffffff; }
        """)
        self.btn_mas.clicked.connect(self.seleccionar_carpeta_manual)
        layout_principal.addWidget(self.btn_mas)

    def keyPressEvent(self, event):
        if not self.lista_canciones:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Down:
            nueva_fila = min(self.lista_widget.currentRow() + 1, self.lista_widget.count() - 1)
            self.lista_widget.setCurrentRow(nueva_fila)
        elif event.key() == Qt.Key_Up:
            nueva_fila = max(self.lista_widget.currentRow() - 1, 0)
            self.lista_widget.setCurrentRow(nueva_fila)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.indice_actual = self.lista_widget.currentRow()
            self.reproducir_cancion_actual()
        else:
            super().keyPressEvent(event)

    def formatear_tiempo(self, ms):
        segundos = int((ms / 1000) % 60)
        minutos = int((ms / (1000 * 60)) % 60)
        return f"{minutos:02d}:{segundos:02d}"

    def actualizar_posicion_barra(self, posicion):
        if not self.usuario_arrastrando:
            self.slider_progreso.setValue(posicion)
            self.lbl_tiempo_actual.setText(self.formatear_tiempo(posicion))

    def actualizar_duracion_barra(self, duracion):
        self.slider_progreso.setRange(0, duracion)
        self.lbl_tiempo_total.setText(self.formatear_tiempo(duracion))

    def detectar_fin_cancion(self, estado):
        if estado == QMediaPlayer.StoppedState:
            if self.player.position() > 0 and self.player.position() >= (self.player.duration() - 1000):
                self.cancion_siguiente()

    def bloquear_actualizacion_automatica(self):
        self.usuario_arrastrando = True

    def cambiar_tiempo_cancion(self):
        nuevo_tiempo = self.slider_progreso.value()
        self.player.setPosition(nuevo_tiempo)
        self.usuario_arrastrando = False

    def cambiar_imagen_fondo(self):
        archivo_imagen, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Fondo", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if archivo_imagen:
            ruta_limpia = archivo_imagen.replace('\\', '/')
            self.widget_central.setStyleSheet(f"""
                QWidget#VentanaPrincipal {{
                    border-image: url('{ruta_limpia}') 0 0 0 0 stretch stretch;
                }}
            """)

    def escanear_carpeta_descargas(self):
        ruta_home = os.path.expanduser("~")
        opciones_carpetas = ["Descargas", "Downloads"]
        ruta_descargas = ""
        
        for carpeta in opciones_carpetas:
            posible_ruta = os.path.join(ruta_home, carpeta)
            if os.path.exists(posible_ruta):
                ruta_descargas = posible_ruta
                break
                
        if ruta_descargas:
            self.cargar_musica_desde_ruta(ruta_descargas)
        else:
            self.lbl_estado.setText("Carpeta de descargas no encontrada.")

    def cargar_musica_desde_ruta(self, ruta):
        self.lista_widget.clear()
        self.lista_canciones = []
        
        try:
            for archivo in os.listdir(ruta):
                if archivo.lower().endswith(".mp3"):
                    self.lista_canciones.append(os.path.join(ruta, archivo))
                    self.lista_widget.addItem(archivo)
            
            if self.lista_canciones:
                self.lbl_estado.setText(f"{len(self.lista_canciones)} pistas listas")
                self.indice_actual = 0
                self.lista_widget.setCurrentRow(0)
            else:
                self.lbl_estado.setText("No se encontraron archivos .mp3")
        except Exception:
            self.lbl_estado.setText("Error al acceder a la carpeta.")

    def seleccionar_carpeta_manual(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if carpeta:
            self.cargar_musica_desde_ruta(carpeta)

    def reproducir_cancion_actual(self):
        if 0 <= self.indice_actual < len(self.lista_canciones):
            ruta_archivo = self.lista_canciones[self.indice_actual]
            url = QUrl.fromLocalFile(ruta_archivo)
            self.player.setMedia(QMediaContent(url))
            self.player.play()
            
            self.lista_widget.setCurrentRow(self.indice_actual)
            nombre_archivo = os.path.basename(ruta_archivo)
            self.lbl_estado.setText(nombre_archivo)
            self.btn_play.setText("⏸")

    def control_play_pausa(self):
        if not self.lista_canciones:
            return

        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()
            self.btn_play.setText("⏸")
        else:
            if self.indice_actual == -1:
                self.indice_actual = 0
            self.reproducir_cancion_actual()

    def reproducir_seleccionada(self, item):
        self.indice_actual = self.lista_widget.row(item)
        self.reproducir_cancion_actual()

    def cancion_siguiente(self):
        if self.lista_canciones:
            self.indice_actual = (self.indice_actual + 1) % len(self.lista_canciones)
            self.reproducir_cancion_actual()

    def cancion_anterior(self):
        if self.lista_canciones:
            self.indice_actual = (self.indice_actual - 1) % len(self.lista_canciones)
            self.reproducir_cancion_actual()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = NanoTune()
    player.show()
    sys.exit(app.exec_())