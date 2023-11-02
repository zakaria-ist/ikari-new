
$(document).ready(function () {
    recalculateUndistributedAmount();
});


$('#doc_date_view').keyup(function(event){
    adjust_input_date(this);
});

$('#post_date_view').keyup(function(event){
    adjust_input_date(this);
});

$('#batch_view_date').keyup(function(event){
    adjust_input_date(this);
});

$('#id_document_number').on('change', function () {
    var value = $(this).val();
    var cust = $('#id_supplier').val();
    if (!cust) {
        cust = '0'
    }
    $.ajax({
        method: "POST",
        url: '/accounting/check_if_duplicate/AP_Invoice/document_number/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'value': value,
            'cust': cust
        },
        dataType: 'JSON',
        success: function (data) {
            var is_duplicate = data.data.is_duplicate;
            if (is_duplicate) {
                pop_ok_dialog("Error!",
                    "Duplicate document number !",
                    function () {
                        $('#id_document_number').val('');
                        $('#id_document_number').focus();
                    });
            }
        }
    });
});

$('#id_document_type').on('change', function() {
    if ($('#id_document_type').val() == 2 || ($('#id_document_type').val()) == 3){
        $('#customise_aplly').removeClass('hide');
        $('#div_orig_rate').removeClass('hide');
    } else {
        $('#customise_aplly').addClass('hide');
        $('#div_orig_rate').addClass('hide');
    }
});

$('#inv_id-table').on( 'draw.dt', function () {
    selectTableRow('#inv_id-table', 8);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

$('#id_inv').on('click', function () {
    var id_customer = $("#id_supplier").val();
    var balance_type = $('#id_document_type').val();
    if (id_customer) {
        $("#list_inv_journal").modal("show");
        $('#inv_id-table').DataTable().destroy();
        $('#inv_id-table').dataTable({
            "processing": true,
            "iDisplayLength": 7,
            "iDisplayStart": 0,
            "bLengthChange": false,
            "order": [[ 1, 'desc' ], [ 0, 'asc' ]],
            "serverSide": true,
            "stateSave": false,
            "ajax": {
                "url": "/accounting/document_list_aplly/",
                "data": {
                    "customer_id": id_customer,
                    "balance_type" :balance_type,
                    "journal_type" :'2' /* TRANSACTION_TYPES)['AP Invoice'] */
                    // 1 = AR , 2 = AP
                }
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "date", "sClass": "text-left"},
                {"data": "document_type", "sClass": "text-left"},
                {"data": "desc", "sClass": "text-left"},
                {"data": "payment_term", "sClass": "text-left"},
                {"data": "outstanding_amount", "sClass": "text-right"},
                {
                    "data": null,
                    "render": function (data, type, full, meta) {
                        if (full.is_fully_paid == 'True') {
                            var mSpan = '<span class="label label-success label-mini">Yes</span>'
                            return mSpan
                        }
                        else {
                            var mSpan = '<span class="label label-danger label-mini">No</span>'
                            return mSpan
                        }
                    }
                },
                {"data": "fully_paid_date", "sClass": "text-left", "orderable": false},
                {
                    "orderable": false,
                    "data": null,
                    "sClass": "hide_column",
                    "render": function (data, type, full, meta) {
                        return '<input type="radio" name="document-choices" id="' +
                            full.id + '" class="call-checkbox" value="' + meta.row + '">';
                    }
                },
                {"data": "id", "sClass": "text-left hidden"},
                {"data": "exch_rate", "sClass": "hidden"},
                {"data": "exch_rate_fk", "sClass": "hidden"}
            ]
        });

        setTimeout(() => {
            $('#inv_id-table').DataTable().columns.adjust();
        }, 300);
    }else{
        $("#list_inv_journal").modal("hide");

    }
});

function id_inv_applied() {
    var row = $("input[name='document-choices']:checked").val();
    if (row) {
        table = $('#inv_id-table').DataTable();
        id_inv_aplly = table.cell(row, $("#inv-id").index()).data();
        inv_document = table.cell(row, $("#inv-numb").index()).data();
        old_rate = table.cell(row, $("#exch_rate").index()).data();
        old_rate_pk = table.cell(row, $("#exch_rate_pk").index()).data();
        $("#id_related_invoice").val(id_inv_aplly);
        $("#related_invoice").val(inv_document);
        $("#orig_rate").val(old_rate);
        $("#orig_rate_pk").val(old_rate_pk);
        $("#list_inv_journal").modal("hide");
    }
}

$('#supplier-table').on( 'draw.dt', function () {
    selectTableRow('#supplier-table', 9);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Supplier button*/
$('#btnSearchSupplier').on('click', function () {
    $("#supplier_error").text(""); // Delete error message
    $('#supplier-table').DataTable().destroy();
    $('#supplier-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": "/accounting/supplier_list/"
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "term_days", "sClass": "text-left"},
            {"data": "payment_mode", "sClass": "text-left"},
            {"data": "credit_limit", "sClass": "text-left hide_column"},
            {"data": "id", "sClass": "text-left hide_column",},
            {"data": "tax_id", "sClass": "text-left hide_column",},
            {"data": "currency_id", "sClass": "text-left hide_column",},
            {"data": "currency_code", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="supplier-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });

    setTimeout(() => {
        $('#supplier-table').DataTable().columns.adjust();
    }, 300);
});

function changeSupllier() {
    var row = $("input[name='supplier-choices']:checked").val();
    if (row) {
        var table = $('#supplier-table').DataTable();

        // Supllier
        var supplier_id = table.cell(row, $("#sup-id").index()).data();
        // var id_supplier_code = table.cell(row, $("#sup-code").index()).data();
        // var id_supplier_name = table.cell(row, $("#sup-name").index()).data();
        // $("#id_supplier").val(supplier_id);
        // $("#id_supplier_code").val(id_supplier_code);
        // $("#id_supplier_name").val(id_supplier_name);
        $("#id_supplier").val(supplier_id).trigger('change');

        // Currency
        // var id_currency = table.cell(row, $("#sup-currency").index()).data();
        // var id_currency_code = table.cell(row, $("#sup-currency_code").index()).data();
        // $("#id_currency").val(id_currency);
        // $("#id_currency_code").val(id_currency_code);

        // Document Type
        // $("#id_document_number").val("");
        // $("#id_document_amount").val("");
        // $('#id_document_amount').trigger('change');

        // Tax
        // $('#id_tax_amount').val(0);
        // $('#id_total_amount').val(0);
        // $('#id_total_amount').trigger('change');

        $("#SupplierListModal").modal("hide");
    }
    else {
        $("#supplier_error").text("Please choose 1 supplier");
    }
}
/* End Search Supplier button*/


$('#account-table').on( 'draw.dt', function () {
    selectTableRow('#account-table', 6);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Account button*/
$('#btnSearchAccount').on('click', function () {
    $('#account-table').DataTable().destroy();
    $('#account-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        // scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/account_set_list/2/", /* ACCOUNT_SET_TYPE_DICT['AP Account Set'] */
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.currency_id = $('#id_currency').val();
            }
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "control_account", "sClass": "text-left"},
            {"data": "currency_code", "sClass": "text-left"},
            {"data": "revaluation_account", "sClass": "text-left"},
            {"data": "id", "sClass": "text-left hide_column"},
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

    setTimeout(() => {
        $('#account-table').DataTable().columns.adjust();
    }, 300);
});

function changeAccount() {
    var row = $("input[name='account-choices']:checked").val();
    if (row) {
        var table = $('#account-table').DataTable();
        var id_account = table.cell(row, $("#acc-id").index()).data();
        var id_account_code = table.cell(row, $("#acc-code").index()).data();
        $("#id_account_set").val(id_account);
        $("#id_account_code").val(id_account_code);

        $('#select2-id_account_set-container').attr('title', id_account_code);
        $('#select2-id_account_set-container').text(id_account_code)

        $("#AccountListModal").modal("hide");
    }
    else {
        $("#account_error").text("Please choose 1 account");
    }
}
/* End Search Account button*/

$('#exchange-table').on( 'draw.dt', function () {
    selectTableRow('#exchange-table', 5);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Enxchange Rate */
$('#btnSearchExchangeRate').on('click', function () {
    $('#exchange-table').DataTable().destroy();
    $('#exchange-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[2, "desc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/exchange_rate_list/",
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.currency_id = $('#id_currency').val();
            }
        },
        "columns": [
            {"data": "from_currency", "sClass": "text-left"},
            {"data": "to_currency", "sClass": "text-left"},
            {"data": "exchange_date", "sClass": "text-left"},
            {"data": "rate", "sClass": "text-left"},
            {"data": "id", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="exchange-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });

    setTimeout(() => {
        $('#exchange-table').DataTable().columns.adjust();
    }, 300);
});

function changeExchangeRate() {
    var row = $("input[name='exchange-choices']:checked").val();
    if (row) {
        table = $('#exchange-table').DataTable();
        id_exchange = table.cell(row, $("#exc-id").index()).data();
        rate = table.cell(row, $("#exc-rate").index()).data();

        $("#id_exchange_rate_fk").val(id_exchange);
        $("#id_exchange_rate").val(rate);

        setTimeout(() => {
            var exch_date = table.cell(row, $("#exc-date").index()).data();
            var year_perd = $('#doc_date_view').val();
            if (exch_date && year_perd) {
                if (exch_date.split('-')[1] != year_perd.split('-')[1]) {
                    pop_ok_dialog("Warning",
                        "This Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                        function () { });
                } else if (exch_date.split('-')[2] != year_perd.split('-')[2]) {
                    pop_ok_dialog("Warning",
                        "This Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                        function () { });
                }
            }
        }, 300);


        $("#ExchangeRateListModal").modal("hide");
    }
    else {
        $("#account_error").text("Please choose 1 account");
    }
}

$('#id_currency').on('change', function() {
    currency = $('#id_currency').val();

    if(currency && currency != company_currency) {
        $('#btnSearchExchangeRate').prop('disabled', false);
        $('#btnSearchTaxExchangeRate').prop('disabled', false);
        $('#id_exchange_rate').val('1.000000000');
        $('#id_tax_exchange_rate').val('1.000000000');
    } else if(currency && currency == company_currency) {
        // $('#btnSearchExchangeRate').prop('disabled', true);
        $('#id_exchange_rate').val('1.000000000');
        $('#id_tax_exchange_rate').val('1.000000000');
        //$("#exchange_id").val('0');
    } else {
        // $('#btnSearchExchangeRate').prop('disabled', true);
        $('#id_exchange_rate').val('1.000000000');
        $('#id_tax_exchange_rate').val('1.000000000');
    }
});

/* End Search Exchange Rate */

/* Search Document button*/
$('#btnSearchDocument').on('click', function () {
    $('#document-table').DataTable().destroy();
    $('#document-table').dataTable({
        "iDisplayLength": 5,
        "iDisplayStart": 0,
        "bLengthChange": false,
        "order": [[0, "desc"]],
        "serverSide": true,
        "stateSave": false,
        "ajax": {
            "url": "/accounting/supplier_document_list/",
            "data": {
                "supplier_id": $("#id_supplier").val()
            }
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "date", "sClass": "text-left"},
            {"data": "reference", "sClass": "text-left"},
            {"data": "amount", "sClass": "text-left"},
            {"data": "supplier_name", "sClass": "text-left"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="document-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            },
            {"data": "id", "sClass": "text-left hidden"}
        ]
    });
});

$('#document-table').on( 'draw.dt', function () {
    selectTableRow('#document-table', 5);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

function changeDocument() {
    $("#document_error").text(""); // Delete error message
    var row = $("input[name='document-choices']:checked").val();
    if (row) {
        var table = $('#document-table').DataTable();
        var id_document_number = table.cell(row, $("#doc-number").index()).data();
        var id_document_amount = table.cell(row, $("#doc-total_amount").index()).data();
        var id_order = table.cell(row, $("#doc-id").index()).data();
        $("#id_document_number").val(id_document_number);
        $("#id_document_amount").val(id_document_amount);
        $("#id_order_id").val(id_order);

        recalculateUndistributedAmount();
        $("#modalSearchDocument").modal("hide");
    }
    else {
        $("#account_error").text("Please choose 1 document");
    }
}
/* End Search Document button*/

function set_tax_reporting_rate() {
    var currency_id = $('#id_currency').val();
    var doc_date = $('#id_document_date').val();
    if(currency_id && doc_date) {
        get_tax_reporting_rate(currency_id, doc_date);
    }
}

// Seach on focus out
$('#id_supplier').on('change', function () {
    transaction_new.length = 0;
    transaction_update.length = 0;
    var supplier_id = parseInt($(this).val());
    $.ajax({
        method: "POST",
        url: url_load_supplier,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'supplier_id': supplier_id
        },
        success: function (json) {
            $('#id_supplier_name').val('');
            $('#id_supplier_code').val('');
            // $('#id_document_amount').val('0.00');
            
            recalculateUndistributedAmount();
            // if (journal_id == '') {
            //     if (json.is_decimal) {
            //         $('#id_document_amount').val('0.00');
            //         $('#id_tax_amount').val('0.00');
            //         $('#id_tax_report_amount').val('0.00');
            //         $('#id_total_amount').val('0.00');
            //         $('#id_amount').val('0.00');
            //     } else {
            //         $('#id_document_amount').val('0');
            //         $('#id_tax_amount').val('0');
            //         $('#id_tax_report_amount').val('0.00');
            //         $('#id_total_amount').val('0');
            //         $('#id_amount').val('0');
            //     }
            //     $('#transaction-table').DataTable().clear().draw();
            //     current_line = 0;
            //     setTimeout(() => {
            //         $('#btnSaveAPEntry').prop('disabled', true);
            //     }, 300);
            // }
            $('#id_supplier_name').val(json.supplier_name);
            $('#id_currency').data("is_decimal", json.is_decimal);
            $('#id_currency').val(json.supplier_currency_id).trigger('change');
            set_tax_reporting_rate();
            $("#id_exchange_rate_fk").val(json.exchange_id);
            $("#id_exchange_rate").val(parseFloat(json.exchange_rate).toFixed(9));
            $('#doc_date_view').trigger('change');
            var due_date = moment($('#doc_date_view').val(), "DD-MM-YYYY").add(parseInt(json.term_days), 'days').format("DD-MM-YYYY");
            $('#id_due_date').datepicker('setDate', due_date);
            $('#id_supplier').attr('term_days', json.term_days);
            // $('#id_account_set').val(json.account_set_id).trigger('change');
            $('#tax_value').val(json.tax_id);
            $('#dis_code_id').val(json.distribution_id);
            $('#id_account_set').prop('disabled', false);
            $('#id_payment_code').prop('disabled', false);
            $('#id_is_manual_doc').prop('disabled', false);
            $('#btnAddTransDialog').removeAttr('disabled');
            $('#btnSearchExchangeRate').prop('disabled', false);
            $('#btnSearchTaxExchangeRate').prop('disabled', false);
            $('#btnSearchAccount').prop('disabled', false);
            $('#btnSearchDocument').prop('disabled', false);
            $('#id_inv').prop('disabled', false);
            $('button[type="submit"]').prop('disabled', false);
            // var def_tax_id = 0
            // var def_dist_id = 0
            // if (json.tax_id > 0){
            //     def_tax_id = json.tax_id
            // }
            // $('#id_tax').val(parseInt(def_tax_id)).trigger('change');
            // if (json.distribution_id > 0){
            //     def_dist_id = json.distribution_id
            // }
            //$('#id_distribution_code').val(parseInt(def_dist_id)).trigger('change');

            if (json.supplier_currency_id){
                $.ajax({
                    method: "POST",
                    url: '/accounting/load_account_set/2/',
                    dataType: 'JSON',
                    data: {
                        'currency_id': json.supplier_currency_id,
                    },
                    success: function (jsn) {
                        if (jsn) {
                            $('#id_account_set').select2().empty();
                            $('#id_account_set').select2({data: jsn});
                            setTimeout(() => {
                                $('#id_account_set').val(json.account_set_id).trigger('change');
                            }, 200);
                        }
                    }
                });
            }
            // if (!json.account_payable_id) {
            //     pop_ok_dialog("Warning!",
            //     "This Vendor does not have default Payable Account selected",
            //     function () {  })
            // }
            if (!json.account_set_id) {
                pop_ok_dialog("Warning!",
                "This Vendor does not have default Account Set selected",
                function () { 
                    setTimeout(() => {
                        $('#id_account_set').select2('open');
                    }, 400);
                 });
            } else {
                setTimeout(() => {
                    $('#id_exchange_rate').select();
                }, 500);
            }
        }
    });
});

$('#id_document_amount').on("change", function () {
    var document_amount = float_format($('#id_document_amount').val());
    if(isNaN(document_amount) || !document_amount) {
        document_amount = 0;
    }

    if ($('#id_currency').data("is_decimal") == false) {
        $('#id_document_amount').val(comma_format(document_amount, 0));
    } else {
        $('#id_document_amount').val(comma_format(document_amount));
    }

    var total_amount = float_format($('#id_total_amount').val());
    if(document_amount != total_amount) {
        setTimeout(function(){
            $('#btnSaveAPEntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAPEntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAPEntry').prop('disabled', false);
        }
    }
    $('#undistributed_amount').val(comma_format(document_amount - total_amount));
});

// Add transaction list data when submit form
function getTransactionTableData() {
    array = [];
    array.length = 0;
    var table = $('#transaction-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        rowData = this.data();
        transaction_list = {};
        transaction_list.id = rowData[$("#trs-id").index()].toString();
        transaction_list.distribution_id = rowData[$("#trs-distribution_id").index()] != null ? rowData[$("#trs-distribution_id").index()].toString() : '';
        transaction_list.distribution_code = rowData[$("#trs-distribution_code").index()] != null ? rowData[$("#trs-distribution_code").index()].toString() : '';
        transaction_list.distribution_name = rowData[$("#trs-distribution_name").index()] != null ? rowData[$("#trs-distribution_name").index()].toString() : '';
        transaction_list.account_id = rowData[$("#trs-account_id").index()].toString();
        transaction_list.account_code = rowData[$("#trs-account_code").index()].toString();
        transaction_list.account_name = filter_special_char(rowData[$("#trs-account_name").index()].toString());
        transaction_list.description = filter_special_char(rowData[$("#trs-description").index()].toString());
        transaction_list.amount = rowData[$("#trs-amount").index()].toString();
        transaction_list.tax_amount = rowData[$("#trs-tax_amount").index()].toString();
        transaction_list.base_tax_amount = rowData[$("#trs-base_tax_amount").index()].toString();
        transaction_list.total_amount = rowData[$("#trs-total_amount").index()].toString();
        transaction_list.tax_id = rowData[$("#trs-tax_id").index()].toString();
        transaction_list.is_tax_include = rowData[$("#trs-tax_include").index()] != null ? rowData[$("#trs-tax_include").index()].toString() : '0';
        transaction_list.is_tax_transaction = rowData[$("#trs-tax_transaction").index()] != null ? rowData[$("#trs-tax_transaction").index()].toString() : '0';
        transaction_list.is_manual_tax_input = rowData[$("#trs-manual_tax_input").index()] != null ? rowData[$("#trs-manual_tax_input").index()].toString() : '0';
        transaction_list.delete = rowData[$("#trs-delete").index()].toString();
        array.push(transaction_list);
    });

    $('#transaction_list_data').val(JSON.stringify(array));
    if ($('#start_date').attr('id') !== undefined) {
        var s_date = $('#start_date').val().split('-');
        if (s_date[0].length == 2)
            $('#start_date').val(moment($('#start_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        if ($('#expire_date').val()) {
            var e_date = $('#expire_date').val().split("-");
            if (e_date[0].length == 2)
                $('#expire_date').val(moment($('#expire_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        }
    }
    try {
        $('#id_exchange_rate').val(float_format($('#id_exchange_rate').val()).toFixed(10));
        $('#id_tax_exchange_rate').val(float_format($('#id_tax_exchange_rate').val()).toFixed(10));
    } catch (e) {
        console.log(e);
    }
    setTimeout(function(){
        $('#btnSaveAPEntry').prop('disabled', true);
    }, 100);
}

$(document).on('change keypress', 'input', function() {
    $('#btnSaveAPEntry').prop('disabled', false);
    var document_amount = float_format($('#id_document_amount').val());
    var total_amount = float_format($('#id_total_amount').val());
    if(document_amount != total_amount) {
        setTimeout(function(){
            $('#btnSaveAPEntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAPEntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAPEntry').prop('disabled', false);
        }
    }
});

$(document).on('change', 'select', function() {
    $('#btnSaveAPEntry').prop('disabled', false);
    var document_amount = float_format($('#id_document_amount').val());
    var total_amount = float_format($('#id_total_amount').val());
    if(document_amount != total_amount) {
        setTimeout(function(){
            $('#btnSaveAPEntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAPEntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAPEntry').prop('disabled', false);
        }
    }
});

// function to re-calculate tax amoount and total amount for transaction table
function recalculateTaxAmount(rate) {
    var table = $('#transaction-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        rowData = this.data();
        amount = float_format(rowData[$("#trs-amount").index()]);
        tax_mount = float_format(amount * rate);
        total_amount = amount + tax_mount;
        table.cell(rowIdx, $("#trs-tax_amount").index()).data(comma_format(tax_mount));
        table.cell(rowIdx, $("#trs-total_amount").index()).data(comma_format(total_amount));
    });
    table.draw();
}

// function to re-calculate tax amoount and total amount for transaction table
function recalculateUndistributedAmount() {
    var document_amount = $('#id_document_amount').val();
    var total_dmount = $('#id_total_amount').val();

    int_doc_amount = document_amount.replace(/,/g , '');
    int_tot_amount = total_dmount.replace(/,/g , '');
    undistributed_amount = int_doc_amount - int_tot_amount;
    var new_undistib = 0;
    if ($('#id_currency').data("is_decimal") == false) {
        new_undistib = undistributed_amount.toFixed(0);
    } else {
        new_undistib = undistributed_amount.toFixed(2);
    }

    if(new_undistib != 0){
        var ps5 = new_undistib.toString().split(".");
        var new_undistib = ps5[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        $('#undistributed_amount').val(new_undistib+'.'+ps5[1]);
    }else{
        $('#undistributed_amount').val(new_undistib);
    }

}

$('#id_is_manual_doc').on('change', function() {
    isManualDoc = $('#id_is_manual_doc:checkbox:checked').length;

    if(isManualDoc > 0) {
        $('#id_document_number').val('');
        $('#id_document_amount').val('0.00');
        //$('#id_document_number').prop('readonly', false);
        $('#id_document_amount').prop('readonly', false);
        $('.readonly').off('keydown paste');
        $('#id_document_number').removeClass('disabled readonly');

        $('#btnSearchDocument').addClass('hidden');
        recalculateUndistributedAmount();
    }
    else {
        $('#id_document_number').val('');
        $('#id_document_amount').val('0.00');
        //$('#id_document_number').prop('readonly', true);
        $('#id_document_amount').prop('readonly', true);
        $('#id_document_number').addClass('disabled readonly');
        $('.readonly').on('keydown paste', function(e) {
                e.preventDefault();
        });
        $('#btnSearchDocument').removeClass('hidden');
        recalculateUndistributedAmount();
    }
});

$('#id_document_date').on('change', function() {
    $('#id_posting_date').val($('#id_document_date').val());
    set_tax_reporting_rate();
});
