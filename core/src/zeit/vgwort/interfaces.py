# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class ITokens(zope.interface.Interface):
    """Provde access to count tokens (Zählmarke)"""

    def claim():
        """Get a (public token, private token) tuple.

        Raises ValueError when there are no tokens.

        """

    def load(csv_file):
        """Load tokens from csv file (file like object)."""
