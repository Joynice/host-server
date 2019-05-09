$(function () {
    $("#modal").click(function () {
        var dialog = $("#task-dialog");
        var urlInput = dialog.find("input[name='url']");
        var title = $("#myModalLabel");
        var cycleInput = dialog.find("input[name='cycle']");
        var numberInput = dialog.find("input[name='number']");
        urlInput.val("");
        cycleInput.val("");
        numberInput.val("");
        title.text("添加任务");
        dialog.modal('show')
    })
});

$(function () {
    $("#save-task-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $("#task-dialog");
        var urlInput = dialog.find("input[name='url']");
        var cycleInput = dialog.find("input[name='cycle']");
        var numberInput = dialog.find("input[name='number']");

        var url1 = urlInput.val();
        var cycle = cycleInput.val();
        var number= numberInput.val();
        var submitType = self.attr("data-type");
        var taskId = self.attr("data-id");

        if (!url1 || !number) {
            zlalert.alertInfoToast('缺少必要参数！');
            return;
        }
        var url = '';
        if (submitType == 'update') {
            url = '/utask/';
        } else {
            url = '/atask/'
        }
        zlajax.post({
            'url': url,
            'data': {
                'url1': url1,
                'cycle': cycle,
                'number': number,
                'task_id': taskId
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
    $(".edit-task-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $("#task-dialog");
        var title = $("#myModalLabel");
        dialog.modal("show");

        var tr = self.parent().parent();
        var url1 = tr.attr("data-url");
        var cycle = tr.attr("data-cycle");
        var number = tr.attr("data-number");

        var urlInput = dialog.find("input[name='url']");
        var cycleInput = dialog.find("input[name='cycle']");
        var numberInput = dialog.find("input[name='number']");
        var saveBtn = dialog.find("#save-task-btn");

        urlInput.val(url1);
        cycleInput.val(cycle);
        numberInput.val(number);
        title.text("修改任务");
        saveBtn.attr("data-type", 'update');
        saveBtn.attr('data-id', tr.attr('data-id'));
    })
});

$(function () {
    $(".delete-task-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var task_id = tr.attr('data-id');
        zlalert.alertConfirm({
            "msg": '您确定要删除该任务吗？',
            'confirmCallback': function () {
                zlajax.post({
                    'url': '/dtask/',
                    'data': {
                        'task_id': task_id,
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {
                            setTimeout(function () {
                                zlalert.alertSuccessToast('删除成功！');

                            }, 2000);
                            setTimeout(function () {
                                window.location.reload();
                            }, 3000);
                        }
                        else {
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

$(function () {
    $(".result-btn").click(function (event) {
        event.preventDefault();
        var self = $(this);
        var tr = self.parent().parent();
        var task_id = tr.attr('data-id');
        var dialog = $("#result-dialog");
        dialog.modal("show");
        zlajax.get({
            'url': '/tresult/',
            'data': {
                'task_id': task_id
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    console.log(data);
                    var str = JSON.stringify(data['data']['result']);
                    $('.modal-body').text(str);
                }
            }
        })
    })
});