# -*- coding: utf-8 -*-

from imio.helpers.content import uuidToObject
from plone import api
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView


class BaseCommentsView(BrowserView):
    """ """

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.actionspanel_view_name = self.request.get('actionspanel_view_name', 'actions_panel')
        self.force_redirect_after_transition = self.request.get(
            'force_redirect_after_transition', False) == '1'

    def __call__(self):
        form = self.request.form
        # either we received form.submitted in the request because we are applying
        # an action that does not need a confirmation or we clicked on the save button of
        # the confirmation popup
        submitted = form.get('form.buttons.save', False) or form.get('form.submitted') == '1'
        cancelled = form.get('form.buttons.cancel', False)
        actionspanel_view = self._get_actions_panel_view()
        if cancelled:
            # the only way to enter here is the popup overlay not to be shown
            # because while using the popup overlay, the jQ function take care of hidding it
            # while the Cancel button is hit
            return self.request.response.redirect(self.context.absolute_url())
        elif submitted:
            return self.apply(actionspanel_view)
        return self.index()

    def apply(self, actionspanel_view):
        """ """
        raise NotImplementedError

    def _get_actions_panel_view(self):
        '''Get and store the actionspanel view.'''
        if getattr(self, '_actions_panel_view', None):
            return self._actions_panel_view
        actionspanel_view = self.context.restrictedTraverse('@@%s' % self.actionspanel_view_name)
        actionspanel_view.forceRedirectAfterTransition = self.force_redirect_after_transition
        setattr(self, '_actions_panel_view', actionspanel_view)
        return actionspanel_view


class ConfirmTransitionView(BaseCommentsView):
    '''
      This manage the overlay popup displayed when a transition needs to be confirmed.
      For other transitions, this views is also used but the confirmation popup is not shown.
    '''

    def apply(self, actionspanel_view):
        """ """
        return actionspanel_view.triggerTransition(
            transition=self.request.get('transition'),
            comment=self.request.get('comment'),
            redirect=bool(self.request.get('redirect') == '1'))

    @memoize
    def init_transition(self):
        '''Initialize values for the 'transition' form field.'''
        res = {}
        actionspanel_view = self._get_actions_panel_view()
        availableTransitions = actionspanel_view.getTransitions()
        for availableTransition in availableTransitions:
            if self.request.get('transition') == availableTransition['id'] and \
               availableTransition['confirm'] is True:
                res['id'] = self.request.get('transition')
                res['confirm'] = False
        return res

    def transition_title(self):
        '''Returns transition title.'''
        actionspanel_view = self._get_actions_panel_view()
        availableTransitions = actionspanel_view.getTransitions()
        for availableTransition in availableTransitions:
            if self.request.get('transition') == availableTransition['id']:
                return availableTransition['title']


class DeleteWithCommentsView(BaseCommentsView):
    '''
      This manage the overlay popup displayed when deleting an element
      and comments may be provided.
    '''

    def __call__(self):
        """ """
        self.obj = uuidToObject(self.request.get('uid'))
        return super(DeleteWithCommentsView, self).__call__()

    def apply(self, actionspanel_view):
        """ """
        return api.portal.get().restrictedTraverse('@@delete_givenuid')(
            object_uid=self.request.get('uid'),
            historize_in_parent=True)

    def element_title(self):
        '''Returns element title.'''
        return self.obj.Title()

    def pre_comment(self):
        """Possibility to insert computed pre comment before the manually encoded comments.
           Here to be overrided."""
        # avoid character ' in result, that breaks generated JS
        return self.element_title().replace("'", "&#39;")
