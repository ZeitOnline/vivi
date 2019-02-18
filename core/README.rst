=================
Brightcove Videos
=================

Videos und Playlisten werden im System von Brightcove verwaltet (`BC UI`_). Wir
importieren die Metadaten ins vivi, und dort können Teile davon auch bearbeitet
werden, aber Brightcove ist das Master-System.

vivi kommuniziert mit BC über die "`CMS API`_" (`API-Referenz`_), eine
REST-artige HTTP/JSON-Schnittstelle, mit dem
``zeit.brightcove.interfaces.ICMSAPI`` Utility. Die Metadaten von Videos
enthalten sog. "Custom Fields", benutzerdefinierbare Felder, die wir recht
ausführlich nutzen (z.B. für Ressort, Serie, Autorenobjektreferenzen, ...).
Dabei ist z.B. bei Ressort, Serie u.ä. zu beachten, dass der Wertebreich im
vivi von einer XML-Source bestimmt wird, während er im BC-System nochmal
separat eingestellt werden muss, und das beides zusammenpassen muss.

Das Importieren von Videos erfolgt nach dem Push-Prinzip, wir registrieren den
vivi-View ``@@update_video`` (``zeit.brightcove.json.update.Notification``) als
`Notification Subscription`_ bei BC, und dieser wird immer aufgerufen, wenn
sich an Videos in BC etwas ändert, neue hinzugefügt oder bestehende gelöscht
werden. (vivi-frontend.zeit.de hat dazu eine öffentlich erreichbare IP, Port 80
ist in der ZON-Firewall geöffnet, aber nur diese URL ist aus nicht-ZON-Netzen
verfügbar, das steuern wir im `nginx`_ aus.) Daraufhin wird ein
Taskprocessor-Job erstellt, der die Änderung ins vivi überträgt und das
zugehörige Video direkt veröffentlicht (bzw. bei Löschung zurückzieht).

Videos werden veröffentlicht, wenn sie in BC im Status "aktiv" sind, ansonsten
werden sie zurückgezogen. Außerdem gibt es ein Custom Field
`ignore_for_update`, so lange das in BC angehakt ist, werden Änderungen an
diesem Video nicht ins vivi übernommen -- genauer gesagt, der aktuell
bestehende vivi-Stand wird nicht angefasst, d.h. falls das Video aber schon
zuvor importiert wurde, bleibt das vivi-Objekt unangetastet.

Das Importieren von Playlisten erfolgt nach dem Pull-Prinzip, der
``gocept.runner``-Job ``zeit.brightcove.update2.import_playlists`` läuft alle 2
Minuten und liest alle Playlisten ins vivi ein. Diese können in vivi auch nicht
bearbeitet werden.

Beim Einchecken eines `Video-Objekts`_ werden die in vivi erfolgten Änderungen
an BC zurückgeschrieben. Video- und Playlist-Objekte werden nach dem Einchecken
automatisch veröffentlicht (eine kleine Ablauferleichterung).

Die Authentifizierung an der BC-API erfolgt mit einem Access-Token (siehe `BC
OAuth`_), das vivi-Utility erzeugt sich automatisch ein neues, wenn es kein
gültiges (mehr) hat. Wir haben bei BC zwei OAuth-Clients konfiguriert, einen
der nur Lesen darf (z.B. für Staging), und einen für Lesen+Schreiben.

.. _`BC UI`: https://videocloud.brightcove.com/
.. _`CMS API`: https://support.brightcove.com/overview-cms-api
.. _`API-Referenz`: https://brightcovelearning.github.io/Brightcove-API-References/cms-api/v1/doc/index.html
.. _`Video-Objekts`: https://github.com/zeitonline/zeit.content.video
.. _`Notification Subscription`: https://support.brightcove.com/cms-api-notifications
.. _`nginx`: https://github.com/zeitonline/vivi-deployment/blob/master/components/nginx/vivi.conf
.. _`BC OAuth`: http://docs.brightcove.com/en/video-cloud/oauth-api/getting-started/oauth-api-overview.html
