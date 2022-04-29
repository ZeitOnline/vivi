from zeit.cms.content.sources import FEATURE_TOGGLES
import grokcore.component as grok
import logging
import zeit.cms.celery
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zope.component


log = logging.getLogger(__name__)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_index_on_checkin(context, event):
    if not FEATURE_TOGGLES.find('reference_index'):
        return
    if getattr(event, 'publishing', False):
        return
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.index(context)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.container.interfaces.IObjectAddedEvent)
def update_index_on_add(context, event):
    if not zeit.cms.repository.interfaces.ICollection.providedBy(
            context.__parent__):
        return
    if not FEATURE_TOGGLES.find('reference_index'):
        return
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.index(context)


class Dummy:

    uniqueId = None


@zeit.cms.celery.task
def update_referencing_objects(uniqueId):
    # As we want to use this function as celery task, we need a serializable
    # argument, i.e. no ICMSContent object. In fact we do not need a complete
    # ICMSContent object at all at this point, only a dummy with an attribute
    # ``uniqueId``. This also helps with an edge case in
    # ``zeit.cms.redirect.move.store_redirect``. There we need to update
    # objects referencing the old name. But context already has the new name,
    # so adapting to ``ICMSContent`` will not do the job.
    context = Dummy()
    context.uniqueId = uniqueId

    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context)
    for related_object in list(relating_objects):
        log.info(
            'Cycling %s to update referenced metadata (caused by %s)',
            related_object.uniqueId, context.uniqueId)
        # the actual work is done by IBeforeCheckin-handlers
        zeit.cms.checkout.helper.with_checked_out(
            related_object, lambda x: True)
