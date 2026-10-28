# -*- coding: utf-8 -*-
from zope.configuration import xmlconfig
from zope.testing.cleanup import cleanUp

import unittest


# site.zcml of an instance having the package in its `zcml` option (plone.recipe.zope2instance):
# the package is loaded before the Products (Products.CMFCore permissions, Products.CMFPlone)
SITE_ZCML = """
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:five="http://namespaces.zope.org/five">
  <include package="Products.Five" />
  <five:loadProducts file="meta.zcml" />
  <include package="imio.actionspanel" />
  <five:loadProducts />
</configure>
"""


class TestZCML(unittest.TestCase):
    def tearDown(self):
        cleanUp()

    def test_load_before_products(self):
        xmlconfig.string(SITE_ZCML)
