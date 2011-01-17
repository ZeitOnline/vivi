# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt


def contains_element(list, element):
    """lxml.objectify elements are equal if their text contents are equal,
    which is not at all sufficient for filtering elements via xpath, so we
    provide a custom comparision function that includes the tag name and
    attributes.
    """
    for candidate in list:
        if element_equal(candidate, element):
            return True
    return False


def element_equal(a, b):
    return element_properties(a) == element_properties(b)


def element_properties(element):
    return (element.tag, element.text, element.attrib)
