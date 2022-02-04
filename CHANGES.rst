Changelog
=========

1.60 (2022-02-04)
-----------------

- Added possibility to force refresh the page after a WF transition even if on a faceted.
  [gbastien]

1.59 (2022-01-24)
-----------------

- In `actions_panel_actions` displaying `object_buttons`, use the link_target
  defined on the action, only set it to `target="_parent"` if nothing defined
  on the action.
  [gbastien]

1.58 (2022-01-14)
-----------------

- Avoid init `member` in `__init__`, that can lead to member being `Anonymous`.
  [gbastien]
- Fixed detection if transition triggered from faceted, use `has_faceted`
  from `imio.helpers`.
  [gbastien]
- Define a with/height in CSS for icons so it can be reused by
  `collective.js.tooltipster` when it computes the size of the tooltipster.
  [gbastien]
- Added CSS id with context `UID` to the `actions_panel` table.
  [gbastien]

1.57 (2021-11-08)
-----------------

- Whenever an error occurs in `ActionsPanelView.triggerTransition`, make sure
  we get the error in the returned portal message and log the full traceback
  in the Zope log.
  [gbastien]

1.56 (2021-09-09)
-----------------

- Fixed arrow used in message explaining when a transition is not triggerable.
  [gbastien]
- Prevent double clicks when triggering a WF transition by disabling
  the link for 2 seconds.
  [gbastien]

1.55 (2021-06-04)
-----------------

- Implement method `show` when using async like it is already the case when not
  using async to know if viewlet must be shown.
  [gbastien]
- Added `saveHasActions` call in actions_panel_add_content.pt.
  [sgeulette]
- Fixed `actions_panel_arrows.pt` to display the arrows in a table so we avoid
  icons being one under others when there is not enough place to display it,
  actions have to be always on the same line.
  [gbastien]

1.54 (2021-04-26)
-----------------

- Fixed broken JS event on comment popup `Confirm` button to prevent default behavior,
  this probably leads to action not triggered from time to time on `Firefox`.
  [gbastien]

1.53 (2021-04-21)
-----------------

- Fixed `ActionsPanelView.getTransitions` check on transitions to confirm
  informations, do not consider that prefix of given transition to confirm is a
  `meta_type` but consider it as a `class name` as with `dexterity`, the
  `meta_type` is always the same an no more useable to discriminate content.
  [gbastien]
- Added parameter `forceRedirectOnOwnDelete=False` to `ActionsPanelView.__call__`,
  when deleting an element, by default if current context is a faceted,
  the user is not redirected but the page is reloaded, if we are removing the
  page that holds the faceted then we need to redirect.
  [gbastien]
- In JS function `deleteElement`, set `async:true` for the XHR request.
  [gbastien]
- Fixed bug in Firefox not executing the JS `triggerTransition` XHR request when
  `async:true`, this was due to `preventDefaultClickTransition` not applied when
  using the `@@async_actions_panel` in the viewlet displaying actions,
  it was producing a `NS_BINDING_ERROR` because 2 click events were triggered.
  [gbastien]
- When not using the `useIcons` mode (so when using viewlet displaying buttons),
  if no action at all, do not return an empty HTML table, just return nothing.
  This let's hide the entire viewlet when using the `@@async_actions_panel`.
  [gbastien]

1.52 (2021-01-26)
-----------------

- Fixed behavior of just reloading the faceted when deleting an element,
  this was broken because behavior between JS and python code changed and the
  user was redirected to the default dashboard.
  [gbastien]

1.51 (2020-12-07)
-----------------

- Added parameter `view_name="@@delete_givenuid"` to JS functions
  `confirmDeleteObject` and `deleteElement` so it is possible to call another
  view when deleting an element.
  It is also possible to avoid refresh and manage it manually.
  [gbastien]
- Make sure table containing actions does not have any border especially on `<tr>`.
  [gbastien]

1.50 (2020-08-18)
-----------------

- Make CSS rule for `input[type="button"].notTriggerableTransitionButton` more
  specific so it is taken into account.
  [gbastien]
- Fix message (tag title) displayed on a not triggerable WF transition when
  displayed as a button, the transition title was not included in the message.
  [gbastien]

1.49 (2020-06-24)
-----------------

- Fixed broken functionnality, when an action url was a `javascript` action,
  it was not always taken into account because tag <a> `href` was not disabled
  using `event.preventDefault()`.
  [gbastien]

1.48.1 (2020-05-26)
-------------------

- Requires `imio.helpers`.
  [gbastien]

1.48 (2020-05-26)
-----------------

- In `DeleteGivenUidView.__call__`, use `imio.helpers.content.uuidsToObjects`
  with parameter `check_contained_uids=True` to get the object to delete,
  so if not found querying with `UID` index, it will use the `contained_uids`
  index if it exists in the `portal_catalog`.
  [gbastien]

1.47 (2020-04-29)
-----------------

- Add Transifex.net service integration to manage the translation process.
  [macagua]
- Add Spanish translation
  [macagua]
- In `actions_panel_actions.pt`, added `<form>` around `<input>`
  to be able to use `overlays`.
  [gbastien]

1.46 (2020-02-18)
-----------------

- Added renderFolderContents section, rendered following flag and/or interface.
  [sgeulette]
- In `views.AsyncActionsPanelView.__call__`, remove random value `'_' (ajax_load)`
  from `**kwargs` before calling the `@@actions_panel` or `ram_cached`
  `@@actions_panel.__call__` never work as kwargs are always different.
  [gbastien]

1.45 (2019-11-25)
-----------------

- Changed sections order.
  [sgeulette]

1.44 (2019-09-13)
-----------------

- By default, do not display the `Edit` action when calling
  `@@async_actions_panel`.
  [gbastien]

1.43 (2019-09-12)
-----------------

- Disabled first option of add content button list.
  [sgeulette]
- Added apButtonSelect class on select button
  [sgeulette]
- Do not link anymore showEdit to showIcons.
  Disabled by default showEdit in viewlet.
  Render edit as button too.
  [sgeulette]

1.42 (2019-06-28)
-----------------

- Store result of `ActionsPanelView.getTransitions` in `self._transitions` as
  it is called several times to make sure transitions are computed only one time.
  [gbastien]
- In `ConfirmTransitionView`, store the actionspanel view instead instanciating
  it several times as call to `actionspanel.getTransitions` is cached on the
  actionspanel view.
  [gbastien]

1.41 (2019-06-07)
-----------------

- In `load_actions_panel JS function`, do not reload in case of error or the
  page is reloaded ad vitam.  Display an error message instead.
  [gbastien]
- When using `string:` expressions, do not insert a blank space like
  `string: `` or it is kept once rendered.
  [gbastien]
- Manage `IGNORABLE_ACTIONS` the same way `ACCEPTABLE_ACTIONS` so we filter out
  first every non relevant actions then we evaluate it.
  Removed management of `IGNORABLE_CATEGORIES` and `IGNORABLE_PROVIDERS`, we
  only keep `object_buttons` and providers `portal_actions/portal_types`.
  [gbastien]

1.40 (2019-05-16)
-----------------

- Fixed message `KeyError: 'confirm'` in Zope log when a transition is
  triggered on an element for which it is not available anymore
  (already triggered in another browser tab for example).  In this case,
  we just refresh the page.
  [gbastien]
- Fix `saveHasActions` is not called when only untriggerable transitions.
  [gbastien]

1.39 (2019-03-27)
-----------------

- When showing actions and ACCEPTABLE_ACTIONS is defined, directly worked
  with those restricted set. Faster method.
  [sgeulette]
- Added parameter ActionsPanelViewlet.async (set to False by default) to be
  able to render the actions panel viewlet asynchronously using a JS Ajax
  request.  Set every JS ajax request with async:false to be sure that screen
  is refreshed when state changed.
  [gbastien]
- Disabled showOwnDelete when 'delete' is in acceptable actions
  [sgeulette]

1.38 (2019-01-31)
-----------------

- Install `collective.fingerpointing` as we rely on it.
  [gbastien]
- By default, do not render the viewlet in overlays.
  [gbastien]

1.37 (2018-11-06)
-----------------

- Use safely unicoded transition title.
  [sgeulette]

1.36 (2018-08-22)
-----------------

- Moved `views._redirectToViewableUrl` logic to `utils.findViewableURL` so it
  can be used by external code.
  [gbastien]
- Don't nullify margin of actionspanel-no-style-table.
  [sgeulette]

1.35 (2018-05-22)
-----------------

- In `triggerTransition`, do not only catch `WorkflowException` as raised error
  could be of another type.
  [gbastien]
- When an error occurs during a workflow transition, make sure we
  `transaction.abort()` or `review_state` is changed nevertheless.
  [gbastien]

1.34 (2018-04-20)
-----------------

- Use a real arrow character `🡒` instead `->` when building the transition not
  triggerable icon help message.
  [gbastien]
- Fixed call to unexisting method `actionspanel_view._gotoReferer()` when
  cancelling transition confirmation popup (only happens if popup is not
  correctly opened as an overlay).
  [gbastien]

1.33 (2018-03-19)
-----------------

- Rely on imio.history IHContentHistoryView.show_history to know if the history
  icon must be shown.  We need imio.history >= 1.17.
  [gbastien]

1.32 (2018-01-06)
-----------------

- Added possibility to define a target on the edit action. To do this,
  pass the value for `edit_action_target` in the kwargs.
  [sgeulette]

1.31 (2017-11-10)
-----------------

- Added icon on object buttons.
  [sgeulette]
- Added separate external edit button
  [sgeulette]

1.30 (2017-10-03)
-----------------

- Rely on `collective.fingerpointing` for logging capabilities, this replace the
  log message when an element is deleted.
  [gbastien]
- Call `transaction.abort` when an error occurs during deletion in
  `DeleteGivenUidView` to avoid leaving portal in an unconsitent state.
  [gbastien]

1.29 (2017-08-30)
-----------------

- Trigger JS event `ap_delete_givenuid` when an element is removed from a
  faceted page.
  [gbastien]
- Only show the actions panel viewlet on the view of the element, not on the
  other templates like `folder_contents` because it also displays buttons and
  user could be confused about that.
  [gbastien]
- Use same class `apButton` for buttons and select (add content) displayed on
  the actions panel viewlet.
  [gbastien]

1.28 (2017-05-24)
-----------------

- Added parameter `catch_before_delete_exception=True` to the
  `DeleteGivenUidView`.  By default it will catch `BeforeDeleteException`
  but when set to False, it will not be catch it.  This let's catch
  the exception in another method.
  [gbastien]
- Call `reindexObject` when the BeforeDeleteException is catched because at
  this moment, object has already been unindexed.
  [gbastien]

1.27 (2017-05-10)
-----------------

- Use api.adopt_roles rather than create a super user to execute a "own" delete
  action.
  [sdelcourt]
- Use plone.api.
  [gbastien]
- Pass `**kwargs` to ContentDeletableAdapter.mayDelete.
  [gbastien]

1.26 (2017-04-13)
-----------------

- Make sure action title is translated.
  [gbastien]

1.25 (2017-03-22)
-----------------

- Display the description of actions while displayed as input.
  [gbastien]

1.24 (2017-02-14)
-----------------

- Added class on form button.
  Changed select translation.
  [sgeulette]
- The transition reason for which a transition can not be triggered now contains
  the msg as a `zope.i18nmessageid.message.Message` instance, so translate it.
  This is done because the appy `No` msg attribute can not be unicode...
  [gbastien]

1.23 (2017-01-30)
-----------------

- Fix workflow guard check on group conditions.
  [sdelcourt]


1.22 (2017-01-23)
-----------------

- Corrected code to work with collective.externaleditor >= 1.0.3.
  [sgeulette]

1.21 (2016-12-21)
-----------------

- Implemented method `getGroups` for the APOmnipotentUser
  that returns an empty list because default implementation
  will raise an `AttributeError` on `portal_groups`.
  [gbastien]

1.20 (2016-12-05)
-----------------

- Added possibility to define a CSS class on the edit action.  To do this,
  pass the value for `edit_action_class` in the kwargs.  This make it possible
  to use a class that will enable an overlay for the edit action.
  [gbastien]
- Added section that renders arrows to move elements to top/up/down/bottom,
  this only appears if useIcons is True.
  [gbastien]
- While rendering transition button including portal_type title, translate
  portal_type title in the domain defined on the typeInfo of portal_types,
  not systematically in the "plone" domain.
  [gbastien]
- When an element is deleted, check if response received by JS method
  `deleteElement` is an url or a page content.  In case a Redirect exception
  is raised, we receive the entire page content and not an url to redirect to.
  [gbastien]
- Use permission `ManageProperties` to protect the `renderArrows` section.
  Make sure `saveHasActions` is called correctly in the
  `actions_panel_arrows.pt` template.
  [gbastien]
- Check if current context is a folderish in `addableContents` used for the
  `deleteElement` section because `folder_factories` return parent's addable
  content_types if current context is not folderish, this makes the button
  appear when you can not add content, and if used, content is actually added
  to the parent.
  [gbastien]
- Translate workflow transition title and no more id
  [sgeulette]

1.19 (2016-06-22)
-----------------

- Take external edition into account when rendering the `edit` action.
  [sdelcourt]

1.18 (2016-06-17)
-----------------

- Use window.open(url, `_parent`) to manage actions instead of window.location
  so new location is opened in the `_parent` frame, this way, when opened from
  an iframe, the location is not opened in the iframe but in the parent/full
  frame.
  [gbastien]
- Fixed CSS style for the notTriggerableTransition CSS class so it is displayed
  correctly in Chrome.
  [gbastien]

1.17 (2016-04-15)
-----------------

- Made a transitions sort method, that can be overrided.
  [sgeulette]

1.16 (2016-01-21)
-----------------

- Message when deleting an element (delete_confirm_message) is now more
  clear to specify that element will be deleted from the system definitively.
  [gbastien]
- When a WorkflowException is raised during a WF transition, display the exception
  message, this way a beforeTransition event may raise this exception and display
  a particular message to the user.
  [gbastien]


1.15 (2015-12-03)
-----------------

- Use an onClick instead of the `href` on the actions rendered by the
  `actions_panel_actions.pt` to be able to use a javascript method for
  the action URL.
  [gbastien]
- Use `async:false` for jQuery.ajax calls so the ajax loader image (spinner)
  is displayed in IE and Chrome.
  [gbastien]


1.14 (2015-10-06)
-----------------

- Use `POST` as type of jQuery.ajax used to add a comment to a workflow
  transition or it fails when the comment is too long.
  [gbastien]


1.13 (2015-09-04)
-----------------

- CSS for buttons displayed on the transition confirmation popup
  [gbastien]


1.12 (2015-07-14)
-----------------

- Make trigger transition and own delete aware of faceted navigation.
  If the action is made in a faceted navigation, only the faceted page
  is reloaded, not the entire page
  [gbastien]
- Hide the Add menu if no addable content
  [sgeulette]


1.11 (2015-04-23)
-----------------

- Do not generate the image name to use for a transition but
  use the actbox_icon defined on the transition
  [gbastien]


1.10 (2015-04-01)
-----------------

- Use translated transition title in transition confirmation popup
  [gbastien]
- Simplified @@triggertransition view by not using objectUID anymore, we use the context
  as the view is called on it, objectUID was legacy and useless
  [gbastien]


1.9 (2015-03-30)
----------------

- Store transitions to confirm in the registry
  [sgeulette]
- Add a small margin-left to the `notTriggerableTransitionImage` class so if several not
  triggerable transition actions are displayed, it is not stuck together
  [gbastien]
- Rely on imio.history to manage history related section
  [gbastien]

1.8 (2014-11-05)
----------------

- Removed IObjectWillBeRemovedEvent, either use same event from OFS.interfaces or in case we use
  AT, we could need to override manage_beforeDelete as it is called before IObjectWillBeRemovedEvent
  in the OFS object removal machinery.
- Do only rely on `mayDelete` method instead of checking `Delete objects` and mayDelete method,
  this way, we may handle case where user does not have the `Delete objects` but we want him
  to be able to delete an element nevertheless, in this case, the all logic is managed by mayDelete.


1.7 (2014-09-04)
----------------

- Sort transitions by transition title, more easy to use when displaying several transitons.
- Corrected bug where the link to trigger a transition that did not need to be confirmed,
  did not contain the view name, only parameters.  This made the user being redirected to the object
  view and not able to trigger the transition from another place.


1.6 (2014-08-21)
----------------

- Added submethod _findViewablePlace in _computeBackURL where we can manage
  where to redirect the member when he was on the object he just deleted.
  This makes it possible to override only the _findViewable method
  and keep the other part of _computeBackURL that does manage the case when
  the member was not on the object he just deleted.
- Custom action_panels views can now be registered with a different name
  than `actions_panel`.


1.5 (2014-08-20)
----------------

- Adpated _transitionsToConfirm method to be also able to provide custom
  view name to use as confirmation popup.


1.4 (2014-08-19)
----------------

- Moved complete computation of back url when an object is removed to
  _computeBackURL, not only the case when we were on the object we just removed.
- Added CSS class `actionspanel-no-style-table` on the main actions_panel table
  and defined styles for it to remove any border/margin/padding.


1.3 (2014-08-19)
----------------
- Added section that render a link to the object's history if useIcons is True
- Not triggerable transitions are now also displayed using icon if useIcons is True,
  before, not triggerable transitions were always displayed as button, no mater useIcons
  was True or False
- Simplified method that compute addable contents, the default `folder_factories`
  does all the job
- Manage the fact that if after a transition has been triggered on an object,
  this object is not accessible anymore to the current user, it is redirected
  to a viewable place

1.2 (2014-07-01)
----------------
- Do not lookup an object UID in the uid_catalog,
  this fails when using dexterity, use portal_catalog or
  check context UID if element is not indexed
- Do not display a `-` when no actions to display and not using icons
- Implement `__call__` instead of `render` on the actions panel view
  so calling the view is simpler
- Display AddContent actions.

1.1 (2014-04-03)
----------------
- Optimized to be `listing-aware` do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release
