# TODO:
# - maybe change parsing to use an explicit parser object with
# etree.XMLParser(ns_clean=True)?
import lxml.etree

import zeit.connector.dav.interfaces


__all__ = ('xml_from_string', 'xml_from_file')


class DavXmlDoc:
    def __init__(self):
        self.doc = None
        self.nsmap = {'D': 'DAV:', 'd': 'DAV:', 'DAV:': 'DAV:'}

    def from_string(self, string):
        self.parse(lxml.etree.fromstring, string)

    def from_file(self, f):
        self.parse(lxml.etree.parse, f)

    def parse(self, method, arg):
        try:
            self.doc = method(arg)
        except lxml.etree.XMLSyntaxError as e:
            raise zeit.connector.dav.interfaces.DavXmlParseError(
                e.error_log.filter_levels(lxml.etree.ErrorLevels.FATAL)
            )

    def xpathEval(self, expr):
        return self.doc.xpath(expr, namespaces=self.nsmap)

    # :note: why is this here? Or better, iff this is here,
    # why aren't the other node-finding functions here?
    def get_response_nodes(self):
        """Return a list of all D:response nodes"""
        res = self.xpathEval('D:response')
        return res

    def get_property_nodes(self, root):
        return self.xpathEval('DAV:propstat/DAV:prop/*')


def xml_from_string(data):
    d = DavXmlDoc()
    d.from_string(data)
    return d


def xml_from_file(f_in):
    d = DavXmlDoc()
    d.from_file(f_in)
    return d
