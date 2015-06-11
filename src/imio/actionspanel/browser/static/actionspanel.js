/* Function that shows a popup that asks the user if he really wants to delete
   some object. If confirmed, the form where p_theElement lies is posted. */
function confirmDeleteObject(theElement, msgName){
    if (!msgName) {
        msgName = 'delete_confirm_message';
    };
    var msg = window.eval(msgName);
    if (confirm(msg)) { getEnclosingForm(theElement).submit(); }
}

function getEnclosingForm(elem) {
  // Gets the form that surrounds the HTML p_elem.
  var node = elem.parentNode;
  while (node.nodeName != "FORM") { node = node.parentNode; }
  return node;
}

initializeOverlays = function () {
    jQuery(function($) {
        // Add transition confirmation popup
        $('a.link-overlay-actionspanel.transition-overlay').prepOverlay({
              subtype: 'ajax',
              closeselector: '[name="form.buttons.cancel"]',
        });
        // Content history popup
        $('a.overlay-history').prepOverlay({
           subtype: 'ajax',
           filter: 'h2, #content-history',
           cssclass: 'overlay-history',
           urlmatch: '@@historyview',
           urlreplace: '@@contenthistorypopup'
        });
    });
};

jQuery(document).ready(initializeOverlays);

// prevent
preventDefaultClickTransition = function() {
$("a.trigger-transition-prevent-default").click(function(event) {
  event.preventDefault();
});
$("input.trigger-transition-prevent-default").click(function(event){
  event.preventDefault();
});
}
jQuery(document).ready(preventDefaultClickTransition);

function triggerTransition(baseUrl, viewName, transition, tag) {
    // find comment in the page
    comment = '';
    if ($('form#confirmTransitionForm textarea').length) {
        comment = $('form#confirmTransitionForm textarea')[0].value;
    }

  $.ajax({
    url: baseUrl + "/" + viewName,
    dataType: 'html',
    data: {'transition':transition,
           'comment': comment,
           'form.submitted': '1',
           'redirect': '0'},
    cache: false,
    async: false,
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if (Faceted.BASEURL) {
            Faceted.URLHandler.hash_changed();
        }
        else {
            window.location.href = window.location.href;
        }
      },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}
