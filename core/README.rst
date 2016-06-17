=======
Artikel
=======

Body
====

Der Body ist der eigentliche Inhalt des Artikels. Er besteht aus Modulen (siehe
``zeit.edit``), aber nur einer einzigen Area, dem Body eben:
``zeit.content.article.edit.interfaces.IEditableBody(article)``

Auf XML-Ebene gibt es eine zusätzliche Schachtelungsebene, die ``<division>``
(eigentlich: Artikelseite), die werden von IEditableBody aber flach geklopft
und eingereiht, als ob sie normale Module wären -- bis auf die erste, die es
immer geben muss und daher nicht editierbar ist (vivi stellt beim Checkout
sicher, dass der Body mind. eine Division enthält).


Header
======

Im Kopf des Artikels werden Dinge angezeigt wie Titel, Spitzmarke, Autoren etc.
Außerdem gibt es _ein_ Header-Modul, in den allermeisten Fällen eine
Bildergruppe, kann aber auch Video, Quiz o.ä. sein.

Zum Bearbeiten ist das eine weitere Area, verfügbar als
``zeit.content.article.edit.interfaces.IHeaderArea(article)``. Zum Anzeigen in
``zeit.web`` gibt es ``IHeaderArea(article).module``, was einen einfacheren
Zugriff erlaubt. Außerdem wird dadurch ein historisch gewachsenes Datenproblem
normalisiert: Wenn das erste Modul im Body ein Bild oder Video ist (und das
Bild-Layout nicht ``float`` bzw. das Video-Layout was mit ``header`` ist),
behandeln wir es "schon immer" gesondert. Daher gibt
``IHeaderArea(article).module`` solche Module zurück (wenn nicht explizit ein
eigenes Header-Modul angelegt wurde), und ``zeit.web`` tut dann so, als wären
sie im Body nicht vorhanden.
