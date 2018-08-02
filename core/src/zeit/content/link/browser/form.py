from zeit.cms.i18n import MessageFactory as _

import gocept.form.grouped
import itertools
import zeit.content.image.interfaces
import zeit.cms.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.push.browser.form
import zope.formlib.form


class Base(zeit.push.browser.form.SocialBase,
           zeit.push.browser.form.MobileBase):

    metadata_group = gocept.form.grouped.Fields(
        _("Metadaten"),
        ('__name__', 'url', 'ressort', 'sub_ressort',
         'product', 'copyrights', 'authorships'),
        css_class='wide-widgets column-left')

    teaser_group = gocept.form.grouped.Fields(
        _("Teaser"),
        ('teaserSupertitle', 'teaserTitle', 'teaserText', 'image'),
        css_class='column-left wide-widgets')

    option_group = gocept.form.grouped.Fields(
        _("Options"),
        ('channels', 'lead_candidate', 'serie', 'access', 'dailyNewsletter',
         'keywords'),
        css_class='column-right')

    marketing_group = gocept.form.grouped.Fields(
        _("Marketing"),
        ('color_scheme', 'cap_title', 'banner_id'),
        css_class='column-right')

    story_stream_group = gocept.form.grouped.Fields(
        _("Storystream"),
        ('tldr_title', 'tldr_text', 'tldr_milestone', 'tldr_date',
         'storystreams'),
        css_class='column-right wide-widgets')

    link_group = gocept.form.grouped.Fields(
        _("Link"),
        ('target', 'nofollow'),
        css_class='column-right')

    # Make link specific field groups for other views
    link_field_groups = (metadata_group,
                         option_group,
                         marketing_group,
                         story_stream_group,
                         teaser_group,
                         link_group)

    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink,
        zeit.content.image.interfaces.IImages).select(
            *list(itertools.chain.from_iterable(
                [group.get_field_names() for group in
                 link_field_groups])))

    field_groups = (
        metadata_group,
        option_group,
        marketing_group,
        teaser_group,
        story_stream_group,
        zeit.push.browser.form.MobileBase.mobile_fields,
        link_group,
        zeit.push.browser.form.SocialBase.social_fields
    )

    def setUpWidgets(self, *args, **kw):
        super(Base, self).setUpWidgets(*args, **kw)
        self.set_charlimit('teaserSupertitle')
        self.set_charlimit('teaserTitle')
        self.set_charlimit('teaserText')


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link


class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit link')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View link metadata')
