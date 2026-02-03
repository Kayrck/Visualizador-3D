# src/ui/styles.py

APP_STYLE = """
QMainWindow {
    background-color: #000000;
}

QWidget {
    color: #7FF9C6;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Painéis Laterais */
QFrame#SidePanel {
    background-color: #192E41;
    border-right: 1px solid #1EB3B2;
}

/* Botões */
QPushButton {
    background-color: #126D83;
    color: #FFFFFF;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1EB3B2;
    color: #000000;
}

QPushButton:pressed {
    background-color: #7FF9C6;
}

/* Cabeçalhos */
QLabel#Header {
    font-size: 18px;
    color: #1EB3B2;
    font-weight: bold;
    margin-bottom: 10px;
}
"""