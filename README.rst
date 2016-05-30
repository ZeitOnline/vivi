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

Mit ``ITagger.update()`` wird der Content ans TMS geschickt, um ihn nach
Schlagworten analysieren zu lassen (``PUT /documents?enrich=true``); das
Ergebnis wird als XML serialisiert und in einer DAV-Property gespeichert.

Für gepinnte sowie entfernte Schlagworte werden die IDs in weiteren
DAV-Properties gespeichert, und das Ergebnis von ``ITagger.update()`` wird von
vivi entsprechend nachverarbeitet.


Themenseiten
============

Schlagwort-Themenseiten
-----------------------

Für Themenseiten wird ein `zeit.content.dynamicfolder`_ angelegt, dessen
Template eine CP mit Autofläche mit einer solr-query für das jeweilige
Schlagwort erzeugt. Der virtuelle Inhalt befüllt sich aus einer XML-Datei mit
allen Schlagworten; diese werden per Cronjob (XXX Code-Stelle nennen)
periodisch aus dem TMS ausgelesen (``GET /linguistic/entities``).

.. _`zeit.content.dynamicfolder`: https://github.com/zeitonline/zeit.content.dynamicfolder

NOTE: Schlagwort-Themenseiten werden von "richtigen" TMS-Themenseiten abgelöst,
sobald das Projekt so weit ist.

TMS-Themenseiten
----------------

Technisch funktionieren im TMS angelegte Themenseiten überwiegend gleich, nur
dass sie nicht mit einer solr-query, sondern einer Anfrage ans TMS arbeiten
(``GET /topic-page-documents/<id>``). Themenseiten werden per Cronjob mit
``GET /topic-pages`` ausgelesen.

Um im TMS Themenseiten anlegen zu können, muss der Content dort verfügbar sein.
Dazu übergibt vivi ihn beim Einchecken zum Indizieren ans TMS (``PUT
/documents?index=true``).


In-Text-Links
=============

Der Plan ist, In-Text-Links beim Rendern von www.zeit.de durch ``zeit.web``
einzufügen. Das hat zwei Teile, zum einen schickt man das HTML ans TMS, wo
Link-Platzhalter eingefügt werden (``PUT /documents?in_text_links=true``), die
in etwa so aussehen::

    <a class="rtr-entity" data-rtr-entity="FC Schalke 04" data-rtr-etype="organisation" data-rtr-id="8313c3173b1e8e0e23eeaff21eaaed17239ee97f" data-rtr-score="55.982832618" href="#">Schalke 04</a>

Zum anderen fragt man periodisch ein Mapping von rtr-id auf Themenseiten-URLs
ab (``GET /entities/in-text-link-whitelist``), mit dessen Hilfe man dann die
``href``-Attribute ausfüllt.


Suche
=====

Wir nutzen den TMS-Index (Elasticsearch) gleich mit als Such-Index, sowohl für
vivi als auch www.zeit.de. XXX genauer beschreiben, vor allem die
published/nicht-published Trennung.
