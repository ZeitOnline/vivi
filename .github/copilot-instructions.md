# Projektspezifische Copilot-Anweisungen

## Projekt starten
- Nutze folgende Informationen, um das Projekt lokal zu starten und auszuführen.
- Dieses Repo ist das Code-Repo für das CMS. Das Deployment-Repo liegt in drei Ordnern darüber `cd ../../../`
- Das Code-Repo `vivi` liegt damit im Deployment-Repo `vivi-deployment`. Vom Deployment-Repo aus gesehen liegt das Code-Repo in `./work/source/vivi`
- Finde zunächst immer den absoluten Pfad des Deployment-Repos heraus mit `pwd`. Nutze dann am besten absolute Pfade, falls neue Terminals gestartet werden.
- Im Deployment-Repo gibt es einen Supervisor. Dieser lässt alle wichtigen Programme des CMS laufen. `bin/sv status` zeigt alle Programme, die gerade laufen
- `bin/sv stop zope` stoppt den Hauptprozess des CMS, die Zope Instanz oder vom Code-Repo aus gesehen `../../../bin/sv stop zope`
- `bin/sv start zope` startet man den Hauptprozess des CMS wieder oder vom Code-Repo aus gesehen `../../../bin/sv start zope`
- Wenn man eine Umgebung starten möchte, die sich mit der Staging oder Produktionsdatenbank verbindet, sollte man zuvor den Zope Prozess stoppen, sofern er läuft.
- Mit `bin/serve staging` startet man eine Instanz, die sich mit der Staging-Datenbank des CMS verbindet. Oder vom Code-Repo aus gesehen `../../../bin/serve staging`
- Mit `bin/serve production` startet man eine Instanz, die sich mit der Staging-Datenbank des CMS verbindet. Oder vom Code-Repo aus gesehen `../../../bin/serve production`

## Tests
- Alle tests kann man im Deployment Repo mit `bin/test` ausführen.
- Tests sind mit pytest geschrieben.
- mit `-k` kann man Keyword angeben, die gezielt bestimmte Tests aufrufen

## Terminal-Verhalten
- Kombiniere zusammenhängende Terminal-Befehle in einem einzigen Aufruf, um Terminal-Fragmentierung zu vermeiden
- Beispiel: `cd ../../../ && bin/sv status && bin/sv stop zope && bin/serve staging` statt einzelne Befehle
- Verwende absolute Pfade oder explizite Verzeichniswechsel, da das Arbeitsverzeichnis zwischen verschiedenen Tool-Aufrufen variieren kann

