# Alle Infos zu diesem Projekt befinden sich auf meinem Blog

https://www.michaelreitbauer.at/blog

# Unterstützte Zähler

-   [Kaifa Drehstromzähler MA309 (EVN)](#HSmartMeterEVN)
-   [Kaifa Drehstromzähler MA309MH4LAT1 (Vorarlberg)](#HSmartMeterVKW)

# <a id="HSmartMeterEVN"></a>SmartMeterEVN

Dieses Projekt ermöglicht es den Smartmeter der EVN (Netz Niederösterreich) über die Kundenschnittstelle auszulesen.
Smart Meter werden von der Netz NÖ GmbH eingebaut, auf Basis der gesetzlichen Forderungen.

## Getting Started

### Voraussetzungen Hardware

-   Passwort für die Kundenschnittstelle
    -   Alle folgenden Informationen sind aus dem Folder der EVN. (https://www.netz-noe.at/Download-(1)/Smart-Meter/218_9_SmartMeter_Kundenschnittstelle_lektoriert_14.aspx)
    -   Wenn bereits ein Smart Meter in der Kundenanlage eingebaut ist, kann hier das der Schlüssel angefordert werden: smartmeter@netz-noe.at
        -   Kundennummer oder Vertragskontonummer
        -   Zählernummer
        -   Handynummer

### Voraussetzungen Software

-   Python 3, plus Libraries (siehe "requirements.txt")
    Installation der Python Libraries:
    ```
    pip install -r requirements.txt
    ```

### Zähler Hersteller

-   Kaifa Drehstromzähler MA309

# <a id="HSmartMeterVKW"></a>SmartMeterVKW
Das Skript `SmartMeterVKW.py` ermöglicht den Zugriff auf den Vorarlberger Smartmeter vom Typ `MA309M`<sub>`H4LAT1`</sub>. Der Code könnte auch für Zähler des gleichen Typs außerhalb von Vorarlberg funktionieren.

## Getting Started

### Voraussetzungen Hardware

-   Passwort für die Kundenschnittstelle
    -   Wenn bereits ein Smart Meter in der Kundenanlage eingebaut ist, kann der Schüssel Online im [Kundenportal](https://online-services.vkw.at/powercommerce/portal/) angefordert werden.

### Voraussetzungen Software

- Auch für dieses Skript werden wieder die gleichen Requirements wie schon oben beschrieben benötigt.

#### Anpassungen

-   Es muss eine config.json Datei nach Vorlage der config.example.json Datei angelegt werden, die die nötigen Informationen erhält.
-   Statt des Hauptscripts muss nun die Datei SmartMeterVKW.py ausgeführt werden.

### Zähler Hersteller

-   Kaifa Drehstromzähler MA309M<sub>H4LAT1</sub>

# Unterstützung

Spendenlink: https://www.paypal.me/greenMikeEU

# License

This project is licensed under the GNU General Public License v3.0 License - see the LICENSE.md file for details
