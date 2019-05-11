$(function () {
    $("#modal").click(function (event) {
        event.preventDefault();
        var flag = 1;
        zlajax.get({
            'url': '/addzc/',
            'data': {
                'flag': flag
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    zlalert.alertSuccessToast(data['message']);
                    setTimeout(function () {
                        window.location.reload()
                    }, 2000)
                }
            }
        })
    })
});

//显示ports
$(function () {
    $(".show-zc-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var td = self.parent().parent();
        var other = td.attr("data-other");
        var dialog = $("#show-dialog");
        dialog.modal("show");
        $("#other-body").text(other);
    })
});

//删除资产
$(function () {
    $(".delete-zc-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var zc_id = tr.attr("data-id");
        zlalert.alertConfirm({
            'msg': '确认要删除这条资产信息吗？',
            'confirmCallback': function () {
                zlajax.post({
                    'url': '/deletezc/',
                    'data': {
                        'zc_id': zc_id
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {
                            setTimeout(function () {
                                zlalert.alertSuccessToast(data['message']);
                            }, 100);
                            tr.remove();
                        } else {
                            zlalert.alertInfo(data['message']);
                        }
                    },
                    'fail': function () {
                        zlalert.alertNetworkError();
                    }
                })
            }
        });

    })
});

//更改资产
$(function () {
    $(".edit-zc-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var dialog = $("#zc-dialog");
        var textInput = dialog.find("input[name='text']");
        var saveBtn = dialog.find("#save-zc-btn");
        saveBtn.attr("data-id",tr.attr('data-id'));
        textInput.val('');
        dialog.modal('show');

    })
});

$(function () {
    $("#save-zc-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var zc_id = self.attr('data-id');
        var dialog = $("#zc-dialog");
        var typeInput = $("#AreaId");
        var type = typeInput.val();
        var textInput = dialog.find("input[name='text']");
        var text = textInput.val();
        if (text == '') {
            zlalert.alertInfoToast('请输入更改内容！');
            return;
        }
        console.log(type);
        zlajax.post({
            'url': '/uzc/',
            'data': {
                'zc_id': zc_id,
                'type': type,
                'text': text
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    zlalert.alertSuccessToast(data['message']);
                    //TODO:前端优化
                    setTimeout(function () {
                        window.location.reload()
                    }, 1000)
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function () {
                zlalert.alertNetworkError();
            }
        })
    })
});