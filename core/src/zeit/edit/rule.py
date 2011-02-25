# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.POSException
import gocept.cache.method
import grokcore.component
import logging
import sys
import urllib2
import zeit.cms.workflow.interfaces
import zeit.edit.interfaces
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

        globs = zeit.edit.interfaces.IRuleGlobs(context)
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


@grokcore.component.adapter(zope.interface.Interface)
@grokcore.component.implementer(zeit.edit.interfaces.IRuleGlobs)
def globs(context):
    globs = {}
    for name, adapter in zope.component.getAdapters(
        (context,), zeit.edit.interfaces.IRuleGlob):
        if not name:
            continue
        globs[name] = adapter
    return globs


def glob(adapts):
    """Decorator that creates an entry in the rule globs.

    The name for the glob is the decorated function's name.
    The glob applies for objects with the interface given in `adapts`.

    """
    def decorate(func):
        frame = sys._getframe(1)
        name = '__zeit_edit_globs__'
        globs = frame.f_locals.get(name, None)
        if globs is None:
            frame.f_locals[name] = globs = []
        globs.append((func, adapts))
        return func
    return decorate


class RulesManager(grokcore.component.GlobalUtility):

    grokcore.component.implements(zeit.edit.interfaces.IRulesManager)

    def __init__(self):
        self._rules = []

    @gocept.cache.method.Memoize(360)
    def get_rules(self):
        rules = []
        config = zope.app.appsetup.product.getProductConfiguration('zeit.edit')
        if not config:
            return []
        url = config.get('rules-url')
        if not url:
            return []
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
        rule = zeit.edit.rule.Rule(code, line_no + 1)
        return rule

    @property
    def rules(self):
        try:
            self._rules = self.get_rules()
        except SyntaxError, e:
            # return the previously cached rules unmodified
            log.exception(e)
        return self._rules


class Validator(grokcore.component.Adapter):
    """Generic validator for all elements."""

    grokcore.component.implements(zeit.edit.interfaces.IValidator)
    grokcore.component.context(zeit.edit.interfaces.IElement)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        for rule in rm.rules:
            status = rule.apply(context)
            if status.status and self.status != zeit.edit.rule.ERROR:
                self.status = status.status
            if status.message:
                self.messages.append(status.message)


class RecursiveValidator(object):
    """A RecursiveValidator iterates through (some definition of) children of
    its context and generates its result from the validation of those."""

    zope.interface.implements(zeit.edit.interfaces.IValidator)

    status = None

    def __init__(self, context):
        self.context = context
        self.messages = []
        for item in self.children:
            validator = zeit.edit.interfaces.IValidator(item)
            if validator.status and self.status != ERROR:
                # Set self status when there was an error or warning, but only
                # if there was no error before. If there was an error the whole
                # validation will stay in error state
                self.status = validator.status
            if validator.messages:
                self.messages.extend(validator.messages)

    @property
    def children(self):
        return iter(self.context)


class ValidatingWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):

    def can_publish(self):
        validator = zeit.edit.interfaces.IValidator(self.context)
        if validator.status == ERROR:
            return False
        return True


@glob(zeit.edit.interfaces.IElement)
def type(context):
    return context.type


@glob(zeit.edit.interfaces.IBlock)
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


@glob(zeit.edit.interfaces.IElement)
def area(context):
    return zeit.edit.interfaces.IArea(context).__name__


@glob(zeit.edit.interfaces.IContainer)
def count(context):
    return len(context)


@glob(zeit.edit.interfaces.IElement)
def position(context):
    return context.__parent__.keys().index(context.__name__) + 1


@glob(zope.interface.Interface)
def is_published(context):
    def is_published_inner(obj):
        pi = zeit.cms.workflow.interfaces.IPublishInfo(obj, None)
        return pi is not None and pi.published
    return is_published_inner
