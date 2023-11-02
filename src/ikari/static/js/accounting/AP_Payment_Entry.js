var PAYMENT_TRANSACTION_TYPES_PAYMENT = 1;
var PAYMENT_TRANSACTION_TYPES_MISC_PAYMENT = 2;
var is_currency_differene = false;
var supp_bank_exch_rate = 1;
var company_currency = 'FUNC. CURR.';
var bank_exchange_date = '';
var vendor_exchange_date = '';

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
        scrollX: true,
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": url_load_bank_list,
        },
        "columns": [
            {"data": "code", "sClass": "text-left", },
            {"data": "name", "sClass": "text-left", },
            {"data": "currency_id", "sClass": "text-left", "visible": false, },
            {"data": "currency", "sClass": "text-left", },
            {"data": "account", "sClass": "text-left", },
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

    // th not tabbable
    
});

$('#btnSelectBank').on('click', function () {
    var selected_row = [];
    var dtTable = $('#bank-table').DataTable();
    $("input[name='choices']:checked").each(function () {
        selected_row.push(this.value);
        var dtRow = dtTable.row($(this).parents('tr')[0]).data();
        selected_row.push(dtRow['currency_id']);
    });
    $('#id_bank option').removeAttr('selected');
    $('#id_bank option[value="' + selected_row[0] + '"]').prop('selected', true);
    $('#select2-id_bank-container').text($('#id_bank option:selected').text());
    $('#id_currency option').removeAttr('selected');
    $('#id_currency option[value="' + selected_row[1] + '"]').prop('selected', true);
});

function set_tax_reporting_rate() {
    var currency_id = $('#id_currency').val();
    var doc_date = $('#id_document_date').val();
    if(currency_id && doc_date) {
        get_tax_reporting_rate(currency_id, doc_date);
    }
}

$('#id_bank').on('change', function () {
    var bank_id = parseInt($(this).val());
    if(bank_id) {
        $('#id_serial_no').attr('disabled', false);
    }
    $.ajax({
        method: "POST",
        url: url_load_currency,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'bank_id': bank_id
        },
        success: function (json) {
            $('#id_currency option').removeAttr('selected');
            if (json['currency_id'] != null) {
                $('#id_currency option[value="' + json['currency_id'] + '"]').prop('selected', true);
                $('#id_currency_text').val(json['currency_code']);
                $('.payment_currency').val(json['currency_code']);

                if (serial_no != '') {
                    var day = $('#doc_date_view').val();
                    var pecahin = day.split('-');
                    var bulan = pecahin[1];
                    var tahun = pecahin[2].substring(2, 4);
                    var supplier_currency = json['currency_code']
                    var serial = serial_no;
                    bank = $("#id_bank option:selected").text().substring(0, 3);
                    $('#id_reference').val(bank+'-R'+serial+'-'+bulan+'/'+tahun+''+supplier_currency);
                }
            } else {
                $('#id_currency option:empty').prop('selected', true);
            }
            if (!jrn_id) {
                var date_rate = $("#id_document_date").val();
                var bank_currency = $("#id_currency option:selected").val();
                if (bank_currency) {
                    $.ajax({
                        type: "GET",
                        url :'/currencies/get_exchange_by_date/1/'+bank_currency+'/'+date_rate+'/3/',
                        dataType: 'JSON',
                        success: function(data){
                            if (parseFloat(data[0].rate) == 0) {
                                pop_ok_dialog("Invalid Exchange Rate",
                                    "Exchange Rate not found for current period for " + data[0].from_code + " to " + data[0].to_code +".",
                                    function () { }
                                );
                            } else {
                                company_currency = data[0].company_currency;
                                $('#id_exchange_rate_fk').val(data[0].id);
                                $('#id_exchange_rate').val(data[0].rate).trigger('change');
                                $('#id_payment_currency_id').val(parseInt(bank_currency));
                                bank_is_decimal = data[0].is_decimal;
                                bank_exchange_date = data[0].exchange_date;
                                update_final_exch_rate();
                            }
                        }
                    });
                }
                set_tax_reporting_rate();
            }
        }
    });
    if(bank_is_decimal) {
        $("#id_batch_amount").val(comma_format(float_format($("#id_batch_amount").val())));
    } else {
        $("#id_batch_amount").val(comma_format(float_format($("#id_batch_amount").val()), 0));
    }
});

$('#id_exchange_rate').on('change', function(){
    setTimeout(() => {
        var exch_date = bank_exchange_date;
        var year_perd = $('#doc_date_view').val();
        if (exch_date && year_perd) {
            if (exch_date.split('-')[1] != year_perd.split('-')[1]) {
                pop_ok_dialog("Warning",
                    "Bank Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { });
            } else if (exch_date.split('-')[0] != year_perd.split('-')[2]) {
                pop_ok_dialog("Warning",
                    "Bank Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { });
            }
        }
    }, 300);
});

$('#id_orig_exch_rate').on('change', function(){
    setTimeout(() => {
        var exch_date = vendor_exchange_date;
        var year_perd = $('#doc_date_view').val();
        if (exch_date && year_perd) {
            if (exch_date.split('-')[1] != year_perd.split('-')[1]) {
                pop_ok_dialog("Warning",
                    "Vendor Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { });
            } else if (exch_date.split('-')[0] != year_perd.split('-')[2]) {
                pop_ok_dialog("Warning",
                    "Vendor Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { });
            }
        }
    }, 300);
});


$('#id_payment_code').on('change', function () {
    payment_code_id = parseInt($('#id_payment_code').val());
    if (payment_code_id) {
        $.ajax({
            method: "POST",
            url: '/accounting/load_payment_type/',
            dataType: 'JSON',
            data: {
                'payment_code_id': payment_code_id,
            },
            success: function (json) {
                if (json.payment_type == '2') {

                    $('#id_payment_check_number').removeClass('hidden');
                    $('#id_payment_check_number_label').removeClass('hidden');
                }
                else {
                    $('#id_payment_check_number').val('');
                    $('#id_payment_check_number').addClass('hidden');
                    $('#id_payment_check_number_label').addClass('hidden');
                }
            }
        });
    }
    //$('#id_document_number').focus();

});

$('#id_transaction_type').on('change', function () {
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == PAYMENT_TRANSACTION_TYPES_PAYMENT) {
        $("#id_supplier").prop('disabled', false);
        $('#id_payment_code').val('').trigger('change');
        $('#id_payment_code').select2({
            placeholder: "Select Payment Code",
        });

        $('#id_supplier_group').removeClass('hidden');
        $('#id_account_set_group').removeClass('hidden');

        $("#id_supplier").prop('required', true);
        $("#id_account_set").prop('required', true);

        $('#py-transaction-table').DataTable().clear().draw();
        $('#transaction_div').removeClass('hidden');

        $('#misc-transaction-table').DataTable().clear().draw();
        $('#misc_transaction_div').addClass('hidden');


        $('#id_payment_check_number').addClass('hidden');
        $('#id_payment_check_number_label').addClass('hidden');
        $('#tax_reporting_rate_div').addClass('hidden');

        if (!$('#id_supplier').val()) {
            $('#id_account_set').prop('disabled', true);
            $('#id_payment_code').prop('disabled', true);
            $('#btnAddPaymentTransDialog').attr('disabled', 'disabled');
            $('button[type="submit"]').prop('disabled', true);
            $('#btnSearchAccountSet').prop('disabled', true);
            $('#btnSearchPaymentCode').prop('disabled', true);
        }

        $('#id_tax').select2({
            placeholder: "Select Tax",
            width: '100%',
            allowClear: true,
        });
        $("#id_invoice_number").val("");
        $("#id_invoice_number").text('');
        $("#id_tax").prop('disabled', true);
        $("#id_tax_group").addClass('hidden');

        $('#id_account_set').select2({
            placeholder: "Select Account Set",
            width: '100%',
            allowClear: true
        });

        $('#subtotal-div').addClass('hidden');
        $('#subtotal-span').removeClass('hidden');
        $('#payment_div').removeClass('hidden');
        $('#id_total_amount').val(float_format(0.00).toFixed(2));
        $('#id_payment_amount').val(float_format(0.00).toFixed(2));
        $('#id_original_amount').val(float_format(0.00).toFixed(2));

    } else if (transaction_type == PAYMENT_TRANSACTION_TYPES_MISC_PAYMENT) {

        $('#id_supplier_name').val('');
        $('#id_supplier').val('').trigger('change');
        // $("#id_supplier").prop('disabled', true);
        $('#id_supplier_currency').val('');
        $('#id_payment_code').val('');
        $('#id_account_set').val('');
        $("#id_invoice_number").val('');


        $('#id_payment_code').select2({
            placeholder: "Select Payment Code",
        });

        $('#id_supplier').select2({
            placeholder: "Select Vendor",
            allowClear: true
        });

        $('#id_account_set').select2({
            placeholder: "Select Account Set",
            width: '100%'
        });

        $("#id_supplier").prop('required', false);
        $("#id_account_set").prop('required', false);

        // $('#id_supplier_group').addClass('hidden');
        // $('#id_account_set_group').addClass('hidden');
        $('#id_payment_code').prop('disabled', false);
        $('#btnSearchPaymentCode').prop('disabled', false);

        $('#id_payment_check_number').addClass('hidden');
        $('#id_payment_check_number_label').addClass('hidden');

        $('#py-transaction-table').DataTable().clear().draw();
        $('#transaction_div').addClass('hidden');

        $('#misc-transaction-table').DataTable().clear().draw();
        $('#misc_transaction_div').removeClass('hidden');

        $("#id_tax").prop('disabled', false);


        $("#id_tax_group").removeClass('hidden');

        $('#subtotal-div').removeClass('hidden');
        $('#subtotal-span').addClass('hidden');
        $('#payment_div').addClass('hidden');

        $('#id_total_amount').val(float_format(0.00).toFixed(2));
        current_line = 0;
        $('#tax_reporting_rate_div').removeClass('hidden');

        calculate_value = recalculatePaymentAmount();
        if(bank_is_decimal) {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        } else {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
        }
    }
});

$('#supplier-table').on( 'draw.dt', function () {
    selectTableRow('#supplier-table', 9);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});


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
            "url": "/accounting/supplier_list/",
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

        $("#id_supplier").val(supplier_id).trigger('change');

        $("#SupplierListModal").modal("hide");
    }
    else {
        $("#supplier_error").text("Please choose 1 supplier");
    }
}

$('#id_supplier').on('change', function () {
    transaction_new.length = 0;
    transaction_update.length = 0;
    if ($(this).val()) {
        var supplier_id = parseInt($('#id_supplier').val());
        $.ajax({
            method: "POST",
            url: '/accounting/load_supplier/',
            dataType: 'JSON',
            data: {
                'supplier_id': supplier_id,
            },
            success: function (json) {
                $('#id_supplier_name').val('');
                $('#id_supplier_name').val(json.supplier_name);
                $('#id_supplier_currency').val(json.supplier_currency);
                var curr = $("#id_supplier_currency option[value=" + json.supplier_currency + "]").text();
                $('.supp_currency').val(curr);

                $('#id_account_set').prop('disabled', false);
                $('#id_account_set').val(json.account_set_id).trigger('change');

                $('#id_payment_code').prop('disabled', false);
                $('#id_payment_code').find('option:selected').removeAttr('selected');

                if (json['payment_code_id'] != null) {
                    $('#id_payment_code').val(json['payment_code_id']).trigger('change');
                } else {
                    $('#id_payment_code option:empty').prop('selected', true);
                    $('#select2-id_payment_code-container').find('span').text('Select Payment Code');
                }
                // $('#id_payment_code').trigger('change');
                setTimeout(() => {
                    $('#id_payment_code').focus();
                }, 500);
                

                $('#btnAddPaymentTransDialog').removeAttr('disabled');
                $('#btnSearchAccountSet').prop('disabled', false);
                $('#btnSearchPaymentCode').prop('disabled', false);
                $('button[type="submit"]').prop('disabled', false);
                $('#py-transaction-table').DataTable().clear().draw();
                $('#id_total_amount').val(float_format(0.00).toFixed(2));
                $('#id_payment_amount').val(float_format(0.00).toFixed(2));
                $('#id_original_amount').val(float_format(0.00).toFixed(2));
                current_line = 0;
                set_tax_reporting_rate();

                var id_account_set = $('#id_account_set').val();
                if (!id_account_set){
                    $.ajax({
                        method: "POST",
                        url: '/accounting/load_account_set/2/',
                        dataType: 'JSON',
                        data: {
                            'currency_id': json.supplier_currency,
                        },
                        success: function (json) {
                            if (json) {
                                $('#id_account_set').select2().empty();
                                $('#id_account_set').select2({data: json});
                            }
                        }
                    });
                }

                var date_rate = $("#id_document_date").val();
                var supplier_currency = $("#id_supplier_currency").val();
                if (supplier_currency) {
                    $.ajax({
                        type: "GET",
                        url :'/currencies/get_exchange_by_date/1/'+supplier_currency+'/'+date_rate+'/3/',
                        dataType: 'JSON',
                        success: function(data){
                            if (parseFloat(data[0].rate) == 0) {
                                pop_ok_dialog("Invalid Exchange Rate",
                                    "Exchange Rate not found for current period for " + data[0].from_code + " to " + data[0].to_code +".",
                                    function () { }
                                );
                            } else {
                                company_currency = data[0].company_currency;
                                $('#id_orig_exch_rate').val(data[0].rate).trigger('change');
                                $('#id_original_currency_id').val(parseInt(supplier_currency));
                                vendor_is_decimal = data[0].is_decimal;
                                vendor_exchange_date = data[0].exchange_date;
                                update_final_exch_rate();
                            }
                        }
                    });
                }
            }
        });
    } else {
        $('#id_supplier_name').val('');
        $('#id_supplier_currency').val('');
        $('#id_account_set').val('').trigger('change');
    }
    $('#document-payment-table').DataTable().clear().draw();
});

$('#document-payment-table').on( 'draw.dt', function () {
    $('#document-payment-table tbody tr').bind('click', function () {
        var radio_td = $(this).find('td').eq(9);
        var radio = $(radio_td).find('input').eq(0);

        if($(radio).is(':checked')) {
            $(radio).prop("checked", false);
        } else {
            $(radio).prop("checked", true);
        }

        $("input[type='checkbox']:not(:checked)").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
        $("input[type='checkbox']:checked").each(function () {
            if(!$(this).hasClass('hidden')) {
                $(this).closest('tr').css('background-color', '#3ff3f3');
            }
        });
    });
    $("input[type='checkbox']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
    $('#document-payment-table tbody tr').each(function () {
        $(this).find('td').eq(3).text(comma_format($(this).find('td').eq(3).text()));
        $(this).find('td').eq(5).text(comma_format($(this).find('td').eq(5).text()));
        $(this).find('td').eq(6).text(comma_format($(this).find('td').eq(6).text()));
    });
});

$('#btnAddPaymentTransDialog').on('click', function () {
    var exclude_transaction_list = [];
    var supplier_id = parseInt($('#id_supplier').val());
    $('#document-payment-table').DataTable().destroy();

    transactiontbl = $('#py-transaction-table').DataTable();
    transactiontbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
        invoice_id = transactiontbl.cell(rowIdx, $('#trs-invoice-id').index()).data();
        exclude_transaction_list.push(invoice_id);
    });
    $('#document-payment-table').dataTable({
        "processing": true,
        "paging":   false,
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollX: true,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": "/accounting/document_payment_list/",
            "data": {
                'supplier_id': supplier_id,
                "exclude_transaction_list": JSON.stringify(exclude_transaction_list)
            },

        },
        "columns": [
            {"data": "document_number", "sClass": "text-left"},
            {"data": "document_type", "sClass": "text-left"},
            {"data": "document_date", "sClass": "text-left"},
            {"data": "document_amount", "sClass": "text-right"},
            {"data": "payment_number", "sClass": "text-right"},
            {"data": "paid_amount", "sClass": "text-right"},
            {"data": "out_amount", "sClass": "text-right"},
            {"data": "due_date", "sClass": "text-left"},
            {"data": "invoice_id", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    if (selected_doc.includes(full.invoice_id) || exclude_transaction_list.includes(String(full.invoice_id))) {
                        return '<input style="width: 15%;" type="checkbox" name="document-choices" id="check-' +
                        full.invoice_id + '" class="call-checkbox hidden" value="' + full.invoice_id + '">';
                    } else {
                        return '<input style="width: 15%;" type="checkbox" name="document-choices" id="check-' +
                        full.invoice_id + '" class="call-checkbox" value="' + full.invoice_id + '">';
                    }

                }
            },
        ]
    });
    setTimeout(() => {
        $('#document-payment-table').DataTable().columns.adjust();
    }, 300);
});

function PaymentTransaction() {
    this.document_number = null;
    this.document_type = null;
    this.document_date = null;
    this.document_amount = null;
    this.payment_number = null;
    this.paid_amount = null;
    this.outstanding_amount = null;
    this.due_date = null;
    this.invoice_id = null;
    this.id = null;
}

function getPaymentTransactionForm(invoice_id) {
    var transaction = new PaymentTransaction();
    var datatbl = $('#document-payment-table').DataTable();
    datatbl.rows().every(function (row, tableLoop, rowLoop) {
        invc_id = datatbl.cell(row, $('#invoice-id').index()).data();
        if (invc_id == invoice_id) {
            transaction.document_number = datatbl.cell(row, $('#doc-num').index()).data();
            transaction.document_type = datatbl.cell(row, $('#doc-type').index()).data();
            transaction.document_date = datatbl.cell(row, $('#doc-date').index()).data();
            transaction.document_amount = datatbl.cell(row, $('#doc-amount').index()).data();
            transaction.payment_number = datatbl.cell(row, $('#py-num').index()).data();
            transaction.paid_amount = datatbl.cell(row, $('#py-amount').index()).data();
            transaction.outstanding_amount = datatbl.cell(row, $('#out-amount').index()).data();
            transaction.due_date = datatbl.cell(row, $('#due-date').index()).data();
            transaction.invoice_id = datatbl.cell(row, $('#invoice-id').index()).data();
        }
    });
    return transaction;
}

function selectDocuments() {
    $('#loading').show();

    $("input[name='document-choices']:checked").each(function () {
        row = this.value;
        // doctbl = $('#document-payment-table').DataTable();
        // invoice_id = doctbl.cell(row, $('#invoice-id').index()).data();
        invoice_id = this.value;
        selected_doc.push(parseInt(invoice_id));
        selected_row.push(this.value);
    });

    selected_row = selected_row.filter(function (item, index, inputArray) {
        return inputArray.indexOf(item) == index;
    });

    if (selected_row.length > 0) {
        var table = $('#py-transaction-table').DataTable();
        for (i = 0; i < selected_row.length; i++) {
            if (!alreadyDrawed.includes(String(selected_row[i]))) {
                paymentTransaction = getPaymentTransactionForm(selected_row[i]);
                for (x = 0; x < stashedInvoices.length; x++) {
                    if (stashedInvoices[x].id == paymentTransaction.invoice_id) {
                        paymentTransaction.outstanding_amount = float_format(paymentTransaction.outstanding_amount) + float_format(stashedInvoices[x].amount);
                        paymentTransaction.id = stashedInvoices[x].transaction_id;
                    }
                }
                var button = '<div class="btn-group dropup">'
                    + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" style="min-width: 40px!important;" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Action'
                    + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
                    + '</button>'
                    + '<ul class="dropdown-menu dropdown-menu-right">'
                    + '<li><a onclick="deleteNewPaymentTransactionModal(' + selected_doc[i] + ')">Delete</a></li>'
                    + '</ul>'
                    + '</div>';
                // appliedAmount = '<input class="form-control-item applied-amount" id="appliedAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="' + comma_format(paymentTransaction.outstanding_amount) + '" type="text" step="0.01" min="0">'
                // discountAmount = '<input class="form-control-item discount-amount" id="discountAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="0.00" type="text" step="0.01" min="0">'
                outstanding_amount = comma_format(paymentTransaction.outstanding_amount)
                document_amount = comma_format(paymentTransaction.document_amount)
                if (vendor_is_decimal) {
                    outstanding_amount = comma_format(paymentTransaction.outstanding_amount)
                    document_amount = comma_format(paymentTransaction.document_amount)
                    appliedAmount = '<input style="" class="applied-amount text-right" id="appliedAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="' + comma_format(paymentTransaction.outstanding_amount) + '" type="text" step="0.01" min="0">'
                    discountAmount = '<input style="" class="discount-amount text-right" id="discountAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="0.00" type="text" step="0.01" min="0">'
                } else {
                    appliedAmount = '<input style="" class="applied-amount text-right" id="appliedAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="' + comma_format(paymentTransaction.outstanding_amount, 0) + '" type="text" step="1" min="0">'
                    discountAmount = '<input style="" class="discount-amount text-right" id="discountAmount-' + selected_doc[i] + '" name="appliedAmount" onblur="checkValue(' + selected_doc[i] + ')" value="0" type="text" step="1" min="0">'
                    outstanding_amount = comma_format(paymentTransaction.outstanding_amount, 0)
                    document_amount = comma_format(paymentTransaction.document_amount, 0)
                }

                array_row = [
                    paymentTransaction.document_number,
                    paymentTransaction.document_type,
                    paymentTransaction.payment_number,
                    outstanding_amount,
                    appliedAmount,
                    discountAmount,
                    outstanding_amount,
                    document_amount,
                    paymentTransaction.document_date,
                    paymentTransaction.due_date,
                    button,
                    paymentTransaction.id,
                    paymentTransaction.invoice_id,
                ]
                table.row.add(array_row).draw();
                alreadyDrawed.push(selected_row[i]);
                $('#appliedAmount-' + selected_doc[i]).trigger('blur');
            }

        }

        $("#Payment_TransModal").modal("hide");
        checkNegativeValue();

    } else {
        $("#supplier_error").text("Please choose at least 1 document");
    }
    $('#loading').hide();
}

function checkNegativeValue() {
    $("input[name='appliedAmount']").keydown(function (e) {
        // Allow: backspace, delete, tab, escape, enter and .
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
            // Allow: Ctrl+A, Command+A
            (e.keyCode === 65 && (e.ctrlKey === true || e.metaKey === true)) ||
            // Allow: home, end, left, right, down, up
            (e.keyCode >= 35 && e.keyCode <= 40)) {
            // let it happen, don't do anything
            return;
        }
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
}

function checkValue(invoice_id) {
    // if($("input[name='appliedAmount-"+row+"']").val() == '') {
    //     $('#appliedAmount-'+row).val(float_format('0.00').toFixed(2))
    // } else {
    //     $('#appliedAmount-'+row).val(value.toFixed(2));
    // }

    table = $('#py-transaction-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        selected = table.cell(rowIdx, $('#trs-invoice-id').index()).data();
        if (selected == invoice_id) {
            value = float_format(table.cell(rowIdx, $('#trs-apply-amount').index()).node().firstChild.value.replace(',', ''));
            discount = float_format(table.cell(rowIdx, $('#trs-discount-amount').index()).node().firstChild.value.replace(',', ''));

            if (isNaN(discount)) discount = 0;

            if ($.isNumeric(value)) {
                if(vendor_is_decimal) {
                    $('#appliedAmount-' + invoice_id).val(comma_format(value));
                }else{
                    $('#appliedAmount-' + invoice_id).val(comma_format(value, 0));
                }

                outstandingAmount = float_format(table.cell(rowIdx, $('#trs-out-amount').index()).data());

                if (value + discount > outstandingAmount) {
                    $('#appliedAmount_error').text('Applied amount is greater than remaining balance. Please reduce the applied amount !');
                    value = 0;
                    $('#appliedAmount-' + invoice_id).val(float_format('0.00').toFixed(2));
                    $('#appliedAmount-' + invoice_id).focus();
                } else {
                    $('#appliedAmount_error').text('');
                    netAmount = outstandingAmount - (value + discount);
                    calculate_value = recalculatePaymentAmount();
                    if(bank_is_decimal) {
                        $('#id_total_amount').val(comma_format(calculate_value.total_amount));
                        $('#id_payment_amount').val(comma_format(calculate_value.total_amount));
                    } else {
                        $('#id_total_amount').val(comma_format(calculate_value.total_amount, 0));
                        $('#id_payment_amount').val(comma_format(calculate_value.total_amount, 0));
                    }
                    if(vendor_is_decimal) {
                        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount));
                        table.cell(rowIdx, $('#trs-net-amount').index()).data(comma_format(netAmount));
                    } else {
                        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount, 0));
                        table.cell(rowIdx, $('#trs-net-amount').index()).data(comma_format(netAmount, 0));
                    }
                }
            } else {
                $('#appliedAmount-' + invoice_id).val(float_format('0.00').toFixed(2));
            }
        }
    });
}

function deleteNewPaymentTransactionModal(invoice_id) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deletePaymentTransaction(" + invoice_id + ")");
}

function deleteOldPaymentTransactionModal(transaction_id, invoice_id, amount) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteOldPaymentTransaction(" + transaction_id + "," + invoice_id + "," + amount + ")");
}

// delete not-saved-yet Payment Transaction
function deletePaymentTransaction(invoice_id) {
    var table = $('#py-transaction-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        selected = table.cell(rowIdx, $('#trs-invoice-id').index()).data();
        if (selected == invoice_id) {
            table.row(rowIdx).remove().draw();
            // index1 = selected_row.indexOf(String(rowIdx));
            // index2 = alreadyDrawed.indexOf(String(rowIdx));
            selected_row.splice(rowIdx, 1);
            alreadyDrawed.splice(rowIdx, 1);
        }
    });


    index3 = selected_doc.indexOf(invoice_id);

    // if(index1 > -1 && index2 > -1) {
    //     selected_row.splice(index1, 1);
    //     alreadyDrawed.splice(index2, 1);
    // }
    if (index3 > -1) {
        selected_doc.splice(index3, 1);
    }
    calculate_value = recalculatePaymentAmount();
    if(bank_is_decimal) {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount));
    } else {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount, 0));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount, 0));
    }
    if(vendor_is_decimal) {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount));
    } else {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount, 0));
    }
}

// delete already saved Payment Transaction
function deleteOldPaymentTransaction(transaction_id, invoice_id, amount) {
    invoice = {};
    invoice.id = invoice_id;
    invoice.amount = amount;
    invoice.transaction_id = transaction_id;
    stashedInvoices.push(invoice);

    var table = $('#py-transaction-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        selected = table.cell(rowIdx, $('#trs-invoice-id').index()).data();
        if (selected == invoice_id) {
            table.row(rowIdx).remove().draw();
            // index1 = selected_row.indexOf(String(rowIdx));
            // index2 = alreadyDrawed.indexOf(String(rowIdx));
            selected_row.splice(rowIdx, 1);
            alreadyDrawed.splice(rowIdx, 1);
        }
    });


    index3 = selected_doc.indexOf(invoice_id);

    // if(index1 > -1 && index2 > -1) {
    //     selected_row.splice(index1, 1);
    //     alreadyDrawed.splice(index2, 1);
    // }
    if (index3 > -1) {
        selected_doc.splice(index3, 1);
    }
    calculate_value = recalculatePaymentAmount();
    if(bank_is_decimal) {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount));
    } else {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount, 0));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount, 0));
    }
    if(vendor_is_decimal) {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount));
    } else {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount, 0));
    }
}



// Add transaction list data when submit form
function getTransactionTableData(form) {
    if ($('#id_exchange_rate').val() == "") {
        pop_ok_dialog("Invalid Exchange Rate",
            "Please enter a valid Exchange Rate",
            function () { }
        );
        return false;
    }
    var array = [];
    $('#transaction_list_data').val(JSON.stringify(array));
    $('#loading').show();
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == PAYMENT_TRANSACTION_TYPES_PAYMENT) {
        var amount_list = [];
        $("input[name='appliedAmount']").each(function () {
            amount_list.push($(this).val());
        });
        if (validatePayment(transaction_type) == 0) {
            // if($.inArray('0.000000', amount_list) == -1) {
            array = [];
            array.length = 0;
            var table = $('#py-transaction-table').DataTable();
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                rowData = this.data();
                applied_amount = table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.value;
                discount_amount = table.cell(rowIdx, $("#trs-discount-amount").index()).node().firstChild.value;

                transaction_list = {};
                transaction_list.document_number = rowData[$("#trs-doc-num").index()];
                transaction_list.document_type = rowData[$("#trs-doc-type").index()];
                transaction_list.payment_number = rowData[$("#trs-py-num").index()];
                transaction_list.outstanding_amount = rowData[$("#trs-out-amount").index()];
                transaction_list.applied_amount = applied_amount;
                transaction_list.discount_amount = discount_amount;
                transaction_list.net_amount = rowData[$("#trs-net-amount").index()];
                transaction_list.document_amount = rowData[$("#trs-doc-amount").index()];
                transaction_list.documnent_date = rowData[$("#trs-doc-date").index()];
                transaction_list.due_date = rowData[$("#due-date").index()];
                transaction_list.id = rowData[$("#trs-py-id").index()] || '';
                transaction_list.invoice_id = rowData[$("#trs-invoice-id").index()];
                array.push(transaction_list);
            });

            $('#transaction_list_data').val(JSON.stringify(array));
        } else {
            $('#loading').hide();
            return false;
        }
        $('#id_amount').val(float_format($('#id_amount').val()));
        $('#id_tax_amount').val(float_format($('#id_tax_amount').val()));
        $('#id_total_amount').val(float_format($('#id_total_amount').val()));
        $('#id_payment_amount').val(float_format($('#id_total_amount').val()));
        $('#id_original_amount').val(float_format($('#id_original_amount').val()));
        $('#id_batch_amount').val(float_format($('#id_batch_amount').val()));
    } else if (transaction_type == PAYMENT_TRANSACTION_TYPES_MISC_PAYMENT) {
        array = [];
        var table = $('#misc-transaction-table').DataTable();
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
            transaction_list.base_tax_amount = rowData[$("#trs-base_tax_amount").index()];
            transaction_list.total_amount = rowData[$("#trs-total_amount").index()];
            // transaction_list.delete = rowData[$("#trs-delete").index()];
            transaction_list.is_tax_included = rowData[$("#trs-tax_included").index()];
            transaction_list.is_tax_transaction = rowData[$("#trs-tax_transaction").index()];
            transaction_list.is_manual_tax_input = rowData[$("#trs-manual_tax_input").index()];
            transaction_list.tax_id = rowData[$("#trs-tax_id").index()];
            array.push(transaction_list);
        });

        $('#transaction_list_data').val(JSON.stringify(array));

        $('#id_amount').val(float_format($('#id_amount').val()));
        $('#id_tax_amount').val(float_format($('#id_tax_amount').val()));
        $('#id_total_amount').val(float_format($('#id_total_amount').val()));
        $('#id_batch_amount').val(float_format($('#id_batch_amount').val()));
        $('#id_payment_amount').val(float_format($('#id_total_amount').val()));
        $('#id_original_amount').val(float_format($('#id_original_amount').val()));
    }
    if('True' == is_rec_entry){
        var s_date = $('#start_date').val().split('-');
        if (s_date[0].length == 2)
            $('#start_date').val(moment($('#start_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        if ($('#expire_date').val()){
            var e_date = $('#expire_date').val().split("-");
            if(e_date[0].length == 2)
                $('#expire_date').val(moment($('#expire_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        }
    }

    form.btnSave.disabled = true;
    form.is_posted.disabled = true;
}

function recalculatePaymentAmount() {
    total_amount = 0.000000;
    vendor_amount = 0.000000;
    subtotal_amount = 0.000000;
    total_tax_amount = 0.000000;
    calculate_value = {};

    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == PAYMENT_TRANSACTION_TYPES_PAYMENT) {
        var bank_exch_rate = parseFloat($('#id_exchange_rate').val());
        var ven_exch_rate = parseFloat($('#id_orig_exch_rate').val());
        supp_bank_exch_rate =  ven_exch_rate / bank_exch_rate;
        var table = $('#py-transaction-table').DataTable();
        table.rows().every(function (rowIdx, tableLoop, rowLoop) {
            doc_type = table.cell(rowIdx, $("#trs-doc-type").index()).data();
            amount = table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.value;
            if (doc_type == 'Credit Note'){
                total_amount -= (float_format(amount) * float_format(supp_bank_exch_rate));
                vendor_amount -= float_format(amount);
            } else {
                total_amount += (float_format(amount) * float_format(supp_bank_exch_rate));
                vendor_amount += float_format(amount);
            }
        });
        calculate_value.total_amount = float_format((total_amount).toFixed(3));
        calculate_value.vendor_amount = float_format((vendor_amount).toFixed(3));

        return calculate_value;
    } else if (transaction_type == PAYMENT_TRANSACTION_TYPES_MISC_PAYMENT) {
        var datatbl = $('#misc-transaction-table').DataTable();
        datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
            tt_amount = datatbl.cell(rowIdx, $("#trs-total_amount").index()).data();
            st_amount = datatbl.cell(rowIdx, $("#trs-amount").index()).data();
            tax_amount = datatbl.cell(rowIdx, $("#trs-tax_amount").index()).data();
            int_tt_amount = tt_amount.replace(/,/g , '');
            int_st_amount = st_amount.replace(/,/g , '');
            if (tax_amount){
                int_tax_amount = tax_amount.replace(/,/g, '');
            } else {
                int_tax_amount = 0;
            }

            total_amount += float_format(int_tt_amount);
            subtotal_amount += float_format(int_st_amount);
            total_tax_amount += float_format(int_tax_amount);
        });

        calculate_value.total_amount = float_format((total_amount).toFixed(3));
        calculate_value.subtotal_amount = float_format((subtotal_amount).toFixed(3));
        calculate_value.total_tax_amount = float_format((total_tax_amount).toFixed(3));

        return calculate_value;
    }
}

function update_exch_rate() {
    var date_rate = $("#id_document_date").val();
    var bank_currency = $("#id_currency option:selected").val();
    var supplier_currency = $("#id_supplier_currency").val();
    if (bank_currency) {
        $.ajax({
            type: "GET",
            url :'/currencies/get_exchange_by_date/1/'+bank_currency+'/'+date_rate+'/3/',
            dataType: 'JSON',
            success: function(data){
                if (parseFloat(data[0].rate) == 0) {
                    pop_ok_dialog("Invalid Exchange Rate",
                        "Exchange Rate not found for current period for " + data[0].from_code + " to " + data[0].to_code +".",
                        function () { }
                    );
                } else {
                    company_currency = data[0].company_currency;
                    $('#id_exchange_rate_fk').val(data[0].id);
                    $('#id_exchange_rate').val(data[0].rate).trigger('change');
                    $('#id_payment_currency_id').val(parseInt(bank_currency));
                    bank_is_decimal = data[0].is_decimal;
                    bank_exchange_date = data[0].exchange_date;
                }
            }
        });
    }
    if (supplier_currency) {
        $.ajax({
            type: "GET",
            url :'/currencies/get_exchange_by_date/1/'+supplier_currency+'/'+date_rate+'/3/',
            dataType: 'JSON',
            success: function(data){
                if (parseFloat(data[0].rate) == 0) {
                    pop_ok_dialog("Invalid Exchange Rate",
                        "Exchange Rate not found for current period for " + data[0].from_code + " to " + data[0].to_code +".",
                        function () { }
                    );
                } else {
                    company_currency = data[0].company_currency;
                    $('#id_orig_exch_rate').val(data[0].rate).trigger('change');
                    $('#id_original_currency_id').val(parseInt(supplier_currency));
                    vendor_is_decimal = data[0].is_decimal;
                    vendor_exchange_date = data[0].exchange_date;
                }
            }
        });
    }
    setTimeout(() => {
        update_final_exch_rate();
    }, 600);

}

function update_final_exch_rate() {
    var bank_currency = $("#id_currency option:selected").val();
    var supplier_currency = $("#id_supplier_currency").val();
    if (bank_currency && supplier_currency) {
        if (bank_currency != supplier_currency) {
            is_currency_differene = true;
            bank_exch_rate = parseFloat($('#id_exchange_rate').val());
            ven_exch_rate = parseFloat($('#id_orig_exch_rate').val());
            supp_bank_exch_rate =  ven_exch_rate / bank_exch_rate;
        } else {
            supp_bank_exch_rate = 1.0;
        }
    } else {
        supp_bank_exch_rate = 1.0;
    }
    calculate_value = recalculatePaymentAmount();
    if(bank_is_decimal) {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount));
    } else {
        $('#id_total_amount').val(comma_format(calculate_value.total_amount, 0));
        $('#id_payment_amount').val(comma_format(calculate_value.total_amount, 0));
    }
    if(vendor_is_decimal) {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount));
    } else {
        $('#id_original_amount').val(comma_format(calculate_value.vendor_amount, 0));
    }
}

// validate amount and currency for AP Payment - Payment Type
function validatePayment(transaction_type) {
    error = 0;
    if (transaction_type == PAYMENT_TRANSACTION_TYPES_PAYMENT) {
        amount_list = [];
        $("input[name='appliedAmount']").each(function () {
            amount_list.push($(this).val());
        });

        if ($.inArray('0.000000', amount_list) != -1) {
            error += 1;
            $('#appliedAmount_error').text('Applied amount must be greater than zero !');
        } else {
            $('#appliedAmount_error').text('');
        }

        // bank_currency = $("#id_currency option:selected").val();
        // supplier_currency = $("#id_supplier_currency").val();
        // if (bank_currency != supplier_currency) {
        //     error += 1;
        //     $('#journal_error').text('Bank currency and Supplier currency is not the same currency.')
        //     $("html, body").animate({scrollTop: 0}, "fast");
        // } else {
        //     $('#journal_error').text('');
        // }
    }
    return error;
}

$('#account-table').on( 'draw.dt', function () {
    selectTableRow('#account-table', 6);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Account button*/
$('#btnSearchAccountSet').on('click', function () {
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
            "url": "/accounting/account_set_list/2/", /* ACCOUNT_SET_TYPE_DICT['AP Account Set'] */
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.currency_id = $('#id_supplier_currency').val();
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

$('#payment-table').on( 'draw.dt', function () {
    selectTableRow('#payment-table', 3);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

$('#btnSearchPaymentCode').on('click', function () {
    if ($('#id_payment_code').prop('disabled') == true) {
        alert('Please select Customer');
    } else {
        $('#id_payment_code').prop('disabled', false);
        $('#payment-table').DataTable().destroy();
        $('#payment-table').dataTable({
            "iDisplayLength": 10,
            // "bLengthChange": false,
            scrollY: '50vh',
            scrollCollapse: true,
            "order": [[0, "asc"]],
            "serverSide": true,
            "ajax": {
                "url": "/accounting/load_payment_list/2/",
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "name", "sClass": "text-left"},
                {"data": "payment_type", "sClass": "text-left"},
                {
                    "orderable": false,
                    "data": null,
                    "sClass": "hide_column",
                    "render": function (data, type, full, meta) {
                        return '<input type="radio" name="payment-choices" id="' +
                            full.id + '" class="call-checkbox" value="' + full.id + '">';
                    }
                },
            ]
        });
        setTimeout(() => {
            $('#payment-table').DataTable().columns.adjust();
        }, 300);
    }
});


$('#btnPaymentSelect').on('click', function () {
    $("input[name='payment-choices']:checked").each(function () {
        $('#id_payment_code option').removeAttr('selected');
        $('#id_payment_code option[value="' + this.value + '"]').prop('selected', true);
        $('#select2-id_payment_code-container').text($('#id_payment_code option:selected').text());
    });
});

$('#id_is_manual_doc').on('change', function() {
    isManualDoc = $('#id_is_manual_doc:checkbox:checked').length;

    if(isManualDoc > 0) {
        $('#id_document_number').val('');
        //$('#id_document_number').prop('readonly', false);
        $('.readonly').off('keydown paste');
        $('#id_document_number').removeClass('disabled readonly');
        $('#id_document_number').attr('required', true);
    }
    else {
        $('#id_document_number').removeAttr('required');
        $('#id_document_number').val('');
        $('#id_document_number').addClass('disabled readonly');
        $('.readonly').on('keydown paste', function(e) {
                e.preventDefault();
        });
    }
});

$('#id_document_date').on('change', function() {
    $('#id_posting_date').val($('#id_document_date').val());
    update_exch_rate();
    set_tax_reporting_rate();
});

$('#btnSaveAPPayment').on('click', function () {
    setTimeout(function(){
        $('#btnSaveAPPayment').prop('disabled', true);
    }, 100);
});

$(document).on('change keypress', 'input', function() {
    $('#btnSaveAPPayment').prop('disabled', false);
});

$(document).on('change', 'select', function() {
    $('#btnSaveAPPayment').prop('disabled', false);
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
