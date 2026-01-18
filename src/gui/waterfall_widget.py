"""
Widget Waterfall Display
Wyświetla widmo w funkcji czasu (2D)
"""

import sys
import numpy as np
from pathlib import Path
from collections import deque

# Dodaj root projektu do Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from config.settings import GUIConfig


class WaterfallWidget(QWidget):
    """
    Widget do wyświetlania waterfall (spektrogram)

    Pokazuje widmo w funkcji czasu jako obraz 2D:
    - Oś X: Częstotliwość
    - Oś Y: Czas (najnowsze na dole)
    - Kolor: Moc sygnału [dB]
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Historia widm (bufor cykliczny)
        self.history_size = GUIConfig.WATERFALL_HISTORY_SIZE
        self.spectrum_history = deque(maxlen=self.history_size)

        # Zakres kolorów (regulowany suwakami)
        self.color_min = GUIConfig.WATERFALL_MIN_DB
        self.color_max = GUIConfig.WATERFALL_MAX_DB

        # Częstotliwości (ustawiane z zewnątrz)
        self.frequencies = None

        # Inicjalizuj UI
        self.init_ui()

    def init_ui(self):
        """Stwórz interfejs waterfall"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(GUIConfig.PLOT_BG_COLOR)
        self.plot_widget.setLabel('bottom', 'Częstotliwość [MHz]')
        self.plot_widget.setLabel('left', 'Czas [s]', units='')
        self.plot_widget.setTitle('Waterfall - Spektrogram')

        # Wyłącz auto-range dla Y (czas płynie w dół)
        self.plot_widget.setYRange(0, self.history_size)

        # ImageItem do wyświetlania waterfall
        self.image_item = pg.ImageItem()
        self.plot_widget.addItem(self.image_item)

        # Mapa kolorów
        self.set_colormap(GUIConfig.WATERFALL_COLORMAP)

        layout.addWidget(self.plot_widget)

        # Panel kontrolny - suwaki nasycenia
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)

    def create_control_panel(self):
        """Stwórz panel ze suwakami nasycenia kolorów"""

        from PyQt5.QtWidgets import QGroupBox

        group = QGroupBox("Nasycenie kolorów")
        layout = QVBoxLayout()

        # Suwak MIN
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Min [dB]:"))

        self.min_slider = QSlider(Qt.Horizontal)
        self.min_slider.setRange(-150, -20)
        self.min_slider.setValue(int(self.color_min))
        self.min_slider.setTickPosition(QSlider.TicksBelow)
        self.min_slider.setTickInterval(10)
        self.min_slider.valueChanged.connect(self.on_min_changed)
        min_layout.addWidget(self.min_slider)

        self.min_label = QLabel(f"{self.color_min:.0f}")
        self.min_label.setMinimumWidth(50)
        min_layout.addWidget(self.min_label)

        layout.addLayout(min_layout)

        # Suwak MAX
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max [dB]:"))

        self.max_slider = QSlider(Qt.Horizontal)
        self.max_slider.setRange(-100, 20)  # Rozszerzony zakres do +20 dB
        self.max_slider.setValue(int(self.color_max))
        self.max_slider.setTickPosition(QSlider.TicksBelow)
        self.max_slider.setTickInterval(20)
        self.max_slider.valueChanged.connect(self.on_max_changed)
        max_layout.addWidget(self.max_slider)

        self.max_label = QLabel(f"{self.color_max:.0f}")
        self.max_label.setMinimumWidth(50)
        max_layout.addWidget(self.max_label)

        layout.addLayout(max_layout)

        group.setLayout(layout)
        return group

    def on_min_changed(self, value):
        """Callback gdy zmienia się MIN"""
        self.color_min = value
        self.min_label.setText(f"{value:.0f}")

        # Upewnij się że min < max
        if self.color_min >= self.color_max:
            self.color_max = self.color_min + 10
            self.max_slider.setValue(int(self.color_max))

        self.update_color_scale()

    def on_max_changed(self, value):
        """Callback gdy zmienia się MAX"""
        self.color_max = value
        self.max_label.setText(f"{value:.0f}")

        # Upewnij się że max > min
        if self.color_max <= self.color_min:
            self.color_min = self.color_max - 10
            self.min_slider.setValue(int(self.color_min))

        self.update_color_scale()

    def update_color_scale(self):
        """Aktualizuj skalę kolorów"""
        self.image_item.setLevels([self.color_min, self.color_max])

    def set_colormap(self, colormap_name):
        """
        Ustaw mapę kolorów

        Args:
            colormap_name: 'viridis', 'plasma', 'inferno', 'hot', 'jet', etc.
        """

        # PyQtGraph colormap - tylko sprawdzone mapy
        try:
            if colormap_name == 'viridis':
                cmap = pg.colormap.get('viridis')
            elif colormap_name == 'plasma':
                cmap = pg.colormap.get('plasma')
            elif colormap_name == 'inferno':
                cmap = pg.colormap.get('inferno')
            elif colormap_name == 'hot':
                cmap = pg.colormap.get('CET-L4')  # Hot-like
            elif colormap_name == 'jet':
                # Jet - stwórz własną mapę
                colors = [
                    (0.0, (0, 0, 143)),  # Ciemnoniebieski
                    (0.25, (0, 0, 255)),  # Niebieski
                    (0.5, (0, 255, 0)),  # Zielony
                    (0.75, (255, 255, 0)),  # Żółty
                    (1.0, (255, 0, 0))  # Czerwony
                ]
                cmap = pg.ColorMap(
                    pos=[c[0] for c in colors],
                    color=[c[1] for c in colors]
                )
            else:
                # Domyślnie viridis
                cmap = pg.colormap.get('viridis')

            self.image_item.setColorMap(cmap)

        except Exception as e:
            print(f"⚠️ Błąd ustawiania colormap '{colormap_name}': {e}")
            print(f"   Używam domyślnej mapy viridis")
            # Fallback - prosta mapa grayscale
            cmap = pg.ColorMap(
                pos=[0.0, 1.0],
                color=[(0, 0, 0), (255, 255, 255)]
            )
            self.image_item.setColorMap(cmap)

        # Ustaw poziomy kolorów
        self.update_color_scale()

    def add_spectrum(self, power_db, frequencies=None):
        """
        Dodaj nowe widmo do waterfall

        Args:
            power_db: Tablica mocy w dB
            frequencies: Tablica częstotliwości [MHz] (opcjonalne, tylko przy pierwszym)
        """

        # Zapisz częstotliwości przy pierwszym dodaniu
        if frequencies is not None and self.frequencies is None:
            self.frequencies = frequencies

            # Ustaw zakres X
            self.plot_widget.setXRange(frequencies[0], frequencies[-1])

        # Dodaj do historii
        self.spectrum_history.append(power_db)

        # Aktualizuj obraz
        self.update_image()

    def update_image(self):
        """Aktualizuj obraz waterfall"""

        if len(self.spectrum_history) == 0:
            return

        # Konwertuj historię na tablicę 2D
        # Shape: (time, frequency)
        waterfall_data = np.array(self.spectrum_history)

        # Obróć tak żeby czas płynął w dół (najnowsze na dole)
        waterfall_data = np.flipud(waterfall_data)

        # Ustaw dane obrazu
        self.image_item.setImage(waterfall_data.T, autoLevels=False)

        # Ustaw pozycję i skalę obrazu
        if self.frequencies is not None:
            freq_min = self.frequencies[0]
            freq_max = self.frequencies[-1]
            freq_range = freq_max - freq_min

            # rect = (x, y, width, height)
            self.image_item.setRect(
                freq_min,  # x position
                0,  # y position (czas)
                freq_range,  # width (zakres częstotliwości)
                len(self.spectrum_history)  # height (liczba próbek czasu)
            )

    def clear(self):
        """Wyczyść waterfall"""
        self.spectrum_history.clear()
        self.frequencies = None
        self.image_item.clear()

    def get_colormap_names(self):
        """Zwróć dostępne mapy kolorów"""
        return ['viridis', 'plasma', 'inferno', 'hot', 'jet']