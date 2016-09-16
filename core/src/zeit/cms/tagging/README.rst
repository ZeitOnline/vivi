Verschlagwortung
================

Alle Objekte, die ``zeit.cms.content.interfaces.ICommonMetadata``
implementieren, bieten über die Eigenschaft ``keywords`` Schlagworte an.
Dieses Paket definitiert die abstrakten APIs, konkrete Implementierungen
dazu befinden sich in `zeit.intrafind
<https://github.com/ZeitOnline/zeit.intrafind>`_ bzw. `zeit.retresco
<https://github.com/ZeitOnline/zeit.retresco>`_.


Keywords Property
-----------------

Die Eigenschaft ``keywords`` wird vom Deskriptor ``zeit.cms.tagging.tag.Tags``
an ``zeit.cms.tagging.interfaces.ITagger`` delegiert.
Beim Speichern von Schlagworten wird sichergestellt, dass Duplikate entfernt
werden und *Änderungen* gespeichert (hinzufügen, löschen, pinnen).

Üblicherweise wird beim Speichern auf eine Property der gesamte Inhalt
überschrieben -- Schlagworte, die nicht verändert wurden, werden allerdings
_nicht_ angefasst, um nicht ausversehen Metadaten zu "vergessen", die von der
Schlagwort-Mechanik nicht gelesen werden.


Speicherung der Schlagworte
---------------------------

Die Informationen zu Schlagworten werden unter dem Namespace
``http://namespaces.zeit.de/CMS/tagging`` in DAV-Properties gespeichert
(``rankedTags`, ``disabled`` und ``pinned``). Da insbesondere ``disabled`` und
``pinned`` nur intern für die Schlagwort-Mechanik verwendet werden, wird
explizit vermieden, dass diese DAV-Properties ins XML übertragen werden (siehe
``zeit.cms.tagging.tag.veto_tagging_properties``).

Die Schlagworte selbst (``rankedTags``) werden der Vollständigkeit halber /
fürs XSLT beim Checkin explizit ins XML geschrieben
(siehe ``zeit.cms.tagging.tag.add_ranked_tags_to_head``).


Type-Ahead Widget
-----------------

Das ``zeit.cms.tagging.browser.widget.Widget`` zum Schlagworte manipulieren
(hinzufügen, löschen, pinnen) funktioniert konzeptionell wie das
``zeit.cms.browser.widget.DropObjectWidget``, d.h. einzelne Schlagworte werden
als ``ICMSContent`` referenziert (also müssen Schlagworte sich per ``uniqueId``
auflösen lassen, als URL traversierbar sein und eine ``@@object-details``
Vorschau anbieten).

Das Widget schlägt dem Benutzer bei der Eingabe Schlagworte vor (Type-Ahead);
die Vorschläge werden über ``zeit.cms.tagging.interfaces.IWhitelist`` gewonnen.
