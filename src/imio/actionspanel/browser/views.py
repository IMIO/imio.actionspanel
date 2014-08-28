import logging
logger = logging.getLogger('imio.actionspanel')

from appy.gen import No

from Acquisition import aq_base
from AccessControl import Unauthorized

from zope.component import getMultiAdapter
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

DEFAULT_CONFIRM_VIEW = '@@triggertransition'


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
        self.portal_url = self.request.get('imio.actionspanel_portal_url_cachekey', None)
        self.portal = self.request.get('imio.actionspanel_portal_cachekey', None)
        if not self.portal_url or not self.portal:
            self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
            self.portal_url = self.portal.absolute_url()
            self.request.set('imio.actionspanel_portal_url_cachekey', self.portal_url)
            self.request.set('imio.actionspanel_portal_cachekey', self.portal)
        self.SECTIONS_TO_RENDER = ('renderTransitions',
                                   'renderEdit',
                                   'renderOwnDelete',
                                   'renderActions',
                                   'renderAddContent',
                                   'renderHistory')
        # portal_actions.object_buttons action ids not to keep
        # every actions will be kept except actions listed here
        self.IGNORABLE_ACTIONS = ()

        # portal_actions.object_buttons action ids to keep
        # if you define some here, only these actions will be kept
        self.ACCEPTABLE_ACTIONS = ()

        # when using showHistory and showHistoryLastEventHasComments
        # we can give a list of comments we do not consider
        # for example is some default comments are added at specific time
        # just for information
        self.IGNORABLE_HISTORY_COMMENTS = ('', u'', None)

    def __call__(self,
                 useIcons=True,
                 showTransitions=True,
                 appendTypeNameToTransitionLabel=False,
                 showEdit=True,
                 showOwnDelete=True,
                 showActions=True,
                 showAddContent=False,
                 showHistory=False,
                 showHistoryLastEventHasComments=True,
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
        self.showAddContent = showAddContent
        self.showHistory = showHistory
        self.showHistoryLastEventHasComments = showHistoryLastEventHasComments
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

    def renderAddContent(self):
        """
          Render allowed_content_types coming from portal_type.
        """
        if self.showAddContent:
            return ViewPageTemplateFile("actions_panel_add_content.pt")(self)

    def renderHistory(self):
        """
          Render a link to the object's history (@@historyview).
        """
        if self.showHistory and self.useIcons and self.showHistoryForContext():
            return ViewPageTemplateFile("actions_panel_history.pt")(self)

    def showHistoryForContext(self):
        """
          Should an access to the @@historyview be shown for the object?
        """
        if not _checkPermission('CMFEditions: Access previous versions', self.context):
            return False
        return True

    def historyLastEventHasComments(self):
        '''
          Returns True if the last event of the object's history has a comment.
        '''
        history = getattr(aq_base(self.context), 'workflow_history', None)
        if not history:
            return False
        # workflow_history is like :
        # {'my_content_workflow': ({'action': None, 'review_state': 'created', 'actor': 'admin',
        #                           'comments': 'My comment', 'time': DateTime('2014/06/05 14:35 GMT+2')},
        #  'my_content_former_workflow': ({'action': None, 'review_state': 'created', 'actor': 'admin',
        #                           'comments': 'My comment', 'time': DateTime('2012/02/02 12:00 GMT+2')}, }
        # if we have only one key in the history, we take relevant corresponding actions but if we have
        # several keys, we need to get current workflow and to reach relevant actions
        keys = history.keys()
        lastEvent = {'comments': ''}
        if len(keys) == 1:
            lastEvent = history[keys[0]][-1]
        elif len(keys) > 1:
            # get current workflow history
            wfTool = getToolByName(self.context, 'portal_workflow')
            contextWFs = wfTool.getWorkflowsFor(self.context)
            if not contextWFs:
                return False
            currentWFId = contextWFs[0].getId()
            lastEvent = history[currentWFId][-1]
        if not lastEvent['comments'] in self.IGNORABLE_HISTORY_COMMENTS:
            return True
        return False

    def mayEdit(self):
        """
          Method that check if special 'edit' action has to be displayed.
        """
        return self.member.has_permission('Modify portal content', self.context)

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
        toConfirm = self._transitionsToConfirmInfos()
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
                    confirmation_view = toConfirm.get(preNameMetaType, '') or toConfirm.get(preNamePortalType, '')
                    tInfo = {
                        'id': transition.id,
                        # if the transition.id is not translated, use translated transition.title...
                        'title': translate(transition.id,
                                           domain="plone",
                                           context=self.request,
                                           default=translate(transition.title,
                                                             domain="plone",
                                                             context=self.request)),
                        'description': transition.description,
                        'name': transition.actbox_name, 'may_trigger': True,
                        'confirm': bool(confirmation_view),
                        'confirmation_view': confirmation_view or DEFAULT_CONFIRM_VIEW,
                        'url': transition.actbox_url %
                            {'content_url': self.context.absolute_url(),
                             'portal_url': '',
                             'folder_url': ''}
                    }
                    if not mayTrigger:
                        tInfo['may_trigger'] = False
                        tInfo['reason'] = mayTrigger.msg
                    res.append(tInfo)

        # sort transitions by title
        def _sortByTransitionTitle(x, y):
            return cmp(x['title'], y['title'])
        res.sort(_sortByTransitionTitle)

        return res

    def _transitionsToConfirmInfos(self):
        transitions = self._transitionsToConfirm()
        if type(transitions) is not dict:
            transitions = dict([(t, DEFAULT_CONFIRM_VIEW) for t in transitions])
        else:
            for name, confirm_view in transitions.iteritems():
                if not confirm_view:
                    transitions[name] = DEFAULT_CONFIRM_VIEW
        return transitions

    def _transitionsToConfirm(self):
        """
          Return the list of transitions the user will have to confirm, aka
          the user will be able to enter a comment for.
          This is a per meta_type or portal_type list of transitions to confirm.
          So for example, this could be :
          ('ATDocument.reject', 'Document.publish', 'Collection.publish', )
          --> ATDocument is a meta_type and Document is a portal_type for example
          The list can also be a dict with the key being the transition name to
          confirm and the value being the name of the view to call to confirm
          the transition. eg:
          {'Document.reject': 'simpleconfirmview', 'Mytype.cancel': 'messageconfirmview'}
          If no confirmation view is provided (empty string) imio.actionspanel confirmation
          default view is used instead.
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

    def addableContents(self):
        """
          Return addable content types.
        """
        factories_view = getMultiAdapter((self.context, self.request),
                                         name='folder_factories')
        return factories_view.addable_types()

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
            # can not access the obj anymore, try to find a place viewable by the user
            redirectToUrl = self._redirectToViewableUrl()
            # add a specific portal_message before redirecting the user
            msg = _('redirected_after_transition_not_viewable',
                    default="You have been redirected here because you do not have "
                            "access anymore to the element you just changed the state for.")
            plone_utils.addPortalMessage(msg, 'warning')
            return self.request.RESPONSE.redirect(redirectToUrl)
        else:
            return self._gotoReferer()

    def _redirectToViewableUrl(self):
        """
          Return a url the user may access.
          This is called when user does not have access anymore to
          the object he triggered a transition for.
          First check if HTTP_REFERER is not the object not accessible, if it is not, we redirect
          to HTTP_REFERER, but if it is, we check parents until we find a viewable parent.
        """
        http_referer = self.request['HTTP_REFERER']
        if not http_referer.startswith(self.context.absolute_url()):
            # HTTP_REFERER is not the object we have not access to anymore
            # we can redirect to it...  probably...
            redirectToUrl = http_referer
        else:
            # if HTTP_REFERER is the object we can not access anymore
            # we will try to find a parent object we can be redirected to
            parent = self.context.getParentNode()
            while not self.member.has_permission('View', parent):
                if parent.portal_type == 'Plone Site':
                    # if we arrived to the root Plone Site and it is still
                    # not viewable, we can not do anything else but raise an error...
                    raise Exception('Unable to redirect user to a viewable place!')
                else:
                    parent = parent.getParentNode()
            redirectToUrl = parent.absolute_url()
        return redirectToUrl

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
    def __init__(self, context, request):
        super(DeleteGivenUidView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()

    def __call__(self, object_uid):
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

        # we use an adapter to manage if we may delete the object
        # that checks if the user has the 'Delete objects' permission
        # on the content by default but that could be overrided
        self.member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        if self.member.has_permission("Delete objects", obj) and IContentDeletable(obj).mayDelete():
            msg = {'message': _('object_deleted'),
                   'type': 'info'}
            # remove the object
            # just manage BeforeDeleteException because we rise it ourselves
            from OFS.ObjectManager import BeforeDeleteException
            try:
                unrestrictedRemoveGivenObject(obj)
            except BeforeDeleteException, exc:
                msg = {'message': exc.message,
                       'type': 'error'}
        else:
            # as the action calling delete_givenuid is already protected by the chek
            # made in the 'if' here above, if we arrive here it is that user is doing
            # something wrong, we raise Unauthorized
            raise Unauthorized

        # Redirect the user to the correct page and display the correct message.
        backURL = self._computeBackURL(obj)
        self.portal.plone_utils.addPortalMessage(**msg)
        return self.request.RESPONSE.redirect(backURL)

    def _computeBackURL(self, obj):
        '''This is made to be overriden...'''
        objectUrl = obj.absolute_url()
        refererUrl = self.request['HTTP_REFERER']
        if not refererUrl.startswith(objectUrl):
            backURL = refererUrl
        else:
            # find a parent the current user may access
            backURL = self._findViewablePlace(obj)
        return backURL

    def _findViewablePlace(self, obj):
        '''
          Find a place the current user may access.
          By default, it will try to find a viewable parent.
        '''
        parent = obj.getParentNode()
        while (not self.member.has_permission('View', parent) and not parent.meta_type == 'Plone Site'):
            parent = parent.getParentNode()
        return parent.absolute_url()
