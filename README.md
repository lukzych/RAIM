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

## 3. Symulacja zaburzeń w transmisji sygnałów 

Zaimplementowano mechanizmy symulujące problemy z transmisją danych w systemach telemedycznych czasu rzeczywistego. Ze względu na drastyczne różnice w częstotliwości próbkowania poszczególnych sensorów (od 4 Hz do 700 Hz), system jest podatny na specyficzne zjawiska sieciowe.

W aplikacji zaimplementowano następujące scenariusze zaburzeń (symulowane na poziomie wątków obsługujących kolejki strumieniowe):

**1. Latencja sieciowa (Podstawowe opóźnienie transmisji)**
* **Teoria:** Latencja to czas, jaki upływa od momentu wygenerowania danych przez sensor medyczny do momentu ich fizycznego udostępnienia na interfejsie przeglądarki lekarza. W sprzęcie medycznym wynika ona m.in. z czasu potrzebnego na przetworzenie sygnału z ADC (przetwornika analogowo-cyfrowego) i zakodowanie go do transmisji bezprzewodowej.
* **Wpływ na system i implementacja:** Aplikacja symuluje narzut czasowy transmisji poprzez programowe usypianie wątków (moduł `time.sleep`). Ze względu na konieczność paczkowania bardzo gęstych danych z czujnika ECG (700 Hz - wysyłanie 70 próbek na raz), system musi poczekać na zbudowanie całego bufora.

**2. Jitter (Fluktuacje opóźnień / Zmienność opóźnienia)**
* **Teoria:** Jitter to nieregularność opóźnienia pakietów w sieci. W rzeczywistych warunkach medycznych (np. pacjent poruszający się po sali z nadajnikiem Bluetooth lub zatłoczona sieć Wi-Fi w szpitalu) pakiety danych nigdy nie docierają w idealnie równych odstępach czasu.
* **Wpływ na system i implementacja:** W kodzie zjawisko to symulowane jest za pomocą dynamicznie losowanej zmiennej (moduł `random.uniform(0.1, 0.2)`). Dodaje ona do każdej iteracji wysyłania paczki nieregularne mikro-opóźnienia (od 100 ms do 200 ms). W efekcie, po stronie interfejsu wizualnego, wykresy o najwyższej częstotliwości (ECG) docierają nierównomiernie, co powoduje wizualne "szarpanie" sygnału i testuje odporność systemu na desynchronizację w stosunku do wolniejszych sygnałów (EDA - 4 Hz).

### Instrumentacja i Pomiary
W celu monitorowania stanu systemu i wpływu symulowanych zaburzeń na stabilność przesyłu, zaimplementowano pełną instrumentację:
* **Tabela logów (Audyt):** Aplikacja automatycznie zapisuje do bazy SQLite (tabela `StreamLog`) każdy wysłany z wątku pakiet danych, jego dokładny znacznik czasowy (`timestamp`) oraz precyzyjnie zmierzoną wartość napotkanego w danej iteracji opóźnienia (`latency_ms`).
* **Automatyczne raportowanie (PDF):** Osobny, asynchroniczny wątek aplikacji (`report_thread`) odczekuje na zgromadzenie odpowiedniej próbki danych logowania, a następnie agreguje zebrane metryki. Wykorzystując bibliotekę `matplotlib`, system automatycznie rysuje wykres nakładających się na siebie opóźnień wszystkich trzech sensorów w czasie. Następnie wykres ten jest osadzany i zapisywany w wygenerowanym raporcie końcowym `report.pdf` przy użyciu biblioteki `reportlab`.