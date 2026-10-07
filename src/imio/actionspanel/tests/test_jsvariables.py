# -*- coding: utf-8 -*-
from imio.actionspanel.testing import IntegrationTestCase


class TestJSVariables(IntegrationTestCase):

    def test___call__(self):
        view = self.portal.restrictedTraverse("@@actions_panel_javascript_variables.js")
        # no English translation: the msgid
        self.assertEqual(view(), 'var delete_confirm_message = "delete_confirm_message";\n')
        self.assertEqual(self.request.response.getHeader("content-type"), "text/javascript;;charset=utf-8")
