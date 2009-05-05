# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component
import zope.interface


ERROR = 'error'
WARNING = 'warning'


class Break(Exception):
    pass


class Rule(object):
    def __init__(self, code):
        code = '\n'.join([line.strip() for line in code.split('\n')])
        self.code = compile(code, '<string>', 'exec')

    def apply(self, context):
        self.status = None
        self.message = None

        globs = dict(
            applicable=self.applicable,
            error_if=self.error_if,
            error_unless=self.error_unless,
            warning_if=self.warning_if,
            warning_unless=self.warning_unless,
            context=context,
        )

        defaults = ['area', 'layout', 'position', 'count',
                    'is_block', 'is_area']
        for key in defaults:
            globs[key] = None
        globs.update(zeit.content.cp.interfaces.IRuleGlobs(context))

        try:
            eval(self.code, globs)
        except Break:
            pass

        return self.status

    def applicable(self, condition):
        if not condition:
            raise Break

    def error_if(self, condition, message=None):
        if condition:
            self.status = ERROR
            self.message = message
        raise Break

    def error_unless(self, condition, message=None):
        self.error_if(not condition, message)

    def warning_if(self, condition, message=None):
        if condition:
            self.status = WARNING
            self.message = message

    def warning_unless(self, condition, message=None):
        self.warning_if(not condition, message)


@zope.component.adapter(zeit.content.cp.interfaces.IBlock)
@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs_for_block(context):
    area = context.__parent__
    globs = dict(
        is_block=True,
        layout=context.layout.id,
        area=area.__name__,
        position=area.keys().index(context.__name__) + 1,
        )
    return globs


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs_for_area(context):
    globs = dict(
        is_area=True,
        count=len(context),
        area=context.__name__
        )
    return globs
