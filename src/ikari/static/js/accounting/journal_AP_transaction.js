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
    // loadTax();
    // Reset form transaction
    $("#transaction_error").text("");
    var table = $('#transaction-table').DataTable();
    let row_count = table.rows().count();
    trigger_row = $('#transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
    trigger_line = parseInt(trigger_row.find("td:first").text());
    if (isNaN(trigger_line)) {
        trigger_line = 0;
    }
    trigger_row = null;

    tax_value = $('#tax_value').val();
    dis_code_id = $('#dis_code_id').val();
    $("#transaction_error").text("");
    $(".trs-field").val("");
    $('#id_account_code').val('').trigger('change');
    $('#id_distribution_code').val(dis_code_id).trigger('change');
    $('#manual-tax').prop('checked', false).trigger('change');
    $('#tax-checkbox').prop('checked', false);
    $('#tax-only-checkbox').prop('checked', false).trigger('change');
    $('#manual-tax').attr('disabled', true);
    $('#tax-checkbox').attr('disabled', true);
    $('#tax-only-checkbox').attr('disabled', true);
    $('#id_tax').val(tax_value).trigger('change');
    $('#base_amount').val('');
    $('#tax_amount').val('');
    $('#tax_report_amount').val('');
    // Add action to save button
    $("#save-trs").attr("onclick", "addTransaction()");
    $('#line_number').val(trigger_line + 1);
    $("#TransactionModal").modal("show");
    new_line = true;

    setTimeout(() => {
        $('#id_distribution_code').select2('open');
    }, 500);
}

$('#TransactionModal').on('hidden.bs.modal', function (ev) {
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

$('#TransactionModal').on('shown.bs.modal', function (ev) {
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

$('#id_tax').on('change', function(){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        if ($('#id_tax').val() && $('#id_tax').val() != '0'){
            $('#tax-checkbox').attr('disabled', false);
            $('#tax-only-checkbox').attr('disabled', false);
            $('#manual-tax').attr('disabled', false); 
        } else {
            $('#tax-checkbox').attr('disabled', true);
            $('#tax-only-checkbox').attr('disabled', true);
            $('#manual-tax').attr('disabled', true);
        }
    }
    // taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});

// function showTransactionModal() {
//     // loadTax();
//     // Reset form transaction
//     $("#transaction_error").text("");
//     $(".trs-field").val("");
//     $('#tax-checkbox').prop('checked', false);
//     // Add action to save button
//     $("#save-trs").attr("onclick", "addTransaction()")
//     $("#TransactionModal").modal("show");
// }

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
            {"data": "code", "sClass": "text-left"},
            {"data": "name", "sClass": "text-left"},
            {"data": "account_type", "sClass": "text-left"},
            {"data": "balance_type", "sClass": "text-left"},
            {"data": "amount", "orderable": false},
            {"data": "account_group", "sClass": "text-left"},
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

    var id =id ;
    // $.ajax({
    //     method: "GET",
    //     url: '/accounting/taxBySupplier/'+id,
    //     dataType: 'JSON',
    //     data: {
    //         // 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
    //         // 'tax_id': parseInt($('#id_tax').val()),
    //     },
    //     success: function (resp) {
            
    //         var tax_code = resp.tax_code;
    //         var id_distributor = resp.id_distributor;
    //         var tax_distribution_code_id = resp.tax_distribution_code_id;
    //         var tax_id = resp.tax_id;
    //         var tax_name = resp.tax_name;
    //         var tax_rate = resp.tax_rate;
    //     },
    //     error: function () {

    //     }
    // }); 
    $("#id_distribution_code").val(id).trigger('change');
    $("#id_account_code").val(account_id).trigger('change');
}

function selectAccount(id, code, name) {
    // $("#distribution_id").val("");
    // $("#id_distribution_code").val("");
    // $("#distribution_desc").val("");
    // $("#account_id_trs").val(id);
    // $("#id_account_code").val(code);
    // $("#account_desc").val(name);
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
    this.tax_id = null;
    this.is_tax_include = null;
    this.is_tax_transaction = null;
    this.base_tax_amount = null;
    this.is_manual_tax_input = null;
    this.row_number = null;
}

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
            transaction.is_tax_include = 0;
            transaction.is_tax_transaction = 1;
            transaction.amount = 0;
            transaction.base_tax_amount = base_tax_amount;
            transaction.tax_amount = tax_amount;
            transaction.total_amount = tax_amount;
        } else if (taxIncluded > 0) {
            transaction.is_tax_include = 1;
            transaction.is_tax_transaction = 0;
            transaction.amount = base_tax_amount;
            transaction.base_tax_amount = base_tax_amount;
            transaction.tax_amount = tax_amount;
            transaction.total_amount = base_tax_amount + tax_amount;
        } else {
            transaction.is_tax_include = 0;
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
            transaction.is_tax_include = 0;
            transaction.is_tax_transaction = 1;
        } else {
            if (taxIncluded > 0) {
                transaction.total_amount = amount;
                rate = rate / 100;
                transaction.amount = float_format(comma_format(amount / (1 + rate)));
                transaction.tax_amount = transaction.total_amount - transaction.amount;
                transaction.is_tax_include = 1;
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
                transaction.is_tax_include = 0;
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
    if ($('#id_currency').data("is_decimal") == false) {
        $("#tax_amount").val(comma_format(transaction.tax_amount, 0));
        $("#base_amount").val(comma_format(transaction.base_tax_amount, 0));
        $("#amount").val(comma_format(transaction.amount, 0));
    } else {
        $("#tax_amount").val(comma_format(transaction.tax_amount));
        $("#base_amount").val(comma_format(transaction.base_tax_amount));
        $("#amount").val(comma_format(transaction.amount));
    }
    $("#tax_report_amount").val(comma_format(transaction.tax_amount*tax_reporting_rate));
    if (transaction.is_manual_tax_input == 1) {
        $('#manual-tax').prop('checked', true).trigger('change');
        $('#manual-tax').attr('disabled', false);
        if(transaction.is_tax_transaction == 1){
            $("#tax-only-checkbox").prop('checked', true);
            $('#tax-only-checkbox').attr('disabled', false);
            if ($('#id_currency').data("is_decimal") == false) {
                $("#amount").val(comma_format(transaction.amount, 0));
            } else {
                $("#amount").val(comma_format(transaction.amount));
            }
        }
        if(transaction.is_tax_include == 1){
            $("#tax-checkbox").prop('checked', true);
            $('#tax-checkbox').attr('disabled', false);
            if ($('#id_currency').data("is_decimal") == false) {
                $("#amount").val(comma_format(transaction.total_amount, 0));
            } else {
                $("#amount").val(comma_format(transaction.total_amount));
            }
        }
        $('#tax-checkbox').attr('disabled', false);
        $("#id_tax").val(transaction.tax_id).trigger('change');
    } else {
        $('#manual-tax').prop('checked', false).trigger('change');
        if (transaction.is_tax_transaction == 1) {
            if ($('#id_currency').data("is_decimal") == false) {
                $("#amount").val(comma_format(transaction.amount, 0));
            } else {
                $("#amount").val(comma_format(transaction.amount));
            }
            $("#tax-only-checkbox").prop('checked', true).trigger('change');
            $('#tax-only-checkbox').attr('disabled', false);
        } else {
            $("#tax-only-checkbox").prop('checked', false).trigger('change');
            if (transaction.is_tax_include == 0) {
                if ($('#id_currency').data("is_decimal") == false) {
                    $("#amount").val(comma_format(transaction.amount, 0));
                } else {
                    $("#amount").val(comma_format(transaction.amount));
                }
                $("#tax-checkbox").prop('checked', false);
            }
            else if (transaction.is_tax_include == 1) {
                if ($('#id_currency').data("is_decimal") == false) {
                    $("#amount").val(comma_format(transaction.total_amount, 0));
                } else {
                    $("#amount").val(comma_format(transaction.total_amount));
                }
                $("#tax-checkbox").prop('checked', true);
                $('#tax-checkbox').attr('disabled', false);
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
    $('#transaction-table tbody tr').each(function (indx) {
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
        let row_count = $('#transaction-table').DataTable().rows().count();
        trigger_row = $('#transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
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
    let row_count = $('#transaction-table').DataTable().rows().count();
    trigger_row = $('#transaction-table tbody tr:nth-child('+row_count+')').closest('tr');
    loadRowForEdit();
    new_line = false;
}

function goFirst() {
    trigger_row = $('#transaction-table tbody tr:nth-child(1)').closest('tr');
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
            let trans_id = $('#transaction-table').DataTable().row( trigger_row ).data()[9];
            let line = $('#transaction-table').DataTable().row( trigger_row ).data()[18];
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
    dis_code_id = $('#dis_code_id').val();
    $("#transaction_error").text("");
    $(".trs-field").val("");
    $('#id_account_code').val('').trigger('change');
    //$('#id_distribution_code').val(dis_code_id).trigger('change');
    // $('#id_tax').val(tax_value).trigger('change');
    $('#id_tax').val('').trigger('change');
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
    $("#TransactionModal").modal("show");
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
        $("#transaction_error").text("");
        // Get Data from Transaction Form
        var transaction = getTransactionForm();
        if ($('#id_currency').data("is_decimal") == false) {
            transAmount = comma_format(transaction.amount, 0);
            transTax = comma_format(transaction.tax_amount, 0);
            transTamount = comma_format(transaction.total_amount, 0);
        } else {
            transAmount = comma_format(transaction.amount);
            transTax = comma_format(transaction.tax_amount);
            transTamount = comma_format(transaction.total_amount);
        }
        // Add new row into table
        var datatbl = $('#transaction-table').dataTable();
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
                transaction.tax_id,
                transaction.is_tax_include,
                transaction.is_tax_transaction,
                transaction.is_manual_tax_input,
                comma_format(transaction.base_tax_amount),
                "",
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

        calculate_value = recalculateInvoiceAmount();
        // Get tax info
        // Change Subtotal, Tax Amount, Total

        // var amount = float_format($("#id_amount").val()) + float_format(transaction.amount);
        // var tax_amount = float_format($("#id_tax_amount").val()) + float_format(transaction.tax_amount);
        // var total = float_format($("#id_total_amount").val()) + float_format(transaction.total_amount);

        if ($('#id_currency').data("is_decimal") == false) {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
        } else {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        }
        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount*tax_reporting_rate));

        $("#id_total_amount").trigger('change');

        // $("#TransactionModal").modal("hide");
        showTransactionModal();
    }
}

// Show modal to edit new transation
function editNewTransactionModal(line) {
    // loadTax();
    // Reset form transaction
    $("#transaction_error").text("");
    $(".trs-field").val("");
    // Find object
    var result = $.grep(transaction_new, function (e) {
        return e.line == line;
    });
    // Not found object -> return
    if (result.length == 0) {
        return 0;
    }
    // Found object -> show object
    else if (result.length == 1) {
        setTransactionForm(result[0]);
    }
    // Add action to save button
    $("#save-trs").attr("onclick", "editNewTransaction(" + line + ")");
    $('#line_number').val(trigger_line);
    $("#TransactionModal").modal("show");
}

// Save Update New Transaction
function editNewTransaction(line) {
    var validate = checkTransaction();
    if (validate == "success") {
        // Get Data from Transaction Form
        var transaction = getTransactionForm();

        // Update row data
        var datatbl = $('#transaction-table').DataTable();
        row = trigger_row;
        // var old_amount = datatbl.cell(row, $("#trs-amount").index()).data();
        // var old_tax_amount = datatbl.cell(row, $("#trs-tax_amount").index()).data();
        // var old_total_amount = datatbl.cell(row, $("#trs-total_amount").index()).data();

        // Draw data into table
        datatbl.cell(row, $("#trs-distribution_id").index()).data(transaction.distribution_id);
        datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
        datatbl.cell(row, $("#trs-account_code").index()).data(transaction.account_code);
        datatbl.cell(row, $("#trs-account_name").index()).data(filter_special_char(transaction.account_name));
        if ($('#id_currency').data("is_decimal") == false) {
            datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount, 0));
            datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount, 0));
            datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount, 0));
        } else {
            datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount));
            datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount));
            datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount));
        }
        datatbl.cell(row, $("#trs-tax_id").index()).data(transaction.tax_id);
        datatbl.cell(row, $("#trs-tax_include").index()).data(transaction.is_tax_include);
        datatbl.cell(row, $("#trs-tax_transaction").index()).data(transaction.is_tax_transaction);
        datatbl.cell(row, $("#trs-manual_tax_input").index()).data(transaction.is_manual_tax_input);
        datatbl.cell(row, $("#trs-base_tax_amount").index()).data(comma_format(transaction.base_tax_amount));
        datatbl.cell(row, $("#trs-row_number").index()).data(line);
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
            result[0].tax_id = transaction.tax_id;
            result[0].is_tax_include = transaction.is_tax_include;
            result[0].is_tax_transaction = transaction.is_tax_transaction;
            result[0].is_manual_tax_input = transaction.is_manual_tax_input;
            result[0].base_tax_amount = transaction.base_tax_amount;
        }

        // Get tax info
        // var tax = float_format($("#tax_value").val());
        // var tax_rate = float_format($('#id_tax').find(':selected').data('rate'));
        // Change Subtotal, Tax Amount, Total
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
        // var taxamount = float_format((tax_rate * subtotal) / 100);
        // var total = float_format(subtotal + taxamount);


        calculate_value = recalculateInvoiceAmount();
        if ($('#id_currency').data("is_decimal") == false) {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
        } else {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        }
        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount*tax_reporting_rate));
        $("#id_total_amount").trigger('change');

        $("#TransactionModal").modal("hide");
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
        // loadTax();
        // Load data of transaction
        if(is_rec_entry){
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
                transaction.tax_amount = float_format(data[0].tax_amount);
                transaction.total_amount = float_format(data[0].total_amount);
                transaction.base_tax_amount = float_format(data[0].base_tax_amount);
                transaction.tax_id = data[0].tax_id;
                transaction.is_tax_include = data[0].is_tax_include;
                transaction.is_tax_transaction = data[0].is_tax_transaction;
                transaction.is_manual_tax_input = data[0].is_manual_tax_input;
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
    // calculate_value = recalculateInvoiceAmount();

    $('#line_number').val(trigger_line);
    $("#save-trs").attr("onclick", "editOldTransaction(" + line + ")");
    $("#TransactionModal").modal("show");
}

// Save Update Old Transaction
function editOldTransaction(line) {
    var validate = checkTransaction();
    if (validate == "success") {
        // Get Data from Transaction Form
        var transaction = getTransactionForm();

        // Update row data
        var datatbl = $('#transaction-table').DataTable();
        row = trigger_row;
        var old_amount = datatbl.cell(row, $("#trs-amount").index()).data();
        // var old_tax_amount = datatbl.cell(row, $("#trs-tax_amount").index()).data();
        // var old_total_amount = datatbl.cell(row, $("#trs-total_amount").index()).data();

        // Draw data into table
        datatbl.cell(row, $("#trs-distribution_id").index()).data(transaction.distribution_id);
        datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
        datatbl.cell(row, $("#trs-account_code").index()).data(transaction.account_code);
        datatbl.cell(row, $("#trs-account_name").index()).data(filter_special_char(transaction.account_name));
        if ($('#id_currency').data("is_decimal") == false) {
            datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount, 0));
            datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount, 0));
            datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount, 0));
        } else {
            datatbl.cell(row, $("#trs-amount").index()).data(comma_format(transaction.amount));
            datatbl.cell(row, $("#trs-tax_amount").index()).data(comma_format(transaction.tax_amount));
            datatbl.cell(row, $("#trs-total_amount").index()).data(comma_format(transaction.total_amount));
        }
        datatbl.cell(row, $("#trs-tax_id").index()).data(transaction.tax_id);
        datatbl.cell(row, $("#trs-tax_include").index()).data(transaction.is_tax_include);
        datatbl.cell(row, $("#trs-tax_transaction").index()).data(transaction.is_tax_transaction);
        datatbl.cell(row, $("#trs-manual_tax_input").index()).data(transaction.is_manual_tax_input);
        datatbl.cell(row, $("#trs-base_tax_amount").index()).data(comma_format(transaction.base_tax_amount));
        datatbl.cell(row, $("#trs-row_number").index()).data(line);
        datatbl.draw();
        // // Draw data into table
        // datatbl.cell(row, $("#trs-distribution_id").index()).data(transaction.distribution_id);
        // datatbl.cell(row, $("#trs-distribution_code").index()).data(transaction.distribution_code);
        // datatbl.cell(row, $("#trs-description").index()).data(transaction.description);
        // datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
        // datatbl.cell(row, $("#trs-account_code").index()).data(transaction.account_code);
        // datatbl.cell(row, $("#trs-account_name").index()).data(transaction.account_name);
        // datatbl.cell(row, $("#trs-amount").index()).data(transaction.amount.toFixed(6));
        // datatbl.cell(row, $("#trs-tax_amount").index()).data(transaction.tax_amount.toFixed(6));
        // datatbl.cell(row, $("#trs-total_amount").index()).data(transaction.total_amount.toFixed(6));
        // datatbl.cell(row, $("#trs-tax_id").index()).data(transaction.tax_id);
        // datatbl.cell(row, $("#trs-tax_include").index()).data(transaction.is_tax_include);
        // datatbl.draw();

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
            result[0].tax_id = transaction.tax_id;
            result[0].is_tax_include = transaction.is_tax_include;
            result[0].is_tax_transaction = transaction.is_tax_transaction;
            result[0].is_manual_tax_input = transaction.is_manual_tax_input;
            result[0].base_tax_amount = transaction.base_tax_amount;
        }


        // Get tax rate
        var tax_rate = float_format($('#id_tax').find(':selected').data('rate'));
        // var tax = float_format($("#tax_value").val());
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
        var taxamount = float_format((tax_rate * subtotal) / 100);
        var total = float_format(subtotal + taxamount);


        calculate_value = recalculateInvoiceAmount();
        if ($('#id_currency').data("is_decimal") == false) {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
        } else {
            $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
            $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
            $("#id_total_amount").val(comma_format(calculate_value.total_amount));
        }
        $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount*tax_reporting_rate));
        $("#id_total_amount").trigger('change');

        $("#TransactionModal").modal("hide");
    }
    else {
        //$("#transaction_error").text(validate);
        pop_ok_dialog("Error",
            validate,
            function () { });
    }
}

$('#id_total_amount').on("change", function () {
    $('#id_document_amount').val($('#id_total_amount').val()).trigger('change');
    recalculateUndistributedAmount();
    if ('True' == is_rec_entry){
        $('#id_batch_amount').val($('#id_total_amount').val());
    }
    if (float_format($(this).val()) < 0) {
        setTimeout(() => {
            $('#btnSaveAPEntry').prop('disabled', true);
        }, 500);
        
    }
});

// Show Comfirm delete old transaction
function deleteOldTransactionModal(line) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteOldTransaction(" + line + ")");
}

// Action when delete old transaction
function deleteOldTransaction(line) {
    var datatbl = $('#transaction-table').DataTable();
    datatbl.rows(trigger_row).nodes().to$().addClass("delete");
    datatbl.cell(trigger_row, $("#trs-delete").index()).data("Delete");


    datatbl.row(trigger_row).remove().draw();

    // Load amount, tax amount, total amount of this row
    // var subtotal_row = datatbl.cell(line - 1, $("#trs-amount").index()).data();
    // subtotal_row = float_format(subtotal_row);
    // var taxamount_row = datatbl.cell(line - 1, $("#trs-tax_amount").index()).data();
    // taxamount_row = float_format(taxamount_row);
    // var total_row = datatbl.cell(line - 1, $("#trs-total_amount").index()).data();
    // total_row = float_format(total_row);
    // //Load subtotal, tax amount, total of this journer
    // var subtotal = float_format($("#id_amount").val());
    // var taxamount = float_format($("#id_tax_amount").val());
    // var total = float_format($("#id_total_amount").val());
    // Update subtotal, tax amount, total
    calculate_value = recalculateInvoiceAmount();

    // Update subtotal, tax amount, total
    if ($('#id_currency').data("is_decimal") == false) {
        $("#id_amount").val(comma_format(calculate_value.subtotal_amount, 0));
        $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount, 0));
        $("#id_total_amount").val(comma_format(calculate_value.total_amount, 0));
    } else {
        $("#id_amount").val(comma_format(calculate_value.subtotal_amount));
        $("#id_tax_amount").val(comma_format(calculate_value.total_tax_amount));
        $("#id_total_amount").val(comma_format(calculate_value.total_amount));
    }
    $("#id_tax_report_amount").val(comma_format(calculate_value.total_tax_amount*tax_reporting_rate));
    $("#id_total_amount").trigger('change');

    var deleted_line = line;
    $.map(transaction_new, function (value, key) {
        if (value && value.line == deleted_line) {
            transaction_new.splice(key, 1);
            return true;
        }
    })

    // array_rows = [];
    // line_rd = 1;

    // datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     rowData = this.data();

    //     $.map(transaction_new, function (value, key) {
    //         if (value && value.line == rowData[0]) {
    //             transaction_new[key].line = line_rd;
    //             return true;
    //         }
    //     })

    //     rowData[0] = line_rd;

    //     if (rowData[9]) {
    //         button = '<div class="btn-group dropup">'
    //             + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
    //             + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
    //             + '</button>'
    //             + '<ul class="dropdown-menu dropdown-menu-right">'
    //             + '<li><a onclick="editOldTransactionModal(' + rowData[9] + ',' + line_rd + ')">Edit</a></li>'
    //             + '<li><a onclick="deleteOldTransactionModal(' + line_rd + ')">Delete</a></li>'
    //             + '</ul>'
    //             + '</div>';
    //     } else {
    //         button = '<div class="btn-group dropup">'
    //             + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
    //             + '<span class="caret" style="margin-left:15px"></span><span class="sr-only">Toggle Dropdown</span>'
    //             + '</button>'
    //             + '<ul class="dropdown-menu dropdown-menu-right">'
    //             + '<li><a onclick="editNewTransactionModal(' + line_rd + ')">Edit</a></li>'
    //             + '<li><a onclick="deleteNewTransactionModal(' + line_rd + ')">Delete</a></li>'
    //             + '</ul>'
    //             + '</div>';
    //     }


    //     rowData[8] = button;
    //     array_rows.push(rowData);
    //     line_rd += 1;
    // });

    // datatbl.rows().remove().draw();
    // datatbl.rows.add(array_rows).draw();
    
    // reset line number
    resetLine();
    datatbl.draw();
    recalculateUndistributedAmount();

    $("#active-" + line).hide();
    $("#deactive-" + line).show();

}

// Restore old Transaction
function restoreOldTransaction(line) {
    var datatbl = $('#transaction-table').DataTable();
    datatbl.rows(trigger_row).nodes().to$().removeClass("delete");
    datatbl.cell(trigger_row, $("#trs-delete").index()).data("");

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
    if ($('#id_currency').data("is_decimal") == false) {
        $("#id_amount").val(comma_format(subtotal + subtotal_row, 0));
        $("#id_tax_amount").val(comma_format(taxamount + taxamount_row, 0));
        $("#id_total_amount").val(comma_format(total + total_row, 0));
    } else {
        $("#id_amount").val(comma_format(subtotal + subtotal_row));
        $("#id_tax_amount").val(comma_format(taxamount + taxamount_row));
        $("#id_total_amount").val(comma_format(total + total_row));
    }
    $("#id_tax_report_amount").val(comma_format((taxamount + taxamount_row)*tax_reporting_rate));
    $('#id_total_amount').trigger('change');

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
    var datatbl = $('#transaction-table').DataTable();
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
    if ($('#id_currency').data("is_decimal") == false) {
        $("#id_amount").val(comma_format(subtotal - subtotal_row, 0));
        $("#id_tax_amount").val(comma_format(taxamount - taxamount_row, 0));
        $("#id_total_amount").val(comma_format(total - total_row, 0));
    } else {
        $("#id_amount").val(comma_format(subtotal - subtotal_row));
        $("#id_tax_amount").val(comma_format(taxamount - taxamount_row));
        $("#id_total_amount").val(comma_format(total - total_row));
    }
    $("#id_tax_report_amount").val(comma_format((taxamount - taxamount_row)*tax_reporting_rate));
    $('#id_total_amount').trigger('change');

    // Remove row
    datatbl.row(trigger_row).remove().draw();
    var deleted_line = line;
    $.map(transaction_new, function (value, key) {
        if (value && value.line == deleted_line) {
            transaction_new.splice(key, 1);
            return true;
        }
    })

    // array_rows = [];
    // line_rd = 1;

    // datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
    //     rowData = this.data();

    //     $.map(transaction_new, function (value, key) {
    //         if (value && value.line == rowData[0]) {
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
    //     line_rd += 1;
    // });

    // datatbl.rows().remove().draw();
    // datatbl.rows.add(array_rows).draw();

    // reset line number
    resetLine();
    datatbl.draw();
    recalculateUndistributedAmount();

}
$("#id_distribution_code").on('change', function () {
    if($("#id_distribution_code").val() != '') {
        name = $(this).find(':selected').data('name');
        account_code = $(this).find(':selected').data('gl-account');
        tax_id = $(this).find(':selected').data('tax_id');
        if (name && name != 'undefined') {
            $('#distribution_desc').val(name);
            $("#description").val(filter_special_char(name));
        }
        if (account_code && account_code != 'undefined') {
            $('#id_account_code').val(account_code).trigger('change');
        }
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

//------validate amount-------//
function recalculateInvoiceAmount() {
    total_amount = 0.000000;
    subtotal_amount = 0.000000;
    total_tax_amount = 0.000000;
    calculate_value = {};

    var datatbl = $('#transaction-table').DataTable();
    datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {

        tt_amount = datatbl.cell(rowIdx, $("#trs-total_amount").index()).data();
        st_amount = datatbl.cell(rowIdx, $("#trs-amount").index()).data();
        tax_amount = datatbl.cell(rowIdx, $("#trs-tax_amount").index()).data();
        // int_tt_amount = tt_amount.replace(/,/g , '');
        // int_st_amount = st_amount.replace(/,/g , '');
        // int_tax_amount = tax_amount.replace(/,/g , '');
        total_amount += float_format(tt_amount);
        subtotal_amount += float_format(st_amount);
        total_tax_amount += float_format(tax_amount);
    });
    calculate_value.total_amount = float_format((total_amount).toFixed(3));
    calculate_value.subtotal_amount = float_format((subtotal_amount).toFixed(3));
    calculate_value.total_tax_amount = float_format((total_tax_amount).toFixed(3));

    return calculate_value;
}

$("#tax-only-checkbox").on('change', function () {
    var taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    if (taxOnly > 0) {
        $('#tax-checkbox').prop('checked', false);
        $('#tax-checkbox').prop('disabled', true);
        $('#manual-tax').prop('checked', true).trigger('change');
    } else {
        $('#tax-checkbox').prop('disabled', false);
    }
    var taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});

$("#tax-checkbox").on('change', function () {
    var taxincl = $('#tax-checkbox:checkbox:checked').length;
    if (taxincl > 0) {
        $('#tax-only-checkbox').prop('checked', false);
        $('#tax-only-checkbox').prop('disabled', true);
    } else {
        $('#tax-only-checkbox').prop('disabled', false);
    }
    var taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman == 0) {
        $('#amount').trigger('change');
    }
});

$("#manual-tax").on('change', function () {
    var taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        $('#base_amount').prop('disabled', false);
        $('#tax_amount').prop('disabled', false);
    } else {
        $('#tax-only-checkbox').prop('disabled', false);
        $('#tax-checkbox').prop('disabled', false);
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

    // id_currency get from AR_entry.html
    if ($('#id_currency').data("is_decimal") == false) {
        $('#amount').val(comma_format(float_format($('#amount').val()), 0));
        $('#base_amount').val(comma_format(float_format($('#base_amount').val()), 0));
        $('#tax_amount').val(comma_format(float_format($('#tax_amount').val()), 0));
    } else {
        $('#amount').val(comma_format(float_format($('#amount').val())));
    }
    $('#tax_report_amount').val(comma_format(float_format($('#tax_amount').val())*tax_reporting_rate));

});

$('#base_amount').on('change', function(e){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        if ($('#id_currency').data("is_decimal") == false) {
            $('#base_amount').val(comma_format(float_format($('#base_amount').val()), 0));
        } else {
            $('#base_amount').val(comma_format(float_format($('#base_amount').val())));
        }
    }
});

$('#tax_amount').on('change', function(e){
    taxman = $('#manual-tax:checkbox:checked').length;
    if (taxman > 0) {
        if ($('#id_currency').data("is_decimal") == false) {
            $('#tax_amount').val(comma_format(float_format($('#tax_amount').val()), 0));
        } else {
            $('#tax_amount').val(comma_format(float_format($('#tax_amount').val())));
        }
        $('#tax_report_amount').val(comma_format(float_format($('#tax_amount').val())*tax_reporting_rate));
    }
});