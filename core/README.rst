============
zeit.locales
============

Gebrauchsanweisung:

::

  $ cd vivi-deployment
  $ bin/i18nextract  # übersetzbare Strings aus dem Code aufsammeln

  # Deutsche Übersetzungsdatei (.po) aus Katalog (.pot) aktualisieren (z.B. mit poedit)
  # und dann übersetzen (z.B. mit poedit)
  # .po zu .mo kompilieren (macht poedit automatisch)
  $ cd work/source/zeit.locales

  # ggf. CHANGES.txt eintragen (als Marker, dass es ein Release braucht)
  $ git commit -a
  $ git push
