
$(function () {
    $("#modal").click(function () {
        var dialog = $("#user-dialog");
        var usernameInput = dialog.find("input[name='username']");
        var title = $("#myModalLabel");
        var emailInput = dialog.find("input[name='email']");
        var email_captInput = dialog.find("input[name='email-capt']");
        var passwordInput = dialog.find("input[name='password']");
        usernameInput.val("");
        emailInput.val("");
        email_captInput.val("");
        passwordInput.val("");
        title.text("添加用户");
        dialog.modal('show')
    })
});

$(function () {
   $('')
});