from urllib.parse import urlparse, urlunparse

from google.api_core.client_options import ClientOptions
from google.auth.credentials import AnonymousCredentials
from sqlalchemy import Integer, Unicode, select
from sqlalchemy.orm import mapped_column
import google.cloud.bigquery
import sqlalchemy
import sqlalchemy.orm
import zope.interface

import zeit.cms.config
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.kpi.interfaces


@zope.interface.implementer(zeit.kpi.interfaces.IKPIDatasource)
class KPIBigQuery:
    def __init__(self, dsn):
        args = {'prefer_bqstorage_client': False}
        url = urlparse(dsn)

        if url.port:  # for tests
            dsn = urlunparse(url._replace(netloc=url.hostname))
            dsn += '?user_supplied_client=True'
            client = google.cloud.bigquery.Client(
                project=url.hostname,
                client_options=ClientOptions(api_endpoint=f'http://localhost:{url.port}'),
                credentials=AnonymousCredentials(),
            )
            args['client'] = client

        self.engine = sqlalchemy.create_engine(dsn, connect_args=args)
        self.session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=self.engine))
        self.LIVE_PREFIX = zeit.cms.config.required('zeit.cms', 'live-prefix')

    def query(self, contents):
        by_url = {}
        urls = []
        for content in contents:
            url = content.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, self.LIVE_PREFIX)
            urls.append(url)
            by_url[url] = content
        kpi = self.session.execute(select(KPIData).where(KPIData.url.in_(urls)))
        result = [(by_url[x.url], x) for x in kpi.scalars()]
        return result


@zope.interface.implementer(zeit.kpi.interfaces.IKPIDatasource)
def from_product_config():
    return KPIBigQuery(zeit.cms.config.required('zeit.kpi', 'dsn'))


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


@zope.interface.implementer(zeit.cms.content.interfaces.IKPI)
class KPIData(Base):
    __tablename__ = 'export_buzzboard'
    # Might be nicer to pass dataset via DSN, but that seems to have no effect.
    __table_args__ = {'schema': 'export'}

    url = mapped_column('page', Unicode, primary_key=True)
    # IKPI
    visits = mapped_column('visits', Integer)
    comments = mapped_column('comments', Integer)
    subscriptions = mapped_column('orders', Integer)


@zope.interface.implementer(zeit.kpi.interfaces.IKPIDatasource)
class MockKPI:
    result = []

    def query(self, contents):
        return self.result

    def _reset(self):
        self.result[:] = []


def reset_mock():
    mock = zope.component.queryUtility(zeit.kpi.interfaces.IKPIDatasource)
    if isinstance(mock, MockKPI):
        mock._reset()
