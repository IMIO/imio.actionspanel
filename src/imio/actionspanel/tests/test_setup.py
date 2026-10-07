# -*- coding: utf-8 -*-
from imio.actionspanel.interfaces import IActionsPanelLayer
from imio.actionspanel.testing import IntegrationTestCase
from plone import api
from plone.browserlayer.utils import registered_layers
from zope.i18n import translate


class TestSetup(IntegrationTestCase):

    def test_browserlayer(self):
        self.assertIn(IActionsPanelLayer, registered_layers())

    def test_metadata(self):
        setup = self.portal.portal_setup
        self.assertEqual(setup.getLastVersionForProfile("imio.actionspanel:default"), ("2000", ))
        # dependencies
        self.assertNotEqual(setup.getLastVersionForProfile("imio.history:default"), "unknown")
        self.assertNotEqual(setup.getLastVersionForProfile("collective.fingerpointing:default"), "unknown")

    def test_cssregistry(self):
        self.assertIn("++resource++imio.actionspanel/actionspanel.css", self.portal.portal_css.getResourceIds())

    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        self.assertIn("++resource++imio.actionspanel/actionspanel.js", resource_ids)
        self.assertIn("actions_panel_javascript_variables.js", resource_ids)

    def test_registry(self):
        self.assertIsNone(
            api.portal.get_registry_record("imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions"))

    def test_skins(self):
        skins = self.portal.portal_skins
        self.assertIn("actionspanel_plone", skins.objectIds())
        self.assertEqual(skins.getSkinPath(skins.getDefaultSkin()).split(",")[:2], ["custom", "actionspanel_plone"])
        # skin elements relied on by dependents
        for name in ("folder_position_typeaware", "rename_icon.gif", "extedit_icon.png"):
            self.assertTrue(self.portal.restrictedTraverse(name))

    def test_actions(self):
        actions = self.portal.portal_actions
        icons = dict((action_id, actions.object_buttons[action_id].icon_expr)
                     for action_id in ("cut", "copy", "paste", "delete", "rename"))
        self.assertEqual(icons, {
            "cut": "string:$portal_url/cut_icon.png",
            "copy": "string:$portal_url/copy_icon.png",
            "paste": "string:$portal_url/paste_icon.png",
            "delete": "string:$portal_url/delete_icon.png",
            "rename": "string:$portal_url/rename_icon.gif"})
        self.assertEqual(actions.document_actions.extedit.icon_expr, "string:$portal_url/extedit_icon.png")

    def test_locales(self):
        self.assertEqual(
            translate(u"delete_confirm_message", domain="imio.actionspanel", target_language="fr"),
            u"\xcates-vous certain de vouloir supprimer d\xe9finitivement cet \xe9l\xe9ment de l'application?")
        self.assertEqual(
            translate(u"delete_confirm_message", domain="imio.actionspanel", target_language="es"),
            u"\xbfEst\xe1s seguro de que deseas eliminar permanentemente este elemento de la aplicaci\xf3n?")
        self.assertEqual(
            translate(u"delete_element", domain="plone", target_language="fr"), u"Supprimer un \xe9l\xe9ment")
