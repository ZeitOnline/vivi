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

from zeit.cms.i18n import MessageFactory as _
from zeit.connector import models
from zeit.workflow.scheduled.interfaces import (
    IScheduledOperation,
    IScheduledOperations,
    IScheduledOperationsStorage,
)
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces


log = logging.getLogger(__name__)


# Annotation key for storing operations in ZODB
SCHEDULED_OPERATIONS_KEY = 'zeit.workflow.scheduled.operations'


@grok.implementer(IScheduledOperation)
class ScheduledOperationCache(persistent.Persistent):
    """ZODB-persisted scheduled operation for working copies."""

    def __init__(
        self, operation_id, operation, scheduled_on, property_changes=None, created_by=None
    ):
        self.id = operation_id
        self.operation = operation
        self.scheduled_on = scheduled_on
        self.property_changes = property_changes or {}
        self.created_by = created_by
        self.date_created = pendulum.now('UTC')


@grok.implementer(IScheduledOperation)
class ScheduledOperation:
    """Read-only view of a scheduled operation."""

    def __init__(self, model):
        self._model = model

    @property
    def id(self):
        return self._model.id

    @property
    def operation(self):
        return self._model.operation

    @property
    def scheduled_on(self):
        return self._model.scheduled_on

    @property
    def property_changes(self):
        return self._model.property_changes or {}

    @property
    def created_by(self):
        return self._model.created_by

    @property
    def date_created(self):
        return self._model.date_created


@grok.implementer(IScheduledOperationsStorage)
@grok.adapter(zeit.cms.checkout.interfaces.ILocalContent)
class ZODBScheduledOperationsStorage:
    def __init__(self, context):
        self.context = context
        self._storage = self._get_annotations_storage()

    def _get_annotations_storage(self):
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        if SCHEDULED_OPERATIONS_KEY not in annotations:
            annotations[SCHEDULED_OPERATIONS_KEY] = BTrees.OOBTree.OOBTree()
            self.context._p_changed = True
        return annotations[SCHEDULED_OPERATIONS_KEY]

    def add(
        self, operation_id, operation, scheduled_on, property_changes, created_by, date_created=None
    ):
        op = ScheduledOperationCache(
            operation_id=operation_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes,
            created_by=created_by,
        )
        if date_created is not None:
            op.date_created = date_created
        self._storage[operation_id] = op
        self.context._p_changed = True

    def remove(self, operation_id):
        if operation_id not in self._storage:
            raise KeyError(f'Operation {operation_id} not found')
        del self._storage[operation_id]
        self.context._p_changed = True

    def update(self, operation_id, scheduled_on=None, property_changes=None):
        if operation_id not in self._storage:
            raise KeyError(f'Operation {operation_id} not found')

        op = self._storage[operation_id]
        if scheduled_on is not None:
            op.scheduled_on = scheduled_on
        if property_changes is not None:
            op.property_changes = property_changes

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
            raise KeyError(f'Operation {operation_id} not found')
        return self._storage[operation_id]


@grok.implementer(IScheduledOperationsStorage)
@grok.adapter(zeit.cms.interfaces.ICMSContent)
class SQLScheduledOperationsStorage:
    def __init__(self, context):
        self.context = context
        self.content_id = zeit.cms.content.interfaces.IUUID(context).shortened
        self._connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def add(
        self, operation_id, operation, scheduled_on, property_changes, created_by, date_created=None
    ):
        model = models.ScheduledOperation(
            id=operation_id,
            content=self.content_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes or {},
            created_by=created_by,
        )
        if date_created is not None:
            model.date_created = date_created
        self._connector.session.add(model)

    def remove(self, operation_id):
        result = self._connector.session.execute(
            delete(models.ScheduledOperation).where(models.ScheduledOperation.id == operation_id)
        )
        if result.rowcount == 0:
            raise KeyError(f'Operation {operation_id} not found')
        log.debug('Removed operation %s from SQL', operation_id)

    def update(self, operation_id, scheduled_on=None, property_changes=None):
        model = self._connector.session.get(models.ScheduledOperation, operation_id)
        if not model:
            raise KeyError(f'Operation {operation_id} not found')

        if scheduled_on is not None:
            model.scheduled_on = scheduled_on
        if property_changes is not None:
            model.property_changes = property_changes

    def list(self, operation=None):
        query = select(models.ScheduledOperation).where(
            models.ScheduledOperation.content == self.content_id
        )
        if operation:
            query = query.where(models.ScheduledOperation.operation == operation)
        query = query.order_by(models.ScheduledOperation.scheduled_on)

        return self._connector.session.execute(query).scalars().all()

    def get(self, operation_id):
        model = self._connector.session.get(models.ScheduledOperation, operation_id)
        if not model:
            raise KeyError(f'Operation {operation_id} not found')
        return model


@grok.implementer(IScheduledOperations)
@grok.adapter(zeit.cms.interfaces.ICMSContent)
class ScheduledOperations:
    def __init__(self, context):
        self.context = context
        self._storage = IScheduledOperationsStorage(self.context)

    def add(self, operation, scheduled_on, property_changes=None):
        if operation not in ('publish', 'retract'):
            raise ValueError(f'Invalid operation: {operation}')

        if property_changes:
            self._validate_property_changes(property_changes)

        operation_id = str(uuid4())

        self._storage.add(
            operation_id=operation_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes,
            created_by=self._get_principal(),
        )

        log_util = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_util.log(
            self.context,
            _(
                'Scheduled ${op} for ${date}',
                mapping={'op': operation, 'date': scheduled_on.isoformat()},
            ),
        )

        return operation_id

    def remove(self, operation_id):
        self._storage.remove(operation_id)

    def update(self, operation_id, scheduled_on=None, property_changes=None):
        if property_changes is not None:
            self._validate_property_changes(property_changes)
        self._storage.update(operation_id, scheduled_on, property_changes)

    def list(self, operation=None):
        raw_operations = self._storage.list(operation)
        return [ScheduledOperation(op) for op in raw_operations]

    def get(self, operation_id):
        raw_operation = self._storage.get(operation_id)
        return ScheduledOperation(raw_operation)

    def _validate_property_changes(self, property_changes):
        if not isinstance(property_changes, dict):
            raise ValueError('property_changes must be a dict')

        for name in property_changes:
            if not isinstance(name, str):
                raise ValueError(f'Property name must be string, got {type(name)}')

            if not hasattr(self.context, name):
                raise ValueError(
                    f'Property "{name}" not found on {self.context.__class__.__name__}. '
                )

    def _get_principal(self):
        """In case of multiple principals we take the first one we can get"""
        interaction = zope.security.management.getInteraction()
        if interaction and interaction.participations:
            return interaction.participations[0].principal.id
        return None
