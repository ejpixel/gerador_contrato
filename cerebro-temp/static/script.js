$(document).ready(function() {
    $(".edition").hide();
    $(".clickable").attr("edited", "false");
    $(".clickable").mouseenter(function(){
        $(this).find(".edition").fadeIn(100);
    })
    $(".clickable").mouseleave(function(){
        $(this).find(".edition").fadeOut(100);
    })
    $(".edit").on("click", function () {
        $(this).parent().prev().attr("contenteditable", "true")
    })
    $(".clickable").on("input", function(){
        if (!$(this).prop("edited")) {
        let temp_saved_text = $(this).text()
        $(this).on("input", function(){
            if (temp_saved_text === $(this).text()) {
                $(this).attr("edited", "false")

            }
            else {
                $(this).attr("edited", "true")
            }
          })
        }
    })

    showHideView()
    function showHideView() {
        let id = $("#page-view").val()
        $("#" + id).show()
        $("#page-view option").each(function(){
            if ($(this).val() != id) {
                $("#" + $(this).val()).hide()
            }
        })
    }

    $("#page-view").on("change", showHideView);
})
