==================
Anbindung Retresco
==================

.. image:: https://github.com/zeitonline/zeit.retresco/blob/master/architecture.png
    :alt: Architecture Overview
    :width: 700
    :align: center
.. source file: ./architecture.graphml <https://www.yworks.com/downloads#yEd>

Das Retresco Themenseiten-Management-System (`TMS`_) besteht aus Elasticsearch
und einer in Python implementierten HTTP/REST-API und bietet unter anderem
folgende Funktionen:

.. _`TMS`: http://www.retresco.de/automatisierung/themenseiten-management-system

* Zu einem Text Schlagworte bestimmen (inkl. Typen wie Person/Ort/etc.)
* Artikel aus div. Kriterien zu Themenseiten zusammenstellen
* Text mit Links zu Themenseiten anreichern


Verschlagwortung
================

vivi bietet folgende Funktionen:

* Schlagworte generieren lassen
* Schlagwort hinzufügen (Autocomplete aus Liste)
* Schlagwort entfernen (kommt auch durch Generieren nicht wieder)
* Schlagwort festpinnen (wird durch Generieren nicht entfernt)
* Schagworte anordnen

Die API dafür ist ``zeit.cms.tagging.interfaces.ITagger(ICMSContent)``, von der
Idee her ein OrderedDict von ``ITag``-Objekten, mit den folgenden Eigenschaften:

:code: Interne ID (um Homonyme unterscheiden zu können, z.B. "Offenbach" Person vs. Ort)
:label: Schlagwort
:url_value: URL-safe Normalisierung von `label`
:entity_type: person, location, etc.

Aus Gründen der Effizienz und Abwärtskompatibilität wird für den ``code`` eines
Schlagworts nicht die ``entity_id`` aus dem TMS verwendet, sondern der ``code``
wird aus ``label`` und ``entity_type`` generiert. Dadurch kann ein Schlagwort
direkt aus dem ``code`` erzeugt werden, anstatt die ID über einen HTTP Request
im TMS nachzuschlagen.

Der ``url_value`` ist hier nur aus historischen Gründen implementiert, da die
Eigenschaft von ``ITag`` erwartet wird. ``url_value`` wird zurzeit im Friedbert
verwendet, um Links auf Themenseiten zu erstellen. In Zukunft werden dafür
jedoch TMS-Themenseiten verwendet (siehe `Themenseiten`_).


Schlagworte generieren lassen
-----------------------------

Mit ``ITagger.update()`` wird der Content ans TMS geschickt, um ihn nach
Schlagworten analysieren zu lassen (``POST /content/enrich``); das
Ergebnis wird als XML serialisiert und in einer DAV-Property gespeichert.

Für gepinnte sowie entfernte Schlagworte werden die IDs in weiteren
DAV-Properties gespeichert, und das Ergebnis von ``ITagger.update()`` wird von
vivi entsprechend nachverarbeitet.


Schlagworte hinzufügen
----------------------

Um ein Schlagwort manuell hinzuzufügen, bietet das TMS eine Type-Ahead API
(``GET /entities?q=&entity_type=``).
Diese kann über ``zeit.retresco.connection.TMS.get_keywords(term)``
angesprochen werden. Zur Abstraktion wird der Zugriff jedoch über
``zeit.cms.tagging.interfaces.IWhitelist.search(term)`` gekapselt.


Abwärtskompatibilität
---------------------

Schlagworte, die mit ``zeit.intrafind`` angelegt wurden, können nach wie vor
gelesen und gepinnt werden. Es ist jedoch nicht möglich sie erneut
hinzuzufügen, da Retresco eine unabhängige Menge von Schlagworten verwaltet.
Gegebenenfalls kann also nicht dasselbe, aber ein gleichnamiges Schlagwort
hinzugefügt werden. Im Gegensatz zu ``zeit.intrafind`` werden außerdem
Schlagworte, die nicht auf der Whitelist stehen, beim Type-Ahead nicht
unterstützt.

Die Abwärtskompatibilität funktioniert, weil ``zeit.retresco`` die gleiche DAV-
Property mit gleicher Syntax weiterhin benutzt, und die Eigenschaft ``code``
aus ``label`` und ``entity_type`` generiert wird, da diese Informationen sowohl
in ``zeit.intrafind`` als auch in ``zeit.retresco`` hinterlegt werden. Die
inkompatible UUID, die von ``zeit.intrafind`` als ``code`` verwendet wird, wird
dabei schlicht ignoriert.


Rückkanal
---------

Das TMS kann bei vivi eine Neuverschlagwortung von (Mengen von)
Content-Objekten auslösen (``vivi.zeit.de/@@update_keywords`` ->
``zeit.retresco.json.update``), wenn dort Einstellungen geändert wurden, die
entsprechende Auswirkungen haben (z.B. Änderung an Schlagworten oder Regeln für
In-Text-Links). Das muss durchs vivi geführt werden, damit entfernte/gepinnte
Schlagworte erhalten bleiben, weil dieses Feature rein vivi-seitig
implementiert ist.


Themenseiten
============

Für Themenseiten wird ein `zeit.content.dynamicfolder`_ angelegt, dessen
Template eine CP mit Autofläche mit einer TMS-Abfrage für die jeweilige
Themenseite erzeugt. Der virtuelle Inhalt befüllt sich aus einer XML-Datei mit
allen Themenseiten; diese werden per Cronjob
(``zeit.retresco.connection.update_topiclist``) periodisch aus dem TMS
ausgelesen (``GET /topic-pages?q=*:*``).

.. _`zeit.content.dynamicfolder`: https://github.com/zeitonline/zeit.content.dynamicfolder

Um im TMS Themenseiten anlegen zu können, muss der Content dort verfügbar sein.
Dazu übergibt vivi ihn beim Einchecken zum Indizieren ans TMS (``PUT
/content/<id>``). Das TMS speichert diese Dokumente zunächst in einem
"nicht-veröffentlicht" Index (``zeit_pool``). Beim Veröffentlichen gibt der
`Publisher`_ dem TMS Bescheid (``POST /content/<id>/publish``), wodurch das
Dokument in den "veröffentlichten" Index (``zeit_publish``) kopiert wird --
erst dann ist es auf Themenseiten verfügbar.

.. _`Publisher`: https://github.com/zeitonline/zeit.publisher


In-Text-Links
=============

Das TMS kann im Artikelbody einzelne Worte mit Links versehen, die auf
entsprechend erkannte Themenseiten verlinken. Dazu lässt vivi beim Einchecken
eine Analyse durchführen (``POST /content/enrich?in-text-linked``), wo in den
Body Link-Platzhalter eingefügt werden, die in etwa so aussehen::

    <a class="rtr-entity" data-rtr-entity="FC Schalke 04" data-rtr-etype="organisation" data-rtr-id="8313c3173b1e8e0e23eeaff21eaaed17239ee97f" data-rtr-score="55.982832618" href="#">Schalke 04</a>

Diesen angereicherten Body übergibt vivi dann ans TMS zum Speichern (beim
``PUT /content/<id>``). Beim Rendern für www.zeit.de lässt Friedbert sich dann
diesen Body vom TMS geben anstatt dem aus dem veröffentlichten Content
(``GET /in-text-linked/documents/<id>/body.html``). Dieser Endpunkt gibt als
Metadaten auch noch Links zu Themenseiten zurück, die unterhalb des
Artikelbodys ausgespielt werden können.


Suche
=====

Wir nutzen den TMS-Index (Elasticsearch) gleich mit als Such-Index, sowohl für
vivi als auch www.zeit.de (jeweils gegen den passenden Index, unveröffentlicht
``zeit_pool``, veröffentlicht ``zeit_publish``).
