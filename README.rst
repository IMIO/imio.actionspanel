====================
imio.actionspanel
====================

This package provides a view and a sample viewlet that will display a table of different actions available on an element.

By default, so called sections available are :
- transitions
- edit
- actions
- allowed content types

Transitions :
=============
This will display different available workflow transitions and his managed by the section "renderTransitions".

Transitions to confirm :
------------------------
You can specify 'transitions to confirm' by overriding the '_transitionsToConfirm' method,
this will display a popup when the user trigger the transition that let's him add a
comment and accept/cancel workflow transition triggering.
The '_transitionsToConfirm' method must return a tuple that specify 'object_meta_type.transition_id' and could looks like :

def _transitionsToConfirm():
    """ """
    return ('ATDocument.reject', 'ATDocument.publish', 'ATFolder.publish', 'Collection.retract', )

Actions (portal_actions) :
==========================
This will display different available actions coming from portal_actions.object_buttons and his managed by the section "renderActions".

Ignorable and acceptable actions :
----------------------------------
It is possible to override the IGNORABLE_ACTIONS and ACCEPTABLE_ACTIONS so you filter existing actions and avoid to display them.

If ACCEPTABLE_ACTIONS are defined, only these action will be considered.  If IGNORABLE_ACTIONS are defined, every available
actions will be considered except if the action id is in the IGNORABLE_ACTIONS.

Edit :
======
This will display an edit action and his managed by the section "renderEdit".

By default, it is only available when useIcons is True as useIcons is supposed to be used in dashboards displaying several elements and not
on a particular element view.  On the element view, the edit action is not displayed as it is redundant with the already existing tab "Edit".
