from sqlalchemy import bindparam, func, select
from sqlalchemy import text as sql
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.cli import commit_with_retry
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import PRIORITY_LOW, IPublish
from zeit.connector.models import Content
from zeit.wochenmarkt.sources import ingredientsSource, recipeCategoriesSource
import zeit.cms.cli
import zeit.connector.interfaces
import zeit.retresco.interfaces


def find_ingredients():
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    query_text = """
        type = 'article'
        AND article_genre in :genres
        AND published = true
    """
    query = (
        select(func.jsonb_array_elements(Content.recipe_ingredients))
        .where(
            sql(query_text).bindparams(
                bindparam('genres', recipeCategoriesSource.factory.genres, expanding=True)
            )
        )
        .distinct()
    )
    return connector.execute_sql(query)


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.wochenmarkt', 'used-ingredients-principal')
)
def collect_used():
    result = find_ingredients()
    if not result:
        return

    used = set(result.scalars())
    xml = ingredientsSource(None).factory._get_tree()
    for item in xml.xpath('//ingredient'):
        if item.get('id') not in used:
            item.getparent().remove(item)

    for _ in commit_with_retry():
        source = ICMSContent('http://xml.zeit.de/data/ingredients_in_use.xml')
        with checked_out(source) as co:
            co.xml = xml

    IPublish(source).publish(priority=PRIORITY_LOW)
