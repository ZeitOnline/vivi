=======
Ausgabe
=======

Das Paket ``zeit.content.volume`` stellt den Content-Typ ``Volume`` zur
Verfügung, der Information zu einer PRINT-Ausgabe bereitstellt (z.B. Jahr,
Nummer, beiliegende Produkte, Coverbild). Über eine Konfigurationsdatei und
Eintragungen in der ``products.xml`` können mögliche beiliegende Produkte und
Coverbilder und die generischen Speicherorte der Coverbilder eingestellt
werden.

Um von einem ``ICommonMetadata`` (z.B. einen Artikel) zur zugehörigen Ausgabe
zu kommen, genügt es auf ``zeit.content.volume.interfaces.IVolume`` zu
adaptieren. Um beispielsweise das Cover-Bild ``printcover`` für die Ausgabe
eines Artikels zu lesen, genügt folgender Aufruf::

    volume = zeit.content.volume.interfaces.IVolume(article)
    image = volume.covers['printcover']

Dabei wird vorausgesetzt, dass der Artikel einem Produkt zugeordnet ist, das
Ausgaben unterstützt (siehe Produkt-Source weiter unten) und eine Ausgabe
mit  selben Jahr & Ausgabennummer existiert. Diese Ausgabe muss außerdem an
der "richtigen" Stelle im Vivi hinterlegt sein. Der genaue Ort wird durch
die Produkt-Source bestimmt (siehe unten).


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

In der Produktion wird `diese Konfigurationsdatei`_ verwendet.

.. _`diese Konfigurationsdatei`: http://cms-backend.zeit.de:9000/cms/work/data/volume-covers.xml


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

Inhaltsverzeichnis
==================

Außerdem kann für jedes Ausgabenobjekt ein Inhaltsverzeichnis als csv
erstellt werden (über /ausgabe/@@toc.csv). Dieses Inhaltsverzeichnis
wird allerdings nicht durch Parsen der XML's im repository erzeugt, da
das IHV erstellt werden soll noch bevor der Print-Import Stufe 2 gelaufen
ist. Der Print-Import Stufe 1, der bereits gelaufen sein sollte, sorgt
dafür, dass die XML's unter
http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv-in
liegen. Diese werden benutzt, um das Inhaltsverzeichnis zu erstellen.
Welche Produkte das Inhaltsverzeichnis umfasst, wird zurzeit über die
product config bestimmt::

    <product-config zeit.content.volume>
        toc-product-ids ZEI ZEIH
    </product-config>

Bei dieser Konfiguration umfasst das IHV dann nur "Die Zeit" und "Die Zeit
Hamburg".
Wird nun beispielsweise versucht das IHV für die Ausgabe 2016/35
zu ermitteln, werden für die Print-Ausgabe die Unterordner von
http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv-in/ZEI/2016/35
und
http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv-in/ZEIH/2016/35
nach Artikeln durchsucht und diese werden dann dem IHV hinzugefügt.

Ausgabenseite
=============

Nicht alle Produkte haben öffentlich sichtbare Ausgaben, bzw. diese Ansichten
sind teilweise unterschiedlich organisiert. Daher gibt es in zeit.web keinen
View für Ausgabenobjekte, sondern zu diesem Zweck kann ein eigenes
Content-Objekt, die sog. "Ausgabenseite" (typischerweise eine `Centerpage`_)
angelegt werden. Dieser Zusammenhang wird in der ``products.xml`` als
``centerpage`` eingestellt::

    <product
      id="ZEI"
      volume="True"
      location="http://xml.zeit.de/{year}/{name}/ausgabe"
      centerpage="http://xml.zeit.de/{year}/{name}/index">
      Die Zeit</product>

Dadurch kann man die CP auffinden, indem man das Ausgabenobjekt auf
``zeit.content.cp.interfaces.ICenterPage(volume)`` adaptiert.

Die Ausgabenseite kann automatisch erzeugt werden, wenn ein Ausgabenobjekt
erstellt wird. Dazu gibt man mit ``cp_template`` ein Template-Skript an, was
dann ausgeführt wird, um das Objekt zu erzeugen. Das Objekt wird dann an die
von ``centerpage`` beschriebenen Stelle gelegt::

    <product
      id="ZEI"
      volume="True"
      centerpage="http://xml.zeit.de/{year}/{name}/index">
      cp_template="http://xml.zeit.de/data/ausgabe-ZEI.py"
      Die Zeit</product>

Das Ausgabenobjekt wird an das Skript im ``context``-dict unter dem Namen
``volume`` übergeben, und muss das erzeugte Objekt mit Hilfe der Hilfsfunktion
``__return`` zurückgeben (siehe ``zeit.content.text.interfaces.IPythonScript``).
Ein minimaler Inhalt für so ein Skript könnte z.B. so aussehen (in Produktion
ist es natürlich `umfangreicher`_)::

    import zeit.content.cp.centerpage
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.year = context['volume'].year
    cp.volume = context['volume'].volume
    __return(cp)

.. _`Centerpage`: https://github.com/zeitonline/zeit.content.cp
.. _`umfangreicher`: http://cms-backend.zeit.de:9000/cms/work/data/ausgabe-ZEI.py

Beiliegende Produkte des Ausgabenobjekts
========================================
Für Produkte die Ausgaben unterstützen können mittels der products.xml auch
zusätzliche beiliegende Produkte definiert werden. Dies geschieht mittels
des Attributes 'relates_to', dessen Wert eine andere Product-ID sein muss.
Will man beispielsweise ausdrücken, dass das Zeit Magazin eine Beilage von
DIE ZEIT ist, schreibt man in die products.xml::

    <products>
        <product id="ZEI"
                 volume="True"
                 location="http://xml.zeit.de/{year}/{name}/ausgabe">
                 centerpage="http://xml.zeit.de/{year}/{name}/index">
                 cp_template="http://xml.zeit.de/data/ausgabe-ZEI.py"
                 Die Zeit</product>
        <product id="ZMLB"
                 relates_to="ZEI">
                  Zeit Magazin</product>
    </products>

Man kann das Produkt des Ausgabenobjekts fragen, welche potentiellen
Beilagen es hat. Für obige Konfiguration sieht das dann so aus::

    >>> volume.product.title
    u'Die Zeit'
    >>> volume.product.dependent_products
    [<zeit.cms.content.sources.Product object at 0x7fee6a2363d0>]
    >>> volume.product.dependent_products[0].title
    u'Zeit Magazin'

Content der gleichen Print Ausgabe adaptiert dann auch zum gleichen
Ausgabenobjekt::

    >>> zmlb_content.product.title
    u'Zeit Magazin'
    >>> zei_content.product.title
    u'Die Zeit'
    >>> IVolume(zei_content) == IVolume(zmlb_content)
    True

Achtung: Nicht möglich ist, dass beim Anlegen eines
Ausgabenobjekt unterschieden wird, ob ein konkretes Ausgabenobjekt
tatsächlich eine bestimmte Beilage hatte. Beispielsweise ist die Beilage
"Zeit Doktor" nicht bei jeder Ausgabe von DIE ZEIT dabei, taucht aber bei
den dependent_products des Produkts der Ausgabe immer auf, da dies allein
über die products.xml definiert wird. Da das für unsere Anwendung bis jetzt
aber egal ist, bleibt das erstmal so.