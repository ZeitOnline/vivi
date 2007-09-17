========
Workflow
========

Der Workflow ist statusorientiert. Ein Dokument hat allerdings mehrere den
Workflow betreffende Status. Aus Nutzersicht ergeben sich quasi parallele
Aktivitäten.


Aktivitäten
===========

Schreiben bzw. eingeben
+++++++++++++++++++++++

Bedingung
    Neues oder importiertes Dokument

Ausgang „fertig“:
    Status
        zu redigieren, zu korrigieren, zu veredeln, Bild einfügen

Ausgang „sofort veröffentlichen“
    Bedingung
        Erfordert „Eilmeldung“ bzw. „Wochenende“
    Status
        zu redigieren, zu korrigieren, zu veredeln, Bild einfügen,
        veröffentlichen

Redigieren
++++++++++

Bedingung
    Status „zu redigieren“

Ausgang „fertig“
    Status
        redigiert, veröffentlichen?


Korrigieren
+++++++++++

Bedingung
    Status „zu korrigieren“
Ausgang „fertig“:
    Status
        korrigiert


Veredeln
++++++++

Bedingung
    Status „zu veredeln“
Ausgang „fertig“:
    Status
        veredelt



Bild hinzufügen
+++++++++++++++

Bedingung
    Status „Bild hinzufügen“
Ausgang „fertig“
    Status
        Bild hinzugefügt
    


Status
======

Im Folgenden sind die Status aufgelistet. Der erste angegebene Wert ist jeweils
der Standard- bzw. Initialwert:

Redaktion
    neu / zu redigieren / redigiert

Korrektorat
    neu / zu korrigieren / korrigiert

Veredelung
    neu / zu veredeln / veredelt

Grafik
    kein Bild einfügen / Bild einfügen / Bild eingefügt

Veröffentlichung
    nicht öffentlich / öffentlich

Eilmeldung / Wochenende
    nein / ja
   

Nebenbedingungen o.Ä.:

Priorität
    1 / 2 / 3 | A / B /C (??)

Veröffentlichungsdatum, -uhrzeit
    [Wann ist es draußen sichtbar]

Löschdatum, -uhrzeit
    [Wann wird es automatisch von der öffentlichen Seite entfernt]

