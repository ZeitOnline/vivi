import zeit.cms.browser.objectdetails


class Details(zeit.cms.browser.objectdetails.Details):
    @property
    def graphical_preview_url(self):
        return self.context.video_still
