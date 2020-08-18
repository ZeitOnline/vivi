Rezepte
=======

Rezepte sind definiert als Artikel vom Ressort ZEIT Magazin und Genre "Rezept".
Rezepten können global spezielle Kategorien zugewiesen werden (Vegan,
Weihnachten, Grillen, ...).

Darüber hinaus können in den Artikeltext von Rezepten Module des Typs
"Rezeptliste" hinzugefügt werden, über die rezeptspezifische Listen von Zutaten
organisiert werden.


Rezept-Kategorien
-----------------
Rezepte können Rezeptkategorien zugeordnet werden.
Diese Kategorien werden in ``data/categories.xml`` gepflegt und stehen als
``zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist`` zur Verfügung.
Um Rezepten Kategorien zuweisen zu können, muss zunächst ein gültiges Genre
gemäss
``zeit.content.article.edit.browser.form.RecipeCategories.recipe_categories``
ausgewählt werden. Anschließend wird das Kategorien-Widget eingeblendet. Darüber
lassen sich Kategorien dem Rezeptartikel hinzufügen, sortieren und löschen.


Rezeptlisten
------------
Rezeptlisten stehen Artikeln des Ressorts ZEIT Magazin als Modul über
``zeit.content.modules.recipelist.RecipeList`` zur Verfügung. Sie können wie
gewohnt in den Artikeltext platziert und beliebig verschoben werden.
Rezeptlisten verfügen über folgende Metadaten:

**Komplexität** und **Zubereitungsdauer** sind Auswahlfelder, deren Inhalte aus
der Konfigurationsdatei ``recipe-metadata.xml`` stammen.

**Portionen** erlauben die Eingabe einer Zahl bzw. eines Umfangs (z.B. 10-12).

**Rezeptnamen** sind auf der website stets durchsuchbar und beschreiben den
Namen der Rezeptliste, z.B. "Bananen-Shake".

**Zwischenüberschriften** sind optional durchsuchbar und kategorisieren eine
Rezeptliste meist im Kontext mehrerer, z.B. "Für das Dessert" oder "Für die
Beilage".

**Sonderzutat** ist ein reines Freitextfeld ohne Validierung, das nie
durchsuchbar ist und keine Zutaten-CP erhält. Hier können Redakteure eine
besondere "Zutat" eintragen, wie z.B. "eine Extraportion Liebe" oder "drei
Einmachgläser".

**Zutaten** (siehe Zutaten).

Mehrere Rezeptlisten können darüber hinaus zu einer einzigen **zusammengeführt**
werden. Um dies zu veranlassen, steht im vivi hierzu eine Checkbox zur
Verfügung. Das eigentliche Zusammenführen geschieht dann in
``zeit.web.magazin.block.RecipeList``.


Zutaten
-------
Zutaten können über ein Type-Ahead Widget Rezeptlisten hinzugefügt werden.
Hierfür steht über ``.ingredients.IngredientsSearchURL`` ein Endpunkt
``@@ingredients_find`` zur Verfügung. Bei Anfragen an diesen Endpunkt wird via
``ingredients.Ingredients.search`` eine ``.ingredients.IngredientsSource``
durchsucht. Bei dieser handelt es sich um eine XML-Datei, die im Deployment über
``ingredients_url`` definiert ist und aus einer Liste von Zutaten besteht (siehe
``.tests/fixtures/ingredients.xml``).

Im Gegensatz zum Autoren-Widget arbeiten wir bei der Zutatensuche nicht mit
Referenzen, weshalb aus Restriktionsgründen der Formlib das Zutaten-Widget rein
über Javascript arrangiert wird. Um dennoch mit der Formlib zu sprechen bedienen
wir uns einem Mechanismus aus `z.c.tagging`. Hierbei findet die Kommunikation
zwischen der Formlib und dem Javascript über ein verstecktes Input-Field statt.
Dort werden die Zutaten-Informationen als JSON-Struktur abgelegt und von beiden
Seiten geschrieben bzw. ausgelesen.

Siehe:
``core/src/zeit/wochenmarkt/browser/widget.py``
``core/src/zeit/content/modules/recipelist.py``

Zu jeder Zutat können weitere Informationen hinterlegt werden, wie z.B. Menge,
Details, Einheit, etc. Letzteres ist ein Auswahlfeld, dessen Inhalt ebenfalls
aus der ``recipe-metadata.xml`` stammt.
