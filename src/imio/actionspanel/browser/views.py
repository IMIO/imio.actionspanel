from appy.gen import No

from AccessControl import getSecurityManager
from Acquisition import aq_base

from zope.component import getMultiAdapter
from zope.i18n import translate

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflow.Expression import createExprContext
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION


class ActionsPanelView(BrowserView):
    """
      This manage the view displaying actions on context
    """
    def __init__(self, context, request):
        super(ActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()
        self.SECTIONS_TO_RENDER = ('renderTransitions',
                                   'renderEdit',
                                   'renderActions', )
        self.IGNORABLE_ACTIONS = ()

    def render(self,
               useIcons=True,
               showTransitions=True,
               appendTypeNameToTransitionLabel=False,
               showEdit=True,
               showActions=True,
               **kwargs):
        """
        """
        self.useIcons = useIcons
        self.showTransitions = showTransitions
        self.appendTypeNameToTransitionLabel = appendTypeNameToTransitionLabel
        self.showEdit = showEdit
        self.showActions = showActions
        self.kwargs = kwargs
        self.hasActions = False
        return self.index()

    def _renderSections(self):
        """
        """
        res = ''
        for section in self.SECTIONS_TO_RENDER:
            renderedSection = getattr(self, section)() or ''
            res += renderedSection
        return res

    def renderTransitions(self):
        """
        """
        if self.showTransitions:
            return ViewPageTemplateFile("actions_panel_transitions.pt")(self)
        return ''

    def renderEdit(self):
        """
        """
        if self.showEdit and self.mayEdit():
            return ViewPageTemplateFile("actions_panel_edit.pt")(self)
        return ''

    def renderActions(self):
        """
        """
        if self.showActions:
            return ViewPageTemplateFile("actions_panel_actions.pt")(self)

    def mayEdit(self):
        """
          Method that check if special 'edit' action has to be displayed.
        """
        member = self.context.restrictedTraverse('@@plone_portal_state').member()
        return member.has_permission('Modify portal content', self.context) and self.useIcons

    def saveHasActions(self):
        """
          Save the fact that we have actions
        """
        self.hasActions = True

    def getTransitions(self):
        '''This method is similar to portal_workflow.getTransitionsFor, but
           with some improvements:
           - we retrieve transitions that the user can't trigger, but for
             which he needs to know for what reason he can't trigger it;
           - for every transition, we know if we need to display a confirm
             popup or not.
        '''
        res = []
        # Get the workflow definition for p_obj.
        wfTool = getToolByName(self.context, 'portal_workflow')
        workflows = wfTool.getWorkflowsFor(self.context)
        if not workflows:
            return res
        workflow = workflows[0]
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
                                                            getSecurityManager(),
                                                            workflow,
                                                            self.context)
                if mayTrigger or isinstance(mayTrigger, No):
                    # Information about this transition must be part of result.
                    preName = '%s.%s' % (self.context.meta_type, transition.id)
                    tInfo = {
                        'id': transition.id,
                        'title': translate(transition.title,
                                           domain='plone',
                                           context=self.request),
                        'description': transition.description,
                        'name': transition.actbox_name, 'may_trigger': True,
                        'confirm': preName in toConfirm,
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
        """
        return []

    def _checkTransitionGuard(self, guard, sm, wf_def, ob):
        '''This method is similar to DCWorkflow.Guard.check, but allows to
           retrieve the truth value as a appy.gen.No instance, not simply "1"
           or "0".'''
        u_roles = None
        if wf_def.manager_bypass:
            # Possibly bypass.
            u_roles = sm.getUser().getRolesInContext(ob)
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
                u_roles = sm.getUser().getRolesInContext(ob)
            for role in guard.roles:
                if role in u_roles:
                    break
            else:
                return 0
        if guard.groups:
            # Require at least one of the specified groups.
            u = sm.getUser()
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
        """
        actionsTool = getToolByName(self, 'portal_actions')
        allActions = actionsTool.listFilteredActionsFor(self.context)

        objectButtonActions = []
        if 'object_buttons' in allActions:
            objectButtonActions = allActions['object_buttons']

        res = []
        for action in objectButtonActions:
            if not (action['id'] in self.IGNORABLE_ACTIONS):
                act = [action['url']]
                # We try to append the url of the icon of the action
                # look on the action itself
                if action['icon']:
                    # make sure we only have the action icon name not a complete
                    # path including portal_url or so...
                    act.append(action['icon'].split('/')[-1])
                else:
                    act.append('')
                act.append(action['title'])
                act.append(action['id'])
                res.append(act)
        return res
