from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MedSlicerPy - Visualizador de Órgãos")
        self.resize(1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (Horizontal: Menu à esquerda, Visualizador à direita)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Painel Lateral (Menu) ---
        self.side_panel = QFrame()
        self.side_panel.setObjectName("SidePanel") # Para o CSS identificar
        self.side_panel.setFixedWidth(300)
        
        side_layout = QVBoxLayout(self.side_panel)
        
        # Título do Menu
        lbl_title = QLabel("Controles")
        lbl_title.setObjectName("Header")
        side_layout.addWidget(lbl_title)
        
        # Botões de Carregamento
        self.btn_load = QPushButton("Carregar DICOM")
        side_layout.addWidget(self.btn_load)

        # Botões de Segmentação (Órgãos)
        lbl_seg = QLabel("Segmentação")
        lbl_seg.setObjectName("Header")
        side_layout.addSpacing(20)
        side_layout.addWidget(lbl_seg)
        
        organs = ["Próstata", "Rins", "Fígado", "Pâncreas", "Útero"]
        for organ in organs:
            btn = QPushButton(f"Segmentar {organ}")
            side_layout.addWidget(btn)

        side_layout.addStretch() # Empurra tudo para cima
        
        # --- 2. Área de Visualização (Placeholder do VTK) ---
        self.view_area = QFrame()
        self.view_area.setStyleSheet("background-color: #000000;")
        view_layout = QVBoxLayout(self.view_area)
        
        lbl_view = QLabel("Visualização 3D (VTK Render Window)")
        lbl_view.setAlignment(Qt.AlignCenter)
        lbl_view.setStyleSheet("color: #1EB3B2; font-size: 20px;")
        
        view_layout.addWidget(lbl_view)

        # Adicionar ao layout principal
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.view_area)

        # Conectar sinais (exemplo)
        self.btn_load.clicked.connect(self.on_load_dicom)

    def on_load_dicom(self):
        print("Abrir diálogo de arquivos...")