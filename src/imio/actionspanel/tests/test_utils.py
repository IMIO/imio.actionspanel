# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from imio.actionspanel.testing import IntegrationTestCase
from imio.actionspanel.testing import MEMBER_ID
from imio.actionspanel.utils import findViewableURL
from imio.actionspanel.utils import unrestrictedRemoveGivenObject
from plone import api
from plone.app.testing import login


NOT_VIEWABLE_MSG = (
    u"You have been redirect here because the action you just made have made thelement no more "
    u"viewable to you.",
    u"warning",
)


class TestUtils(IntegrationTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.folder = api.content.create(
            container=self.portal, type="Folder", id="folder", title="Folder"
        )
        self.doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.doc2 = api.content.create(
            container=self.folder, type="Document", id="doc2", title="Doc 2"
        )

    def test_unrestrictedRemoveGivenObject(self):
        api.user.grant_roles(username=MEMBER_ID, obj=self.folder, roles=["Reader"])
        login(self.portal, MEMBER_ID)
        self.assertRaises(Unauthorized, self.folder.manage_delObjects, ["doc2"])
        # removed as a Manager, the caller checks the permissions
        unrestrictedRemoveGivenObject(self.doc)
        self.assertEqual(self.folder.objectIds(), ["doc2"])
        self.assertNotIn("Manager", api.user.get_roles())

    def test_findViewableURL(self):
        # viewable: HTTP_REFERER
        self.assertEqual(findViewableURL(self.doc, self.request), "")
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(
            findViewableURL(self.doc, self.request), "http://nohost/plone/folder/doc"
        )
        self.assertEqual(self.status_messages(), [])
        # not viewable, HTTP_REFERER is the element: first viewable parent
        member = api.user.get(MEMBER_ID)
        self.assertEqual(
            findViewableURL(self.doc, self.request, member), "http://nohost/plone"
        )
        self.assertEqual(self.status_messages(), [NOT_VIEWABLE_MSG])
        api.content.transition(self.folder, "publish")
        self.assertEqual(
            findViewableURL(self.doc, self.request, member),
            "http://nohost/plone/folder",
        )
        # not viewable, HTTP_REFERER is another page
        self.request["HTTP_REFERER"] = "http://nohost/plone/dashboard"
        self.assertEqual(
            findViewableURL(self.doc, self.request, member),
            "http://nohost/plone/dashboard",
        )
        # Known issue: a referer starting with the element URL is considered as the element
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc2"
        self.assertEqual(
            findViewableURL(self.doc, self.request, member),
            "http://nohost/plone/folder",
        )
        # Known issue: no HTTP_REFERER, '' is returned
        self.request["HTTP_REFERER"] = ""
        self.assertEqual(findViewableURL(self.doc, self.request, member), "")
        # the current user by default
        login(self.portal, MEMBER_ID)
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(
            findViewableURL(self.doc, self.request), "http://nohost/plone/folder"
        )
