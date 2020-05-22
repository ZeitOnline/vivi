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
Rezeptlisten stehen als Modul über ``zeit.content.modules.recipelist.RecipeList`` zur Verfügung.

Zutaten können über ein Type-Ahead Widget Rezeptlisten hinzugefügt werden.
Hierfür steht über ``.ingredients.IngredientsSearchURL`` ein Endpunkt ``@@ingredients_find`` zur Verfügung. Bei Anfragen an diesen Endpunkt wird via ``ingredients.Ingredients.search`` eine ``.ingredients.IngredientsSource`` durchsucht. Bei dieser handelt es sich um eine XML-Datei, die im Deployment über ``ingredients_url`` definiert ist und aus einer Liste von Zutaten besteht (siehe ``.tests/fixtures/ingredients.xml``).

Jeder Zutat können weitere Informationen hinterlegt werden, wie z.B. Menge, Einheit, etc.
