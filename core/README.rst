=======
Ausgabe
=======

Das Paket ``zeit.content.volume`` stellt den Content-Typ ``Volume`` zur
Verfügung, der Information zu einer PRINT-Ausgabe bereitstellt (z.B. Jahr,
Nummer, Coverbild). Über eine Konfigurationsdatei und Eintragungen in der
``products.xml`` können mögliche Coverbilder und die generischen Speicherorte
eingestellt werden.

Um von einem ``ICommonMetadata`` (z.B. einen Artikel) zur zugehörigen Ausgabe
zu kommen, genügt es auf ``zeit.content.volume.interfaces.IVolume`` zu
adaptieren. Um beispielsweise das Cover-Bild ``printcover`` für die Ausgabe
eines Artikels zu lesen, genügt folgender Aufruf::

    volume = zeit.content.volume.interfaces.IVolume(article)
    image = volume.covers['printcover']

Dabei wird vorausgesetzt, dass der Artikel einem Produkt zugeordnet ist, das
Ausgaben unterstützt (siehe Produkt-Source weiter unten, aktuell nur ``ZEI``)
und eine Ausgabe mit selben Jahr & Ausgabennummer existiert. Diese Ausgabe muss
außerdem an der "richtigen" Stelle im Vivi hinterlegt sein. Der genaue Ort wird
durch die Produkt-Source bestimmt (siehe unten).


Cover-Bilder
============

Die Konfigurationsdatei für Coverbilder besteht aus einer Liste von möglichen
Coverbildern. Beispiel::

    <covers>
      <cover id="portrait">Hochformat</cover>
      <cover id="landscape">Querformat</cover>
      <cover id="ipad">iPad</cover>
    </covers>

Über das Attribut ``Volume.covers`` kann auf die entsprechende ``id``
zugegriffen werden. Der Zugriff erfolg über Dict-Notation, d.h.
``volume.covers['ipad']``.

Diese werden dynamisch beim ``Volume`` angezeigt und dann direkt im XML
desselben gespeichert.

In der Produktion wird `diese Konfigurationsdatei` verwendet.


Product-Source
==============

Um ein Produkt für die Benutzung von Ausgaben freizuschalten, muss in der
``products.xml`` für das entsprechende Produkt ein Attribut ``volume="True"``
gesetzt werden.

Ausgaben zu dem Produkt müssen im Vivi in einer Ordner-Struktur hinterlegt
werden, welche dem ``location`` Attribut in der Source entspricht.

Um ein beliebiges Objekt mit dem ``ICommonMetadata``-Interface einer Ausgabe zu
zuordnen, existiert ein Adapter, der aus den bereits vorhanden Attributen
``year`` und ``volume`` die entsprechende Ausgabe errechnet. Für die
Einstellung mit dem ``location``-Attribut können ``{year}`` und ``{name}``
verwendet werden. Das letzte Element im Pfad wird als Dateiname des
Ausgabenobjektes interpretiert.

Im folgenden Beispiel werden beide Optionen ausgesteuert::

    <products>
        <product id="ZEI"
                 volume="True"
                 location="http://xml.zeit.de/{year}/{name}/ausgabe">
                 Die Zeit</product>
        <product id="ZMLB">Zeit Magazin</product>
    </products>

In Produktion ist diese `products.xml` in Benutzung.

.. _`products.xml`: http://http://cms-backend.zeit.de:9000/cms/work/data/products.xml
.. _`diese Konfigurationsdatei`: http://cms-backend.zeit.de:9000/cms/work/data/volume-covers.xml


Inhaltsverzeichnis
==================

Außerdem kann für jedes Ausgabenobjekt ein Inhaltsverzeichnis als csv
erstellt werden (über /ausgabe/@@toc.csv). Dieses Inhaltsverzeichnis
wird allerdings nicht durch Parsen der XML's im repository erzeugt, da
das IHV erstellt werden soll bevor der Print-Import Stufe 2 gelaufen ist,
sondern durch das Parsen der XML's die unter
http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv
liegen, die bereits vorher zur Verfügung stehen sollten.
Welche Produkte das Inhaltsverzeichnis umfasst, wird zurzeit über die
product config bestimmt::

    <product-config zeit.content.volume>
        toc-product-ids ZEI ZEIH
    </product-config>

Bei dieser Konfiguration umfasst das IHV dann nur "Die Zeit" und "Die Zeit
Hamburg".
Wird nun beispielsweise versucht das IHV für die Ausgabe 2016/35
zu ermitteln, werden für die Print-Ausgabe die Unterordner von
http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv/ZEI/2016/35
nach Artikeln durchsucht und diese werden dann dem IHV hinzugefügt.
