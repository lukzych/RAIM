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
*  **Warstwa serwera (Backend):** aplikacja w języku Python (Flask), która odpowiada za wczytywanie danych, ich wstępne przetwarzanie oraz udostępnianie ich do interfejsu użytkownika.
*  **Warstwa interfejsu (Frontend):** aplikacja działająca w przeglądarce, wykorzystująca JavaScript oraz technologię Canvas. Odpowiada za dynamiczną wizualizację i agregację sygnałów oraz obsługę wspólnego dashboardu.

