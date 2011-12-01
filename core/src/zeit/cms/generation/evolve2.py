# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.cms.relation.relation
import zeit.cms.relation.interfaces


def update(root):
    site_manager = zope.component.getSiteManager()
    relations = site_manager['relations']
    relations._catalog._relTools['load'] = \
        relations._catalog._attrs['related']['load'] = \
        zeit.cms.relation.relation._load_content
    relations._catalog._relTools['dump'] = \
        relations._catalog._attrs['related']['dump'] = \
        zeit.cms.relation.relation._dump_content
    relations._catalog._attrs['related']['callable'] = (
        zeit.cms.content.related.related)

    relations.__class__ = zeit.cms.relation.relation.Relations


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
