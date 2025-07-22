from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal


class DropGroup(QGroupBox):
    def __init__(self, title, add_button_text=None, parent=None):
        super().__init__(title, parent)
        self.layout = QVBoxLayout(self)

        # Drop area
        self.drop_frame = QFrame()
        self.drop_frame.setFrameShape(QFrame.StyledPanel)
        self.drop_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                min-height: 60px;
            }
        """)
        self.drop_frame.setAcceptDrops(True)

        self.drop_label = QLabel("Перетащите файл сюда")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("color: #888888;")

        drop_layout = QVBoxLayout(self.drop_frame)
        drop_layout.addWidget(self.drop_label)

        self.layout.addWidget(self.drop_frame)

        # Buttons
        self.buttons_layout = QHBoxLayout()

        self.add_button = None
        if add_button_text:
            self.add_button = QPushButton(add_button_text)
            self.add_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            self.buttons_layout.addWidget(self.add_button)

        self.clear_button = QPushButton("X")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.buttons_layout.addWidget(self.clear_button)

        self.layout.addLayout(self.buttons_layout)

        self.clear_button.setEnabled(False)
        if self.add_button is not None:
            self.add_button.setEnabled(False)

    def set_content(self, pixmap=None, text=None):
        if pixmap:
            self.drop_label.setPixmap(pixmap)
            self.drop_label.setText("")
            self.clear_button.setEnabled(True)

        elif text:
            self.drop_label.setText(text)
            self.drop_label.setPixmap(None)


    def set_allow_add(self, is_allow):
        if self.add_button is not None:
            self.add_button.setEnabled(is_allow)

    def clear(self):
        self.drop_label.setText("Перетащите файл сюда")
        if self.add_button is not None:
            self.add_button.setEnabled(False)
        self.clear_button.setEnabled(False)

    def enable_add(self, is_on):
        if self.add_button is None:
            return

        self.add_button.setEnabled(is_on)


class LabeledInput(QWidget):
    def __init__(self, label_text="Label", value=""):
        super().__init__(None)

        # Создаем виджеты
        self.label = QLabel(label_text)

        self.input_widget = QLineEdit()

        # Настраиваем layout
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)

        self.setLayout(layout)
        self.set_text(value)

    def text(self) -> str:
        return self.input_widget.text()

    def set_text(self, text: str):
        self.input_widget.setText(text)


class DocumentSigningView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stamp_size_input: LabeledInput
        self.sign_size_input: LabeledInput
        self.sign_button = None
        self.setWindowTitle("Подписание документов")
        self.setGeometry(100, 100, 900, 650)
        self.doc_label = None
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Left column (25%)
        self.left_column = QFrame()
        self.left_column.setFixedWidth(int(self.width() * 0.3))
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setAlignment(Qt.AlignTop)

        # Right column (75%)
        self.right_column = QFrame()
        self.right_layout = QVBoxLayout(self.right_column)

        self.main_layout.addWidget(self.left_column)
        self.main_layout.addWidget(self.right_column)

        # Initialize UI components
        self.init_ui()

    def init_ui(self):
        # Create custom drop groups
        self.stamp_group = DropGroup("Печать:", "Добавить печать")
        self.signature_group = DropGroup("Подпись:", "Добавить подпись")
        self.document_group = DropGroup("Документ:")  # Without add button
        self.stamp_size_input = LabeledInput("Диаметр печати (мм):", str(42))
        self.sign_size_input = LabeledInput("Ширина подписи (мм):",  str(20))


        # Sign button
        self.sign_button = QPushButton("Подписать документ")
        self.sign_button.setEnabled(False)
        self.sign_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        # Add components to left column
        self.left_layout.addWidget(self.stamp_group)
        self.left_layout.addWidget(self.signature_group)
        self.left_layout.addWidget(self.document_group)
        self.left_layout.addStretch()
        self.left_layout.addWidget(self.stamp_size_input)
        self.left_layout.addWidget(self.sign_size_input)
        self.left_layout.addWidget(self.sign_button)

        # Document edit area
        self.document_edit_area = QFrame()
        self.document_edit_area.setFrameShape(QFrame.StyledPanel)
        self.document_edit_area.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px dashed #aaaaaa;
            }
        """)

        # Trash area
        # self.trash_area = QFrame()
        # self.trash_area.setFrameShape(QFrame.StyledPanel)
        # self.trash_area.setStyleSheet("""
        #     QFrame {
        #         background-color: #f8f8f8;
        #         border: 2px dashed #ff6666;
        #         min-height: 40px;
        #         max-height: 80px;
        #     }
        # """)
        # trash_label = QLabel("Перетащите сюда для удаления")
        # trash_label.setAlignment(Qt.AlignCenter)
        # trash_label.setStyleSheet("color: #ff6666; font-weight: bold;")
        #
        # trash_layout = QVBoxLayout(self.trash_area)
        # trash_layout.addWidget(trash_label)

        # Add components to right column
        # self.right_layout.addWidget(self.trash_area)
        self.right_layout.addWidget(self.document_edit_area)


    def set_document_edit_image(self, pixmap):
        """Устанавливает изображение в основную область редактирования"""
        # Очищаем предыдущие виджеты в области
        for child in self.document_edit_area.children():
            if isinstance(child, QLabel):
                child.deleteLater()

        # Создаем QLabel для отображения изображения
        self.doc_label = QLabel(self.document_edit_area)
        self.doc_label.setAlignment(Qt.AlignCenter)
        self.doc_label.setScaledContents(False)

        self.doc_label.setStyleSheet("""
            QLabel {
                border: none;  # Убираем все границы у QLabel
                margin: 0px;   # Убираем отступы
                padding: 0px;  # Убираем внутренние отступы
            }
        """)

        # Фиксированная ширина
        fixed_width = 600

        # Рассчитываем пропорциональную высоту
        original_width = pixmap.width()
        original_height = pixmap.height()
        proportional_height = int((fixed_width / original_width) * original_height)

        # Масштабируем изображение
        scaled_pixmap = pixmap.scaled(
            fixed_width,
            proportional_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Устанавливаем изображение и фиксируем размер QLabel

        self.doc_label.setPixmap(scaled_pixmap)
        size = scaled_pixmap.size()
        self.doc_label.setFixedSize(size)

        # Настраиваем layout для центрирования
        layout = self.document_edit_area.layout()
        if layout is None:
            layout = QVBoxLayout(self.document_edit_area)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)  # Центрирование по вертикали и горизонтали

        # Добавляем QLabel с выравниванием по центру
        layout.addWidget(self.doc_label, alignment=Qt.AlignCenter)


class DocumentStamp(QLabel):
    clicked = pyqtSignal()  # Сигнал для будущего взаимодействия

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150);
            border: 1px dashed #888;
        """)
        self.setScaledContents(True)
        self.drag_start_position = None
        #self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            #self.setCursor(Qt.ClosedHandCursor)
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_position is None:
            return

        # Вычисляем смещение
        delta = event.pos() - self.drag_start_position
        new_pos = self.pos() + delta

        # Ограничиваем перемещение границами родителя
        parent_rect = self.parent().rect()
        new_pos.setX(max(0, min(new_pos.x(), parent_rect.width() - self.width())))
        new_pos.setY(max(0, min(new_pos.y(), parent_rect.height() - self.height())))

        self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = None
            #self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)