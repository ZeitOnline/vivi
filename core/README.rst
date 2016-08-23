=================
Dynamische Ordner
=================

Das Paket ``zeit.content.dynamicfolder`` stellt den Content-Typ
``DynamicFolder`` (DAV-Typ ``dynamic-collection``) zur Verfügung, der mittels
einer Konfigurationsdatei (XML-Format siehe unten) bestimmt, was für Inhalte er
enthält. Wird so ein Ordner nach einem Kind gefragt und dieses existiert nicht
als tatsächlicher DAV-Inhalt, generiert er on-the-fly ein Content-Objekt anhand
der Angaben in der Konfigurationsdatei.


Konfigurationsdatei
===================

Die Konfigurationsdatei besteht aus zwei Teilen, ``head`` und ``body``. Der
``head`` enthält Metadaten und der ``body`` legt fest, welche virtuellen Kinder
der Ordner hat. Beispiel::

    <dynamic-cp-config>
    <head>
      <cp_template>http://xml.zeit.de/path/to/template.xml</cp_template>
    </head>
    <body key="@url">
      <entry url="one" foo="bar" baz="qux"/>
      <entry url="two" foo="zonk" baz="ping"/>
    </body>
    </dynamic-cp-config>

Jeder Kindknoten von ``<body>`` definiert ein Kind des Ordners. Der Tagname ist
unerheblich. Ein Kind wird erzeugt, indem das ``cp_template`` aus dem Connector
geladen wird und als Jinja2-Template ausgewertet wird. Als Variablen stehen dem
Template alle Attribute des Kindknotens, sowie die spezielle Variable ``text``
für den Textinhalt des Kindknotens zur Verfügung. Ebenso kann auf
``__parent__`` zugegriffen werden, um Informationen über den dynamischen Ordner
zu erhalten, zum Beispiel ``__name__``.

Da es keine Einschränkungen der XML-Struktur gibt, muss festgelegt werden,
welches Attribut des Kindknotens den Dateinamen des Kindobjekts enthält, dies
wird im Attribut ``key`` vom ``<body>``-Tag angegeben. (Im Beispiel heißt das,
der Ordner hat die Kinder ``one`` und ``two``).

Um bereits existierende Konfigurationsdateien weiterverwenden zu können,
unterstützt der ``<body>``-Tag einen Include-Mechanismus::

    <body key="@url">
      <include href="http://xml.zeit.de/data/series.xml"
       xpointer="/allseries/series"/>
    </body>

Das ``href``-Attribut wird über den Connector aufgelöst, und das
``xpointer``-Attribut enthält einen XPath-Ausdruck, welche Knoten aus dem
Zieldokument als Kinder des ``<body>`` eingefügt werden sollen.


Beispiel-Template
=================

::

    <centerpage xmlns:cp="http://namespaces.zeit.de/CMS/cp" type="centerpage">
      <head>
      </head>
     <body>
        <title>{{title}}</title>
        <cluster visible="True" area="feature" kind="solo">
          <region visible="True" hide-dupes="True" area="lead" kind="single" count="5" automatic="True" automatic_type="query">
            <container cp:type="auto-teaser" module="parquet-regular" visible="True" cp:__name__="id-167b003d-0199-4cc5-831e-c1eaac5f925c"/>
            <container cp:type="auto-teaser" module="parquet-regular" visible="True" cp:__name__="id-4a960096-2165-4f23-bdf9-c38a34655c43"/>
            <container cp:type="auto-teaser" module="parquet-regular" visible="True" cp:__name__="id-aa3d66b6-5a83-4c28-98de-78686d074a62"/>
            <container cp:type="auto-teaser" module="parquet-regular" visible="True" cp:__name__="id-13b34132-500d-41b4-b565-2e29f7f9840f"/>
            <container cp:type="auto-teaser" module="parquet-regular" visible="True" cp:__name__="id-097121c4-56ca-4171-950d-54989b5ed453"/>
            <raw_query>published:"published" AND serie:"{{serienname}}"</raw_query>
          </region>
          <region area="informatives"/>
        </cluster>
        <cluster visible="True" area="teaser-mosaic" kind="solo"/>
      </body>
    </centerpage>
