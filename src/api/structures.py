"""
Struktury ctypes dla SDRplay API v3.15
Zgodne z dokumentacją sekcja 2 (str. 5-19)
"""

import ctypes
import sys

# =============================================================================
# STAŁE
# =============================================================================

SDRPLAY_MAX_SER_NO_LEN = 64
SDRPLAY_MAX_DEVICES = 16


# =============================================================================
# 2.4.3 - Gain Structures (str. 12)
# =============================================================================

class sdrplay_api_GainValuesT(ctypes.Structure):
    """Aktualne wartości wzmocnienia"""
    _fields_ = [
        ("curr", ctypes.c_float),
        ("max", ctypes.c_float),
        ("min", ctypes.c_float)
    ]


class sdrplay_api_GainT(ctypes.Structure):
    """Parametry wzmocnienia"""
    _fields_ = [
        ("gRdB", ctypes.c_int),  # Redukcja wzmocnienia IF [dB]
        ("LNAstate", ctypes.c_ubyte),  # Stan LNA (0-9)
        ("syncUpdate", ctypes.c_ubyte),  # Synchroniczna aktualizacja
        ("minGr", ctypes.c_uint),  # Min gain reduction mode
        ("gainVals", sdrplay_api_GainValuesT)  # Wartości wzmocnienia (output)
    ]


# =============================================================================
# 2.4.3 - RF Frequency Structure (str. 12)
# =============================================================================

class sdrplay_api_RfFreqT(ctypes.Structure):
    """Parametry częstotliwości RF"""
    _fields_ = [
        ("rfHz", ctypes.c_double),  # Częstotliwość RF [Hz]
        ("syncUpdate", ctypes.c_ubyte)  # Synchroniczna aktualizacja
    ]


# =============================================================================
# 2.4.3 - DC Offset Tuner Structure (str. 12)
# =============================================================================

class sdrplay_api_DcOffsetTunerT(ctypes.Structure):
    """Parametry kalibracji DC offset tunera"""
    _fields_ = [
        ("dcCal", ctypes.c_ubyte),  # DC calibration mode
        ("speedUp", ctypes.c_ubyte),  # Speed up calibration
        ("trackTime", ctypes.c_int),  # Track time
        ("refreshRateTime", ctypes.c_int)  # Refresh rate time
    ]


# =============================================================================
# 2.4.3 - Tuner Parameters Structure (str. 12)
# =============================================================================

class sdrplay_api_TunerParamsT(ctypes.Structure):
    """Parametry tunera"""
    _fields_ = [
        ("bwType", ctypes.c_uint),  # Bandwidth type
        ("ifType", ctypes.c_int),  # IF type
        ("loMode", ctypes.c_uint),  # LO mode
        ("gain", sdrplay_api_GainT),  # Gain settings
        ("rfFreq", sdrplay_api_RfFreqT),  # RF frequency
        ("dcOffsetTuner", sdrplay_api_DcOffsetTunerT)  # DC offset params
    ]


# =============================================================================
# 2.5.2 - Control Parameters Structures (str. 13)
# =============================================================================

class sdrplay_api_DcOffsetT(ctypes.Structure):
    """Parametry korekcji DC offset"""
    _fields_ = [
        ("DCenable", ctypes.c_ubyte),  # DC offset correction enable
        ("IQenable", ctypes.c_ubyte)  # IQ imbalance correction enable
    ]


class sdrplay_api_DecimationT(ctypes.Structure):
    """Parametry decymacji"""
    _fields_ = [
        ("enable", ctypes.c_ubyte),  # Decimation enable
        ("decimationFactor", ctypes.c_ubyte),  # Decimation factor
        ("wideBandSignal", ctypes.c_ubyte)  # Wide band signal
    ]


class sdrplay_api_AgcT(ctypes.Structure):
    """Parametry AGC (Automatic Gain Control)"""
    _fields_ = [
        ("enable", ctypes.c_uint),  # AGC mode
        ("setPoint_dBfs", ctypes.c_int),  # AGC setpoint [dBfs]
        ("attack_ms", ctypes.c_ushort),  # Attack time [ms]
        ("decay_ms", ctypes.c_ushort),  # Decay time [ms]
        ("decay_delay_ms", ctypes.c_ushort),  # Decay delay [ms]
        ("decay_threshold_dB", ctypes.c_ushort),  # Decay threshold [dB]
        ("syncUpdate", ctypes.c_int)  # Synchronous update
    ]


class sdrplay_api_ControlParamsT(ctypes.Structure):
    """Parametry kontrolne"""
    _fields_ = [
        ("dcOffset", sdrplay_api_DcOffsetT),  # DC offset correction
        ("decimation", sdrplay_api_DecimationT),  # Decimation
        ("agc", sdrplay_api_AgcT),  # AGC
        ("adsbMode", ctypes.c_uint)  # ADS-B mode
    ]


# =============================================================================
# 2.6 - RSP1A Specific Structures (str. 14)
# =============================================================================

class sdrplay_api_Rsp1aTunerParamsT(ctypes.Structure):
    """Parametry tunera RSP1A"""
    _fields_ = [
        ("biasTEnable", ctypes.c_ubyte)  # Bias-T enable
    ]


class sdrplay_api_Rsp1aParamsT(ctypes.Structure):
    """Parametry urządzenia RSP1A"""
    _fields_ = [
        ("rfNotchEnable", ctypes.c_ubyte),  # RF notch filter (FM)
        ("rfDabNotchEnable", ctypes.c_ubyte)  # RF DAB notch filter
    ]


# =============================================================================
# 2.2.1 - Receive Channel Structure (str. 9)
# =============================================================================

class sdrplay_api_RxChannelParamsT(ctypes.Structure):
    """Parametry kanału odbiorczego"""
    _fields_ = [
        ("tunerParams", sdrplay_api_TunerParamsT),  # Tuner params
        ("ctrlParams", sdrplay_api_ControlParamsT),  # Control params
        ("rsp1aTunerParams", sdrplay_api_Rsp1aTunerParamsT),  # RSP1A tuner params
        # RSP2, RSPduo, RSPdx params (nie używamy dla RSP1A)
        ("_rsp2TunerParams", ctypes.c_byte * 32),
        ("_rspDuoTunerParams", ctypes.c_byte * 32),
        ("_rspDxTunerParams", ctypes.c_byte * 32)
    ]


# =============================================================================
# 2.3.2 - Device Parameters Structures (str. 10)
# =============================================================================

class sdrplay_api_FsFreqT(ctypes.Structure):
    """Parametry częstotliwości próbkowania ADC"""
    _fields_ = [
        ("fsHz", ctypes.c_double),  # Sample frequency [Hz]
        ("syncUpdate", ctypes.c_ubyte),  # Synchronous update
        ("reCal", ctypes.c_ubyte)  # Recalibrate
    ]


class sdrplay_api_SyncUpdateT(ctypes.Structure):
    """Parametry synchronicznej aktualizacji"""
    _fields_ = [
        ("sampleNum", ctypes.c_uint),  # Sample number
        ("period", ctypes.c_uint)  # Period
    ]


class sdrplay_api_ResetFlagsT(ctypes.Structure):
    """Flagi reset dla operacji update"""
    _fields_ = [
        ("resetGainUpdate", ctypes.c_ubyte),  # Reset gain update flag
        ("resetRfUpdate", ctypes.c_ubyte),  # Reset RF update flag
        ("resetFsUpdate", ctypes.c_ubyte)  # Reset Fs update flag
    ]


class sdrplay_api_DevParamsT(ctypes.Structure):
    """Parametry urządzenia (nie związane z kanałem odbiorczym)"""
    _fields_ = [
        ("ppm", ctypes.c_double),  # PPM correction
        ("fsFreq", sdrplay_api_FsFreqT),  # Sample frequency
        ("syncUpdate", sdrplay_api_SyncUpdateT),  # Sync update
        ("resetFlags", sdrplay_api_ResetFlagsT),  # Reset flags
        ("mode", ctypes.c_uint),  # Transfer mode (ISOCH/BULK)
        ("samplesPerPkt", ctypes.c_uint),  # Samples per packet (output)
        ("rsp1aParams", sdrplay_api_Rsp1aParamsT),  # RSP1A params
        # RSP2, RSPduo, RSPdx params (nie używamy)
        ("_rsp2Params", ctypes.c_byte * 32),
        ("_rspDuoParams", ctypes.c_byte * 32),
        ("_rspDxParams", ctypes.c_byte * 32)
    ]


# =============================================================================
# 2.1.4 - Device Parameters Structure (str. 8)
# =============================================================================

class sdrplay_api_DeviceParamsT(ctypes.Structure):
    """Główna struktura parametrów urządzenia"""
    _fields_ = [
        ("devParams", ctypes.POINTER(sdrplay_api_DevParamsT)),  # Device params
        ("rxChannelA", ctypes.POINTER(sdrplay_api_RxChannelParamsT)),  # Tuner A params
        ("rxChannelB", ctypes.POINTER(sdrplay_api_RxChannelParamsT))  # Tuner B params (RSPduo)
    ]


# =============================================================================
# 2.1.4 - Device Structure (str. 8)
# =============================================================================

class sdrplay_api_DeviceT(ctypes.Structure):
    """Struktura urządzenia"""
    _fields_ = [
        ("SerNo", ctypes.c_char * SDRPLAY_MAX_SER_NO_LEN),  # Serial number
        ("hwVer", ctypes.c_ubyte),  # Hardware version
        ("tuner", ctypes.c_uint),  # Tuner selection
        ("rspDuoMode", ctypes.c_uint),  # RSPduo mode
        ("valid", ctypes.c_ubyte),  # Valid flag
        ("rspDuoSampleFreq", ctypes.c_double),  # RSPduo sample freq
        ("dev", ctypes.c_ulonglong)  # Device handle (64-bit)
    ]


# =============================================================================
# 2.10.2 - Callback Structures (str. 19)
# =============================================================================

class sdrplay_api_StreamCbParamsT(ctypes.Structure):
    """Parametry callback streamu"""
    _fields_ = [
        ("firstSampleNum", ctypes.c_uint),  # First sample number
        ("grChanged", ctypes.c_int),  # Gain reduction changed flag
        ("rfChanged", ctypes.c_int),  # RF frequency changed flag
        ("fsChanged", ctypes.c_int),  # Sample rate changed flag
        ("numSamples", ctypes.c_uint)  # Number of samples
    ]


# =============================================================================
# 2.10.3 - Callback Function Prototypes (str. 19)
# =============================================================================

# WAŻNE: Windows używa __stdcall (WINFUNCTYPE), Linux/Mac używa __cdecl (CFUNCTYPE)
if sys.platform == 'win32':
    StreamCallback_t = ctypes.WINFUNCTYPE(
        None,  # Return type
        ctypes.POINTER(ctypes.c_short),  # xi (I samples)
        ctypes.POINTER(ctypes.c_short),  # xq (Q samples)
        ctypes.POINTER(sdrplay_api_StreamCbParamsT),  # params
        ctypes.c_uint,  # numSamples
        ctypes.c_uint,  # reset
        ctypes.c_void_p  # cbContext
    )

    EventCallback_t = ctypes.WINFUNCTYPE(
        None,  # Return type
        ctypes.c_uint,  # eventId
        ctypes.c_uint,  # tuner
        ctypes.c_void_p,  # params
        ctypes.c_void_p  # cbContext
    )
else:
    StreamCallback_t = ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(ctypes.c_short),
        ctypes.POINTER(ctypes.c_short),
        ctypes.POINTER(sdrplay_api_StreamCbParamsT),
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_void_p
    )

    EventCallback_t = ctypes.CFUNCTYPE(
        None,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_void_p
    )


class sdrplay_api_CallbackFnsT(ctypes.Structure):
    """Struktura funkcji callback"""
    _fields_ = [
        ("StreamACbFn", StreamCallback_t),  # Stream callback dla tunera A
        ("StreamBCbFn", StreamCallback_t),  # Stream callback dla tunera B
        ("EventCbFn", EventCallback_t)  # Event callback
    ]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_structure_info():
    """Wyświetl informacje o strukturach"""

    structures = [
        ("sdrplay_api_DeviceT", sdrplay_api_DeviceT),
        ("sdrplay_api_DeviceParamsT", sdrplay_api_DeviceParamsT),
        ("sdrplay_api_DevParamsT", sdrplay_api_DevParamsT),
        ("sdrplay_api_RxChannelParamsT", sdrplay_api_RxChannelParamsT),
        ("sdrplay_api_TunerParamsT", sdrplay_api_TunerParamsT),
        ("sdrplay_api_ControlParamsT", sdrplay_api_ControlParamsT),
        ("sdrplay_api_CallbackFnsT", sdrplay_api_CallbackFnsT)
    ]

    print("=" * 70)
    print("STRUKTURY SDRPLAY API")
    print("=" * 70)

    for name, struct in structures:
        size = ctypes.sizeof(struct)
        print(f"\n{name}:")
        print(f"  Rozmiar: {size} bajtów")
        print(f"  Pola: {len(struct._fields_)}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_structure_info()