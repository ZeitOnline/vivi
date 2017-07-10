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
