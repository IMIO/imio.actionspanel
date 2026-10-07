# -*- coding: utf-8 -*-
from imio.actionspanel.browser.registry import IImioActionsPanelConfig
from imio.actionspanel.testing import IntegrationTestCase
from z3c.form.validator import Data
from zope.interface import Invalid


class TestIImioActionsPanelConfig(IntegrationTestCase):
    def validate(self, data):
        """Validate the invariants as the registry record edit form does (field named 'value')."""
        data = Data(IImioActionsPanelConfig, data, self.portal)
        IImioActionsPanelConfig.validateInvariants(data)
        return data._Data_data___

    def assertInvalid(self, values, msgid, mapping):
        with self.assertRaises(Invalid) as cm:
            self.validate({"value": values})
        self.assertEqual(cm.exception.args[0], msgid)
        self.assertEqual(cm.exception.args[0].mapping, mapping)

    def test_validateSettings(self):
        # nothing to validate
        self.assertEqual(self.validate({}), {})
        self.assertEqual(self.validate({"value": None}), {"value": None})
        with self.assertRaises(Invalid) as cm:
            self.validate({"transitions": []})
        self.assertEqual(cm.exception.args[0], "Internal validation error")
        # values are stripped and completed with '|'
        self.assertEqual(
            self.validate(
                {
                    "value": [
                        " Document.publish ",
                        "Document.submit|@@my_confirm",
                        "Folder.publish|",
                    ]
                }
            ),
            {
                "value": [
                    "Document.publish|",
                    "Document.submit|@@my_confirm",
                    "Folder.publish|",
                ]
            },
        )
        # invalid values
        self.assertInvalid(
            ["Document. publish"],
            "The value cannot contain space: line ${i}, '${val}'",
            {"i": 1, "val": "Document. publish"},
        )
        self.assertInvalid(
            ["Document.publish", "Document.publish|@@my_confirm"],
            "The transition value '${val}' is set multiple times.",
            {"val": "Document.publish"},
        )
        msgid = "The first part must contain one dot to separate the type and the transition: line ${i}, '${val}'"
        self.assertInvalid(
            ["Document.publish", "Documentpublish"],
            msgid,
            {"i": 2, "val": "Documentpublish"},
        )
        self.assertInvalid([".publish"], msgid, {"i": 1, "val": ".publish"})
        self.assertInvalid(
            ["Document.publish.now"], msgid, {"i": 1, "val": "Document.publish.now"}
        )
        self.assertInvalid(
            ["Unknown.publish"],
            "This portal_type doesn't exist: line ${i}, '${val}'",
            {"i": 1, "val": "Unknown.publish"},
        )
        self.assertInvalid(
            ["Document.unknown"],
            "This transition id isn't valid for the portal_type: line ${i}, '${val}'",
            {"i": 1, "val": "Document.unknown"},
        )
