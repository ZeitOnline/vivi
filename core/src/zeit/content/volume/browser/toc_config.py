# -*- coding: utf-8 -*-

# TODO Hier finde ich nichts...
# Infografik TODO Darüber muss man sich Gedanken machen, titel des Dokuments
# ENTDECKEN
# Nur ganz kurz
# KINDERZEIT
# Moment Mal!
# Rekord der Woche
# Comic
# CHANCEN
# Universum
# Work-Life-Balance
# Idea
# Compiled regex for xpath, if match -> Article should be excluded
import re


class ArticleExcluder(object):
    """
    Checks if an article should be excluded from the table of contents.
    """
    # Rules should be as strict as possible, otherwise the wrong article might get  excluded
    TITLE_XPATH = "body/title/text()"
    SUPERTITLE_XPATH = "body/supertitle/text()"
    JOBNAME_XPATH = "//attribute[@name='jobname']/text()"
    _title_exclude = [
        u"Heute \d+.\d+",
        u"Damals \d+.\d+",
        u"PROMINENT IGNORIERT",
        u"Du siehst aus, wie ich mich fühle",
        u"WAS MEIN LEBEN REICHER MACHT",
        u"UND WER BIST DU?"

    ]
    _supertitle_exclude = [
        u"NEIN. QUARTERLY",
        u"MAIL AUS:",
        u"MACHER UND MÄRKTE",
        u"AUTO WOFÜR IST DAS DA",
        u"HALBWISSEN",
        u"ZAHL DER WOCHE",
        u"WIR RATEN (AB|ZU)",
        u"DER UNNÜTZE VERGLEICH",
        u"MALEN NACH ZAHLEN",
        u"LEXIKON DER NEUROSEN",
        u"ZEITSPRUNG",
        u"(LESE|BASTEL)-TIPP"
    ]

    _jobname_exclude = [
        u'(Traumstück|AS-Zahl)'
    ]

    def __init__(self):
        # TODO Create combined regex? Should be faster.
        # compile regexes for article
        self._compiled_title_regexs = [re.compile(regex) for regex in self._title_exclude]
        self._compiled_supertitle_regexs = [re.compile(regex) for regex in self._supertitle_exclude]
        self._compiled_jobname_regexs = [re.compile(regex) for regex in self._jobname_exclude]

    def is_relevant(self, article_lxml_tree):
        # TODO A lot of Code repetition
        title_values = article_lxml_tree.xpath(self.TITLE_XPATH)
        supertitle_values = article_lxml_tree.xpath(self.SUPERTITLE_XPATH)
        jobname_values = article_lxml_tree.xpath(self.JOBNAME_XPATH)

        title_value = title_values[0] if len(title_values) > 0 else ''
        supertitle_value = supertitle_values[0] if len(supertitle_values) > 0 else ''
        jobname_value = jobname_values[0] if len(jobname_values) > 0 else ''

        title_exclude = any(
            [re.match(title_pattern, title_value) for title_pattern in self._compiled_title_regexs]
        )
        supertitle_exclude = any(
            [re.match(supertitle_pattern, supertitle_value) for supertitle_pattern in self._compiled_supertitle_regexs]
        )
        jobname_exclude = any(
            [re.match(jobname_pattern, jobname_value) for jobname_pattern in self._compiled_jobname_regexs]
        )

        return not(title_exclude or supertitle_exclude or jobname_exclude)

