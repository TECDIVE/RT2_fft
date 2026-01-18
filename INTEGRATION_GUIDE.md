# 🎯 Zalecane Wartości Integracji - Przewodnik

## Dla Różnych Celów Obserwacyjnych

---

## 📊 Szybkie Testy i Kalibracja

### 🔬 Test Systemu (100-500 integracji)
**Cel:** Sprawdzenie czy system działa poprawnie

- **Liczba integracji:** 100 - 500
- **Czas:** 10-50 sekund
- **SNR improvement:** ~10-22x
- **Zastosowanie:**
  - Pierwsza obserwacja
  - Test po zmianie konfiguracji
  - Sprawdzenie wskazówki anteny

### ⚙️ Kalibracja Wstępna (1,000-2,000)
**Cel:** Podstawowe ustawienie parametrów

- **Liczba integracji:** 1,000 - 2,000
- **Czas:** 2-3 minuty
- **SNR improvement:** ~32-45x
- **Zastosowanie:**
  - Optymalizacja gain
  - Test różnych okien FFT
  - Szybka weryfikacja sygnału

---

## 🌌 Obserwacje Naukowo-Badawcze

### 🔭 Standardowa Obserwacja (10,000-20,000)
**Cel:** Podstawowe obserwacje radioastronomiczne

- **Liczba integracji:** 10,000 - 20,000
- **Czas:** 17-33 minuty
- **SNR improvement:** ~100-141x (+40-43 dB)
- **Zastosowanie:**
  - Detekcja linii HI w Drodze Mlecznej
  - Podstawowe pomiary prędkości
  - Mapy rough scan

**Przykład:**
```python
# W GUI ustaw: 10000
# Lub w config/settings.py:
SPECTRUM_INTEGRATION_COUNT = 10000
```

### 🌟 Obserwacja Wysokiej Jakości (50,000-100,000)
**Cel:** Precyzyjne pomiary, słabe sygnały

- **Liczba integracji:** 50,000 - 100,000
- **Czas:** 1.4 - 2.8 godziny
- **SNR improvement:** ~224-316x (+47-50 dB)
- **Zastosowanie:**
  - Galaktyki z niską jasnością powierzchniową
  - Precyzyjne profile linii
  - Pomiary szerokości linii
  - Detekcja rotacji galaktyk

### 🏆 Obserwacja Profesjonalna (200,000-500,000)
**Cel:** Najwyższa jakość, bardzo słabe sygnały

- **Liczba integracji:** 200,000 - 500,000
- **Czas:** 5.6 - 14 godzin
- **SNR improvement:** ~447-707x (+53-57 dB)
- **Zastosowanie:**
  - Dalekie galaktyki (z przesunięciem dopplerowskim)
  - Chmury międzygwiazdowe o niskiej gęstości
  - Struktury filamentarne
  - Obserwacje naukowe wymagające publikacji

---

## 🎯 Specyficzne Cele

### 📐 Mapowanie 2D (Drift Scan)
**Liczba integracji na punkt:** 5,000 - 10,000

- Dla mapy 10×10 punktów → 50,000 - 100,000 łącznie
- Czas na punkt: ~8-17 minut
- Całkowity czas: ~14-28 godzin
- **Wskazówka:** Używaj skryptów automatyzujących

### 🌀 Krzywe Rotacji Galaktyk
**Liczba integracji:** 20,000 - 50,000 na pozycję

- Wiele pozycji wzdłuż galaktyki
- Precyzyjne pomiary prędkości potrzebne
- **Wymagana dokładność:** ±1 km/s

### ☁️ Chmury HI w Drodze Mlecznej
**Liczba integracji:** 30,000 - 100,000

- Wykrycie struktur wielkoskalowych
- Pomiar temperatury jasności
- Identyfikacja komponent prędkości

### 🌌 Obserwacje Ekstragalaktyczne
**Liczba integracji:** 100,000 - 1,000,000

- Galaktyki o niskiej jasności powierzchniowej
- Obiekty z dużym przesunięciem z
- Wymaga doskonałej stabilności systemu

---

## ⚡ Optymalizacja Czasu Obserwacji

### Strategia "Quick Look"
```
1. Szybki test: 500 integracji (~50s)
   ↓ (czy widzisz sygnał?)
2. Średnia jakość: 5,000 integracji (~8min)
   ↓ (czy sygnał jest wyraźny?)
3. Pełna obserwacja: 20,000+ integracji
```

### Strategia Nocna
**Dla obserwacji wielogodzinnych:**

1. **Przygotowanie (wieczór):**
   - Ustawienie anteny
   - Test 1,000 integracji
   - Start długiej integracji (100,000-200,000)

2. **Obserwacja (noc):**
   - System pracuje automatycznie
   - Monitor postępu zdalnie

3. **Zapis (rano):**
   - Zakończenie integracji
   - Automatyczny zapis (jeśli włączony)
   - Backup danych

---

## 📈 Wzrost Jakości vs Czas

| Integracje | SNR Improvement | Czas      | Jakość           | Zastosowanie              |
|-----------|----------------|-----------|------------------|---------------------------|
| 100       | 10x (+20dB)    | 10s       | ⭐               | Test                      |
| 1,000     | 32x (+30dB)    | 2min      | ⭐⭐             | Kalibracja                |
| 5,000     | 71x (+37dB)    | 8min      | ⭐⭐⭐           | Quick look                |
| 10,000    | 100x (+40dB)   | 17min     | ⭐⭐⭐⭐         | Standard                  |
| 20,000    | 141x (+43dB)   | 33min     | ⭐⭐⭐⭐⭐       | Wysoka jakość             |
| 50,000    | 224x (+47dB)   | 1.4h      | ⭐⭐⭐⭐⭐⭐     | Bardzo wysoka             |
| 100,000   | 316x (+50dB)   | 2.8h      | ⭐⭐⭐⭐⭐⭐⭐   | Profesjonalna             |
| 200,000   | 447x (+53dB)   | 5.6h      | ⭐⭐⭐⭐⭐⭐⭐⭐ | Naukowa                   |

---

## 🎓 Przykładowe Sesje Obserwacyjne

### Sesja 1: Pierwsza Obserwacja
```
Cel: Sprawdzenie systemu
Obiekt: Centrum Drogi Mlecznej
Integracje: 1,000
Czas: ~2 minuty
Rezultat: Potwierdzenie detekcji linii HI
```

### Sesja 2: Profil Linii HI
```
Cel: Pomiar profilu linii
Obiekt: M31 (Galaktyka Andromedy)
Integracje: 20,000
Czas: ~33 minuty
Rezultat: Profil z komponentami prędkości
```

### Sesja 3: Mapa 2D
```
Cel: Mapa dystrybucji HI
Obiekt: Obszar w Drodze Mlecznej
Integracje: 5,000 × 25 punktów = 125,000
Czas: ~3.5 godziny (z przerwami)
Rezultat: Mapa 5×5 punktów
```

### Sesja 4: Deep Integration
```
Cel: Detekcja słabego sygnału
Obiekt: Daleka galaktyka karłowata
Integracje: 200,000
Czas: ~5.6 godziny (nocna sesja)
Rezultat: Detekcja 3-sigma
```

---

## 💡 Wskazówki Pro

### Jak Wybrać Optymalną Liczbę?

1. **RMS szumu w pojedynczym widmie:** ~X dB
2. **Docelowy SNR:** Y dB
3. **Potrzebna poprawa:** (Y/X)²
4. **Liczba integracji:** N ≈ (Y/X)²

**Przykład:**
- RMS = 5 dB
- Chcę SNR = 50 dB
- Poprawa: (50/5)² = 100
- N ≈ 10,000 integracji

### Kiedy Zatrzymać Integrację?

✅ **Zatrzymaj gdy:**
- Sygnał jest wyraźnie widoczny
- Osiągnięto zakładany SNR
- Profil linii jest dobrze zdefiniowany

⏸️ **Kontynuuj gdy:**
- Sygnał ledwo widoczny
- Potrzebujesz lepszej rozdzielczości prędkości
- Chcesz detekcji słabych komponent

### Backup i Bezpieczeństwo

⚠️ **WAŻNE:**
- Zapisuj częściowe wyniki przy długich integracjach
- Rób backup danych po każdej sesji
- Używaj UPS przy obserwacjach >2h
- Monitoruj dostępne miejsce na dysku

---

## 📊 Kalkulator Czasu

```python
def calculate_integration_time(n_integrations, refresh_ms=100):
    """
    Oblicz szacowany czas integracji
    
    n_integrations: liczba integracji
    refresh_ms: odświeżanie w ms (domyślnie 100)
    """
    time_seconds = (n_integrations * refresh_ms) / 1000
    
    if time_seconds < 60:
        return f"{time_seconds:.0f} sekund"
    elif time_seconds < 3600:
        return f"{time_seconds/60:.1f} minut"
    else:
        return f"{time_seconds/3600:.1f} godzin"

# Przykłady:
print(calculate_integration_time(1000))      # 1.7 minut
print(calculate_integration_time(10000))     # 16.7 minut
print(calculate_integration_time(100000))    # 2.8 godzin
```

---

## 🎯 Podsumowanie - Szybki Wybór

| Mam... | To używam... |
|--------|--------------|
| 5 minut | 1,000-2,000 integracji |
| 20 minut | 10,000 integracji |
| 1 godzinę | 30,000-40,000 integracji |
| Całą noc | 100,000-200,000 integracji |
| Weekend | 500,000-1,000,000 integracji |

**Pamiętaj:** Jakość > Ilość. Lepiej 10,000 dobrych integracji niż 100,000 z niestabilnym systemem!

---

*Ostatnia aktualizacja: 18 stycznia 2026*
