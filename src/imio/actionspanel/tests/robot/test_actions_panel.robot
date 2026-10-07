*** Settings ***
Documentation  Actions panel of a content, as buttons below it and as icons above it.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  imio_actionspanel.robot
Test Setup  Open a manager browser with a folder
Test Teardown  Close all browsers


*** Test Cases ***
A transition button changes the state of the document
    Go to  ${DOC_URL}
    The workflow state is  private
    Click the transition button  submit
    The status message contains  Item state changed
    The workflow state is  pending
    Location should be  ${DOC_URL}

A transition to confirm is triggered with a comment kept in the history
    Go to  ${DOC_URL}
    The history icon is highlighted  expected=${False}
    Click the transition button  publish
    The modal is open
    Input the modal comment  Published after review
    Save the modal
    The status message contains  Item state changed
    The workflow state is  published
    The history icon is highlighted
    Open the history of the panel
    The history shows the comment  Published after review

Cancelling a transition to confirm keeps the state
    Go to  ${DOC_URL}
    Click the transition button  publish
    The modal is open
    Input the modal comment  Not now
    Cancel the modal
    The modal is closed
    Location should be  ${DOC_URL}
    Reload page
    The workflow state is  private

The panel loaded by JS works as the panel of the page
    Go to  ${DOC_URL}?async_panel=1
    Click the transition button of the async panel  publish
    The modal is open
    Cancel the modal
    The modal is closed
    Click the transition button of the async panel  submit
    The status message contains  Item state changed
    The workflow state is  pending

The delete button deletes the document after a confirmation
    Go to  ${DOC_URL}
    Click the delete button
    Dismiss the confirmation
    Reload page
    Location should be  ${DOC_URL}
    The workflow state is  private
    Click the delete button
    Accept the confirmation
    The document is deleted

Delete with comments deletes the element and shows its parent
    [Documentation]  On a folder: on a document, the form deletes the parent (Known issues in MIGRATION.md)
    Go to  ${SUBFOLDER_URL}
    Open the delete with comments form
    Input the modal comment  No more needed
    Save the modal
    Wait until location is  ${FOLDER_URL}
    The folder lists  Sub folder  expected=${False}
    The folder lists  First document

The history icon opens the history
    Go to  ${DOC_URL}
    Open the history of the panel
    The history is shown

The arrows move the document in its folder
    Go to  ${DOC_URL}
    The move arrow is available  up  expected=${False}
    Click the move arrow  down
    The status message contains  position has changed
    The move arrow is available  up
    Go to  ${FOLDER_URL}
    The folder lists in this order  Second document  First document

The add content list opens the add form of the chosen type
    Go to  ${FOLDER_URL}
    Add content with the panel  Page
    The add form is shown  Document

The action buttons copy and paste the document
    Go to  ${DOC_URL}
    Click the action button  copy
    The status message contains  copied
    Go to  ${FOLDER_URL}
    Click the action button  paste
    The status message contains  pasted
    Go to  ${FOLDER_URL}/copy_of_doc1
    The content title is  First document

A member only gets the actions she may do
    Publish the document
    Go to  ${DOC_URL}
    The transition button is available  retract
    The delete button is available
    The action button is available  cut
    Log in with the login form  ${MEMBER}  ${MEMBER_PASSWORD}
    Go to  ${DOC_URL}
    The content title is  First document
    The transition button is available  retract  expected=${False}
    The delete button is available  expected=${False}
    The action button is available  cut  expected=${False}
    The action button is available  copy
