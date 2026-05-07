<h1 align="center">Agregacja danych z wielu sensorów</h1>

<p align="center">
  <strong>Politechnika Gdańska</strong><br>
 <strong>Katedra Inżynierii Biomedycznej (KIB)</strong><br>
</p>
<p align="center">
  <img src="logo_PG.png" height="80">
  <img src="logo_KIB.png" height="80">
</p>

---

## Informacje o projekcie
* **Autorzy:** Łukasz Zych, Rafał Kruszewski
* **Przedmiot:** Rozwój aplikacji internetowych w medycynie
* **Rok studiów:** 3
* **Prowadzący:** dr inż. Anna Jezierska

---

## 1. Analiza potrzeb i wymagań klinicznych

### Identyfikacja problemu
Współczesna diagnostyka medyczna generuje ogromne ilości danych z różnorodnych sensorów.Głównym problemem klinicznym jest brak spójnej wizualizacji, która łączyłaby różne sygnały kardiologiczne i fizjologiczne pacjenta w czasie rzeczywistym. Surowe dane liczbowe są trudne do interpretacji bez odpowiedniej agregacji i przedstawienia ich w formie geometrycznej, która pozwala na szybką ocenę stanu pacjenta.

### Określenie użytkowników
*  **Lekarze i personel medyczny:** do monitorowania pacjentów w czasie rzeczywistym.
*  **Pacjenci:** jako prosty feedback wizualny podczas np. rehabilitacji.
*  **Analitycy danych:** do weryfikacji spójności i szukania korelacji między różnymi sygnałami.

### Analiza ryzyk
*  **Opóźnienia w przesyłaniu danych:** ryzyko wyświetlania nieaktualnych parametrów. 
*  **Brak synchronizacji między sensorami:** ryzyko, że sygnał z jednego urządzenia (np. szybsze EKG) wyprzedzi dane z drugiego sensora (np. BVP).
*  **Zablokowanie systemu (Deadlock):** ryzyko zawieszenia aplikacji przy jednoczesnym dostępie wielu sensorów do bazy. 

---

## 2. Projekt architektury systemu

System opiera się na trzech warstwach:

### Schemat architektury:
*  **Warstwa danych:** wykorzystanie bazy WESAD. Dane symulują ciągły strumień informacji z sensorów medycznych.
  - ’ECG.csv’ (Elektrokardiogram) – pomiar aktywności elektrycznej serca, wyrażony w miliwoltach (mV).
  - ’BVP.csv’ (Blood Volume Pulse / Fotopletyzmografia) – sygnał objętości krwi, odczyty z sensora optycznego wyrażone w jednostkach umownych (a.u.).
  - ’EDA.csv’ (Electrodermal Activity) – przewodnictwo skóry, wskaźnik stresu wyrażony w mikrosimensach (µS).
* **Warstwa serwera (Backend):** aplikacja w języku Python (Flask), która odpowiada za wczytywanie danych, ich wstępne przetwarzanie oraz udostępnianie ich do interfejsu użytkownika.
* **Warstwa interfejsu (Frontend):** aplikacja działająca w przeglądarce, wykorzystująca JavaScript oraz technologię Canvas. Odpowiada za dynamiczną wizualizację i agregację sygnałów oraz obsługę wspólnego dashboardu.

---

## 3. Symulacja zaburzeń w transmisji sygnałów (Etap 2)

W ramach architektury systemu zaimplementowano mechanizmy symulujące typowe problemy z transmisją danych. Ze względu na drastyczne różnice w częstotliwości próbkowania poszczególnych sensorów (od powolnego 4 Hz dla EDA do aż 700 Hz dla ECG), system musi radzić sobie z niestabilnością łącza i opóźnieniami.

Zrealizowano dwa główne scenariusze zaburzeń:

### 3.1. Jitter (Zmienna latencja)
* **Teoria:** Jitter to zmienność opóźnienia w czasie — nie samo opóźnienie, ale jego nieregularność. W systemach czasu rzeczywistego powoduje to, że pakiety danych nie przychodzą w równych odstępach czasu, co może prowadzić do nieregularnego próbkowania sygnału i utrudniać jego interpretację medyczną.
* **Implementacja w kodzie:** Zjawisko to jest symulowane przez losowe odchylenie od bazowego interwału 100 ms. Każdy wątek przed wysłaniem danych losuje dodatkowe opóźnienie i czeka inny czas między kolejnymi wysyłkami, co obrazuje logika: `time.sleep(0.1 + random_delay)`. Na wygenerowanym raporcie pomiarów jitter jest wyraźnie widoczny jako oscylacje latencji między 0.1 a 0.2 sekundy.

### 3.2. Packet Loss (Utrata pakietów)
* **Teoria:** Packet loss oznacza, że dane bezpowrotnie nie zostają dostarczone do odbiorcy (np. z powodu zakłóceń lub słabego sygnału połączenia). W systemach czasu rzeczywistego utrata pakietów powoduje chwilowe przerwy w sygnale.
* **Implementacja w kodzie:** Symulacja polega na losowym pomijaniu wysyłki paczki z 10-procentowym prawdopodobieństwem (`if random_data_loss > 0.1`). Jeśli pakiet ulega zniszczeniu, program omija instrukcję dodania danych do kolejki (`q.put`). Zmienna `offset` w bazie przesuwa się jednak dalej, więc po kilku iteracjach system znowu pokazuje dane z odpowiedniego momentu czasowego. Skutkuje to tym, że gdy sygnał ECG ominie iterację, a BVP nie, wykresy przez chwilę nie pokazują tego samego momentu (następuje chwilowa desynchronizacja). Zjawisko to jest oznaczane w logach specjalną flagą utraty: `latency_ms = -1`.

### 3.3. Instrumentacja i Raportowanie
W celu monitorowania zachowania aplikacji, wdrożono pełną instrumentację na poziomie warstwy danych:
* **Logi i pomiary:** Aplikacja na bieżąco audytuje swój stan, zapisując dane do tabeli `StreamLog` w bazie SQLite. Każda iteracja wątku otrzymuje stempel czasowy (`timestamp`) oraz zmierzoną wartość opóźnienia (`latency_ms`). Dzięki temu zdarzenia utraty pakietów są jednoznacznie rejestrowane ze znacznikiem `-1`.
* **Raport z pomiarów:** Wydzielony wątek w tle (po zebraniu próbki 100 iteracji) generuje graficzny raport z pomiarów. Przy użyciu biblioteki `matplotlib` wyrysowany zostaje wykres latencji poszczególnych sensorów. Następnie biblioteka `reportlab` automatycznie osadza ten wykres w dokumencie `report.pdf`, dopisując do niego wygenerowane bezpośrednio z poziomu kodu wnioski teoretyczne.
