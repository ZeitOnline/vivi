import datetime
import re
import zeit.cms.testing
import zeit.content.image.testing
import zope.testing.renormalizing


now_plus_7_days = datetime.date.today() + datetime.timedelta(days=7)

checker = zope.testing.renormalizing.RENormalizing(
    [
        (
            re.compile(
                '%04d-%02d-%02d 00:00:00'
                % (now_plus_7_days.year, now_plus_7_days.month, now_plus_7_days.day)
            ),
            '<Datetime-7-Days-In-Future>',
        )
    ]
)


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'imagefolder.txt',
        'master-image.txt',
        package='zeit.content.image.browser',
        checker=checker,
        layer=zeit.content.image.testing.WSGI_LAYER,
    )
