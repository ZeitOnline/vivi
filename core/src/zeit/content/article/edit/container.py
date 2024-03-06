import lxml.etree

import zeit.edit.container


class TypeOnTagContainer(zeit.edit.container.Base):
    _find_item = lxml.etree.XPath(
        './/*[@cms:__name__ = $name]', namespaces={'cms': 'http://namespaces.zeit.de/CMS/cp'}
    )

    def _get_element_type(self, xml_node):
        if not isinstance(xml_node.tag, str):
            return '__invalid__'
        return xml_node.tag

    def _set_default_key(self, xml_node):
        key = xml_node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if not key:
            key = self._generate_block_id()
            xml_node.set('{http://namespaces.zeit.de/CMS/cp}__name__', key)
            self._p_changed = True
        return key

    def index(self, value):
        return self.values().index(value)
