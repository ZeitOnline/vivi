# -*- coding: utf-8 -*-
import zeit.cms.browser.view
import csv
import logging
import zeit.find.search
import zeit.solr.query
# So logt der einfach auf die Konsole
log = logging.getLogger(__name__)


class Toc(zeit.cms.browser.view.Base):

    def __call__(self):
        volume_obj = self.context
        # Die Felder muss es geben, wegen IVolume
        year = volume_obj.year
        volume = volume_obj.volume
        filename = self._generate_file_name(year, volume)
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content(year, volume)

    #

    def _create_toc_content(self, year, volume):
        solr_data = self._get_toc_content_from_solr(year, volume)
        return self._solr_data_to_csv(solr_data)

    def _generate_file_name(self, year, volume):
        # from zeit.cms.i18n import MessageFactory as _
        # muss hier internationalisiert werden, wenn ja wie?
        # Das macht doch dann die Factory, nicht wahr
        return "inhalsverzeichnis_{}_{}.csv".format(year, volume)

    def _get_toc_content_from_solr(self, year, volume):
        q = zeit.solr.query.field('volume', str(volume))
        return str(zeit.find.search.search(q).docs[0])

    def _solr_data_to_csv(sefl, solr_data):
        return solr_data