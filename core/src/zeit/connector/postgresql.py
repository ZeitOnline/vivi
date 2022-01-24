import sqlalchemy
import sqlalchemy.orm
import zeit.connector.interfaces
import zope.interface
import zope.sqlalchemy


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
class Connector:

    def __init__(self, dsn):
        self.dsn = dsn
        self.engine = sqlalchemy.create_engine(dsn, future=True)
        self.session = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine, future=True))
        zope.sqlalchemy.register(self.session)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.connector') or {}
        return cls(config['dsn'])


factory = Connector.factory


METADATA = sqlalchemy.MetaData()
DBObject = sqlalchemy.orm.declarative_base(metadata=METADATA)
