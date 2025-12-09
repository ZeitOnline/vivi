from uuid import uuid4
import logging

from sqlalchemy import delete, select
import BTrees.OOBTree
import grokcore.component as grok
import pendulum
import persistent
import zope.annotation.interfaces
import zope.component
import zope.security.management
import zope.security.proxy

from zeit.cms.i18n import MessageFactory as _
from zeit.connector import models
from zeit.workflow.scheduled.interfaces import IScheduledOperation, IScheduledOperations
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces


log = logging.getLogger(__name__)


# Annotation key for storing operations in ZODB
SCHEDULED_OPERATIONS_KEY = 'zeit.workflow.scheduled.operations'


class ScheduledOperationMixin:
    def _init_fields(self, source):
        for field_name in IScheduledOperation.names():
            value = getattr(source, field_name)
            if field_name == 'property_changes' and value is None:
                value = {}
            setattr(self, field_name, value)


@grok.implementer(IScheduledOperation)
class ScheduledOperationCache(persistent.Persistent, ScheduledOperationMixin):
    """ZODB-persisted scheduled operation for working copies."""

    def __init__(
        self, operation_id, operation, scheduled_on, property_changes=None, created_by=None
    ):
        persistent.Persistent.__init__(self)
        self.id = operation_id
        self.operation = operation
        self.scheduled_on = scheduled_on
        self.property_changes = property_changes or {}
        self.created_by = created_by
        self.date_created = pendulum.now('UTC')
        self.executed_on = None

    @classmethod
    def from_operation(cls, op):
        """Create cache instance from an existing IScheduledOperation."""
        instance = cls.__new__(cls)
        persistent.Persistent.__init__(instance)
        instance._init_fields(op)
        return instance


@grok.implementer(IScheduledOperation)
class ScheduledOperation(grok.Adapter, ScheduledOperationMixin):
    """Read-only adapter for SQL model scheduled operations."""

    grok.context(models.ScheduledOperation)

    def __init__(self, model):
        self._init_fields(model)


class ScheduledOperationsBase:
    def _get_principal(self):
        """In case of multiple principles, we take the first one we can get."""
        interaction = zope.security.management.getInteraction()
        if interaction and interaction.participations:
            return interaction.participations[0].principal.id
        return None

    def _log_operation(self, operation, scheduled_on):
        log_util = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_util.log(
            self.context,
            _(
                'Scheduled ${op} for ${date}',
                mapping={'op': operation, 'date': scheduled_on.isoformat()},
            ),
        )


@grok.implementer(IScheduledOperations)
class RepositoryScheduledOperations(grok.Adapter, ScheduledOperationsBase):
    """Manage scheduled operations for stored content (SQL storage)."""

    grok.context(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = zope.security.proxy.removeSecurityProxy(context)
        self.content_id = zeit.cms.content.interfaces.IUUID(self.context).shortened
        self._connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def add(self, operation, scheduled_on, property_changes=None):
        model = models.ScheduledOperation(
            content=self.content_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes or {},
            created_by=self._get_principal(),
            executed_on=None,
        )
        self._connector.session.add(model)
        self._log_operation(operation, scheduled_on)

        return model.id

    def remove(self, operation_id):
        result = self._connector.session.execute(
            delete(models.ScheduledOperation).where(models.ScheduledOperation.id == operation_id)
        )
        if result.rowcount == 0:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )
        log.debug('Removed operation %s from SQL', operation_id)

    def update(self, operation_id, scheduled_on=None, executed_on=None, property_changes=None):
        model = self._connector.session.get(models.ScheduledOperation, operation_id)
        if not model:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )

        if scheduled_on is not None:
            model.scheduled_on = scheduled_on
        if property_changes is not None:
            model.property_changes = property_changes
        if executed_on is not None:
            model.executed_on = executed_on

    def list(self, operation=None):
        query = select(models.ScheduledOperation).where(
            models.ScheduledOperation.content == self.content_id
        )
        if operation:
            query = query.where(models.ScheduledOperation.operation == operation)
        query = query.order_by(models.ScheduledOperation.scheduled_on)

        raw_operations = self._connector.session.execute(query).scalars().all()
        return [IScheduledOperation(op) for op in raw_operations]

    def get(self, operation_id):
        model = self._connector.session.get(models.ScheduledOperation, operation_id)
        if not model:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )
        return IScheduledOperation(model)

    def synchronize(self, operations):
        self._connector.session.execute(
            delete(models.ScheduledOperation).where(
                models.ScheduledOperation.content == self.content_id
            )
        )

        if not operations:
            return

        operation_models = []
        for op in operations:
            model = models.ScheduledOperation(
                id=op.id,
                content=self.content_id,
                operation=op.operation,
                scheduled_on=op.scheduled_on,
                property_changes=op.property_changes or {},
                created_by=op.created_by,
                executed_on=op.executed_on,
            )
            model.date_created = op.date_created
            operation_models.append(model)

        self._connector.session.add_all(operation_models)

    def execute(self, operation):
        if operation.executed_on is not None:
            log.warning(
                f'Operation {operation.id} already executed on {operation.executed_on}, skipping'
            )
            return

        if operation.property_changes:
            self._apply_property_changes(operation.property_changes)

        publisher = zeit.cms.workflow.interfaces.IPublish(self.context)
        if operation.operation == 'publish':
            publisher.publish(
                background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED
            )
            self.update(operation.id, executed_on=pendulum.now('UTC'))
            log.debug(
                f'Executed scheduled publish for {self.context.uniqueId} (ID: {operation.id})'
            )
        elif operation.operation == 'retract':
            info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
            if not info.published:
                self.update(operation.id, executed_on=pendulum.now('UTC'))
                log.info(
                    f'Content {self.context.uniqueId} already retracted, '
                    f'skipping (ID: {operation.id})'
                )
            else:
                publisher.retract(
                    background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED
                )
                self.update(operation.id, executed_on=pendulum.now('UTC'))
                log.debug(
                    f'Executed scheduled retract for {self.context.uniqueId} (ID: {operation.id})'
                )
        else:
            raise ValueError(f'Unknown operation type: {operation.operation} (ID: {operation.id})')

    def _apply_property_changes(self, property_changes):
        objectlog = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)

        with zeit.cms.checkout.helper.checked_out(
            self.context, will_publish_soon=True, raise_if_error=True
        ) as co:
            for name, new_value in property_changes.items():
                if hasattr(co, name):
                    old_value = getattr(co, name, None)
                    setattr(co, name, new_value)
                    objectlog.log(
                        self.context,
                        _(
                            '${name} changed from "${old}" to "${new}"',
                            mapping={'name': name, 'old': old_value, 'new': new_value},
                        ),
                    )
                    log.debug(f'Applied property change: {name} = {new_value}')
                else:
                    log.warning(f'Property {name} not found on {self.context.uniqueId}, skipping')


@grok.implementer(IScheduledOperations)
class WorkingCopyScheduledOperations(grok.Adapter, ScheduledOperationsBase):
    """Manage scheduled operations for working copies (ZODB storage)."""

    grok.context(zeit.cms.checkout.interfaces.ILocalContent)

    def __init__(self, context):
        self.context = zope.security.proxy.removeSecurityProxy(context)
        self._storage = self._get_annotations_storage()

    def _get_annotations_storage(self):
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        if SCHEDULED_OPERATIONS_KEY not in annotations:
            annotations[SCHEDULED_OPERATIONS_KEY] = BTrees.OOBTree.OOBTree()
            self.context._p_changed = True
        return annotations[SCHEDULED_OPERATIONS_KEY]

    def add(self, operation, scheduled_on, property_changes=None):
        operation_id = str(uuid4())
        op = ScheduledOperationCache(
            operation_id=operation_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes,
            created_by=self._get_principal(),
        )
        self._storage[operation_id] = op
        self.context._p_changed = True
        self._log_operation(operation, scheduled_on)

        return operation_id

    def remove(self, operation_id):
        if operation_id not in self._storage:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )
        del self._storage[operation_id]
        self.context._p_changed = True

    def update(self, operation_id, scheduled_on=None, executed_on=None, property_changes=None):
        if operation_id not in self._storage:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )

        op = self._storage[operation_id]
        if scheduled_on is not None:
            op.scheduled_on = scheduled_on
        if property_changes is not None:
            op.property_changes = property_changes
        if executed_on is not None:
            op.executed_on = executed_on

        op._p_changed = True
        self.context._p_changed = True

    def list(self, operation=None):
        results = []
        for op in self._storage.values():
            if operation is None or op.operation == operation:
                results.append(op)
        return sorted(results, key=lambda x: x.scheduled_on)

    def get(self, operation_id):
        if operation_id not in self._storage:
            raise KeyError(
                f'Operation {operation_id} not found for content {self.context.uniqueId}'
            )
        return self._storage[operation_id]

    def synchronize(self, operations):
        self._storage.clear()

        for operation in operations:
            self._storage[operation.id] = ScheduledOperationCache.from_operation(operation)

        self.context._p_changed = True

    def execute(self, operation):
        raise NotImplementedError(
            'Cannot execute operations on working copy. '
            'Check in first, then execute on repository content.'
        )
