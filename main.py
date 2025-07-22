import sys
from PyQt5.QtWidgets import QApplication
from view import DocumentSigningView
from controller import DocumentSigningController


def main():
    app = QApplication(sys.argv)

    # Настройка стилей
    app.setStyleSheet("""
        QGroupBox {
            border: 1px solid #dddddd;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
    """)

    # Создаем представление
    view = DocumentSigningView()

    # Создаем контроллер и связываем с представлением
    controller = DocumentSigningController(view)

    # Показываем окно
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()