$(function () {
    $("#modal").click(function () {
        var dialog = $("#cms-dialog");
        var urlInput = dialog.find("input[name='url']");
        var nameInput = dialog.find("input[name='name']");
        var reInput = dialog.find("input[name='re']");
        var md5Input = dialog.find("input[name='md5']");
        var title = $("#myModalLabel");
        urlInput.val("");
        nameInput.val("");
        reInput.val("");
        md5Input.val("");
        title.text("添加CMS");
        dialog.modal('show')
    })
});

$(function () {
    $("#save-cms-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $("#cms-dialog");
        var urlInput = dialog.find("input[name='url']");
        var nameInput = dialog.find("input[name='name']");
        var reInput = dialog.find("input[name='re']");
        var md5Input = dialog.find("input[name='md5']");

        var url1 = urlInput.val();
        var name = nameInput.val();
        var re = reInput.val();
        var md5 = md5Input.val();
        var submitType = self.attr("data-type");
        var cmsId = self.attr("data-id");

        if ((!re || !md5) && !name) {
            zlalert.alertInfoToast('缺少必要参数！');
            return;
        }
        var url = '';
        if (submitType == 'update') {
            url = '/ucms/';
        } else {
            url = '/acms/'
        }
        zlajax.post({
            'url': url,
            'data': {
                'url1': url1,
                'name': name,
                're': re,
                'md5': md5,
                'cms_id': cmsId
            },
            'success': function (data) {
                dialog.modal("hide");
                if (data['code'] == 200) {
                    //重新加载整个页面
                    zlalert.alertSuccessToast(data['message']);
                    setTimeout(function () {
                        window.location.reload();
                    }, 1000);

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

$(function () {
    $(".edit-cms-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $("#cms-dialog");
        var title = $("#myModalLabel");
        dialog.modal("show");

        var tr = self.parent().parent();
        var url1 = tr.attr("data-url");
        var name = tr.attr("data-name");
        var re = tr.attr("data-re");
        var md5 = tr.attr("data-md5");

        var urlInput = dialog.find("input[name='url']");
        var nameInput = dialog.find("input[name='name']");
        var reInput = dialog.find("input[name='re']");
        var md5Input = dialog.find("input[name='md5']");
        var saveBtn = dialog.find("#save-cms-btn");

        urlInput.val(url1);
        nameInput.val(name);
        reInput.val(re);
        md5Input.val(md5);
        title.text('修改CMS');
        saveBtn.attr("data-type", 'update');
        saveBtn.attr('data-id', tr.attr('data-id'));
    })
});

$(function () {
    $(".delete-cms-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var cms_id = tr.attr('data-id');
        zlalert.alertConfirm({
            "msg": '您确定要删除该CMS吗？',
            'confirmCallback': function () {
                zlajax.post({
                    'url': '/dcms/',
                    'data': {
                        'cms_id': cms_id,
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {
                            zlalert.alertSuccessToast('删除成功');
                            window.location.reload();
                        } else {
                            zlalert.alertInfo(data['message']);
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