"""
Stałe i enumy dla SDRplay API v3.15
Zgodne z dokumentacją sekcja 2.1-2.10 (str. 6-18)
"""


# =============================================================================
# 2.1.3 - Error Codes (str. 6)
# =============================================================================

class ErrorCode:
    """Kody błędów API"""
    SUCCESS = 0
    FAIL = 1
    INVALID_PARAM = 2
    OUT_OF_RANGE = 3
    GAIN_UPDATE_ERROR = 4
    RF_UPDATE_ERROR = 5
    FS_UPDATE_ERROR = 6
    HW_ERROR = 7
    ALIASING_ERROR = 8
    ALREADY_INITIALISED = 9
    NOT_INITIALISED = 10
    NOT_ENABLED = 11
    HW_VER_ERROR = 12
    OUT_OF_MEM_ERROR = 13
    SERVICE_NOT_RESPONDING = 14
    START_PENDING = 15
    STOP_PENDING = 16
    INVALID_MODE = 17
    FAILED_VERIFICATION_1 = 18
    FAILED_VERIFICATION_2 = 19
    FAILED_VERIFICATION_3 = 20
    FAILED_VERIFICATION_4 = 21
    FAILED_VERIFICATION_5 = 22
    FAILED_VERIFICATION_6 = 23
    INVALID_SERVICE_VERSION = 24

    @staticmethod
    def get_name(code):
        """Zwróć nazwę kodu błędu"""
        names = {
            0: "Success",
            1: "Fail",
            2: "InvalidParam",
            3: "OutOfRange",
            4: "GainUpdateError",
            5: "RfUpdateError",
            6: "FsUpdateError",
            7: "HwError",
            8: "AliasingError",
            9: "AlreadyInitialised",
            10: "NotInitialised",
            11: "NotEnabled",
            12: "HwVerError",
            13: "OutOfMemError",
            14: "ServiceNotResponding",
            15: "StartPending",
            16: "StopPending",
            17: "InvalidMode",
            24: "InvalidServiceVersion"
        }
        return names.get(code, f"Unknown({code})")


# =============================================================================
# 2.4.2 - Bandwidth Enumerated Type (str. 11)
# =============================================================================

class Bandwidth:
    """Szerokość pasma IF"""
    UNDEFINED = 0
    BW_0_200 = 200  # 200 kHz
    BW_0_300 = 300  # 300 kHz
    BW_0_600 = 600  # 600 kHz
    BW_1_536 = 1536  # 1.536 MHz
    BW_5_000 = 5000  # 5 MHz
    BW_6_000 = 6000  # 6 MHz
    BW_7_000 = 7000  # 7 MHz
    BW_8_000 = 8000  # 8 MHz

    @staticmethod
    def get_name(bw):
        """Zwróć nazwę bandwidth"""
        names = {
            0: "Undefined",
            200: "200 kHz",
            300: "300 kHz",
            600: "600 kHz",
            1536: "1.536 MHz",
            5000: "5 MHz",
            6000: "6 MHz",
            7000: "7 MHz",
            8000: "8 MHz"
        }
        return names.get(bw, f"Unknown({bw})")


# =============================================================================
# 2.4.2 - IF Type Enumerated Type (str. 11)
# =============================================================================

class IFType:
    """Typ częstotliwości pośredniej (IF)"""
    UNDEFINED = -1
    ZERO = 0  # Zero IF (baseband)
    IF_0_450 = 450  # 450 kHz IF
    IF_1_620 = 1620  # 1.620 MHz IF
    IF_2_048 = 2048  # 2.048 MHz IF

    @staticmethod
    def get_name(if_type):
        """Zwróć nazwę IF type"""
        names = {
            -1: "Undefined",
            0: "Zero IF",
            450: "450 kHz",
            1620: "1.620 MHz",
            2048: "2.048 MHz"
        }
        return names.get(if_type, f"Unknown({if_type})")


# =============================================================================
# 2.4.2 - LO Mode Enumerated Type (str. 11)
# =============================================================================

class LOMode:
    """Tryb lokalnego oscylatora (LO)"""
    UNDEFINED = 0
    AUTO = 1  # Automatyczny dobór
    LO_120MHZ = 2  # 120 MHz
    LO_144MHZ = 3  # 144 MHz
    LO_168MHZ = 4  # 168 MHz


# =============================================================================
# 2.4.2 - Minimum Gain Reduction Type (str. 11)
# =============================================================================

class MinGainReduction:
    """Minimalny poziom redukcji wzmocnienia"""
    EXTENDED_MIN_GR = 0  # Extended mode (0 dB min)
    NORMAL_MIN_GR = 20  # Normal mode (20 dB min)


# =============================================================================
# 2.4.2 - Tuner Select Enumerated Type (str. 11)
# =============================================================================

class TunerSelect:
    """Wybór tunera"""
    NEITHER = 0  # Żaden tuner
    TUNER_A = 1  # Tuner A
    TUNER_B = 2  # Tuner B (tylko RSPduo)
    BOTH = 3  # Oba tunery (RSPduo dual mode)


# =============================================================================
# 2.5.1 - AGC Control Enumerated Type (str. 13)
# =============================================================================

class AGCControl:
    """Tryb AGC (Automatic Gain Control)"""
    DISABLE = 0  # AGC wyłączony
    AGC_100HZ = 1  # AGC z bandwidth 100 Hz
    AGC_50HZ = 2  # AGC z bandwidth 50 Hz
    AGC_5HZ = 3  # AGC z bandwidth 5 Hz
    AGC_CTRL_EN = 4  # Nowy schemat AGC (z parametrami)


# =============================================================================
# 2.5.1 - ADS-B Mode Enumerated Type (str. 13)
# =============================================================================

class ADSBMode:
    """Tryb ADS-B"""
    DECIMATION = 0  # Z decymacją
    NO_DECIMATION_LOWPASS = 1  # Bez decymacji, lowpass
    NO_DECIMATION_BANDPASS_2MHZ = 2  # Bez decymacji, bandpass 2 MHz
    NO_DECIMATION_BANDPASS_3MHZ = 3  # Bez decymacji, bandpass 3 MHz


# =============================================================================
# 2.3.1 - Transfer Mode Enumerated Type (str. 10)
# =============================================================================

class TransferMode:
    """Tryb transferu danych USB"""
    ISOCH = 0  # Isochronous (14-bit, gwarantowana przepustowość)
    BULK = 1  # Bulk (12-bit, wyższa przepustowość ale bez gwarancji)


# =============================================================================
# 2.10.1 - Event Types (str. 18)
# =============================================================================

class EventType:
    """Typy zdarzeń callback"""
    GAIN_CHANGE = 0  # Zmiana wzmocnienia
    POWER_OVERLOAD_CHANGE = 1  # Przeciążenie mocy
    DEVICE_REMOVED = 2  # Urządzenie odłączone
    RSPDUO_MODE_CHANGE = 3  # Zmiana trybu RSPduo
    DEVICE_FAILURE = 4  # Awaria urządzenia

    @staticmethod
    def get_name(event_id):
        """Zwróć nazwę eventu"""
        names = {
            0: "GainChange",
            1: "PowerOverloadChange",
            2: "DeviceRemoved",
            3: "RspDuoModeChange",
            4: "DeviceFailure"
        }
        return names.get(event_id, f"Unknown({event_id})")


# =============================================================================
# 2.10.1 - Power Overload Event (str. 18)
# =============================================================================

class PowerOverloadEvent:
    """Zdarzenia przeciążenia mocy"""
    OVERLOAD_DETECTED = 0  # Przeciążenie wykryte
    OVERLOAD_CORRECTED = 1  # Przeciążenie skorygowane


# =============================================================================
# 2.1.2 - Device IDs (str. 6)
# =============================================================================

class DeviceID:
    """ID urządzeń SDRplay"""
    RSP1 = 1
    RSP1A = 255
    RSP2 = 2
    RSPDUO = 3
    RSPDX = 4
    RSP1B = 6
    RSPDXR2 = 7

    @staticmethod
    def get_name(device_id):
        """Zwróć nazwę urządzenia"""
        names = {
            1: "RSP1",
            255: "RSP1A",
            2: "RSP2",
            3: "RSPduo",
            4: "RSPdx",
            6: "RSP1B",
            7: "RSPdxR2"
        }
        return names.get(device_id, f"Unknown({device_id})")


# =============================================================================
# 2.1.3 - Update Reasons (str. 7-8)
# =============================================================================

class UpdateReason:
    """Powody wywołania sdrplay_api_Update()"""

    # Master only mode
    NONE = 0x00000000
    DEV_FS = 0x00000001  # Zmiana sample rate
    DEV_PPM = 0x00000002  # Zmiana PPM
    DEV_SYNC_UPDATE = 0x00000004  # Sync update
    DEV_RESET_FLAGS = 0x00000008  # Reset flags

    RSP1A_BIAST_CONTROL = 0x00000010  # Bias-T RSP1A
    RSP1A_RF_NOTCH_CONTROL = 0x00000020  # RF notch RSP1A
    RSP1A_RF_DAB_NOTCH_CONTROL = 0x00000040  # RF DAB notch RSP1A

    # Master and slave mode
    TUNER_GR = 0x00008000  # Zmiana gain reduction
    TUNER_GR_LIMITS = 0x00010000  # Zmiana gain limits
    TUNER_FRF = 0x00020000  # Zmiana RF frequency
    TUNER_BW_TYPE = 0x00040000  # Zmiana bandwidth
    TUNER_IF_TYPE = 0x00080000  # Zmiana IF type
    TUNER_DC_OFFSET = 0x00100000  # Zmiana DC offset
    TUNER_LO_MODE = 0x00200000  # Zmiana LO mode

    CTRL_DC_OFFSET_IQ_IMBALANCE = 0x00400000  # DC/IQ correction
    CTRL_DECIMATION = 0x00800000  # Decimation
    CTRL_AGC = 0x01000000  # AGC
    CTRL_ADSB_MODE = 0x02000000  # ADS-B mode
    CTRL_OVERLOAD_MSG_ACK = 0x04000000  # Overload acknowledge


class UpdateReasonExt1:
    """Rozszerzone powody update (dla RSPdx/RSPduo)"""
    NONE = 0x00000000


# =============================================================================
# 2.6 - RSP1A LNA States (str. 14 + sekcja 5)
# =============================================================================

class RSP1A_LNA:
    """Liczba stanów LNA dla RSP1A w różnych pasmach"""
    NUM_LNA_STATES = 10  # Domyślnie (większość pasm)
    NUM_LNA_STATES_AM = 7  # Pasmo AM (0-60 MHz dla HiZ)
    NUM_LNA_STATES_LBAND = 9  # Pasmo L (1000-2000 MHz)


# =============================================================================
# STAŁE POMOCNICZE
# =============================================================================

class Limits:
    """Limity parametrów"""
    MAX_BB_GR = 59  # Maksymalna redukcja wzmocnienia baseband
    MIN_BB_GR = 20  # Minimalna redukcja (normal mode)
    MIN_BB_GR_EXTENDED = 0  # Minimalna redukcja (extended mode)

    ADC_BITS = 14  # Rozdzielczość ADC (ISOCH)
    ADC_MAX_VALUE = 8191  # Maksymalna wartość ADC (2^13 - 1)
    ADC_MIN_VALUE = -8192  # Minimalna wartość ADC (-2^13)

    MIN_SAMPLE_RATE_HZ = 200000  # 200 kHz
    MAX_SAMPLE_RATE_HZ = 10000000  # 10 MHz

    MIN_FREQ_HZ = 1000  # 1 kHz
    MAX_FREQ_HZ = 2000000000  # 2 GHz


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_constants_info():
    """Wyświetl informacje o stałych"""

    print("=" * 70)
    print("STAŁE SDRPLAY API")
    print("=" * 70)

    print("\n📱 URZĄDZENIA:")
    for device_id in [1, 255, 2, 3, 4, 6, 7]:
        print(f"   {device_id:3d} = {DeviceID.get_name(device_id)}")

    print("\n⚠️  KODY BŁĘDÓW:")
    for code in [0, 1, 2, 3, 4, 5, 6, 7, 10, 14]:
        print(f"   {code:2d} = {ErrorCode.get_name(code)}")

    print("\n📻 BANDWIDTH:")
    for bw in [200, 300, 600, 1536, 5000, 6000, 7000, 8000]:
        print(f"   {bw:4d} = {Bandwidth.get_name(bw)}")

    print("\n🔧 IF TYPE:")
    for if_type in [-1, 0, 450, 1620, 2048]:
        print(f"   {if_type:4d} = {IFType.get_name(if_type)}")

    print("\n📊 EVENTS:")
    for event_id in [0, 1, 2, 3, 4]:
        print(f"   {event_id} = {EventType.get_name(event_id)}")

    print("\n⚙️  LIMITY:")
    print(f"   ADC bits:       {Limits.ADC_BITS}")
    print(f"   ADC range:      {Limits.ADC_MIN_VALUE} do {Limits.ADC_MAX_VALUE}")
    print(f"   Gain reduction: {Limits.MIN_BB_GR} - {Limits.MAX_BB_GR} dB")
    print(f"   Sample rate:    {Limits.MIN_SAMPLE_RATE_HZ / 1e6:.1f} - {Limits.MAX_SAMPLE_RATE_HZ / 1e6:.1f} MHz")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_constants_info()