# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class ISection(zope.interface.Interface):
    """Marks a z.c.repository:IFolder as a section.

    Content objects inside a section are marked with specific marker
    interfaces, so they can have their behaviour/UI tailored specifically.
    (Marking happens on z.c.repository:IBeforeObjectAddEvent and
    z.c.checkout:IAfterCheckoutEvent.)

    Usage:
    * Create a specific section interface by inheriting from this,
      e.g. IMySection(ISection), and apply it to the folder.
    * Create an interface with which all content objects inside the folder
      shall be marked. Must inherit from ISectionMarker.
      Register it as an adapter from IMySection to ISectionMarker.
    * (Optional) Create interfaces with which specific content types
      inside the folder shall be marked. Must inherit from ISectionMarker.
      Register these as an adapter from IMySection to ISectionMarker,
      with the type identifier as the adapter name.
    """

    def apply_markers(content):
        """Apply marker interfaces to content object."""


class ISectionMarker(zope.interface.Interface):
    """Marks an interface as a marker that belongs to a section.

    This is used both to look up which marker interfaces to apply
    to content objects inside an ISection, and to remove all section markers
    when a content object is moved to another folder.
    """
