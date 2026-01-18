"""
Konfiguracja systemu radioteleskopu
Wszystkie parametry w jednym miejscu
"""

# =============================================================================
# PARAMETRY SPRZĘTOWE
# =============================================================================

class HardwareConfig:
    """Konfiguracja sprzętu"""

    # SDRplay RSP1A
    SDR_MODEL = "RSP1A"
    SDR_SERIAL = None  # None = auto-detect pierwszego urządzenia

    # LNA - Nooelec Sawbird+ H1
    LNA_GAIN_DB = 40.0      # Wzmocnienie LNA
    LNA_NF_DB = 0.8         # Noise Figure LNA

    # Temperatura szumowa systemu
    T_SYS_KELVIN = 85       # Zmierzona temperatura szumowa całego systemu

    # Antena paraboliczna
    ANTENNA_DIAMETER_M = 1.8         # Średnica czaszy [m]
    ANTENNA_EFFICIENCY = 0.80        # Sprawność anteny (0.0-1.0)
    ANTENNA_GAIN_DBI = 32.0          # Wzmocnienie anteny przy 1420 MHz [dBi]
    ANTENNA_BEAMWIDTH_DEG = 10.0     # Szerokość wiązki [stopnie]

    # Zasilanie
    BIAS_T_ENABLED = False  # Bias-T wyłączony (zewnętrzny zasilacz)


# =============================================================================
# PARAMETRY ODBIORNIKA
# =============================================================================

class ReceiverConfig:
    """Konfiguracja odbiornika SDR"""

    # Częstotliwość - PRECYZYJNA linia wodoru HI 21cm
    CENTER_FREQ_MHZ = 1420.40575177     # Częstotliwość centralna [MHz] - dokładna linia HI

    # Kalibracja częstotliwości
    FREQ_CALIBRATION_ENABLED = True     # Czy używać kalibracji
    FREQ_OFFSET_PPM = 0.0               # Offset w PPM (parts per million)
    FREQ_OFFSET_KHZ = 0.0               # Dodatkowy offset w kHz
    # Efektywna częstotliwość = CENTER_FREQ * (1 + PPM/1e6) + OFFSET_KHZ/1000

    # Próbkowanie
    SAMPLE_RATE_MHZ = 6.0           # Częstotliwość próbkowania [MHz] - max dla 14-bit ADC
    BANDWIDTH_MHZ = 6000            # Szerokość pasma IF [kHz] - BW_6_000 (pełne 6 MHz)

    # Wzmocnienie i LNA
    GAIN_REDUCTION_DB = 55          # Redukcja wzmocnienia IF [dB] (20-59)
    LNA_STATE = 5                   # Stan LNA SDR (0-9, niższy = więcej wzmocnienia)
    MIN_GAIN_REDUCTION = 20         # Minimalna redukcja (20=NORMAL, 0=EXTENDED)

    # AGC
    AGC_ENABLED = False             # AGC wyłączony (manualna kontrola)

    # Filtry
    RF_NOTCH_ENABLED = False        # Filtr notch FM 85-100 MHz (wyłączony - nie przeszkadza przy 1420 MHz)
    RF_DAB_NOTCH_ENABLED = False    # Filtr notch DAB 165-230 MHz (wyłączony - nie przeszkadza przy 1420 MHz)

    # IF i LO
    IF_MODE = "Zero"                # Zero IF - jedyny sposób na uniknięcie image frequency przy szerokim paśmie
    LO_MODE = "Auto"                # Automatyczny dobór LO
    
    # DC Spike Mitigation (software)
    DC_NOTCH_ENABLED = True         # Włącz software notch filter na DC spike
    DC_NOTCH_WIDTH_KHZ = 50         # Szerokość notch (kHz) - usuwa DC spike ale zachowuje większość sygnału HI

    # DC offset correction
    DC_OFFSET_ENABLED = True        # Korekcja DC (włączona)
    IQ_IMBALANCE_ENABLED = True     # Korekcja IQ (włączona)

    # Transfer mode
    TRANSFER_MODE = "ISOCH"         # ISOCH dla 14-bit (lub BULK dla 12-bit)


# =============================================================================
# PARAMETRY PRZETWARZANIA
# =============================================================================

class ProcessingConfig:
    """Konfiguracja przetwarzania sygnału"""

    # FFT
    FFT_SIZE = 65536                # Rozmiar FFT (potęga 2)
    WINDOW_TYPE = "hann"            # Okno: hann, hamming, blackman, flat_top

    # Integracja
    INTEGRATION_TIME_SEC = 1.0      # Czas integracji [sekundy]

    # Averaging
    AVERAGING_ENABLED = True        # Uśrednianie widm
    AVERAGING_FACTOR = 10           # Liczba widm do uśrednienia

    # Integracja długoterminowa (radioastronomia)
    SPECTRUM_INTEGRATION_COUNT = 1000      # Liczba widm do zintegrowania (domyślnie)
    SPECTRUM_INTEGRATION_ENABLED = False   # Czy integracja jest aktywna
    SPECTRUM_INTEGRATION_AUTO_SAVE = False # Automatyczny zapis po zakończeniu

    # Detekcja
    DETECTION_THRESHOLD_SIGMA = 3.0 # Próg detekcji [sigma powyżej szumu]
    BASELINE_WINDOW_MHZ = 1.0       # Okno do estymacji baseline [MHz]


# =============================================================================
# PARAMETRY GUI
# =============================================================================

class GUIConfig:
    """Konfiguracja interfejsu użytkownika"""

    # Okno główne
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 1000  # Zwiększone dla waterfall
    WINDOW_TITLE = "Radioteleskop 1420 MHz - SDRplay RSP1A"

    # Odświeżanie
    REFRESH_RATE_MS = 100           # Odświeżanie wykresu [ms]

    # Wykres FFT
    PLOT_BG_COLOR = 'k'             # Kolor tła (k=czarny)
    PLOT_LINE_COLOR = 'y'           # Kolor linii (y=żółty)
    PLOT_LINE_WIDTH = 2             # Szerokość linii
    PLOT_GRID_ALPHA = 0.3           # Przezroczystość siatki

    # Zakres osi Y
    PLOT_Y_MIN_DB = -120            # Minimum osi Y [dB]
    PLOT_Y_MAX_DB = -20             # Maximum osi Y [dB]
    PLOT_Y_AUTO = True              # Auto-skalowanie Y

    # Waterfall
    WATERFALL_ENABLED = True        # Włącz waterfall
    WATERFALL_HEIGHT = 400          # Wysokość waterfall [piksele]
    WATERFALL_HISTORY_SIZE = 500    # Liczba linii historii
    WATERFALL_COLORMAP = 'viridis'  # Mapa kolorów: viridis, plasma, inferno, hot, jet
    WATERFALL_MIN_DB = -100         # Domyślne min [dB]
    WATERFALL_MAX_DB = -40          # Domyślne max [dB]


# =============================================================================
# PARAMETRY ZAPISU DANYCH
# =============================================================================

class DataConfig:
    """Konfiguracja zapisu danych"""

    # Ścieżki
    DATA_DIR = "./data"             # Folder na dane
    LOG_DIR = "./logs"              # Folder na logi

    # Formaty plików
    DEFAULT_FORMAT = "hdf5"         # hdf5, fits, csv, npz

    # Kompresja
    COMPRESSION_ENABLED = True
    COMPRESSION_LEVEL = 6           # 0-9 dla gzip

    # Metadane
    SAVE_METADATA = True            # Zapisuj metadane (czas, parametry, etc.)
    OBSERVER_NAME = ""              # Nazwa obserwatora
    OBSERVATORY_NAME = "Home"       # Nazwa obserwatorium
    TELESCOPE_NAME = "Parabola 1.8m"


# =============================================================================
# STAŁE FIZYCZNE
# =============================================================================

class PhysicsConstants:
    """Stałe fizyczne"""

    BOLTZMANN_K = 1.380649e-23      # Stała Boltzmanna [J/K]
    SPEED_OF_LIGHT = 299792458      # Prędkość światła [m/s]

    # Linia wodoru HI
    HYDROGEN_LINE_FREQ_MHZ = 1420.40575177  # Częstotliwość linii 21cm [MHz]
    HYDROGEN_LINE_WAVELENGTH_CM = 21.106    # Długość fali [cm]


# =============================================================================
# POZIOMY DEBUGOWANIA
# =============================================================================

class DebugConfig:
    """Konfiguracja debugowania"""

    DEBUG_ENABLED = True            # Włącz debug
    VERBOSE_LOGGING = True          # Szczegółowe logi
    LOG_API_CALLS = False           # Loguj wszystkie wywołania API
    LOG_OVERLOAD_EVENTS = True      # Loguj przeciążenia
    PRINT_STATS_INTERVAL_SEC = 5.0  # Co ile wyświetlać statystyki


# =============================================================================
# WALIDACJA KONFIGURACJI
# =============================================================================

def validate_config():
    """Sprawdź poprawność konfiguracji"""

    errors = []

    # Sprawdź zakres gain
    if not (20 <= ReceiverConfig.GAIN_REDUCTION_DB <= 59):
        errors.append(f"GAIN_REDUCTION_DB musi być w zakresie 20-59, jest: {ReceiverConfig.GAIN_REDUCTION_DB}")

    # Sprawdź LNA state
    if not (0 <= ReceiverConfig.LNA_STATE <= 9):
        errors.append(f"LNA_STATE musi być w zakresie 0-9, jest: {ReceiverConfig.LNA_STATE}")

    # Sprawdź FFT size (potęga 2)
    import math
    if not (math.log2(ProcessingConfig.FFT_SIZE).is_integer()):
        errors.append(f"FFT_SIZE musi być potęgą 2, jest: {ProcessingConfig.FFT_SIZE}")

    # Sprawdź sample rate
    if not (0.2 <= ReceiverConfig.SAMPLE_RATE_MHZ <= 10.0):
        errors.append(f"SAMPLE_RATE_MHZ poza zakresem, jest: {ReceiverConfig.SAMPLE_RATE_MHZ}")

    if errors:
        print("⚠️  BŁĘDY KONFIGURACJI:")
        for err in errors:
            print(f"   - {err}")
        return False

    return True


# =============================================================================
# HELPER - Oblicz parametry systemu
# =============================================================================

def calculate_system_params():
    """Oblicz parametry teoretyczne systemu"""

    import math

    # Efektywna powierzchnia anteny
    A_eff = math.pi * (HardwareConfig.ANTENNA_DIAMETER_M / 2)**2 * HardwareConfig.ANTENNA_EFFICIENCY

    # SEFD (System Equivalent Flux Density)
    SEFD = (2 * PhysicsConstants.BOLTZMANN_K * HardwareConfig.T_SYS_KELVIN) / A_eff
    SEFD_Jy = SEFD * 1e26  # Konwersja do Jansky

    # Teoretyczna czułość przy integracji 1h
    delta_nu = ReceiverConfig.SAMPLE_RATE_MHZ * 1e6  # Hz
    t_int = 3600  # 1 godzina w sekundach
    sensitivity_Jy = SEFD_Jy / math.sqrt(delta_nu * t_int)

    return {
        'A_eff_m2': A_eff,
        'SEFD_Jy': SEFD_Jy,
        'sensitivity_1h_Jy': sensitivity_Jy,
        'beamwidth_deg': HardwareConfig.ANTENNA_BEAMWIDTH_DEG,
        'total_gain_db': HardwareConfig.ANTENNA_GAIN_DBI + HardwareConfig.LNA_GAIN_DB,
        'system_temp_K': HardwareConfig.T_SYS_KELVIN
    }


def print_system_info():
    """Wyświetl informacje o systemie"""

    print("=" * 70)
    print("KONFIGURACJA RADIOTELESKOPU")
    print("=" * 70)

    print(f"\n📡 SPRZĘT:")
    print(f"   SDR:           {HardwareConfig.SDR_MODEL}")
    print(f"   LNA:           Sawbird H1 ({HardwareConfig.LNA_GAIN_DB} dB, NF={HardwareConfig.LNA_NF_DB} dB)")
    print(f"   Antena:        Parabola {HardwareConfig.ANTENNA_DIAMETER_M}m")
    print(f"   T_sys:         {HardwareConfig.T_SYS_KELVIN} K")

    print(f"\n📻 ODBIORNIK:")
    print(f"   Częstotliwość: {ReceiverConfig.CENTER_FREQ_MHZ} MHz")
    print(f"   Próbkowanie:   {ReceiverConfig.SAMPLE_RATE_MHZ} MHz")
    print(f"   Pasmo:         ±{ReceiverConfig.SAMPLE_RATE_MHZ/2} MHz")
    print(f"   Gain:          -{ReceiverConfig.GAIN_REDUCTION_DB} dB (LNA state={ReceiverConfig.LNA_STATE})")
    print(f"   Bias-T:        {'ON' if HardwareConfig.BIAS_T_ENABLED else 'OFF'}")

    print(f"\n🔬 PRZETWARZANIE:")
    print(f"   FFT:           {ProcessingConfig.FFT_SIZE} punktów")
    print(f"   Okno:          {ProcessingConfig.WINDOW_TYPE}")
    print(f"   Integracja:    {ProcessingConfig.INTEGRATION_TIME_SEC} s")

    params = calculate_system_params()

    print(f"\n📊 PARAMETRY TEORETYCZNE:")
    print(f"   A_eff:         {params['A_eff_m2']:.2f} m²")
    print(f"   SEFD:          {params['SEFD_Jy']:.0f} Jy")
    print(f"   Czułość (1h):  {params['sensitivity_1h_Jy']*1000:.1f} mJy")
    print(f"   Beamwidth:     {params['beamwidth_deg']:.1f}°")
    print(f"   Gain całk.:    {params['total_gain_db']:.1f} dB")

    print("\n" + "=" * 70)


# Auto-walidacja przy imporcie
if __name__ == "__main__":
    if validate_config():
        print("✓ Konfiguracja poprawna")
        print_system_info()
    else:
        print("✗ Konfiguracja zawiera błędy!")
