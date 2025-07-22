from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QFileDialog, QLabel

from config import Config
from view import DocumentStamp, DocumentSigningView

from pathlib import Path

class DocumentSigningController:
    def __init__(self, view: DocumentSigningView):
        self.view = view
        self.current_stamp = None
        self.current_signature = None
        self.current_document = None
        self.file_path = None
        self.cache_dir = Path.home() / ".doc_signer_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.config = Config(str(self.cache_dir))
        # Connect signals
        self.connect_signals()
        self.stamps = []
        self.signs = []


        # Загружаем сохраненные изображения (если есть)
        self.load_cached_images()

    def load_cached_images(self):
        """Загружаем изображения из кэша при старте"""
        stamp_path = self.cache_dir / "stamp.png"
        signature_path = self.cache_dir / "signature.png"

        if stamp_path.exists():
            self.load_image(str(stamp_path), "stamp", save_to_cache=False)

        if signature_path.exists():
            self.load_image(str(signature_path), "signature", save_to_cache=False)

    def connect_signals(self):
        # Connect clear buttons
        self.view.stamp_group.clear_button.clicked.connect(self.clear_stamp)
        self.view.signature_group.clear_button.clicked.connect(self.clear_signature)
        self.view.document_group.clear_button.clicked.connect(self.clear_document)

        # # Connect add buttons
        self.connect_add_buttons()

        # Connect drag and drop events
        self.view.stamp_group.drop_frame.dragEnterEvent = self.drag_enter_event
        self.view.stamp_group.drop_frame.dropEvent = lambda e: self.drop_event(e, 'stamp')

        self.view.signature_group.drop_frame.dragEnterEvent = self.drag_enter_event
        self.view.signature_group.drop_frame.dropEvent = lambda e: self.drop_event(e, 'signature')

        self.view.document_group.drop_frame.dragEnterEvent = self.drag_enter_event
        self.view.document_group.drop_frame.dropEvent = lambda e: self.drop_event(e, 'document')

        self.view.sign_button.clicked.connect(self.handle_sign_document)

        self.view.sign_size_input.set_text(str(self.config.settings['sign_size']))
        self.view.stamp_size_input.set_text(str(self.config.settings['stamp_size']))

        self.view.sign_size_input.input_widget.textChanged.connect(self.apply_sing_size_input)
        self.view.stamp_size_input.input_widget.textChanged.connect(self.apply_stamp_size_input)


    def apply_sing_size_input(self, value: str):
        try:
            int_value = int(value)
            self.config.settings['sign_size'] = int_value
            self.config.save_settings()
        except ValueError:
            self.view.sign_size_input.set_text(str(self.config.settings['sign_size']))

    def apply_stamp_size_input(self, value: str):
        try:
            int_value = int(value)
            self.config.settings['stamp_size'] = int_value
            self.config.save_settings()
        except ValueError:
            self.view.sign_size_input.set_text(str(self.config.settings['stamp_size']))

    def handle_sign_document(self):
        if not self.current_document:
            return

        final_pixmap = self.generate_final_document()
        if not final_pixmap:
            return

        # Сохраняем в файл (можно заменить на диалог выбора файла)
        from pathlib import Path

        original_path = Path(self.file_path)
        save_path = str(original_path.with_name(f"{original_path.stem}_подписано{original_path.suffix}"))
        final_pixmap.save(save_path)
        print(f"Документ сохранен как {save_path}")

        # Можно показать сообщение об успешном сохранении
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.view, "Готово", "Документ успешно подписан и сохранен!")

    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event, field_type):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_image(file_path, field_type)

    def add_image(self, field_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            f"Выберите {field_type}",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.load_image(file_path, field_type)

    def load_image(self, file_path, field_type, save_to_cache=True):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            if field_type == 'stamp':
                self.clear_stamp()
                self.current_stamp = pixmap
                scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.view.stamp_group.set_content(scaled_pixmap)

                # Сохраняем в кэш
                if save_to_cache:
                    cache_path = self.cache_dir / "stamp.png"
                    pixmap.save(str(cache_path))

            elif field_type == 'signature':
                self.clear_signature()
                self.current_signature = pixmap
                scaled_pixmap = pixmap.scaled(150, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.view.signature_group.set_content(scaled_pixmap)
                # Сохраняем в кэш
                if save_to_cache:
                    cache_path = self.cache_dir / "signature.png"
                    pixmap.save(str(cache_path))

            elif field_type == 'document':
                self.file_path = file_path
                self.clear_document()
                self.current_document = pixmap
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.view.document_group.set_content(scaled_pixmap)
                self.view.set_document_edit_image(pixmap)


            self.update_sign_button_state()

    def clear_stamp(self):
        self.current_stamp = None
        self.view.stamp_group.clear()
        self.update_sign_button_state()

    def clear_signature(self):
        self.current_signature = None
        self.view.signature_group.clear()
        self.update_sign_button_state()

    def clear_document(self):
        self.stamps.clear()
        self.signs.clear()
        self.current_document = None
        self.view.document_group.clear()

        for child in self.view.document_edit_area.children():
            if isinstance(child, QLabel):
                child.deleteLater()

        self.update_sign_button_state()

    def update_sign_button_state(self):
        all_filled = all([
            self.current_stamp is not None,
            self.current_signature is not None,
            self.current_document is not None
        ])
        self.view.sign_button.setEnabled(all_filled)

        self.view.signature_group.enable_add(self.current_document is not None and self.current_signature  is not None)
        self.view.stamp_group.enable_add(self.current_document is not None and self.current_stamp  is not None)

    def connect_add_buttons(self):
        if self.view.stamp_group.add_button:
            self.view.stamp_group.add_button.clicked.connect(
                lambda: self.add_document_element('stamp'))
        if self.view.signature_group.add_button:
            self.view.signature_group.add_button.clicked.connect(
                lambda: self.add_document_element('signature'))

    def is_document_landscape(self, pixmap):
        return pixmap.width() > pixmap.height()

    def calculate_element_size(self, element_type, document_pixmap):
        # Физические размеры A4 в мм
        a4_width_mm = 210
        a4_height_mm = 297

        # Определяем ориентацию документа
        is_landscape = self.is_document_landscape(document_pixmap)


        # Размеры элементов в мм
        if element_type == 'stamp':
            element_width_mm = self.config.settings['stamp_size']
            element_pixmap = self.current_stamp
        elif element_type == 'signature':
            element_width_mm = self.config.settings['sign_size']
            element_pixmap = self.current_signature
        else:
            return QSize(0, 0)

        # Рассчитываем соотношение пикселей к миллиметрам
        if is_landscape:
            px_per_mm = document_pixmap.width() / a4_height_mm
        else:
            px_per_mm = document_pixmap.width() / a4_width_mm

        # Вычисляем размеры в пикселях
        width_px = int(element_width_mm * px_per_mm)
        height_px = int(width_px * (element_pixmap.height() / element_pixmap.width())) # Сохраняем пропорции A4

        return QSize(width_px, height_px)

    def add_document_element(self, element_type):
        if not self.current_document:
            return

        if element_type == 'stamp' and not self.current_stamp:
            return
        elif element_type == 'signature' and not self.current_signature:
            return

        # Получаем нужное изображение
        pixmap = self.current_stamp if element_type == 'stamp' else self.current_signature

        # Рассчитываем размер
        element_size = self.calculate_element_size(element_type, self.view.doc_label.pixmap())

        # Создаем элемент
        element = DocumentStamp(self.view.document_edit_area)
        if element_type == 'stamp':
            self.stamps.append(element)
        else: self.signs.append(element)

        scaled_pixmap = pixmap.scaled(
            element_size.width(),
            element_size.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        element.setPixmap(scaled_pixmap)
        element.setFixedSize(element_size)

        # Позиционирование (центрирование по умолчанию)
        doc_rect = self.view.document_edit_area.rect()
        x = (doc_rect.width() - element_size.width()) // 2
        y = (doc_rect.height() - element_size.height()) // 2
        element.move(x, y)
        element.show()

    # def generate_final_document(self):
    #     if not self.current_document:
    #         return None
    #
    #     # Создаем QPixmap с размером оригинального документа
    #     final_pixmap = QPixmap(self.current_document.size())
    #     final_pixmap.fill(Qt.white)  # Белый фон
    #
    #     # Рисуем на нем оригинальный документ
    #     painter = QPainter(final_pixmap)
    #     painter.drawPixmap(0, 0, self.current_document)
    #
    #     # Рассчитываем масштаб между отображаемым и оригинальным документом
    #     scale_x = self.current_document.width() / self.view.doc_label.width()
    #     scale_y = self.current_document.height() / self.view.doc_label.height()
    #
    #     # Рисуем все элементы (печати и подписи)
    #     for element in self.elements:
    #         if not element.pixmap():
    #             continue
    #
    #         # Получаем позицию элемента относительно doc_label
    #         element_pos = element.pos()
    #         label_pos = self.view.doc_label.pos()
    #         relative_x = element_pos.x() - label_pos.x()
    #         relative_y = element_pos.y() - label_pos.y()
    #
    #         # Масштабируем позицию и размер
    #         original_x = int(relative_x * scale_x)
    #         original_y = int(relative_y * scale_y)
    #         original_width = int(element.width() * scale_x)
    #         original_height = int(element.height() * scale_y)
    #
    #         # Масштабируем изображение элемента
    #         scaled_element = element.pixmap().scaled(
    #             original_width,
    #             original_height,
    #             Qt.KeepAspectRatio,
    #             Qt.SmoothTransformation
    #         )
    #
    #         # Рисуем элемент на итоговом изображении
    #         painter.drawPixmap(original_x, original_y, scaled_element)
    #
    #     painter.end()
    #     return final_pixmap

    def generate_final_document(self):
        if not self.current_document:
            return None

        # Создаем QPixmap с размером оригинального документа
        final_pixmap = QPixmap(self.current_document.size())
        final_pixmap.fill(Qt.white)  # Белый фон

        # Рисуем на нем оригинальный документ
        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, self.current_document)

        # Рассчитываем масштаб между отображаемым и оригинальным документом
        scale_x = self.current_document.width() / self.view.doc_label.width()
        scale_y = self.current_document.height() / self.view.doc_label.height()

        # Рисуем все штампы

        for stamp in self.stamps:
            original_pixmap = self.current_stamp
            if not original_pixmap:
                continue

            # Получаем позицию элемента относительно doc_label
            element_pos = stamp.pos()
            label_pos = self.view.doc_label.pos()
            relative_x = element_pos.x() - label_pos.x()
            relative_y = element_pos.y() - label_pos.y()

            # Масштабируем позицию и размер
            original_x = int(relative_x * scale_x)
            original_y = int(relative_y * scale_y)
            original_width = int(stamp.width() * scale_x)
            original_height = int(stamp.height() * scale_y)

            # Масштабируем оригинальное изображение (не преобразованное)
            scaled_element = original_pixmap.scaled(
                original_width,
                original_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Рисуем элемент на итоговом изображении
            painter.drawPixmap(original_x, original_y, scaled_element)

        # Рисуем все подписи
        for sign in self.signs:
            original_pixmap = self.current_signature
            if not original_pixmap:
                continue

            # Получаем позицию элемента относительно doc_label
            element_pos = sign.pos()
            label_pos = self.view.doc_label.pos()
            relative_x = element_pos.x() - label_pos.x()
            relative_y = element_pos.y() - label_pos.y()

            # Масштабируем позицию и размер
            original_x = int(relative_x * scale_x)
            original_y = int(relative_y * scale_y)
            original_width = int(sign.width() * scale_x)
            original_height = int(sign.height() * scale_y)

            # Масштабируем оригинальное изображение (не преобразованное)
            scaled_element = original_pixmap.scaled(
                original_width,
                original_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Рисуем элемент на итоговом изображении
            painter.drawPixmap(original_x, original_y, scaled_element)

        painter.end()
        return final_pixmap