# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from imio.actionspanel.browser.views import DEFAULT_CONFIRM_VIEW
from imio.actionspanel.browser.views import No
from imio.actionspanel.interfaces import IFolderContentsShowableMarker
from imio.actionspanel.testing import IntegrationTestCase
from imio.actionspanel.testing import MEMBER_ID
from OFS.interfaces import IObjectWillBeRemovedEvent
from OFS.ObjectManager import BeforeDeleteException
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.ActionInformation import Action
from Products.DCWorkflow.Guard import Guard
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides
from zope.interface import Interface


TRANSITIONS_RECORD = (
    "imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions"
)
SUBMIT_TITLE = u"Member submits content for publication"
PUBLISH_TITLE = u"Reviewer publishes content"


class INotRemovable(Interface):
    """Marker of content whose removal raises BeforeDeleteException."""


def raise_before_delete(obj, event):
    raise BeforeDeleteException("Can not delete {0}".format(obj.getId()))


class BaseViewsTestCase(IntegrationTestCase):
    def setUp(self):
        super(BaseViewsTestCase, self).setUp()
        self.folder = api.content.create(
            container=self.portal, type="Folder", id="folder", title="Folder"
        )
        self.doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.wf = self.wft["simple_publication_workflow"]


class TestActionsPanelView(BaseViewsTestCase):
    def panel(self, obj=None, **kwargs):
        """Return the @@actions_panel view of p_obj, called with p_kwargs."""
        view = (obj or self.doc).restrictedTraverse("@@actions_panel")
        view(**kwargs)
        return view

    def login_member(self, roles=("Reader",)):
        """Log in as the member, with p_roles on the folder."""
        api.user.grant_roles(username=MEMBER_ID, obj=self.folder, roles=roles)
        login(self.portal, MEMBER_ID)
        self.clean_request_caches()

    def test___init__(self):
        view = self.doc.restrictedTraverse("@@actions_panel")
        self.assertEqual(view.parent, self.folder)
        self.assertEqual(view.portal, self.portal)
        self.assertEqual(view.portal_url, "http://nohost/plone")
        self.assertEqual(
            view.SECTIONS_TO_RENDER,
            (
                "renderFolderContents",
                "renderEdit",
                "renderExtEdit",
                "renderTransitions",
                "renderArrows",
                "renderOwnDelete",
                "renderOwnDeleteWithComments",
                "renderActions",
                "renderAddContent",
                "renderHistory",
            ),
        )
        self.assertEqual(view.IGNORABLE_ACTIONS, ())
        self.assertEqual(view.ACCEPTABLE_ACTIONS, ())
        # portal and portal_url are cached in the request
        self.assertEqual(
            self.request.get("imio.actionspanel_portal_url_cachekey"),
            "http://nohost/plone",
        )
        self.assertEqual(
            self.request.get("imio.actionspanel_portal_cachekey"), self.portal
        )
        self.request.set("imio.actionspanel_portal_url_cachekey", "http://cached")
        view = self.doc.restrictedTraverse("@@actions_panel")
        self.assertEqual(view.portal_url, "http://cached")
        # both are computed again if one is missing
        self.request.set("imio.actionspanel_portal_cachekey", None)
        view = self.doc.restrictedTraverse("@@actions_panel")
        self.assertEqual(view.portal_url, "http://nohost/plone")

    def test___call__(self):
        view = self.doc.restrictedTraverse("@@actions_panel")
        # default parameters: icons, transitions, edit, own delete and actions
        rendered = view()
        self.assertIn(
            'id="actions-panel-identifier-{0}"'.format(self.doc.UID()), rendered
        )
        self.assertIn('align="right"', rendered)
        self.assertIn("http://nohost/plone/folder/doc/edit", rendered)
        self.assertIn("apButtonWF_submit", rendered)
        self.assertIn("confirmDeleteObject(", rendered)
        self.assertIn("apButtonAction_form_cut", rendered)
        self.assertNotIn("@@historyview", rendered)
        self.assertTrue(view.useIcons)
        self.assertTrue(view.hasActions)
        self.assertFalse(view.forceRedirectAfterTransition)
        self.assertEqual(view.kwargs, {})
        # own delete replaces Plone's delete action, only once when called several times
        self.assertEqual(view.IGNORABLE_ACTIONS, ("delete",))
        view()
        self.assertEqual(view.IGNORABLE_ACTIONS, ("delete",))
        self.assertNotIn("apButtonAction_form_delete", rendered)
        # as buttons, redirect after transition is forced
        view = self.doc.restrictedTraverse("@@actions_panel")
        rendered = view(useIcons=False, forceRedirectAfterTransition=False)
        self.assertIn('align="left"', rendered)
        self.assertTrue(view.forceRedirectAfterTransition)
        self.assertIn("force_redirect_after_transition=1", rendered)
        self.assertIn("apButtonAction_edit", rendered)
        # Plone's delete action is kept without own delete
        view = self.doc.restrictedTraverse("@@actions_panel")
        rendered = view(showOwnDelete=False)
        self.assertEqual(view.IGNORABLE_ACTIONS, ())
        self.assertNotIn("confirmDeleteObject(", rendered)
        self.assertIn("apButtonAction_form_delete", rendered)
        # 'delete' in ACCEPTABLE_ACTIONS takes precedence on showOwnDelete
        view = self.doc.restrictedTraverse("@@actions_panel")
        view.ACCEPTABLE_ACTIONS = ("delete",)
        rendered = view(showOwnDelete=True)
        self.assertFalse(view.showOwnDelete)
        self.assertNotIn("confirmDeleteObject(", rendered)
        self.assertIn("apButtonAction_form_delete", rendered)
        self.assertNotIn("apButtonAction_form_cut", rendered)
        # extra kwargs are stored and used by the sections
        view = self.doc.restrictedTraverse("@@actions_panel")
        rendered = view(edit_action_class="my-edit-class", edit_action_target="_blank")
        self.assertEqual(
            view.kwargs,
            {"edit_action_class": "my-edit-class", "edit_action_target": "_blank"},
        )
        self.assertIn('class="my-edit-class"', rendered)
        self.assertIn('target="_blank"', rendered)
        # nothing to render: nothing as buttons, "-" as icons
        params = dict(
            showTransitions=False,
            showEdit=False,
            showOwnDelete=False,
            showActions=False,
        )
        view = self.doc.restrictedTraverse("@@actions_panel")
        self.assertEqual(view(useIcons=False, **params).strip(), u"")
        self.assertFalse(view.hasActions)
        rendered = view(useIcons=True, **params)
        self.assertIn("<td>-</td>", rendered)

    def test_member(self):
        view = self.panel()
        self.assertEqual(view.member.getId(), TEST_USER_ID)
        self.assertEqual(
            self.request.get("imio.actionspanel_member_cachekey").getId(), TEST_USER_ID
        )
        # cached in the request
        login(self.portal, MEMBER_ID)
        self.assertEqual(view.member.getId(), TEST_USER_ID)
        self.clean_request_caches()
        self.assertEqual(view.member.getId(), MEMBER_ID)

    def test_isInFacetedNavigation(self):
        view = self.panel()
        self.assertFalse(view.isInFacetedNavigation())
        self.request.set("URL", "http://nohost/plone/folder/@@faceted_query")
        self.assertTrue(view.isInFacetedNavigation())

    def test__renderSections(self):
        view = self.panel()
        view.SECTIONS_TO_RENDER = ("renderEdit",)
        rendered = view._renderSections()
        self.assertIn("http://nohost/plone/folder/doc/edit", rendered)
        self.assertNotIn("apButtonWF_submit", rendered)
        # sections returning None (renderActions) are ignored
        view.SECTIONS_TO_RENDER = ("renderActions", "renderHistory")
        view.showActions = False
        self.assertEqual(view._renderSections(), "")

    def test_renderArrows(self):
        doc2 = api.content.create(
            container=self.folder, type="News Item", id="doc2", title="Doc 2"
        )
        doc3 = api.content.create(
            container=self.folder, type="Document", id="doc3", title="Doc 3"
        )
        move_url = "http://nohost/plone/folder/folder_position?position={0}&amp;id={1}&amp;template_id=http://nohost"
        # only as icons and when asked
        self.assertEqual(self.panel(useIcons=False, showArrows=True).renderArrows(), "")
        self.assertEqual(self.panel(showArrows=False).renderArrows(), "")
        # first element: down and bottom
        view = self.panel(showArrows=True)
        view.hasActions = False
        rendered = view.renderArrows()
        self.assertEqual(view.parentObjectIds, ["doc", "doc2", "doc3"])
        self.assertEqual(view.objId, "doc")
        self.assertIn(move_url.format("down", "doc"), rendered)
        self.assertIn(move_url.format("bottom", "doc"), rendered)
        self.assertNotIn("position=up", rendered)
        self.assertNotIn("position=top", rendered)
        self.assertIn("++resource++imio.actionspanel/arrowBottom.png", rendered)
        self.assertTrue(view.hasActions)
        # middle element: all the arrows
        rendered = self.panel(doc2, showArrows=True).renderArrows()
        for position in ("top", "up", "down", "bottom"):
            self.assertIn(move_url.format(position, "doc2"), rendered)
        # last element: up and top
        rendered = self.panel(doc3, showArrows=True).renderArrows()
        self.assertIn(move_url.format("up", "doc3"), rendered)
        self.assertIn(move_url.format("top", "doc3"), rendered)
        self.assertNotIn("position=down", rendered)
        # portal_type aware: only elements of the same portal_type are considered
        view = self.panel(doc3, showArrows=True, arrowsPortalTypeAware=True)
        rendered = view.renderArrows()
        self.assertEqual(view.parentObjectIds, ["doc", "doc3"])
        self.assertIn(
            "http://nohost/plone/folder/folder_position_typeaware?position=up&amp;id=doc3",
            rendered,
        )
        # 'Manage properties' on the parent is required
        self.login_member()
        self.assertEqual(self.panel(showArrows=True).renderArrows(), "")

    def test__moveUrl(self):
        view = self.panel()
        self.assertEqual(
            view._moveUrl(),
            "http://nohost/plone/folder/folder_position?position=%s&id=%s&template_id=http://nohost",
        )
        view.arrowsPortalTypeAware = True
        self.request["URL"] = "http://nohost/plone/folder"
        self.assertEqual(
            view._moveUrl(),
            "http://nohost/plone/folder/folder_position_typeaware?position=%s&id=%s&template_id=http://nohost/plone/folder",
        )

    def test__returnTo(self):
        view = self.panel()
        self.assertEqual(view._returnTo(), "http://nohost")
        self.request["URL"] = "http://nohost/plone/folder/doc/view"
        self.assertEqual(view._returnTo(), "http://nohost/plone/folder/doc/view")

    def test_renderTransitions(self):
        self.assertEqual(self.panel(showTransitions=False).renderTransitions(), "")
        # transitions applied without confirmation (AJAX)
        view = self.panel()
        view.hasActions = False
        rendered = view.renderTransitions()
        self.assertTrue(view.hasActions)
        self.assertIn('class="apButton apButtonWF apButtonWF_submit"', rendered)
        self.assertIn('value="{0}"'.format(SUBMIT_TITLE), rendered)
        self.assertIn("apButtonWF_publish", rendered)
        self.assertIn('class="prevent-default"', rendered)
        self.assertIn(
            "http://nohost/plone/folder/doc/@@triggertransition?transition=submit&amp;"
            "actionspanel_view_name=actions_panel&amp;form.submitted=1&amp;force_redirect_after_transition=0",
            rendered,
        )
        self.assertIn(
            "applyWithComments(baseUrl='http://nohost/plone/folder/doc'", rendered
        )
        # transition to confirm: overlay
        api.portal.set_registry_record(TRANSITIONS_RECORD, ["Document.submit|"])
        rendered = self.panel().renderTransitions()
        self.assertIn('class="link-overlay-actionspanel transition-overlay"', rendered)
        self.assertIn(
            "http://nohost/plone/folder/doc/@@triggertransition?transition=submit&amp;"
            "actionspanel_view_name=actions_panel&amp;force_redirect_after_transition=0",
            rendered,
        )
        # icon of the transition, when displayed as icons
        self.wf.transitions.submit.actbox_icon = "%(portal_url)s/submit.png"
        rendered = self.panel().renderTransitions()
        self.assertIn('src="http://nohost/plone/submit.png"', rendered)
        self.assertIn('title="{0}"'.format(SUBMIT_TITLE), rendered)
        self.assertNotIn("apButtonWF_submit", rendered)
        self.assertIn(
            "apButtonWF_submit", self.panel(useIcons=False).renderTransitions()
        )
        # a transition the user may not trigger is displayed disabled with the reason
        self.wf.transitions.publish.guard.changeFromProperties(
            {"guard_expr": "python: request.get('ap_guard')"}
        )
        self.request.set("ap_guard", No("Not ready yet"))
        rendered = self.panel(useIcons=False).renderTransitions()
        self.assertIn('class="apButton notTriggerableTransitionButton"', rendered)
        self.assertIn(u"{0} ➔ Not ready yet".format(PUBLISH_TITLE), rendered)
        self.assertNotIn("transition=publish", rendered)
        self.wf.transitions.publish.actbox_icon = "%(portal_url)s/publish.png"
        rendered = self.panel().renderTransitions()
        self.assertIn('class="notTriggerableTransitionImage"', rendered)
        self.assertIn('src="http://nohost/plone/publish.png"', rendered)

    def test_renderFolderContents(self):
        self.assertEqual(
            self.panel(self.folder, showFolderContents=False).renderFolderContents(), ""
        )
        # as icon
        view = self.panel(
            self.folder,
            showFolderContents=True,
            folder_contents_action_class="my-class",
        )
        rendered = view.renderFolderContents()
        self.assertIn('href="http://nohost/plone/folder/folder_contents"', rendered)
        self.assertIn('class="my-class"', rendered)
        self.assertIn('target="_parent"', rendered)
        # as button
        rendered = self.panel(
            self.folder, useIcons=False, showFolderContents=True
        ).renderFolderContents()
        self.assertIn('action="http://nohost/plone/folder/folder_contents"', rendered)
        self.assertIn("apButtonAction_folder_contents", rendered)
        # not on a not folderish element
        self.assertEqual(self.panel(showFolderContents=True).renderFolderContents(), "")
        # markingInterface must be provided by the current folder
        marker = "imio.actionspanel.interfaces.IFolderContentsShowableMarker"
        view = self.panel(self.folder, showFolderContents=True, markingInterface=marker)
        self.assertEqual(view.renderFolderContents(), "")
        alsoProvides(self.folder, IFolderContentsShowableMarker)
        self.assertIn("folder_contents", view.renderFolderContents())

    def test_renderEdit(self):
        self.assertEqual(self.panel(showEdit=False).renderEdit(), "")
        rendered = self.panel().renderEdit()
        self.assertIn('href="http://nohost/plone/folder/doc/edit"', rendered)
        self.assertIn('src="http://nohost/plone/edit.png"', rendered)
        self.assertIn('target="_parent"', rendered)
        rendered = self.panel(useIcons=False).renderEdit()
        self.assertIn('action="http://nohost/plone/folder/doc/edit"', rendered)
        self.assertIn("apButtonAction_edit", rendered)
        # 'Modify portal content' is required
        self.login_member()
        self.assertEqual(self.panel().renderEdit(), "")

    def test_renderExtEdit(self):
        self.assertEqual(self.panel(showExtEdit=False).renderExtEdit(), "")
        self.assertEqual(
            self.panel(useIcons=False, showExtEdit=True).renderExtEdit(), ""
        )
        # collective.externaleditor is not installed
        self.assertEqual(self.panel(showExtEdit=True).renderExtEdit(), "")

    def test_renderOwnDelete(self):
        uid = self.doc.UID()
        self.assertEqual(self.panel(showOwnDelete=False).renderOwnDelete(), "")
        rendered = self.panel().renderOwnDelete()
        self.assertIn(
            "javascript:confirmDeleteObject(base_url='http://nohost/plone/folder/doc', object_uid='{0}', this, "
            "msgName=null, view_name='@@delete_givenuid', redirect=null);".format(uid),
            rendered,
        )
        self.assertIn('src="http://nohost/plone/delete_icon.png"', rendered)
        # as button, forceRedirectOnOwnDelete is used
        rendered = self.panel(useIcons=False).renderOwnDelete()
        self.assertIn("apButtonAction_delete", rendered)
        self.assertIn("view_name='@@delete_givenuid', redirect=1);", rendered)
        rendered = self.panel(
            useIcons=False, forceRedirectOnOwnDelete=False
        ).renderOwnDelete()
        self.assertIn("view_name='@@delete_givenuid', redirect=null);", rendered)
        # IContentDeletable.mayDelete is checked
        self.login_member()
        self.assertEqual(self.panel().renderOwnDelete(), "")

    def test_renderOwnDeleteWithComments(self):
        self.assertEqual(self.panel().renderOwnDeleteWithComments(), "")
        rendered = self.panel(
            showOwnDeleteWithComments=True
        ).renderOwnDeleteWithComments()
        self.assertIn(
            'class="link-overlay-actionspanel delete-comments-overlay"', rendered
        )
        self.assertIn(
            'href="@@delete_with_comments?uid={0}"'.format(self.doc.UID()), rendered
        )
        self.assertIn('src="http://nohost/plone/delete_icon.png"', rendered)
        rendered = self.panel(
            useIcons=False, showOwnDeleteWithComments=True
        ).renderOwnDeleteWithComments()
        self.assertIn("apButtonAction_delete", rendered)
        self.login_member()
        self.assertEqual(
            self.panel(showOwnDeleteWithComments=True).renderOwnDeleteWithComments(), ""
        )

    def test_renderActions(self):
        self.assertIsNone(self.panel(showActions=False).renderActions())
        # as icons
        rendered = self.panel().renderActions()
        self.assertIn('href="http://nohost/plone/folder/doc/object_cut"', rendered)
        self.assertIn('class="apButtonAction_form_cut"', rendered)
        self.assertIn('src="http://nohost/plone/cut_icon.png"', rendered)
        self.assertIn('target="_parent"', rendered)
        # as buttons
        rendered = self.panel(useIcons=False).renderActions()
        self.assertIn('action="http://nohost/plone/folder/doc/object_cut"', rendered)
        self.assertIn('class="apButton apButtonAction apButtonAction_cut"', rendered)
        # a javascript action uses onclick, link_target is used
        self.portal.portal_actions.object_buttons._setObject(
            "js_action",
            Action(
                "js_action",
                title="JS action",
                url_expr="string:javascript:doSomething()",
                icon_expr="string:$portal_url/js.png",
                link_target="_blank",
                permissions=("View",),
                visible=True,
            ),
        )
        rendered = self.panel().renderActions()
        self.assertIn(
            'onclick="javascript:event.preventDefault();doSomething()"', rendered
        )
        self.assertIn('href=""', rendered)
        self.assertIn('target="_blank"', rendered)
        # an action without icon is a button, also as icons
        self.portal.portal_actions.object_buttons.js_action.manage_changeProperties(
            icon_expr=""
        )
        rendered = self.panel().renderActions()
        self.assertIn(
            'class="apButton apButtonAction apButtonAction_js_action"', rendered
        )
        self.assertIn('action="javascript:doSomething()"', rendered)

    def test_renderAddContent(self):
        self.assertIsNone(self.panel(self.folder).renderAddContent())
        rendered = self.panel(self.folder, showAddContent=True).renderAddContent()
        self.assertIn('class="apButton apButtonSelect"', rendered)
        self.assertIn("Add an element", rendered)
        self.assertIn("Document", rendered)
        # nothing addable in a Document
        self.assertEqual(self.panel(showAddContent=True).renderAddContent().strip(), "")

    def test_renderHistory(self):
        self.assertIsNone(self.panel().renderHistory())
        self.assertIsNone(self.panel(useIcons=False, showHistory=True).renderHistory())
        rendered = self.panel(showHistory=True).renderHistory()
        self.assertIn('href="http://nohost/plone/folder/doc/@@historyview"', rendered)
        self.assertIn('class="overlay-history"', rendered)
        self.assertIn(
            'src="http://nohost/plone/++resource++imio.actionspanel/history.gif"',
            rendered,
        )
        self.assertIn('title="history.gif_icon_title"', rendered)
        # highlighted when the last event has a comment
        self.wft.doActionFor(self.doc, "submit", comment="My comment")
        rendered = self.panel(showHistory=True).renderHistory()
        self.assertIn(
            "++resource++imio.actionspanel/history_last_event_has_comment.gif", rendered
        )
        rendered = self.panel(
            showHistory=True, showHistoryLastEventHasComments=False
        ).renderHistory()
        self.assertIn("++resource++imio.actionspanel/history.gif", rendered)

    def test_showHistoryForContext(self):
        view = self.panel()
        self.assertTrue(view.showHistoryForContext())
        self.assertEqual(view.contenthistory.__name__, "contenthistory")
        self.login_member()
        self.assertTrue(self.panel().showHistoryForContext())

    def test_historyLastEventHasComments(self):
        view = self.panel()
        view.showHistoryForContext()
        self.assertFalse(view.historyLastEventHasComments())
        self.wft.doActionFor(self.doc, "submit", comment="My comment")
        view = self.panel()
        view.showHistoryForContext()
        self.assertTrue(view.historyLastEventHasComments())
        self.wft.doActionFor(self.doc, "publish")
        view = self.panel()
        view.showHistoryForContext()
        self.assertFalse(view.historyLastEventHasComments())

    def test_mayFolderContents(self):
        self.assertTrue(self.panel(self.folder).mayFolderContents())
        # not folderish
        self.assertFalse(self.panel().mayFolderContents())
        # 'List folder contents' is required
        self.login_member()
        self.assertFalse(self.panel(self.folder).mayFolderContents())

    def test_mayEdit(self):
        self.assertTrue(self.panel().mayEdit())
        self.login_member()
        self.assertFalse(self.panel().mayEdit())

    def test_mayExtEdit(self):
        # collective.externaleditor is not installed
        self.assertFalse(self.panel().mayExtEdit())
        self.login_member()
        self.assertFalse(self.panel().mayExtEdit())

    def test_saveHasActions(self):
        view = self.panel()
        view.hasActions = False
        view.saveHasActions()
        self.assertTrue(view.hasActions)

    def test_sortTransitions(self):
        view = self.panel()
        transitions = [
            {"id": "b", "title": u"Zorro"},
            {"id": "a", "title": u"Alpha"},
            {"id": "c", "title": u"Mike"},
        ]
        self.assertIsNone(view.sortTransitions(transitions))
        self.assertEqual([tr["id"] for tr in transitions], ["a", "c", "b"])

    def test_getTransitions(self):
        view = self.panel()
        transitions = view.getTransitions()
        self.assertEqual(
            transitions,
            [
                {
                    "id": "submit",
                    "title": SUBMIT_TITLE,
                    "description": "Puts your item in a review queue, so it can be published on the site.",
                    "name": "Submit for publication",
                    "may_trigger": True,
                    "confirm": False,
                    "confirmation_view": DEFAULT_CONFIRM_VIEW,
                    "url": "http://nohost/plone/folder/doc/content_status_modify?workflow_action=submit",
                    "icon": "",
                },
                {
                    "id": "publish",
                    "title": PUBLISH_TITLE,
                    "description": "Publishing the item makes it visible to other users.",
                    "name": "Publish",
                    "may_trigger": True,
                    "confirm": False,
                    "confirmation_view": DEFAULT_CONFIRM_VIEW,
                    "url": "http://nohost/plone/folder/doc/content_status_modify?workflow_action=publish",
                    "icon": "",
                },
            ],
        )
        # the workflow is cached in the request, the result in the view
        self.assertEqual(
            self.request.get("imio.actionspanel_workflow_Document_cachekey"), self.wf
        )
        self.assertIs(view.getTransitions(), transitions)
        self.assertIsNot(view.getTransitions(caching=False), transitions)
        # transitions to confirm, by portal_type or class name, with an optional view
        api.portal.set_registry_record(
            TRANSITIONS_RECORD,
            [
                "Document.submit|",
                "{0}.publish|@@my_confirm".format(self.doc.__class__.__name__),
            ],
        )
        transitions = self.panel().getTransitions()
        self.assertEqual(
            [(tr["id"], tr["confirm"], tr["confirmation_view"]) for tr in transitions],
            [("submit", True, DEFAULT_CONFIRM_VIEW), ("publish", True, "@@my_confirm")],
        )
        # icon expression
        self.wf.transitions.submit.actbox_icon = "%(content_url)s/submit.png"
        self.wf.transitions.publish.actbox_icon = "%(portal_url)s/publish.png"
        transitions = self.panel().getTransitions()
        self.assertEqual(
            [tr["icon"] for tr in transitions],
            [
                "http://nohost/plone/folder/doc/submit.png",
                "http://nohost/plone/publish.png",
            ],
        )
        # transitions available to the user only
        self.login_member(("Owner",))
        self.assertEqual([tr["id"] for tr in self.panel().getTransitions()], ["submit"])
        login(self.portal, TEST_USER_NAME)
        self.clean_request_caches()
        # a guard returning appy's No keeps the transition with the reason
        self.wf.transitions.publish.guard.changeFromProperties(
            {"guard_expr": "python: request.get('ap_guard')"}
        )
        self.request.set("ap_guard", No("Not ready yet"))
        transitions = self.panel().getTransitions()
        self.assertFalse(transitions[1]["may_trigger"])
        self.assertEqual(transitions[1]["reason"], u"Not ready yet")
        self.assertNotIn("reason", transitions[0])
        # a guard returning False removes the transition
        self.request.set("ap_guard", False)
        self.assertEqual([tr["id"] for tr in self.panel().getTransitions()], ["submit"])
        # a transition without guard is always available
        self.wf.transitions.publish.guard = None
        self.assertEqual(
            [tr["id"] for tr in self.panel().getTransitions()], ["submit", "publish"]
        )
        # transitions are user actions with an action box name
        self.wf.transitions.publish.actbox_name = ""
        self.assertEqual([tr["id"] for tr in self.panel().getTransitions()], ["submit"])
        # no workflow
        self.wft.setChainForPortalTypes(("Document",), ())
        self.clean_request_caches()
        self.assertEqual(self.panel().getTransitions(), [])

    def test__transitionsToConfirmInfos(self):
        view = self.panel()
        self.assertEqual(view._transitionsToConfirmInfos(), {})
        api.portal.set_registry_record(
            TRANSITIONS_RECORD, ["Document.submit|", "Document.publish|@@my_confirm"]
        )
        self.assertEqual(
            view._transitionsToConfirmInfos(),
            {
                "Document.submit": DEFAULT_CONFIRM_VIEW,
                "Document.publish": "@@my_confirm",
            },
        )
        # dependents may override _transitionsToConfirm and return a list
        view._transitionsToConfirm = lambda: ("Document.submit",)
        self.assertEqual(
            view._transitionsToConfirmInfos(), {"Document.submit": DEFAULT_CONFIRM_VIEW}
        )

    def test__transitionsToConfirm(self):
        view = self.panel()
        self.assertIsNone(api.portal.get_registry_record(TRANSITIONS_RECORD))
        self.assertEqual(view._transitionsToConfirm(), ())
        api.portal.set_registry_record(TRANSITIONS_RECORD, [])
        self.assertEqual(view._transitionsToConfirm(), {})
        api.portal.set_registry_record(
            TRANSITIONS_RECORD, ["Document.submit|", "Document.publish|@@my_confirm"]
        )
        self.assertEqual(
            view._transitionsToConfirm(),
            {"Document.submit": "", "Document.publish": "@@my_confirm"},
        )

    def test__checkTransitionGuard(self):
        view = self.panel()
        guard = Guard()
        # no condition
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )
        # permissions
        guard.changeFromProperties({"guard_permissions": "Review portal content"})
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )
        # roles
        guard.changeFromProperties({"guard_roles": "Reviewer"})
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 0
        )
        guard.changeFromProperties({"guard_roles": "Reviewer;Manager"})
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )
        # groups
        guard.changeFromProperties({"guard_groups": "Reviewers"})
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 0
        )
        api.group.add_user(groupname="Reviewers", username=TEST_USER_ID)
        login(self.portal, TEST_USER_NAME)
        self.clean_request_caches()
        view = self.panel()
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )
        # expression: its value is returned, appy's No included
        guard.changeFromProperties({"guard_expr": "python: request.get('ap_guard')"})
        self.request.set("ap_guard", No("Not ready yet"))
        result = view._checkTransitionGuard(guard, view.member, self.wf, self.doc)
        self.assertIsInstance(result, No)
        self.assertEqual(result.msg, "Not ready yet")
        self.request.set("ap_guard", True)
        self.assertTrue(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc)
        )
        # manager bypass
        guard = Guard()
        guard.changeFromProperties({"guard_roles": "Reviewer"})
        self.wf.manager_bypass = True
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )
        # permissions of a member
        self.login_member(("Owner",))
        view = self.panel()
        guard = Guard()
        guard.changeFromProperties({"guard_permissions": "Review portal content"})
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 0
        )
        guard.changeFromProperties(
            {"guard_permissions": "Review portal content;Request review"}
        )
        self.assertEqual(
            view._checkTransitionGuard(guard, view.member, self.wf, self.doc), 1
        )

    def test_getTransitionTitle(self):
        view = self.panel()
        transition = view.getTransitions()[0]
        self.assertEqual(view.getTransitionTitle(transition), SUBMIT_TITLE)
        view = self.panel(appendTypeNameToTransitionLabel=True)
        self.assertEqual(
            view.getTransitionTitle(transition), u"{0} Page".format(SUBMIT_TITLE)
        )
        self.assertIn('value="{0} Page"'.format(SUBMIT_TITLE), view.renderTransitions())

    def test_computeTriggerTransitionLink(self):
        view = self.panel()
        transition = {
            "id": "submit",
            "confirm": False,
            "confirmation_view": DEFAULT_CONFIRM_VIEW,
        }
        self.assertEqual(
            view.computeTriggerTransitionLink(transition),
            "http://nohost/plone/folder/doc/@@triggertransition?transition=submit&actionspanel_view_name=actions_panel"
            "&form.submitted=1&force_redirect_after_transition=0",
        )
        transition = {
            "id": "submit",
            "confirm": True,
            "confirmation_view": "@@my_confirm",
        }
        view.forceRedirectAfterTransition = True
        self.assertEqual(
            view.computeTriggerTransitionLink(transition),
            "http://nohost/plone/folder/doc/@@my_confirm?transition=submit&actionspanel_view_name=actions_panel"
            "&force_redirect_after_transition=1",
        )

    def test_computeTriggerTransitionOnClick(self):
        view = self.panel()
        reload_js = "window.location.href=window.location.href;"
        # transition no more available: reload the page
        self.assertEqual(view.computeTriggerTransitionOnClick(None), reload_js)
        self.assertEqual(view.computeTriggerTransitionOnClick({}), reload_js)
        self.assertEqual(
            view.computeTriggerTransitionOnClick({"id": "retract", "confirm": False}),
            reload_js,
        )
        # transition without confirmation: AJAX call
        submit = view.getTransitions()[0]
        self.assertEqual(
            view.computeTriggerTransitionOnClick(submit),
            "applyWithComments(baseUrl='http://nohost/plone/folder/doc', viewName='@@triggertransition', "
            "{'transition': 'submit'}, this, force_redirect=0, event_id='ap_transition_triggered');",
        )
        view.forceRedirectAfterTransition = True
        self.assertIn("force_redirect=1", view.computeTriggerTransitionOnClick(submit))
        # transition to confirm: the overlay is used
        submit["confirm"] = True
        self.assertEqual(view.computeTriggerTransitionOnClick(submit), "")

    def test_computeDeleteGivenUIDOnClick(self):
        view = self.panel()
        # Known issue: deleteElement(baseUrl, object_uid, tag, ...) receives the view name as object_uid
        self.assertEqual(
            view.computeDeleteGivenUIDOnClick(),
            "deleteElement(baseUrl='http://nohost/plone/folder/doc', viewName='@@delete_givenuid', "
            "object_uid='{0}');".format(self.doc.UID()),
        )

    def test_computeActionOnClick(self):
        view = self.panel()
        self.assertEqual(
            view.computeActionOnClick("javascript:doIt()"),
            "javascript:event.preventDefault();doIt()",
        )
        self.assertEqual(
            view.computeActionOnClick("javascript:event.preventDefault();doIt()"),
            "javascript:event.preventDefault();doIt()",
        )
        self.assertEqual(
            view.computeActionOnClick("http://nohost/plone/doc"),
            "http://nohost/plone/doc",
        )

    def test_addableContents(self):
        self.assertEqual(self.panel().addableContents(), [])
        addable_ids = [
            addable["id"] for addable in self.panel(self.folder).addableContents()
        ]
        self.assertIn("Document", addable_ids)
        self.assertIn("Folder", addable_ids)
        # addable types are memoized by context: use another folder for the member
        folder2 = api.content.create(
            container=self.portal, type="Folder", id="folder2", title="Folder 2"
        )
        api.user.grant_roles(username=MEMBER_ID, obj=folder2, roles=["Reader"])
        self.login_member()
        self.assertEqual(self.panel(folder2).addableContents(), [])

    def test_listObjectButtonsActions(self):
        view = self.panel()
        actions = view.listObjectButtonsActions()
        self.assertEqual([act["id"] for act in actions], ["cut", "copy", "rename"])
        self.assertEqual(
            [act["icon"] for act in actions],
            ["cut_icon.png", "copy_icon.png", "rename_icon.gif"],
        )
        self.assertEqual(actions[0]["url"], "http://nohost/plone/folder/doc/object_cut")
        # IGNORABLE_ACTIONS
        view.IGNORABLE_ACTIONS = ("cut", "rename")
        self.assertEqual(
            [act["id"] for act in view.listObjectButtonsActions()], ["copy", "delete"]
        )
        # ACCEPTABLE_ACTIONS take precedence
        view.ACCEPTABLE_ACTIONS = ("rename", "delete")
        self.assertEqual(
            [act["id"] for act in view.listObjectButtonsActions()], ["delete", "rename"]
        )
        # icon in a resource directory: the resource name is kept
        self.portal.portal_actions.object_buttons.rename.manage_changeProperties(
            icon_expr="string:$portal_url/++resource++imio.actionspanel/history.gif"
        )
        self.assertEqual(
            [act["icon"] for act in view.listObjectButtonsActions()],
            ["delete_icon.png", "++resource++imio.actionspanel/history.gif"],
        )
        # object_buttons actions of the portal_type
        self.portal.portal_types.Document.addAction(
            id="my_action",
            name="My action",
            action="string:${object_url}/my_action",
            condition="",
            permission=("View",),
            category="object_buttons",
        )
        view = self.panel()
        self.assertEqual(
            [act["id"] for act in view.listObjectButtonsActions()],
            ["cut", "copy", "rename", "my_action"],
        )
        # actions available to the user only
        self.login_member()
        self.assertEqual(
            [act["id"] for act in self.panel().listObjectButtonsActions()],
            ["copy", "my_action"],
        )

    def test_triggerTransition(self):
        view = self.panel()
        # no HTTP_REFERER: '' is returned when redirecting
        self.assertEqual(view.triggerTransition("submit", "My comment"), "")
        self.assertEqual(api.content.get_state(self.doc), "pending")
        self.assertEqual(
            self.doc.workflow_history["simple_publication_workflow"][-1]["comments"],
            "My comment",
        )
        self.assertEqual(self.status_messages(), [(u"Item state changed.", u"info")])
        # HTTP_REFERER is returned when redirecting
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder"
        self.assertEqual(
            view.triggerTransition("retract", ""), "http://nohost/plone/folder"
        )
        self.assertIsNone(view.triggerTransition("submit", "", redirect=False))
        # the element is no more viewable: redirect to HTTP_REFERER if it is not the element
        api.user.grant_roles(username=MEMBER_ID, obj=self.doc, roles=["Reviewer"])
        login(self.portal, MEMBER_ID)
        self.clean_request_caches()
        view = self.panel()
        self.assertEqual(
            view.triggerTransition("reject", ""), "http://nohost/plone/folder"
        )
        self.assertEqual(api.content.get_state(self.doc), "private")
        self.assertEqual(
            self.status_messages()[-1],
            (
                u"You have been redirect here because the action you just made have made thelement no more "
                u"viewable to you.",
                u"warning",
            ),
        )
        # or to the first viewable parent
        login(self.portal, TEST_USER_NAME)
        self.wft.doActionFor(self.doc, "submit")
        login(self.portal, MEMBER_ID)
        self.clean_request_caches()
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(
            self.panel().triggerTransition("reject", "", redirect=False),
            "http://nohost/plone",
        )
        # an error is displayed in a portal message and the transaction is aborted
        login(self.portal, TEST_USER_NAME)
        self.clean_request_caches()
        view = self.panel(self.folder)
        self.status_messages()
        self.assertIsNone(view.triggerTransition("unknown", ""))
        self.assertEqual(
            [msg_type for msg, msg_type in self.status_messages()], [u"warning"]
        )
        self.assertNotIn("folder", self.portal.objectIds())

    def test__redirectToViewableUrl(self):
        view = self.panel()
        self.assertEqual(view._redirectToViewableUrl(), "")
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(
            view._redirectToViewableUrl(), "http://nohost/plone/folder/doc"
        )
        # the member cached in the request is used
        login(self.portal, MEMBER_ID)
        self.assertEqual(
            view._redirectToViewableUrl(), "http://nohost/plone/folder/doc"
        )
        self.clean_request_caches()
        self.assertEqual(view._redirectToViewableUrl(), "http://nohost/plone")

    def test_getCurrentFolder(self):
        self.assertEqual(self.panel().getCurrentFolder(), self.folder)
        self.assertEqual(self.panel(self.folder).getCurrentFolder(), self.folder)

    def test_isMarked(self):
        view = self.panel()
        marker = "imio.actionspanel.interfaces.IFolderContentsShowableMarker"
        self.assertTrue(view.isMarked(None))
        self.assertFalse(view.isMarked("imio.actionspanel.interfaces.IUnknown"))
        self.assertFalse(view.isMarked(marker))
        self.assertFalse(view.isMarked(marker, self.folder))
        alsoProvides(self.folder, IFolderContentsShowableMarker)
        self.assertFalse(view.isMarked(marker))
        self.assertTrue(view.isMarked(marker, self.folder))
        alsoProvides(self.doc, IFolderContentsShowableMarker)
        self.assertTrue(view.isMarked(marker))


class TestDeleteGivenUidView(BaseViewsTestCase):
    def test___call__(self):
        view = self.portal.restrictedTraverse("@@delete_givenuid")
        self.assertRaises(KeyError, view, "unknown_uid")
        # deleted: redirect to HTTP_REFERER or a viewable place
        self.assertEqual(view(self.doc.UID()), "")
        self.assertNotIn("doc", self.folder.objectIds())
        self.assertEqual(self.status_messages(), [(u"object_deleted", u"info")])
        # without redirect: 204
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.assertIsNone(view(doc.UID(), redirect=False))
        self.assertEqual(self.request.response.getStatus(), 204)
        self.assertNotIn("doc", self.folder.objectIds())
        # redirect received from the JS
        for redirect in ("0", "null", 0):
            self.request.response.setStatus(200)
            doc = api.content.create(
                container=self.folder, type="Document", id="doc", title="Doc"
            )
            self.request.form["redirect"] = redirect
            self.assertIsNone(view(doc.UID()))
            self.assertEqual(self.request.response.getStatus(), 204)
        self.request.form["redirect"] = 1
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc"
        self.assertEqual(
            doc.restrictedTraverse("@@delete_givenuid")(doc.UID()),
            "http://nohost/plone/folder",
        )
        del self.request.form["redirect"]
        # historized in the parent with the comment
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.request.form["comment"] = "My comment"
        view(doc.UID(), historize_in_parent=True)
        self.assertEqual(len(self.folder.deleted_children_history), 1)
        event = self.folder.deleted_children_history[0]
        self.assertEqual(event["action"], "delete_element")
        self.assertEqual(event["comments"], "My comment")
        self.assertEqual(event["actor"], TEST_USER_ID)
        # element not in portal_catalog: found in uid_catalog when it exists (Archetypes)
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        self.portal.portal_catalog.unindexObject(doc)
        if "uid_catalog" in self.portal:
            view(doc.UID())
            self.assertNotIn("doc", self.folder.objectIds())
        else:
            self.assertRaises(KeyError, view, doc.UID())
            api.content.delete(doc)
        # the user must be able to delete the element itself, not the parent
        api.user.grant_roles(username=MEMBER_ID, obj=self.folder, roles=["Reader"])
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        doc2 = api.content.create(
            container=self.folder, type="Document", id="doc2", title="Doc 2"
        )
        api.user.grant_roles(username=MEMBER_ID, obj=doc2, roles=["Owner"])
        login(self.portal, MEMBER_ID)
        self.assertRaises(Unauthorized, view, doc.UID())
        self.assertIn("doc", self.folder.objectIds())
        view(doc2.UID())
        self.assertNotIn("doc2", self.folder.objectIds())
        login(self.portal, TEST_USER_NAME)
        api.content.delete(doc)
        # BeforeDeleteException: the transaction is aborted
        gsm = getGlobalSiteManager()
        gsm.registerHandler(
            raise_before_delete, (INotRemovable, IObjectWillBeRemovedEvent)
        )
        self.addCleanup(
            gsm.unregisterHandler,
            raise_before_delete,
            (INotRemovable, IObjectWillBeRemovedEvent),
        )
        doc = api.content.create(
            container=self.folder, type="Document", id="doc", title="Doc"
        )
        alsoProvides(doc, INotRemovable)
        self.assertRaises(
            BeforeDeleteException, view, doc.UID(), catch_before_delete_exception=False
        )
        self.status_messages()
        self.request.response.setStatus(200)
        folder = api.content.create(
            container=self.portal, type="Folder", id="folder", title="Folder"
        )
        doc = api.content.create(
            container=folder, type="Document", id="doc", title="Doc"
        )
        alsoProvides(doc, INotRemovable)
        self.assertIsNone(view(doc.UID()))
        self.assertEqual(
            self.status_messages(),
            [(u"Can not delete doc (BeforeDeleteException)", u"error")],
        )
        self.assertEqual(self.request.response.getStatus(), 204)

    def test__findViewablePlace(self):
        view = self.doc.restrictedTraverse("@@delete_givenuid")
        # HTTP_REFERER is not the deleted element
        self.request["HTTP_REFERER"] = "http://nohost/plone/dashboard"
        self.assertEqual(
            view._findViewablePlace(self.doc), "http://nohost/plone/dashboard"
        )
        # HTTP_REFERER is the deleted element: first viewable parent
        self.request["HTTP_REFERER"] = "http://nohost/plone/folder/doc/view"
        self.assertEqual(
            view._findViewablePlace(self.doc), "http://nohost/plone/folder"
        )
        login(self.portal, MEMBER_ID)
        self.assertEqual(view._findViewablePlace(self.doc), "http://nohost/plone")
        # HTTP_REFERER is compared with the context of the view, not with the deleted element
        view = self.portal.restrictedTraverse("@@delete_givenuid")
        self.request["HTTP_REFERER"] = "http://nohost/plone/dashboard"
        self.assertEqual(view._findViewablePlace(self.doc), "http://nohost/plone")


class TestAsyncActionsPanelView(BaseViewsTestCase):
    def test__convert_form_values(self):
        view = self.doc.restrictedTraverse("@@async_actions_panel")
        self.assertEqual(view._convert_form_values(), {})
        self.request.form.update(
            {"useIcons": "false", "showEdit": "true", "_": "1696700000000"}
        )
        self.assertEqual(
            view._convert_form_values(),
            {"useIcons": False, "showEdit": True, "_": 1696700000000},
        )

    def test_show(self):
        view = self.doc.restrictedTraverse("@@async_actions_panel")
        self.assertTrue(view.show())
        self.request.set("ajax_load", "1")
        self.assertFalse(view.show())

    def test___call__(self):
        expected = self.doc.restrictedTraverse("@@actions_panel")(
            useIcons=False, showEdit=False
        )
        self.request.form.update(
            {"useIcons": "false", "showEdit": "false", "_": "1696700000000"}
        )
        view = self.doc.restrictedTraverse("@@async_actions_panel")
        self.assertEqual(view(), expected)
        self.assertNotIn("apButtonAction_edit", view())
        # form values take precedence over kwargs
        self.assertEqual(view(showEdit=True), expected)
