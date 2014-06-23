import logging

from appy.gen import No

from Acquisition import aq_base

from zope.i18n import translate

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone import PloneMessageFactory as _plone
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflow.Expression import createExprContext
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from imio.actionspanel import ActionsPanelMessageFactory as _
from imio.actionspanel.interfaces import IContentDeletable
from imio.actionspanel.utils import unrestrictedRemoveGivenObject


class ActionsPanelView(BrowserView):
    """
      This manage the view displaying actions on context.
    """
    def __init__(self, context, request):
        super(ActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.member = self.request.get('imio.actionspanel_member_cachekey', None)
        if not self.member:
            self.member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
            self.request.set('imio.actionspanel_member_cachekey', self.member)
        self.SECTIONS_TO_RENDER = ('renderTransitions',
                                   'renderEdit',
                                   'renderOwnDelete',
                                   'renderActions', )
        # portal_actions.object_buttons action ids not to keep
        # every actions will be kept except actions listed here
        self.IGNORABLE_ACTIONS = ()

        # portal_actions.object_buttons action ids to keep
        # if you define some here, only these actions will be kept
        self.ACCEPTABLE_ACTIONS = ()

    def __call__(self,
                 useIcons=True,
                 showTransitions=True,
                 appendTypeNameToTransitionLabel=False,
                 showEdit=True,
                 showOwnDelete=True,
                 showActions=True,
                 **kwargs):
        """
          Master method that will render the content.
          This is not supposed to be overrided.
        """
        self.useIcons = useIcons
        self.showTransitions = showTransitions
        self.appendTypeNameToTransitionLabel = appendTypeNameToTransitionLabel
        self.showEdit = showEdit
        self.showOwnDelete = showOwnDelete
        # if we manage our own delete, do not use Plone default one
        if self.showOwnDelete and not 'delete' in self.IGNORABLE_ACTIONS:
            self.IGNORABLE_ACTIONS = self.IGNORABLE_ACTIONS + ('delete', )
        self.showActions = showActions
        self.kwargs = kwargs
        self.hasActions = False
        return self.index()

    def _renderSections(self):
        """
          This will check what sections need to be rendered.
          This is not supposed to be overrided.
        """
        res = ''
        for section in self.SECTIONS_TO_RENDER:
            renderedSection = getattr(self, section)() or ''
            res += renderedSection
        return res

    def renderTransitions(self):
        """
          Render the current context available workflow transitions.
        """
        if self.showTransitions:
            return ViewPageTemplateFile("actions_panel_transitions.pt")(self)
        return ''

    def renderEdit(self):
        """
          Render a 'edit' action.  By default, only available when actions are displayed
          as icons because when it is not the case, we already have a 'edit' tab and that would
          be redundant.
        """
        if self.showEdit and self.useIcons and self.mayEdit():
            return ViewPageTemplateFile("actions_panel_edit.pt")(self)
        return ''

    def renderOwnDelete(self):
        """
          Render our own version of the 'delete' action.
        """
        if self.showOwnDelete and \
           self.member.has_permission('Delete objects', self.context) and \
           IContentDeletable(self.context).mayDelete():
            return ViewPageTemplateFile("actions_panel_own_delete.pt")(self)
        return ''

    def renderActions(self):
        """
          Render actions coming from portal_actions.object_buttons and available on the context.
        """
        if self.showActions:
            return ViewPageTemplateFile("actions_panel_actions.pt")(self)

    def mayEdit(self):
        """
          Method that check if special 'edit' action has to be displayed.
        """
        return self.member.has_permission('Modify portal content', self.context) and self.useIcons

    def saveHasActions(self):
        """
          Save the fact that we have actions.
        """
        self.hasActions = True

    def getTransitions(self):
        """
          This method is similar to portal_workflow.getTransitionsFor, but
          with some improvements:
          - we retrieve transitions that the user can't trigger, but for
            which he needs to know for what reason he can't trigger it;
          - for every transition, we know if we need to display a confirm
            popup or not.
        """
        res = []
        # Get the workflow definition for p_obj.
        workflow = self.request.get('imio.actionspanel_workflow_%s_cachekey' % self.context.portal_type, None)
        if not workflow:
            wfTool = getToolByName(self.context, 'portal_workflow')
            workflows = wfTool.getWorkflowsFor(self.context)
            if not workflows:
                return res
            workflow = workflows[0]
            self.request.set('imio.actionspanel_workflow_%s_cachekey' % self.context.portal_type, workflow)
        # What is the current state for self.context?
        currentState = workflow._getWorkflowStateOf(self.context)
        if not currentState:
            return res
        # Get the transitions to confirm from the config.
        toConfirm = self._transitionsToConfirm()
        # Analyse all the transitions that start from this state.
        for transitionId in currentState.transitions:
            transition = workflow.transitions.get(transitionId, None)
            if transition and (transition.trigger_type == TRIGGER_USER_ACTION) \
               and transition.actbox_name:
                # We have a possible candidate for a user-triggerable transition
                if transition.guard is None:
                    mayTrigger = True
                else:
                    mayTrigger = self._checkTransitionGuard(transition.guard,
                                                            self.member,
                                                            workflow,
                                                            self.context)
                if mayTrigger or isinstance(mayTrigger, No):
                    # Information about this transition must be part of result.
                    # check if the transition have to be confirmed regarding
                    # current object meta_type/portal_type and transition to trigger
                    preNameMetaType = '%s.%s' % (self.context.meta_type, transition.id)
                    preNamePortalType = '%s.%s' % (self.context.portal_type, transition.id)
                    tInfo = {
                        'id': transition.id,
                        # if the transition.id is not translated, use translated transition.title...
                        'title': _plone(transition.id,
                                        default=translate(transition.title,
                                                          domain="plone",
                                                          context=self.request)),
                        'description': transition.description,
                        'name': transition.actbox_name, 'may_trigger': True,
                        'confirm': preNameMetaType in toConfirm or preNamePortalType in toConfirm,
                        'url': transition.actbox_url %
                            {'content_url': self.context.absolute_url(),
                             'portal_url': '',
                             'folder_url': ''}
                    }
                    if not mayTrigger:
                        tInfo['may_trigger'] = False
                        tInfo['reason'] = mayTrigger.msg
                    res.append(tInfo)
        return res

    def _transitionsToConfirm(self):
        """
          Return the list of transitions the user will have to confirm, aka
          the user will be able to enter a comment for.
          This is a per meta_type or portal_type list of transitions to confirm.
          So for example, this could be :
          ('ATDocument.reject', 'Document.publish', 'Collection.publish', )
          --> ATDocument is a meta_type and Document is a portal_type for example
        """
        return ()

    def _checkTransitionGuard(self, guard, sm, wf_def, ob):
        """
          This method is similar to DCWorkflow.Guard.check, but allows to
          retrieve the truth value as a appy.gen.No instance, not simply "1"
          or "0".
        """
        u_roles = None
        if wf_def.manager_bypass:
            # Possibly bypass.
            u_roles = sm.getRolesInContext(ob)
            if 'Manager' in u_roles:
                return 1
        if guard.permissions:
            for p in guard.permissions:
                if _checkPermission(p, ob):
                    break
            else:
                return 0
        if guard.roles:
            # Require at least one of the given roles.
            if u_roles is None:
                u_roles = sm.getRolesInContext(ob)
            for role in guard.roles:
                if role in u_roles:
                    break
            else:
                return 0
        if guard.groups:
            # Require at least one of the specified groups.
            u = sm
            b = aq_base(u)
            if hasattr(b, 'getGroupsInContext'):
                u_groups = u.getGroupsInContext(ob)
            elif hasattr(b, 'getGroups'):
                u_groups = u.getGroups()
            else:
                u_groups = ()
            for group in guard.groups:
                if group in u_groups:
                    break
            else:
                return 0
        expr = guard.expr
        if expr is not None:
            econtext = createExprContext(StateChangeInfo(ob, wf_def))
            res = expr(econtext)
            return res
        return 1

    def listObjectButtonsActions(self):
        """
          Return a list of object_buttons actions coming from portal_actions.
        """
        actionsTool = getToolByName(self, 'portal_actions')
        # we only want object_buttons, so ignore other categories and providers
        IGNORABLE_CATEGORIES = ['site_actions', 'object', 'controlpanel/controlpanel_addons', 'workflow',
                                'portal_tabs', 'global', 'document_actions', 'user', 'folder_buttons', 'folder']
        IGNORABLE_PROVIDERS = ['portal_workflow', ]
        allActions = actionsTool.listFilteredActionsFor(self.context,
                                                        ignore_providers=IGNORABLE_PROVIDERS,
                                                        ignore_categories=IGNORABLE_CATEGORIES)

        objectButtonActions = []
        if 'object_buttons' in allActions:
            objectButtonActions = allActions['object_buttons']

        res = []
        for action in objectButtonActions:
            if (self.ACCEPTABLE_ACTIONS and action['id'] in self.ACCEPTABLE_ACTIONS) or \
               (not self.ACCEPTABLE_ACTIONS and not action['id'] in self.IGNORABLE_ACTIONS):
                act = {}
                act['id'] = action['id']
                act['title'] = action['title']
                act['url'] = action['url']
                # We try to append the url of the icon of the action
                # look on the action itself
                if action['icon']:
                    # make sure we only have the action icon name not a complete
                    # path including portal_url or so, just take care that we do not have
                    # an image in a static resource folder
                    splittedIconPath = action['icon'].split('/')
                    if len(splittedIconPath) > 1 and '++resource++' in splittedIconPath[-2]:
                        # keep last 2 parts of the path
                        act['icon'] = '/'.join((splittedIconPath[-2], splittedIconPath[-1], ))
                    else:
                        act['icon'] = splittedIconPath[-1]
                else:
                    act['icon'] = ''
                res.append(act)
        return res

    def triggerTransition(self, transition, comment):
        """
          Triggers a p_transition on self.context.
        """
        wfTool = getToolByName(self, 'portal_workflow')
        try:
            wfTool.doActionFor(self.context,
                               transition,
                               comment=comment)
        except WorkflowException:
            # fail silently if the user triggered a transition he could not
            # this avoid WorkflowException error in the UI if a user double-click on an icon
            # triggering a workflow transition
            logger = logging.getLogger('imio.actionspanel')
            logger.info("WorkflowException in imio.actionspanel.triggerTransition, the user '%s' "
                        "tried to trigger the transition '%s' but he could not.  Double click in the UI?" %
                        (self.member.getId(), self.request.get('transition')))
        # use transition title to translate so if several transitions have the same title,
        # we manage only one translation
        transition_title = wfTool.getWorkflowsFor(self.context)[0].transitions[self.request['transition']].title or \
            self.request['transition']
        # add a portal message, we try to translate a specific one or add 'Item state changed.' as default
        msg = _('%s_done_descr' % transition_title,
                default=_plone("Item state changed."))
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(msg)
        if not self.member.has_permission('View', self.context):
            # After having triggered a wfchange, it the current user
            # can not access the obj anymore :
            # - redirect the user to HTTP_REFERER if we where not on the obj
            # - redirect the user to his home page if we were on the no more accessible obj
            # - display a clear portal message
            redirectToUrl = self._redirectToUrl()
            # add a specific portal_message before redirecting the user
            msg = _('redirected_after_transition_not_viewable',
                    default="You have been redirected here because you do not have "
                            "access anymore to the element you just changed the state for.")
            plone_utils.addPortalMessage(msg, 'warning')
            return self.request.RESPONSE.redirect(redirectToUrl)
        else:
            return self._gotoReferer()

    def _redirectToUrl(self):
        """
          Return the url the user must be redirected to.
        """
        return self.request['HTTP_REFERER']

    def _gotoReferer(self):
        """
          This method allows to go specify where to go back after a transition has been triggered.
        """
        urlBack = self.request['HTTP_REFERER']
        return self.request.RESPONSE.redirect(urlBack)


class DeleteGivenUidView(BrowserView):
    """
      View that ease deletion of elements by not checking the 'Delete objects' permission on parent
      but only on the object to delete itself.
      Callable using self.portal.restrictedTraverse('@@delete_givenuid)(object_to_delete.UID()) in the code
      and using classic traverse in a url : http://nohost/plonesite/delete_givenuid?object_uid=anUID
    """
    def __call__(self, object_uid):
        logger = logging.getLogger('imio.actionspanel')
        membershipTool = getToolByName(self, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()

        # Get the object to delete
        # try to get it from the portal_catalog
        catalog_brains = self.context.portal_catalog(UID=object_uid)
        # if not found, try to get it from the uid_catalog
        if not catalog_brains:
            catalog_brains = self.context.uid_catalog(UID=object_uid)
        # if nto found at all, raise
        if not catalog_brains:
            raise KeyError('The given uid could not be found!')
        obj = catalog_brains[0].getObject()
        objectUrl = obj.absolute_url()

        # we use an adapter to manage if we may delete the object
        # that checks if the user has the 'Delete objects' permission
        # on the content by default but that could be overrided
        if member.has_permission("Delete objects", obj) and IContentDeletable(obj).mayDelete():
            msg = {'message': 'object_deleted',
                   'type': 'info'}
            logMsg = '%s at %s deleted by "%s"' % \
                     (obj.meta_type, obj.absolute_url_path(), member.getId())
            # remove the object
            # just manage BeforeDeleteException because we rise it ourselves
            from OFS.ObjectManager import BeforeDeleteException
            try:
                unrestrictedRemoveGivenObject(self.context, obj)
                logger.info(logMsg)
            except BeforeDeleteException, exc:
                msg = {'message': exc.message,
                       'type': 'error'}
        else:
            msg = {'message': 'cant_delete_object',
                   'type': 'error'}

        # Redirect the user to the correct page and display the correct message.
        refererUrl = self.request['HTTP_REFERER']
        if not refererUrl.startswith(objectUrl):
            urlBack = refererUrl
        else:
            # we were on the object, redirect to the home page of the current meetingConfig
            # redirect to the exact home page url, not to the home page that redirects
            # to the meeting folder page or the portal_message is lost
            mc = self.context.portal_plonemeeting.getMeetingConfig(self.context)
            app = self.context.portal_plonemeeting.getPloneMeetingFolder(mc.id)
            urlBack = app.restrictedTraverse('@@meetingfolder_redirect_view').getFolderRedirectUrl()

        # Add the message. If I try to get plone_utils directly from context
        # (context.plone_utils), in some cases (ie, the user does not own context),
        # Unauthorized is raised (?).
        self.context.portal_plonemeeting.plone_utils.addPortalMessage(**msg)
        return self.request.RESPONSE.redirect(urlBack)

