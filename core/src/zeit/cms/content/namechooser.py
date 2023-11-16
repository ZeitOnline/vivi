import re
import zope.container.contained
import zope.container.interfaces
import zope.exceptions.interfaces
import zope.interface


invalid_chars = re.compile(r'[^a-z0-9\-]')


@zope.interface.implementer(zope.container.interfaces.INameChooser)
class NameChooser(zope.container.contained.NameChooser):
    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        super().checkName(name, object)
        m = invalid_chars.search(name)
        if m is not None:
            raise zope.exceptions.interfaces.UserError(
                'The given name contains invalid characters.'
            )

    def chooseName(self, name, object):
        name = name.lower().replace(' ', '-')
        name = invalid_chars.sub('', name)
        return super().chooseName(name, object)
