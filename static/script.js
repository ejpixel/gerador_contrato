$(document).ready(function() {
    clientType();

    function clientType() {
        if ($("#type_client").val() == "regular") {
            $("#client_store_name input").removeAttr("required");
            $("#client_store_name").slideUp();
            $("#client_cnpj input").removeAttr("required")
            $("#client_cnpj").slideUp();;
        }
        else {
            $("#client_store_name input").attr("required", "required")
            $("#client_store_name").show("slow");
            $("#client_cnpj input").attr("required", "required")
            $("#client_cnpj").show("slow");
        }
    }

    function calculatePaymentPrice() {
        if ($("#payment").val() != "" && $("#price").val() != "") {
            let payment = $("#payment").val();
            let price = $("#price").val();
            $("#payment_price").val(price / payment);
        }
    }
    $("#type_client").on("change", clientType);
    $("#payment").on("input", calculatePaymentPrice);
    $("#price").on("input", calculatePaymentPrice);
})
