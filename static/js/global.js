$(document).ready(function() {
  // Show login modal if user not authenticated
  if (!Scratch.INIT_DATA.LOGGED_IN_USER.options.authenticated) {
    $('body').on('click.login', '[data-control="modal-login"]', function() {
      $('#login-dialog').modal('show');
      setTimeout(function() {
        $('#login-dialog input:first').focus();
      }, 200);
    });
  }

  // Prevent spacebar from scrolling when focused on SWF
  $('object').keydown(function(e) {
    if (e.keyCode === 32) {
      e.stopPropagation();
    }
  });

  // Optional: set jQuery UI dialog defaults
  if ($.ui && $.ui.dialog) {
    $.extend($.ui.dialog.prototype.options, {
      resizable: false,
      modal: true,
      dialogClass: 'jqui-modal',
      closeText: 'x'
    });
  }
});