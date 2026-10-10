# -*- coding: utf-8 -*-
from imio.actionspanel.interfaces import IActionsPanelLayer
from imio.actionspanel.testing import IntegrationTestCase
from plone import api
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from zope.i18n import translate


class TestSetup(IntegrationTestCase):
    def test_browserlayer(self):
        self.assertIn(IActionsPanelLayer, registered_layers())

    def test_metadata(self):
        setup = self.portal.portal_setup
        self.assertEqual(
            setup.getLastVersionForProfile("imio.actionspanel:default"), ("3000",)
        )
        # dependencies, imio.helpers: helpers.js used by actionspanel.js
        for profile in ("imio.helpers:default", "imio.history:default"):
            self.assertNotEqual(setup.getLastVersionForProfile(profile), "unknown")
        self.assertNotEqual(
            setup.getLastVersionForProfile("collective.fingerpointing:default"),
            "unknown",
        )

    def test_bundles(self):
        for name, compiled in (
            ("imio-actionspanel", "jscompilation"),
            ("imio-actionspanel", "csscompilation"),
            ("imio-actionspanel-variables", "jscompilation"),
            # imio.helpers (dependency)
            ("imio-helpers", "jscompilation"),
        ):
            prefix = "plone.bundles/{0}.".format(name)
            self.assertTrue(api.portal.get_registry_record(prefix + "enabled"))
            path = api.portal.get_registry_record(prefix + compiled)
            # the resource is served
            self.assertTrue(self.portal.restrictedTraverse(path))
        self.assertEqual(
            api.portal.get_registry_record("plone.bundles/imio-actionspanel.depends"),
            "plone",
        )
        # loaded before the inline scripts of the page (preventDefaultClick)
        for key in ("load_async", "load_defer"):
            self.assertFalse(
                api.portal.get_registry_record("plone.bundles/imio-actionspanel." + key)
            )
        self.assertEqual(
            api.portal.get_registry_record(
                "plone.bundles/imio-actionspanel.jscompilation"
            ),
            "++resource++imio.actionspanel/actionspanel.js",
        )

    def test_registry(self):
        self.assertIsNone(
            api.portal.get_registry_record(
                "imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions"
            )
        )

    def test_resources(self):
        # former skin elements relied on by dependents (Plone 4 skin layer actionspanel_plone)
        for name in (
            "folder_position",
            "folder_position_typeaware",
            "++resource++imio.actionspanel/rename_icon.gif",
            "++resource++imio.actionspanel/extedit_icon.png",
        ):
            self.assertTrue(self.portal.restrictedTraverse(name))
        self.assertNotIn("actionspanel_plone", self.portal.portal_skins.objectIds())

    def test_actions(self):
        # Plone's action icons are not overridden anymore (Plone 6 icon names)
        actions = self.portal.portal_actions
        icons = dict(
            (action_id, actions.object_buttons[action_id].icon_expr)
            for action_id in ("cut", "copy", "paste", "delete", "rename")
        )
        self.assertEqual(
            icons,
            {
                "cut": "string:plone-cut",
                "copy": "string:plone-copy",
                "paste": "string:plone-paste",
                "delete": "string:plone-delete",
                "rename": "string:plone-rename",
            },
        )

    def test_uninstall(self):
        installer = get_installer(self.portal, self.request)
        installer.uninstall_product("imio.actionspanel")
        self.assertFalse(installer.is_product_installed("imio.actionspanel"))
        self.assertNotIn(IActionsPanelLayer, registered_layers())
        records = api.portal.get_tool("portal_registry").records
        for name in (
            "plone.bundles/imio-actionspanel.jscompilation",
            "plone.bundles/imio-actionspanel-variables.jscompilation",
            "imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions",
        ):
            self.assertNotIn(name, records)

    def test_locales(self):
        self.assertEqual(
            translate(
                "delete_confirm_message",
                domain="imio.actionspanel",
                target_language="fr",
            ),
            "\xcates-vous certain de vouloir supprimer d\xe9finitivement cet \xe9l\xe9ment de l'application?",
        )
        self.assertEqual(
            translate(
                "delete_confirm_message",
                domain="imio.actionspanel",
                target_language="es",
            ),
            "\xbfEst\xe1s seguro de que deseas eliminar permanentemente este elemento de la aplicaci\xf3n?",
        )
        self.assertEqual(
            translate("delete_element", domain="plone", target_language="fr"),
            "Supprimer un \xe9l\xe9ment",
        )
