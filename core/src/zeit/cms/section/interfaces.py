import zope.interface

import zeit.cms.interfaces


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


class IRessortSection(zope.interface.Interface):
    """Marks an ``ICommonMetadata.ressort`` value as a section.

    Usage:

    * Create a spefic section interface, e.g. IMySection(ISection)
    * Register it an adapter to IRessortSection with the name of the ressort::

        <adapter
          factory="IMySection"
          for="zeit.cms.content.interfaces.ICommonMetadata"
          provides="zeit.cms.section.interfaces.IRessortSection"
          name="MyRessort"
          />
    """


class IZONSection(ISection):
    """Marker for the ZEIT ONLINE section (which is 95% of all content ;-)"""


class IZONContent(zeit.cms.interfaces.ICMSContent, ISectionMarker):
    pass
