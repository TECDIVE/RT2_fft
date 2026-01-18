"""
Radioteleskop 1420 MHz - SDRplay RSP1A
Punkt wejścia aplikacji

Uruchom z root folderu projektu:
    python main.py
"""

import sys
from pathlib import Path

# Dodaj root projektu do Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importy
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import RadioTelescopeWindow
from config.settings import print_system_info, validate_config


def main():
    """Główna funkcja aplikacji"""

    print("=" * 70)
    print("RADIOTELESKOP 1420 MHz - SDRplay RSP1A")
    print("=" * 70)

    # Waliduj konfigurację
    print("\n🔧 Sprawdzanie konfiguracji...")
    if not validate_config():
        print("\n✗ Konfiguracja zawiera błędy!")
        print("Popraw plik config/settings.py i uruchom ponownie.")
        return 1

    print("✓ Konfiguracja poprawna")

    # Wyświetl info o systemie
    print_system_info()

    # Uruchom GUI
    print("\n🚀 Uruchamianie GUI...")
    print("=" * 70)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Nowoczesny styl

    window = RadioTelescopeWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)