"""
Kontroler SDRplay RSP1A
Zarządza komunikacją z urządzeniem przez API
"""

import ctypes
import numpy as np
import sys
from pathlib import Path

# Dodaj root projektu do Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importy lokalne
from src.api.structures import *
from src.api.constants import *
from config.settings import HardwareConfig, ReceiverConfig


class SDRplayController:
    """
    Kontroler dla SDRplay RSP1A
    Zarządza:
    - Połączeniem z urządzeniem
    - Konfiguracją parametrów
    - Streamingiem danych I/Q
    - Callbackami
    """

    def __init__(self):
        """Inicjalizacja kontrolera"""
        self.dll = None
        self.device = None
        self.device_params = None

        # Bufory danych I/Q
        self.i_buffer = []
        self.q_buffer = []
        self.max_buffer_size = 1000000  # 1M próbek

        # Callbacki
        self.stream_cb = None
        self.stream_b_cb = None
        self.event_cb = None

        # Statystyki
        self.overload_count = 0
        self.total_samples = 0

        # Status
        self.is_streaming = False

    # =========================================================================
    # INICJALIZACJA I ZARZĄDZANIE URZĄDZENIEM
    # =========================================================================

    def find_dll(self):
        """Znajdź DLL SDRplay API w rejestrze Windows"""
        import winreg

        paths = [
            r"SOFTWARE\SDRplay\Service\API",
            r"SOFTWARE\WOW6432Node\SDRplay\Service\API"
        ]

        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                install_dir = winreg.QueryValueEx(key, "Install_Dir")[0]
                dll_path = f"{install_dir}\\x64\\sdrplay_api.dll"

                # Sprawdź czy plik istnieje
                if Path(dll_path).exists():
                    return dll_path
            except:
                continue

        # Fallback - domyślna lokalizacja
        default_path = r"C:\Program Files\SDRplay\API\x64\sdrplay_api.dll"
        if Path(default_path).exists():
            return default_path

        raise FileNotFoundError("Nie znaleziono sdrplay_api.dll!")

    def initialize(self):
        """
        Inicjalizacja API i wybór urządzenia
        Kroki 1-5 z dokumentacji (str. 32)
        """
        try:
            # KROK 1: Open API
            dll_path = self.find_dll()
            print(f"📚 Ładowanie DLL: {dll_path}")
            self.dll = ctypes.CDLL(dll_path)

            err = self.dll.sdrplay_api_Open()
            if err != ErrorCode.SUCCESS:
                raise Exception(f"sdrplay_api_Open failed: {ErrorCode.get_name(err)}")

            print("✓ API otwarte")

            # KROK 2: Lock API
            self.dll.sdrplay_api_LockDeviceApi()

            # KROK 3: GetDevices
            devices = (sdrplay_api_DeviceT * SDRPLAY_MAX_DEVICES)()
            num_devs = ctypes.c_uint()

            err = self.dll.sdrplay_api_GetDevices(
                devices,
                ctypes.byref(num_devs),
                SDRPLAY_MAX_DEVICES
            )

            if err != ErrorCode.SUCCESS:
                raise Exception(f"GetDevices failed: {ErrorCode.get_name(err)}")

            if num_devs.value == 0:
                raise Exception("Nie znaleziono urządzeń SDRplay!")

            # Znajdź RSP1A (lub użyj pierwszego dostępnego)
            device_found = False
            for i in range(num_devs.value):
                dev = devices[i]
                dev_name = DeviceID.get_name(dev.hwVer)
                print(f"  Znaleziono [{i}]: {dev.SerNo.decode()} ({dev_name})")

                # Preferuj RSP1A, ale zaakceptuj każde urządzenie
                if dev.hwVer == DeviceID.RSP1A or not device_found:
                    self.device = dev
                    device_found = True
                    if dev.hwVer == DeviceID.RSP1A:
                        break

            if not device_found:
                raise Exception("Nie znaleziono odpowiedniego urządzenia!")

            print(f"✓ Wybrano: {self.device.SerNo.decode()} ({DeviceID.get_name(self.device.hwVer)})")

            # KROK 4: SelectDevice
            self.device.tuner = TunerSelect.TUNER_A

            err = self.dll.sdrplay_api_SelectDevice(ctypes.byref(self.device))
            if err != ErrorCode.SUCCESS:
                raise Exception(f"SelectDevice failed: {ErrorCode.get_name(err)}")

            # KROK 5: Unlock API
            self.dll.sdrplay_api_UnlockDeviceApi()

            return True

        except Exception as e:
            print(f"✗ Błąd inicjalizacji: {e}")

            # Cleanup w razie błędu
            if self.dll:
                try:
                    self.dll.sdrplay_api_UnlockDeviceApi()
                    self.dll.sdrplay_api_Close()
                except:
                    pass

            return False

    # =========================================================================
    # KONFIGURACJA I START
    # =========================================================================

    def configure_and_start(self, freq_mhz=None, sr_mhz=None, gain_db=None):
        """
        Konfiguracja i uruchomienie streamingu
        Kroki 6-8 z dokumentacji (str. 32-37)

        Args:
            freq_mhz: Częstotliwość [MHz] (None = z config)
            sr_mhz: Sample rate [MHz] (None = z config)
            gain_db: Gain reduction [dB] (None = z config)
        """

        # Użyj wartości z config jeśli nie podano
        freq_mhz = freq_mhz or ReceiverConfig.CENTER_FREQ_MHZ
        sr_mhz = sr_mhz or ReceiverConfig.SAMPLE_RATE_MHZ
        gain_db = gain_db or ReceiverConfig.GAIN_REDUCTION_DB

        try:
            # KROK 6: GetDeviceParams
            print("\n📋 Konfiguracja parametrów...")

            self.dll.sdrplay_api_GetDeviceParams.restype = ctypes.c_uint
            self.dll.sdrplay_api_GetDeviceParams.argtypes = [
                ctypes.c_ulonglong,
                ctypes.POINTER(ctypes.POINTER(sdrplay_api_DeviceParamsT))
            ]

            device_params_ptr = ctypes.POINTER(sdrplay_api_DeviceParamsT)()
            err = self.dll.sdrplay_api_GetDeviceParams(
                self.device.dev,
                ctypes.byref(device_params_ptr)
            )

            if err != ErrorCode.SUCCESS:
                raise Exception(f"GetDeviceParams failed: {ErrorCode.get_name(err)}")

            self.device_params = device_params_ptr.contents

            # KROK 7: Modyfikuj parametry
            print(f"  📻 Częstotliwość: {freq_mhz} MHz")
            print(f"  📊 Sample rate:   {sr_mhz} MSPS")
            print(f"  🔧 Gain:          -{gain_db} dB (LNA state={ReceiverConfig.LNA_STATE})")

            # Parametry urządzenia
            if self.device_params.devParams:
                dev = self.device_params.devParams.contents

                # Sample rate
                dev.fsFreq.fsHz = sr_mhz * 1e6

                # Transfer mode (ISOCH dla 14-bit)
                dev.mode = TransferMode.ISOCH

                # RF Notch filters (redukcja RFI)
                dev.rsp1aParams.rfNotchEnable = 1 if ReceiverConfig.RF_NOTCH_ENABLED else 0
                dev.rsp1aParams.rfDabNotchEnable = 1 if ReceiverConfig.RF_DAB_NOTCH_ENABLED else 0

                if ReceiverConfig.RF_NOTCH_ENABLED or ReceiverConfig.RF_DAB_NOTCH_ENABLED:
                    print(f"  🔇 RF Notch:      FM={'ON' if ReceiverConfig.RF_NOTCH_ENABLED else 'OFF'}, "
                          f"DAB={'ON' if ReceiverConfig.RF_DAB_NOTCH_ENABLED else 'OFF'}")

            # Parametry tunera
            if self.device_params.rxChannelA:
                ch = self.device_params.rxChannelA.contents

                # RF Frequency
                ch.tunerParams.rfFreq.rfHz = freq_mhz * 1e6

                # Bandwidth
                ch.tunerParams.bwType = ReceiverConfig.BANDWIDTH_MHZ

                # IF Type
                if ReceiverConfig.IF_MODE == "Zero":
                    ch.tunerParams.ifType = IFType.ZERO
                elif ReceiverConfig.IF_MODE == "IF_2_048":
                    ch.tunerParams.ifType = IFType.IF_2_048
                elif ReceiverConfig.IF_MODE == "IF_1_620":
                    ch.tunerParams.ifType = IFType.IF_1_620
                elif ReceiverConfig.IF_MODE == "IF_0_450":
                    ch.tunerParams.ifType = IFType.IF_0_450
                else:
                    ch.tunerParams.ifType = IFType.ZERO  # Default

                # Gain
                ch.tunerParams.gain.gRdB = int(gain_db)
                ch.tunerParams.gain.LNAstate = ReceiverConfig.LNA_STATE
                ch.tunerParams.gain.minGr = ReceiverConfig.MIN_GAIN_REDUCTION

                # AGC
                ch.ctrlParams.agc.enable = AGCControl.AGC_CTRL_EN if ReceiverConfig.AGC_ENABLED else AGCControl.DISABLE

                # DC offset correction
                ch.ctrlParams.dcOffset.DCenable = 1 if ReceiverConfig.DC_OFFSET_ENABLED else 0
                ch.ctrlParams.dcOffset.IQenable = 1 if ReceiverConfig.IQ_IMBALANCE_ENABLED else 0

                # Bias-T (zawsze OFF - używamy zewnętrznego zasilacza)
                ch.rsp1aTunerParams.biasTEnable = 0
                print(f"  ⚡ Bias-T:        OFF (zewnętrzny zasilacz)")

            print("✓ Parametry ustawione")

            # KROK 8: Init - uruchom streaming
            print("\n▶️  Uruchamianie streamingu...")

            # Stwórz callbacki
            self._setup_callbacks()

            # Struktura callbacków
            cb_fns = sdrplay_api_CallbackFnsT()
            cb_fns.StreamACbFn = self.stream_cb
            cb_fns.StreamBCbFn = self.stream_b_cb
            cb_fns.EventCbFn = self.event_cb

            # Setup funkcji Init
            self.dll.sdrplay_api_Init.restype = ctypes.c_uint
            self.dll.sdrplay_api_Init.argtypes = [
                ctypes.c_ulonglong,
                ctypes.POINTER(sdrplay_api_CallbackFnsT),
                ctypes.c_void_p
            ]

            # Init!
            err = self.dll.sdrplay_api_Init(
                self.device.dev,
                ctypes.byref(cb_fns),
                None
            )

            if err != ErrorCode.SUCCESS:
                raise Exception(f"Init failed: {ErrorCode.get_name(err)} ({err})")

            self.is_streaming = True
            print("✓ Streaming uruchomiony!")

            return True

        except Exception as e:
            print(f"✗ Błąd konfiguracji: {e}")
            import traceback
            traceback.print_exc()
            return False

    # =========================================================================
    # CALLBACKI
    # =========================================================================

    def _setup_callbacks(self):
        """Przygotuj funkcje callback dla API"""

        def _stream_a_callback(xi, xq, params, n, reset, ctx):
            """Callback dla streamu tunera A"""

            if reset:
                # Reset bufora przy reinicjalizacji
                self.i_buffer.clear()
                self.q_buffer.clear()
                self.total_samples = 0
                return

            try:
                # Konwertuj na numpy arrays
                i_arr = np.ctypeslib.as_array(xi, shape=(n,))
                q_arr = np.ctypeslib.as_array(xq, shape=(n,))

                # Sprawdź saturację ADC
                max_i = np.max(np.abs(i_arr))
                max_q = np.max(np.abs(q_arr))

                if max_i > 8000 or max_q > 8000:
                    self.overload_count += 1
                    if self.overload_count % 100 == 0:  # Co 100 pakietów
                        print(f"⚠️  Saturacja ADC: I={max_i}, Q={max_q} (max=8191)")

                # Normalizuj do -1.0..1.0 (14-bit: -8192 do 8191)
                i_norm = i_arr.astype(np.float32) / 8192.0
                q_norm = q_arr.astype(np.float32) / 8192.0

                # Dodaj do bufora
                self.i_buffer.extend(i_norm)
                self.q_buffer.extend(q_norm)

                # Ogranicz rozmiar bufora
                if len(self.i_buffer) > self.max_buffer_size:
                    self.i_buffer = self.i_buffer[-self.max_buffer_size//2:]
                    self.q_buffer = self.q_buffer[-self.max_buffer_size//2:]

                self.total_samples += n

            except Exception as e:
                print(f"✗ Błąd w stream callback: {e}")

        def _stream_b_callback(xi, xq, params, n, reset, ctx):
            """Callback dla tunera B (nie używany dla RSP1A)"""
            pass

        def _event_callback(eid, tuner, params, ctx):
            """Callback dla eventów"""

            event_name = EventType.get_name(eid)

            if eid == EventType.POWER_OVERLOAD_CHANGE:
                print(f"⚠️  POWER OVERLOAD!")
                print(f"   Zwiększ gain reduction lub zmniejsz LNA state")

            elif eid == EventType.DEVICE_REMOVED:
                print(f"✗ Urządzenie odłączone!")
                self.is_streaming = False

            elif eid == EventType.DEVICE_FAILURE:
                print(f"✗ Awaria urządzenia!")
                self.is_streaming = False

            elif eid != EventType.GAIN_CHANGE:  # GainChange jest normalny
                print(f"ℹ️  Event: {event_name}")

        # Konwertuj na typy callback
        self.stream_cb = StreamCallback_t(_stream_a_callback)
        self.stream_b_cb = StreamCallback_t(_stream_b_callback)
        self.event_cb = EventCallback_t(_event_callback)

    # =========================================================================
    # POBIERANIE DANYCH
    # =========================================================================

    def get_samples(self, num_samples=65536):
        """
        Pobierz próbki I/Q z bufora

        Args:
            num_samples: Liczba próbek (domyślnie 65536 dla FFT)

        Returns:
            Complex numpy array (I+jQ) lub None jeśli za mało danych
        """
        if len(self.i_buffer) >= num_samples:
            i_data = np.array(self.i_buffer[-num_samples:])
            q_data = np.array(self.q_buffer[-num_samples:])
            return i_data + 1j * q_data

        return None

    def get_buffer_size(self):
        """Zwróć aktualny rozmiar bufora"""
        return len(self.i_buffer)

    def clear_buffer(self):
        """Wyczyść bufor danych"""
        self.i_buffer.clear()
        self.q_buffer.clear()
        self.total_samples = 0

    # =========================================================================
    # ZATRZYMANIE I CLEANUP
    # =========================================================================

    def stop(self):
        """Zatrzymaj streaming"""

        if not self.is_streaming:
            return

        try:
            # Setup funkcji Uninit
            self.dll.sdrplay_api_Uninit.restype = ctypes.c_uint
            self.dll.sdrplay_api_Uninit.argtypes = [ctypes.c_ulonglong]

            err = self.dll.sdrplay_api_Uninit(self.device.dev)

            if err == ErrorCode.SUCCESS:
                print("✓ Streaming zatrzymany")
                self.is_streaming = False
            else:
                print(f"⚠️  Uninit warning: {ErrorCode.get_name(err)}")

        except Exception as e:
            print(f"✗ Błąd zatrzymania: {e}")

    def close(self):
        """Zamknij połączenie i zwolnij zasoby"""

        # Zatrzymaj streaming jeśli działa
        if self.is_streaming:
            self.stop()

        # Release device
        if self.dll and self.device:
            try:
                err = self.dll.sdrplay_api_ReleaseDevice(ctypes.byref(self.device))
                if err == ErrorCode.SUCCESS:
                    print("✓ Urządzenie zwolnione")
            except Exception as e:
                print(f"⚠️  Release device warning: {e}")

        # Close API
        if self.dll:
            try:
                err = self.dll.sdrplay_api_Close()
                if err == ErrorCode.SUCCESS:
                    print("✓ API zamknięte")
            except Exception as e:
                print(f"⚠️  Close API warning: {e}")

        # Wyczyść
        self.clear_buffer()

    # =========================================================================
    # STATYSTYKI I INFO
    # =========================================================================

    def get_stats(self):
        """Zwróć statystyki działania"""
        return {
            'is_streaming': self.is_streaming,
            'buffer_size': len(self.i_buffer),
            'total_samples': self.total_samples,
            'overload_count': self.overload_count,
            'buffer_fill_percent': (len(self.i_buffer) / self.max_buffer_size) * 100
        }

    def print_stats(self):
        """Wyświetl statystyki"""
        stats = self.get_stats()

        print("\n📊 Statystyki:")
        print(f"   Streaming:     {'✓ AKTYWNY' if stats['is_streaming'] else '✗ ZATRZYMANY'}")
        print(f"   Bufor:         {stats['buffer_size']:,} próbek ({stats['buffer_fill_percent']:.1f}%)")
        print(f"   Łącznie:       {stats['total_samples']:,} próbek")
        print(f"   Przeciążenia:  {stats['overload_count']}")