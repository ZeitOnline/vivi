# -*- coding: utf-8 -*-
from zeit.solr import query
import zeit.content.article.article
import zeit.content.infobox.infobox
import zeit.cms.admin.browser.admin
import zope.formlib.form as form


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Admin View with the publish button.
    Check out the normal Admin View.
    /zeit.cms/src/zeit/cms/admin/browser/admin.py.
    """

    extra_actions = form.Actions()

    @property
    def actions(self):
        return list(super(VolumeAdminForm, self).actions) + \
               list(self.extra_actions)

    @form.action("Publish content of this volume", extra_actions)
    def publish_all(self, action, data):
        to_publish = self._get_result_from_solr(self)


    def _get_result_from_solr(self):
        # TODO: Think about infoboxes. They should be published as well.
        # Check if they are in Solr
        additional_queries = [
            query.field('published', 'not-published'),
            query.or_(
                query.and_(
                    query.bool_field('urgent', True),
                    query.field_raw(
                        'type',
                        zeit.content.article.article.ArticleType.type)),
                query.field_raw('type',
                                zeit.content.infobox.infobox.InfoboxType.type),
            ),

        ]
        return self.context.all_content_via_solr(
            additional_query_contstraints=additional_queries)
