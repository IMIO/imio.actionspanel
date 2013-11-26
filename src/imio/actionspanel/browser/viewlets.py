from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter


class ActionsPanelViewlet(ViewletBase):
    '''This viewlet displays the available actions on the context.'''

    def update(self):
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')

    def available(self):
        """Is the viewlet available here?"""
        return True

    def renderViewlet(self):
        """Render the view @@actions_panel that display relevant actions.
           Here we want to display elements with full space, so not as icons."""
        return self.context.restrictedTraverse("@@actions_panel").render(useIcons=False)
