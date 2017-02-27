# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish

from zeit.solr import query
import zeit.content.article.article
import zeit.content.infobox.infobox
import zeit.cms.admin.browser.admin
import zope.formlib.form as form


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = form.Actions()

    @property
    def actions(self):
        return list(super(VolumeAdminForm, self).actions) + \
               list(self.extra_actions)

    @form.action(_("Publish content of this volume"), extra_actions)
    def publish_all(self, action, data):
        additional_constraints = [
            query.field('published', 'not-published'),

            query.or_(
                # Only Articles marked as urgent and infoboxes should be
                # published
                query.and_(
                    query.bool_field('urgent', True),
                    query.field_raw(
                        'type',
                        zeit.content.article.article.ArticleType.type)),
                query.field_raw('type',
                                zeit.content.infobox.infobox.InfoboxType.type),
            ),

        ]
        to_publish = self.context.all_content_via_solr(
            additional_query_contstraints=additional_constraints)
        IPublish(self.context).publish_multiple(to_publish)
