Rezepte
=======

Rezepte sind definiert als Artikel vom Genre "Rezept". Rezepten können global
spezielle Kategorien zugewiesen werden (Vegan, Weihnachten, Grillen, ...), sowie
Informationen über Zubereitungsdauer, Schwierigkeitsgrad, etc.

Darüber hinaus können in den Artikeltext von Rezepten Module des Typs
"Rezeptliste" hinzugefügt werden, über die rezeptspezifische Zutatenlisten
hinzugefügt werden.


Rezept-Kategorien
-----------------
TODO


Allgemeine Informationen
------------------------
TODO


Rezeptlisten
------------
Rezeptlisten stehen als Modul über
``zeit.content.modules.recipelist.RecipeList`` zur Verfügung.  Sie können wie
gewohnt in den Artikeltext platziert und beliebig verschoben werden.

Rezeptlisten verfügen über Metadaten wie Komplexität, Zubereitungsdauer, sowie
einen speziell für die Rezeptlisten zur Verfügung stehende Rezeptlistentitel.
Über eine Checkbox kann entschieden werden, ob der jeweilige Rezeptlistentitel
in der externen Suche auftauchen soll oder nicht. Unabhägig davon sind Zutaten
einer Rezeptliste jedoch **immer** auffindbar, selbst wenn der Titel durch die
Checkbox nicht durchsucht werden kann.

Zutaten können über ein Type-Ahead Widget Rezeptlisten hinzugefügt werden.
Hierfür steht über ``.ingredients.IngredientsSearchURL`` ein Endpunkt
``@@ingredients_find`` zur Verfügung. Bei Anfragen an diesen Endpunkt wird via
``ingredients.Ingredients.search`` eine ``.ingredients.IngredientsSource``
durchsucht. Bei dieser handelt es sich um eine XML-Datei, die im Deployment über
``ingredients_url`` definiert ist und aus einer Liste von Zutaten besteht (siehe
``.tests/fixtures/ingredients.xml``).

Jeder Zutat können weitere Informationen hinterlegt werden, wie z.B. Menge,
Einheit, etc.

Im Gegensatz zum Autoren-Widget arbeiten wir bei der Zutatensuche nicht mit
Referenzen, weshalb aus Restriktionsgründen der Formlib das Zutaten-Widget rein
über Javascript arrangiert wird. Um dennoch mit der Formlib zu sprechen bedienen
wir uns einem Mechanismus aus `z.c.tagging`. Hierbei findet die Kommunikation
zwischen der Formlib und dem Javascript über ein verstecktes Input-Field statt.
Dort werden die Zutaten-Informationen als JSON-Struktur abgelegt und von beiden
Seiten geschrieben bzw. ausgelesen.

Siehe:
core/src/zeit/wochenmarkt/browser/widget.py
core/src/zeit/content/modules/recipelist.py
