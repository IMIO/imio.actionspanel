# -*- coding: utf-8 -*-
from imio.actionspanel.adapters import ContentDeletableAdapter
from imio.actionspanel.adapters import DeletedChildrenHistoryAdapter
from imio.actionspanel.interfaces import IContentDeletable
from imio.actionspanel.testing import IntegrationTestCase
from imio.actionspanel.testing import MEMBER_ID
from imio.history.interfaces import IImioHistory
from imio.history.utils import add_event_to_history
from plone import api
from plone.app.testing import login
from zope.component import getAdapter


class TestContentDeletableAdapter(IntegrationTestCase):

    def test_mayDelete(self):
        folder = api.content.create(container=self.portal, type="Folder", id="folder", title="Folder")
        doc = api.content.create(container=folder, type="Document", id="doc", title="Doc")
        adapter = IContentDeletable(doc)
        self.assertIsInstance(adapter, ContentDeletableAdapter)
        self.assertTrue(adapter.mayDelete())
        self.assertTrue(adapter.mayDelete(initiator=folder, other="value"))
        # 'Delete objects' on the element, not on its parent
        doc2 = api.content.create(container=folder, type="Document", id="doc2", title="Doc 2")
        api.user.grant_roles(username=MEMBER_ID, obj=doc2, roles=["Owner"])
        login(self.portal, MEMBER_ID)
        self.assertFalse(IContentDeletable(doc).mayDelete())
        self.assertTrue(IContentDeletable(doc2).mayDelete())
        self.assertFalse(IContentDeletable(folder).mayDelete())


class TestDeletedChildrenHistoryAdapter(IntegrationTestCase):

    def setUp(self):
        super(TestDeletedChildrenHistoryAdapter, self).setUp()
        self.folder = api.content.create(container=self.portal, type="Folder", id="folder", title="Folder")

    def test_getHistory(self):
        adapter = getAdapter(self.folder, IImioHistory, "deleted_children")
        self.assertIsInstance(adapter, DeletedChildrenHistoryAdapter)
        self.assertEqual(adapter.getHistory(), [])
        add_event_to_history(self.folder, "deleted_children_history", "delete_element", comments=u"My comment")
        history = getAdapter(self.folder, IImioHistory, "deleted_children").getHistory()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["type"], "deleted_children")
        self.assertEqual(history[0]["action"], "delete_element")
        self.assertEqual(history[0]["comments"], u"My comment")

    def test_historyLastEventHasComments(self):
        self.assertFalse(getAdapter(self.folder, IImioHistory, "deleted_children").historyLastEventHasComments())
        add_event_to_history(self.folder, "deleted_children_history", "delete_element", comments=u"My comment")
        self.assertTrue(getAdapter(self.folder, IImioHistory, "deleted_children").historyLastEventHasComments())
        add_event_to_history(self.folder, "deleted_children_history", "delete_element")
        self.assertFalse(getAdapter(self.folder, IImioHistory, "deleted_children").historyLastEventHasComments())
