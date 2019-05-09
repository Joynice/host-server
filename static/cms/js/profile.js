// 生成key
$(function () {
    $('#up').click(function (event) {
        event.preventDefault();
        zlajax.get(
            {
                url: '/secretkey/',
                data: {
                    'type': 1
                },
                'success': function (data) {
                    if (data['code'] == 200) {
                        zlalert.alertSuccessToast(data['message']);
                        setTimeout(function () {
                            window.location.reload()
                        }, 2000)
                    } else {
                        zlalert.alertInfoToast(data['message']);
                    }
                },
                'fail': function (error) {
                    zlalert.alertNetworkError()
                }
            }
        )

    })
});

//删除key
$(function () {
    $("#down").click(function (event) {
        event.preventDefault();
        zlajax.get(
            {
                url: '/secretkey/',
                data: {
                    'type': 2
                },
                'success': function (data) {
                    if (data['code'] == 200) {
                        zlalert.alertSuccessToast(data['message']);
                        setTimeout(function () {
                            window.location.reload()
                        }, 2000)
                    } else {
                        zlalert.alertInfoToast(data['message']);
                    }
                },
                'fail': function (error) {
                    zlalert.alertNetworkError()
                }
            }
        )
    })
});

//更新key
$(function () {
    $("#upgrade").click(function (event) {
        event.preventDefault();
        zlajax.get(
            {
                url: '/secretkey/',
                data: {
                    'type': 3
                },
                'success': function (data) {
                    if (data['code'] == 200) {
                        zlalert.alertSuccessToast(data['message']);
                        setTimeout(function () {
                            window.location.reload()
                        }, 2000)
                    } else {
                        zlalert.alertInfoToast(data['message']);
                    }
                },
                'fail': function (error) {
                    zlalert.alertNetworkError()
                }
            }
        )
    })
});

//修改头像
$(function () {
    $("button[title='Upload selected files']").click(function (event) {
        event.preventDefault();
        var formData = new FormData($('#uploadForm')[0]);
        console.log(formData);
        $.ajax({
            url: "/profile/",
            type: "POST",
            data: formData,
            async: true,
            cashe: false,
            contentType: false,
            processData: false,
            success: function (data) {
                if(data['code']==200){
                    zlalert.alertSuccessToast('头像修改成功！');
                    setTimeout(function () {
                        window.location.reload();
                    }, 500)
                }
                else {
                    zlalert.alertInfo(data['message']);
                }
            },
            error: function () {
                zlalert.alertInfo('上传文件太大！')
            }
        });
    });
});

//修改昵称
$(function () {
    $("#uusername").click(function (event) {
        event.preventDefault();
        zlalert.alertOneInput({
            'title': '请输入',
            'placeholder': '新的用户名',
            'confirmCallback': function (inputValue) {
                var username = inputValue;
                zlajax.post({
                    'url': '/uusername/',
                    'data':{
                        'username': username
                    },
                    'success':function (data) {
                        if(data['code']==200){
                            zlalert.alertSuccessToast('修改成功！');
                            setTimeout(function () {
                                window.location.reload();
                            },1000)
                        }else {
                            zlalert.alertErrorToast(data['message']);
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