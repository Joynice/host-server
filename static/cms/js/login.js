$(function () {
    $('#captcha-img').click(function (event) {
        var self = $(this);
        var src = self.attr('src');
        var newsrc = zlparam.setParam(src, 'xx', Math.random());
        self.attr('src', newsrc);
    });
});

$(function () {
    $(".login_btn").click(function (event) {
        event.preventDefault();
        var email_input = $("input[name=email]");
        var password_input = $("input[name='password']");
        var graph_captcha_input = $("input[name='graph_captcha']");
        var remember_input = $("input[name='remember']");

        var email = email_input.val();
        var password = password_input.val();
        var remember = remember_input.checked ? 1 : 0;
        var graph_captcha = graph_captcha_input.val();

        zlajax.post({
            'url': '/login/',
            'data': {
                'email': email,
                'password': password,
                'remember': remember,
                'graph_captcha': graph_captcha
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    window.location = '/admin/';
                } else {
                    zlalert.alertInfoToast(data['message']);
                }
            },
            'fail':function (error) {
                    zlalert.alertNetworkError();
                }

        })
    })
});