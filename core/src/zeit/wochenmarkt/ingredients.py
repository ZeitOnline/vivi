import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.cli import commit_with_retry
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import PRIORITY_LOW, IPublish
from zeit.wochenmarkt.sources import ingredientsSource
import zeit.cms.cli
import zeit.retresco.interfaces
import zeit.wochenmarkt.interfaces


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.wochenmarkt', 'used-ingredients-principal')
)
def collect_used():
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    result = es.aggregate(
        {
            'aggs': {
                'ingredients': {'terms': {'field': 'payload.recipe.ingredients', 'size': 10000}}
            },
            'size': 0,
        }
    )
    if not result:
        return

    used = set()
    for item in result['ingredients']['buckets']:
        used.add(item['key'])

    xml = ingredientsSource._get_tree()
    for item in xml.xpath('//ingredient'):
        if item.get('id') not in used:
            item.getparent().remove(item)

    for _ in commit_with_retry():
        source = ICMSContent('http://xml.zeit.de/data/ingredients_in_use.xml')
        with checked_out(source) as co:
            co.xml = xml

    IPublish(source).publish(priority=PRIORITY_LOW)
