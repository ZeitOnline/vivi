# -*- coding: utf-8 -*-
from zeit.solr import query
import zeit.content.article.article
import zeit.content.infobox.infobox
import zeit.cms.admin.browser.admin


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Admin View with the publish button.
    Check out the normal Admin View.
    /zeit.cms/src/zeit/cms/admin/browser/admin.py.
    """

    def _get_result_from_solr(self):
        # TODO: Think about infoboxes. They should be published as well,
        # if they never got checked out they wont be in SOLR.
        # One Dirty Way would be to checkout all infoboxes after they got
        # imported.
        additional_queries = [
            query.field('published', 'not-published'),
            query.or_(query.field_raw(
                'type', zeit.content.article.article.ArticleType.type),
                  query.field_raw(
                'type', zeit.content.infobox.infobox.InfoboxType.type),
            ),
            query.bool_field('urgent', True)
        ]
        return self.context.all_content_via_solr(
            additional_query_contstraints=additional_queries)
