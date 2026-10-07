# -*- coding: utf-8 -*-
from imio.actionspanel.testing import IntegrationTestCase
from plone import api


class TestFolderPositionTypeaware(IntegrationTestCase):
    """Skin script skins/actionspanel_plone/folder_position_typeaware.cpy."""

    def setUp(self):
        super(TestFolderPositionTypeaware, self).setUp()
        self.folder = api.content.create(
            container=self.portal, type="Folder", id="folder", title="Folder"
        )
        for obj_id, portal_type in (
            ("n0", "News Item"),
            ("d1", "Document"),
            ("n2", "News Item"),
            ("d3", "Document"),
            ("n4", "News Item"),
        ):
            api.content.create(
                container=self.folder, type=portal_type, id=obj_id, title=obj_id
            )

    def move(self, position, obj_id):
        self.folder.restrictedTraverse("folder_position_typeaware")(
            position=position, id=obj_id
        )
        return self.folder.objectIds()

    def test_folder_position_typeaware(self):
        # up and down skip the elements of other portal_types
        self.assertEqual(self.move("up", "d3"), ["n0", "d3", "d1", "n2", "n4"])
        self.assertEqual(self.move("down", "d3"), ["n0", "d1", "d3", "n2", "n4"])
        self.assertEqual(self.move("Down", "d1"), ["n0", "d3", "d1", "n2", "n4"])
        # no element of the same portal_type after: not moved
        self.assertEqual(self.move("down", "d1"), ["n0", "d3", "d1", "n2", "n4"])
        self.assertEqual(self.move("down", "n4"), ["n0", "d3", "d1", "n2", "n4"])
        # top and bottom are not portal_type aware
        self.assertEqual(self.move("top", "d1"), ["d1", "n0", "d3", "n2", "n4"])
        self.assertEqual(self.move("bottom", "d1"), ["n0", "d3", "n2", "n4", "d1"])
        # portal message and redirect to the template_id of the request (arrows URL), folder_contents by default
        self.assertEqual(
            self.status_messages()[-1], (u"Item's position has changed.", u"info")
        )
        self.assertEqual(
            self.request.response.getHeader("location"),
            "http://nohost/plone/folder/folder_contents",
        )
        self.set_form({"template_id": "http://nohost/plone/folder/view"})
        self.move("up", "n2")
        self.assertEqual(
            self.request.response.getHeader("location"),
            "http://nohost/plone/folder/view",
        )
