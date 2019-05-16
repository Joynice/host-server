$(function () {
   $("#gx").click(function (event) {
       event.preventDefault();
       zlalert.alertSuccessToast('更新成功');
       setTimeout(function () {
           window.location.reload();
       },1000)
   })
});