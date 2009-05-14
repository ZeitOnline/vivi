# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component.zcml
import zope.configuration.fields
import zope.interface
import zope.security.metaconfigure


class ICPExtrasDirective(zope.interface.Interface):

    module = zope.configuration.fields.GlobalObject(
        title=u"Module containing cpextras")


def cpextras_directive(_context, module):
    """automatically does


  <class class=".cpextra.CPExtraBlock">
    <require
      interface="..interfaces.ICPExtraBlock"
      permission="zope.View" />
    <require
      set_schema="..interfaces.ICPExtraBlock"
      permission="zeit.EditContent"/>
  </class>
  <adapter factory=".cpextra.MostreadFactory" name="mostread" />
  <adapter
    provides="..interfaces.IBlock"
    name="mostread"
    factory=".cpextra.MostreadBlock"
    />

    """
    for class_, factory, name in module.cp_extras:
        cd = zope.security.metaconfigure.ClassDirective(_context, class_)
        cd.require(_context,
                   permission='zope.View',
                   interface=[zeit.content.cp.interfaces.ICPExtraBlock])
        cd.require(_context,
                   permission='zeit.EditContent',
                   set_schema=[zeit.content.cp.interfaces.ICPExtraBlock])
        zope.component.zcml.adapter(
            _context,
            factory=[class_],
            provides=zeit.content.cp.interfaces.IBlock,
            name=unicode(name))
        zope.component.zcml.adapter(
            _context,
            factory=[factory],
            name=unicode(name))
