*** Settings ***
Documentation  imio.actionspanel keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.0 syntax (shared with the Plone 4.3 environment).
...            The robot site (testing.ROBOT_ACCEPTANCE) shows two actions panels on every content:
...            buttons below the content (default params: transitions, delete, object_buttons actions)
...            and icons above it (delete with comments, arrows, add content, history).
...            Document.publish is a transition to confirm.
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${FOLDER_URL}  ${PLONE_URL}/folder
${DOC_URL}  ${FOLDER_URL}/doc1
${SUBFOLDER_URL}  ${FOLDER_URL}/subfolder
${MEMBER}  member
${MEMBER_PASSWORD}  member_password


*** Keywords ***
Open a manager browser with a folder
    [Documentation]  "My folder" contains, in this order, "First document" (doc1),
    ...              "Second document" (doc2) and "Sub folder" (subfolder), all private
    Open test browser
    Enable autologin as  Manager
    ${uid}=  Create content  type=Folder  id=folder  title=My folder
    Create content  type=Document  container=${uid}  id=doc1  title=First document
    Create content  type=Document  container=${uid}  id=doc2  title=Second document
    Create content  type=Folder  container=${uid}  id=subfolder  title=Sub folder

Publish the document
    ${uid}=  Path to uid  /${PLONE_SITE_ID}/folder/doc1
    Fire transition  ${uid}  publish

The document is deleted
    [Documentation]  Its folder is shown and doesn't list it anymore
    Wait until location is  ${FOLDER_URL}
    The folder lists  First document  expected=${False}
    Go to  ${DOC_URL}
    The page is not found
