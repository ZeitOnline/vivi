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


Source
======

Für den Artikel gibt es verschiedene Sourcen, die Vokabulare bereit stellen,
um Werte für bestimmte Eigenschaften des Artikels einzuschränken. Sourcen
können kontextuell sein, d.h. je nach voreingestellter Eigenschaft, können sich
zum Beispiel die Wertebereiche bestimmter Sourcen ändern.

ACHTUNG: Es gibt derzeit nur wenig Validierung bei den Sourcen. Es ist also
_leicht_ möglich fehlerhafte Konfigurationen zu speichern. Also lieber
nachfragen, wenn man nicht genau weiss, was man tut.


Artikel-Template-Source
-----------------------

Diese Source definiert gültige Werte für ``article.template`` und
``article.header_layout``. Darüber hinaus kann hier eingestellt werden, welcher
Content-Typ (also z.B. ICMSContent) welche Default-Werte hat. Hier ist jedoch
zu beachten, dass die Spezifität nicht aufgelöst wird. Falls also in der Source
ein allgemeines und ein spezielles Interface als default konfiguriert ist, kann
man allenfalls über die XML document order beeinflussen, dass das spezielle
zuerst berücksichtigt wird.

::

    <templates>
      <template name="article">
        <title>Artikel</title>
        <header name="default" default_for="zeit.cms.section.interfaces.IZONContent">
          <title>Standard (Headline unter Bild)</title>
        </header>
        ...
      </template>
      ...
    </templates>

Das Attribut ``default_for`` ist mengenwertig (Trenner ist ein Leerzeichen).
Prinzipiell kann jedes Interface genutzt werden. Ein ``*`` gibt an, dass es als
default für alle Interfaces gelten soll. (Hier wird Spezifität berücksichtigt.)
Das Attribut kann für ``template`` aber auch für ``header`` genutzt werden.
Wobei auch hier gilt, dass eine Konfiguration auf ``header`` nicht spezieller
ist.

Image-Variant-Name-Source
-------------------------

Diese Source bestimmt die Layouts für das Hauptild des Artikels. Sie hat je
nach ``article.template`` oder ``article.header_layout`` ggfs. unterschiedliche
Wertebereiche

::

    <variant-names>
      <variant-name id="wide" default_for="*">Breit</variant-name>
      <variant-name id="original" default_for="article.default">
          Original</variant-name>
      <variant-name id="square" default_for="article.inside article.sticker">
          Square 1:1</variant-name>
      <variant-name id="templates_only" allowed='column column.vonanachb'
          default_for="column">Templates Only</variant-name>
      <variant-name id="header_vonanachb" allowed='column.vonanachb'
          default_for="column.vonanachb">Header: Von A nach B</variant-name>
      <variant-name id="zmo-only"
          available="zeit.magazin.interfaces.IZMOContent">
          ZMO Only</variant-name>
    </variant-names>

Das Attribut ``default_for`` ist wiederum mengenwertig. Hier werden gültige
Templatenamen aus der Artikel-Template-Source referenziert oder Kombinationen
aus Template und Header (``my_template.my_header``). Hier wiederum mit
``*``-Operator.

Die Wertebereiche können über die Attribute ``allowed`` und ``available``
eingeschränkt werden. ``allowed`` bezieht sich hier wiederum auf gültige
Templates oder Template/Header-Kombinationen. ``available`` bezieht sich auf
interfaces.

Falls ein default für einen ungültigen Wertebereich definiert wurde, wird
dieser nicht ausgeweretet.

Sind ``article.template`` und ``article.header_layout`` nicht gesetzt, sind
alle Layoutwerte erlaubt.
