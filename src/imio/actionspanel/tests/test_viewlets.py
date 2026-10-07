# -*- coding: utf-8 -*-
from imio.actionspanel.browser.viewlets import ActionsPanelViewlet
from imio.actionspanel.testing import IntegrationTestCase
from plone import api
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class TestActionsPanelViewlet(IntegrationTestCase):

    def setUp(self):
        super(TestActionsPanelViewlet, self).setUp()
        self.folder = api.content.create(container=self.portal, type="Folder", id="folder", title="Folder")
        self.doc = api.content.create(container=self.folder, type="Document", id="doc", title="Doc")
        # the element view is displayed
        self.request.set("ACTUAL_URL", self.doc.absolute_url())

    def viewlet(self, obj):
        """The viewlet registered in testing.zcml, as dependents register it."""
        view = BrowserView(obj, self.request)
        manager = getMultiAdapter((obj, self.request, view), IViewletManager, name="plone.belowcontentbody")
        viewlet = getMultiAdapter((obj, self.request, view, manager), IViewlet, name="imio.actionspanel")
        viewlet.update()
        return viewlet

    def test_show(self):
        self.assertTrue(self.viewlet(self.doc).show())
        # not the view of the element
        self.assertFalse(self.viewlet(self.folder).show())
        # not in an overlay
        self.request.set("ajax_load", "1")
        self.assertFalse(self.viewlet(self.doc).show())

    def test_renderViewlet(self):
        viewlet = self.viewlet(self.doc)
        self.assertIsInstance(viewlet, ActionsPanelViewlet)
        self.assertEqual(viewlet.params, {"useIcons": False, "showEdit": False})
        self.assertEqual(
            viewlet.renderViewlet(), self.doc.restrictedTraverse("@@actions_panel")(useIcons=False, showEdit=False))
        self.assertIn("apButtonWF_submit", viewlet.renderViewlet())
        self.assertNotIn("apButtonAction_edit", viewlet.renderViewlet())
        # params of a dependent
        viewlet.params = {"useIcons": False, "showEdit": True}
        self.assertIn("apButtonAction_edit", viewlet.renderViewlet())
        # not shown
        self.assertIsNone(self.viewlet(self.folder).renderViewlet())

    def test_render(self):
        viewlet = self.viewlet(self.doc)
        self.assertFalse(viewlet.is_async)
        self.assertEqual(viewlet.render().strip(), viewlet.renderViewlet().strip())
        # asynchronous: actionspanel.js loads @@async_actions_panel in the div
        viewlet.is_async = True
        rendered = viewlet.render()
        self.assertIn('id="async_actions_panel"', rendered)
        self.assertIn('data-use-icons="false"', rendered)
        self.assertIn('data-show-edit="false"', rendered)
        self.assertIn('src="http://nohost/plone/spinner_small.gif"', rendered)
        self.assertNotIn("apButtonWF_submit", rendered)
        # not shown
        self.assertEqual(self.viewlet(self.folder).render().strip(), "")
