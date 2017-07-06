from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces


class Video(object):

    def __init__(self):
        self.data = {}

    @classmethod
    def from_cms(cls, cmsobj):
        instance = cls()
        data = instance.data
        data['custom_fields'] = custom = {}

        # This is coupled to our IAddLocation and importing implementation.
        data['id'] = cmsobj.__name__

        data['name'] = cmsobj.title
        data['description'] = cmsobj.teaserText
        data['long_description'] = cmsobj.subtitle

        custom['authors'] = ' '.join(
            x.target.uniqueId for x in cmsobj.authorships)
        custom['allow_comments'] = cls.bc_bool(cmsobj.commentsAllowed)
        custom['premoderate_comments'] = cls.bc_bool(
            cmsobj.commentsPremoderate)
        custom['banner'] = cmsobj.banner
        custom['banner_id'] = cmsobj.banner
        custom['newsletter'] = cmsobj.dailyNewsletter
        custom['recensions'] = cmsobj.has_recensions
        custom['produkt-id'] = cmsobj.product.id if cmsobj.product else None
        custom['cmskeywords'] = u';'.join(x.code for x in cmsobj.keywords)
        custom['ressort'] = cmsobj.ressort
        custom['serie'] = cmsobj.serie.serienname if cmsobj.serie else None
        custom['supertitle'] = cmsobj.supertitle
        custom['credit'] = cmsobj.video_still_copyright

        related = zeit.cms.related.interfaces.IRelatedContent(cmsobj).related
        for i in range(1, 6):
            try:
                item = related[i - 1]
            except IndexError:
                custom['ref_link%s' % i] = ''
                custom['ref_title%s' % i] = ''
            else:
                metadata = zeit.cms.content.interfaces.ICommonMetadata(
                    item, None)
                if metadata and metadata.teaserTitle:
                    title = metadata.teaserTitle
                else:
                    title = u'unknown'
                custom['ref_link%s' % i] = item.uniqueId
                custom['ref_title%s' % i] = title

        return instance

    @staticmethod
    def bc_bool(value):
        return '1' if value else '0'

    @property
    def write_data(self):
        data = {}
        for key in [
                'custom_fields', 'name', 'description', 'long_description']:
            if key in self.data:
                data[key] = self.data[key]
        return data

    @cachedproperty
    def id(self):
        return str(self.data.get('id', ''))

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.id or '(unknown)')


def update_brightcove(context, event):
    if not event.publishing:
        session = zeit.brightcove.session.get()
        session.update_video(Video.from_cms(context))


def publish_on_checkin(context, event):
    # prevent infinite loop, since there is a checkout/checkin cycle during
    # publishing (to update XML references etc.)
    if not event.publishing:
        zeit.cms.workflow.interfaces.IPublish(context).publish()
