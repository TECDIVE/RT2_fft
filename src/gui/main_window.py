"""
Główne okno GUI dla radioteleskopu
PyQt5 + pyqtgraph
"""

import sys
import numpy as np
from pathlib import Path

# Dodaj root projektu do Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGroupBox, QMessageBox, QSplitter)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

from src.hardware.sdr_controller import SDRplayController
from src.gui.waterfall_widget import WaterfallWidget
from config.settings import ReceiverConfig, GUIConfig, ProcessingConfig


class RadioTelescopeWindow(QMainWindow):
    """
    Główne okno aplikacji radioteleskopu

    Zawiera:
    - Panel kontrolny (przyciski start/stop)
    - Wykres FFT w czasie rzeczywistym
    - Pasek statusu
    """

    def __init__(self):
        super().__init__()

        # Kontroler SDR
        self.sdr = SDRplayController()

        # Timer do odświeżania wykresu
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spectrum)

        # Parametry
        self.current_freq_mhz = ReceiverConfig.CENTER_FREQ_MHZ
        self.current_sr_mhz = ReceiverConfig.SAMPLE_RATE_MHZ

        # Inicjalizuj UI
        self.init_ui()

    # =========================================================================
    # INTERFEJS UŻYTKOWNIKA
    # =========================================================================

    def init_ui(self):
        """Stwórz interfejs użytkownika"""

        # Ustawienia okna
        self.setWindowTitle(GUIConfig.WINDOW_TITLE)
        self.setGeometry(100, 100, GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT)

        # Główny widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout główny
        main_layout = QVBoxLayout(central_widget)

        # Panel kontrolny
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # Splitter dla FFT i Waterfall
        splitter = QSplitter(Qt.Vertical)

        # Wykres FFT
        self.create_spectrum_plot()
        splitter.addWidget(self.plot_widget)

        # Waterfall (jeśli włączony)
        if GUIConfig.WATERFALL_ENABLED:
            self.waterfall = WaterfallWidget()
            splitter.addWidget(self.waterfall)

            # Proporcje: FFT 60%, Waterfall 40%
            splitter.setStretchFactor(0, 3)
            splitter.setStretchFactor(1, 2)
        else:
            self.waterfall = None

        main_layout.addWidget(splitter)

        # Pasek statusu
        self.status_label = QLabel('Status: Gotowy')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-top: 2px solid #cccccc;
            }
        """)
        main_layout.addWidget(self.status_label)

    def create_control_panel(self):
        """Stwórz panel kontrolny"""

        group = QGroupBox("Kontrola")
        layout = QHBoxLayout()

        # Info o konfiguracji
        info_layout = QVBoxLayout()

        self.freq_label = QLabel(f"📻 Częstotliwość: {ReceiverConfig.CENTER_FREQ_MHZ} MHz")
        self.sr_label = QLabel(f"📊 Próbkowanie: {ReceiverConfig.SAMPLE_RATE_MHZ} MSPS")
        self.gain_label = QLabel(f"🔧 Gain: -{ReceiverConfig.GAIN_REDUCTION_DB} dB")

        info_layout.addWidget(self.freq_label)
        info_layout.addWidget(self.sr_label)
        info_layout.addWidget(self.gain_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Przyciski
        btn_layout = QHBoxLayout()

        # Przycisk Połącz i Uruchom
        self.start_btn = QPushButton("▶  Połącz i Uruchom")
        self.start_btn.setMinimumHeight(60)
        self.start_btn.setMinimumWidth(200)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.start_btn.clicked.connect(self.start_observation)
        btn_layout.addWidget(self.start_btn)

        # Przycisk Stop
        self.stop_btn = QPushButton("⏹  Stop")
        self.stop_btn.setMinimumHeight(60)
        self.stop_btn.setMinimumWidth(200)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_observation)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def create_spectrum_plot(self):
        """Stwórz wykres widma FFT"""

        # Widget wykresu
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(GUIConfig.PLOT_BG_COLOR)

        # Etykiety osi
        self.plot_widget.setLabel('left', 'Moc [dB]')
        self.plot_widget.setLabel('bottom', 'Częstotliwość [MHz]')

        # Tytuł
        title_style = {'color': '#FFF', 'size': '14pt'}
        self.plot_widget.setTitle(
            f'Widmo FFT - Linia Wodoru ({ReceiverConfig.CENTER_FREQ_MHZ} MHz)',
            **title_style
        )

        # Siatka
        self.plot_widget.showGrid(x=True, y=True, alpha=GUIConfig.PLOT_GRID_ALPHA)

        # Zakres osi Y
        if not GUIConfig.PLOT_Y_AUTO:
            self.plot_widget.setYRange(GUIConfig.PLOT_Y_MIN_DB, GUIConfig.PLOT_Y_MAX_DB)

        # Krzywa wykresu
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(
                color=GUIConfig.PLOT_LINE_COLOR,
                width=GUIConfig.PLOT_LINE_WIDTH
            )
        )

        # Linia referencyjna dla linii wodoru (1420.40575 MHz)
        hydrogen_line_freq = 1420.40575177
        if abs(ReceiverConfig.CENTER_FREQ_MHZ - hydrogen_line_freq) < 5:
            # Dodaj pionową linię na częstotliwości linii wodoru
            vline = pg.InfiniteLine(
                pos=hydrogen_line_freq,
                angle=90,
                pen=pg.mkPen('r', width=1, style=Qt.DashLine),
                label='HI 21cm'
            )
            self.plot_widget.addItem(vline)

    # =========================================================================
    # OBSŁUGA ZDARZEŃ
    # =========================================================================

    def start_observation(self):
        """Rozpocznij obserwację"""

        # Inicjalizuj urządzenie
        self.set_status("Łączenie z urządzeniem...", "orange")

        if not self.sdr.initialize():
            QMessageBox.critical(
                self,
                "Błąd",
                "Nie można połączyć z urządzeniem SDRplay!\n\n"
                "Sprawdź:\n"
                "- Czy RSP1A jest podłączony?\n"
                "- Czy zainstalowano SDRplay API?\n"
                "- Czy serwis SDRplay działa?"
            )
            self.set_status("Błąd połączenia", "red")
            return

        # Konfiguruj i uruchom
        self.set_status("Konfiguracja parametrów...", "orange")

        if not self.sdr.configure_and_start():
            QMessageBox.critical(
                self,
                "Błąd",
                "Nie można skonfigurować urządzenia!\n\n"
                "Sprawdź logi w konsoli."
            )
            self.set_status("Błąd konfiguracji", "red")
            self.sdr.close()
            return

        # Sukces - uruchom odświeżanie
        self.timer.start(GUIConfig.REFRESH_RATE_MS)

        # Aktualizuj UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.set_status(
            f"✓ Obserwacja aktywna - {self.current_freq_mhz} MHz, "
            f"{self.current_sr_mhz} MSPS",
            "green"
        )

    def stop_observation(self):
        """Zatrzymaj obserwację"""

        # Zatrzymaj timer
        self.timer.stop()

        # Zatrzymaj SDR
        self.sdr.stop()

        # Aktualizuj UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.set_status("Zatrzymano", "blue")

    def update_spectrum(self):
        """Odśwież wykres FFT (wywołane przez timer)"""

        # Pobierz próbki
        samples = self.sdr.get_samples(ProcessingConfig.FFT_SIZE)

        if samples is None:
            return

        try:
            # Oblicz FFT
            # Zastosuj okno (hann, hamming, etc.)
            window = self.get_window(len(samples))
            windowed_samples = samples * window

            # FFT
            fft_data = np.fft.fftshift(np.fft.fft(windowed_samples))

            # Moc w dB (Power Spectral Density)
            power_db = 20 * np.log10(np.abs(fft_data) + 1e-10)

            # Częstotliwości
            sr_hz = self.current_sr_mhz * 1e6
            freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1 / sr_hz))
            freqs_mhz = (freqs / 1e6) + self.current_freq_mhz

            # Aktualizuj wykres
            self.curve.setData(freqs_mhz, power_db)

            # Aktualizuj waterfall
            if self.waterfall is not None:
                self.waterfall.add_spectrum(power_db, freqs_mhz)

            # Aktualizuj status co jakiś czas
            buffer_size = self.sdr.get_buffer_size()
            if buffer_size > 0:
                samples_per_sec = self.current_sr_mhz * 1e6
                buffer_time_sec = buffer_size / samples_per_sec

                # Aktualizuj co 1 sekundę (10 razy przy 100ms refresh)
                if hasattr(self, '_update_counter'):
                    self._update_counter += 1
                else:
                    self._update_counter = 0

                if self._update_counter % 10 == 0:
                    stats = self.sdr.get_stats()
                    self.set_status(
                        f"✓ Aktywny | Bufor: {buffer_size:,} próbek ({buffer_time_sec:.1f}s) | "
                        f"Łącznie: {stats['total_samples']:,} | "
                        f"Przeciążenia: {stats['overload_count']}",
                        "green"
                    )

        except Exception as e:
            print(f"✗ Błąd aktualizacji wykresu: {e}")

    def get_window(self, size):
        """Zwróć okno do FFT"""

        window_type = ProcessingConfig.WINDOW_TYPE.lower()

        if window_type == "hann":
            return np.hanning(size)
        elif window_type == "hamming":
            return np.hamming(size)
        elif window_type == "blackman":
            return np.blackman(size)
        elif window_type == "flat_top":
            # Flat top window - implementacja własna (bez scipy)
            # Współczynniki dla flat top window
            a0 = 0.21557895
            a1 = 0.41663158
            a2 = 0.277263158
            a3 = 0.083578947
            a4 = 0.006947368

            n = np.arange(size)
            window = (a0
                      - a1 * np.cos(2 * np.pi * n / (size - 1))
                      + a2 * np.cos(4 * np.pi * n / (size - 1))
                      - a3 * np.cos(6 * np.pi * n / (size - 1))
                      + a4 * np.cos(8 * np.pi * n / (size - 1)))
            return window
        else:
            # Domyślnie: prostokątne (bez okna)
            return np.ones(size)

    def set_status(self, message, color="black"):
        """Ustaw status i kolor"""

        self.status_label.setText(f"Status: {message}")

        colors = {
            "green": "#4CAF50",
            "red": "#f44336",
            "orange": "#ff9800",
            "blue": "#2196F3",
            "black": "#000000"
        }

        bg_color = colors.get(color, "#000000")

        self.status_label.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-top: 2px solid #cccccc;
                color: {bg_color};
            }}
        """)

    # =========================================================================
    # ZAMKNIĘCIE APLIKACJI
    # =========================================================================

    def closeEvent(self, event):
        """Obsługa zamknięcia okna"""

        # Zatrzymaj timer
        self.timer.stop()

        # Zamknij SDR
        self.sdr.close()

        # Zaakceptuj zamknięcie
        event.accept()


# =============================================================================
# HELPER - uruchomienie aplikacji
# =============================================================================

def run_application():
    """Uruchom aplikację GUI"""

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Ustaw styl
    app.setStyle('Fusion')

    # Stwórz i pokaż okno
    window = RadioTelescopeWindow()
    window.show()

    # Uruchom event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_application()