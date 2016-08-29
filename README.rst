=======
VG-Wort
=======

Die `VG Wort`_ erhebt an diversen Stellen (z.B. Abgabe auf Kopiergeräte)
Abgaben für die Nutzung von urheberrechtlich geschützten Werken, und zahlt
diese an Autoren und Verlage nach diversen Schlüsseln dann aus.

.. _`VG Wort`: https://www.vgwort.de/

Das gilt auch für im Web veröffentlichte Texte; daran teilzunehmen läuft wie
folgt ab:

* Wir speichern zu jedem Artikel ein public und ein private Token, das wir von
  der VGWort bekommen.
* Wir binden auf den Artikeln auf www.zeit.de ein 1x1 großes transparentes Bild
  (Zählpixel) ein, das in seiner URL das public Token enthält. Damit zählt die
  VGWort die Anzahl der Aufrufe des Artikels.
* Wir melden über den Webservice der VGWort alle Artikel anhand ihres private
  Tokens und beanspruchen sie (und ihre Aufrufe) damit für uns. Dabei
  übertragen wir die VGWort-ID der am Artikel beteiligten Autoren (wird am
  Autorenobjekt gespeichert, siehe ``zeit.content.author``), um diese Zuordnung
  herzustellen.


Tokens
======

vivi vergibt Tokens im ``IBeforePublishEvent``. Um nicht beim Veröffentlichen
synchron auf das vgwort-System zugreifen zu müssen, speichert vivi Tokens
zwischen (in der ZODB, siehe ``zeit.vgwort.interfaces.ITokens``) und zieht per
Cronjob stündlich 100 neue Tokenpaare, wenn weniger als 10000 Tokens vorhanden
sind.

Implementierungsdetail: Da DAV keine Transaktionen unterstützt, wäre im
Fehlerfall ein Token bereits im DAV verwendet, obwohl es laut ZODB nach
Rollback noch verfügbar ist. Um das zu vermeiden, reserviert vivi das Token per
XML-RPC gegen sich selber, weil das in seiner eigenen Transaktion abläuft und
somit das Token auch bei späteren Fehlern korrekt als vergeben markiert ist.


Meldung
=======

vivi meldet per Cronjob alle 10 Minuten alle Artikel (genauergesagt:
Content mit ICommonMetadata), die

* noch nicht erfolgreich gemeldet wurden
* bereits länger als 7 Tage veröffentlicht sind

**Achtung**: Artikel, die gemeldet wurden und von der VGWort als inhaltlich
fehlerhaft zurückgewisen wurden (ein typisches Beispiel ist, sie müssen eine
Mindestanzahl an Wörtern lang sein, um meldefähig zu sein), werden **nicht**
automatisch nochmal gemeldet. Dazu muss manuell die Fehlermeldung aus dem CMS
entfernt werden (``zeit.vgwort.interfaces.IReportInfo(content).reported_error =
None``).
