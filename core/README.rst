======================================
zeit.edit: Objektzugriff auf XML-Bäume
======================================

`Centerpages`_ haben eine dreistufige Struktur: Sie haben mehrere Regionen, die
Flächen enthalten, und diese enthalten Module (typische Module: Teaser,
Markdown, ...). Bei `Artikeln`_ ist die Struktur nur einstufig: der Body
enthält Module (Absatz, Bild, ...).

.. _`Centerpages`: https://github.com/zeitonline/zeit.content.cp
.. _`Artikeln`: https://github.com/zeitonline/zeit.content.article

Im XML wird diese Struktur durch verschachtelte Knoten abgebildet::

    <region cp:__name__="id-1" kind="solo">
      <area cp:__name__="id-2" kind="major">
        <module cp:type="teaser" module="zon-large" cp:__name__="id-3">
          <block href="http://xml.zeit.de/testcontent" />
        </module>
      </area>
    </region>

(Anmerkung: Bei Centerpages sind die Namen im XML aus bw-compat Gründen leider
aktuell nicht ganz passend, dort heißt Region: ``cluster``, Fläche: ``region``
und Modul: ``container``)

In Python wird die Struktur durch ``IContainer`` und ``IBlock`` (XXX das sollte
``IModule`` heißen) abgebildet. Beides sind ``IElement``. ``IContainer`` sind
dict-like Objekte, die andere Elemente enthalten, als Keys werden synthetische
IDs benutzt (fürs vivi-UI definiert zeit.edit noch ``IArea``, das ist ein
Container, der Module enthält. XXX Terminologie überschneidet sich mit IArea
bei CPs). Diese Objekte sind zuständig für einen Ausschnitt aus dem XML-Baums
des Content-Objekts, ihre Methoden und Attribute lesen und schreiben direkt
dort hinein.


Implementierung IElement
========================

Zu einem Element gehören zwei grundsätzliche Angaben:

a. Sein ``type``. Man muss ja den XML-Knoten irgendwie zuordnen können, welche
   Element-Klasse dafür zuständig ist. Beispielsweise wird bei Modulen in CPs
   der ``type`` als Attribut ``cp:type`` auf den Knoten geschrieben (z.B.
   ``<container cp:type="quiz" id="42"/>``), in Artikeln ist der Tag-Name der
   ``type`` (z.B. ``<quiz id="42"/>``)
b. In welchen Flächen (``IContainer``) es vorkommen kann.

Ein Element muss außerdem zwei Operationen unterstützen, wie man es erzeugen
kann:

1. Beim Lesen, d.h. wenn der zugehörige XML-Knoten bereits existiert (das
   passiert z.B., wenn man in einem Container per getitem zugreift).
2. Beim Schreiben, d.h. wenn man ein neues Element erzeugt, zu dem es noch kein
   XML gibt.

Operation 1 wird dadurch implementiert, dass man die Element-Klasse als
benannten Adapter registriert, von ``(IContainer, IObjectified)`` zu
``IElement``, mit dem ``type`` als Namen des Adapters (für Angabe b nimmt man
das konkrete Interface der Fläche statt allgemein ``IContainer``).

Für Operation 2 registriert man einen Adapter von ``IContainer`` auf
``IElementFactory``, ebenfalls mit dem ``type`` als Namen des Adapters. Dieser
muss einen geeigneten XML-Knoten erzeugen, ruft damit Operation 1 auf und fügt
das resultierende Element-Objekt (an dem der neu erzeugte XML-Knoten hängt) dem
Container hinzu.

Für all diese Dinge stellt ``zeit.edit`` Basisklassen bereit, die mit Hilfe von
`grok`_ automatisch die nötigen Registrierungen vornehmen. Hier ein Beispiel,
wie man ein Modul damit implementiert::

    class IHelloModule(zope.interface.Interface):

        greeting = zope.schema.TextLine()


    class HelloModule(zeit.edit.block.SimpleElement):

        area = IMyArea
        grok.implements(IHelloModule)
        type = 'hello'

        greeting = ObjectPathProperty('.', 'greeting', IHelloModule['greeting'])


    class Factory(zeit.edit.block.TypeOnAttributeElementFactory):

        grok.context(IMyArea)
        produces = HelloModule
        title = _('Hello module')


.. _`grok`: https://pypi.python.org/pypi/grokcore.component

(Typischerweise macht sich jeder Content-Typ eigene Basisklassen für Element
und ElementFactory, die schonmal die Content-Typ-spezifischen Dinge abhandeln,
wie z.B. welche Area gemeint ist.)


UI-Aufbau
=========

Die Baum-Struktur findet sich auch im vivi-UI wieder, dort wird sie mit Hilfe
von rekursiven Views sowie Viewlets umgesetzt (siehe :doc:`../zope/views`).

Einstieg ist der View ``@@edit.html`` für das jeweilige Content-Objekt. Dieser
View rendert nur ein div-Skelett und aktiviert dadurch Javascript, das per XHR
den View ``@@contents`` auf dem Content-Objekt aufruft, und das Ergebnis in den
passenden div einfügt.

Die Default-Implementierung von ``@@contents`` sammelt alle Viewlets für
``zeit.edit.interfaces.IContentViewletManager`` (``name="zeit.edit.contents"``)
ein und gibt diese aus.

Für ``IContainer`` gibt es ein Viewlet (das zu ``IContentViewletManager``
gehört, also für ``container/@@contents`` gerendert wird, und zu allem
Überfluss aber selbst auch ``contents`` heißt), dort wird ``for item in
context.values()`` der ``@@contents`` View gerendert. Sprich: Der
``@@contents`` eines Containers sind nacheinander die ``@@contents`` seiner
Kinder.

Für ``IBlock`` gibt es ein Viewlet, das eine Kopfleiste rendert; darin wird ein
weiterer Viewlet-Manager ausgespielt
(``zeit.edit.interfaces.IEditBarViewletManager``), sodass man flexibel Knöpfe
etc. für verschiedene Module anzeigen kann.

Durch den rekursiven Aufbau können dann per XHR gezielt Teile vom Server neu
geladen werden, wenn sie bearbeitet wurden, z.B. nur das eine Modul, wenn sein
Inhalt editiert wurde, oder nur die eine Fläche, wenn ein neues Modul
hinzugefügt wurde.
