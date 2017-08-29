// Function that shows a popup that asks the user if he really wants to delete
function confirmDeleteObject(base_url, object_uid, tag, msgName){
    if (!msgName) {
        msgName = 'delete_confirm_message';
    }
    var msg = window.eval(msgName);
    if (confirm(msg)) {
        deleteElement(base_url, object_uid, tag); }
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
};
jQuery(document).ready(preventDefaultClickTransition);

function triggerTransition(baseUrl, viewName, transition, tag) {
  // find comment in the page
  comment = '';
  if ($('form#confirmTransitionForm textarea').length) {
      comment = $('form#confirmTransitionForm textarea')[0].value;
      // find the right tag because we are in an overlay and the tag will
      // never be found like being in a faceted
      // find the button that opened this overlay
      overlay_id = $(tag).closest('div.overlay-ajax').attr('id');
      tag = $('[rel="#' + overlay_id + '"]');
  }

  // refresh faceted if we are on it, else, let triggerTransition manage redirect
  redirect = '0';
  if (!$('#faceted-form').has(tag).length) {
    redirect = '1';
  }

  $.ajax({
    url: baseUrl + "/" + viewName,
    dataType: 'html',
    data: {'transition': transition,
           'comment': comment,
           'form.submitted': '1',
           'redirect': redirect},
    cache: false,
    async: true,
    type: "POST",
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if ((redirect === '0') && !(data)) {
            Faceted.URLHandler.hash_changed();
            $.event.trigger({
                type: "ap_transition_triggered",
                tag: tag,
                transition: transition,
                comment: comment});
        }
        else {
            window.location.href = data;
        }
      },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}

function deleteElement(baseUrl, object_uid, tag) {
  redirect = '0';
  if (!$('#faceted-form').has(tag).length) {
    redirect = '1';
  }
  $.ajax({
    url: baseUrl + "/@@delete_givenuid",
    dataType: 'html',
    data: {'object_uid': object_uid,
           'redirect': redirect},
    cache: false,
    async: true,
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if ((redirect === '0') && !(data)) {
            Faceted.URLHandler.hash_changed();
            $.event.trigger({
                type: "ap_delete_givenuid",
                tag: tag});
        }
        else {
            if (data.search('<!DOCTYPE') != -1) {
                document.open();
                document.write(data);
                document.close();
            }
            else {
                window.location.href = data;
            }
        }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}