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
        let headers = []
        let row = $(this).parent().parent()
        let data = row.find("td")
        row.parent().prev().find("tr > th").each(function() {
            header = [$(this).attr("class"), $(this).attr("type")]
            headers.push(header)
        })
        headers.map(function(element, i) {
            if (element[0] != null) {
               data.eq(i).attr("contenteditable", "true")
               data.eq(i).attr("class", element[1])
            }
        })
    })

    $(".clickable").on("input", function() {
        $(this).attr("edited", "true");
    })

    $(".clickable").on('input', '.number', function() {
        if (!/\d+/.test($(this).text)) {
            $(this).text($(this).text().slice(0, -1));
        }
    });

    $(".save").click(function() {
        let modified_list = []
        let headers = []
        let target = $(this).prev().attr("id")
        $(this).prev().find("tr > th").each(function() {headers.push($(this).html())});

        $("tr").each(function() {
        let tRow = $(this)
            if (tRow.attr("edited") === "true") {
                let modified = {};
                headers.map(function (element, i) {
                    modified[element] = tRow.find(`td:eq(${i})`).html()
                })
                modified_list.push(modified)
            }
        })
        if (modified_list.length > 0) {
            $.ajax({
                type: "POST",
                contentType: 'application/json; charset=utf-8',
                dataType: "json",
                url: "edit_" + target,
                data: JSON.stringify(modified_list)
            });
        }
    })


    showHideView();
    function showHideView() {
        let id = $("#page-view").val();
        $("#" + id).show();
        $("#page-view option").each(function() {
            if ($(this).val() != id) {
                $("#" + $(this).val()).hide();
            }
        })
    }

    $("#page-view").on("change", showHideView);
})
