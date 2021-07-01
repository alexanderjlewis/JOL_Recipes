$(document).on("click", ".open-ingredientModal-add", function() {
    resetAddEditIngredientForm()

    $("#addEditIngredientForm #inputMode")[0].value = "add";
});

$(document).on("click", ".open-ingredientModal-edit", function(event) {
    resetAddEditIngredientForm()

    $("#addEditIngredientForm #inputMode")[0].value = "edit";
    $('input[name=inputIngredientName]')[0].value = $(this)[0].dataset.name;
    $('input[name=inputIngredientName]')[0].readOnly = true;
});

function resetAddEditIngredientForm() {
    $('input').prop('readonly', false);
    $('input').removeClass('is-invalid is-valid');
    $('.invalid-feedback').empty();
    $("#addEditIngredientForm")[0].reset();
    $('#addEditIngredientForm .alert').hide();
};

$("#addEditIngredientForm").on("submit", function(event) {
    event.preventDefault(); //stop the form being handled by the default handler and use this custom one..

    $('input').removeClass('is-invalid is-valid')
    $('#addEditIngredientForm .alert').hide();

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
                location.reload(); //reload the page so the update data is retrieved
            } else if (response.status == 'general_error') {
                $('#addEditIngredientForm .alert').html(response.data.error_msg);
                $('#addEditIngredientForm .alert').show();
            } else {
                $.each(response.data, function(k, v) {
                    $('input[name=' + k + ']')[0].classList.add('is-invalid');
                    $('div[for=' + k + '].invalid-feedback').html(v);
                });
            };
        },
        error: function(data) {
            console.log(data);
        }
    });


});