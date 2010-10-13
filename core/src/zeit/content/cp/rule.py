# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.POSException
import gocept.cache.method
import itertools
import logging
import urllib2
import zeit.cms.workflow.interfaces
import zeit.content.cp.interfaces
import zeit.workflow.timebased
import zope.app.appsetup.product
import zope.component
import zope.interface


log = logging.getLogger(__name__)


ERROR = 'error'
WARNING = 'warning'


class Break(Exception):
    pass


class Status(object):

    status = None
    message = None


class Rule(object):

    def __init__(self, code, line=None):
        self.code = compile(code, '<string>', 'exec')
        self.line = line

    def apply(self, context):
        status = Status()

        globs = zeit.content.cp.interfaces.IRuleGlobs(context)
        globs.update(
            applicable=self.applicable,
            error_if=lambda *args: self.error_if(status, *args),
            error_unless=lambda *args: self.error_unless(status, *args),
            warning_if=lambda *args: self.warning_if(status, *args),
            warning_unless=lambda *args: self.warning_unless(status, *args),
            context=context,
        )

        try:
            eval(self.code, globs)
        except Break:
            pass
        except ZODB.POSException.ConflictError:
            raise
        except:
            globs['uniqueId'] = zeit.content.cp.interfaces.ICenterPage(
                context).uniqueId
            log.error('Error while evaluating rule starting line %s\n'
                      'Globals=%s' %
                      (self.line if self.line else '<unknown>', globs),
                      exc_info=True)

        return status

    def applicable(self, condition):
        if not condition:
            raise Break

    def error_if(self, status, condition, message=None):
        if condition:
            status.status = ERROR
            status.message = message
        raise Break

    def error_unless(self, status, condition, message=None):
        self.error_if(status, not condition, message)

    def warning_if(self, status, condition, message=None):
        if condition:
            status.status = WARNING
            status.message = message

    def warning_unless(self, status, condition, message=None):
        self.warning_if(status, not condition, message)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.content.cp.interfaces.IRuleGlobs)
def globs(context):
    globs = {}
    for name, adapter in zope.component.getAdapters(
        (context,), zeit.content.cp.interfaces.IRuleGlob):
        if not name:
            continue
        globs[name] = adapter
    return globs


_globs = []


def glob(adapts):
    """Decorator that creates an entry in the rule globs.

    The name for the glob is the decorated function's name.
    The glob applies for objects with the interface given in `adapts`.

    The globs created here can be registered by the <globs/>-Directive in
    zcml.py
    """
    def decorate(func):
        _globs.append((func, adapts))
        return func
    return decorate


@glob(zeit.edit.interfaces.IElement)
def position(context):
    return context.__parent__.keys().index(context.__name__) + 1


@glob(zeit.edit.interfaces.IElement)
def area(context):
    return zeit.edit.interfaces.IArea(context).__name__


@glob(zeit.content.cp.interfaces.IBlock)
def type(context):
    return context.type


@glob(zeit.content.cp.interfaces.IBlock)
def is_block(context):
    return True


@glob(zope.interface.Interface)
def is_block(context):
    return False


@glob(zeit.edit.interfaces.IArea)
def is_area(context):
    return True


@glob(zope.interface.Interface)
def is_area(context):
    return False


@glob(zope.interface.Interface)
def is_region(context):
    return False


@glob(zeit.content.cp.interfaces.IRegion)
def is_region(context):
    return True


@glob(zeit.edit.interfaces.IContainer)
def count(context):
    return len(context)


@glob(zeit.content.cp.interfaces.ITeaserBlock)
def layout(context):
    return context.layout.id


@glob(zeit.content.cp.interfaces.ITeaserBar)
def layout(context):
    return context.layout.id


@glob(zeit.content.cp.interfaces.IBlock)
def content(context):
    return list(
        zeit.content.cp.interfaces.ICMSContentIterable(context, []))


@glob(zope.interface.Interface)
def cp_type(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return None
    return cp.type


@glob(zope.interface.Interface)
def is_published(context):
    def is_published_inner(obj):
        pi = zeit.cms.workflow.interfaces.IPublishInfo(obj, None)
        return pi is not None and pi.published
    return is_published_inner


class RulesManager(object):

    zope.interface.implements(zeit.content.cp.interfaces.IRulesManager)

    def __init__(self):
        self._rules = []

    @gocept.cache.method.Memoize(360)
    def get_rules(self):
        rules = []
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        url = config['rules-url']
        file_rules = urllib2.urlopen(url)
        log.info('Loading rules from %s' % url)
        noop = True
        rule = []
        start_line = 0
        for line_no, line in enumerate(file_rules):
            line = unicode(line, 'utf-8')
            if line.startswith('applicable') and noop:
                # start a new rule
                if rule:
                    rules.append(self.create_rule(rule, start_line))
                rule = []
                start_line = line_no
            noop = line.strip().startswith('#') or not line.strip()
            if not noop:
                rule.append(line)
        if rule:
            rules.append(self.create_rule(rule, start_line))
        file_rules.close()
        return rules

    def create_rule(self, commands, line_no):
        code = '\n'.join(commands)
        compile(code, '<string>', 'exec') # syntax check
        rule = Rule(code, line_no + 1)
        return rule

    @property
    def rules(self):
        try:
            self._rules = self.get_rules()
        except SyntaxError, e:
            # return the previously cached rules unmodified
            log.exception(e)
        return self._rules


class Validator(object):

    zope.interface.implements(zeit.content.cp.interfaces.IValidator)
    zope.component.adapts(zeit.edit.interfaces.IElement)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        rm = zope.component.getUtility(
            zeit.content.cp.interfaces.IRulesManager)
        for rule in rm.rules:
            status = rule.apply(context)
            if status.status and self.status != ERROR:
                self.status = status.status
            if status.message:
                self.messages.append(status.message)


class CenterPageValidator(object):

    zope.interface.implements(zeit.content.cp.interfaces.IValidator)
    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        areas = context.values()
        for item in itertools.chain(areas, *[a.values() for a in areas]):
            validator = zeit.content.cp.interfaces.IValidator(item)
            if validator.status and self.status != ERROR:
                # Set self status when there was an error or warning, but only
                # if there was no error before. If there was an error the whole
                # validation will stay in error state
                self.status = validator.status
            if validator.messages:
                self.messages.extend(validator.messages)


class ValidatingWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):

    def can_publish(self):
        validator = zeit.content.cp.interfaces.IValidator(self.context)
        if validator.status == zeit.content.cp.rule.ERROR:
            return False
        return True
