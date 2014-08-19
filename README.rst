imio.actionspanel
=================

This package provides a view and a sample viewlet that will display a table of different actions available on an element.

By default, so called sections available are :

- transitions
- edit
- own delete action management
- actions
- addable types
- object history

Transitions :
-------------
This will display different available workflow transitions and is managed by the section "renderTransitions".

Transitions to confirm :
^^^^^^^^^^^^^^^^^^^^^^^^
You can specify 'transitions to confirm' by overriding the '_transitionsToConfirm' method,
this will display a popup when the user trigger the transition that let's him add a
comment and accept/cancel workflow transition triggering.
The '_transitionsToConfirm' method must return a tuple that specify 'object_meta_type.transition_id' and could looks like :

def _transitionsToConfirm():
    return ('ATDocument.reject', 'ATDocument.publish', 'ATFolder.publish', 'Collection.retract', )

Edit :
------
This will display an edit action and his managed by the section "renderEdit".

By default, it is only available when useIcons is True as useIcons is supposed to be used in dashboards displaying several elements and not
on a particular element view.  On the element view, the edit action is not displayed as it is redundant with the already existing tab "Edit".

Own delete management :
-----------------------
This own delete management is made to surround behaviour where it is necessary to delete an object to have the "Delete objects" permission on the parent.  Here, it will do delete work even if user does not have the permission "Delete objects" on the object's parent.  Just having "Delete objects" on the object to delete will be enough.  You can also override the adapter "ContentDeletableAdapter" to be able to define a "mayDelete" method that will do anything you want to check if current user may delete the object.  It is managed by the section "renderOwnDelete".

Actions (portal_actions.object_buttons) :
-----------------------------------------
This will display different available actions coming from portal_actions.object_buttons and is managed by the section "renderActions".

Ignorable and acceptable actions :
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It is possible to override the IGNORABLE_ACTIONS and ACCEPTABLE_ACTIONS so you filter existing actions and avoid to display them.

If ACCEPTABLE_ACTIONS are defined, only these action will be considered.  If IGNORABLE_ACTIONS are defined, every available
actions will be considered except if the action id is in the IGNORABLE_ACTIONS.

Addable types :
---------------
This will display a combo list that will display types that are addable in the object if it is a container.  It is managed by the section "renderAddContent".

Object history :
----------------
Add a link to the object's history and will be displayed in a popup.  It is managed by the section "renderHistory".
