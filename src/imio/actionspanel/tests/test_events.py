# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from imio.actionspanel.adapters import ContentDeletableAdapter
from imio.actionspanel.browser.views import No
from imio.actionspanel.events import onObjWillBeRemoved
from imio.actionspanel.interfaces import IContentDeletable
from imio.actionspanel.testing import IntegrationTestCase
from imio.actionspanel.testing import MEMBER_ID
from OFS.event import ObjectWillBeRemovedEvent
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides


class IDependentContent(Interface):
    """Content of a dependent registering its own IContentDeletable adapter."""


class INotDeletable(Interface):
    """Content the dependent's adapter does not allow to delete."""


class DependentDeletableAdapter(ContentDeletableAdapter):
    """Records the initiator, refuses with a reason for INotDeletable content."""

    calls = []

    def mayDelete(self, initiator=None, **kwargs):
        self.calls.append((self.context.getId(), initiator.getId()))
        if INotDeletable.providedBy(self.context):
            return No(u"{0} is used elsewhere".format(self.context.getId()))
        return super(DependentDeletableAdapter, self).mayDelete(initiator=initiator, **kwargs)


class TestEvents(IntegrationTestCase):

    def setUp(self):
        super(TestEvents, self).setUp()
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DependentDeletableAdapter, (IDependentContent, ), IContentDeletable)
        self.addCleanup(gsm.unregisterAdapter, DependentDeletableAdapter, (IDependentContent, ), IContentDeletable)
        DependentDeletableAdapter.calls = []
        self.folder = api.content.create(container=self.portal, type="Folder", id="folder", title="Folder")
        self.doc = api.content.create(container=self.folder, type="Document", id="doc", title="Doc")

    def test_onObjWillBeRemoved(self):
        # the subscriber registered by dependents (testing.zcml) checks mayDelete
        alsoProvides(self.folder, IDependentContent)
        alsoProvides(self.doc, IDependentContent, INotDeletable)
        # default message when mayDelete returns False
        login(self.portal, MEMBER_ID)
        with self.assertRaises(Unauthorized) as cm:
            onObjWillBeRemoved(self.folder, ObjectWillBeRemovedEvent(self.folder, self.portal, "folder"))
        self.assertEqual(str(cm.exception), "You can not delete this element!")
        # the Plone site is not checked
        event = ObjectWillBeRemovedEvent(self.portal, self.portal.aq_parent, "plone")
        self.assertIsNone(onObjWillBeRemoved(self.portal, event))
        # message of appy's No
        login(self.portal, TEST_USER_NAME)
        with self.assertRaises(Unauthorized) as cm:
            api.content.delete(self.doc)
        self.assertEqual(str(cm.exception), "doc is used elsewhere")
        self.assertIn("doc", self.folder.objectIds())
        # the initially deleted element is passed as initiator, also to the contained elements
        noLongerProvides(self.doc, INotDeletable)
        DependentDeletableAdapter.calls = []
        api.content.delete(self.folder)
        self.assertNotIn("folder", self.portal.objectIds())
        self.assertEqual(sorted(DependentDeletableAdapter.calls), [("doc", "folder"), ("folder", "folder")])
