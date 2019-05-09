
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
        $("#password1").show();
        dialog.modal('show')
    })
});

//发送邮件
$(function () {
    $('#email-capt').click(function (event) {
        event.preventDefault();
        var dialog = $("#user-dialog");
        var email = dialog.find("input[name='email']").val();
        event.preventDefault();
        var self = $(this);

        console.log(email);
        if (!(/^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/.test(email))) {
            zlalert.alertInfoToast('请输入正确格式的邮箱地址！');
            return;
        }
        // var timestamp = (new Date).getTime();
        // var sign = md5(timestamp+email+"q3423805gdflvbdfvhsdoa`#$%")
        zlajax.get({
            'url': '/email_captcha/',
            'data': {
                'email': email,
                // 'timestamp': timestamp,
                // 'sign': sign
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    zlalert.alertSuccessToast('邮件已发送，请注意查收！');
                    self.attr("disabled", 'disabled');
                    var timeCount = 60;
                    var timer = setInterval(function () {
                        timeCount--;
                        self.text(timeCount);
                        if (timeCount <= 0) {
                            self.removeAttr('disabled');
                            clearInterval(timer);
                            self.text('发送验证码');
                        }
                    }, 1000);
                } else {
                    zlalert.alertInfoToast(data['message']);
                }

            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        })
    });
});

//提交表单
$(function () {
    $("#save-user-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $('#user-dialog');
        var username = dialog.find("input[name='username']").val();
        var password = dialog.find("input[name='password']").val();
        var email_capt = dialog.find("input[name='email-capt']").val();
        var email = dialog.find("input[name='email']").val();
        var options = $("#AreaId option:selected");//获取当前选择项.
        var role = options.val();//获取当前选择项的值.
        var submitType = self.attr("data-type");
        var user_id = self.attr("data-id");
        console.log(username, email);

        var url = '';
        if (submitType == "update") {
            url = '/updateuser/';
            if (!username || !email) {
                zlalert.alertInfoToast("缺少必要参数！");
                return;
            }
        } else {
            url = '/adduser/';
            if (!username || !password || !email_capt || !email) {
                zlalert.alertInfoToast("缺少必要参数！");
                return;
            }
        }

        zlajax.post({
            'url': url,
            'data': {
                'username': username,
                'password': password,
                'email': email,
                'email_capt': email_capt,
                'role': role,
                'user_id': user_id
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    zlalert.alertSuccessToast(data['message']);
                    setTimeout(function () {
                        window.location.reload()
                    }, 1000);
                } else {
                    zlalert.alertErrorToast(data['message']);
                }
            },
            'fail': function (erroe) {
                zlalert.alertNetworkError();
            }
        })

    })
});

//key
$(function () {
    $(".key").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var user_id = tr.attr('data-id');
        var key = self.attr('value');
        tr.attr('class','in_user');
        console.log(user_id, key);
        if (key == 'down') {
            var text = '禁用'
        } else {
            var text = '启用'
        }
        zlalert.alertConfirm({
            'msg': '是否' + text + 'Secret Key',
            'confirmCallback': function () {
                zlajax.post({
                        'url': '/iskey/',
                        'data': {
                            'user_id': user_id,
                            'key': key
                        },
                        'success': function (data) {
                            if (data['code'] == 200) {
                                setTimeout(function () {
                                    zlalert.alertSuccessToast(text + '成功！');
                                },2000);
                                setTimeout(function () {
                                    window.location.reload()
                                }, 3000);

                            } else {
                                zlalert.alertInfo(data['message']);
                            }
                        },
                        'fail': function () {
                            zlalert.alertNetworkError();
                        }
                    }
                )
            }
        })
    })
});

//编辑
$(function () {
    $(".edit-user-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $("#user-dialog");
        var title = $("#myModalLabel");
        $("#password1").hide();
        dialog.modal("show");

        var tr = self.parent().parent();
        var username = tr.attr("data-username");
        var email = tr.attr("data-email");
        var role = tr.attr("data-role");

        var usernameInput = dialog.find("input[name='username']");
        var emailInput = dialog.find("input[name='email']");
        var email_captInput = dialog.find("input[name='email-capt']");
        var options = $("#AreaId");//获取当前选择项.
        var saveBtn = dialog.find("#save-user-btn");
        email_captInput.attr('placeholder', '邮箱验证码');
        email_captInput.val("");
        usernameInput.val(username);
        emailInput.val(email);
        options.val(role);
        title.text("修改用户信息");
        saveBtn.attr("data-type", 'update');
        saveBtn.attr('data-id', tr.attr('data-id'));

    })
});

//禁用用户
$(function () {
   $(".user").click(function (event) {
       event.preventDefault();
       var self = $(this);
       var tr = self.parent().parent();
       var user_id = tr.attr('data-id');
       var status = self.val();
       var username = tr.attr('data-username');

        if (status == 'down') {
            var text = '禁用'
        } else {
            var text = '启用'
        }
       zlalert.alertConfirm({
           'msg': '确定要'+text+' '+ username+ ' '+ '用户',
           'confirmCallback': function () {
                zlajax.post({
                    'url': '/stopuser/',
                    'data':{
                        'user_id': user_id,
                        'status': status
                    },
                    'success':function (data) {
                        if(data['code']==200){
                            setTimeout(function () {
                                zlalert.alertSuccessToast(text+'成功！');
                            }, 2000);
                            setTimeout(function () {
                                window.location.reload();
                            },3000);

                        }else {
                            zlalert.alertInfoToast(data['message']);
                        }
                    },
                    'fail': function () {
                        zlalert.alertNetworkError();
                    }
                })
           }
       })
   })
});

$(function () {
   $("#query").click(function (event) {
       event.preventDefault();

       var roleInput = $("#role");
       if($("#or").is(':checked')){
           var or = '在线'
       }else {
           or = '所有'
       }

       var role = roleInput.val();
       if(role ==''){
           zlalert.alertInfoToast('请选择角色！');
           return;
       }
       $("#table tr").each(function () {
           var tr = $(this).children();
           var user_role = tr[2].innerText;
           console.log(role);
           $(this).hide();
          if (role==user_role){
                  $(this).show();
                  zlalert.alertSuccessToast('查询成功！');
              }
          if (role=='所有用户'){
              zlalert.alertSuccessToast('查询成功！');
              setTimeout(function () {
                  window.location.reload()
              },2000);

          }

       });

   })
});
