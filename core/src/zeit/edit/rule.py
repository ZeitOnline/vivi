from datetime import datetime
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
from zeit.workflow.interfaces import ITimeBasedPublishing
from zope.cachedescriptors.property import Lazy as cachedproperty
import ZODB.POSException
import grokcore.component as grok
import logging
import pytz
import sys
import zeit.cms.content.sources
import zeit.cms.workflow.interfaces
import zeit.edit.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publishinfo
import zeit.workflow.timebased
import zope.app.appsetup.product
import zope.component
import zope.interface


log = logging.getLogger(__name__)


ERROR = 'error'
WARNING = 'warning'


class Break(Exception):
    pass


class Status:

    status = None
    message = None


class Rule:

    def __init__(self, code, line=None):
        self.source = code
        self.code = compile(code, '<string>', 'exec')
        self.line = line

    def apply(self, context, globs):
        status = Status()

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
        except Exception:
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


@grok.adapter(zope.interface.Interface)
@grok.implementer(zeit.edit.interfaces.IRuleGlobs)
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


@grok.implementer(zeit.edit.interfaces.IRulesManager)
class RulesManager(grok.GlobalUtility):

    def __init__(self):
        self._rules = []

    @CONFIG_CACHE.cache_on_arguments()
    def get_rules(self):
        rules = []
        config = zope.app.appsetup.product.getProductConfiguration('zeit.edit')
        if not config:
            return []
        url = config.get('rules-url')
        if not url:
            return []
        file_rules = zeit.cms.content.sources.load(url)
        log.info('Loading rules from %s' % url)
        noop = True
        rule = []
        start_line = 0
        for line_no, line in enumerate(file_rules):
            if not isinstance(line, str):
                line = line.decode('utf-8')
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
        compile(code, '<string>', 'exec')  # syntax check
        rule = zeit.edit.rule.Rule(code, line_no + 1)
        return rule

    @property
    def rules(self):
        try:
            self._rules = self.get_rules()
        except SyntaxError as e:
            # return the previously cached rules unmodified
            log.exception(e)
        return self._rules


@grok.implementer(zeit.edit.interfaces.IValidator)
class Validator(grok.Adapter):
    """Generic validator for all elements."""

    grok.context(zeit.edit.interfaces.IElement)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        globs = zeit.edit.interfaces.IRuleGlobs(context)
        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        for rule in rm.rules:
            status = rule.apply(context, globs)
            if status.status and self.status != zeit.edit.rule.ERROR:
                self.status = status.status
            if status.message:
                self.messages.append(status.message)


@zope.interface.implementer(zeit.edit.interfaces.IValidator)
class RecursiveValidator:
    """A RecursiveValidator iterates through (some definition of) children of
    its context and generates its result from the validation of those."""

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

    @cachedproperty
    def validator(self):
        return zeit.edit.interfaces.IValidator(self.context)

    def can_publish(self):
        status = super().can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        if self.validator.status == ERROR:
            self.error_messages = (
                _('Could not publish ${id} since it has validation errors.',
                  mapping=self._error_mapping),) + tuple(
                      self.validator.messages)
            return CAN_PUBLISH_ERROR
        if self.validator.status == WARNING:
            self.error_messages = self.validator.messages
            return CAN_PUBLISH_WARNING
        return CAN_PUBLISH_SUCCESS


@glob(zeit.edit.interfaces.IElement)
def type(context):
    return context.type


@glob(zeit.edit.interfaces.IBlock)
def is_block(context):
    return True


@glob(zope.interface.Interface)  # noqa
def is_block(context):
    return False


@glob(zeit.edit.interfaces.IArea)
def is_area(context):
    return True


@glob(zope.interface.Interface)  # noqa
def is_area(context):
    return False


@glob(zeit.edit.interfaces.IElement)
def area(context):
    area = zeit.edit.interfaces.IArea(context, None)
    if area is not None:
        return area.__name__
    return None


@glob(zeit.edit.interfaces.IContainer)
def count(context):
    return len(context)


@glob(zeit.edit.interfaces.IElement)
def position(context):
    return list(context.__parent__).index(context.__name__) + 1


@glob(zope.interface.Interface)
def is_published(context):
    def is_published_inner(obj):
        pi = zeit.cms.workflow.interfaces.IPublishInfo(obj, None)
        if pi.__class__ is zeit.workflow.publishinfo.NotPublishablePublishInfo:
            # for the purposes of the validation rules
            return True
        return pi is not None and pi.published
    return is_published_inner


@glob(zope.interface.Interface)
def scheduled_for_publishing(context):
    def inner(obj):
        pi = zeit.cms.workflow.interfaces.IPublishInfo(obj, None)
        if (pi is None or not ITimeBasedPublishing.providedBy(pi)):
            return False
        if not pi.release_period[0]:
            return False
        if pi.release_period[1]:
            now = datetime.now(pytz.UTC)
            return now <= pi.release_period[1]
        return True
    return inner
