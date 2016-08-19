=======
Ausgabe
=======

Das Paket ``zeit.content.volume`` stellt den Content-Typ ``Volume`` zur
Verfügung, der Information zu einer PRINT-Ausgabe bereitstellt (z.B. Jahr,
Nummer, Coverbild). Über eine Konfigurationsdatei und Eintragungen in der
``products.xml`` können mögliche Coverbilder und die generischen Speicherorte
eingestellt werden.


Konfigurationsdatei
===================

Die Konfigurationsdatei besteht aus einer Liste von möglichen Coverbildern.
Beispiel::

    <covers>
      <cover id="portrait">Hochformat</cover>
      <cover id="landscape">Querformat</cover>
      <cover id="ipad">iPad</cover>
    </covers>

Über das Attribut ``Volume.covers`` kann auf die entsprechende ``id``
zugegriffen werden. ``volume.covers['ipad']`` und ``volume.covers.ipad`` ist
beides möglich.

Diese werden dynamisch beim ``Volume`` angezeigt und dann direkt im XML
desselben gespeichert.


products.xml
============

Um ein Produkt für die Benutzung von Ausgaben freizuschalten, muss in der
``products.xml`` für das entsprechende Produkt ein Attribut ``volume="True"``
 gesetzt werden.

Um ein beliebiges Objekt mit dem ``ICommonMetadata``-Interface einer Ausgabe
zu zuordnen, existiert ein Adapter, der aus den bereits vorhanden Attributen
``year`` und ``volume`` die entsprechende Ausgabe errechnet. Für die
Einstellung mit dem ``location``-Attribut können ``{year}`` und ``{name}``
verwendet werden.

Im folgenden Beispiel werden beide Optionen ausgesteuert::

    <products>
        <product id="ZEI"
                 volume="True"
                 location="http://xml.zeit.de/ausgabe/{year}/{name}">
                 Die Zeit</product>
        <product id="ZMLB">Zeit Magazin</product>
    </products>
