$(document).bind("ajaxStop", function () {
    location.reload();
});

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
               data.eq(i).css("background-color", "#F8F8FF")
            }
        })
    })

    $(".clickable").on("input", function() {
        $(this).attr("edited", "true");
    })

    $(".clickable").on('input', '.number', function() {
        if (!/^\d+$/.test($(this).text())) {
            $(this).text($(this).text().replace(/\D/g, ""))
        }
    });

    $(".save").click(function() {
        let modified_list = []
        let removed_list = []
        let headers = []
        let target = $(this).prev().attr("id")
        $(this).prev().find("tr > th").each(function() {headers.push($(this).html())});

        $("tr").each(function() {
        let tRow = $(this)
            if (tRow.attr("edited") === "true" || tRow.attr("mark-removed") === "true") {
                let modified = {};
                headers.map(function (element, i) {
                    modified[element] = tRow.find(`td:eq(${i})`).html()
                })
                if (tRow.attr("edited") === "true") {
                    modified_list.push(modified)
                }

                else if (tRow.attr("mark-removed") === "true") {
                    removed_list.push(modified)
                }

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

        else if (removed_list.length > 0) {
            $.ajax({
                type: "POST",
                contentType: 'application/json; charset=utf-8',
                dataType: "json",
                url: "remove_" + target,
                data: JSON.stringify(removed_list)
            });
        }
    })

    $(".remove").on("click", function(){
        $(this).parent().find("button").each(function(i, e){$(e).fadeOut()})
        $(this).parent().append("<div class='temp-popup'><span>Do you really wants to remove this item?</span><button class='btn- btn-danger btn-sm remove-confirmation'>Yes</button><button class='btn- btn-primary btn-sm remove-negation'>No</button></div>");
        $(this).next().fadeIn()
    })


    $(".edition").on("click", ".remove-confirmation", function(){
        $(this).parent().parent().parent().attr("mark-removed", "true")
        $(this).parent().parent().parent().css("background-color", "red")
        $(this).parent().parent().append("<button class='btn btn-primary btn-sm remove-negation'>Restore</button>")
        $(this).parent().remove()
    })

        $(".edition").on("click", ".remove-negation", function(){
        $(this).parent().parent().attr("mark-removed", "false")
        $(this).parent().parent().css("background-color", "")
        $(this).parent().find("button").each(function(i, e){$(e).fadeIn()})
        $(this).remove()
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
