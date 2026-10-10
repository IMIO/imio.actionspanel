*** Settings ***
Documentation  Plone 6 Classic UI keywords. Same keyword names and arguments as ui_plone4.robot.
...            Robot Framework 3.0 syntax: shared with the Plone 4.3 (Python 2) environment.
...            Selectors checked on Plone 6.1 (collective.contact.contactlist) and, for the keywords used by
...            imio.actionspanel, on Plone 6.2 (phase 7).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***
${MODAL}  css=.modal-dialog
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist


*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    Click button  css=#buttons-login
    Wait until page contains element  css=#personaltools-menulink

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions ul
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories > a
    Wait until element is visible  css=#plone-contentmenu-factories ul

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id}  href  ${url}

The personal action is not available
    [Arguments]  ${action_id}
    Page should not contain element  css=#personaltools-${action_id}

The modal is open
    [Documentation]  Overlay (Plone 4) or modal (Plone 6) showing a form
    Wait until element is visible  ${MODAL} form

Modal element
    [Documentation]  Locator of the element with this id inside the modal
    ...              (an argument starting with # would be a robot comment)
    [Arguments]  ${id}
    [Return]  ${MODAL} [id="${id}"]

Save the modal
    [Documentation]  By name: the forms of imio.actionspanel have no button id
    Click button  css=.modal-footer [name="form.buttons.save"]

Cancel the modal
    Click button  css=.modal-footer [name="form.buttons.cancel"]

Click the modal button
    [Documentation]  Button of the form shown in the modal (moved to the modal footer), by id
    [Arguments]  ${id}
    Click button  css=.modal-footer [id="${id}"]

Input the modal field
    [Documentation]  Field of the form shown in the modal, by id
    [Arguments]  ${id}  ${text}
    Input text  ${MODAL} [id="${id}"]  ${text}

The modal shows the error
    [Arguments]  ${text}
    Wait until element contains  ${MODAL} .field.error  ${text}

The modal is closed
    Wait until page does not contain element  ${MODAL}

The status message contains
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

The content title is
    [Documentation]  Plone 6.2 views have no documentFirstHeading class on the title
    [Arguments]  ${title}
    Element should contain  css=#content h1  ${title}

The workflow state is
    [Documentation]  State shown in the workflow menu, by state id
    [Arguments]  ${state}
    Wait until page contains element  css=#plone-contentmenu-workflow .label-state-${state}

The folder lists
    [Documentation]  Link of the content in the folder view
    [Arguments]  ${title}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  xpath=//*[@id="content-core"]//a[normalize-space()="${title}"]
    ...  ELSE  Page should not contain element  xpath=//*[@id="content-core"]//a[normalize-space()="${title}"]

The folder lists in this order
    [Arguments]  ${first}  ${second}
    Page should contain element
    ...  xpath=//*[@id="content-core"]//a[normalize-space()="${first}"]/following::a[normalize-space()="${second}"]

The history is shown
    [Documentation]  @@contenthistorypopup (imio.history) in a modal
    Wait until element is visible  ${MODAL} th.history-action

The history shows the comment
    [Arguments]  ${comment}
    The history is shown
    Element should contain  ${MODAL} table  ${comment}

# Actions panel below the content, as buttons (testing.zcml viewlet, default params)

Click the transition button
    [Arguments]  ${transition}
    Click element  css=input.apButtonWF_${transition}

The transition button is available
    [Arguments]  ${transition}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=input.apButtonWF_${transition}
    ...  ELSE  Page should not contain element  css=input.apButtonWF_${transition}

Click the transition button of the async panel
    [Documentation]  Panel loaded by JS (testing.py RobotAsyncViewlet, page called with ?async_panel=1)
    [Arguments]  ${transition}
    Wait until element is visible  css=#async_actions_panel input.apButtonWF_${transition}
    Click element  css=#async_actions_panel input.apButtonWF_${transition}

Click the delete button
    [Documentation]  Asks for a confirmation (JS confirm)
    Click element  css=input.apButtonAction_delete

The delete button is available
    [Arguments]  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=input.apButtonAction_delete
    ...  ELSE  Page should not contain element  css=input.apButtonAction_delete

Accept the confirmation
    Handle alert  ACCEPT

Dismiss the confirmation
    Handle alert  DISMISS

Click the action button
    [Documentation]  object_buttons action, by action id
    [Arguments]  ${action}
    Click button  css=input.apButtonAction_${action}

The action button is available
    [Arguments]  ${action}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=input.apButtonAction_${action}
    ...  ELSE  Page should not contain element  css=input.apButtonAction_${action}

Input the modal comment
    [Arguments]  ${comment}
    Input text  ${MODAL} textarea[name="comment"]  ${comment}

# Actions panel above the content, as icons (testing.py RobotIconsViewlet)

Open the delete with comments form
    Click element  css=#icons-actions-panel a.delete-comments-overlay
    The modal is open

Open the history of the panel
    Click element  css=#icons-actions-panel a.overlay-history

The history icon is highlighted
    [Documentation]  Class of the history link when the last event has a comment (same icon)
    [Arguments]  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=#icons-actions-panel a.overlay-history.highlight-history-link img
    ...  ELSE  Page should contain element  css=#icons-actions-panel a.overlay-history:not(.highlight-history-link) img

Click the move arrow
    [Documentation]  direction: top, up, down or bottom
    [Arguments]  ${direction}
    Click element  css=#icons-actions-panel a[href*="position=${direction}&"]

The move arrow is available
    [Arguments]  ${direction}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=#icons-actions-panel a[href*="position=${direction}&"]
    ...  ELSE  Page should not contain element  css=#icons-actions-panel a[href*="position=${direction}&"]

Add content with the panel
    [Documentation]  Option of the add content list, by type title
    [Arguments]  ${type_title}
    Select from list by label  css=#icons-actions-panel select.apButtonSelect  ${type_title}

The add form is shown
    [Documentation]  Dexterity add form, by portal_type
    [Arguments]  ${portal_type}
    Wait until location contains  ++add++${portal_type}
    Page should contain element  css=#form
