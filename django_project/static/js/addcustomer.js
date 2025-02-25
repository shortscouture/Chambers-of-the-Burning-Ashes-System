document.addEventListener("DOMContentLoaded", function () {
    let modeOfPayment = document.querySelector("#id_mode_of_payment");
    let fullPaymentFields = document.querySelector("#full_payment_fields");
    let installmentPaymentFields = document.querySelector("#installment_payment_fields");

    function togglePaymentFields() {
        if (modeOfPayment.value === "Full Payment") {
            fullPaymentFields.style.display = "block";
            installmentPaymentFields.style.display = "none";
        } else if (modeOfPayment.value === "6-Month Installment") {
            fullPaymentFields.style.display = "none";
            installmentPaymentFields.style.display = "block";
        } else {
            fullPaymentFields.style.display = "none";
            installmentPaymentFields.style.display = "none";
        }
    }

    // Run on page load
    togglePaymentFields();

    // Run when mode of payment changes
    modeOfPayment.addEventListener("change", togglePaymentFields);
});
