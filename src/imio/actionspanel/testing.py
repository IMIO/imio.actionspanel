# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import WSGI_SERVER_FIXTURE
from Products.statusmessages.interfaces import IStatusMessage
from zope.event import notify
from zope.globalrequest import setRequest
from zope.traversing.interfaces import BeforeTraverseEvent

import imio.actionspanel
import unittest


MEMBER_ID = "member"
MEMBER_PASSWORD = "member_password"


class ActionsPanelLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # testing.zcml includes the package and registers the sample viewlet
        # and the deletion subscriber that dependents register themselves
        self.loadZCML(package=imio.actionspanel, name="testing.zcml")

    def setUpPloneSite(self, portal):
        # collective.fingerpointing logs the registry changes (bundles) and the user creation:
        # it needs the global request
        setRequest(portal.REQUEST)
        applyProfile(portal, "imio.actionspanel:default")
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        portal.acl_users.userFolderAddUser(MEMBER_ID, MEMBER_PASSWORD, ["Member"], [])
        setRequest(None)


FIXTURE = ActionsPanelLayer(name="FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")

ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, WSGI_SERVER_FIXTURE),
    name="ACCEPTANCE",
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests, logged in as a Manager."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request.form.clear()
        # mark the request with the browser layers (IActionsPanelLayer, IImioHistoryLayer), as traversal does
        notify(BeforeTraverseEvent(self.portal, self.request))
        self.wft = self.portal.portal_workflow
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def clean_request_caches(self):
        """Remove the imio.actionspanel_*_cachekey values stored in the request."""
        for key in list(self.request.other.keys()):
            if key.startswith("imio.actionspanel_"):
                del self.request.other[key]

    def set_form(self, values):
        """Set p_values in the request form and, as the publisher does, in request.other,
        read first by request.get.  A None value removes the key."""
        for key, value in values.items():
            for namespace in (self.request.form, self.request.other):
                if value is None:
                    namespace.pop(key, None)
                else:
                    namespace[key] = value

    def status_messages(self):
        """Return and clear the portal messages, as (message, type)."""
        return [(msg.message, msg.type) for msg in IStatusMessage(self.request).show()]


class FunctionalTestCase(IntegrationTestCase):
    """Base class for functional tests (transactions committed, test browser)."""

    layer = FUNCTIONAL


# Robot: setup of the robot suites only (ROBOT_ACCEPTANCE), the unit tests don't use it.
# As in dependents, the panel is shown with other params (testing.zcml): as icons above the content,
# besides the buttons panel below it, and loaded by JS (?async_panel=1).
# Document.publish is a transition to confirm.
from imio.actionspanel.browser.viewlets import (  # noqa: E402  isort:skip
    ActionsPanelViewlet,
)
from zope.interface import Interface  # noqa: E402  isort:skip


class IRobotLayer(Interface):
    """Browser layer of the robot site."""


class RobotIconsViewlet(ActionsPanelViewlet):
    """Actions panel as icons, with the sections the buttons panel doesn't show."""

    params = {
        "useIcons": True,
        "showTransitions": False,
        "showEdit": False,
        "showOwnDelete": False,
        "showActions": False,
        "showOwnDeleteWithComments": True,
        "showHistory": True,
        "showArrows": True,
        "showAddContent": True,
    }

    def render(self):
        return '<div id="icons-actions-panel">{0}</div>'.format(
            self.renderViewlet() or ""
        )


class RobotAsyncViewlet(ActionsPanelViewlet):
    """Actions panel loaded by JS (load_actions_panel), on pages called with ?async_panel=1."""

    is_async = True

    def show(self):
        return (
            "async_panel" in self.request.form and super(RobotAsyncViewlet, self).show()
        )


class RobotLayer(PloneSandboxLayer):

    defaultBases = (FIXTURE,)

    def setUpPloneSite(self, portal):
        from plone import api
        from plone.browserlayer.utils import register_layer

        # collective.fingerpointing logs the registry changes: it needs the global request
        setRequest(portal.REQUEST)
        register_layer(IRobotLayer, "imio.actionspanel.robot")
        api.portal.set_registry_record(
            "imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions",
            ["Document.publish|"],
        )
        # Plone's rename opens in a modal ({}): redirect on success, as imio.pm.wsclient's send actions
        portal.portal_actions.object_buttons.rename.manage_changeProperties(
            modal='{"actionOptions": {"redirectOnResponse": true}}'
        )
        setRequest(None)


ROBOT_FIXTURE = RobotLayer(name="ROBOT_FIXTURE")

ROBOT_ACCEPTANCE = FunctionalTesting(
    bases=(ROBOT_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, WSGI_SERVER_FIXTURE),
    name="ROBOT_ACCEPTANCE",
)
