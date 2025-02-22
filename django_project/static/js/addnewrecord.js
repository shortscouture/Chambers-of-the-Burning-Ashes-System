function togglePaymentFields() {
    var paymentMode = document.getElementById("id_mode_of_payment").value;
    var fullPaymentFields = document.getElementById("full_payment_fields");
    var installmentFields = document.getElementById("installment_payment_fields");

    if (paymentMode === "Full Payment") {
        fullPaymentFields.style.display = "block";
        installmentFields.style.display = "none";
    } else if (paymentMode === "6-Month Installment") {
        fullPaymentFields.style.display = "none";
        installmentFields.style.display = "block";
    } else {
        fullPaymentFields.style.display = "none";
        installmentFields.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    togglePaymentFields();
});