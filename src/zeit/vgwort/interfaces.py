# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


class ITokens(zope.interface.Interface):
    """Provde access to count tokens (Zählmarke)"""

    def claim():
        """Get a (public token, private token) tuple.

        Raises ValueError when there are no tokens.

        """

    def load(csv_file):
        """Load tokens from csv file (file like object)."""

    def add(public_token, private_token):
        """Add tokens."""


class IToken(zope.interface.Interface):

    public_token = zope.schema.TextLine(
        title=_('Public VGWort token'),
        required=False)
    private_token = zope.schema.TextLine(
        title=_('Private VGWort token'),
        required=False)


class IGenerallyReportableContent(zope.interface.Interface):
    """Marker for types which are generally reportable to vgwort.

    This marker is used to determine types which content types contain content
    which is in general reportable to vgwort (meldefähig). There are more
    constraints which are not supported yet (≥1800 characters etc.)

    """
