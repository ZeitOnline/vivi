# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish

import zeit.content.article.article
import zeit.content.infobox.infobox
import zeit.cms.admin.browser.admin
import zope.formlib.form
import zeit.solr.query


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()

    @property
    def actions(self):
        return list(super(VolumeAdminForm, self).actions) + \
               list(self.extra_actions)

    @zope.formlib.form.action(_("Publish content of this volume"),
                              extra_actions)
    def publish_all(self, action, data):
        Q = zeit.solr.query
        additional_constraints = [
            Q.field('published', 'not-published'),
            Q.or_(
                # Only Articles marked as urgent and infoboxes should be
                # published
                Q.and_(
                    Q.bool_field('urgent', True),
                    Q.field_raw(
                        'type',
                        zeit.content.article.article.ArticleType.type)),
                Q.field_raw('type',
                                zeit.content.infobox.infobox.InfoboxType.type),
            ),

        ]
        to_publish = self.context.all_content_via_solr(
            additional_query_contstraints=additional_constraints)
        IPublish(self.context).publish_multiple(to_publish)
