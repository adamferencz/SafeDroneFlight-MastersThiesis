## DroneFlightAssistant
### Bezpečný průzkum dronem s využitím chytrého pohybu po trajektoriích

Diplomová práce - 
VUT FIT 2022 - 
Bc. Adam Ferencz

## Stažení a příprava simulátoru AirSim
1. Stáhněte si soubor AirSimNH.zip ze stránky https://github.com/Microsoft/AirSim/releases
2. Extrahujte a spusťte AirSimNH\WindowsNoEditor\AirSimNH.exe; po jeho spuštění ho můžete opět vypnout
3. Po prvním spuštění se vytvoří v dokumentech počítače soubor settings.json
   (Například může být na cestě D:\OneDrive\Dokumenty\AirSim\settings.json)
4. Nahraďte obsah souboru obsahem z přiloženého settings.json souboru,
   to nastaví kameru do pozice třetí osoby s volným pohybem a připraví quadcoper jako simulované vozidlo
5. Po uložení aktualizovaného souboru settings.json můžete opět spustit AirSimNH.exe

## NÁVOD NA SPUŠTĚNÍ PROGRAMU
1. Vytvořte si virtuální prostředí a aktivujte ho https://pypi.org/project/virtualenv/
2. Nainstalujte potřebné kníhovny: pip install -r requirements.txt
3. Připojte Xbox kontroler
4. Zapněte program AirSimNH.exe
5. Spusťte aplikaci: python safe_flight_assistant_app.py
	
### Požadavky:
 - viz requirements.txt

### Soubory:
 - data - Nastavení vzhledu pygame-gui.
 - logs - Složka pro ukládání logů.
   - general_logs - Ukládání fotek, pokud není zapnuté logování.
   - test_users - Složka pro třídění testovacích letů, obsahuje originální logy z uživatelského testování.
   - test_user_results - Výstupní složka pro script compare_test_flights.py
 - missions - Složka pro ukládání misí.
   - test1-14-04-2022_13-51-55.json - Mise použitá při uživatelkém testování.
   - AbstractDroneModel.py - Abstraktní třída dronu.
   - AirSimDroneModel.py - Model dronu pro komunikaci se simulátorem AirSim.
   - compare_test_flights.py - Vyhodnocovací skript pro sumarizaci testování.
   - Corrector.py - Korekční modul.
   - distances.py - Pomocná knihovna pro výpočet vzdálenosti.
   - Logger.py - Třída pro logování letu.
   - Path.py - Třída reprezentující bezpečnou dráhu.
   - README.md
   - requirements.txt - Požadavky.
   - safe_flight_assistant_app.py
   - settings.json - Ukázkový soubor, jak má být nastavený AirSim.
   - Transformer.py - Třída pro transformaci mezi soustavami (prostory).
   - utils.py - Pomocné funkce.
   - vectors.py  - Pomocná knihovna pro počítání s vektory.
   - Waypoint.py - Kontrolní bod bezpeční dráhy.
