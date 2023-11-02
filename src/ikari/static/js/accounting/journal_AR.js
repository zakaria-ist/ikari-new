
$(document).ready(function () {
    recalculateUndistributedAmount();
    isManualDoc = $('#id_is_manual_doc:checkbox:checked').length;
    if(isManualDoc > 0) {
        //$('#id_document_number').prop('readonly', false);
        $('#id_document_amount').prop('readonly', false);
        $('.readonly').off('keydown paste');
        $('#id_document_number').removeClass('disabled readonly');

        $('#btnSearchDocument').addClass('hidden');
        recalculateUndistributedAmount();
    }
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
    var id_customer = $("#id_customer").val();
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
                    "journal_type" :'1' /* TRANSACTION_TYPES)['AR Invoice'] */
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

$('#customer-table').on( 'draw.dt', function () {
    selectTableRow('#customer-table', 10);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Customer button*/
$('#btnSearchCustomer').on('click', function () {
    $("#customer_error").text(""); // Delete error message
    $('#customer-table').DataTable().destroy();
    $('#customer-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": "/accounting/customer_list/"
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "payment_term", "sClass": "text-left"},
            {"data": "payment_mode", "sClass": "text-left hide_column"},
            {"data": "credit_limit", "sClass": "text-left hide_column"},
            {"data": "id", "sClass": "text-left hide_column"},
            {"data": "tax_id", "sClass": "text-left hide_column"},
            {"data": "currency_id", "sClass": "text-left hide_column"},
            {"data": "currency_code", "sClass": "text-left"},
            {"data": "account_set_id", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="customer-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });

    setTimeout(() => {
        $('#customer-table').DataTable().columns.adjust();
    }, 300);
});

function changeCustomer() {
    var row = $("input[name='customer-choices']:checked").val();
    if (row) {
        var table = $('#customer-table').DataTable();

        // $('#id_customer_name').val('');
        //     $('#id_document_number').val('');
        //     $('#id_document_amount').val('0.000000')
        //     recalculateUndistributedAmount();
        //     $('#id_customer_name').val(json.customer_name);
        //     $('#id_currency').val(json.customer_currency_id);
        //     $('#id_account_set').prop('disabled', false);
        //     $('#id_account_set').val(json.account_set_id).trigger('change');
        //     $('#tax_value').val(json.tax_id);
        //     $('#id_payment_code').prop('disabled', false);
        //     $('#id_is_manual_doc').prop('disabled', false);
        //     $('#btnAddTransDialog').removeAttr('disabled');
        //     $('#btnSearchAccount').prop('disabled', false);
        //     $('#btnSearchDocument').prop('disabled', false);
        //     $('button[type="submit"]').prop('disabled', false);
        // Customer
        
        // Account Set
        

        // Customer
        var customer_id = table.cell(row, $("#cus-id").index()).data();
        $("#id_customer").val(customer_id).trigger('change');
        //$("#id_customer_code").val(id_customer_code);
        //$("#id_customer_name").val(id_customer_name);

        
        
        
        $("#myCustomerListModal").modal("hide");
    }
    else {
        $("#customer_error").text("Please choose 1 customer");
    }
}
/* End Search Customer button*/


$('#account-table').on( 'draw.dt', function () {
    selectTableRow('#account-table', 6);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Account button*/
$('#btnSearchAccount').on('click', function () {
    $("#account_error").text(""); // Delete error message
    $('#account-table').DataTable().destroy();
    $('#account-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/account_set_list/1/", /* ACCOUNT_SET_TYPE_DICT['AR Account Set'] */
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
        $('#select2-id_account_set-container').text(id_account_code);

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
        $("#account_error").text("Please choose 1 rate");
    }
}

$('#id_currency').on('change', function() {
    currency = $('#id_currency').val();

    if(currency && currency != company_currency) {
        if ('True' != is_rec_entry){
            $('#btnSearchExchangeRate').prop('disabled', false);
            $('#btnSearchTaxExchangeRate').prop('disabled', false);
        }
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
    var id_customer = $("#id_customer").val();
    if (id_customer) {
        $("#modalSearchDocument").modal("show");

        $('#document-table').DataTable().destroy();
        $('#document-table').dataTable({
            "iDisplayLength": 5,
            "iDisplayStart": 0,
            "bLengthChange": false,
            "order": [[0, "desc"]],
            "serverSide": true,
            "stateSave": false,
            "ajax": {
                "url": "/accounting/customer_document_list/",
                "data": {
                    "customer_id": id_customer
                }
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "date", "sClass": "text-left"},
                {"data": "reference", "sClass": "text-left"},
                {"data": "amount", "sClass": "text-left"},
                {"data": "customer_name", "sClass": "text-left"},
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
    }
    else {
        alert("Please choose customer");
    }
});

$('#exchange-table').on( 'draw.dt', function () {
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
        $("#id_document_number").val(id_document_number);
        $("#id_document_amount").val(comma_format(id_document_amount));
        recalculateUndistributedAmount();

        $("#modalSearchDocument").modal("hide");
    }
    else {
        $("#document_error").text("Please choose 1 document");
    }
}
/* End Search Document button*/



$('#id_document_number').on('change', function () {
    var value = $(this).val();
    var cust = $('#id_customer').val();
    if (!cust) {
        cust = '0'
    }
    $.ajax({
        method: "POST",
        url: '/accounting/check_if_duplicate/AR_Invoice/document_number/',
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

function set_tax_reporting_rate() {
    var currency_id = $('#id_currency').val();
    var doc_date = $('#id_document_date').val();
    if(currency_id && doc_date) {
        get_tax_reporting_rate(currency_id, doc_date);
    }
}

$('#id_customer').on('change', function () {
    transaction_new.length = 0;
    transaction_update.length = 0;
    var customer_id = parseInt($(this).val());
    $.ajax({
        method: "POST",
        url: url_load_customer,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'customer_id': customer_id
        },
        success: function (json) {
            $('#id_customer_name').val('');
            $('#id_customer_code').val('');
            
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
            //         $('#btnSaveAREntry').prop('disabled', true);
            //     }, 300);
            // }
            $('#id_customer_name').val(json.customer_name);
            $('#id_currency').data("is_decimal", json.is_decimal);
            $('#id_currency').val(json.customer_currency_id).trigger('change');
            set_tax_reporting_rate();
            $("#id_exchange_rate_fk").val(json.exchange_id);
            $("#id_exchange_rate").val(parseFloat(json.exchange_rate).toFixed(9));
            $('#doc_date_view').trigger('change');
            var due_date = moment($('#doc_date_view').val(), "DD-MM-YYYY").add(parseInt(json.payment_term), 'days').format("DD-MM-YYYY");
            $('#id_due_date').datepicker('setDate', due_date);
            $('#id_customer').attr('payment_term', json.payment_term);
            $('#id_account_set').prop('disabled', false);
            // $('#id_account_set').val(json.account_set_id).trigger('change');
            $('#tax_value').val(json.tax_id);
            $('#id_payment_code').prop('disabled', false);
            $('#id_is_manual_doc').prop('disabled', false);
            $('#btnSearchExchangeRate').prop('disabled', false);
            $('#btnSearchTaxExchangeRate').prop('disabled', false);
            $('#btnAddTransDialog').removeAttr('disabled');
            $('#btnSearchAccount').prop('disabled', false);
            $('#btnSearchDocument').prop('disabled', false);
            $('#id_inv').prop('disabled', false);
            $('button[type="submit"]').prop('disabled', false);
            // var def_tax_id = 0;
            // if (json.tax_id > 0){
            //     def_tax_id = json.tax_id;
            // }
            // $('#id_tax').val(parseInt(def_tax_id)).trigger('change');

            // var id_account_set = $('#id_account_set').val();
            if (json.customer_currency_id){
                $.ajax({
                    method: "POST",
                    url: '/accounting/load_account_set/1/',
                    dataType: 'JSON',
                    data: {
                        'currency_id': json.customer_currency_id,
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
            //     "This Customer does not have default Receivable Account selected",
            //     function () {  })
            // }
            if (!json.account_set_id) {
                pop_ok_dialog("Warning!",
                "This Customer does not have default Account Set selected",
                function () { 
                    setTimeout(() => {
                        $('#id_account_set').select2('open');
                    }, 400);
                 })
            } else {
                setTimeout(() => {
                    $('#id_exchange_rate').select();
                }, 500);
            }
        }
    });
});

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

$('#id_document_amount').on('change', function() {
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
            $('#btnSaveAREntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAREntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAREntry').prop('disabled', false);
        }
    }
    $('#undistributed_amount').val(comma_format(document_amount - total_amount));
});

// Add transaction list data when submit form
function getTransactionTableData(is_posted) {
    var applied = $("#id_related_invoice").val();
    if(is_posted) {
        undistributed_amount = float_format($('#undistributed_amount').val());
        if(undistributed_amount != 0) {
            $('#journal_error').text('The distributed amount does not equal the document amount.');
        }
        else {
            $('#journal_error').text('');
            array = [];
            array.length = 0;
            $('#transaction_list_data').val(JSON.stringify(array));
            var table = $('#transaction-table').DataTable();
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                rowData = this.data();
                transaction_list = {};
                transaction_list.id = rowData[$("#trs-id").index()];
                transaction_list.distribution_id = rowData[$("#trs-distribution_id").index()] || '';
                transaction_list.distribution_code = rowData[$("#trs-distribution_code").index()] || '';
                transaction_list.distribution_name = rowData[$("#trs-distribution_name").index()] || '';
                transaction_list.account_id = rowData[$("#trs-account_id").index()];
                transaction_list.account_code = rowData[$("#trs-account_code").index()];
                transaction_list.account_name = filter_special_char(rowData[$("#trs-account_name").index()]);
                transaction_list.description = filter_special_char(rowData[$("#trs-description").index()]);
                transaction_list.amount = rowData[$("#trs-amount").index()];
                transaction_list.tax_amount = rowData[$("#trs-tax_amount").index()];
                transaction_list.total_amount = rowData[$("#trs-total_amount").index()];
                transaction_list.delete = rowData[$("#trs-delete").index()];
                transaction_list.is_tax_included = rowData[$("#trs-tax_included").index()];
                transaction_list.is_tax_transaction = rowData[$("#trs-tax_transaction").index()];
                transaction_list.tax_id = rowData[$("#trs-tax_id").index()];
                transaction_list.base_tax_amount = rowData[$("#trs-base_tax_amount").index()];
                transaction_list.is_manual_tax_input = rowData[$("#trs-manual_tax_input").index()];
                transaction_list.related_invoice = applied;
                array.push(transaction_list);
            });

            $('#transaction_list_data').val(JSON.stringify(array));
        }
    } else {
        array = [];
        array.length = 0;
        $('#transaction_list_data').val(JSON.stringify(array));
        var trx_table = $('#transaction-table').DataTable();
        trx_table.rows().every(function (rowIdx, tableLoop, rowLoop) {
            rowData = this.data();
            transaction_list = {};
            transaction_list.id = rowData[$("#trs-id").index()];
            transaction_list.distribution_id = rowData[$("#trs-distribution_id").index()] || '';
            transaction_list.distribution_code = rowData[$("#trs-distribution_code").index()] || '';
            transaction_list.distribution_name = rowData[$("#trs-distribution_name").index()] || '';
            transaction_list.account_id = rowData[$("#trs-account_id").index()];
            transaction_list.account_code = rowData[$("#trs-account_code").index()];
            transaction_list.account_name = filter_special_char(rowData[$("#trs-account_name").index()]);
            transaction_list.description = filter_special_char(rowData[$("#trs-description").index()]);
            transaction_list.amount = rowData[$("#trs-amount").index()];
            transaction_list.tax_amount = rowData[$("#trs-tax_amount").index()];
            transaction_list.total_amount = rowData[$("#trs-total_amount").index()];
            transaction_list.delete = rowData[$("#trs-delete").index()];
            transaction_list.is_tax_included = rowData[$("#trs-tax_included").index()];
            transaction_list.is_tax_transaction = rowData[$("#trs-tax_transaction").index()];
            transaction_list.tax_id = rowData[$("#trs-tax_id").index()];
            transaction_list.base_tax_amount = rowData[$("#trs-base_tax_amount").index()];
            transaction_list.is_manual_tax_input = rowData[$("#trs-manual_tax_input").index()];
            transaction_list.related_invoice = applied;
            array.push(transaction_list);
        });
        $('#transaction_list_data').val(JSON.stringify(array));
    }
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
        $('#btnSaveAREntry').prop('disabled', true);
    }, 100);
}

$(document).on('change keypress', 'input', function() {
    $('#btnSaveAREntry').prop('disabled', false);
    var document_amount = float_format($('#id_document_amount').val());
    var total_amount = float_format($('#id_total_amount').val());
    if(document_amount != total_amount) {
        setTimeout(function(){
            $('#btnSaveAREntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAREntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAREntry').prop('disabled', false);
        }
    }
});

$(document).on('change', 'select', function() {
    $('#btnSaveAREntry').prop('disabled', false);
    var document_amount = float_format($('#id_document_amount').val());
    var total_amount = float_format($('#id_total_amount').val());
    if(document_amount != total_amount) {
        setTimeout(function(){
            $('#btnSaveAREntry').prop('disabled', true);
        }, 200);
    } else {
        if (float_format(document_amount) < 0) {
            setTimeout(() => {
                $('#btnSaveAREntry').prop('disabled', true);
            }, 200);
        } else {
            $('#btnSaveAREntry').prop('disabled', false);
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

// function to re-calculate undistributed amount = document amount - total amount in grid
function recalculateUndistributedAmount() {
    document_amount = $('#id_document_amount').val();
    total_dmount = $('#id_total_amount').val();
    int_doc_amount = document_amount.replace(/,/g , '');
    int_tot_amount = total_dmount.replace(/,/g , '');
    undistributed_amount = int_doc_amount - int_tot_amount;
    if ($('#id_currency').data("is_decimal") == false) {
        $('#undistributed_amount').val(comma_format(undistributed_amount, 0));
    } else {
        $('#undistributed_amount').val(comma_format(undistributed_amount));
    }
    // new_undistib = undistributed_amount.toFixed(2)
    // if(new_undistib != 0 ){
    //     var ps5 = new_undistib.toString().split(".");
    //     var new_undistib = ps5[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    //     $('#undistributed_amount').val(new_undistib+'.'+ps5[1]);
    // }else{
    //     $('#undistributed_amount').val(new_undistib);
    // }

    // $('#undistributed_amount').val(undistributed_amount.toFixed(6));
}

$('#doc_date_view').keyup(function(event){
    adjust_input_date(this);
});

$('#post_date_view').keyup(function(event){
    adjust_input_date(this);
});

$('#batch_view_date').keyup(function(event){
    adjust_input_date(this);
});

function FillYearPeriodOptLst(){
    var year_part = 0;
    var month_part = 0;

    var yr_prd = $('#perd_year').val();
    if ((yr_prd) && (parseInt(yr_prd) > 0)) {
        year_part = yr_prd;
    } else {
        yr_prd = new Date($('#doc_date_view').val().split("-").reverse().join("-"));
        year_part = yr_prd.getFullYear();
        month_part = yr_prd.getMonth() + 1;
    }
    var list_period = [];
    for (i = 1; i <= 15; i++) {
        var prd = {};
        prd.year = year_part;
        prd.period = i;
        list_period.push(prd);
    }
    $.each(list_period, function (key, value) {
        var period_part = value.period > 9 ? value.period : '0' + value.period;
        period_part = value.period == 14 ? 'ADJ' : period_part;
        period_part = value.period == 15 ? 'CLS' : period_part;
        var year_period_text = value.year + '-' + period_part;
        if (value.period != 13) {
            $('#year_period')
                .append($("<option></option>")
                    .attr("value", value.period)
                    .text(year_period_text));
        }
    });
    if ((saved_prd) && (parseInt(saved_prd) > 0)) {
        $('#year_period').val(saved_prd).trigger('change');
    } else {
        $('#year_period').val(month_part).trigger('change');
    }
    $('#year_period').select2();
}

function ResetYearPeriodOptLst() {
    $('#year_period').empty().append('<option value="0">kosong</option>');
    FillYearPeriodOptLst();
    $("#year_period option[value='0']").remove();
}