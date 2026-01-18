# 🔭 RT2_fft - Radioteleskop 1420 MHz

**Oprogramowanie do obserwacji radioastronomicznych linii wodoru HI (21 cm)**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![SDR](https://img.shields.io/badge/SDR-SDRplay_RSP1A-orange.svg)

---

## 📋 Spis Treści

- [O Projekcie](#o-projekcie)
- [Funkcje](#funkcje)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Użycie](#użycie)
- [Integracja Widm](#integracja-widm)
- [Struktura Projektu](#struktura-projektu)
- [Konfiguracja](#konfiguracja)
- [Analiza Danych](#analiza-danych)
- [FAQ](#faq)

---

## 🔬 O Projekcie

RT2_fft to kompletne oprogramowanie do obserwacji radioastronomicznych z wykorzystaniem odbiornika **SDRplay RSP1A** i anteny parabolicznej. Program umożliwia:

- Obserwację linii wodoru neutralnego (HI) na 1420.406 MHz
- Integrację widm dla poprawy SNR (1 - 1,000,000 integracji)
- Wizualizację widma w czasie rzeczywistym (FFT + Waterfall)
- Zapis i analizę danych w formatach NPZ i CSV

### Zastosowania:
- 🌌 Obserwacje galaktyk (rotacja, dystrybucja wodoru)
- ☁️ Mapowanie chmur międzygwiazdowych
- 📊 Pomiary prędkości radialnych
- 🔬 Profilowanie linii spektralnych

---

## ✨ Funkcje

### Podstawowe:
- ✅ Interfejs graficzny PyQt5
- ✅ Wykres FFT w czasie rzeczywistym (pyqtgraph)
- ✅ Waterfall (diagram wodospadowy)
- ✅ Automatyczna konfiguracja SDR
- ✅ Monitoring bufora i statystyk

### Integracja Widm (NOWOŚĆ):
- ✅ **Ustawialna liczba integracji** (1 - 1,000,000)
- ✅ **Pasek postępu** w czasie rzeczywistym
- ✅ **Odszumianie na żywo** - widoczne na wykresie
- ✅ **Zapis zintegrowanego widma** (NPZ, CSV)
- ✅ **Metadane obserwacji** w pliku

### Obsługiwane Formaty:
- 📊 **NPZ** - NumPy Archive (zalecany, z metadanymi)
- 📄 **CSV** - uniwersalny format tekstowy
- 🔜 **FITS** - format astronomiczny (planowany)

---

## 🛠 Wymagania

### Sprzęt:
- **SDR:** SDRplay RSP1A
- **Antena:** Parabola 1.8m (lub inna)
- **LNA:** Nooelec Sawbird+ H1 (opcjonalnie)
- **Komputer:** Linux/Windows, RAM ≥4GB

### Oprogramowanie:
- Python 3.8+
- SDRplay API v3.x
- Biblioteki Python (patrz `requirements.txt`)

---

## 📦 Instalacja

### 1. Zainstaluj SDRplay API

**Linux:**
```bash
wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.xx.x.run
chmod +x SDRplay_RSP_API-Linux-3.xx.x.run
sudo ./SDRplay_RSP_API-Linux-3.xx.x.run
```

**Windows:**
Pobierz instalator ze strony: https://www.sdrplay.com/downloads/

### 2. Sklonuj repozytorium

```bash
git clone https://github.com/TECDIVE/RT2_fft.git
cd RT2_fft
```

### 3. Zainstaluj zależności Python

```bash
pip install -r requirements.txt
```

Główne zależności:
- `PyQt5` - interfejs graficzny
- `pyqtgraph` - wykresy w czasie rzeczywistym
- `numpy` - operacje numeryczne
- `sdrplay-api` - komunikacja z SDR (ctypes)

---

## 🚀 Użycie

### Szybki Start

1. **Podłącz SDR:**
   ```bash
   # Sprawdź czy urządzenie jest wykryte
   lsusb | grep "SDRplay"
   ```

2. **Uruchom aplikację:**
   ```bash
   python main.py
   ```

3. **W GUI:**
   - Kliknij **"▶ Połącz i Uruchom"**
   - Obserwuj widmo w czasie rzeczywistym
   - Użyj **"Integracja Widm"** dla długoterminowych obserwacji

### Przykładowa Sesja:

```bash
$ python main.py

======================================================================
RADIOTELESKOP 1420 MHz - SDRplay RSP1A
======================================================================

🔧 Sprawdzanie konfiguracji...
✓ Konfiguracja poprawna

======================================================================
KONFIGURACJA RADIOTELESKOPU
======================================================================

📡 SPRZĘT:
   SDR:           RSP1A
   LNA:           Sawbird H1 (40.0 dB, NF=0.8 dB)
   Antena:        Parabola 1.8m
   T_sys:         85 K

📻 ODBIORNIK:
   Częstotliwość: 1420.40575177 MHz
   Próbkowanie:   6.0 MHz
   Pasmo:         ±3.0 MHz
   Gain:          -55 dB (LNA state=5)

🔬 PRZETWARZANIE:
   FFT:           65536 punktów
   Okno:          hann
   Integracja:    1.0 s

🚀 Uruchamianie GUI...
======================================================================
```

---

## 🔬 Integracja Widm

### Czym jest integracja?

**Integracja widm** to sumowanie kolejnych widm FFT w celu poprawy stosunku sygnału do szumu (SNR). Im więcej widm zintegrujemy, tym lepiej widoczne będą słabe sygnały.

### Wzór:
```
SNR_improvement = √N
```
gdzie N = liczba integracji

### Przykłady:
| Integracje | Poprawa SNR | Poprawa [dB] | Czas (100ms refresh) |
|-----------|-------------|--------------|----------------------|
| 100       | 10x         | +20 dB       | ~10 s                |
| 1,000     | 31.6x       | +30 dB       | ~2 min               |
| 10,000    | 100x        | +40 dB       | ~17 min              |
| 100,000   | 316x        | +50 dB       | ~2.8 h               |
| 200,000   | 447x        | +53 dB       | ~5.6 h               |

### Jak używać?

1. **Uruchom obserwację:** kliknij "▶ Połącz i Uruchom"
2. **Ustaw liczbę integracji:** wpisz wartość (np. 10000)
3. **Start integracji:** kliknij "▶ Start Integracji"
4. **Obserwuj postęp:** pasek pokazuje `N / M widm (X%)`
5. **Zapisz wynik:** po zakończeniu kliknij "💾 Zapisz Widmo"

### Wykres:
- 🟡 **Żółta linia:** bieżące widmo (szumne)
- 🔴 **Czerwona linia:** zintegrowane widmo (odszumione)
- 🔴 **Przerywana pionowa:** linia HI 1420.406 MHz

---

## 📁 Struktura Projektu

```
RT2_fft/
├── main.py                      # Punkt startowy aplikacji
├── config/
│   └── settings.py             # Konfiguracja systemu
├── src/
│   ├── api/
│   │   ├── constants.py        # Stałe API SDRplay
│   │   └── structures.py       # Struktury danych
│   ├── gui/
│   │   ├── main_window.py      # Główne okno GUI
│   │   └── waterfall_widget.py # Widget waterfall
│   └── hardware/
│       └── sdr_controller.py   # Kontroler SDR
├── data/                        # Zapisane widma
├── logs/                        # Pliki logów
├── analyze_spectrum.py          # Skrypt analizy
├── requirements.txt             # Zależności Python
├── README.md                    # Ten plik
├── QUICK_START.md              # Szybki start
└── RT2_fft_ZMIANY.md           # Szczegóły zmian
```

---

## ⚙️ Konfiguracja

Wszystkie parametry w pliku `config/settings.py`:

### Częstotliwość i Próbkowanie:
```python
CENTER_FREQ_MHZ = 1420.40575177  # Częstotliwość centralna [MHz]
SAMPLE_RATE_MHZ = 6.0            # Próbkowanie [MSPS]
```

### Wzmocnienie:
```python
GAIN_REDUCTION_DB = 55           # Redukcja IF gain (20-59)
LNA_STATE = 5                    # Stan LNA (0-9, niższy=więcej)
```

### FFT:
```python
FFT_SIZE = 65536                 # Rozmiar FFT (potęga 2)
WINDOW_TYPE = "hann"             # Okno: hann, hamming, blackman
```

### Integracja:
```python
SPECTRUM_INTEGRATION_COUNT = 1000  # Domyślna liczba
```

### GUI:
```python
REFRESH_RATE_MS = 100            # Odświeżanie [ms]
WATERFALL_ENABLED = True         # Włącz waterfall
```

---

## 📊 Analiza Danych

### Skrypt Analizy:

```bash
python analyze_spectrum.py spectrum_integrated_10000x_20260118.npz
```

**Funkcje:**
- 📈 Wyświetlenie metadanych obserwacji
- 📊 Obliczenie statystyk (średnia, odch. std, zakres)
- 🔍 Analiza linii wodoru (pozycja, moc, doppler)
- 📉 Wykresy (pełne widmo + zoom na HI)
- 💾 Eksport do CSV

### Wczytywanie w Pythonie:

```python
import numpy as np

# Wczytaj dane
data = np.load('spectrum_integrated_10000x_20260118.npz')

frequencies = data['frequencies_mhz']  # MHz
power = data['power_db']               # dB
metadata = data['metadata'].item()     # Słownik

# Informacje
print(f"Integracje: {metadata['integration_count']}")
print(f"Częstotliwość: {metadata['center_freq_mhz']} MHz")
```

### Wizualizacja:

```python
import matplotlib.pyplot as plt

plt.plot(frequencies, power, 'b-', linewidth=0.5)
plt.xlabel('Częstotliwość [MHz]')
plt.ylabel('Moc [dB]')
plt.axvline(1420.40575177, color='r', ls='--', label='HI')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

---

## ❓ FAQ

**Q: Dlaczego nie widzę linii wodoru?**  
A: Upewnij się, że:
- Antena celuje w galaktykę (np. Droga Mleczna)
- LNA jest zasilany i działa
- Gain nie jest za niski ani za wysoki
- Wykonano wystarczającą liczbę integracji (≥10,000)

**Q: Jak długo trwa integracja 100,000 widm?**  
A: Przy domyślnym odświeżaniu 100ms: około 2.8 godziny

**Q: Czy mogę zatrzymać i wznowić integrację?**  
A: Możesz zatrzymać i zapisać bieżący stan, ale nie wznowić tej samej sesji

**Q: Jaki format pliku wybrać?**  
A: **NPZ** - zalecany (szybki, z metadanymi). **CSV** - uniwersalny.

**Q: Ile RAM potrzeba?**  
A: ~4GB wystarcza. Widma są sumowane w pamięci (bardzo efektywne).

**Q: Co jeśli komputer zawiesi się podczas integracji?**  
A: Dane w pamięci zostaną utracone. Zapisuj regularnie!

**Q: Czy działa na Windows?**  
A: Tak, po zainstalowaniu SDRplay API i Python.

**Q: Jak obliczyć prędkość radialną z przesunięcia dopplerowskiego?**  
A: `v = (Δf / f₀) × c`, gdzie c = 3×10⁵ km/s

---

## 📞 Kontakt i Wsparcie

- 🐛 **Zgłaszanie błędów:** GitHub Issues
- 💬 **Dyskusje:** GitHub Discussions
- 📧 **Email:** [dodaj swój email]

---

## 📜 Licencja

MIT License - patrz plik `LICENSE`

---

## 🙏 Podziękowania

- **SDRplay** - za doskonały sprzęt i API
- **Nooelec** - za wysokiej jakości LNA
- **Społeczność radioastronomów amatorów** - za inspirację

---

## 🔮 Roadmapa

- [ ] Eksport do FITS
- [ ] Automatyczna korekcja baseline
- [ ] Fitowanie gaussowskie linii
- [ ] Obsługa wielu źródeł (switching)
- [ ] Kalibracja na źródłach znanych
- [ ] Pomiary temperatury jasności
- [ ] Mapy 2D (drift scan)

---

**Powodzenia w obserwacjach! 🔭✨**

*Ostatnia aktualizacja: 18 stycznia 2026*
