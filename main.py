import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.styles import APP_STYLE

def main():
    # Inicializa a aplicação
    app = QApplication(sys.argv)
    
    # Aplica o estilo global
    app.setStyleSheet(APP_STYLE)
    
    # Cria e mostra a janela principal
    window = MainWindow()
    window.show()
    
    # Loop de execução
    sys.exit(app.exec())

if __name__ == "__main__":
    main()