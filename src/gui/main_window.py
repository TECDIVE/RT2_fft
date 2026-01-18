"""
Główne okno GUI dla radioteleskopu
PyQt5 + pyqtgraph
Z funkcją integracji widm dla radioastronomii
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime
import time

# Dodaj root projektu do Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGroupBox, QMessageBox, 
                             QSplitter, QSpinBox, QProgressBar, QFileDialog,
                             QDoubleSpinBox, QCheckBox)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

from src.hardware.sdr_controller import SDRplayController
from src.gui.waterfall_widget import WaterfallWidget
from config.settings import ReceiverConfig, GUIConfig, ProcessingConfig, DataConfig


class RadioTelescopeWindow(QMainWindow):
    """
    Główne okno aplikacji radioteleskopu

    Zawiera:
    - Panel kontrolny (przyciski start/stop)
    - Panel integracji widm (dla obserwacji radioastronomicznych)
    - Wykres FFT w czasie rzeczywistym
    - Waterfall
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

        # Integracja widm
        self.integration_active = False
        self.integration_count = 0
        self.integration_target = ProcessingConfig.SPECTRUM_INTEGRATION_COUNT
        self.integrated_spectrum = None
        self.integration_freqs = None
        self.integration_start_time = None  # Czas rozpoczęcia integracji
        self.last_integration_update_time = None  # Ostatnia aktualizacja

        # Kalibracja częstotliwości
        self.freq_offset_ppm = ReceiverConfig.FREQ_OFFSET_PPM
        self.freq_offset_khz = ReceiverConfig.FREQ_OFFSET_KHZ
        self.calibration_enabled = ReceiverConfig.FREQ_CALIBRATION_ENABLED

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

        # Panel kalibracji częstotliwości
        calibration_panel = self.create_calibration_panel()
        main_layout.addWidget(calibration_panel)

        # Panel integracji widm
        integration_panel = self.create_integration_panel()
        main_layout.addWidget(integration_panel)

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

    def create_calibration_panel(self):
        """Stwórz panel kalibracji częstotliwości"""

        group = QGroupBox("🎯 Kalibracja Częstotliwości")
        main_layout = QVBoxLayout()

        # Górny wiersz: checkbox i wartości
        top_layout = QHBoxLayout()

        # Checkbox włączenia kalibracji
        self.calibration_checkbox = QCheckBox("Włącz kalibrację częstotliwości")
        self.calibration_checkbox.setChecked(self.calibration_enabled)
        self.calibration_checkbox.stateChanged.connect(self.toggle_calibration)
        self.calibration_checkbox.setStyleSheet("font-size: 12px; font-weight: bold;")
        top_layout.addWidget(self.calibration_checkbox)

        top_layout.addStretch()

        # Offset PPM
        ppm_label = QLabel("Offset PPM:")
        top_layout.addWidget(ppm_label)

        self.ppm_spinbox = QDoubleSpinBox()
        self.ppm_spinbox.setMinimum(-100.0)
        self.ppm_spinbox.setMaximum(100.0)
        self.ppm_spinbox.setValue(self.freq_offset_ppm)
        self.ppm_spinbox.setDecimals(3)
        self.ppm_spinbox.setSingleStep(0.1)
        self.ppm_spinbox.setSuffix(" ppm")
        self.ppm_spinbox.setMinimumWidth(120)
        self.ppm_spinbox.valueChanged.connect(self.update_frequency_calibration)
        top_layout.addWidget(self.ppm_spinbox)

        # Offset kHz
        khz_label = QLabel("Offset kHz:")
        top_layout.addWidget(khz_label)

        self.khz_spinbox = QDoubleSpinBox()
        self.khz_spinbox.setMinimum(-1000.0)
        self.khz_spinbox.setMaximum(1000.0)
        self.khz_spinbox.setValue(self.freq_offset_khz)
        self.khz_spinbox.setDecimals(3)
        self.khz_spinbox.setSingleStep(1.0)
        self.khz_spinbox.setSuffix(" kHz")
        self.khz_spinbox.setMinimumWidth(120)
        self.khz_spinbox.valueChanged.connect(self.update_frequency_calibration)
        top_layout.addWidget(self.khz_spinbox)

        main_layout.addLayout(top_layout)

        # Dolny wiersz: przyciski i info
        bottom_layout = QHBoxLayout()

        # Informacja o efektywnej częstotliwości
        self.effective_freq_label = QLabel()
        self.update_effective_frequency_display()
        self.effective_freq_label.setStyleSheet("font-size: 11px; color: #666;")
        bottom_layout.addWidget(self.effective_freq_label)

        bottom_layout.addStretch()

        # Przycisk auto-kalibracji
        self.auto_calibrate_btn = QPushButton("🎯 Auto-kalibracja z szczytu")
        self.auto_calibrate_btn.setMinimumHeight(35)
        self.auto_calibrate_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #117a8b;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.auto_calibrate_btn.clicked.connect(self.auto_calibrate_frequency)
        self.auto_calibrate_btn.setEnabled(False)
        bottom_layout.addWidget(self.auto_calibrate_btn)

        # Przycisk reset kalibracji
        reset_cal_btn = QPushButton("↻ Reset")
        reset_cal_btn.setMinimumHeight(35)
        reset_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        reset_cal_btn.clicked.connect(self.reset_calibration)
        bottom_layout.addWidget(reset_cal_btn)

        # Przycisk zapisu kalibracji
        save_cal_btn = QPushButton("💾 Zapisz")
        save_cal_btn.setMinimumHeight(35)
        save_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_cal_btn.clicked.connect(self.save_calibration_to_config)
        bottom_layout.addWidget(save_cal_btn)

        main_layout.addLayout(bottom_layout)

        group.setLayout(main_layout)
        return group

    def create_integration_panel(self):
        """Stwórz panel integracji widm"""

        group = QGroupBox("⏱ Integracja Widm (Radioastronomia)")
        main_layout = QVBoxLayout()

        # Górny wiersz: ustawienia
        settings_layout = QHBoxLayout()

        # Etykieta i pole liczby integracji
        integration_label = QLabel("Liczba integracji:")
        settings_layout.addWidget(integration_label)

        self.integration_spinbox = QSpinBox()
        self.integration_spinbox.setMinimum(1)
        self.integration_spinbox.setMaximum(1000000)  # Do miliona integracji
        self.integration_spinbox.setValue(ProcessingConfig.SPECTRUM_INTEGRATION_COUNT)
        self.integration_spinbox.setSuffix(" widm")
        self.integration_spinbox.setMinimumWidth(150)
        self.integration_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
            }
        """)
        settings_layout.addWidget(self.integration_spinbox)

        settings_layout.addStretch()

        # Przyciski kontroli integracji
        self.start_integration_btn = QPushButton("▶ Start Integracji")
        self.start_integration_btn.setMinimumHeight(40)
        self.start_integration_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.start_integration_btn.clicked.connect(self.start_integration)
        self.start_integration_btn.setEnabled(False)
        settings_layout.addWidget(self.start_integration_btn)

        self.stop_integration_btn = QPushButton("⏹ Stop Integracji")
        self.stop_integration_btn.setMinimumHeight(40)
        self.stop_integration_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.stop_integration_btn.clicked.connect(self.stop_integration)
        self.stop_integration_btn.setEnabled(False)
        settings_layout.addWidget(self.stop_integration_btn)

        self.save_spectrum_btn = QPushButton("💾 Zapisz Widmo")
        self.save_spectrum_btn.setMinimumHeight(40)
        self.save_spectrum_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #117a8b;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.save_spectrum_btn.clicked.connect(self.save_integrated_spectrum)
        self.save_spectrum_btn.setEnabled(False)
        settings_layout.addWidget(self.save_spectrum_btn)

        main_layout.addLayout(settings_layout)

        # Dolny wiersz: pasek postępu
        progress_layout = QVBoxLayout()

        # Etykieta postępu
        self.integration_progress_label = QLabel("Postęp: 0 / 0 widm (0.0%)")
        self.integration_progress_label.setStyleSheet("font-size: 12px; color: #666;")
        progress_layout.addWidget(self.integration_progress_label)
        
        # Etykieta czasu pozostałego
        self.integration_time_label = QLabel("Szacowany czas do zakończenia: --")
        self.integration_time_label.setStyleSheet("font-size: 12px; color: #0066cc; font-weight: bold;")
        progress_layout.addWidget(self.integration_time_label)

        # Pasek postępu
        self.integration_progressbar = QProgressBar()
        self.integration_progressbar.setMinimum(0)
        self.integration_progressbar.setMaximum(100)
        self.integration_progressbar.setValue(0)
        self.integration_progressbar.setTextVisible(True)
        self.integration_progressbar.setFormat("%p%")
        self.integration_progressbar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.integration_progressbar)

        main_layout.addLayout(progress_layout)

        group.setLayout(main_layout)
        return group

    def create_spectrum_plot(self):
        """Stwórz wykres widma FFT"""

        # Widget wykresu
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(GUIConfig.PLOT_BG_COLOR)

        # Etykiety osi
        self.plot_widget.setLabel('left', 'Moc [dB]')
        self.plot_widget.setLabel('bottom', 'Przesunięcie Dopplera [km/s]', color='white')

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

        # Krzywa wykresu - bieżące widmo (żółta)
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(
                color=GUIConfig.PLOT_LINE_COLOR,
                width=GUIConfig.PLOT_LINE_WIDTH
            )
        )

        # Krzywa zintegrowanego widma (czerwona, grubsza)
        self.integrated_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='r', width=3)
        )

        # Linia referencyjna dla linii wodoru (v=0 km/s)
        vline = pg.InfiniteLine(
            pos=0,  # v=0 km/s
            angle=90,
            pen=pg.mkPen('r', width=1, style=Qt.DashLine),
            label='v=0'
        )
        self.plot_widget.addItem(vline)
        
        # Dodaj górną oś X z częstotliwościami w MHz
        # Używamy getPlotItem().layout aby dostać się do layoutu
        self.top_axis = pg.AxisItem(orientation='top')
        plot_layout = self.plot_widget.getPlotItem().layout
        plot_layout.addItem(self.top_axis, 1, 1)
        self.top_axis.linkToView(self.plot_widget.getPlotItem().vb)
        self.top_axis.setLabel('Częstotliwość [MHz]', color='cyan')
        
        # Zachowujemy referencje do konwersji Doppler <-> MHz
        self.freq_mhz_array = None

    # =========================================================================
    # INTEGRACJA WIDM
    # =========================================================================
    
    def freq_to_doppler_velocity(self, freqs_mhz):
        """
        Konwertuj częstotliwości na prędkości Dopplera w km/s
        
        Wzór: v = c * (f0 - f) / f0
        gdzie:
        - v to prędkość radialna [km/s]
        - c to prędkość światła [km/s]
        - f0 to częstotliwość linii wodoru w spoczynku [MHz]
        - f to obserwowana częstotliwość [MHz]
        
        Uwaga: dla wzrostu częstotliwości (f > f0) mamy ujemne prędkości (zbliżanie)
               dla spadku częstotliwości (f < f0) mamy dodatnie prędkości (oddalanie)
        """
        c = 299792.458  # Prędkość światła w km/s
        f0 = 1420.40575177  # Częstotliwość linii HI w MHz
        
        # v = c * (f0 - f) / f0
        # Dla f > f0 (blue shift): v < 0 (zbliżanie się)
        # Dla f < f0 (red shift): v > 0 (oddalanie się)
        velocities_km_s = c * (f0 - freqs_mhz) / f0
        
        return velocities_km_s
    
    def doppler_to_freq(self, velocities_km_s):
        """
        Konwertuj prędkości Dopplera z powrotem na częstotliwości
        
        Odwrotność freq_to_doppler_velocity
        """
        c = 299792.458  # Prędkość światła w km/s
        f0 = 1420.40575177  # Częstotliwość linii HI w MHz
        
        # Z wzoru: v = c * (f0 - f) / f0
        # Wyznaczamy f: f = f0 * (1 - v/c)
        freqs_mhz = f0 * (1 - velocities_km_s / c)
        
        return freqs_mhz
    
    def update_top_axis_ticks(self, doppler_velocities):
        """
        Aktualizuj znaczniki na górnej osi MHz na podstawie zakresu prędkości Dopplera
        """
        if doppler_velocities is None or len(doppler_velocities) == 0:
            return
        
        # Pobierz zakres prędkości Dopplera
        v_min = np.min(doppler_velocities)
        v_max = np.max(doppler_velocities)
        
        # Konwertuj na częstotliwości
        freq_at_vmin = self.doppler_to_freq(v_min)
        freq_at_vmax = self.doppler_to_freq(v_max)
        
        # Utwórz znaczniki częstotliwości
        # Wybieramy ~8-10 znaczników
        num_ticks = 10
        freq_ticks = np.linspace(freq_at_vmax, freq_at_vmin, num_ticks)
        
        # Konwertuj z powrotem na pozycje v (dla wyrównania z dolną osią)
        v_positions = self.freq_to_doppler_velocity(freq_ticks)
        
        # Utwórz etykiety
        tick_labels = [(v_pos, f"{freq:.2f}") for v_pos, freq in zip(v_positions, freq_ticks)]
        
        # Ustaw znaczniki na górnej osi
        self.top_axis.setTicks([tick_labels])

    # =========================================================================
    # INTEGRACJA WIDM
    # =========================================================================

    def start_integration(self):
        """Rozpocznij integrację widm"""

        # Pobierz liczbę integracji z spinboxa
        self.integration_target = self.integration_spinbox.value()

        # Resetuj liczniki
        self.integration_count = 0
        self.integrated_spectrum = None
        self.integration_freqs = None
        
        # Zapisz czas rozpoczęcia
        self.integration_start_time = time.time()
        self.last_integration_update_time = time.time()
        self.integration_freqs = None

        # Ustaw status
        self.integration_active = True

        # Aktualizuj UI
        self.start_integration_btn.setEnabled(False)
        self.stop_integration_btn.setEnabled(True)
        self.integration_spinbox.setEnabled(False)
        self.save_spectrum_btn.setEnabled(False)

        # Aktualizuj pasek postępu
        self.update_integration_progress()

        self.set_status(
            f"🔬 Integracja rozpoczęta: 0 / {self.integration_target} widm",
            "blue"
        )

        print(f"\n{'='*70}")
        print(f"🔬 INTEGRACJA WIDM ROZPOCZĘTA")
        print(f"{'='*70}")
        print(f"   Docelowa liczba integracji: {self.integration_target}")
        print(f"   Odszumianie w czasie rzeczywistym...")
        print(f"{'='*70}\n")

    def stop_integration(self):
        """Zatrzymaj integrację widm"""

        self.integration_active = False

        # Aktualizuj UI
        self.start_integration_btn.setEnabled(True)
        self.stop_integration_btn.setEnabled(False)
        self.integration_spinbox.setEnabled(True)

        # Włącz zapis jeśli mamy dane
        if self.integrated_spectrum is not None and self.integration_count > 0:
            self.save_spectrum_btn.setEnabled(True)

        self.set_status(
            f"⏸ Integracja zatrzymana: {self.integration_count} / {self.integration_target} widm",
            "orange"
        )

        print(f"\n⏸ Integracja zatrzymana na {self.integration_count} widmach")

    def update_integration_progress(self):
        """Aktualizuj pasek postępu integracji"""

        if self.integration_target > 0:
            progress_pct = (self.integration_count / self.integration_target) * 100
            self.integration_progressbar.setValue(int(progress_pct))

            self.integration_progress_label.setText(
                f"Postęp: {self.integration_count} / {self.integration_target} widm ({progress_pct:.1f}%)"
            )
            
            # Oblicz szacowany czas pozostały
            if self.integration_count > 0 and self.integration_start_time is not None:
                elapsed_time = time.time() - self.integration_start_time
                avg_time_per_spectrum = elapsed_time / self.integration_count
                remaining_spectra = self.integration_target - self.integration_count
                estimated_remaining_time = avg_time_per_spectrum * remaining_spectra
                
                # Formatuj czas
                if estimated_remaining_time < 60:
                    time_str = f"{int(estimated_remaining_time)}s"
                elif estimated_remaining_time < 3600:
                    minutes = int(estimated_remaining_time / 60)
                    seconds = int(estimated_remaining_time % 60)
                    time_str = f"{minutes}m {seconds}s"
                else:
                    hours = int(estimated_remaining_time / 3600)
                    minutes = int((estimated_remaining_time % 3600) / 60)
                    time_str = f"{hours}h {minutes}m"
                
                self.integration_time_label.setText(
                    f"Szacowany czas do zakończenia: {time_str}"
                )
            else:
                self.integration_time_label.setText("Szacowany czas do zakończenia: obliczanie...")
        else:
            self.integration_progressbar.setValue(0)
            self.integration_progress_label.setText("Postęp: 0 / 0 widm (0.0%)")
            self.integration_time_label.setText("Szacowany czas do zakończenia: --")

    def integrate_spectrum(self, power_db, doppler_velocities):
        """Zintegruj bieżące widmo z narastającą sumą"""

        if not self.integration_active:
            return

        # Pierwsza integracja - inicjalizuj bufor
        if self.integrated_spectrum is None:
            self.integrated_spectrum = np.zeros_like(power_db, dtype=np.float64)
            self.integration_freqs = doppler_velocities.copy()  # Teraz przechowujemy prędkości Dopplera

        # Dodaj bieżące widmo do sumy
        # Konwertujemy z dB do mocy liniowej, sumujemy, i z powrotem do dB
        linear_power = 10 ** (power_db / 10.0)
        self.integrated_spectrum += linear_power

        # Zwiększ licznik
        self.integration_count += 1

        # Oblicz uśrednione widmo (w dB)
        averaged_spectrum_linear = self.integrated_spectrum / self.integration_count
        averaged_spectrum_db = 10 * np.log10(averaged_spectrum_linear + 1e-10)

        # Aktualizuj wykres zintegrowanego widma (używając prędkości Dopplera)
        self.integrated_curve.setData(self.integration_freqs, averaged_spectrum_db)

        # Aktualizuj pasek postępu
        self.update_integration_progress()

        # Aktualizuj status co 10 integracji
        if self.integration_count % 10 == 0:
            progress_pct = (self.integration_count / self.integration_target) * 100
            self.set_status(
                f"🔬 Integracja: {self.integration_count} / {self.integration_target} widm ({progress_pct:.1f}%)",
                "blue"
            )

        # Sprawdź czy osiągnięto cel
        if self.integration_count >= self.integration_target:
            self.integration_complete()

    def integration_complete(self):
        """Obsługa zakończenia integracji"""

        self.integration_active = False

        # Aktualizuj UI
        self.start_integration_btn.setEnabled(True)
        self.stop_integration_btn.setEnabled(False)
        self.integration_spinbox.setEnabled(True)
        self.save_spectrum_btn.setEnabled(True)

        self.set_status(
            f"✓ Integracja zakończona: {self.integration_count} widm zintegrowanych",
            "green"
        )

        print(f"\n{'='*70}")
        print(f"✓ INTEGRACJA ZAKOŃCZONA")
        print(f"{'='*70}")
        print(f"   Liczba zintegrowanych widm: {self.integration_count}")
        print(f"   Czas integracji: ~{self.integration_count * 0.1:.1f} sekund")
        print(f"   Widmo gotowe do zapisu")
        print(f"{'='*70}\n")

        # Wyświetl komunikat
        QMessageBox.information(
            self,
            "Integracja zakończona",
            f"Zintegrowano {self.integration_count} widm!\n\n"
            f"Widmo zostało odszumione i jest gotowe do zapisu.\n"
            f"Użyj przycisku 'Zapisz Widmo' aby zapisać dane."
        )

    def save_integrated_spectrum(self):
        """Zapisz zintegrowane widmo do pliku"""

        if self.integrated_spectrum is None or self.integration_count == 0:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Brak zintegrowanego widma do zapisu.\n\n"
                "Najpierw wykonaj integrację widm."
            )
            return

        # Dialog zapisu pliku
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"spectrum_integrated_{self.integration_count}x_{timestamp}.npz"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz zintegrowane widmo",
            str(Path(DataConfig.DATA_DIR) / default_filename),
            "NumPy Archive (*.npz);;CSV (*.csv);;All Files (*)"
        )

        if not filename:
            return  # Użytkownik anulował

        try:
            # Oblicz uśrednione widmo w dB
            averaged_spectrum_linear = self.integrated_spectrum / self.integration_count
            averaged_spectrum_db = 10 * np.log10(averaged_spectrum_linear + 1e-10)

            # Przygotuj metadane
            metadata = {
                'integration_count': self.integration_count,
                'center_freq_mhz': self.current_freq_mhz,
                'sample_rate_mhz': self.current_sr_mhz,
                'fft_size': ProcessingConfig.FFT_SIZE,
                'window_type': ProcessingConfig.WINDOW_TYPE,
                'timestamp': timestamp,
                'gain_reduction_db': ReceiverConfig.GAIN_REDUCTION_DB,
                'lna_state': ReceiverConfig.LNA_STATE
            }

            # Zapisz w formacie NPZ lub CSV
            if filename.endswith('.csv'):
                # Format CSV
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['# Zintegrowane widmo - Radioteleskop 1420 MHz'])
                    writer.writerow([f'# Liczba integracji: {self.integration_count}'])
                    writer.writerow([f'# Częstotliwość centralna: {self.current_freq_mhz} MHz'])
                    writer.writerow([f'# Data: {timestamp}'])
                    writer.writerow(['Doppler_Velocity_km_s', 'Power_dB'])
                    for velocity, power in zip(self.integration_freqs, averaged_spectrum_db):
                        writer.writerow([velocity, power])
            else:
                # Format NPZ (domyślny)
                np.savez_compressed(
                    filename,
                    doppler_velocities_km_s=self.integration_freqs,
                    power_db=averaged_spectrum_db,
                    metadata=metadata
                )

            self.set_status(f"✓ Widmo zapisane: {Path(filename).name}", "green")

            print(f"\n✓ Zintegrowane widmo zapisane:")
            print(f"   Plik: {filename}")
            print(f"   Liczba integracji: {self.integration_count}")
            print(f"   Format: {'CSV' if filename.endswith('.csv') else 'NPZ'}")

            QMessageBox.information(
                self,
                "Zapis pomyślny",
                f"Zintegrowane widmo zapisane pomyślnie!\n\n"
                f"Plik: {Path(filename).name}\n"
                f"Liczba integracji: {self.integration_count}"
            )

        except Exception as e:
            print(f"✗ Błąd zapisu widma: {e}")
            QMessageBox.critical(
                self,
                "Błąd zapisu",
                f"Nie udało się zapisać widma:\n\n{str(e)}"
            )

    # =========================================================================
    # KALIBRACJA CZĘSTOTLIWOŚCI
    # =========================================================================

    def toggle_calibration(self, state):
        """Włącz/wyłącz kalibrację"""
        self.calibration_enabled = (state == Qt.Checked)
        self.update_effective_frequency_display()
        
        if self.calibration_enabled:
            print(f"✓ Kalibracja włączona: PPM={self.freq_offset_ppm}, kHz={self.freq_offset_khz}")
        else:
            print("✗ Kalibracja wyłączona")

    def update_frequency_calibration(self):
        """Aktualizuj wartości kalibracji z spinboxów"""
        self.freq_offset_ppm = self.ppm_spinbox.value()
        self.freq_offset_khz = self.khz_spinbox.value()
        self.update_effective_frequency_display()

    def update_effective_frequency_display(self):
        """Aktualizuj wyświetlanie efektywnej częstotliwości"""
        base_freq = ReceiverConfig.CENTER_FREQ_MHZ
        
        if self.calibration_enabled:
            # Oblicz efektywną częstotliwość
            effective_freq = base_freq * (1 + self.freq_offset_ppm / 1e6) + self.freq_offset_khz / 1000
            offset_mhz = effective_freq - base_freq
            
            self.effective_freq_label.setText(
                f"Efektywna częstotliwość: {effective_freq:.9f} MHz "
                f"(offset: {offset_mhz*1000:+.3f} kHz)"
            )
        else:
            self.effective_freq_label.setText(
                f"Częstotliwość bazowa: {base_freq:.9f} MHz (bez kalibracji)"
            )

    def apply_frequency_calibration(self, freqs_mhz):
        """Zastosuj kalibrację do tablicy częstotliwości"""
        if not self.calibration_enabled:
            return freqs_mhz
        
        # Oblicz offset względem częstotliwości centralnej
        center_freq = ReceiverConfig.CENTER_FREQ_MHZ
        
        # Zastosuj korekcję PPM (proporcjonalnie do częstotliwości)
        freqs_corrected = freqs_mhz * (1 + self.freq_offset_ppm / 1e6)
        
        # Dodaj offset w kHz
        freqs_corrected += self.freq_offset_khz / 1000
        
        return freqs_corrected

    def auto_calibrate_frequency(self):
        """Automatyczna kalibracja na podstawie wykrytego szczytu"""
        
        # Potrzebujemy bieżącego widma
        if not hasattr(self, '_last_power_db') or not hasattr(self, '_last_freqs_mhz'):
            QMessageBox.warning(
                self,
                "Brak danych",
                "Rozpocznij obserwację, aby móc wykonać auto-kalibrację."
            )
            return
        
        power_db = self._last_power_db
        freqs_mhz = self._last_freqs_mhz
        
        # Znajdź szczyt w oknie ±2 MHz wokół linii HI
        HI_FREQ = 1420.40575177
        window_mhz = 2.0
        
        mask = (freqs_mhz >= HI_FREQ - window_mhz) & (freqs_mhz <= HI_FREQ + window_mhz)
        window_freqs = freqs_mhz[mask]
        window_power = power_db[mask]
        
        if len(window_power) == 0:
            QMessageBox.warning(
                self,
                "Błąd",
                "Nie znaleziono danych w oknie kalibracji."
            )
            return
        
        # Znajdź szczyt
        peak_idx = np.argmax(window_power)
        peak_freq = window_freqs[peak_idx]
        peak_power = window_power[peak_idx]
        
        # Oblicz baseline
        baseline = np.median(window_power)
        
        # Sprawdź czy szczyt jest znaczący
        if peak_power - baseline < 3.0:  # Minimum 3 dB różnicy
            reply = QMessageBox.question(
                self,
                "Słaby sygnał",
                f"Wykryty szczyt jest słaby ({peak_power - baseline:.1f} dB nad baseline).\n"
                f"Czy kontynuować kalibrację?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Oblicz potrzebną korekcję
        freq_error_mhz = peak_freq - HI_FREQ
        freq_error_khz = freq_error_mhz * 1000
        
        # Ustaw korekcję w kHz (proste przesunięcie)
        self.khz_spinbox.setValue(-freq_error_khz)  # Minus, bo korygujemy w drugą stronę
        
        # Zaktualizuj wyświetlanie
        self.update_frequency_calibration()
        
        # Informacja
        QMessageBox.information(
            self,
            "Kalibracja wykonana",
            f"Auto-kalibracja zakończona!\n\n"
            f"Wykryty szczyt: {peak_freq:.6f} MHz\n"
            f"Linia HI (ref): {HI_FREQ:.6f} MHz\n"
            f"Błąd: {freq_error_khz:+.3f} kHz\n\n"
            f"Ustawiono korekcję: {-freq_error_khz:+.3f} kHz\n"
            f"Moc szczytu: {peak_power:.1f} dB\n"
            f"Baseline: {baseline:.1f} dB\n"
            f"SNR: {peak_power - baseline:.1f} dB"
        )
        
        print(f"\n{'='*70}")
        print(f"AUTO-KALIBRACJA CZĘSTOTLIWOŚCI")
        print(f"{'='*70}")
        print(f"Wykryty szczyt:  {peak_freq:.6f} MHz")
        print(f"Linia HI (ref):  {HI_FREQ:.6f} MHz")
        print(f"Błąd:            {freq_error_khz:+.3f} kHz")
        print(f"Korekcja:        {-freq_error_khz:+.3f} kHz")
        print(f"Moc szczytu:     {peak_power:.1f} dB")
        print(f"Baseline:        {baseline:.1f} dB")
        print(f"SNR:             {peak_power - baseline:.1f} dB")
        print(f"{'='*70}\n")

    def reset_calibration(self):
        """Resetuj kalibrację do wartości domyślnych"""
        self.ppm_spinbox.setValue(0.0)
        self.khz_spinbox.setValue(0.0)
        self.update_frequency_calibration()
        
        print("↻ Kalibracja zresetowana do wartości domyślnych")

    def save_calibration_to_config(self):
        """Zapisz kalibrację do pliku konfiguracyjnego"""
        
        config_file = Path(project_root) / "config" / "settings.py"
        
        try:
            # Wczytaj plik
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Zaktualizuj wartości
            import re
            
            # PPM
            content = re.sub(
                r'FREQ_OFFSET_PPM\s*=\s*[+-]?\d+\.?\d*',
                f'FREQ_OFFSET_PPM = {self.freq_offset_ppm}',
                content
            )
            
            # kHz
            content = re.sub(
                r'FREQ_OFFSET_KHZ\s*=\s*[+-]?\d+\.?\d*',
                f'FREQ_OFFSET_KHZ = {self.freq_offset_khz}',
                content
            )
            
            # Enabled
            content = re.sub(
                r'FREQ_CALIBRATION_ENABLED\s*=\s*(?:True|False)',
                f'FREQ_CALIBRATION_ENABLED = {self.calibration_enabled}',
                content
            )
            
            # Zapisz
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            QMessageBox.information(
                self,
                "Zapis pomyślny",
                f"Kalibracja zapisana do config/settings.py\n\n"
                f"PPM: {self.freq_offset_ppm}\n"
                f"kHz: {self.freq_offset_khz}\n"
                f"Włączona: {self.calibration_enabled}"
            )
            
            print(f"💾 Kalibracja zapisana do {config_file}")
            
        except Exception as e:
            print(f"✗ Błąd zapisu kalibracji: {e}")
            QMessageBox.critical(
                self,
                "Błąd zapisu",
                f"Nie udało się zapisać kalibracji:\n\n{str(e)}"
            )

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
        self.start_integration_btn.setEnabled(True)
        self.auto_calibrate_btn.setEnabled(True)  # Włącz auto-kalibrację

        self.set_status(
            f"✓ Obserwacja aktywna - {self.current_freq_mhz} MHz, "
            f"{self.current_sr_mhz} MSPS",
            "green"
        )

    def stop_observation(self):
        """Zatrzymaj obserwację"""

        # Zatrzymaj timer
        self.timer.stop()

        # Zatrzymaj integrację jeśli aktywna
        if self.integration_active:
            self.stop_integration()

        # Zatrzymaj SDR
        self.sdr.stop()

        # Aktualizuj UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.start_integration_btn.setEnabled(False)
        self.stop_integration_btn.setEnabled(False)
        self.auto_calibrate_btn.setEnabled(False)  # Wyłącz auto-kalibrację

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
            
            # Opcjonalny software notch filter na DC spike (tylko dla Zero IF)
            if hasattr(ReceiverConfig, 'DC_NOTCH_ENABLED') and ReceiverConfig.DC_NOTCH_ENABLED:
                # Znajdź indeks DC (środek widma)
                center_idx = len(power_db) // 2
                
                # Oblicz szerokość notch w binach FFT
                bin_width_hz = sr_hz / len(samples)
                notch_width_hz = ReceiverConfig.DC_NOTCH_WIDTH_KHZ * 1000
                notch_bins = int(notch_width_hz / bin_width_hz / 2)  # połowa szerokości na każdą stronę
                
                # Zastosuj notch: zastąp wartości DC przez interpolację z sąsiednich binów
                if notch_bins > 0 and notch_bins < len(power_db) // 4:
                    left_idx = max(0, center_idx - notch_bins)
                    right_idx = min(len(power_db), center_idx + notch_bins + 1)
                    
                    # Interpolacja liniowa przez DC spike
                    if left_idx > 0 and right_idx < len(power_db):
                        left_val = power_db[left_idx - 1]
                        right_val = power_db[right_idx]
                        power_db[left_idx:right_idx] = np.linspace(left_val, right_val, right_idx - left_idx)

            # Częstotliwości
            sr_hz = self.current_sr_mhz * 1e6
            freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1 / sr_hz))
            freqs_mhz = (freqs / 1e6) + self.current_freq_mhz

            # Zastosuj kalibrację częstotliwości
            freqs_mhz_calibrated = self.apply_frequency_calibration(freqs_mhz)

            # Zapisz dla auto-kalibracji
            self._last_power_db = power_db.copy()
            self._last_freqs_mhz = freqs_mhz.copy()  # Przed kalibracją!
            
            # Konwertuj częstotliwości na prędkości Dopplera (w km/s)
            doppler_velocities = self.freq_to_doppler_velocity(freqs_mhz_calibrated)
            
            # Zapisz tablicę częstotliwości dla górnej osi
            self.freq_mhz_array = freqs_mhz_calibrated

            # Aktualizuj wykres bieżącego widma (używając prędkości Dopplera)
            self.curve.setData(doppler_velocities, power_db)
            
            # Aktualizuj górną oś X (częstotliwości MHz)
            # Robmy to tylko co jakiś czas aby nie obciążać CPU
            if not hasattr(self, '_axis_update_counter'):
                self._axis_update_counter = 0
            self._axis_update_counter += 1
            
            if self._axis_update_counter % 20 == 0:  # Co 2 sekundy przy 100ms refresh
                self.update_top_axis_ticks(doppler_velocities)

            # Jeśli integracja aktywna - dodaj do sumy
            if self.integration_active:
                # Przekaż zarówno widmo jak i prędkości Dopplera
                self.integrate_spectrum(power_db, doppler_velocities)

            # Aktualizuj waterfall (używając prędkości Dopplera)
            if self.waterfall is not None:
                self.waterfall.add_spectrum(power_db, doppler_velocities)

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

                if self._update_counter % 10 == 0 and not self.integration_active:
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

        # Zatrzymaj integrację
        if self.integration_active:
            self.stop_integration()

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
