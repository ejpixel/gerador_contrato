$(document).ready(function() {
    $(".edition").hide();
    $(".clickable").attr("edited", "false");
    $(".clickable").on("click", function(){
        $(".edition").fadeOut();
        $(this).next().fadeIn();
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
})
