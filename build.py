import os
import shutil
import PyInstaller.__main__
from pathlib import Path

# Конфигурационные параметры
APP_NAME = "Singer"
ENTRY_SCRIPT = "main.py"
ICON_PATH = "icon.ico"  # Укажите путь к иконке или None
ONE_FILE = True  # Собирать в один файл

def clean_dist_folder():
    """Очистка папок сборки"""
    for folder in ['dist', 'build']:
        try:
            shutil.rmtree(folder)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f'Ошибка при очистке {folder}: {e}')

def build():
    """Запуск процесса сборки"""
    pyinstaller_args = [
        '--clean',
        '--windowed',  # Без консоли
        '--name', APP_NAME,
        '--noconfirm',
    ]

    # Добавляем иконку если указана
    if ICON_PATH and Path(ICON_PATH).exists():
        pyinstaller_args.extend(['--icon', ICON_PATH])

    # Режим сборки
    pyinstaller_args.append('--onefile' if ONE_FILE else '--onedir')

    # Обязательные скрытые импорты (только действительно необходимые)
    pyinstaller_args.extend([
        '--hidden-import', 'PyQt5.sip',  # Требуется для PyQt5
    ])

    # Добавляем точку входа
    pyinstaller_args.append(ENTRY_SCRIPT)

    # Запуск PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

if __name__ == "__main__":
    print("Начало сборки...")
    clean_dist_folder()
    build()
    print("\nСборка завершена! EXE-файл находится в папке 'dist'")