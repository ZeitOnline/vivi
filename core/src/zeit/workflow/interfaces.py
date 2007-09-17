# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zc.form.field

import zeit.workflow.source


class IWorkflow(zope.interface.Interface):
    """Zeit Workflow interface.

    Currently there is only a *very* simple and static property based workflow
    implemented.

    """

    edited = zope.schema.Choice(
        title=u"Bearbeitet (Redaktion)",
        default=False,
        source=zeit.workflow.source.TriState())

    corrected = zope.schema.Choice(
        title=u"Korrigiert",
        default=False,
        source=zeit.workflow.source.TriState())

    refined = zope.schema.Choice(
        title=u"Veredelt",
        default=False,
        source=zeit.workflow.source.TriState())

    images_added = zope.schema.Choice(
        title=u"Bilder hinzugefügt (Grafik)",
        default=False,
        source=zeit.workflow.source.TriState())

    urgent = zope.schema.Bool(
        title=u"Eilmeldung / Wochenende",
        default=False)

    release_period = zc.form.field.Combination(
        (zope.schema.Datetime(title=u"Von", required=False),
         zope.schema.Datetime(title=u"Bis", required=False)),
        title=u"Veröffentlichugnszeitraum",
        description=u"Leer für keine Einschränkung",
        required=False)
