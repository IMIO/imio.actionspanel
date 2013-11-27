from zope.component import getMultiAdapter
from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class ConfirmTransitionView(BrowserView):
    '''
      This manage the overlay popup displayed when a transition needs to be confirmed.
      For other transitions, this views is also used but the confirmation popup is not shown.
    '''
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    def __call__(self):
        # check that the user has actually a transition to trigger with confirmation
        if not self.initTransition():
            self.request.RESPONSE.redirect(self.context.absolute_url())
        form = self.request.form
        # either we received form.submitted in the request because we are triggering
        # a transition that does not need a confirmation or we clicked on the save button of
        # the confirmation popup
        submitted = form.get('form.buttons.save', False) or form.get('form.submitted', False)
        cancelled = form.get('form.buttons.cancel', False)
        if submitted:
            uid_catalog = getToolByName(self.context, 'uid_catalog')
            obj = uid_catalog(UID=self.request['objectUid'])[0].getObject()
            obj.restrictedTraverse('@@actions_panel').triggerTransition(self.request.get('transition'),
                                                                        self.request.get('comment'))
        elif cancelled:
            # the only way to enter here is the popup overlay not to be shown
            # because while using the popup overlay, the jQ function take care of hidding it
            # while the Cancel button is hit
            self.request.response.redirect(form.get('form.HTTP_REFERER'))
        return self.index()

    @memoize
    def initTransition(self):
        '''
          Initialize values for the 'transition' form field
        '''
        res = ''
        availableTransitions = self.context.restrictedTraverse('@@actions_panel').getTransitions()
        for availableTransition in availableTransitions:
            if self.request.get('transition') == availableTransition['id'] and \
               availableTransition['confirm'] is True:
                res = self.request.get('transition')
        return res

    def initIStartNumber(self):
        '''
          Initialize values for the 'iStartNumber' form field
        '''
        return self.request.get('iStartNumber')

    def initLStartNumber(self):
        '''
          Initialize values for the 'lStartNumber' form field
        '''
        return self.request.get('lStartNumber')
