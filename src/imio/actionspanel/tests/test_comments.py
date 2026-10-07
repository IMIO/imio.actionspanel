# -*- coding: utf-8 -*-
from imio.actionspanel.browser.comments import BaseCommentsView
from imio.actionspanel.testing import IntegrationTestCase
from plone import api


TRANSITIONS_RECORD = "imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions"
SUBMIT_TITLE = u"Member submits content for publication"


class BaseCommentsTestCase(IntegrationTestCase):

    def setUp(self):
        super(BaseCommentsTestCase, self).setUp()
        self.folder = api.content.create(container=self.portal, type="Folder", id="folder", title="Folder")
        self.doc = api.content.create(container=self.folder, type="Document", id="doc", title="Doc")
        self.request["REQUEST_METHOD"] = "GET"


class TestBaseCommentsView(BaseCommentsTestCase):

    def test___init__(self):
        view = self.doc.restrictedTraverse("@@triggertransition")
        self.assertEqual(view.actionspanel_view_name, "actions_panel")
        self.assertFalse(view.force_redirect_after_transition)
        self.set_form({"actionspanel_view_name": "my_actions_panel", "force_redirect_after_transition": "1"})
        view = self.doc.restrictedTraverse("@@triggertransition")
        self.assertEqual(view.actionspanel_view_name, "my_actions_panel")
        self.assertTrue(view.force_redirect_after_transition)
        self.set_form({"force_redirect_after_transition": "0"})
        self.assertFalse(self.doc.restrictedTraverse("@@triggertransition").force_redirect_after_transition)

    def test___call__(self):
        # the confirmation form
        self.set_form({"transition": "submit"})
        rendered = self.doc.restrictedTraverse("@@triggertransition")()
        self.assertIn('id="commentsForm"', rendered)
        self.assertIn('name="form.buttons.save"', rendered)
        self.assertIn('name="form.buttons.cancel"', rendered)
        self.assertIn(SUBMIT_TITLE, rendered)
        # the transition is not to confirm: the save button reloads the page
        self.assertIn("window.location.href=window.location.href;", rendered)
        api.portal.set_registry_record(TRANSITIONS_RECORD, ["Document.submit|"])
        rendered = self.doc.restrictedTraverse("@@triggertransition")()
        self.assertIn(
            "applyWithComments(baseUrl='http://nohost/plone/folder/doc', viewName='@@triggertransition', "
            "{'transition': 'submit'}, this, force_redirect=0, event_id='ap_transition_triggered');",
            rendered)
        # cancelled: back to the element
        self.set_form({"form.buttons.cancel": "Cancel"})
        self.doc.restrictedTraverse("@@triggertransition")()
        self.assertEqual(self.request.response.getHeader("location"), "http://nohost/plone/folder/doc")
        self.assertEqual(api.content.get_state(self.doc), "private")
        self.set_form({"form.buttons.cancel": None})
        # saved or submitted: applied
        self.set_form({"form.buttons.save": "Save"})
        self.assertIsNone(self.doc.restrictedTraverse("@@triggertransition")())
        self.assertEqual(api.content.get_state(self.doc), "pending")
        self.set_form({"form.buttons.save": None})
        self.set_form({"form.submitted": "1", "transition": "retract"})
        self.doc.restrictedTraverse("@@triggertransition")()
        self.assertEqual(api.content.get_state(self.doc), "private")

    def test_apply(self):
        self.assertRaises(NotImplementedError, BaseCommentsView(self.doc, self.request).apply, None)

    def test__get_actions_panel_view(self):
        view = self.doc.restrictedTraverse("@@triggertransition")
        actions_panel = view._get_actions_panel_view()
        self.assertEqual(actions_panel.__name__, "actions_panel")
        self.assertEqual(actions_panel.context, self.doc)
        self.assertFalse(actions_panel.forceRedirectAfterTransition)
        # stored
        self.assertIs(view._get_actions_panel_view(), actions_panel)
        # actionspanel_view_name and force_redirect_after_transition from the request
        self.set_form({"actionspanel_view_name": "async_actions_panel", "force_redirect_after_transition": "1"})
        actions_panel = self.doc.restrictedTraverse("@@triggertransition")._get_actions_panel_view()
        self.assertEqual(actions_panel.__name__, "async_actions_panel")
        self.assertTrue(actions_panel.forceRedirectAfterTransition)


class TestConfirmTransitionView(BaseCommentsTestCase):

    def test_apply(self):
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder"
        self.set_form({"transition": "submit", "comment": "My comment", "redirect": "1"})
        view = self.doc.restrictedTraverse("@@triggertransition")
        self.assertEqual(view.apply(view._get_actions_panel_view()), "http://nohost/plone/folder")
        self.assertEqual(api.content.get_state(self.doc), "pending")
        self.assertEqual(self.doc.workflow_history["simple_publication_workflow"][-1]["comments"], "My comment")
        # Known issue: actionspanel.js sends 'redirect:int', 1 is not '1', so no redirect
        self.set_form({"transition": "retract", "comment": "", "redirect": 1})
        view = self.doc.restrictedTraverse("@@triggertransition")
        self.assertIsNone(view.apply(view._get_actions_panel_view()))
        self.assertEqual(api.content.get_state(self.doc), "private")
        # no redirect
        self.set_form({"redirect": None})
        self.set_form({"transition": "publish"})
        view = self.doc.restrictedTraverse("@@triggertransition")
        self.assertIsNone(view.apply(view._get_actions_panel_view()))
        self.assertEqual(api.content.get_state(self.doc), "published")

    def test_init_transition(self):
        self.set_form({"transition": "submit"})
        self.assertEqual(self.doc.restrictedTraverse("@@triggertransition").init_transition(), {})
        api.portal.set_registry_record(TRANSITIONS_RECORD, ["Document.submit|"])
        self.assertEqual(
            self.doc.restrictedTraverse("@@triggertransition").init_transition(), {"id": "submit", "confirm": False})
        # transition not available
        self.set_form({"transition": "retract"})
        self.assertEqual(self.doc.restrictedTraverse("@@triggertransition").init_transition(), {})

    def test_transition_title(self):
        self.set_form({"transition": "submit"})
        self.assertEqual(self.doc.restrictedTraverse("@@triggertransition").transition_title(), SUBMIT_TITLE)
        self.set_form({"transition": "retract"})
        self.assertIsNone(self.doc.restrictedTraverse("@@triggertransition").transition_title())


class TestDeleteWithCommentsView(BaseCommentsTestCase):

    def test___call__(self):
        uid = self.doc.UID()
        self.set_form({"uid": uid})
        view = self.doc.restrictedTraverse("@@delete_with_comments")
        rendered = view()
        self.assertEqual(view.obj, self.doc)
        self.assertIn('id="commentsForm"', rendered)
        self.assertIn('<h1 class="documentFirstHeading highlightValue">Doc</h1>', rendered)
        self.assertIn('name="form.buttons.save"', rendered)
        # the save button sends the UID of the context, not the uid parameter (see Known issues)
        self.assertIn(
            "applyWithComments(baseUrl='http://nohost/plone/folder/doc', viewName='@@delete_with_comments', "
            "extraData={{'uid': '{0}', 'preComment': 'Doc'}}, this);".format(uid),
            rendered)
        # cancelled: back to the context
        self.set_form({"form.buttons.cancel": "Cancel"})
        self.doc.restrictedTraverse("@@delete_with_comments")()
        self.assertEqual(self.request.response.getHeader("location"), "http://nohost/plone/folder/doc")
        self.assertIn("doc", self.folder.objectIds())
        self.set_form({"form.buttons.cancel": None})
        # submitted: deleted
        self.set_form({"form.submitted": "1"})
        self.doc.restrictedTraverse("@@delete_with_comments")()
        self.assertNotIn("doc", self.folder.objectIds())

    def test_apply(self):
        self.set_form({"uid": self.doc.UID(), "comment": "Doc\n\nMy comment"})
        view = self.doc.restrictedTraverse("@@delete_with_comments")
        self.assertEqual(view.apply(None), "")
        self.assertNotIn("doc", self.folder.objectIds())
        self.assertEqual(self.status_messages(), [(u"object_deleted", u"info")])
        event = self.folder.deleted_children_history[-1]
        self.assertEqual(event["action"], "delete_element")
        self.assertEqual(event["comments"], "Doc\n\nMy comment")
        # @@delete_givenuid is called on the portal: redirect to the first viewable parent
        doc = api.content.create(container=self.folder, type="Document", id="doc", title="Doc")
        self.set_form({"uid": doc.UID()})
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(view.apply(None), "http://nohost/plone/folder")
        self.assertEqual(len(self.folder.deleted_children_history), 2)

    def test_element_title(self):
        self.set_form({"uid": self.doc.UID()})
        view = self.folder.restrictedTraverse("@@delete_with_comments")
        view()
        self.assertEqual(view.element_title(), "Doc")

    def test_pre_comment(self):
        self.doc.setTitle("Doc's title")
        self.set_form({"uid": self.doc.UID()})
        view = self.doc.restrictedTraverse("@@delete_with_comments")
        # escaped in the onclick attribute, actionspanel.js puts the quote back
        self.assertIn("'preComment': 'Doc&amp;#39;s title'", view())
        self.assertEqual(view.pre_comment(), "Doc&#39;s title")
