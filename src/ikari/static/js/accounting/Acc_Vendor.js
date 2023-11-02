/* Search Account button new*/

$('#bank-table').on( 'draw.dt', function () {
    selectTableRow('#bank-table', 4);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

$('#btnSearchBank').on('click', function () {
    $('#bank-table').DataTable().destroy();
    $('#bank-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": url_load_bank_list,
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "currency_id", "sClass": "text-left", "visible": false},
            {"data": "currency", "sClass": "text-left"},
            {"data": "account", "sClass": "text-left"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="choices" id="' +
                        full.id + '" class="call-checkbox" value="' + full.id + '">';
                }
            }
        ]
    });
    setTimeout(() => {
        $('#bank-table').DataTable().columns.adjust();
    }, 300);
});

$('#btnSelectBank').on('click', function () {
    var selected_row = [];
    var dtTable = $('#bank-table').DataTable();
    $("input[name='choices']:checked").each(function () {
        selected_row.push(this.value);
    });
    $('#id_bank_code').val(selected_row[0]).trigger('change');
});


$('#id_currency').on('change', function () {
    var currency_id = parseInt($('#id_currency').val());

    $('#id_currency').find('option:selected').removeAttr('selected');
    $('#id_currency option[value=' + currency_id + ']').attr('selected', 'selected');
    $('#id_currency').val(currency_id);

    $.ajax({
        method: "POST",
        url: '/customers/load_currency_code/',
        dataType: 'JSON',
        data: {
            'currency_id': currency_id,
        },
        success: function (json) {
            $('#id_currency_name').val('');
            $('#id_currency_name').val(json.name);
        }
    });
});

$('#btnCurrencyCodeSelect').on('click', function () {

    var item_select_id = $("input[name='currency-code-choices']:checked").attr('id');
    var nRow = $("input[name='currency-code-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);


    $('#id_currency').find('option:selected').removeAttr('selected');
    $('#id_currency option[value=' + item_select_id + ']').attr('selected', 'selected');
    $('#id_currency').val(item_select_id);

    $('#select2-id_currency-container').attr('title', jqInputs[0].innerText);
    $('#select2-id_currency-container').text(jqInputs[0].innerText);

    $('#id_currency_name').val('');
    $('#id_currency_name').val(jqInputs[1].innerText);

    $(this).attr('data-dismiss', 'modal');
});


$('#btnDisCodeSelect').on('click', function () {

    var item_select_id = $("input[name='dis-code-choices']:checked").attr('id');
    var nRow = $("input[name='dis-code-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);

    $('#id_distribution').find('option:selected').removeAttr('selected');
    $('#id_distribution option[value=' + item_select_id + ']').attr('selected', 'selected');
    $('#id_distribution').val(item_select_id);
    var data_dis_code = $('#id_tax').data('dis-code');
    for (var i = 0; i < data_dis_code.length; i++) {
        var idtax  = data_dis_code[i].idtax;
        if (idtax == item_select_id) {
            $("#id_tax").val(idtax).trigger('change');
            break
         }else{
            $("#id_tax").val(0).trigger('change');
         }

    }
    $('*[data-dis-code="item_select_id"]');
    $('#select2-id_distribution-container').attr('title', jqInputs[0].innerText);
    $('#select2-id_distribution-container').text(jqInputs[0].innerText);

    $('#id_dis_name').val('');
    $('#id_dis_name').val(jqInputs[1].innerText);

    $(this).attr('data-dismiss', 'modal');
});

$('#id_distribution').on('change', function () {
    var dis_id = parseInt($('#id_distribution').val());
    $.ajax({
        method: "POST",
        url: '/suppliers/load_dis_code/',
        dataType: 'JSON',
        data: {
            'dis_id': dis_id,
        },
        success: function (json) {
            $('#id_dis_name').val('');
            $('#id_dis_name').val(json.name);
        }
    });
});

$('#btnTaxCodeSelect').on('click', function () {
    var item_select_id = $("input[name='tax-code-choices']:checked").attr('id');
    var nRow = $("input[name='tax-code-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);
    $('#id_tax').val(item_select_id).trigger('change');
    $('#id_tax_name').val('');
    $('#id_tax_name').val(jqInputs[1].innerText);
    $(this).attr('data-dismiss', 'modal');
});

$('#id_tax').on('change', function () {
    var tax_id = parseInt($('#id_tax').val());
    $.ajax({
        method: "POST",
        url: '/suppliers/load_tax_code/',
        dataType: 'JSON',
        data: {
            'tax_id': tax_id,
        },
        success: function (json) {
            $('#id_tax_name').val('');
            $('#id_tax_name').val(json.name);
        }
    });
});

$('#id_payment_code').on('change', function () {
    var payment_code_id = parseInt($('#id_payment_code').val());
    $.ajax({
        method: "POST",
        url: '/customers/load_payment_code/',
        dataType: 'JSON',
        data: {
            'payment_code_id': payment_code_id,
        },
        success: function (json) {
            $('#id_payment_code_name').val('');
            $('#id_payment_code_name').val(json.name);
        }
    });
});

$('#btnPaymentCodeSelect').on('click', function () {

    var item_select_id = $("input[name='payment-code-choices']:checked").attr('id');
    var nRow = $("input[name='payment-code-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);


    $('#id_payment_code').find('option:selected').removeAttr('selected');
    $('#id_payment_code option[value=' + item_select_id + ']').attr('selected', 'selected');
    $('#id_payment_code').val(item_select_id);

    $('#select2-id_payment_code-container').attr('title', jqInputs[0].innerText);
    $('#select2-id_payment_code-container').text(jqInputs[0].innerText);

    $('#id_payment_code_name').val('');
    $('#id_payment_code_name').val(jqInputs[1].innerText);

    $(this).attr('data-dismiss', 'modal');
});

$('#id_account_set').on('change', function () {
    var account_set_id = parseInt($('#id_account_set').val());
    $.ajax({
        method: "POST",
        url: '/customers/load_account_set/',
        dataType: 'JSON',
        data: {
            'account_set_id': account_set_id,
        },
        success: function (json) {
            $('#id_account_name').val('');
            $('#id_account_name').val(json.name);

            $('#id_currency').val(json.currency_id);
            $('#id_currency').trigger('change');
            // $('#id_currency option:not(:selected)').attr('disabled', true);
        }
    });
});

$('#id_bank_code').on('change', function () {
    var bank_set_id = parseInt($('#id_bank_code').val());
    $.ajax({
        method: "POST",
        url: '/suppliers/load_bank_set/',
        dataType: 'JSON',
        data: {
            'bank_set_id': bank_set_id,
        },
        success: function (json) {
            $('#id_bank_name').val('');
            $('#id_bank_name').val(json.name);
        }
    });
});


$('#id_term_days').on('change', function () {
    $('#term_days_value').val('');
    $('#term_days_value').val($('#id_term_days').val() + ' days');

});


$('#btnTermCodeSelect').on('click', function () {

    var item_select_id = $("input[name='term-code-choices']:checked").attr('id');
    var nRow = $("input[name='term-code-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);


    $('#id_term_days').find('option:selected').removeAttr('selected');
    $('#id_term_days option[value=' + item_select_id + ']').attr('selected', 'selected');
    $('#id_term_days').val(item_select_id);

    $('#select2-id_term_days-container').attr('title', jqInputs[0].innerText);
    $('#select2-id_term_days-container').text(jqInputs[0].innerText);

    $('#term_days_value').val('');
    $('#term_days_value').val(jqInputs[1].innerText);

    $(this).attr('data-dismiss', 'modal');
});

$('#btnSearchAccount').on('click', function () {

    $('#account-table').DataTable().destroy();
    $('#account-table').dataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[0, "desc"]],
        "columnDefs": [
            {
                className: "hide_column",
                targets: [5,]
            },
        ],
        "serverSide": true,
        "ajax": {
            "url": "/suppliers/account_set_list/"
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "control_account", "sClass": "text-left"},
            {"data": "currency_code", "sClass": "text-left"},
            {"data": "revaluation_account", "sClass": "text-left"},
            {"data": "currency_id", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="account-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });
});


function changeAccount() {
    var row = $("input[name='account-choices']:checked").val();
    if (row) {
        var table = $('#account-table').DataTable();
        var id_account = table.cell(row, $("#acc-id").index()).data();
        var id_account_code = table.cell(row, $("#acc-code").index()).data();
        var id_account_name = table.cell(row, $("#acc-name").index()).data();
        $("#id_account_set").val(id_account);
        $("#id_account_name").val(id_account_name);

        $("#AccountListModal").modal("hide");
    }
    else {
        $("#account_error").text("Please choose 1 account");
    }
}

$('#btnAccountSelect').on('click', function () {

    var item_select_id = $("input[name='account-choices']:checked").attr('id');
    var nRow = $("input[name='account-choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);


    $('#id_account_set').find('option:selected').removeAttr('selected');
    $('#id_account_set option[value=' + item_select_id + ']').attr('selected', 'selected');
    $('#id_account_set').val(item_select_id);

    $('#select2-id_account_set-container').attr('title', jqInputs[0].innerText);
    $('#select2-id_account_set-container').text(jqInputs[0].innerText);

    $('#id_account_name').val('');
    $('#id_account_name').val(jqInputs[1].innerText);

    $('#id_currency').val(jqInputs[5].innerText);
    $('#id_currency').trigger('change');
    $('#id_currency option:not(:selected)').attr('disabled', true);

    $(this).attr('data-dismiss', 'modal');
});
/* End Search Account button new*/




