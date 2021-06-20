//initialise toasts
//$('.toast').toast(option)

$(document).on("click", ".open-ingredientModal-add", function() {
    $('input').prop('readonly', false);
    $('input').removeClass('is-invalid is-valid');
    $('.invalid-feedback').empty();
    $("#addEditIngredientForm")[0].reset();


    $("#addEditIngredientForm #inputMode")[0].value = "add";
});

$(document).on("click", ".open-ingredientModal-edit", function(event) {
    $('input').prop('readonly', false);
    $('input').removeClass('is-invalid is-valid');
    $('.invalid-feedback').empty();
    $("#addEditIngredientForm")[0].reset();


    $("#addEditIngredientForm #inputMode")[0].value = "edit";

    $('input[name=inputIngredientName]')[0].value = $(this)[0].dataset.name + '123';
    $('input[name=inputIngredientName]')[0].readOnly = true;
});

$("#addEditIngredientForm").on("submit", function(event) {
    event.preventDefault(); //stop the form being handled by the default handler and use this custom one..

    $('input').removeClass('is-invalid is-valid')

    var formValues = $(this).serialize();

    $('input').removeClass('is-invalid is-valid')

    $.ajax({
        type: "POST",
        url: '/api/addEditIngredient',
        dataType: 'json',
        data: formValues,
        contentType: 'application/x-www-form-urlencoded',
        success: function(response) {
            if (response.status == 'success') {
                // data.redirect contains the string URL to redirect to
                location.reload();
            } else if (response.status == 'general_error') {
                console.log(response)
                $('#addEditIngredientForm .alert').html(response.error_msg);
                $('#addEditIngredientForm .alert').show();
            } else {
                $.each(response.data, function(k, v) {
                    $('input[name=' + k + ']')[0].classList.add('is-invalid');
                    $('div[for=' + k + '].invalid-feedback').html(v);
                });

                console.log(response);
            };
        },
        error: function(data) {
            console.log(data);
        }
    });


});