/**
 * Created by minhtam on 10/20/2016.
 */
// Load Tax to calculate Tax amount, Total amount to save Transaction

var trigger_row;
var trigger_line = 1;
var new_line = false;

function loadTax() {
    $.ajax({
        method: "POST",
        url: '/orders/load_tax/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'tax_id': parseInt($('#id_tax').val()),
        },
        success: function (resp) {
            $("#tax_value").val(resp);
        },
        error: function () {
            alert("Can't load Tax");
        }
    });
}

// Show Transaction Modal to add new
function showTransactionModal() {

    // Reset form transaction
    $("#transaction_error").text("");
    var table = $('#misc-transaction-table').DataTable();
    let row_count = table.rows().count();
    trigger_row = $('#misc-transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
    trigger_line = parseInt(trigger_row.find("td:first").text());
    if (isNaN(trigger_line)) {
        trigger_line = 0;
    }
    trigger_row = null;

    $("#transaction_error").text("");
    $(".trs-field").val("");
    $('#id_distribution_code').val('').trigger('change');
    $('#id_account_code').val('').trigger('change');
    // $('#id_tax').val('').trigger('change');
    $('#manual-tax').prop('checked', false).trigger('change');
    $('#tax-checkbox').prop('checked', false);
    $('#tax-only-checkbox').prop('checked', false).trigger('change');
    $('#manual-tax').attr('disabled', true);
    $('#tax-checkbox').attr('disabled', true);
    $('#tax-only-checkbox').attr('disabled', true);
    $('#base_amount').val('');
    $('#tax_amount').val('');
    $('#tax_report_amount').val('');
    // Add action to save button
    $("#save-trs").attr("onclick", "addTransaction()");
    $('#line_number').val(trigger_line + 1);
    $("#MiscPayment_TransModal").modal("show");
    new_line = true;

    setTimeout(() => {
        $('#id_distribution_code').select2('open');
    }, 500);
}

$('#MiscPayment_TransModal').on('hidden.bs.modal', function () {
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

$('#MiscPayment_TransModal').on('shown.bs.modal', function () {
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

// Show Transaction Modal to add new
function showRateOverrideModal() {
    var bank_currency = $('#id_currency_text').val();
    var vendor_currency = $('#id_supplier_currency option:selected').text();
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

$('#id_bank_rate, #id_vendor_rate').on('change', function(e){
    var bank_currency = $('#id_currency_text').val();
    var vendor_currency = $('#id_supplier_currency option:selected').text();
    if (vendor_currency && bank_currency != vendor_currency) {
        var bank_exch_rate = parseFloat($('#id_bank_rate').val());
        var ven_exch_rate = parseFloat($('#id_vendor_rate').val());
        var new_exch_rate =  ven_exch_rate / bank_exch_rate;
        var total_amount = 0.000000;
        var vendor_amount = 0.000000;

        var table = $('#py-transaction-table').DataTable();
        table.rows().every(function (rowIdx, tableLoop, rowLoop) {
            doc_type = table.cell(rowIdx, $("#trs-doc-type").index()).data();
            amount = table.cell(rowIdx, $("#trs-apply-amount").index()).node().firstChild.value;
            if (doc_type == 'Credit Note'){
                total_amount -= (float_format(amount) * float_format(new_exch_rate));
                vendor_amount -= float_format(amount);
            } else {
                total_amount += (float_format(amount) * float_format(new_exch_rate));
                vendor_amount += float_format(amount);
            }
        });
    
        if(bank_is_decimal) {
            $('#bank_amount').val(comma_format(total_amount));
        } else {
            $('#bank_amount').val(comma_format(total_amount, 0));
        }
        if(vendor_is_decimal) {
            $('#vendor_amount').val(comma_format(customer_amount));
        } else {
            $('#vendor_amount').val(comma_format(customer_amount, 0));
        }
    }

});

function saveExchangeRate() {
    var bank_currency = $('#id_currency_text').val();
    var vendor_currency = $('#id_supplier_currency option:selected').text();
    var old_bank_rate = parseFloat($('#id_exchange_rate').val());
    var old_vendor_rate = parseFloat($('#id_orig_exch_rate').val());
    var bank_rate = parseFloat(parseFloat($('#id_bank_rate').val()).toFixed(10));
    var vendor_rate = parseFloat(parseFloat($('#id_vendor_rate').val()).toFixed(10));
    
    if (vendor_currency && bank_currency != vendor_currency) {
        if(old_bank_rate != bank_rate) {
            $('#id_exchange_rate').val(bank_rate);
            $('#id_exchange_rate_fk').val('');
        }
        if(old_vendor_rate != vendor_rate) {
            $('#id_orig_exch_rate').val(vendor_rate);
        }

        bank_exch_rate = parseFloat($('#id_exchange_rate').val());
        ven_exch_rate = parseFloat($('#id_orig_exch_rate').val());
        supp_bank_exch_rate =  ven_exch_rate / bank_exch_rate;

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
    } else {
        if(old_bank_rate != bank_rate) {
            $('#id_exchange_rate').val(bank_rate);
            $('#id_exchange_rate_fk').val('');
            $('#id_orig_exch_rate').val(bank_rate);
        }
    }

    $("#RateOverrideModal").modal("hide");
}
// Show Distribution Modal for search Distribution of Transaction
function showDistributionModal() {
    loadDistributionAjax();
    $("#tableDistributionModal").modal("show");
}

// Show Account Modal for search Account of Transaction
function showAccountModal() {
    loadAccountAjax();
    $("#tableAccountModal").modal("show");
}

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

var distribution_code = [];

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
            "url": "/accounts/dist-code/list/pagination/2/" /* DIS_CODE_TYPE['AP Distribution Code'] */
        },
        "columns": [
            {"data": "name", "sClass": "text-left"},
            {"data": "code", "sClass": "text-left"},
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
}

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

function loadAccountAjax() {
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
}

function selectDistribution(id, code, name, account_id, account_code, account_name) {
    $("#id_distribution_code").val(id).trigger('change');
    $("#id_account_code").val(account_id).trigger('change');
}

function selectAccount(id, code, name) {
    $("#id_account_code").val(id).trigger('change');
}

// Define class Transaction
function Transaction() {
    this.line = null;
    this.distribution_id = null;
    this.distribution_code = null;
    this.distribution_name = null;
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
    this.base_tax_amount = null;
    this.is_manual_tax_input = null;
    this.row_number = null;
}

// Get Data from Trasaction Form
function getTransactionForm() {
    var transaction = new Transaction();

    if($("#id_distribution_code").val() != '') {
        transaction.distribution_id = $("#id_distribution_code").val();
        transaction.distribution_code = $("#id_distribution_code option:selected").text();
        transaction.distribution_name = $("#distribution_desc").val();
    }


    if($("#id_account_code").val() != '') {
        transaction.account_id = $("#id_account_code").val();
        transaction.account_code = $("#id_account_code option:selected").text();
        transaction.account_name = $("#account_desc").val();
    }
    transaction.tax_id = $('#id_tax').val();
    if (transaction.tax_id) {
        rate = float_format($('#id_tax').find(':selected').data('rate'));
    } else {
        rate = 0;
        transaction.tax_id = '';
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
        if(taxOnly > 0) {
            transaction.amount = 0.0;
            transaction.tax_amount = float_format(amount);
            transaction.total_amount = float_format(amount);
            transaction.is_tax_included = 0;
            transaction.is_tax_transaction = 1;
        } else {
            if(taxIncluded > 0) {
                transaction.total_amount = amount;
                rate = rate/100;
                transaction.amount = float_format(comma_format(amount / (1+rate)));
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
        $('#manual-tax').attr('disabled', false);
        $('#manual-tax').prop('checked', true).trigger('change');
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
    } else{
        $('#manual-tax').prop('checked', false).trigger('change');
        if(transaction.is_tax_transaction ==1){
            $("#amount").val(comma_format(transaction.total_amount));
            $("#tax-only-checkbox").prop('checked', true).trigger('change');
        } else {
            $("#tax-only-checkbox").prop('checked', false).trigger('change');
            if(transaction.is_tax_included == 0) {
                if(bank_is_decimal) {
                    $("#amount").val(comma_format(transaction.amount));
                } else {
                    $("#amount").val(comma_format(transaction.amount, 0));
                }
                $("#tax-checkbox").prop('checked', false);
            }
            else if(transaction.is_tax_included == 1) {
                if(bank_is_decimal) {
                    $("#amount").val(comma_format(transaction.total_amount));
                } else {
                    $("#amount").val(comma_format(transaction.total_amount, 0));
                }
                $("#tax-checkbox").prop('checked', true);
            }
        }
        $("#id_tax").val(transaction.tax_id).trigger('change');
    }
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
            let trans_id = $('#misc-transaction-table').DataTable().row( trigger_row ).data()[9];
            let line = $('#misc-transaction-table').DataTable().row( trigger_row ).data()[17];
            if (trans_id != undefined && trans_id != '') {
                editOldTransactionModal(trans_id, line, rec_etry);
            } else {
                editNewTransactionModal(line);
            }
        } catch(e) {
            console.log(e);
        }
    }
}

function insertTransactionModal() {
    $("#transaction_error").text("");
    $(".trs-field").val("");
    $('#id_distribution_code').val('').trigger('change');
    $('#id_account_code').val('').trigger('change');
    // $('#id_tax').val('').trigger('change');
    $('#manual-tax').prop('checked', false).trigger('change');
    $('#tax-checkbox').prop('checked', false);
    $('#tax-only-checkbox').prop('checked', false).trigger('change');
    $('#manual-tax').attr('disabled', true);
    $('#tax-checkbox').attr('disabled', true);
    $('#tax-only-checkbox').attr('disabled', true);
    $('#base_amount').val('');
    $('#tax_amount').val('');
    $('#tax_report_amount').val('');
    // Add action to save button
    $("#save-trs").attr("onclick", "addTransaction()");
    $("#MiscPayment_TransModal").modal("show");
    $('#line_number').val(trigger_line + 1);
    new_line = true;
}


// Add new transaction
function addTransaction() {
    var validate = checkTransaction();
    if (validate != "success") {
        //$("#transaction_error").text(validate);
        pop_ok_dialog("Error",
            validate,
            function () { });
    } else {
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
        var button = '<div class="btn-group dropup">'
            + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle set_line" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
            + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
            + '</button>'
            + '<ul class="dropdown-menu dropdown-menu-right">'
            + '<li><a onclick="editNewTransactionModal(' + line + ')">Edit</a></li>'
            + '<li><a onclick="deleteNewTransactionModal(' + line + ')">Delete</a></li>'
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
                button,
                "",
                transaction.distribution_id,
                transaction.account_id,
                transaction.is_tax_included,
                transaction.is_tax_transaction,
                transaction.tax_id,
                transaction.is_manual_tax_input,
                comma_format(transaction.base_tax_amount),
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

        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount * tax_reporting_rate));
        
        $("#id_total_amount").trigger('change');        // Get tax info
        

        // $("#MiscPayment_TransModal").modal("hide");
        showTransactionModal();
        $('button[type="submit"]').prop('disabled', false);
    }
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
    $("#save-trs").attr("onclick", "editNewTransaction(" + line + ")");
    $('#line_number').val(trigger_line);
    $("#MiscPayment_TransModal").modal("show");
}

// Save Update New Transaction
function editNewTransaction(line) {
    var validate = checkTransaction();
    if (validate == "success") {
        // Get Data from Transaction Form
        var transaction = getTransactionForm();

        // Update row data
        var datatbl = $('#misc-transaction-table').DataTable();
        row = trigger_row;
        var old_amount = datatbl.cell(row, $("#trs-amount").index()).data();
        // Draw data into table
        datatbl.cell(row, $("#trs-distribution_id").index()).data(transaction.distribution_id);
        datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
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
        datatbl.cell(row, $("#trs-tax_included").index()).data(transaction.is_tax_included);
        datatbl.cell(row, $("#trs-tax_transaction").index()).data(transaction.is_tax_transaction);
        datatbl.cell(row, $("#trs-tax_id").index()).data(transaction.tax_id);
        datatbl.cell(row, $("#trs-manual_tax_input").index()).data(transaction.is_manual_tax_input);
        datatbl.cell(row, $("#trs-base_tax_amount").index()).data(comma_format(transaction.base_tax_amount));
        datatbl.cell(row, $("#trs-row_number").index()).data(comma_format(line));
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
            result[0].distribution_id = transaction.distribution_id;
            result[0].distribution_code = transaction.distribution_code;
            result[0].account_id = transaction.account_id;
            result[0].account_code = transaction.account_code;
            result[0].account_name = filter_special_char(transaction.account_name);
            result[0].description = filter_special_char(transaction.description);
            result[0].amount = transaction.amount;
            result[0].tax_amount = transaction.tax_amount;
            result[0].total_amount = transaction.total_amount;
            result[0].is_tax_included = transaction.is_tax_included;
            result[0].is_tax_transaction = transaction.is_tax_transaction;
            result[0].tax_id = transaction.tax_id;
            result[0].is_manual_tax_input = transaction.is_manual_tax_input;
            result[0].base_tax_amount = transaction.base_tax_amount;
        }

        // // Get tax info
        // var tax = float_format($("#tax_value").val());

        // // Change Subtotal, Tax Amount, Total
        // var id_amount, subtotal;
        // if (old_amount > transaction.amount) {
        //     var sub = old_amount - transaction.amount;
        //     id_amount = float_format($("#id_amount").val());
        //     subtotal = float_format(id_amount - sub);
        // }
        // else {
        //     var add = transaction.amount - old_amount;
        //     id_amount = float_format($("#id_amount").val());
        //     subtotal = float_format(id_amount + add);
        // }
        // var taxamount = float_format((tax * subtotal) / 100);
        // var total = float_format(subtotal + taxamount);


        // $("#id_amount").val(subtotal.toFixed(2));
        // $("#id_tax_amount").val(taxamount.toFixed(2));
        // $("#id_total_amount").val(total.toFixed(2));
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

        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount * tax_reporting_rate));
        $("#id_total_amount").trigger('change');
        $("#MiscPayment_TransModal").modal("hide");
    }
    else {
        //$("#transaction_error").text(validate);
        pop_ok_dialog("Error",
            validate,
            function () { });
    }
}

// Show modal to edit old transation
function editOldTransactionModal(id, line, is_rec_entry) {
    // Reset form transaction
    $("#transaction_error").text("");
    $(".trs-field").val("");
    // Find object
    var result = $.grep(transaction_update, function (e) {
        return e.line == line;
    });
    // Not found object -> load from database
    if (result.length == 0) {
        // Load data of transaction
        if (is_rec_entry) {
            trx_url = '/accounting/get-re-detail-transaction/';
        } else {
            trx_url = '/transactions/get-info-transaction/';
        }

        $.ajax({
            method: "POST",
            url: trx_url,
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'transaction_id': id
            },
            success: function (data) {
                var transaction = new Transaction();
                transaction.distribution_id = data[0].distribution_id;
                transaction.distribution_code = data[0].distribution_code;
                transaction.distribution_name = data[0].distribution_desc;
                transaction.account_id = data[0].account_id_trs;
                transaction.account_code = data[0].account_code;
                transaction.account_name = filter_special_char(data[0].account_desc);
                transaction.description = filter_special_char(data[0].description);
                transaction.amount = float_format(data[0].amount);
                transaction.total_amount = float_format(data[0].total_amount);
                transaction.tax_amount = float_format(data[0].tax_amount);
                transaction.base_tax_amount = float_format(data[0].base_tax_amount);
                transaction.is_tax_included = data[0].is_tax_include;
                transaction.is_tax_transaction = data[0].is_tax_transaction;
                transaction.is_manual_tax_input = data[0].is_manual_tax_input;
                transaction.tax_id = data[0].tax_id;
                setTransactionForm(transaction);

                // disable when jounal was posted
                if (jrn_status == '2') {
                    $('#manual-tax').prop('disabled', true);
                    $('#tax-only-checkbox').prop('disabled', true);
                    $('#tax-checkbox').prop('disabled', true);
                }
            },
            error: function () {
                alert("Can't load Transaction");
            }
        });
    }
    // Found object -> show object
    else if (result.length == 1) {
        setTransactionForm(result[0]);
    }
    // Add action to save button
    $('#line_number').val(trigger_line);
    $("#save-trs").attr("onclick", "editOldTransaction(" + line + ")");
    $("#MiscPayment_TransModal").modal("show");
}

// Save Update Old Transaction
function editOldTransaction(line) {
    var validate = checkTransaction();
    if (validate == "success") {
        // Get Data from Transaction Form
        var transaction = getTransactionForm();

        // Update row data
        var datatbl = $('#misc-transaction-table').DataTable();
        row = trigger_row;
        var old_amount = datatbl.cell(row, $("#trs-amount").index()).data();
        // Draw data into table
        datatbl.cell(row, $("#trs-distribution_id").index()).data(transaction.distribution_id);
        datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
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
        datatbl.cell(row, $("#trs-tax_included").index()).data(transaction.is_tax_included);
        datatbl.cell(row, $("#trs-tax_transaction").index()).data(transaction.is_tax_transaction);
        datatbl.cell(row, $("#trs-tax_id").index()).data(transaction.tax_id);
        datatbl.cell(row, $("#trs-manual_tax_input").index()).data(transaction.is_manual_tax_input);
        datatbl.cell(row, $("#trs-base_tax_amount").index()).data(comma_format(transaction.base_tax_amount));
        datatbl.cell(row, $("#trs-row_number").index()).data(line);
        datatbl.draw();

        // Update old transaction list, not save in database
        transaction.line = line;
        transaction.row_number = line;
        // Find object
        var result = $.grep(transaction_update, function (e) {
            return e.line == line;
        });
        if (result.length == 0) {
            transaction_update.push(transaction);
        }
        else if (result.length == 1) {
            result[0].line = transaction.line;
            result[0].distribution_id = transaction.distribution_id;
            result[0].distribution_code = transaction.distribution_code;
            result[0].account_id = transaction.account_id;
            result[0].account_code = transaction.account_code;
            result[0].account_name = filter_special_char(transaction.account_name);
            result[0].description = filter_special_char(transaction.description);
            result[0].amount = transaction.amount;
            result[0].tax_amount = transaction.tax_amount;
            result[0].total_amount = transaction.total_amount;
            result[0].is_tax_included = transaction.is_tax_included;
            result[0].is_tax_transaction = transaction.is_tax_transaction;
            result[0].tax_id = transaction.tax_id;
            result[0].is_manual_tax_input = transaction.is_manual_tax_input;
            result[0].base_tax_amount = transaction.base_tax_amount;
        }


        // Get tax info
        var tax = float_format($("#tax_value").val());
        // Change Subtotal, Tax Amount, Total
        var id_amount, subtotal;
        if (old_amount > transaction.amount) {
            var sub = old_amount - transaction.amount;
            id_amount = float_format($("#id_amount").val());
            subtotal = float_format(id_amount - sub);
        }
        else {
            var add = transaction.amount - old_amount;
            id_amount = float_format($("#id_amount").val());
            subtotal = float_format(id_amount + add);
        }
        var taxamount = float_format((tax * subtotal) / 100);
        var total = float_format(subtotal + taxamount);


        calculate_value = recalculatePaymentAmount();
        if(bank_is_decimal) {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        } else {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        }

        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount * tax_reporting_rate));
        $("#id_total_amount").trigger('change');
        $("#MiscPayment_TransModal").modal("hide");
    }
    else {
        //$("#transaction_error").text(validate);
        pop_ok_dialog("Error",
            validate,
            function () { });
    }
}

$('#id_total_amount').on("change", function () {
    var document_amount = $('#id_document_amount').val();
    var total_dmount = $('#id_total_amount').val();
    var undistributed_amount = float_format(document_amount) - float_format(total_dmount);
    $('#undistributed_amount').val(comma_format(undistributed_amount));
    if ('True' == is_rec_entry) {
        $('#id_batch_amount').val($('#id_total_amount').val());
    }
});

// Show Comfirm delete old transaction
function deleteOldTransactionModal(line) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteOldTransaction(" + line + ")");
}

// Action when delete old transaction
function deleteOldTransaction(line) {
    var datatbl = $('#misc-transaction-table').DataTable();
    datatbl.rows(trigger_row).nodes().to$().addClass("delete");
    datatbl.cell(trigger_row, $("#trs-delete").index()).data("Delete");

    datatbl.row(trigger_row).remove().draw();

    calculate_value = recalculatePaymentAmount();

    // Update subtotal, tax amount, total
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
        $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
        $("#id_total_amount").val(comma_format(calculate_value.total_amount));
    } else {
        $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
        $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
        $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
    }

    $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount * tax_reporting_rate));
    $("#id_total_amount").trigger('change');
    var deleted_line = line;
    $.map(transaction_new, function(value, key) {
        if(value && value.line == deleted_line) {
            transaction_new.splice(key, 1);
            return true;
        }
    })

    // array_rows = [];
    // line_rd = 1;

    // datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     rowData = this.data();

    //     $.map(transaction_new, function(value, key) {
    //         if(value && value.line == rowData[0]) {
    //             transaction_new[key].line = line_rd;
    //             return true;
    //         }
    //     })

    //     rowData[0] = line_rd;

    //     if(rowData[9]) {
    //         button = '<div class="btn-group dropup">'
    //         + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
    //         + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
    //         + '</button>'
    //         + '<ul class="dropdown-menu dropdown-menu-right">'
    //         + '<li><a onclick="editOldTransactionModal('+ rowData[9] + ',' + line_rd + ')">Edit</a></li>'
    //         + '<li><a onclick="deleteOldTransactionModal(' + line_rd + ')">Delete</a></li>'
    //         + '</ul>'
    //         + '</div>';
    //     } else {
    //         button = '<div class="btn-group dropup">'
    //         + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
    //         + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
    //         + '</button>'
    //         + '<ul class="dropdown-menu dropdown-menu-right">'
    //         + '<li><a onclick="editNewTransactionModal(' + line_rd + ')">Edit</a></li>'
    //         + '<li><a onclick="deleteNewTransactionModal(' + line_rd + ')">Delete</a></li>'
    //         + '</ul>'
    //         + '</div>';
    //     }


    //     rowData[8] = button;
    //     array_rows.push(rowData);
    //     line_rd += 1 ;
    // });

    // datatbl.rows().remove().draw();
    // datatbl.rows.add(array_rows).draw();

    // reset line number
    resetLine();
    datatbl.draw();

    $("#active-" + line).hide();
    $("#deactive-" + line).show();
}

// Restore old Transaction
function restoreOldTransaction(line) {
    var datatbl = $('#misc-transaction-table').DataTable();
    datatbl.rows(line - 1).nodes().to$().removeClass("delete");
    datatbl.cell(line - 1, $("#trs-delete").index()).data("");

    // Load amount, tax amount, total amount of this row
    var subtotal_row = datatbl.cell(line - 1, $("#trs-amount").index()).data();
    subtotal_row = float_format(subtotal_row);
    var taxamount_row = datatbl.cell(line - 1, $("#trs-tax_amount").index()).data();
    taxamount_row = float_format(taxamount_row);
    var total_row = datatbl.cell(line - 1, $("#trs-total_amount").index()).data();
    total_row = float_format(total_row);
    //Load subtotal, tax amount, total of this journer
    var subtotal = float_format($("#id_amount").val());
    var taxamount = float_format($("#id_tax_amount").val());
    var total = float_format($("#id_total_amount").val());
    // Update subtotal, tax amount, total
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(subtotal+subtotal_row));
        $("#id_tax_amount").val(comma_format(taxamount+taxamount_row));
        $("#id_total_amount").val(comma_format(total+total_row));
    } else {
        $("#id_amount").val(comma_format(subtotal+subtotal_row));
        $("#id_tax_amount").val(comma_format(taxamount+taxamount_row));
        $("#id_total_amount").val(comma_format(total+total_row));
    }

    $("#id_tax_report_amount").val(comma_format((taxamount+taxamount_row) * tax_reporting_rate));
    $("#id_total_amount").trigger('change');

    $("#active-" + line).show();
    $("#deactive-" + line).hide();
}

// Show Comfirm delete new transaction
function deleteNewTransactionModal(line) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteNewTransaction(" + line + ")");
}

// Action when delete new transaction
function deleteNewTransaction(line) {
    var datatbl = $('#misc-transaction-table').DataTable();
    // Load amount, tax amount, total amount of this row
    var subtotal_row = datatbl.cell(trigger_row, $("#trs-amount").index()).data();
    subtotal_row = float_format(subtotal_row);
    var taxamount_row = datatbl.cell(trigger_row, $("#trs-tax_amount").index()).data();
    taxamount_row = float_format(taxamount_row);
    var total_row = datatbl.cell(trigger_row, $("#trs-total_amount").index()).data();
    total_row = float_format(total_row);
    //Load subtotal, tax amount, total of this journer
    var subtotal = float_format($("#id_amount").val());
    var taxamount = float_format($("#id_tax_amount").val());
    var total = float_format($("#id_total_amount").val());
    // Update subtotal, tax amount, total
    if(bank_is_decimal) {
        $("#id_amount").val(comma_format(subtotal-subtotal_row));
        $("#id_tax_amount").val(comma_format(taxamount-taxamount_row));
        $("#id_total_amount").val(comma_format(total-total_row));
    } else {
        $("#id_amount").val(comma_format(subtotal-subtotal_row, 0));
        $("#id_tax_amount").val(comma_format(taxamount-taxamount_row, 0));
        $("#id_total_amount").val(comma_format(total-total_row, 0));
    }

    $("#id_tax_report_amount").val(comma_format((taxamount-taxamount_row) * tax_reporting_rate));
    $("#id_total_amount").trigger('change');

    // Remove row
    // Remove row
    datatbl.row(trigger_row).remove().draw();
    var deleted_line = line;
    $.map(transaction_new, function(value, key) {
        if(value && value.line == deleted_line) {
            transaction_new.splice(key, 1);
            return true;
        }
    })

    // array_rows = [];
    // line_rd = 1;

    // datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     rowData = this.data();

    //     $.map(transaction_new, function(value, key) {
    //         if(value && value.line == rowData[0]) {
    //             transaction_new[key].line = line_rd;
    //             return true;
    //         }
    //     })

    //     rowData[0] = line_rd;



    //     button = '<div class="btn-group dropup">'
    //         + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
    //         + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
    //         + '</button>'
    //         + '<ul class="dropdown-menu dropdown-menu-right">'
    //         + '<li><a onclick="editNewTransactionModal(' + line_rd + ')">Edit</a></li>'
    //         + '<li><a onclick="deleteNewTransactionModal(' + line_rd + ')">Delete</a></li>'
    //         + '</ul>'
    //         + '</div>';

    //     rowData[8] = button;
    //     array_rows.push(rowData);
    //     line_rd += 1 ;
    // });

    // datatbl.rows().remove().draw();
    // datatbl.rows.add(array_rows).draw();

    // reset line number
    resetLine();
    datatbl.draw();
}

$("#id_distribution_code").on('change', function() {
    if($("#id_distribution_code").val() != '') {
        name = $(this).find(':selected').data('name');
        account_code = $(this).find(':selected').data('gl-account');
        if(name && name != 'undefined') {
            $('#distribution_desc').val(name);
            $("#description").val(filter_special_char(name));
        }
        if(account_code && account_code != 'undefined') {
            $('#id_account_code').val(account_code).trigger('change');
        }
    } else {
        $("#distribution_desc").val('');
        $("#description").val('');
        $('#id_account_code').val('').trigger('change');
    }
});

$("#id_account_code").on('change', function() {
    name = $(this).find(':selected').data('name');
    if(name != 'undefined') {
        $('#account_desc').val(filter_special_char(name));
    } else {
        $('#account_desc').val('');
    }
});

$("#tax-only-checkbox").on('change', function() {
    taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    if(taxOnly > 0) {
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
        $('#base_amount').val(comma_format(float_format($('#base_amount').val()), 0));
        $('#tax_amount').val(comma_format(float_format($('#tax_amount').val()), 0));
        $('#amount').val(comma_format(float_format($('#amount').val()), 0));
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
