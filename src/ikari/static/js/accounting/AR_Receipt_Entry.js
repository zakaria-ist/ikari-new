var RECEIPT_TRANSACTION_TYPES_RECEIPT = 1;
var RECEIPT_TRANSACTION_TYPES_MISC_RECEIPT = 2;
var RECEIPT_TRANSACTION_TYPES_UNAPPLIED_CASH = 3;

var is_currency_differene = false;
var supp_bank_exch_rate = 1;
var company_currency = 'FUNC. CURR.';
var bank_exchange_date = '';
var vendor_exchange_date = '';

var trigger_row;
var trigger_line = 1;
var new_line = false;

$.adjustment_data = {};
$.invoiceTransactions = {};
$.old_discount = {};

/**
 * Created by tho.pham on 11/10/2016.
 */


function set_tax_reporting_rate() {
    var currency_id = $('#id_currency').val();
    var doc_date = $('#id_document_date').val();
    if(currency_id && doc_date) {
        get_tax_reporting_rate(currency_id, doc_date);
    }
}

$('#id_bank').on('change', function () {
    var bank_id = parseInt($(this).val());
    if (bank_id) {
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
            } else {
                $('#id_currency option:empty').prop('selected', true);
            }
            //Generate reference number
            var day = $('#doc_date_view').val();
            var pecahin = day.split('-');
            var bulan = pecahin[1];
            var tahun = pecahin[2].substring(2, 4);
            var bank_id = $("#id_bank option:selected").val();
            var serial = serial_no;
            var curr_val = $("#id_currency").val();
            var curr = $("#id_currency option[value=" + curr_val + "]").text();
            $(".payment_currency").val(curr);
            if ((ref == '') & (bank_id > 0) & (serial_no != '')) {
                bank = $("#id_bank option:selected").text().substring(0, 3);
                // id_ven = $("#id_supplier option:selected").val();
                $('#id_reference').val(bank + '-R' + serial + '-' + bulan + '/' + tahun + '' + curr);
            }
            if (journal_id == '0') {
                var date_rate = $("#id_document_date").val();
                var bank_currency = $("#id_currency option:selected").val();
                if (bank_currency) {
                    $.ajax({
                        type: "GET",
                        url :'/currencies/get_exchange_by_date/1/'+bank_currency+'/'+date_rate+'/3/',
                        dataType: 'JSON',
                        success: function(data){
                            console.log('data', data)
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

$('#id_document_date').on('change', function() {
    $('#id_posting_date').val($('#id_document_date').val());
    update_exch_rate();
    set_tax_reporting_rate();
});

$('#id_customer').on('change', function () {
    transaction_new.length = 0;
    if ($(this).val()) {
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
                $('#id_customer_name').val(json.customer_name);
                $('#id_customer_currency option').removeAttr('selected');
                if (json['currency_id'] != null) {
                    $('#id_customer_currency option[value="' + json['currency_id'] + '"]').prop('selected', true);
                } else {
                    $('#id_customer_currency option:empty').prop('selected', true);
                }
                var curr =  $('#id_customer_currency option[value="' + json['currency_id'] + '"]').text();
                $(".cust_currency").val(curr);
                $('#id_account_set').prop('disabled', false);
                $('#id_account_set option').removeAttr('selected');
                $('#id_account_set').val(json.account_set_id).trigger('change');


                $('#id_payment_code').prop('disabled', false);
                $('#id_payment_code').find('option:selected').removeAttr('selected');
                if (json['payment_code_id'] != null) {
                    $('#id_payment_code option[value=' + json['payment_code_id'] + ']').attr('selected', 'selected');
                    $('#id_payment_code').val(json['payment_code_id']);
                    $('#id_payment_code option[value="' + json['payment_code_id'] + '"]').prop('selected', true);
                    $('#select2-id_payment_code-container').find('span').text($('#id_payment_code option:selected').text());
                } else {
                    $('#id_payment_code option:empty').prop('selected', true);
                    $('#select2-id_payment_code-container').find('span').text('Select Payment Code');
                }
                setTimeout(() => {
                    // $('#id_payment_code').trigger('change');
                    $('#id_payment_code').focus();
                }, 500);
                

                $('#btnAddReceiptTransDialog').removeAttr('disabled');
                $('button[type="submit"]').prop('disabled', false);
                $('#btnSearchAccountSet').prop('disabled', false);
                $('#btnSearchPaymentCode').prop('disabled', false);
                $('#transaction-table').DataTable().clear().draw();
                $('#id_total_amount').val(float_format(0.00).toFixed(2));
                $('#id_payment_amount').val(float_format(0.00).toFixed(2));
                $('#id_original_amount').val(float_format(0.00).toFixed(2));
                $('#id_receipt_unapplied').val(float_format(0.00).toFixed(2));
                $('#id_customer_unapplied').val(float_format(0.00).toFixed(2));
                $.initTransactionInput();
                current_line = 0;
                set_tax_reporting_rate();

                var id_account_set = $('#id_account_set').val();
                if (!id_account_set){
                    $.ajax({
                        method: "POST",
                        url: '/accounting/load_account_set/1/',
                        dataType: 'JSON',
                        data: {
                            'currency_id': json['currency_id'],
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
                var customer_currency = $("#id_customer_currency").val();
                if (customer_currency) {
                    $.ajax({
                        type: "GET",
                        url :'/currencies/get_exchange_by_date/1/'+customer_currency+'/'+date_rate+'/3/',
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
                                $('#id_original_currency_id').val(parseInt(customer_currency));
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
        $('#id_customer_name').val('');
        $('#id_customer_currency').val('');
        $('#id_account_set').val('').trigger('change');
    }
    $('#document-receipt-table').DataTable().clear().draw();
});



$('#id_total_amount').on('change', function () {
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
        var total_amount = float_format($(this).val());
        var pay_amount = float_format($('#id_payment_amount').val());
        // if (total_amount > pay_amount) {
        //     pay_amount = total_amount;
        //     $('#id_payment_amount').val(comma_format(pay_amount));
        //     $('#id_original_amount').val(comma_format(pay_amount / supp_bank_exch_rate));
        // }
        var rem_amount = pay_amount - total_amount;
        var rem_cust_amount = (pay_amount - total_amount) / supp_bank_exch_rate;
        if (bank_is_decimal) {
            $('#id_receipt_unapplied').val(comma_format(rem_amount));
        } else {
            $('#id_receipt_unapplied').val(comma_format(rem_amount, 0));
        }
        if (vendor_is_decimal) {
            $('#id_customer_unapplied').val(comma_format(rem_cust_amount));
        } else {
            $('#id_customer_unapplied').val(comma_format(rem_cust_amount, 0));
        }
    }
});

$('#id_payment_amount').on('change', function () {
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type != RECEIPT_TRANSACTION_TYPES_MISC_RECEIPT) {
        var pay_amount = float_format($(this).val());
        var total_amount = float_format($('#id_total_amount').val());
        var rem_amount = pay_amount - total_amount;
        if (rem_amount < 0) {
            pay_amount = total_amount;
            rem_amount = 0;
        }
        var orig_amount = pay_amount / supp_bank_exch_rate;
        var rem_orig_amount = rem_amount / supp_bank_exch_rate;

        if (vendor_is_decimal) {
            $('#id_original_amount').val(comma_format(orig_amount));
            $('#id_customer_unapplied').val(comma_format(rem_orig_amount));
        } else {
            $('#id_original_amount').val(comma_format(orig_amount, 0));
            $('#id_customer_unapplied').val(comma_format(rem_orig_amount, 0));
        }
        if (bank_is_decimal) {
            $('#id_receipt_unapplied').val(comma_format(rem_amount));
            $(this).val(comma_format(pay_amount));
        } else {
            $('#id_receipt_unapplied').val(comma_format(rem_amount, 0));
            $(this).val(comma_format(pay_amount, 0));
        }
    }
});


// $('#id_original_amount').on('change', function () {
//     transaction_type = $('#id_transaction_type').val();
//     if (transaction_type == RECEIPT_TRANSACTION_TYPES_UNAPPLIED_CASH) {
//         var orig_amount = float_format($(this).val());
//         var pay_amount = comma_format(orig_amount * supp_bank_exch_rate);
//         $('#id_payment_amount').val(pay_amount);
//         $(this).val(comma_format(orig_amount));
//     }
// });


$('#id_transaction_type').on('change', function () {
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
        $("#id_customer").prop('disabled', false);
        $('#id_customer').val('').trigger('change');
        $('#id_payment_code').val('');
        $('#id_account_set').val('');
        $('#id_payment_code').select2({
            placeholder: "Select Payment Code",
        });

        $('#id_customer_group').removeClass('hidden');
        $('#id_account_set_group').removeClass('hidden');
        $("#id_tax_group").addClass('hidden');

        $("#id_customer").prop('required', true);
        $("#id_account_set").prop('required', true);

        $('#transaction-table').DataTable().clear().draw();
        $('#transaction-table').removeClass('hidden');
        $('#transaction_div').removeClass('hidden');
        $('#misc-transaction-table').DataTable().clear().draw();
        $('#misc_transaction_div').addClass('hidden');
        $('#tax_reporting_rate_div').addClass('hidden');


        if (!$('#id_customer').val()) {
            $('#id_account_set').prop('disabled', true);
            $('#id_payment_code').prop('disabled', true);
            $('#btnAddReceiptTransDialog').attr('disabled', 'disabled');
            $('button[type="submit"]').prop('disabled', true);
            $('#btnSearchAccountSet').prop('disabled', true);
            $('#btnSearchPaymentCode').prop('disabled', true);
        }

        $("#id_tax").val('');
        $('#id_tax').select2({
            placeholder: "Select Tax",
            width: '100%',
        });

        $("#id_invoice_number").val("");

        $('#amount-div').children().addClass('hidden');
        $('#tax-amount-div').children().addClass('hidden');
        $('#tax-report-amount-div').children().addClass('hidden');
        $('#total-amount-div').addClass('hidden');
        //$('#id_payment_amount').addClass('disabled readonly');
        //$('#id_original_amount').addClass('disabled readonly');
        $('#id_total_amount').val(float_format(0.00).toFixed(2));
        $('#id_payment_amount').val(float_format(0.00).toFixed(2));
        $('#id_original_amount').val(float_format(0.00).toFixed(2));
        $('#id_receipt_unapplied').val(float_format(0.00).toFixed(2));
        $('#id_customer_unapplied').val(float_format(0.00).toFixed(2));
        $('#id_receipt_unapplied').removeClass('hidden');
        $('#id_customer_unapplied').removeClass('hidden');

        $( "#check_type" ).hide();
        $( "#payment_code" ).show();
        $('#payment_div').removeClass('hidden');
        $('#unapplied_div').removeClass('hidden');

        $("#btnShowRateOverrideModal").removeClass('hidden');
    } else if (transaction_type == RECEIPT_TRANSACTION_TYPES_MISC_RECEIPT) {
        $('#id_customer_name').val('');
        $('#id_customer').val('').trigger('change');
        // $("#id_customer").prop('disabled', true);
        $('#id_customer_currency').val('');
        $('#id_customer_currency option:empty').prop('selected', true);
        $('#id_payment_code').val('');
        $('#id_account_set').val('');
        $("#id_invoice_number").val('');

        $('#id_customer').select2({
            placeholder: "Select Customer",
            allowClear: true
        });

        $('#id_account_set').select2({
            placeholder: "Select Account Set"
        });
        // $('#id_customer_group').addClass('hidden');
        // $('#id_account_set_group').addClass('hidden');
        $("#id_tax_group").removeClass('hidden');

        $("#id_customer").prop('required', false);
        $("#id_account_set").prop('required', false);

        $('#id_payment_code').prop('disabled', false);
        $('#btnSearchPaymentCode').prop('disabled', false);
        $('#transaction_div').addClass('hidden');

        $('#transaction-table').DataTable().clear().draw();
        $('#transaction_div').addClass('hidden');

        $('#misc-transaction-table').DataTable().clear().draw();
        $('#misc_transaction_div').removeClass('hidden');

        $('#amount-div').children().removeClass('hidden');
        $('#tax-amount-div').children().removeClass('hidden');
        $('#tax-report-amount-div').children().removeClass('hidden');
        $('#total-amount-div').removeClass('hidden');
        $('#payment_div').addClass('hidden');
        $('#unapplied_div').addClass('hidden');
        $('#tax_reporting_rate_div').removeClass('hidden');

        $('#id_total_amount').val(float_format(0.00).toFixed(2));
        $('#id_amount').val(float_format(0.00).toFixed(2));
        $('#id_tax_amount').val(float_format(0.00).toFixed(2));
        $('#id_tax_report_amount').val(float_format(0.00).toFixed(2));

        $("#id_tax").prop('disabled', false);

        current_line = 0;

        //default the selected option to "Check" instead of limit the option to 'only Check'
        var payment_code_list = $('#id_payment_code').data('dis-code');
        var payment_code_id = 0;
        var d = [];
        for (var i = 0; i < payment_code_list.length; i++) {
            var id = payment_code_list[i].id;
            var code = payment_code_list[i].code;
            d.push({'id': id, 'text' : code});
            if (payment_code_list[i].payment_type==2){
                payment_code_id = payment_code_list[i].id;
            }
        }
        var s = $('#id_payment_code').empty().select2({data : d });
        s.val(payment_code_id).trigger("change");

        //and then show the "check number field" just like the old system
        $( "#check_type" ).show();
        $("#id_payment_check_number").removeClass('hidden');
        $('#id_payment_check_number_label').removeClass('hidden');
        $( "#payment_code" ).hide();
        $("#btnShowRateOverrideModal").addClass('hidden');

        if(bank_is_decimal) {
            $("#id_amount").val(comma_format(float_format($("#id_amount").val())));
            $("#id_tax_amount").val(comma_format(float_format($("#id_tax_amount").val())));
            $("#id_total_amount").val(comma_format(float_format($("#id_total_amount").val())));
        } else {
            $("#id_amount").val(comma_format(float_format($("#id_amount").val()), 0));
            $("#id_tax_amount").val(comma_format(float_format($("#id_tax_amount").val()), 0));
            $("#id_total_amount").val(comma_format(float_format($("#id_total_amount").val()), 0));
        }
    } else if (transaction_type == RECEIPT_TRANSACTION_TYPES_UNAPPLIED_CASH) {
        $("#id_customer").prop('disabled', false);
        $('#id_customer').val('').trigger('change');
        $('#id_payment_code').val('');
        $('#id_account_set').val('');
        $('#id_payment_code').select2({
            placeholder: "Select Payment Code",
        });

        $('#id_customer_group').removeClass('hidden');
        $('#id_account_set_group').removeClass('hidden');
        $("#id_tax_group").addClass('hidden');

        $("#btnShowRateOverrideModal").removeClass('hidden');

        $("#id_customer").prop('required', true);
        $("#id_account_set").prop('required', true);

        $('#amount-div').children().addClass('hidden');
        $('#tax-amount-div').children().addClass('hidden');
        $('#tax-report-amount-div').children().addClass('hidden');
        $('#total-amount-div').addClass('hidden');
        $('#payment_div').removeClass('hidden');
        $('#unapplied_div').addClass('hidden');

        $('#transaction-table').DataTable().clear().draw();
        $('#transaction-table').addClass('hidden');
        $('#transaction_div').addClass('hidden');
        $('#misc-transaction-table').DataTable().clear().draw();
        $('#misc_transaction_div').addClass('hidden');
        $('#tax_reporting_rate_div').addClass('hidden');

        $('#id_payment_amount').val(float_format(0.00).toFixed(2));
        $('#id_original_amount').val(float_format(0.00).toFixed(2));
        $('#id_receipt_unapplied').val(float_format(0.00).toFixed(2));
        $('#id_customer_unapplied').val(float_format(0.00).toFixed(2));
        $('#id_receipt_unapplied').addClass('hidden');
        $('#id_customer_unapplied').addClass('hidden');

        //$('#id_payment_amount').removeClass('disabled readonly');
        //$('#id_original_amount').removeClass('disabled readonly');
    }
});

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
        var dtRow = dtTable.row($(this).parents('tr')[0]).data();
        selected_row.push(dtRow['currency_id']);
    });
    $('#id_bank option').removeAttr('selected');
    $('#id_bank option[value="' + selected_row[0] + '"]').prop('selected', true).trigger('change');
    $('#select2-id_bank-container').text($('#id_bank option:selected').text());
    $('#id_currency option').removeAttr('selected');
    $('#id_currency option[value="' + selected_row[1] + '"]').prop('selected', true);
});

$('#customer-table').on( 'draw.dt', function () {
    selectTableRow('#customer-table', 7);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});


$('#btnSearchCustomer').on('click', function () {
    // $("#supplier_error").text(""); // Delete error message
    $('#customer-table').DataTable().destroy();
    $('#customer-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": url_load_customer_list,
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "tax", "sClass": "text-left"},
            {"data": "currency", "sClass": "text-left"},
            {"data": "payment_term", "sClass": "text-left"},
            {"data": "payment_mode", "sClass": "text-left"},
            {"data": "account_set", "sClass": "text-left"},
            {"data": "account_set_id", "visible": false},
            {"data": "payment_code_id", "visible": false},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="customer-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + full.id + '">';
                }
            }
        ]
    });
    setTimeout(() => {
        $('#customer-table').DataTable().columns.adjust();
    }, 300);
});


$('#btnCustomerSelect').on('click', function () {
    var selected_row = [];
    var dtTable = $('#customer-table').DataTable();
    $("input[name='customer-choices']:checked").each(function () {
        selected_row.push(this.value);
        var dtRow = dtTable.row($(this).parents('tr')[0]).data();
        selected_row.push(dtRow['name']);
        selected_row.push(dtRow['currency']);
        selected_row.push(dtRow['account_set_id']);
        selected_row.push(dtRow['payment_code_id']);
    });
    $('#id_customer').val(selected_row[0]).trigger('change');
    // $('#id_customer option').removeAttr('selected');
    // $('#id_customer option[value="' + selected_row[0] + '"]').prop('selected', true);
    // $('#select2-id_customer-container').text($('#id_customer option:selected').text());
    // $('#id_customer_name').val(selected_row[1]);
    // $('#id_customer_currency option').removeAttr('selected');
    // if (selected_row[2] != null) {
    //     $("#id_customer_currency option:contains(" + selected_row[2] + ")").prop('selected', true);
    // } else {
    //     $('#id_customer_currency option:empty').prop('selected', true);
    // }
    ;
    $('#id_account_set').prop('disabled', false);
    $('#id_account_set option').removeAttr('selected');
    $('#id_account_set option[value="' + selected_row[3] + '"]').prop('selected', true);
    $('#select2-id_account_set-container').text($('#id_account_set option:selected').text());

    $('#id_payment_code').prop('disabled', false);
    $('#id_payment_code option').removeAttr('selected');
    $('#id_payment_code option[value="' + selected_row[4] + '"]').prop('selected', true);
    $('#select2-id_payment_code-container').text($('#id_payment_code option:selected').text());

    $('#btnAddPaymentTransDialog').removeAttr('disabled');
    $('#btnSearchAccountSet').prop('disabled', false);
    $('#btnSearchPaymentCode').prop('disabled', false);
    $('#fabtnAddReceiptTransDialoglse').prop('disabled', false);
    $('#btnAddReceiptTransDialog').removeAttr('disabled');
    $('button[type="submit"]').prop('disabled', false);
});

$('#account-table').on( 'draw.dt', function () {
    selectTableRow('#account-table', 6);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

$('#btnSearchAccountSet').on('click', function () {
    if ($('#id_account_set').prop('disabled') == true) {
        alert('Please select Customer');
    } else {
        $('#id_account_set').prop('disabled', false);
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
                "url": url_load_account_set_list,
                "data": function (d) {
                    d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                    d.currency_id = $('#id_customer_currency').val();
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
                            full.id + '" class="call-checkbox" value="' + full.id + '">';
                    }
                }
            ]
        });
        setTimeout(() => {
            $('#account-table').DataTable().columns.adjust();
        }, 300);
    }
});


$('#btnAccountSelect').on('click', function () {
    $("input[name='account-choices']:checked").each(function () {
        $('#id_account_set').val(this.value).trigger('change');
    });
});

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
                "url": url_load_payment_list,
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


$('#document-receipt-table').on( 'draw.dt', function () {
    $('#document-receipt-table tbody tr').bind('click', function () {
        var radio_td = $(this).find('td').eq(8);
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
            $(this).closest('tr').css('background-color', '#3ff3f3');
        });
    });
    $("input[type='checkbox']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
        $(this).on('click', function(){
            $(this).closest('tr').trigger('click');
        });
    });
    $('#document-receipt-table tbody tr').each(function () {
        if(vendor_is_decimal) {
            $(this).find('td').eq(3).text(comma_format($(this).find('td').eq(3).text()));
            $(this).find('td').eq(5).text(comma_format($(this).find('td').eq(5).text()));
            $(this).find('td').eq(6).text(comma_format($(this).find('td').eq(6).text()));
        } else {
            $(this).find('td').eq(3).text(comma_format($(this).find('td').eq(3).text(), 0));
            $(this).find('td').eq(5).text(comma_format($(this).find('td').eq(5).text(), 0));
            $(this).find('td').eq(6).text(comma_format($(this).find('td').eq(6).text(), 0));
        }
    });
});


$('#btnAddReceiptTransDialog').on('click', function () {
    var customer_id = parseInt($('#id_customer').val());
    var exclude_transaction_list = [];
    $('#document-receipt-table').DataTable().destroy();
    var transactionTbl = $('#transaction-table').DataTable();
    transactionTbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
        invoice_id = this.data()[11];
        exclude_transaction_list.push(invoice_id);
    });
    $.initTransactionInput();
    $('#document-receipt-table').dataTable({
        "processing": true,
        "paging":   false,
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": url_ReceiptDocumentsList_as_json,
            "data": {
                'customer_id': customer_id,
                "exclude_transaction_list": JSON.stringify(exclude_transaction_list)
            }

        },
        "columns": [
            {"data": "document_number", "sClass": "text-left"},
            {"data": "document_type", "sClass": "text-left"},
            {"data": "document_date", "sClass": "text-left"},
            {"data": "document_amount", "sClass": "text-right"},
            {"data": "payment_number", "sClass": "text-right"},
            {"data": "paid_amount", "sClass": "text-right"},
            {"data": "outstanding_amount", "sClass": "text-right"},
            {"data": "due_date", "sClass": "text-left"},
            {"data": "invoice_id", "sClass": "text-left", "visible": false},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    if (selected_row.includes(String(meta.row))) {
                        return '<input type="checkbox" name="document-choices" id="check-' +
                            meta.row + '" class="call-checkbox hidden" value="' + meta.row + '">';
                    } else {
                        return '<input type="checkbox" name="document-choices" id="check-' +
                            meta.row + '" class="call-checkbox" value="' + meta.row + '">';
                    }

                }
            }
        ]
    });
    setTimeout(() => {
        $('#document-receipt-table').DataTable().columns.adjust();
    }, 300);
});

function ReceiptTransaction() {
    this.document_number = null;
    this.document_type = null;
    this.document_date = null;
    this.document_amount = null;
    this.payment_number = null;
    this.paid_amount = null;
    this.discount_amount = null;
    this.adjustment_amount = null;
    this.outstanding_amount = null;
    this.due_date = null;
    this.invoice_id = null;
    this.adjustments = [];
}

function getReceiptTransactionForm(row) {
    var transaction = new ReceiptTransaction();
    datatbl = $('#document-receipt-table').DataTable();
    var currentRow = datatbl.row(row).data();

    transaction.document_number = currentRow.document_number;
    transaction.document_type = currentRow.document_type;
    transaction.document_date = currentRow.document_date;
    transaction.document_amount = currentRow.document_amount;
    transaction.payment_number = currentRow.payment_number;
    transaction.paid_amount = currentRow.paid_amount;
    transaction.discount_amount = currentRow.paid_amount;
    transaction.adjustment_amount = currentRow.paid_amount;
    transaction.outstanding_amount = currentRow.outstanding_amount;
    transaction.due_date = currentRow.due_date;
    transaction.invoice_id = currentRow.invoice_id;
    transaction.adjustments = ($.adjustment_data[row] !== undefined) ? $.adjustment_data[row] : [];

    return transaction;
}

function selectDocuments() {
    $('#loading').show();
    var selected_row = [];

    $("input[name='document-choices']:checked").each(function () {
        selected_row.push(this.value);
    });

    selected_row = selected_row.filter(function (item, index, inputArray) {
        return inputArray.indexOf(item) == index;
    });

    if (selected_row.length > 0) {
        var table = $('#transaction-table').DataTable();
        var row_number = table.rows().count();
        for (i = 0; i < selected_row.length; i++) {
            var receiptTransaction = getReceiptTransactionForm(selected_row[i]);
            // var button = '<button id="removerow' + row_number + '" type="button" class="btn btn-white fa fa-minus" value="Delete" onclick="deletePaymentTransaction(' + row_number + ')">'
            //     + '</button>'
            //     + '<button id="adjustrow' + row_number + '" type="button" class="btn btn-white fa fa-pencil btn-adjustment-transaction" value="Adjustment">'
            //     + '</button>';
            var button = '<div class="btn-group dropup">'
                            + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
                            + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
                            + '</button>'
                            + '<ul class="dropdown-menu dropdown-menu-right">'
                            + '<li><a id="adjustrow' + row_number + '" onclick="openAdjustmentDialog(' + row_number + ')">Adjust</a></li>'
                            + '<li><a id="removerow' + row_number + '" onclick="deletePaymentTransaction(' + row_number + ')">Delete</a></li>'
                            + '</ul>'
                            + '</div>';
            // appliedAmount = '<input class="form-control-item appliedAmount" id="appliedAmount-' + row_number + '" name="appliedAmount" value="' + comma_format(receiptTransaction.outstanding_amount) + '" type="text" step="0.000001" min="0" style="width: 100%">'
            // discountAmount = '<input class="form-control-item discountAmount" id="discountAmount-' + row_number + '" name="discountAmount" value="0.00" type="text" step="0.000001" min="0" style="width: 100%">'
            outstanding_amount = comma_format(receiptTransaction.outstanding_amount)
            document_amount = comma_format(receiptTransaction.document_amount)
            adjustmentAmount = '<span class="adjustment-amount text-right">0</span>'
                                + '<input type="hidden" class="input-adjustment-amount" id="adjustmentAmount-' + row_number + '" value="">';
            if (vendor_is_decimal) {
                outstanding_amount = comma_format(receiptTransaction.outstanding_amount)
                document_amount = comma_format(receiptTransaction.document_amount)
                appliedAmount = '<input style="" class="appliedAmount text-right" id="appliedAmount-' + row_number + '" name="appliedAmount" value="' + comma_format(receiptTransaction.outstanding_amount) + '" type="text" step="0.000001" min="0" style="width: 100%">'
                if (receiptTransaction.document_type == 'Invoice') {
                    discountAmount = '<input style="" class="discountAmount text-right" id="discountAmount-' + row_number + '" name="discountAmount" value="0.00" type="text" step="0.01" min="0" style="width: 100%">'
                } else {
                    discountAmount = '<input style="" class="discountAmount text-right" id="discountAmount-' + row_number + '" name="discountAmount" value="0.00" type="text" step="0.01" min="0" style="width: 100%" readonly>'
                }
            } else {
                outstanding_amount = comma_format(receiptTransaction.outstanding_amount, 0)
                document_amount = comma_format(receiptTransaction.document_amount, 0)
                appliedAmount = '<input style="" class="appliedAmount text-right" id="appliedAmount-' + row_number + '" name="appliedAmount" value="' + comma_format(receiptTransaction.outstanding_amount, 0) + '" type="text" step="1" min="0" style="width: 100%">'
                if (receiptTransaction.document_type == 'Invoice') {
                    discountAmount = '<input style="" class="discountAmount text-right" id="discountAmount-' + row_number + '" name="discountAmount" value="0" type="text" step="1" min="0" min="0" style="width: 100%">'
                } else {
                    discountAmount = '<input style="" class="discountAmount text-right" id="discountAmount-' + row_number + '" name="discountAmount" value="0" type="text" step="1" min="0" style="width: 100%" readonly>'
                }
            }
            array_row = [
                receiptTransaction.document_number,
                receiptTransaction.document_type,
                receiptTransaction.payment_number,
                outstanding_amount,
                appliedAmount,
                discountAmount,
                adjustmentAmount,
                outstanding_amount,
                document_amount,
                receiptTransaction.document_date,
                receiptTransaction.due_date,
                receiptTransaction.invoice_id,
                '',
                button,
                '',
            ]
            table.row.add(array_row).draw(false);
            $('#appliedAmount-' + row_number).attr("onchange", "checkValue(" + row_number + ")");
            $('#appliedAmount-' + row_number).trigger('change');
            row_number++;

            $("#transaction-table tbody tr").each(function() {			        
                $(this).find('td:eq(3)').addClass('text-right');
                $(this).find('td:eq(4)').addClass('text-right');
                $(this).find('td:eq(5)').addClass('text-right');
                $(this).find('td:eq(6)').addClass('text-right');
                $(this).find('td:eq(7)').addClass('text-right');
                $(this).find('td:eq(8)').addClass('text-right');
            });
        };

        $.initBtnAdjustmentTransaction();
        $.initTransactionInput();

        $("#Receipt_TransModal").modal("hide");
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
};

function checkValue(row) {
    var i_col_pending = $('#trs-out-amount').index();
    var i_col_original = $('#trs-doc-amount').index();
    var i_col_applied = $('#trs-apply-amount').index();
    var i_col_discount = $('#trs-discount').index();
    var i_col_adjustment = $('#trs-adjustment').index();

    var table = $('#transaction-table').DataTable();

    appliedAmount = float_format(table.cell(row, i_col_applied).node().firstChild.value.replace(',', ''));

    if (vendor_is_decimal) {
        if ($.isNumeric(appliedAmount)) {
            $('#appliedAmount-' + row).val(comma_format(appliedAmount));
        } else {
            $('#appliedAmount-' + row).val(float_format('0.00').toFixed(2));
        }
    } else {
        if ($.isNumeric(appliedAmount)) {
            $('#appliedAmount-' + row).val(comma_format(appliedAmount, 0));
        } else {
            $('#appliedAmount-' + row).val(float_format('0.00').toFixed(0));
        }
    }
    

    discountAmount = float_format(table.cell(row, i_col_discount).node().firstChild.value.replace(',', ''));

    if (vendor_is_decimal) {
        if ($.isNumeric(discountAmount)) {
            $('#discountAmount-' + row).val(comma_format(discountAmount));
        } else {
            $('#discountAmount-' + row).val(float_format('0.00').toFixed(2));
        }
    } else {
        if ($.isNumeric(discountAmount)) {
            $('#discountAmount-' + row).val(comma_format(discountAmount, 0));
        } else {
            $('#discountAmount-' + row).val(float_format('0.00').toFixed(0));
        }
    }

    adjustmentAmount = float_format(table.cell(row, i_col_adjustment).data());

    if (isNaN(adjustmentAmount)) {
        adjustmentAmount = float_format(0);
    }

    if (vendor_is_decimal) {
        if ($.isNumeric(adjustmentAmount)) {
            table.cell(row, 6).data(comma_format(adjustmentAmount));
        } else {
            table.cell(row, 6).data(float_format('0.00').toFixed(2));
        }
    } else {
        if ($.isNumeric(adjustmentAmount)) {
            table.cell(row, 6).data(comma_format(adjustmentAmount, 0));
        } else {
            table.cell(row, 6).data(float_format('0.00').toFixed(0));
        }
    }

    // table.row(row).invalidate();

    outstandingAmount = float_format(table.cell(row, i_col_pending).data().replace(',', ''));
    // outstandingAmount = outstandingAmount + adjustmentAmount;
    outstandingAmount = outstandingAmount;

    if ((appliedAmount + discountAmount)  > outstandingAmount) {
        $('#appliedAmount_error').text('Applied amount is greater than remaining balance. Please reduce the applied amount !');
        appliedAmount = float_format(0);
        discountAmount = float_format(0);
        adjustmentAmount = float_format(0);
        $('#appliedAmount-' + row).val(float_format('0.00').toFixed(2))
        $('#appliedAmount-' + row).focus();
        $('#discountAmount-' + row).val(float_format('0.00').toFixed(2))
        $('#discountAmount-' + row).focus();
        $('button[type="submit"]').prop('disabled', true);
    } else {
        $('#appliedAmount_error').text('');
        netAmount = outstandingAmount - appliedAmount - discountAmount;
        if (vendor_is_decimal) {
            table.cell(row, $('#trs-net-amount').index()).data(comma_format(netAmount));
        } else {
            table.cell(row, $('#trs-net-amount').index()).data(comma_format(netAmount, 0));
        }
        $('button[type="submit"]').prop('disabled', false);
    }
    var calculate_amount = recalculatePaymentAmount();
    if (bank_is_decimal) {
        $("#id_total_amount").val(comma_format(calculate_amount.total_amount)).trigger('change');
    } else {
        $("#id_total_amount").val(comma_format(calculate_amount.total_amount, 0)).trigger('change');
    }
    // $("#id_payment_amount").val(comma_format(calculate_amount.total_amount));
    // $("#id_original_amount").val(comma_format(calculate_amount.customer_amount));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val($('#id_total_amount').val());
    }
    if (parseInt(batch_id) == 0) {
        $("#id_batch_amount").val(comma_format(calculate_amount.total_amount));
    }
}

var initial_net_balance = [];

function adjustmentTransaction(row) {
    $.adjustment_active_row = row;
    $.adjustment_active_invoice_id = $('#transaction-table').DataTable().rows(row).data()[0][11];

    $('#adjustment_customer_number').val();
    $('#adjustment_customer_name').val();
    $('#adjustment_document_type').val();
    $('#adjustment_document_number').val();
    $('#adjustment_document_entry_number').val();
    $('#adjustment_entry_number').val();
    $('#adjustment_net_balance').val();
    $('#adjustment_currency').val();
    $('#adjustment_reference').val();
    $('#adjustment_description').val();

    $('#tableAdjustmentModal').off('show.bs.modal').on('show.bs.modal', function (e) {
        var json_data = $('#transaction-table').DataTable().cell($.adjustment_active_row, $('#trs-trx-adjustment').index()).data();
        var customer_code = $('#id_customer option:selected').html();
        var customer_name = $('#id_customer_name').val();
        var customer_currency = $('#id_customer_currency option:selected').html();
        var document_type = $('#transaction-table').DataTable().cell($.adjustment_active_row, $('#trs-doc-type').index()).data();
        var document_number = $('#transaction-table').DataTable().cell($.adjustment_active_row, $('#trs-doc-num').index()).data();
        var net_balance = $('#transaction-table').DataTable().cell($.adjustment_active_row, $('#trs-net-amount').index()).data();
        var row_number = $.adjustment_active_row + 1;

        $('#adjustment_customer_number').val(customer_code);
        $('#adjustment_customer_name').val(customer_name);
        $('#adjustment_document_type').val(document_type);
        $('#adjustment_document_number').val(document_number);
        $('#adjustment_document_entry_number').val(row_number);
        $('#adjustment_currency').val(customer_currency);
        $('#adjustment_net_balance').val(net_balance);
        initial_net_balance[$.adjustment_active_row] = net_balance;

        if (json_data) {
            json_data = $.parseJSON(json_data);

            $.adjustment_data[$.adjustment_active_row] = {
                'id' : json_data.id,
                'doc_no': json_data.doc_no,
                'reference' : json_data.reference,
                'description' : json_data.description,
                'transactions' : json_data.transactions
            }

        }

        if ($.adjustment_data[$.adjustment_active_row] === undefined) {
            $.adjustment_data[$.adjustment_active_row] = {
                'doc_no' : '',
                'reference' : '',
                'description' : '',
                'transactions' : []
            }
        }

        $('#adjustment_entry_number').val($.adjustment_data[$.adjustment_active_row].doc_no);
        $('#adjustment_reference').val($.adjustment_data[$.adjustment_active_row].reference);
        $('#adjustment_description').val($.adjustment_data[$.adjustment_active_row].description);

        if ($('#adjustment_reference').val() == '') {
            $('#adjustment_reference').val($('#id_reference').val());
        }

        if ($('#adjustment_description').val() == '') {
            $('#adjustment_description').val($('#id_name').val());
        }

        $.reloadTableAdjustmentTransaction($.adjustment_active_row);
    });

    $('#tableAdjustmentModal').off('hide.bs.modal').on('hide.bs.modal', function (e) {
        var is_error = false;

        $('#tableAdjustmentTransaction tbody tr').each(function(){
            var $adj_acc = $(this).find('.adj_acc');

            if (parseInt($adj_acc.val()) == 0) {
                $('#tableAdjustmentTransaction tbody tr').each(function() {
                    $adj_acc.closest('td').find('.select2-selection').css('border-color','#f00');
                });

                $(this).find('.deleteAdjustmentTransaction').trigger('click');

                // is_error = true;
            }
        });

        if (is_error) {
            e.preventDefault();

            return false;
        }

        $.adjustment_data[$.adjustment_active_row].reference = $('#adjustment_reference').val();
        $.adjustment_data[$.adjustment_active_row].description = $('#adjustment_description').val();

        var $trx_table = $('#transaction-table').DataTable();
        var adjustment = $.calculateAdjustment($.adjustment_active_row);

        $('#transaction-table').DataTable().cell($.adjustment_active_row, $('#trs-net-amount').index()).data($.calculateNetbalance($.adjustment_active_row).toFixed(2));
        $('#transaction-table').DataTable().cell($.adjustment_active_row, 14).data(JSON.stringify($.adjustment_data[$.adjustment_active_row]));

        $.adjustment_active_row = 0;
        $.adjustment_active_invoice_id = 0;
        // setTimeout(() => {
        //     checkValue($.adjustment_active_row);
        // }, 300);
        
    });

    $('#btnAddAdjustmentTransaction').off('click').on('click', function (e) {
        $.adjustment_data[$.adjustment_active_row].transactions.push({
            'distribution_code_id': '',
            'account_id': '',
            'account_name': '',
            'reference': '',
            'description': '',
            'debit': '',
            'credit': '',
        });

        $.reloadTableAdjustmentTransaction($.adjustment_active_row);
    });

    var invoice_transactions = $.loadInvoiceTransactions($.adjustment_active_invoice_id, function(transactions) {
        $('#tableAdjustmentModal').modal('show');
    });
}

$.deleteAdjustmentTransaction = function() {

}

$.reloadTableAdjustmentTransaction = function(row) {
    var tableData = [];

    if ($.fn.DataTable.isDataTable('#tableAdjustmentTransaction')) {
        $('#tableAdjustmentTransaction').DataTable().destroy();
    }

    if ($.adjustment_data[row] === undefined) {
        $.adjustment_data[row] = {
            'reference' : '',
            'description' : '',
            'transactions' : []
        }
    }

    $.each($.adjustment_data[row].transactions, function(k, v) {
        var select_accounts = '', select_lines = '', select_dist_codes = '';

        // select_lines = '<option value="0" data-row="">Select Line</option>';

        $.each($.invoiceTransactions[$.adjustment_active_invoice_id], function(k, row) {
            select_lines += '<option value="'+row.line_number+'" '+((v.transaction_id == row.id) ? 'selected="selected"' : '')+' data-row=\''+JSON.stringify(row)+'\'>'+row.line_number+'</option>';
        });

        select_dist_codes = '<option value="0" data-gl-account-id="">Select Dist. Code</option>';

        $.each($.dist_code_list, function(k, row) {
            select_dist_codes += '<option value="'+row.id+'" '+((v.distribution_code_id == row.id) ? 'selected="selected"' : '')+' data-gl-account-id="'+row.gl_account_id+'">'+row.code+'</option>';
        });

        select_accounts = '<option value="0" data-name="">Select Account</option>';

        $.each($.account_list, function(k, row) {
            select_accounts += '<option value="'+row.id+'" '+((v.account_id == row.id) ? 'selected="selected"' : '')+' data-name="'+row.name+'">'+row.code+'</option>';
        });

        tableData.push([
            '<button type="button" class="btn btn-sm deleteAdjustmentTransaction"><i class="fa fa-minus"></i></button>',
            '<select class="adj_line adj_input">'+select_lines+'</select>',
            '<select class="adj_dist adj_input">'+select_dist_codes+'</select>' +
            '<button id="" style="font-size: 10px; padding: 0px;" type="button" class="btn btn-info sended" data-toggle="modal" onclick="showAdjDistributionModal()"><i class="fa fa-search"></i></button>',
            '<select class="adj_acc adj_input">'+select_accounts+'</select>',
            '<input type="text" class="form-control adj_acc_desc adj_input" value="'+v.account_name+'" readonly="readonly">',
            '<input type="text" class="form-control adj_reference adj_input" value="'+v.reference+'">',
            '<input type="text" class="form-control adj_description adj_input" value="'+v.description+'">',
            '<input type="text" class="form-control adj_debit adj_input" value="'+(v.debit > 0 ? float_format(v.debit).toFixed(2) : '')+'">',
            '<input type="text" class="form-control adj_credit adj_input" value="'+(v.credit > 0 ? float_format(v.credit).toFixed(2) : '')+'">',
        ]);
    });

    $('#tableAdjustmentTransaction').DataTable({
        'searching': false,
        'paging': false,
        'ordering': false,
        'responsive': true,
        'scrollCollapse': true,
        'scrollX': true,
        'data': tableData,
        'initComplete': function(settings, json) {

            $('#tableAdjustmentTransaction').find('select.adj_line').each(function () {
                $(this).select2({
                    'placeholder': 'Select Line',
                    'dropdownParent': $('#tableAdjustmentModal'),
                });
            });

            $('#tableAdjustmentTransaction').find('select.adj_dist').each(function () {
                $(this).select2({
                    'placeholder': 'Select Dist. Code',
                    'dropdownParent': $('#tableAdjustmentModal'),
                });
            });

            $('#tableAdjustmentTransaction').find('select.adj_acc').each(function () {
                $(this).select2({
                    'placeholder': 'Select Account',
                    'dropdownParent': $('#tableAdjustmentModal'),
                });
            });

            $('#tableAdjustmentTransaction select.adj_line').on('change', function() {
                var $row = $(this).closest('tr');

                if ($(this).find('option:selected').attr('data-row') == '') {
                    return;
                }
                try{
                    var $trx_data = $(this).find('option:selected').attr('data-row');

                    $row.find('.adj_acc').val($trx_data.account_id);
                    $row.find('.adj_acc_desc').val($trx_data.account_name);
                    $row.find('.adj_reference').val($trx_data.reference);
                    $row.find('.adj_description').val($trx_data.description);
                    $row.find('.adj_debit').val($trx_data.is_credit_account ? float_format(initial_net_balance[$.adjustment_active_row]).toFixed(2) : '');
                    $row.find('.adj_credit').val($trx_data.is_debit_account ? float_format(initial_net_balance[$.adjustment_active_row]).toFixed(2) : '');

                    $row.find('.adj_dist').trigger('change');
                    $row.find('.adj_dist').trigger('select2:select');
                    $row.find('.adj_acc').trigger('change');
                    $row.find('.adj_acc').trigger('select2:select');
                    $row.find('.adj_dist').val($trx_data.distribution_code_id);
                } catch(e){
                    console.log(e);
                }
            });

            $('#tableAdjustmentTransaction select.adj_dist').on('select2:select', function() {
                var $row = $(this).closest('tr');
                var $line = $row.find('select.adj_line');

                if ($line.val() && $line.val() != '0' && $line.find('option:selected').attr('data-row') != '') {
                    var $trx_data = $.parseJSON($line.find('option:selected').attr('data-row'));

                    if ($trx_data.distribution_code_id != $(this).val()) {
                        $line.val('0');

                        $line.trigger('change');
                        $line.trigger('select2:select');
                    }
                }

                if ($(this).val() && $(this).val() != '0') {
                    $row.find('.adj_acc').val($(this).find('option:selected').attr('data-gl-account-id'));
                    $row.find('.adj_acc').trigger('change');
                    $row.find('.adj_acc').trigger('select2:select');
                }
            });

            $('#tableAdjustmentTransaction select.adj_acc').on('select2:select', function() {
                var $row = $(this).closest('tr');
                var $line = $row.find('select.adj_line');
                var $dist = $row.find('select.adj_dist');

                if ($dist.val() && $dist.val() != '0' && $dist.find('option:selected').attr('data-gl-account-id') != $(this).val()) {
                    $dist.val('0');

                    $dist.trigger('change');
                    $dist.trigger('select2:select');
                }

                $row.find('.adj_acc_desc').val($(this).find('option:selected').attr('data-name'));
            });

            $('.deleteAdjustmentTransaction').on('click', function() {
                var trx_index = $(this).closest('tr').index();
                if(trx_index == 0) {
                    $('#adjustment_net_balance').val(initial_net_balance[$.adjustment_active_row]);
                    $('#transaction-table').DataTable().cell($.adjustment_active_row, 6).data(float_format(0).toFixed(2));
                }

                $.adjustment_data[$.adjustment_active_row].transactions.splice(trx_index, 1);

                $.reloadTableAdjustmentTransaction($.adjustment_active_row);
            });

            $('#tableAdjustmentTransaction select, #tableAdjustmentTransaction input[type="text"]').on('change', function() {
                var trx_index = $(this).closest('tr').index();
                var $row = $(this).closest('tr');
                var trx_id = 0;

                $row.find('.adj_acc').closest('td').find('.select2-selection').css('border-color','inherit');

                if ($.adjustment_data[$.adjustment_active_row].transactions[trx_index].id !== undefined) {
                    trx_id = $.adjustment_data[$.adjustment_active_row].transactions[trx_index].id;
                }

                $.adjustment_data[$.adjustment_active_row].transactions[trx_index] = {
                    'transaction_id': $row.find('.adj_line').val(),
                    'distribution_code_id': $row.find('.adj_dist').val(),
                    'account_id': $row.find('.adj_acc').val(),
                    'account_name': $row.find('.adj_acc_desc').val(),
                    'reference': $row.find('.adj_reference').val(),
                    'description': $row.find('.adj_description').val(),
                    'debit': $row.find('.adj_debit').val(),
                    'credit': $row.find('.adj_credit').val(),
                };

                if (trx_id != 0) {
                    $.adjustment_data[$.adjustment_active_row].transactions[trx_index].id = trx_id;
                }

                var adjustment = $.calculateAdjustment($.adjustment_active_row, $.adjustment_active_invoice_id);

                $('#transaction-table').DataTable().cell($.adjustment_active_row, 6).data(float_format(adjustment).toFixed(2));

                $.initBtnAdjustmentTransaction();

                $('#adjustment_net_balance').val($.calculateNetbalance($.adjustment_active_row).toFixed(2));

                $('#tableAdjustmentTransaction').DataTable().draw();
            });
        }
    });

    $('#tableAdjustmentTransaction select').trigger('select2:select');

    $('#tableAdjustmentTransaction').DataTable().columns.adjust();

    setTimeout(function() {
        $('#tableAdjustmentTransaction').DataTable().draw();
    }, 300);
}

function showAdjDistributionModal() {
    loadDistributionAjax();
    $("#tableDistributionModal").modal("show");
}

function loadDistributionAjax() {
    distribution_code.length = 0;
    $('#distribution-table').DataTable().destroy();
    $('#distribution-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[1, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": "/accounts/dist-code/list/pagination/1/" /* DIS_CODE_TYPE['AR Distribution Code'] */
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "gl_account", "sClass": "text-left"},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, full, meta) {
                    if (full.is_active == 'True' && full.id != $("#distribution_id").val()) {
                        distribution_code.push(full);
                        return '<input type="radio" name="choices_distribution" class="call-checkbox" onclick="selectDistribution(\'' + full.id + '\',\'' + full.code + '\',\'' + full.name + '\',\'' + full.account_id + '\',\'' + full.account_code + '\',\'' + full.account_name + '\')" value="' + full.id + '">';
                    }
                    return "";
                }
            }
        ]
    });

    setTimeout(() => {
        $('#distribution-table').DataTable().columns.adjust();
    }, 300);
}

$.calculateNetbalance = function(row, pending_balance) {
    var $trx_table = $('#transaction-table').DataTable();

    var i_col_pending = $('#trs-out-amount').index();
    var i_col_original = $('#trs-doc-amount').index();
    var i_col_applied = $('#trs-apply-amount').index();
    var i_col_discount = $('#trs-discount').index();
    var i_col_adjustment = $('#trs-adjustment').index();

    var original_amount = 0;
    var pending_amount = 0;
    var applied_amount = 0;
    var discount_amount = 0;
    var adjustment_amount = 0;
    try{
        original_amount = float_format($trx_table.cell(row, i_col_original).data().replace(',', ''));
    } catch(e) {
        
    }
    try{
        applied_amount = float_format($trx_table.cell(row, i_col_applied).node().firstChild.value.replace(',', ''));
    } catch(e) {
    }
    try{
        pending_amount = float_format($trx_table.cell(row, i_col_pending).data().replace(',', ''));
    } catch(e) {

    }
    try{
        discount_amount = float_format($trx_table.cell(row, i_col_discount).node().firstChild.value.replace(',', ''));
    } catch(e) {
    }
    try{
        adjustment_amount = float_format($trx_table.cell(row, i_col_adjustment).data());
    } catch(e) {

    }
    
    var old_discount_amount = float_format($.old_discount[row]);

    original_amount = (isNaN(original_amount)) ? 0 : original_amount;
    pending_amount = (isNaN(pending_amount)) ? 0 : pending_amount;
    applied_amount = (isNaN(applied_amount)) ? 0 : applied_amount;
    discount_amount = (isNaN(discount_amount)) ? 0 : discount_amount;
    adjustment_amount = (isNaN(adjustment_amount)) ? 0 : adjustment_amount;
    old_discount_amount = (isNaN(old_discount_amount)) ? 0 : old_discount_amount;

    if (pending_balance === undefined) pending_balance = 0;

    return float_format(original_amount - applied_amount + adjustment_amount - discount_amount);
}

$.calculateAdjustment = function(row, invoice_id) {
    if (!$.adjustment_data[row]) {
        return 0;
    }

    var adjustment = 0, debit = 0, credit = 0;

    $.each($.adjustment_data[row].transactions, function(k, v) {
        debit = float_format(v.debit);
        credit = float_format(v.credit);

        if (isNaN(debit)) debit = 0;
        if (isNaN(credit)) credit = 0;

        adjustment -= debit;
        adjustment += credit;
    });

    return float_format(adjustment);
}

$.loadInvoiceTransactions = function(invoice_id, callback) {
    if (!invoice_id) {
        return [];
    }

    if ($.invoiceTransactions[invoice_id] === undefined) {
        $.getJSON(
            url_Load_Invoice_transactions,
            { journal_id: invoice_id },
            function(data) {
                $.invoiceTransactions[invoice_id] = data;

                $.loadInvoiceTransactions(invoice_id, callback);
            }
        );
    }
    else {
        if (callback !== undefined) {
            if ($.isArray(callback)) {
                $.each(callback, function(fnCallback) {
                    var fn = window[fnCallback];

                    // is object a function?
                    if (typeof fn === "function") fn($.invoiceTransactions[invoice_id]);
                });
            } else if (typeof callback === "function") {
                callback($.invoiceTransactions[invoice_id]);
            } else {
                var fn = window[callback];

                // is object a function?
                if (typeof fn === "function") fn($.invoiceTransactions[invoice_id]);
            }
        }
    }

    return $.invoiceTransactions[invoice_id];
}

function deletePaymentTransaction(row) {
    var table = $('#transaction-table').DataTable();
    var value = float_format($('#appliedAmount-' + row).val());
    var doc_type = table.cell(row, $("#trs-doc-type").index()).data();
    var total_amount = $("#id_total_amount").val();
    var new_total_amount = 0;
    if (doc_type == 'Credit Note' || doc_type == 'Unapplied Cash' || doc_type == 'Receipt'){
        new_total_amount =  float_format(total_amount) + (float_format(value) * float_format(supp_bank_exch_rate));
    } else {
        new_total_amount =  float_format(total_amount) - (float_format(value) * float_format(supp_bank_exch_rate));
    }
    var new_customer_amount = float_format($("#id_original_amount").val()) - float_format(value);
    if(bank_is_decimal) {
        $("#id_total_amount").val(comma_format(new_total_amount)).trigger('change');
    } else {
        $("#id_total_amount").val(comma_format(new_total_amount, 0)).trigger('change');
    }
    // $("#id_payment_amount").val(comma_format(new_total_amount));
    // $("#id_original_amount").val(comma_format(new_customer_amount));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }

    table.row(row).remove().draw();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.id = 'appliedAmount-' + rowIdx;
        $('#appliedAmount-' + rowIdx).attr("onchange", "checkValue(" + rowIdx + ")");
        var is_delete = table.row(rowIdx).data()[12];
        row = parseInt(row);
        if (rowIdx >= row) {
            if (is_delete != '') {
                $("#removerow" + (rowIdx+1)).attr("onclick", "openDeleteConfirmDialog(" + rowIdx + ")");
                $("#removerow" + (rowIdx+1)).attr("id", "removerow" + rowIdx);
                $("#adjustrow" + (rowIdx+1)).attr("id", "adjustrow" + rowIdx);
            } else {
                $("#removerow" + (rowIdx+1)).attr("onclick", "deletePaymentTransaction(" + rowIdx + ")");
                $("#removerow" + (rowIdx+1)).attr("id", "removerow" + rowIdx);
                $("#adjustrow" + (rowIdx+1)).attr("id", "adjustrow" + rowIdx);
            }
            if ($.adjustment_data[(rowIdx+1)]) {
                $.adjustment_data[rowIdx] = $.adjustment_data[(rowIdx+1)];
            }
        }
    });

    if (table.rows().count() == 0) {
        console.log('ZERO ROWS');
        $('#id_receipt_unapplied').val($('#id_payment_amount').val());
        $('#id_customer_unapplied').val($('#id_original_amount').val());
    }
};

function TransactionDetail() {
    this.document_number = null;
    this.document_type = null;
    this.payment_number = null;
    this.pending_balance = null;
    this.applied_amount = null;
    this.net_balance = null;
    this.original_amount = null;
    this.document_date = null;
    this.due_date = null;
    this.invoice_id = null;
    this.is_delete = null;
    this.adjustments = [];
}

var allVals = new Array;

function deletePaymentTransactionInEdit(row) {
    var table = $('#transaction-table').DataTable();
    var doc_type = table.cell(row, $("#trs-doc-type").index()).data();
    var amount = float_format($('#appliedAmount-' + row).val());
    var total_amount = $("#id_total_amount").val();
    var button = $('#btnDeleteInEdit-' + row);
    table.row(row).data()[12] = '1';
    var new_total_amount = 0;
    if (doc_type == 'Credit Note' || doc_type == 'Unapplied Cash' || doc_type == 'Receipt'){
        new_total_amount =  float_format(total_amount) + (float_format(amount) * float_format(supp_bank_exch_rate));
    } else {
        new_total_amount =  float_format(total_amount) - (float_format(amount) * float_format(supp_bank_exch_rate));
    }
    var new_customer_amount = float_format($("#id_original_amount").val()) - float_format(amount);
    if(bank_is_decimal) {
        $("#id_total_amount").val(comma_format(new_total_amount)).trigger('change');
    } else {
        $("#id_total_amount").val(comma_format(new_total_amount, 0)).trigger('change');
    }
    // $("#id_payment_amount").val(comma_format(new_total_amount));
    // $("#id_original_amount").val(comma_format(new_customer_amount));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }
    var row_data = table.row(row).data();
    var applied_amount_index = $('#transaction-table').dataTable().fnGetNodes();
    var transaction = new TransactionDetail();
    transaction.document_number = row_data[0];
    transaction.document_type = row_data[1];
    transaction.payment_number = row_data[2];
    transaction.pending_balance = row_data[3];
    transaction.applied_amount = applied_amount_index[row].cells[4].firstChild.value;
    transaction.discount_amount = applied_amount_index[row].cells[5].firstChild.value;
    transaction.adjustment_amount = applied_amount_index[row].cells[6].value;
    transaction.net_balance = row_data[7];
    transaction.original_amount = row_data[8];
    transaction.document_date = row_data[9];
    transaction.due_date = row_data[10];
    transaction.invoice_id = row_data[11];
    transaction.is_delete = row_data[12];
    transaction.adjustments = ($.adjustment_data[row] !== undefined) ? $.adjustment_data[row] : [];
    allVals.push(transaction);
    table.row(row).remove().draw();

    if ($.adjustment_data[row] !== undefined ) {
        $.adjustment_data[row] = undefined;
    }

    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.id = 'appliedAmount-' + rowIdx;
        var is_delete = table.row(rowIdx).data()[12];
        row = parseInt(row);
        if (rowIdx >= row) {
            if (is_delete != '') {
                $("#removerow" + (rowIdx+1)).attr("onclick", "openDeleteConfirmDialog(" + rowIdx + ")");
                $("#removerow" + (rowIdx+1)).attr("id", "removerow" + rowIdx);
                $("#adjustrow" + (rowIdx+1)).attr("id", "adjustrow" + rowIdx);
            } else {
                $("#removerow" + (rowIdx+1)).attr("onclick", "deletePaymentTransaction(" + rowIdx + ")");
                $("#removerow" + (rowIdx+1)).attr("id", "removerow" + rowIdx);
                $("#adjustrow" + (rowIdx+1)).attr("id", "adjustrow" + rowIdx);
            }
            if ($.adjustment_data[(rowIdx+1)]) {
                $.adjustment_data[rowIdx] = $.adjustment_data[(rowIdx+1)];
            }
        }
    });
};

function openDeleteConfirmDialog(row) {
    var transaction_type = $('#id_transaction_type').val();
    $("#delete-transactiob-dialog").modal("show");
    if (parseInt(transaction_type) == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
        $("#delete-transactiob-dialog button[type='button']").attr('onclick', 'deletePaymentTransactionInEdit(' + row + ');');
    } else {
        $("#delete-transactiob-dialog button[type='button']").attr('onclick', 'deleteTransactionRowOnEditMode(' + row + ');');
    }
};

function storeListTransactions() {
    var array = [];
    $('#listTrans').val(JSON.stringify(array));
    var transaction_type = $('#id_transaction_type').val();
    if (parseInt(transaction_type) == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
        var amount_list = [];
        $("input[name='appliedAmount']").each(function () {
            amount_list.push($(this).val());
        });
        if (validatePayment(transaction_type) == 0) {
            datatbl = $('#transaction-table').DataTable();
            var applied_amount_index = $('#transaction-table').dataTable().fnGetNodes();
            var rows = $('#transaction-table').dataTable().fnGetData();
            for (var i = 0; i < rows.length; i++) {
                //if (typeof($.adjustment_data[i]) === 'undefined') continue;
                if (typeof($.adjustment_data[i]) !== 'undefined' && $.adjustment_data[i] != undefined) {
                    var idx = 1;
                    $.each($.adjustment_data[i].transactions, function(k, v) {
                        if (typeof($.adjustment_data[i].transactions[k].id) !== 'undefined' && $.adjustment_data[i].transactions[k].id != undefined && parseInt($.adjustment_data[i].transactions[k].id) > 0) {
                            $.adjustment_data[i].transactions[k].id = $.adjustment_data[i].transactions[k].id.toString();
                        } else {
                            $.adjustment_data[i].transactions[k].id = idx.toString();
                        }
                        if (typeof($.adjustment_data[i].transactions[k].transaction_id) !== 'undefined' && $.adjustment_data[i].transactions[k].transaction_id != undefined && parseInt($.adjustment_data[i].transactions[k].transaction_id) > 0) {
                            $.adjustment_data[i].transactions[k].transaction_id = $.adjustment_data[i].transactions[k].transaction_id.toString();
                        } else {
                            $.adjustment_data[i].transactions[k].transaction_id = idx.toString();
                        }
                        $.adjustment_data[i].transactions[k].distribution_code_id = ($.adjustment_data[i].transactions[k].distribution_code_id !== null) ? $.adjustment_data[i].transactions[k].distribution_code_id.toString() : '0';
                        $.adjustment_data[i].transactions[k].debit = $.adjustment_data[i].transactions[k].debit.toString();
                        $.adjustment_data[i].transactions[k].credit = $.adjustment_data[i].transactions[k].credit.toString();
                        $.adjustment_data[i].transactions[k].account_id = $.adjustment_data[i].transactions[k].account_id.toString();

                        idx += 1;
                    });
                }
                var transaction = new TransactionDetail();
                transaction.document_number = rows[i][0];
                transaction.document_type = rows[i][1];
                transaction.payment_number = rows[i][2];
                transaction.pending_balance = rows[i][3];
                transaction.applied_amount = applied_amount_index[i].cells[4].firstChild.value; // index 4 = Applied Amount
                transaction.discount_amount = applied_amount_index[i].cells[5].firstChild.value; // index 5 = Discount
                transaction.adjustment_amount = $.calculateAdjustment(i).toString();
                transaction.net_balance = rows[i][7];
                transaction.original_amount = rows[i][8];
                transaction.document_date = rows[i][9];
                transaction.due_date = rows[i][10];
                transaction.invoice_id = rows[i][11].toString();
                transaction.is_delete = rows[i][12];
                if(typeof($.adjustment_data[i]) !== 'undefined' && $.adjustment_data[i] != undefined){
                    transaction.adjustments = $.adjustment_data[i];
                } else{
                    transaction.adjustments = [];
                }
                window.allVals.push(transaction);
            }

            $('#listTrans').val(JSON.stringify(window.allVals));

        } else {
            $('#loading').hide();
            return false;
        }
    } else if (parseInt(transaction_type) == RECEIPT_TRANSACTION_TYPES_MISC_RECEIPT) {
        datatbl = $('#misc-transaction-table').DataTable();
        var applied_amount_index = $('#misc-transaction-table').dataTable().fnGetNodes();
        var rows = $('#misc-transaction-table').dataTable().fnGetData();
        // allVals = []
        for (var i = 0; i < rows.length; i++) {
            var transaction = new Transaction();
            transaction.line = String(rows[i][0]);
            transaction.distribution_code = rows[i][1] || '';
            transaction.description = filter_special_char(rows[i][2]);
            transaction.account_code = rows[i][3];
            transaction.account_name = filter_special_char(rows[i][4]);
            transaction.amount = rows[i][5];
            transaction.tax_amount = rows[i][6];
            transaction.total_amount = rows[i][7];
            transaction.trans_id = rows[i][8];
            transaction.distribution_id = rows[i][9] || '';
            transaction.account_id = rows[i][10];
            transaction.is_tax_included = String(rows[i][11]);
            transaction.is_tax_transaction = String(rows[i][12]);
            transaction.tax_id = rows[i][13];
            transaction.is_manual_tax_input = rows[i][14];
            transaction.base_tax_amount = rows[i][15];
            transaction.is_delete = rows[i][16];
            transaction.row_number = '';
            window.allVals.push(transaction);
        }
        $('#listTrans').val(JSON.stringify(window.allVals));
    } if (parseInt(transaction_type) == RECEIPT_TRANSACTION_TYPES_UNAPPLIED_CASH) {
        var pay_value = $('#id_payment_amount').val();
        if(float_format(pay_value) <= 0.0) {
            return false;
        }
    }

    if('True' == is_rec_entry){
        var s_date = $('#start_date').val().split('-');
        if (s_date[0].length == 2)
            $('#start_date').val(moment($('#start_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        if ($('#expire_date').val()){
            var e_date = $('#expire_date').val().split("-");
            if (e_date[0].length == 2)
                $('#expire_date').val(moment($('#expire_date').val().split("-").reverse().join("-"), "YYYY-MM-DD").format("YYYY-MM-DD"));
        }
    }

    setTimeout(function(){
        $('#btnSave').prop('disabled', true);
    }, 100);

    return true;
}

$(document).on('change keypress', 'input', function() {
    $('#btnSave').prop('disabled', false);
});

$(document).on('change', 'select', function() {
    $('#btnSave').prop('disabled', false);
});


$('#form').on('submit', function (e) {
    // var payment_amount = float_format($("#id_original_amount").val());
    // var trx_total = 0;
    // var table = $('#transaction-table').DataTable();
    // var transaction_type = $('#id_transaction_type').val();
    // if (parseInt(transaction_type) == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
    //     $('#transaction-table tbody tr').each(function() {
    //         try {
    //             var i_col_applied = $('#trs-apply-amount').index();
    //             var i_col_discount = $('#trs-discount').index();
    //             var i_col_adjustment = $('#trs-adjustment').index();
    //             var row = $(this).index();
    //             var doc_type = table.cell(row, $("#trs-doc-type").index()).data();
                
    //             appliedAmount = float_format(table.cell(row, i_col_applied).node().firstChild.value.replace(',', ''));
    //             if (isNaN(appliedAmount)) {
    //                 appliedAmount = float_format(0);
    //             }

    //             discountAmount = float_format(table.cell(row, i_col_discount).node().firstChild.value.replace(',', ''));
    //             if (isNaN(discountAmount)) {
    //                 discountAmount = float_format(0);
    //             }

    //             // adjustmentAmount = float_format(table.cell(row, i_col_adjustment).data());
    //             // if (isNaN(adjustmentAmount)) {
    //             //     adjustmentAmount = float_format(0);
    //             // }
    //             if (doc_type == 'Credit Note' || doc_type == 'Unapplied Cash' || doc_type == 'Receipt'){
    //                 trx_total -= (appliedAmount - discountAmount)
    //             } else {
    //                 trx_total += (appliedAmount - discountAmount)
    //             }
    //         } catch (e) {
    //             console.log(e)
    //         }
    //     });
    //     trx_total = float_format(comma_format(trx_total));
    //     if (trx_total > payment_amount) {
    //         $('#save_error').text('Customer amount is less than applied total. Please reduce the applied amount.');
    //         e.preventDefault();
    //         $('#loading').hide();
    //     }
    //     else if ($('#id_exchange_rate').val() == "") {
    //         pop_ok_dialog("Invalid Exchange Rate",
    //             "Please enter a valid Exchange Rate",
    //             function () { e.preventDefault(); $('#loading').hide();}
    //         );
    //         e.preventDefault();
    //         $('#loading').hide();
    //         $('#save_error').text('');
    //     } else {
    //         $('#save_error').text('');
    //         if (!storeListTransactions()) {
    //             e.preventDefault();
    //             $('#loading').hide();
    //         }
    //     }
    // } else {
    //     if ($('#id_exchange_rate').val() == "") {
    //         pop_ok_dialog("Invalid Exchange Rate",
    //             "Please enter a valid Exchange Rate",
    //             function () { e.preventDefault(); $('#loading').hide();}
    //         );
    //         e.preventDefault();
    //         $('#loading').hide();
    //         $('#save_error').text('');
    //     } else {
    //         $('#save_error').text('');
    //         if (!storeListTransactions()) {
    //             e.preventDefault();
    //             $('#loading').hide();
    //         }
    //     }
    // }
    if ($('#id_exchange_rate').val() == "") {
        pop_ok_dialog("Invalid Exchange Rate",
            "Please enter a valid Exchange Rate",
            function () { e.preventDefault(); $('#loading').hide();}
        );
        e.preventDefault();
        $('#loading').hide();
        $('#save_error').text('');
    } else {
        $('#save_error').text('');
        if (!storeListTransactions()) {
            e.preventDefault();
            $('#loading').hide();
        }
    }
});


$("#id_distribution_code").on('change', function () {
    name = $(this).find(':selected').data('name');
    if (name != 'undefined') {
        $('#distribution_desc').val(name);
        $("#description").val(filter_special_char(name));
    } else {
        $("#distribution_desc").val('');
        $("#description").val('');
        $('#id_account_code').val('').trigger('change');
    }
});

$("#id_account_code").on('change', function () {
    name = $(this).find(':selected').data('name');
    if (name != 'undefined') {
        $('#account_desc').val(filter_special_char(name));
    } else {
        $('#account_desc').val('');
    }
});

function selectDistribution(id, code, name, account_id, account_code, account_name) {
    $("#distribution_id").val(id);
    $("#distribution_code").val(code);
    $("#distribution_desc").val(name);
    $("#account_id_trs").val(account_id);
    $("#account_code").val(account_code);
    $("#account_desc").val(filter_special_char(account_name));
    $("#id_distribution_code").val(id).change();
    $("#id_account_code").val(account_id).change();

    $('.adj_dist').val(id).change();
}


function selectAccount(id, code, name) {
    // $("#distribution_id").val("");
    // $("#distribution_code").val("");
    // $("#distribution_desc").val("");
    $("#account_id_trs").val(id);
    $("#account_code").val(code);
    $("#account_desc").val(filter_special_char(name));
    // $("#id_distribution_code").val("").change();
    $("#id_account_code").val(id).change();

}

var distribution_code = [];

$('#distribution-table').on( 'draw.dt', function () {
    $('#distribution-table tbody tr').bind('click', function () {
        var radio_td = $(this).find('td').eq(3);
        var radio = $(radio_td).find('input').eq(0);
        var code_id = $(radio).val();
        $(radio).prop("checked", true);
        distribution_code.forEach(element => {
            if (element.id == code_id) {
                selectDistribution(element.id, element.code, element.name, element.account_id, element.account_code, element.account_name);
            }
        });

        $("input[type='radio']:not(:checked)").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
        $("input[type='radio']:checked").each(function () {
            $(this).closest('tr').css('background-color', '#3ff3f3');
        });
    });
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});


$('#btnSearchDistribution').on('click', function () {
    distribution_code.length = 0;
    $('#distribution-table').DataTable().destroy();
    $('#distribution-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[1, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": url_DistributionCode__asJson,
        },
        "columns": [
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "gl_account", "sClass": "text-left"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    if (full.is_active == 'True' && full.id != $("#distribution_id").val()) {
                        distribution_code.push(full);
                        return '<input type="radio" name="choices_distribution" class="call-checkbox" onclick="selectDistribution(\'' + full.id + '\',\'' + full.code + '\',\'' + full.name + '\',\'' + full.account_id + '\',\'' + full.account_code + '\',\'' + full.account_name + '\')" value="' + full.id + '">';
                    }
                    return "";
                }
            }
        ]
    });
    setTimeout(() => {
        $('#distribution-table').DataTable().columns.adjust();
    }, 300);
});

$('#account-table-trs').on( 'draw.dt', function () {
    $('#account-table-trs tbody tr').bind('click', function () {
        var code = $(this).find('td').eq(0).text();
        var name = $(this).find('td').eq(1).text();
        var radio_td = $(this).find('td').eq(6);
        var radio = $(radio_td).find('input').eq(0);
        var acc_id = $(radio).val();
        $(radio).prop("checked", true);
        selectAccount(acc_id, code, name);

        $("input[type='radio']:not(:checked)").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
        $("input[type='radio']:checked").each(function () {
            $(this).closest('tr').css('background-color', '#3ff3f3');
        });
    });
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});


$('#btnSearchAccount').on('click', function () {
    $('#account-table-trs').DataTable().destroy();
    $('#account-table-trs').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[1, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": "/accounts/list/pagination/"
        },
        "columns": [
            {"data": "code"},
            {"data": "name"},
            {"data": "account_type"},
            {"data": "balance_type"},
            {"data": "amount", "orderable": false},
            {"data": "account_group"},
            // {"data": "Company_name"},
            // {
            //     "orderable": false,
            //     "data": null,
            //     "render": function (data, type, full, meta) {
            //         if (full.is_active == 'True') {
            //             var mSpan = '<span class="label label-success label-mini">True</span>';
            //             return mSpan;
            //         }
            //         else {
            //             var mSpan = '<span class="label label-danger label-mini">False</span>';
            //             return mSpan;
            //         }
            //     }
            // },
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    if (full.is_active == 'True' && full.id != $("#account_id_trs").val()) {
                        return '<input type="radio" name="choices_account" class="call-checkbox" onclick="selectAccount(\'' + full.id + '\',\'' + full.code + '\',\'' + full.name + '\')" value="' + full.id + '">';
                    }
                    return "";
                }
            }
        ]
    });
    setTimeout(() => {
        $('#account-table-trs').DataTable().columns.adjust();
    }, 300);
});

// Define class Misc Transaction
function Transaction() {
    this.line = null;
    this.distribution_id = null;
    this.distribution_code = null;
    this.account_id = null;
    this.account_code = null;
    this.account_name = null;
    this.description = null;
    this.amount = null;
    this.tax_amount = null;
    this.total_amount = null;
    this.is_tax_included = null;
    this.is_tax_transaction = null;
    this.tax_id = null;
    this.is_manual_tax_input = null;
    this.base_tax_amount = null;
    this.is_delete = null;
    this.trans_id = null;
    this.row_number = null;
}

$("#tax-only-checkbox").on('change', function () {
    taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    if (taxOnly > 0) {
        $('#tax-checkbox').prop('checked', false);
        $('#tax-checkbox').prop('disabled', true);
        $('#manual-tax').prop('checked', true).trigger('change');
    } else {
        $('#tax-checkbox').prop('disabled', false);
    }
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});

$("#tax-checkbox").on('change', function () {
    taxincl = $('#tax-checkbox:checkbox:checked').length;
    if (taxincl > 0) {
        $('#tax-only-checkbox').prop('checked', false);
        $('#tax-only-checkbox').prop('disabled', true);
    } else {
        $('#tax-only-checkbox').prop('disabled', false);
    }
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});


$('#id_tax').on('change', function(){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        if ($('#id_tax').val() && $('#id_tax').val() != '0'){

            if ($('#tax-checkbox:checkbox:checked').length > 0) {
                $('#tax-only-checkbox').attr('disabled', true);
            }else {
                $('#tax-only-checkbox').attr('disabled', false);
            }

            if ($('#tax-only-checkbox:checkbox:checked').length > 0) {
                $('#tax-checkbox').attr('disabled', true);
            } else {
                $('#tax-checkbox').attr('disabled', false);
            }

            $('#manual-tax').attr('disabled', false);
        } else {
            $('#tax-checkbox').attr('disabled', true);
            $('#tax-only-checkbox').attr('disabled', true);
            $('#manual-tax').attr('disabled', true);

            $('#amount').attr('disabled', false);
            $('#tax_amount').attr('disabled', true);
            $('#base_amount').attr('disabled', true);

            $('#tax-checkbox').prop('checked', false);
            $('#tax-only-checkbox').prop('checked', false);
            $('#manual-tax').prop('checked', false);
        }
    }
    // taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});


$("#manual-tax").on('change', function () {
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        $('#base_amount').prop('disabled', false);
        $('#tax_amount').prop('disabled', false);
    } else {
        $('#base_amount').prop('disabled', true);
        $('#tax_amount').prop('disabled', true);
        $('#amount').prop('disabled', false);
    }
});



$('#amount').on('change', function(e){
    taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    taxIncluded = $('#tax-checkbox:checkbox:checked').length;
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        amount = float_format($('#amount').val());
        s_tax = $('#id_tax').val();
        if (s_tax) {
            rate = float_format($('#id_tax').find(':selected').data('rate'));
        } else {
            rate = 0;
        }
        if (taxOnly > 0) {
            $('#base_amount').val(0.0);
            $('#tax_amount').val(comma_format(amount));
        } else {
            if(taxIncluded > 0) {
                rate = rate/100;
                $('#base_amount').val(comma_format((amount / (1+rate))));
                $('#tax_amount').val(comma_format(amount - float_format(comma_format(amount / (1+rate)))));
            } else {
                $('#base_amount').val(comma_format(amount));
                if(s_tax == 0){
                    $('#tax_amount').val(0.0);
                }else{
                    $('#tax_amount').val(comma_format((rate * amount) / 100));
                }
            }
        }
    }
    if(bank_is_decimal) {
        $('#amount').val(comma_format(float_format($('#amount').val())));
    } else {
        $('#amount').val(comma_format(float_format($('#amount').val()), 0));
        $('#base_amount').val(comma_format(float_format($('#base_amount').val()), 0));
        $('#tax_amount').val(comma_format(float_format($('#tax_amount').val()), 0));
    }
    $('#tax_report_amount').val(comma_format(float_format($('#tax_amount').val())*tax_reporting_rate));
});

$('#base_amount').on('change', function(e){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        if(bank_is_decimal) {
            $('#base_amount').val(comma_format(float_format($('#base_amount').val())));
        } else {
            $('#base_amount').val(comma_format(float_format($('#base_amount').val()), 0));
        }
    }
});

$('#tax_amount').on('change', function(e){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        if(bank_is_decimal) {
            $('#tax_amount').val(comma_format(float_format($('#tax_amount').val())));
        } else {
            $('#tax_amount').val(comma_format(float_format($('#tax_amount').val()), 0));
        }
        $('#tax_report_amount').val(comma_format(float_format($('#tax_amount').val())*tax_reporting_rate));
    }
});

// Get Data from Trasaction Form
function getTransactionForm() {
    var transaction = new Transaction();

    if ($("#id_distribution_code").val() != '') {
        transaction.distribution_id = $("#id_distribution_code").val();
        transaction.distribution_code = $("#id_distribution_code option:selected").text();
        transaction.distribution_name = $("#distribution_desc").val();
    }


    if ($("#id_account_code").val() != '') {
        transaction.account_id = $("#id_account_code").val();
        transaction.account_code = $("#id_account_code option:selected").text();
        transaction.account_name = $("#account_desc").val();
    }
    transaction.tax_id = $('#id_tax').val();
    if (transaction.tax_id) {
        rate = float_format($('#id_tax').find(':selected').data('rate'));
    } else {
        rate = 0;
        transaction.tax_id = '0';
    }
    transaction.description = filter_special_char($("#description").val());

    base_tax_amount = float_format($('#base_amount').val());
    amount = float_format($("#amount").val());
    tax_amount = float_format($('#tax_amount').val());
    transaction.base_tax_amount = float_format($('#base_amount').val());
    taxIncluded = $('#tax-checkbox:checkbox:checked').length;
    taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    taxman = $('#manual-tax:checkbox:checked').length;

    if (taxman > 0) {
        transaction.is_manual_tax_input = 1;
        if (taxOnly > 0) {
            transaction.is_tax_included = 0;
            transaction.is_tax_transaction = 1;
            transaction.amount = 0;
            transaction.base_tax_amount = base_tax_amount;
            transaction.tax_amount = tax_amount;
            transaction.total_amount = tax_amount;
        } else if (taxIncluded > 0) {
            transaction.is_tax_included = 1;
            transaction.is_tax_transaction = 0;
            transaction.amount = base_tax_amount;
            transaction.base_tax_amount = base_tax_amount;
            transaction.tax_amount = tax_amount;
            transaction.total_amount = base_tax_amount + tax_amount;
        } else {
            transaction.is_tax_included = 0;
            transaction.is_tax_transaction = 0;
            transaction.amount = amount;
            transaction.base_tax_amount = base_tax_amount;
            transaction.tax_amount = tax_amount;
            transaction.total_amount = amount + tax_amount;
        }
    } else {
        transaction.is_manual_tax_input = 0;
        transaction.base_tax_amount = float_format($('#base_amount').val());
        if (taxOnly > 0) {
            transaction.amount = 0.0;
            transaction.tax_amount = float_format(amount);
            transaction.total_amount = float_format(amount);
            transaction.is_tax_included = 0;
            transaction.is_tax_transaction = 1;
        } else {
            if (taxIncluded > 0) {
                transaction.total_amount = amount;
                rate = rate / 100;
                transaction.amount = float_format(comma_format(amount / (1 + rate)));
                transaction.tax_amount = transaction.total_amount - transaction.amount;
                transaction.is_tax_included = 1;
                transaction.is_tax_transaction = 0;
            } else {
                transaction.amount = amount;
                if(transaction.tax_id == 0){
                    transaction.tax_amount = 0;
                    transaction.total_amount = transaction.tax_amount + transaction.amount;
                }else{
                    // transaction.tax_amount = float_format((rate * amount) / 100);
                    transaction.tax_amount = tax_amount;
                    transaction.total_amount = transaction.tax_amount + transaction.amount;
                }
                transaction.is_tax_included = 0;
                transaction.is_tax_transaction = 0;
            }
        }
    }
    return transaction;
}


function recalculatePaymentAmount() {
    var calculate_value = {};
    var total_amount = 0.00;
    var customer_amount = 0.00;
    transaction_type = $('#id_transaction_type').val();
    if (transaction_type == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
        var table = $('#transaction-table').DataTable();
        table.rows().every(function (rowIdx, tableLoop, rowLoop) {
            doc_type = table.cell(rowIdx, $("#trs-doc-type").index()).data();
            amount = float_format(table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.value);
            if (isNaN(amount)) {
                amount = float_format(0);
            }
            discount = float_format(table.cell(rowIdx, $("#trs-discount").index()).node().firstChild.value);
            if (isNaN(discount)) {
                discount = float_format(0);
            }
            // adjustment = table.cell(rowIdx, $("#trs-adjustment").index()).data();
            // if (isNaN(adjustment)) {
            //     adjustment = float_format(0);
            // }
            // amount = float_format(amount) + float_format(discount) - float_format(adjustment);
            amount = float_format(amount) + float_format(discount);
            if (doc_type == 'Credit Note' || doc_type == 'Unapplied Cash' || doc_type == 'Receipt'){
                total_amount -= (float_format(amount) * float_format(supp_bank_exch_rate));
                customer_amount -= float_format(amount);
            } else {
                total_amount += (float_format(amount) * float_format(supp_bank_exch_rate));
                customer_amount += float_format(amount);
            }
        });
        calculate_value.total_amount = float_format((total_amount).toFixed(3));
        calculate_value.customer_amount = float_format((customer_amount).toFixed(3));

        return calculate_value;
    } else if (transaction_type == RECEIPT_TRANSACTION_TYPES_MISC_RECEIPT) {
        var datatbl = $('#misc-transaction-table').DataTable();
        datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
            amount = datatbl.cell(rowIdx, $("#trs-total_amount").index()).data();
            total_amount += float_format(amount);
        });
        total_amount = float_format((total_amount).toFixed(3));
    }

    return total_amount;
}


// Set Data for Transaction Form
function setTransactionForm(transaction) {
    $("#id_distribution_code").val(transaction.distribution_id).trigger('change');
    $("#id_account_code").val(transaction.account_id).trigger('change');
    $("#description").val(filter_special_char(transaction.description));
    if(bank_is_decimal) {
        $("#tax_amount").val(comma_format(transaction.tax_amount));
        $("#base_amount").val(comma_format(transaction.base_tax_amount));
        $("#amount").val(comma_format(transaction.amount));
    } else {
        $("#tax_amount").val(comma_format(transaction.tax_amount, 0));
        $("#base_amount").val(comma_format(transaction.base_tax_amount, 0));
        $("#amount").val(comma_format(transaction.amount, 0));
    }
    $("#tax_report_amount").val(comma_format(transaction.tax_amount*tax_reporting_rate));
    if (transaction.is_manual_tax_input == 1) {
        $('#manual-tax').prop('checked', true).trigger('change');
        $('#manual-tax').attr('disabled', false);
        if(transaction.is_tax_transaction == 1){
            $("#tax-only-checkbox").prop('checked', true);
            $('#tax-only-checkbox').attr('disabled', false);
            if(bank_is_decimal) {
                $("#amount").val(comma_format(transaction.amount));
            } else {
                $("#amount").val(comma_format(transaction.amount, 0));
            }
        }
        if(transaction.is_tax_included == 1){
            $("#tax-checkbox").prop('checked', true);
            if(bank_is_decimal) {
                $("#amount").val(comma_format(transaction.total_amount));
            } else {
                $("#amount").val(comma_format(transaction.total_amount, 0));
            }
        }
        $('#tax-checkbox').attr('disabled', false);
        $("#id_tax").val(transaction.tax_id).trigger('change');
    } else {
        $('#manual-tax').prop('checked', false).trigger('change');
        if (transaction.is_tax_transaction == 1) {
            if(bank_is_decimal) {
                $("#amount").val(comma_format(transaction.total_amount));
            } else {
                $("#amount").val(comma_format(transaction.total_amount, 0));
            }
            $("#tax-only-checkbox").prop('checked', true).trigger('change');
            $('#tax-only-checkbox').attr('disabled', false);
        } else {
            if (transaction.is_tax_included == 0) {
                if(bank_is_decimal) {
                    $("#amount").val(comma_format(transaction.amount));
                } else {
                    $("#amount").val(comma_format(transaction.amount, 0));
                }
                $("#tax-checkbox").prop('checked', false);
            }
            else if (transaction.is_tax_included == 1) {
                if(bank_is_decimal) {
                    $("#amount").val(comma_format(transaction.total_amount));
                } else {
                    $("#amount").val(comma_format(transaction.total_amount, 0));
                }
                $("#tax-checkbox").prop('checked', true);
                $('#tax-checkbox').attr('disabled', false);
            }
        }
        $("#id_tax").val(transaction.tax_id).trigger('change');
    }
}

// Save Update New Transaction
function editNewTransaction(line) {
    // Get Data from Transaction Form
    var transaction = getTransactionForm();

    // Update row data
    var datatbl = $('#misc-transaction-table').DataTable();
    row = trigger_row;
    var data = datatbl.row(row).data();
    var old_amount = datatbl.cell(row, $("#trs-amount").index()).data();
    // Draw data into table
    datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
    datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
    datatbl.cell(row, $("#trs-account_code").index()).data(transaction.account_code);
    datatbl.cell(row, $("#trs-account_name").index()).data(filter_special_char(transaction.account_name));
    if(bank_is_decimal) {
        datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount));
        datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount));
        datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount));
    } else {
        datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount, 0));
        datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount, 0));
        datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount, 0));
    }
    row[9] = transaction.distribution_id;
    row[10] = transaction.account_id;
    row[11] = transaction.is_tax_included;
    row[12] = transaction.is_tax_transaction;
    row[13] = transaction.tax_id;
    row[14] = transaction.is_manual_tax_input;
    row[15] = comma_format(transaction.base_tax_amount);
    row[17] = line;
    datatbl.draw();

    // Update old transaction list, not save in database
    transaction.line = line;
    transaction.row_number = line;
    // Find object
    var result = $.grep(transaction_new, function (e) {
        return e.line == line;
    });
    // Not found object -> return
    if (result.length == 0) {
        alert("Can't update!");
        return 0;
    }
    // Found object -> update object
    else if (result.length == 1) {
        result[0].line = transaction.line;
        result[0].distribution_code = transaction.distribution_code;
        result[0].description = filter_special_char(transaction.description);
        result[0].account_code = transaction.account_code;
        result[0].account_name = filter_special_char(transaction.account_name);
        result[0].amount = transaction.amount;
        result[0].tax_amount = transaction.tax_amount;
        result[0].total_amount = transaction.total_amount;
        result[0].distribution_id = transaction.distribution_id;
        result[0].account_id = transaction.account_id;
        result[0].is_tax_included = transaction.is_tax_included;
        result[0].is_tax_transaction = transaction.is_tax_transaction;
        result[0].tax_id = transaction.tax_id;
        result[0].is_manual_tax_input = transaction.is_manual_tax_input;
        result[0].base_tax_amount = transaction.base_tax_amount;
    }

    var amount = 0;
    var tax_amount = 0;
    var total_amount = 0;
    datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
        amount += float_format(datatbl.cell(rowIdx, $("#trs-amount").index()).data());
        tax_amount += float_format(datatbl.cell(rowIdx, $("#trs-tax_amount").index()).data());
        total_amount += float_format(datatbl.cell(rowIdx, $("#trs-total_amount").index()).data());
    });
    amount = float_format((amount).toFixed(3));
    tax_amount = float_format((tax_amount).toFixed(3));
    total_amount = float_format((total_amount).toFixed(3));
    // total_amount = recalculatePaymentAmount()
    if(bank_is_decimal) {
        $('#id_amount').val(comma_format(amount));
        $('#id_tax_amount').val(comma_format(tax_amount));
        $("#id_total_amount").val(comma_format(total_amount));
    } else {
        $('#id_amount').val(comma_format(amount, 0));
        $('#id_tax_amount').val(comma_format(tax_amount, 0));
        $("#id_total_amount").val(comma_format(total_amount, 0));
    }
    $("#id_tax_report_amount").val(comma_format(tax_amount * tax_reporting_rate));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }
    $("#MiscReceipt_TransModal").modal("hide");
}

// Show modal to edit new transation
function editNewTransactionModal(line) {
    // Reset form transaction
    $("#transaction_error").text("");
    $(".trs-field").val("");
    // Find object
    var result = $.grep(transaction_new, function (e) {
        return e.line == line;
    });
    // Not found object -> return
    if (result.length == 0) {
        alert("Not found");
        return 0;
    }
    // Found object -> show object
    else if (result.length == 1) {
        setTransactionForm(result[0]);
    }
    // Add action to save button
    $("#btnAddMiscTransaction").attr("onclick", "editNewTransaction(" + (line) + ")");
    $('#line_number').val(trigger_line);
    $("#MiscReceipt_TransModal").modal("show");
}


function deleteMiscTransaction(line) {
    var datatbl = $('#misc-transaction-table').DataTable();
    // Load amount, tax amount, total amount of this row
    var amount_row = datatbl.cell(trigger_row, $("#trs-amount").index()).data();
    amount_row = float_format(amount_row);
    var taxamount_row = datatbl.cell(trigger_row, $("#trs-tax_amount").index()).data();
    taxamount_row = float_format(taxamount_row);
    var total_row = datatbl.cell(trigger_row, $("#trs-total_amount").index()).data();
    total_row = float_format(total_row);
    //Load subtotal, tax amount, total of this journer
    var amount = float_format($("#id_amount").val());
    var taxamount = float_format($("#id_tax_amount").val());
    var total = float_format($("#id_total_amount").val());
    // Update subtotal, tax amount, total
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(amount - amount_row));
        $("#id_tax_amount").val(comma_format(taxamount - taxamount_row));
        $("#id_total_amount").val(comma_format(total - total_row));
    } else {
        $("#id_amount").val(comma_format(amount - amount_row, 0));
        $("#id_tax_amount").val(comma_format(taxamount - taxamount_row, 0));
        $("#id_total_amount").val(comma_format(total - total_row, 0));
    }
    $("#id_tax_report_amount").val(comma_format((taxamount - taxamount_row) * tax_reporting_rate));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }
    // Remove row
    datatbl.row(trigger_row).remove().draw();

    // // Update line number
    // datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     datatbl.cell(rowIdx, $("#trs-line").index()).data(rowIdx + 1);
    //     var is_delete = datatbl.row(rowIdx).data()[16];
    //     var button_edit = datatbl.cell(rowIdx, $("#trs-action-" + rowIdx).index()).node().firstElementChild.lastElementChild.firstElementChild.firstElementChild.id;
    //     var button_delete = datatbl.cell(rowIdx, $("#trs-action-" + rowIdx).index()).node().firstElementChild.lastElementChild.lastElementChild.firstElementChild.id;
    //     if (is_delete != '') {
    //         $('#' + button_edit).attr("onclick", "editTransactionRowOnEditMode(" + rowIdx + ")");
    //         $('#' + button_delete).attr("onclick", "openDeleteConfirmDialog(" + rowIdx + ")");
    //     } else {
    //         $('#' + button_edit).attr("onclick", "editNewTransactionModal(" + rowIdx + ")");
    //         $('#' + button_delete).attr("onclick", "deleteMiscTransaction(" + rowIdx + ")");
    //     }
    //     $('#' + button_edit).attr("id", "editMiscTransaction-" + rowIdx);
    //     $('#' + button_delete).attr("id", "deleteMiscTransaction-" + rowIdx);
    // });

    // reset line number
    resetLine();
    datatbl.draw();
}


$(document).on('click', '.set_line', function() {
    trigger_line = parseInt($(this).closest('tr').find("td:first").text());
    trigger_row = $(this).closest('tr');
});

function resetLine() {
    $('#misc-transaction-table tbody tr').each(function (indx) {
        $(this).find("td:first").text(indx + 1);
    });
}

function goLeft() {
    if (trigger_row) {
        if (new_line) {
            loadRowForEdit();
        } else if (trigger_row.prev().hasClass('even') || trigger_row.prev().hasClass('odd')) {
            trigger_row = trigger_row.prev();
            loadRowForEdit();
        }
    } else {
        let row_count = $('#misc-transaction-table').DataTable().rows().count();
        trigger_row = $('#misc-transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
        loadRowForEdit();
    }
    new_line = false;
}

function goRight() {
    if (trigger_row) {
        if (trigger_row.next().hasClass('even') || trigger_row.next().hasClass('odd')) {
            trigger_row = trigger_row.next();
            loadRowForEdit();
        }
    } else {

    }
    new_line = false;
}

function goLast() {
    let row_count = $('#misc-transaction-table').DataTable().rows().count();
    trigger_row = $('#misc-transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
    loadRowForEdit();
    new_line = false;
}

function goFirst() {
    trigger_row = $('#misc-transaction-table tbody tr:nth-child(1)').closest('tr');
    loadRowForEdit();
    new_line = false;
}

function loadRowForEdit() {
    let rec_etry = false;
    if('True' == is_rec_entry){
        rec_etry = true;
    }
    if(trigger_row != undefined && trigger_row != null) {
        try {
            trigger_line = parseInt(trigger_row.find("td:first").text());
            if (isNaN(trigger_line)) {
                trigger_line = 0;
            }
            let trans_id = $('#misc-transaction-table').DataTable().row( trigger_row ).data()[8];
            let line = $('#misc-transaction-table').DataTable().row( trigger_row ).data()[18];
            var is_delete = $('#misc-transaction-table').DataTable().row( trigger_row ).data()[16];
            if (is_delete != '') {
                editTransactionRowOnEditMode(line);
            } else {
                editNewTransactionModal(line);
            }
        } catch(e) {
            console.log(e);
        }
    }
}

function insertTransactionModal() {
    $('#btnAddMiscTransaction').attr("onclick", "addTransaction()");
    $('#id_distribution_code').val('').trigger('change');
    $('#distribution_desc').val('');
    $('#id_account_code').val('').trigger('change');
    $('#account_desc').val('');
    $('#id_tax').val('').trigger('change');
    $('#description').val('');
    $('#amount').val('');
    $("#tax-only-checkbox").prop('checked', false);
    $("#tax-checkbox").prop('checked', false);
    $('#manual-tax').prop('checked', false).trigger('change');
    $('#tax-only-checkbox').attr('disabled', true);
    $('#tax-checkbox').attr('disabled', true);
    $('#manual-tax').attr('disabled', true);
    $('#base_amount').val('');
    $('#tax_amount').val('');
    $('#tax_report_amount').val('');
    $('#line_number').val(trigger_line + 1);
    new_line = true;
}

// Add new misc transaction
function addTransaction() {
    var validate = checkTransaction();
    if (validate != "success") {
        //$("#transaction_error").text(validate);
        $('#inputButton').trigger('click');
        pop_ok_dialog("Error",
            validate,
            function () { });
    } else {
        $("#transaction_error").text("");
        // Get Data from Transaction Form
        var transaction = getTransactionForm();
        transAmount = comma_format(transaction.amount);
        transTax = comma_format(transaction.tax_amount);
        transTamount = comma_format(transaction.total_amount);
        if(bank_is_decimal) {
            transAmount = comma_format(transaction.amount);
            transTax = comma_format(transaction.tax_amount);
            transTamount = comma_format(transaction.total_amount);
        } else {
            transAmount = comma_format(transaction.amount, 0);
            transTax = comma_format(transaction.tax_amount, 0);
            transTamount = comma_format(transaction.total_amount, 0);
        }
        // Add new row into table
        var datatbl = $('#misc-transaction-table').dataTable();
        current_line = current_line + 1;
        var line = current_line;
        // var button = '<div class="btn-group dropup">'
        //     + '<div class="btn-row">'
        //     + '<button id="editMiscTransaction-' + line + '" class="btn btn-white fa fa-edit" type="button" onclick="editNewTransactionModal(' + line + ')"></button>'
        //     + '<button id="deleteMiscTransaction-' + line + '" class="btn btn-white fa fa-minus" type="button" onclick="deleteMiscTransaction(' + line + ')"></button>'
        //     + '</div>'
        //     + '</div>';
        var button = '<div class="btn-group dropup">'
                        + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle set_line" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
                        + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
                        + '</button>'
                        + '<ul class="dropdown-menu dropdown-menu-right">'
                        + '<li><a id="editMiscTransaction-' + line + '" onclick="editNewTransactionModal(' + line + ')">Edit</a></li>'
                        + '<li><a id="deleteMiscTransaction-' + line + '" onclick="deleteMiscTransaction(' + line + ')">Delete</a></li>'
                        + '</ul>'
                        + '</div>';
        var dt = datatbl.api();
        var array_row = [
            line,
            transaction.distribution_code,
            filter_special_char(transaction.description),
            transaction.account_code,
            filter_special_char(transaction.account_name),
            transAmount,
            transTax,
            transTamount,
            "",
            transaction.distribution_id,
            transaction.account_id,
            transaction.is_tax_included,
            transaction.is_tax_transaction,
            transaction.tax_id,
            transaction.is_manual_tax_input,
            comma_format(transaction.base_tax_amount),
            "",
            button,
            line
        ];
        dt.row.add(array_row);
        // Insert row to the correct index
        var aiDisplayMaster = datatbl.fnSettings()['aiDisplayMaster'];
        var moveRow = aiDisplayMaster.pop();
        aiDisplayMaster.splice(trigger_line, 0, moveRow);
        dt.draw(false);

        // reset line number
        resetLine();

        // Add transaction into list, not save in database
        transaction.line = line;
        transaction.row_number = line;
        transaction_new.push(transaction);

        var new_amount = 0.00;
        var tax_amount = 0.00;
        var total_amount = 0.00;
        var result_amount = 0.00;
        var result_tax_amount = 0.00;
        var result_total_amount = 0.00;

        datatbl = $('#misc-transaction-table').DataTable();
        datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
            new_amount = datatbl.cell(rowIdx, $("#trs-amount").index()).data();
            tax_amount = datatbl.cell(rowIdx, $("#trs-tax_amount").index()).data();
            total_amount = datatbl.cell(rowIdx, $("#trs-total_amount").index()).data();
            result_amount += float_format(new_amount);
            result_tax_amount += float_format(tax_amount);
            result_total_amount += float_format(total_amount);
        });
        result_amount = float_format((result_amount).toFixed(3));
        result_tax_amount = float_format((result_tax_amount).toFixed(3));
        result_total_amount = float_format((result_total_amount).toFixed(3));
        if(bank_is_decimal) {
            $('#id_amount').val(comma_format(result_amount));
            $('#id_tax_amount').val(comma_format(result_tax_amount));
            $('#id_total_amount').val(comma_format(result_total_amount));
        } else {
            $('#id_amount').val(comma_format(result_amount, 0));
            $('#id_tax_amount').val(comma_format(result_tax_amount, 0));
            $('#id_total_amount').val(comma_format(result_total_amount, 0));
        }
        $("#id_tax_report_amount").val(comma_format(result_tax_amount * tax_reporting_rate));
        if ('True' == is_rec_entry) {
            $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
        }
        // $("#MiscReceipt_TransModal").modal("hide");
        $('button[type="submit"]').prop('disabled', false);
        showTransactionModal();
    }
};


function showTransactionModal() {
    $("#transaction_error").text("");
    var table = $('#misc-transaction-table').DataTable();
    let row_count = table.rows().count();
    trigger_row = $('#misc-transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
    trigger_line = parseInt(trigger_row.find("td:first").text());
    if (isNaN(trigger_line)) {
        trigger_line = 0;
    }
    trigger_row = null;

    $('#btnAddMiscTransaction').attr("onclick", "addTransaction()");
    $('#id_distribution_code').val('').trigger('change');
    $('#distribution_desc').val('');
    $('#id_account_code').val('').trigger('change');
    $('#account_desc').val('');
    $('#id_tax').val('').trigger('change');
    $('#description').val('');
    $('#amount').val('');
    $("#tax-only-checkbox").prop('checked', false);
    $("#tax-checkbox").prop('checked', false);
    $('#manual-tax').prop('checked', false).trigger('change');
    $('#tax-only-checkbox').attr('disabled', true);
    $('#tax-checkbox').attr('disabled', true);
    $('#manual-tax').attr('disabled', true);
    $('#base_amount').val('');
    $('#tax_amount').val('');
    $('#tax_report_amount').val('');
    $('#line_number').val(trigger_line + 1);
    $("#MiscReceipt_TransModal").modal("show");
    new_line = true;

    setTimeout(() => {
        $('#id_distribution_code').select2('open');
    }, 500);
};

$('#MiscReceipt_TransModal').on('hidden.bs.modal', function () {
    $('#id_distribution_code').select2('close');
    $('#id_account_code').select2('close');
    $('#id_tax').select2('close');
});

$('#tableDistributionModal').on('shown.bs.modal', function (ev) {
    $('#id_distribution_code').select2('close');
    $('#id_account_code').select2('close');
    $('#id_tax').select2('close');
});
$('#tableDistributionModal').on('hidden.bs.modal', function (ev) {
    $("#id_account_code").select2('open');
});
$('#tableAccountModal').on('hidden.bs.modal', function (ev) {
    $('#id_tax').select2('open');
});
$('#tableAccountModal').on('shown.bs.modal', function (ev) {
    $('#id_distribution_code').select2('close');
    $('#id_account_code').select2('close');
    $('#id_tax').select2('close');
});

$('#MiscReceipt_TransModal').on('shown.bs.modal', function () {
    $('#id_distribution_code').on('select2:unselect', function (e)
    {
        $('#id_account_code').select2('close');
        $('#id_tax').select2('close');
    });
    $('#id_distribution_code').on('select2:close', function (e)
    {
        $('#id_account_code').focus();
        $('#id_account_code').select2('open');
    });
    $('#id_account_code').on('select2:close', function (e)
    {
        $('#id_tax').select2('open');
    });
    $('#id_tax').on('select2:close', function (e)
    {
        $('#amount').focus();
    });
});


function editTransactionRowValue(line) {
    var transaction = getTransactionForm();
    var datatbl = $('#misc-transaction-table').DataTable();
    var row = datatbl.row(trigger_row).data();
    datatbl.cell(trigger_row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
    datatbl.cell(trigger_row, $("#trs-description").index()).data(filter_special_char(transaction.description));
    datatbl.cell(trigger_row, $("#trs-account_code").index()).data(transaction.account_code);
    datatbl.cell(trigger_row, $("#trs-account_name").index()).data(filter_special_char(transaction.account_name));
    if(bank_is_decimal) {
        datatbl.cell(trigger_row, $("#trs-amount").index()).data(comma_format(transaction.amount));
        datatbl.cell(trigger_row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount));
        datatbl.cell(trigger_row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount));
    } else {
        datatbl.cell(trigger_row, $("#trs-amount").index()).data(comma_format(transaction.amount, 0));
        datatbl.cell(trigger_row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount, 0));
        datatbl.cell(trigger_row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount, 0));
    }
    row[9] = transaction.distribution_id;
    row[10] = transaction.account_id;
    row[11] = transaction.is_tax_included;
    row[12] = transaction.is_tax_transaction;
    row[13] = transaction.tax_id;
    row[14] = transaction.is_manual_tax_input;
    row[15] = comma_format(transaction.base_tax_amount);
    row[18] = line;
    datatbl.draw();
    var new_amount = 0;
    var new_tax_amount = 0;
    var new_total_amount = 0;
    datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
        amount = datatbl.cell(rowIdx, $("#trs-amount").index()).data();
        tax_amount = datatbl.cell(rowIdx, $("#trs-tax_amount").index()).data();
        total_amount = datatbl.cell(rowIdx, $("#trs-total_amount").index()).data();
        int_amount = amount.replace(/,/g , '');
        new_amount += float_format(int_amount);
        int_tax_amount = tax_amount.replace(/,/g , '');
        new_tax_amount += float_format(int_tax_amount);
        int_total_amount = total_amount.replace(/,/g , '');
        new_total_amount += float_format(int_total_amount);
    });
    new_amount = float_format((new_amount).toFixed(3));
    new_tax_amount = float_format((new_tax_amount).toFixed(3));
    new_total_amount = float_format((new_total_amount).toFixed(3));
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(new_amount));
        $("#id_tax_amount").val(comma_format(new_tax_amount));
        $("#id_total_amount").val(comma_format(new_total_amount));
    } else {
        $("#id_amount").val(comma_format(new_amount, 0));
        $("#id_tax_amount").val(comma_format(new_tax_amount, 0));
        $("#id_total_amount").val(comma_format(new_total_amount, 0));
    }

    $("#id_tax_report_amount").val(comma_format(new_tax_amount * tax_reporting_rate));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }
    $("#MiscReceipt_TransModal").modal("hide");
};


function editTransactionRowOnEditMode(line) {
    var datatbl = $('#misc-transaction-table').DataTable();
    var row = datatbl.row(trigger_row).data();
    $('#id_distribution_code option[value="' + row[9] + '"]').prop('selected', true);
    $('#distribution_desc').val(row[1]);
    $('#select2-id_distribution_code-container').children().text($('#id_distribution_code option:selected').text());
    $('#id_account_code option[value="' + row[10] + '"]').prop('selected', true);
    $('#account_desc').val(filter_special_char(row[4]));
    $('#select2-id_account_code-container').children().text($('#id_account_code option:selected').text());
    $("#id_tax").val(row[13]).trigger('change');
    // $('#select2-id_tax-container').children().text($('#id_tax option:selected').text());
    $('#description').val(filter_special_char(row[2]));
    if(bank_is_decimal) {
        $("#tax_amount").val(comma_format(float_format(row[6])));
        $("#base_amount").val(comma_format(float_format(row[15])));
    } else {
        $("#tax_amount").val(comma_format(float_format(row[6]), 0));
        $("#base_amount").val(comma_format(float_format(row[15]), 0));
    }
    if (row[14] == '1') {
        $('#manual-tax').prop('checked', true).trigger('change');
        if(bank_is_decimal) {
            $('#amount').val(comma_format(float_format(row[7])));
        } else {
            $('#amount').val(comma_format(float_format(row[7]), 0));
        }
    } else {
        if (row[12] == '1') {
            $("#tax-only-checkbox").prop('checked', true);
            if(bank_is_decimal) {
                $('#amount').val(comma_format(float_format(row[6])));
            } else {
                $('#amount').val(comma_format(float_format(row[6]), 0));
            }
        }
        else if (row[11] == '1') {
            $("#tax-checkbox").prop('checked', true);
            if(bank_is_decimal) {
                $('#amount').val(comma_format(float_format(row[7])));
            } else {
                $('#amount').val(comma_format(float_format(row[7]), 0));
            }
        } else {
            $("#tax-checkbox").prop('checked', false);
            if(bank_is_decimal) {
                $('#amount').val(comma_format(float_format(row[5])));
            } else {
                $('#amount').val(comma_format(float_format(row[5]), 0));
            }
        }
    }

    $("#btnAddMiscTransaction").attr("onclick", "editTransactionRowValue(" + line + ")");

    // disable when jounal was posted
    if (jrn_status == '2') {
        $('#manual-tax').prop('disabled', true);
        $('#tax-only-checkbox').prop('disabled', true);
        $('#tax-checkbox').prop('disabled', true);
    }
    $('#line_number').val(trigger_line);
    $("#MiscReceipt_TransModal").modal("show");
};


function deleteTransactionRowOnEditMode(line) {
    var table = $('#misc-transaction-table').DataTable();
    var amount_of_row = table.cell(trigger_row, $("#trs-amount").index()).data();
    var tax_amount_of_row = table.cell(trigger_row, $("#trs-tax_amount").index()).data();
    var total_amount_of_row = table.cell(trigger_row, $("#trs-total_amount").index()).data();
    amount_of_row = float_format(amount_of_row.replace(/,/, ''));
    tax_amount_of_row = float_format(tax_amount_of_row.replace(/,/, ''));
    total_amount_of_row = float_format(total_amount_of_row.replace(/,/, ''));
    var new_amount = 0;
    var new_tax_amount = 0;
    var new_total_amount = 0;
    var amount = $("#id_amount").val();
    var tax_amount = $("#id_tax_amount").val();
    var total_amount = $("#id_total_amount").val();
    var button = $('#deleteMiscTransaction-' + line);
    table.row(trigger_row).data()[16] = '1';
    new_amount = float_format(amount.replace(/,/, '')) - float_format(amount_of_row);
    new_tax_amount = float_format(tax_amount.replace(/,/, '')) - float_format(tax_amount_of_row);
    new_total_amount = float_format(total_amount.replace(/,/, '')) - float_format(total_amount_of_row);
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(new_amount));
        $("#id_tax_amount").val(comma_format(new_tax_amount));
        $("#id_total_amount").val(comma_format(new_total_amount));
    } else {
        $("#id_amount").val(comma_format(new_amount, 0));
        $("#id_tax_amount").val(comma_format(new_tax_amount, 0));
        $("#id_total_amount").val(comma_format(new_total_amount, 0));
    }
    $("#id_tax_report_amount").val(comma_format(new_tax_amount * tax_reporting_rate));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val(comma_format($('#id_total_amount').val()));
    }
    var row_data = table.row(trigger_row).data();
    var transaction = new Transaction();
    transaction.line = row_data[0];
    transaction.distribution_code = row_data[1];
    transaction.description = filter_special_char(row_data[2]);
    transaction.account_code = row_data[3];
    transaction.account_name = filter_special_char(row_data[4]);
    transaction.amount = row_data[5];
    transaction.tax_amount = row_data[6];
    transaction.total_amount = row_data[7];
    transaction.trans_id = row_data[8];
    transaction.distribution_id = row_data[9];
    transaction.account_id = row_data[10];
    transaction.is_tax_included = row_data[11];
    transaction.is_tax_transaction = row_data[12];
    transaction.tax_id = row_data[13];
    transaction.is_manual_tax_input = row_data[14];
    transaction.base_tax_amount = row_data[15];
    transaction.is_delete = row_data[16];
    transaction.row_number = row_data[0];
    allVals.push(transaction);
    table.row(trigger_row).remove().draw();
    // // Update line number
    // table.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     table.cell(rowIdx, $("#trs-line").index()).data(rowIdx + 1);
    //     var is_delete = table.row(rowIdx).data()[13];
    //     var button_edit = datatbl.cell(rowIdx, $("#trs-action-" + rowIdx).index()).node().firstElementChild.lastElementChild.firstElementChild.firstElementChild.id;
    //     var button_delete = datatbl.cell(rowIdx, $("#trs-action-" + rowIdx).index()).node().firstElementChild.lastElementChild.lastElementChild.firstElementChild.id;
    //     if (is_delete != '') {
    //         $('#' + button_edit).attr("onclick", "editTransactionRowOnEditMode(" + rowIdx + ")");
    //         $('#' + button_delete).attr("onclick", "openDeleteConfirmDialog(" + rowIdx + ")");
    //     } else {
    //         $('#' + button_edit).attr("onclick", "editNewTransactionModal(" + rowIdx + ")");
    //         $('#' + button_delete).attr("onclick", "deleteMiscTransaction(" + rowIdx + ")");
    //     }
    //     $('#' + button_edit).attr("id", "editMiscTransaction-" + rowIdx);
    //     $('#' + button_delete).attr("id", "deleteMiscTransaction-" + rowIdx);
    // });

    // reset line number
    resetLine();
    table.draw();
}

// $('#form').on('submit', function (e) {
//     if ($('#id_currency').val() != $('#id_customer_currency').val()) {
//         e.preventDefault();
//         $('#error_currency').text('The currency of Customers must be same currency of Bank. Please try again!');
//     } else {
//         $('#error_currency').css('display', 'none');
//     }
// })

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

function update_exch_rate() {
    var date_rate = $("#id_document_date").val();
    var bank_currency = $("#id_currency option:selected").val();
    var customer_currency = $("#id_customer_currency").val();
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
                    bank_exchange_date = data[0].exchange_date;
                    bank_is_decimal = data[0].is_decimal;
                }
            }
        });
    }
    if (customer_currency) {
        $.ajax({
            type: "GET",
            url :'/currencies/get_exchange_by_date/1/'+customer_currency+'/'+date_rate+'/3/',
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
                    $('#id_original_currency_id').val(parseInt(customer_currency));
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
    var customer_currency = $("#id_customer_currency").val();
    if (bank_currency && customer_currency) {
        if (bank_currency != customer_currency) {
            is_currency_differene = true;
            bank_exch_rate = parseFloat($('#id_exchange_rate').val());
            cust_exch_rate = parseFloat($('#id_orig_exch_rate').val());
            supp_bank_exch_rate =  cust_exch_rate / bank_exch_rate;
        } else {
            supp_bank_exch_rate = 1.0;
        }
    } else {
        supp_bank_exch_rate = 1.0;
    }
}

function showRateOverrideModal() {
    var bank_currency = $('#id_currency option:selected').text();
    var vendor_currency = $('#id_customer_currency option:selected').text();
    $('#bank_label').text(bank_currency + ' TO ' + company_currency);
    $('#id_bank_rate').val($('#id_exchange_rate').val());
    $('#vendor_label').text(vendor_currency + ' TO ' + company_currency);
    $('#id_vendor_rate').val($('#id_orig_exch_rate').val());
    $('#vendor_amount').val($('#id_original_amount').val());
    $('#bank_amount').val($('#id_payment_amount').val());

    if (vendor_currency && bank_currency != vendor_currency) {
        $('#vendor_section').css('display', 'block');
    } else {
        $('#vendor_section').css('display', 'none');
    }
    $("#RateOverrideModal").modal("show");
}


function saveExchangeRate() {
    var bank_currency = $('#id_currency option:selected').text();
    var vendor_currency = $('#id_customer_currency option:selected').text();
    var old_bank_rate = parseFloat($('#id_exchange_rate').val());
    var old_vendor_rate = parseFloat($('#id_orig_exch_rate').val());
    var bank_rate = parseFloat(parseFloat($('#id_bank_rate').val()).toFixed(10));
    var vendor_rate = parseFloat(parseFloat($('#id_vendor_rate').val()).toFixed(10));

    if (vendor_currency && bank_currency != vendor_currency) {
        if(old_bank_rate != bank_rate) {
            $('#id_exchange_rate').val(bank_rate);
            $('#id_exchange_rate_fk').val('');
            bank_exchange_date = '';
        }
        if(old_vendor_rate != vendor_rate) {
            $('#id_orig_exch_rate').val(vendor_rate);
            vendor_exchange_date = '';
        }

        bank_exch_rate = parseFloat($('#id_exchange_rate').val());
        ven_exch_rate = parseFloat($('#id_orig_exch_rate').val());
        supp_bank_exch_rate =  ven_exch_rate / bank_exch_rate;

        calculate_value = recalculatePaymentAmount();
        if(calculate_value.total_amount == 0) {
            calculate_value.total_amount = float_format($('#id_payment_amount').val());
            calculate_value.customer_amount = calculate_value.total_amount / supp_bank_exch_rate;
        }
        // $('#id_total_amount').val(comma_format(calculate_value.total_amount));
        if(bank_is_decimal) {
            $('#id_payment_amount').val(comma_format(calculate_value.total_amount));
            if (float_format($('#id_total_amount').val()) == 0) {
                $('#id_receipt_unapplied').val(comma_format(calculate_value.total_amount));
            } else {
                $('#id_receipt_unapplied').val(comma_format(0.00));
            }
        } else {
            $('#id_payment_amount').val(comma_format(calculate_value.total_amount, 0));
            if (float_format($('#id_total_amount').val()) == 0) {
                $('#id_receipt_unapplied').val(comma_format(calculate_value.total_amount, 0));
            } else {
                $('#id_receipt_unapplied').val(comma_format(0.00, 0));
            }
        }
        if(vendor_is_decimal) {
            $('#id_original_amount').val(comma_format(calculate_value.customer_amount));
            if (float_format($('#id_total_amount').val()) == 0) {
                $('#id_customer_unapplied').val(comma_format(calculate_value.customer_amount));
            } else {
                $('#id_customer_unapplied').val(comma_format(0.00));
            }
        } else {
            $('#id_original_amount').val(comma_format(calculate_value.customer_amount, 0));
            if (float_format($('#id_total_amount').val()) == 0) {
                $('#id_customer_unapplied').val(comma_format(calculate_value.customer_amount, 0));
            } else {
                $('#id_customer_unapplied').val(comma_format(0.00, 0));
            }
        }

    } else {
        if(old_bank_rate != bank_rate) {
            $('#id_exchange_rate').val(bank_rate);
            $('#id_exchange_rate_fk').val('');
            $('#id_orig_exch_rate').val(bank_rate);
            bank_exchange_date = '';
            vendor_exchange_date = '';
        }
    }

    $("#RateOverrideModal").modal("hide");
}

$('#id_bank_rate, #id_vendor_rate').on('change', function(e){
    var bank_currency = $('#id_currency option:selected').text();
    var vendor_currency = $('#id_customer_currency option:selected').text();
    if (vendor_currency && bank_currency != vendor_currency) {
        var bank_exch_rate = parseFloat($('#id_bank_rate').val());
        var ven_exch_rate = parseFloat($('#id_vendor_rate').val());
        var new_exch_rate =  ven_exch_rate / bank_exch_rate;
        var total_amount = 0.000000;
        var customer_amount = 0.000000;

        transaction_type = $('#id_transaction_type').val();
        if (transaction_type == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
            var table = $('#transaction-table').DataTable();
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                doc_type = table.cell(rowIdx, $("#trs-doc-type").index()).data();
                amount = table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.value;
                if (doc_type == 'Credit Note' || doc_type == 'Unapplied Cash' || doc_type == 'Receipt'){
                    total_amount -= (float_format(amount) * float_format(new_exch_rate));
                    customer_amount -= float_format(amount);
                } else {
                    total_amount += (float_format(amount) * float_format(new_exch_rate));
                    customer_amount += float_format(amount);
                }
            });
            if(total_amount == 0) {
                total_amount = float_format($('#id_payment_amount').val());
                customer_amount = total_amount / new_exch_rate;
            }
        } else {
            total_amount = float_format($('#id_payment_amount').val());
            customer_amount = total_amount / new_exch_rate;
        }

        if (bank_is_decimal) {
            $('#bank_amount').val(comma_format(total_amount));
        } else {
            $('#bank_amount').val(comma_format(total_amount, 0));
        }
        if (vendor_is_decimal) {
            $('#vendor_amount').val(comma_format(customer_amount));
        } else {
            $('#vendor_amount').val(comma_format(customer_amount, 0));
        }

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
                    function () { })
            } else if (exch_date.split('-')[0] != year_perd.split('-')[2]) {
                pop_ok_dialog("Warning",
                    "Bank Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { })
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
                    "Customer Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { })
            } else if (exch_date.split('-')[0] != year_perd.split('-')[2]) {
                pop_ok_dialog("Warning",
                    "Customer Currency Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                    function () { })
            }
        }
    }, 300);
});

// validate amount and currency for AR Receipt - Receipt Type
function validatePayment(transaction_type) {
    error = 0;
    if (transaction_type == RECEIPT_TRANSACTION_TYPES_RECEIPT) {
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
        // customer_currency = $("#id_customer_currency").val();
        // if (bank_currency != customer_currency) {
        //     error += 1;
        //     $('#error_currency').text('Bank currency and Customer currency is not the same currency.')
        //     $("html, body").animate({scrollTop: 0}, "fast");
        // } else {
        //     $('#error_currency').text('');
        // }
    }
    return error;
}

function FillYearPeriodOptLst() {
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

$.initBtnAdjustmentTransaction = function() {
    // $('.btn-adjustment-transaction').off('click').on('click', function() {
    //     var $row = $(this).closest('tr');
    //     console.log($row);
    //     console.log($row.index());

    //     adjustmentTransaction($row.index());
    // });

}
function openAdjustmentDialog(row_number) {

    adjustmentTransaction(parseInt(row_number));
}

$.initTransactionInput = function() {
    $('#transaction-table tr').each(function() {
        var row = $(this).index();

        $(this).find('input.appliedAmount, input.discountAmount').off('change').on('change', function() {
            checkValue(row);
        });
    });
}

$(document).ready(function() {
    setTimeout(function() {
        $.initTransactionInput()
    }, 300);

    $.initBtnAdjustmentTransaction();

    $('#transaction-table').DataTable().rows().every(function(rowIdx, tableLoop, rowLoop) {
        var json_data = $('#transaction-table').DataTable().cell(rowIdx, $('#trs-trx-adjustment').index()).data();

        if (json_data) {
            json_data = $.parseJSON(json_data)

            $.each(json_data.transactions, function(i, v) {
                if (json_data.transactions[i].distribution_code_id === null) {
                    json_data.transactions[i].distribution_code_id = '0';
                }
            });

            $.adjustment_data[rowIdx] = {
                'id' : json_data.id.toString(),
                'reference' : json_data.reference,
                'description' : json_data.description,
                'transactions' : json_data.transactions
            }
        }

        $('#transaction-table').DataTable().cell(rowIdx, $('#trs-adjustment').index()).data($.calculateAdjustment(rowIdx).toFixed(2));
        //$('#transaction-table').DataTable().cell(rowIdx, $('#trs-net-amount').index()).data($.calculateNetbalance(rowIdx).toFixed(2));

        var discount = float_format($($('#transaction-table').DataTable().cell(rowIdx, $('#trs-discount').index()).data()).val().replace(',', ''));

        if (isNaN(discount)) discount = '0';

        $.old_discount[rowIdx] = discount;
    });
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
