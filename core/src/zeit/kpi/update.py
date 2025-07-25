import argparse

from sqlalchemy import and_ as sql_and
from sqlalchemy import select
from sqlalchemy import text as sql
import zope.component

from zeit.connector.models import Content
from zeit.kpi.interfaces import IKPIDatasource, KPIUpdateEvent
import zeit.cms.cli
import zeit.cms.repository.interfaces
import zeit.connector.interfaces


INTERVALS = {
    '48h': "date_first_released >= now() - interval '48h'",
    '7d': """date_first_released < now() - interval '48h' AND
             date_first_released >= now() - interval '7d'""",
    'all': """idate_part('day', date_first_released)=idate_part('day', now()) AND
              idate_part('hour', date_first_released)=idate_part('hour', now())""",
}


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.kpi', 'principal'))
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', choices=list(INTERVALS), required=True)
    parser.add_argument('--kpi-batch-size', type=int, default=1000)
    parser.add_argument('--sql-batch-size', type=int, default=100)
    options = parser.parse_args()
    query = select(Content).where(
        sql_and(
            (Content.published == True),  # noqa
            (Content.type.in_(['article', 'centerpage-2009', 'gallery', 'link', 'video'])),
            sql(INTERVALS[options.interval]),
        )
    )
    update(query, options.kpi_batch_size, options.sql_batch_size)


def update(query, kpi_batch_size, sql_batch_size):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    source = zope.component.getUtility(IKPIDatasource)
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    count = connector.search_sql_count(query)

    batch = []
    query = query.order_by(Content.id).limit(sql_batch_size)
    for i in range(int(count / sql_batch_size) + 1):
        batch.extend(repository.search(query.offset(i * sql_batch_size)))
        if len(batch) >= kpi_batch_size:
            zope.event.notify(KPIUpdateEvent(source.query(batch)))
            batch.clear()
    if batch:
        zope.event.notify(KPIUpdateEvent(source.query(batch)))
