var transaction_new = [];
var transaction_update = [];
var special_trx = false;
var trigger_row;
var trigger_line = 1;
var new_line = false;
var g_curr_id = '';
var old_trx = false; //for not to trigger currency in old transaction load

var journal_desc = $("#id_name").val();
var journal_date = $("#document_date").val();
// var journal_srccode = $("#txtsource_code").val();
var journal_srccode = $("#source_type").val();
var header_data = {
    "journal_desc":journal_desc,
    "journal_date":journal_date,
    "journal_srccode":journal_srccode
};

function setHeaderData(p1,p2,p3){
    header_data["journal_desc"]=p1;
    header_data["journal_date"]=p2;
    header_data["journal_srccode"]=p3;
}

function clearTransactionForm(new_entry=false)
{
    $('#id_auto_exch').prop('checked', false).trigger('change');
    $("#txtref").val("");
    $("#txtdesc").val("");
    $("#txtaccid").val("");
    $("#txtacccode").val("");
    $("#account_desc").val("");
    $('#curr_code').prop('selectedIndex', 0);
    $('#curr_name').html("");
    $("#txtsrcdebit").val('0.00');
    $("#txtsrccredit").val('0.00');
    $("#txtexcrate").val('1.00000000');
    $("#txtexcdate").val("");
    $("#txtfuncdebit").val('0.00');
    $("#txtfunccredit").val('0.00');
    $("#txtcomment").val("");
    $("#div_transaction_error").removeClass('hide_column');
    $("#div_transaction_error").addClass('hide_column');
    $("#error_msg2").removeClass('hide_column');
    $("#error_msg2").addClass('hide_column');
    $("#error_msg2").removeClass('hide_column');
    $("#error_msg2").addClass('hide_column');
    $("#error_msg3").removeClass('hide_column');
    $("#error_msg3").addClass('hide_column');
    $("#div_journal_errorr").addClass('hide_column');
}

// Check form Transaction before save
function checkTransaction() {
    var reference = $("#txtref").val();
    var accid = $("#txtacccode").val();
    if (!accid) {
        $( "#txtacccode" ).focus();
        return "Please fill Account Id";
    }
    var currency = $("#curr_code").val();
    var company_currency = $('#company_curr_id').val();

    var is_auto_exch = $('#id_auto_exch:checkbox:checked').length;
    if (is_auto_exch) {
        special_trx = true;
    } else {
        special_trx = false;
    }

    var srcdebit = $("#txtsrcdebit").val();
    var srccredit = $("#txtsrccredit").val();
    if (!special_trx) {
        if ((srcdebit=='0.00'||srcdebit=='0'||srcdebit=='')&&(srccredit=='0.00'||srccredit=='0'||srccredit=='')) {
            $("#txtsrcdebit").focus();
            $("#txtsrcdebit").select();
            return "Please fill Source Debit or Source Credit";
        }
    }
    if (special_trx && currency == company_currency) {
        if ((srcdebit=='0.00'||srcdebit=='0'||srcdebit=='')&&(srccredit=='0.00'||srccredit=='0'||srccredit=='')) {
            $("#txtsrcdebit").focus();
            $("#txtsrcdebit").select();
            return "Please fill Source Debit or Source Credit";
        }
    }

    var exchrate = $("#txtexcrate").val();
    if (exchrate=='0'||exchrate=='') {
        $("#txtexcrate").focus();
        $("#txtexcrate").select();
        return "Please fill Exchange Rate";
    }

    return "success";
}

function Transaction() {
    this.line = null;
    this.reference = null;
    this.description = null;
    this.account_id = null;
    this.account_code = null;
    this.account_name = null;
    this.currency_id = null;
    this.currency_code = null;
    this.srcdebit = '0';
    this.srccredit = '0';
    this.exchange_rate = '0';
    this.funcdebit = '0';
    this.funccredit = '0';
    this.comment = null;
    this.is_auto_exch = null;
    this.rate_date = '';
    this.is_decimal = true;
    this.row_number = '';
}

function SaveData() {
    var url = $('#btnSaveJournal').data("url");
    array = [];
    array.length = 0;
    $('#transaction_list_data').val(JSON.stringify(array));
    trxdebits = Math.abs(float_format($('#txttrxdebits').val()).toFixed(2));
    trxcredits = Math.abs(float_format($('#txttrxcredits').val()).toFixed(2));
    unbalance = Math.abs(Math.abs(trxdebits-trxcredits).toFixed(2));
    trxdebits_dup = $('#txttrxdebits').val();
    $("#frmglentry").submit(function(e){
        array = [];
        array.length = 0;
        if (trxdebits == 0 && trxcredits == 0){
            setTimeout(function(){
                $("#div_journal_errorr").removeClass('hide_column');
                $('#journal_error').text('No Transaction records found. Cannot Save this journal entry');
                $('#btnSaveJournal').prop('disabled', false);
            }, 200);
            $('#loading').hide();
            e.preventDefault();
        } else if ((trxdebits != trxcredits) || unbalance > 0) {
            setTimeout(function () {
                $("#div_journal_errorr").removeClass('hide_column');
                $('#journal_error').text('You must balance Debit & Credit');
                $('#btnSaveJournal').prop('disabled', false);
            }, 200);
            $('#loading').hide();
            e.preventDefault();
        } else {
            // setTimeout(function(){
                array = [];
                array.length = 0;
                var table = $('#dynamic-table').DataTable();
                table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                    rowData = this.data();
                    transaction_list = {};
                    transaction_list.reference = filter_special_char(rowData[$("#trs-reference").index()]);
                    if (!transaction_list.reference){
                        transaction_list.reference = '';
                    }
                    transaction_list.description = filter_special_char(rowData[$("#trs-description").index()]);
                    if (!transaction_list.description){
                        transaction_list.description = '';
                    }

                    srcdebit= rowData[$("#trs-srcdebit").index()].replace(/,/g , '');
                    srccredit= rowData[$("#trs-srccredit").index()].replace(/,/g , '');
                    funcdebit= rowData[$("#trs-funcdebit").index()].replace(/,/g , '');
                    funccredit= rowData[$("#trs-funccredit").index()].replace(/,/g , '');
                    srcdebit= rowData[$("#trs-srcdebit").index()].replace(/,/g , '');

                    transaction_list.srcdebit = float_format(srcdebit).toFixed(2);
                    transaction_list.srccredit = float_format(srccredit).toFixed(2);
                    transaction_list.exchange_rate = float_format(rowData[$("#trs-exchange_rate").index()]).toFixed(10);
                    transaction_list.funcdebit = float_format(funcdebit).toFixed(2);
                    transaction_list.funccredit = float_format(funccredit).toFixed(2);
                    transaction_list.comment = rowData[$("#trs-comment").index()];
                    transaction_list.id = rowData[$("#trs-id").index()];
                    transaction_list.account_id = rowData[$("#trs-account_id").index()];
                    transaction_list.currency_id = rowData[$("#trs-currency_id").index()];
                    transaction_list.rate_date = String(rowData[$("#trs-rate_date").index()]).split('-').reverse().join('-');

                    if (rowData[$("#trs-is_auto_exch").index()]) {
                        transaction_list.is_auto_exch = 1;
                    } else {
                        transaction_list.is_auto_exch = 0;
                    }
                    if ((transaction_list.srcdebit>0.000000)||(transaction_list.funcdebit>0.000000)){
                        transaction_list.is_debit_account = 1;
                        transaction_list.is_credit_account = 0;
                    } else {
                        transaction_list.is_debit_account = 0;
                        transaction_list.is_credit_account = 1;
                    }
                    array.push(transaction_list);
                });
                $('#transaction_list_data').val(JSON.stringify(array));

                // unbalance journal amount is not allowed to saved as 'journal amount'
                // otherwise then just get debit/credit amount as 'journal amount' since the both side debit and credit is surely at same amount
                var journal_amt = 0;
                if (unbalance<=0.000000){
                    journal_amt = trxdebits_dup;
                }
                var new_total_amt = journal_amt.replace(/,/g , '');
                $('#total_amt').val(new_total_amt);
            // }, 100);
            return;
        }
    });
}

var last_reference = '';
var last_description = '';

// Get Data from Trasaction Form
function getTransactionForm() {
    var transaction = new Transaction();
    if($("#txtref").val() != '') {
        transaction.reference = $("#txtref").val();
        last_reference = $("#txtref").val();
    }
    if($("#txtdesc").val() != '') {
        transaction.description = filter_special_char($("#txtdesc").val());
        last_description = filter_special_char($("#txtdesc").val());
    }
    if($("#txtacccode").val() != '') {
        transaction.account_id = $("#txtaccid").val();
        // transaction.account_code = $("#txtacccode").val();
        transaction.account_code = $("#txtacccode option:selected").text();
        transaction.account_name = $("#account_desc").val();
    }
    if($("#curr_code").val() != '') {
        transaction.currency_id = $("#curr_code").val();
        transaction.currency_code = $('#curr_code option:selected').text();
    }
    if($("#txtsrcdebit").val() != '0') {
        transaction.srcdebit = float_format($("#txtsrcdebit").val()).toFixed(2);
    }
    if($("#txtsrccredit").val() != '0') {
        transaction.srccredit = float_format($("#txtsrccredit").val()).toFixed(2);
    }
    if($("#txtexcrate").val() != '0') {
        transaction.exchange_rate = float_format($("#txtexcrate").val()).toFixed(10);
    }
    if (!special_trx) {
        if(!is_decimal) {
            transaction.funcdebit = (float_format(transaction.srcdebit)*float_format(transaction.exchange_rate)).toFixed(0);
            transaction.funccredit = (float_format(transaction.srccredit)*float_format(transaction.exchange_rate)).toFixed(0);
        } else {
            transaction.funcdebit = (float_format(transaction.srcdebit)*float_format(transaction.exchange_rate)).toFixed(2);
            transaction.funccredit = (float_format(transaction.srccredit)*float_format(transaction.exchange_rate)).toFixed(2);
        }
    } else {
        if(!is_decimal) {
            transaction.funcdebit = float_format($("#txtfuncdebit").val()).toFixed(0);
            transaction.funccredit = float_format($("#txtfunccredit").val()).toFixed(0);
        } else {
            transaction.funcdebit = float_format($("#txtfuncdebit").val()).toFixed(2);
            transaction.funccredit = float_format($("#txtfunccredit").val()).toFixed(2);
        }
    }
    transaction.comment = $("#txtcomment").val();
    transaction.is_auto_exch = $('#id_auto_exch:checkbox:checked').length;
    transaction.rate_date = $('#txtexcdate').val();
    return transaction;
}

function setTransactionForm(transaction) {
    if (transaction.is_debit_account){
        src_amt = float_format(transaction.srcdebit);
        func_amt = float_format(transaction.funcdebit);
        if (src_amt == 0 && func_amt > 0) {
            special_trx = true;
        } else {
            special_trx = false;
        }
    } else {
        src_amt = float_format(transaction.srccredit);
        func_amt = float_format(transaction.funccredit);
        if (src_amt == 0 && func_amt > 0) {
            special_trx = true;
        } else {
            special_trx = false;
        }
    }
    g_curr_id = transaction.currency_id;
    $("#txtref").val(filter_special_char(transaction.reference));
    $("#txtdesc").val(filter_special_char(transaction.description));
    $("#txtaccid").val(transaction.account_id);
    // $("#txtacccode").val(transaction.account_code).trigger('focusout');
    $("#txtacccode").val(transaction.account_id).trigger('change');
    $('#curr_code').val(transaction.currency_id).trigger('change');
    old_trx = false;
    is_currency_decimal = transaction.is_decimal;

    if (transaction.is_debit_account){
        if (is_currency_decimal){
            $("#txtsrcdebit").val(comma_format(transaction.srcdebit));
            $("#txtsrccredit").val('0.00');
        } else {
            $("#txtsrcdebit").val(comma_format(transaction.srcdebit, 0));
            $("#txtsrccredit").val('0');
        }
    } else {
        if (is_currency_decimal){
            $("#txtsrcdebit").val('0.00');
            $("#txtsrccredit").val(comma_format(transaction.srccredit));
        } else {
            $("#txtsrcdebit").val('0');
            $("#txtsrccredit").val(comma_format(transaction.srccredit, 0));
        }
    }

    if (transaction.is_debit_account){
        $("#txtfuncdebit").val(comma_format(transaction.funcdebit));
        $("#txtfunccredit").val('0.00');
    } else {
        $("#txtfuncdebit").val('0.00');
        $("#txtfunccredit").val(comma_format(transaction.funccredit));
    }
    $("#txtcomment").val(filter_special_char(transaction.comment));
    $("#txtexcdate").val(transaction.rate_date);
    setTimeout(function(){
        $("#txtexcrate").val(float_format(transaction.exchange_rate).toFixed(10)).trigger('change');
    }, 100);

    if(transaction.is_auto_exch > 0) {
        $('#id_auto_exch').prop('checked', true).trigger('change');
        $('#btnOpentExchRateDialog').prop('disabled', true);
        $('#txtexcrate').prop('disabled', true);
    } else {
        $('#id_auto_exch').prop('checked', false).trigger('change');
        $('#btnOpentExchRateDialog').prop('disabled', false);
        $('#txtexcrate').prop('disabled', false);
    }

    var form_state = parseInt($('#input_state').val());
    if (form_state == 2) {
        $('[name="txtexcrate"]').prop('disabled', true);
        $('[name="id_auto_exch"]').prop('disabled', true);
        $('#txtfuncdebit').prop('disabled', true);
        $('#txtfunccredit').prop('disabled', true);
    }
}

function showTransactionModal(line = '') {
    // for new transaction when click 'Plus button'
    var table = $('#dynamic-table').DataTable();
    let row_count = table.rows().count();
    trigger_row = $('#dynamic-table tbody tr:nth-child('+row_count+')').closest('tr');
    trigger_line = parseInt(trigger_row.find("td:first").text());
    if (isNaN(trigger_line)) {
        trigger_line = 0;
    }
    trigger_row = null;

    var acccode_val = $('#txtacccode').val();
    clearTransactionForm(true);

    if(entry_mode == '2') {
        if (line != '') {
            var result = $.grep(transaction_mix, function (e) {
                return e.line == line;
            });
            $("#txtdesc").val(filter_special_char(result[0].description));
            $("#txtref").val(filter_special_char(result[0].reference));
        } else {
            $("#txtdesc").val(filter_special_char(last_description));
            $("#txtref").val(filter_special_char(last_reference));
        }
    }
    $("#save-trs").attr("onclick", "addTransaction()");
    // for new transaction when click 'Plus button'
    if (line == '' && acccode_val) {
        $('#txtacccode').val(acccode_val).trigger("change");
    }
    $("#AddTransModal").modal("show");
    //$("#curr_code").select2();
    //$('#curr_code').empty().select2();
    $('#line_number').val(trigger_line + 1);
    new_line = true;
    if (line == ''){
        old_trx = false;
    }
}

$('#AddTransModal').on('shown.bs.modal', function (ev) {   
    $('#txtacccode').on('select2:close', function (e)
    {
        setTimeout(() => {
            $('#curr_code').select2('open');
        }, 500);
    });
    $('#txtacccode').on('select2:open', function (e)
    {
        setTimeout(() => {
            $('#curr_code').select2('close');
        }, 100);
    });
    $('#curr_code').on('select2:close', function (e)
    {
        $('#id_auto_exch').focus();
    });
});

$(document).on('click', '.set_line', function() {
    trigger_line = parseInt($(this).closest('tr').find("td:first").text());
    trigger_row = $(this).closest('tr');
});

function resetLine() {
    $('#dynamic-table tbody tr').each(function (indx) {
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
        let row_count = $('#dynamic-table').DataTable().rows().count();
        trigger_row = $('#dynamic-table tbody tr:nth-child('+row_count+')').closest('tr');
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
    let row_count = $('#dynamic-table').DataTable().rows().count();
    trigger_row = $('#dynamic-table tbody tr:nth-child('+row_count+')').closest('tr');
    loadRowForEdit();
    new_line = false;
}

function goFirst() {
    trigger_row = $('#dynamic-table tbody tr:nth-child(1)').closest('tr');
    loadRowForEdit();
    new_line = false;
}

function loadRowForEdit() {
    if(trigger_row != undefined && trigger_row != null) {
        try {
            trigger_line = parseInt(trigger_row.find("td:first").text());
            if (isNaN(trigger_line)) {
                trigger_line = 0;
            }
            let trans_id = $('#dynamic-table').DataTable().row( trigger_row ).data()[12];
            let line = $('#dynamic-table').DataTable().row( trigger_row ).data()[18];
            if (trans_id != undefined && trans_id != '') {
                editOldTransactionModal(trans_id, line);
            } else {
                editNewTransactionModal(line);
            }
        } catch(e) {
            console.log(e);
        }
    }
}

function addTransaction() {
    var trxdebits0 = 0;
    var trxdebits1 = 0;
    var trxcredits0 = 0;
    var trxcredits1 = 0;
    var trxunbalance = 0;

    var validate = checkTransaction();
    if (validate != "success") {
        $("#div_transaction_error").removeClass('hide_column');
        $("#transaction_error").text(validate);
    } else {
        var transaction = getTransactionForm();
        if(!is_decimal) {
            f_dbt = comma_format(transaction.funcdebit, 0);
            f_cdt = comma_format(transaction.funccredit, 0);
        } else {
            f_dbt = comma_format(transaction.funcdebit);
            f_cdt = comma_format(transaction.funccredit);
        }
        var datatbl = $('#dynamic-table').dataTable();
        current_line = current_line + 1;
        var line = current_line;
        var button = '<div class="btn-group dropdown">'
            + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle set_line" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
            + '<span class="caret" style="margin-left:15px;"></span><span class="sr-only">Toggle Dropdown</span>'
            + '</button>'
            + '<ul class="dropdown-menu dropdown-menu-right">'
            // + '<li><a onclick="NewTransactionModal(0, ' + line + ')">New</a></li>'
            + '<li><a onclick="editNewTransactionModal(' + line + ')">Edit</a></li>'
            + '<li><a onclick="deleteNewTransactionModal(' + line + ')">Delete</a></li>'
            + '</ul>'
            + '</div>';
        transaction.is_decimal = is_currency_decimal;
        var dt = datatbl.api();
        // datatbl.row.add( [
        dt.row.add( [
            line,
            filter_special_char(transaction.reference),
            filter_special_char(transaction.description),
            transaction.account_code+' - '+transaction.account_name,
            transaction.currency_code,
            comma_format(transaction.srcdebit),
            comma_format(transaction.srccredit),
            transaction.exchange_rate,
            f_dbt,
            f_cdt,
            transaction.comment,
            button,
            "",
            transaction.account_id,
            transaction.currency_id,
            "",
            transaction.is_auto_exch,
            transaction.is_decimal,
            line,
            transaction.rate_date
        // ] ).draw( false );
        ] );
        // Insert row to the correct index
        var aiDisplayMaster = datatbl.fnSettings()['aiDisplayMaster'];
        var moveRow = aiDisplayMaster.pop();
        aiDisplayMaster.splice(trigger_line, 0, moveRow);
        dt.draw(false);

        // reset line number
        resetLine();


        $('#batch_curr_id').val(transaction.currency_id);
        $('#batch_curr_code').val(transaction.currency_code);

        // calculateTrxAmount
        var old_f = transaction.funcdebit.replace(/,/g , '');
        var old_f_cr = transaction.funccredit.replace(/,/g , '');
        var txttrxdebits = $('#txttrxdebits').val();
        var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
        var txttrxcredits = $('#txttrxcredits').val();
        var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
        trxdebits1 = float_format(int_txttrxdebits) + float_format(old_f);
        trxcredits1 = float_format(int_txttrxcredits) + float_format(old_f_cr);
        if(!is_decimal) {
            $("#txttrxdebits").val(comma_format(trxdebits1, 0));
            $("#txttrxcredits").val(comma_format(trxcredits1, 0));
        } else {
            $("#txttrxdebits").val(comma_format(trxdebits1));
            $("#txttrxcredits").val(comma_format(trxcredits1));
        }

        $('#id_debit_amount').val($('#txttrxdebits').val());
        $('#id_credit_amount').val($('#txttrxcredits').val());

        var undistributed_amount = float_format(comma_format(trxdebits1)) - float_format(comma_format(trxcredits1));
        if(!is_decimal) {
            $('#txtunbalance').val(comma_format(undistributed_amount, 0));
        } else {
            $('#txtunbalance').val(comma_format(undistributed_amount));
        }
        if(undistributed_amount == 0) {
            $("#div_journal_errorr").addClass('hide_column');
            $('#journal_error').text('');
        }

        transaction.line = line;
        transaction.row_number = line;
        transaction.is_debit_account = transaction.funcdebit>0.000000 ? true : false;
        transaction_new.push(transaction);

        //for entry mode
        transaction_mix.push(transaction);

        // save selected currency to input hidden
        $('#journal_curr_id').val(transaction.currency_id);
        $('#journal_curr_code').val(transaction.currency_code);
        special_trx = false;

        // $("#AddTransModal").modal("hide");
        // if (trigger_row) {
        //     if (trigger_row.next().hasClass('even') || trigger_row.next().hasClass('odd')) {
        //         goRight();
        //     }
        // } else {
            showTransactionModal('');
        // }
        setTimeout(() => {
            $('#txtref').select();
        }, 200);
    }
}

function editNewTransactionModal(line) {
    clearTransactionForm();
    var result = $.grep(transaction_new, function (e) {
        return e.line == line;
    });
    if (result.length == 0) {
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('Record not found !');
        $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
        $("#notificationModal").modal("show");
        return 0;
    } else if (result.length == 1) {
        setTransactionForm(result[0]);
    }
    old_trx = true;
    // Add action to save button
    $("#save-trs").attr("onclick", "editNewTransaction(" + line + ")");
    $('#line_number').val(trigger_line);
    $("#AddTransModal").modal("show");
}

function editNewTransaction(line) {
    var validate = checkTransaction();
    if (validate != "success") {
        $("#div_transaction_error").removeClass('hide_column');
        $("#transaction_error").text(validate);
    } else {
        var transaction = getTransactionForm();
        var datatbl = $('#dynamic-table').DataTable();
        var row = trigger_row;

        // load amount of this row
        var old_funcdebit = float_format(datatbl.cell(row, $("#trs-funcdebit").index()).data());
        var old_funccredit = float_format(datatbl.cell(row, $("#trs-funccredit").index()).data());
        var old_funcamount = old_funcdebit > 0.000000 ? old_funcdebit : old_funccredit;
        var oldIsDebit = old_funcdebit > 0.000000 ? true : false ;

        // Draw data into table
        datatbl.cell(row, $("#trs-reference").index()).data(filter_special_char(transaction.reference));
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account").index()).data(transaction.account_code+' - '+transaction.account_name);
        datatbl.cell(row, $("#trs-currency").index()).data(transaction.currency_code);
        datatbl.cell(row, $("#trs-srcdebit").index()).data(comma_format(transaction.srcdebit));
        datatbl.cell(row, $("#trs-srccredit").index()).data(comma_format(transaction.srccredit));
        datatbl.cell(row, $("#trs-exchange_rate").index()).data(transaction.exchange_rate);
        datatbl.cell(row, $("#trs-funcdebit").index()).data(comma_format(transaction.funcdebit));
        datatbl.cell(row, $("#trs-funccredit").index()).data(comma_format(transaction.funccredit));
        datatbl.cell(row, $("#trs-comment").index()).data(transaction.comment);
        datatbl.cell(row, $("#trs-id").index()).data(transaction.id);
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
        datatbl.cell(row, $("#trs-currency_id").index()).data(transaction.currency_id);
        datatbl.cell(row, $("#trs-is_auto_exch").index()).data(transaction.is_auto_exch);
        datatbl.cell(row, $("#trs-row_number").index()).data(line);
        datatbl.cell(row, $("#trs-rate_date").index()).data(transaction.rate_date);
        datatbl.draw();

        // calculateTrxAmount, detect credit/debit side changes, wtf !
        var isDebit = transaction.funcdebit>0.000000 ? true : false ;
        if (isDebit) {
            trxdebits0 = float_format($("#txttrxdebits").val());
            if (oldIsDebit){
                trxdebits1 = trxdebits0-old_funcamount+float_format(transaction.funcdebit);
            } else {
                trxdebits1 = trxdebits0+float_format(transaction.funcdebit);
                trxcredits0 = float_format($("#txttrxcredits").val());
                trxcredits1 = trxcredits0-old_funcamount;
                $("#txttrxcredits").val(comma_format(trxcredits1));
            }
            if(!is_decimal) {
                $("#txttrxdebits").val(comma_format(trxdebits1, 0));
            } else {
                $("#txttrxdebits").val(comma_format(trxdebits1));
            }
        } else {
            trxcredits0 = float_format($("#txttrxcredits").val());
            if (!oldIsDebit){
                trxcredits1 = trxcredits0-old_funcamount+float_format(transaction.funccredit);
            } else {
                trxcredits1 = trxcredits0+float_format(transaction.funccredit);
                trxdebits0 = float_format($("#txttrxdebits").val());
                trxdebits1 = trxdebits0-old_funcamount;
                $("#txttrxdebits").val(comma_format(trxdebits1));
            }
            if(!is_decimal) {
                $("#txttrxcredits").val(comma_format(trxcredits1, 0));
            } else {
                $("#txttrxcredits").val(comma_format(trxcredits1));
            }
        }
        $('#id_debit_amount').val($('#txttrxdebits').val());
        $('#id_credit_amount').val($('#txttrxcredits').val());
        trxdebits0 = float_format($("#txttrxdebits").val());
        trxcredits0 = float_format($("#txttrxcredits").val());
        trxunbalance = Math.abs(trxdebits0-trxcredits0);

        var txttrxdebits = $('#txttrxdebits').val();
        var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
        var txttrxcredits = $('#txttrxcredits').val();
        var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
        var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
        if(!is_decimal) {
            $('#txtunbalance').val(comma_format(undistributed_amount, 0));
        } else {
            $('#txtunbalance').val(comma_format(undistributed_amount));
        }

        // $("#txtunbalance").val(trxunbalance.toFixed(2));
        // add current 'data' to array
        transaction.line = line;
        transaction.is_debit_account = isDebit;
        var result = $.grep(transaction_new, function (e) {
            return e.line == line;
        });
        if (result.length == 0) {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to update record!');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
            return 0;
        } else if (result.length == 1) {
            result[0].line = transaction.line;
            result[0].reference = filter_special_char(transaction.reference);
            result[0].description = filter_special_char(transaction.description);
            result[0].account_code = transaction.account_code;
            result[0].account_name = filter_special_char(transaction.account_name);
            result[0].currency_code = transaction.currency_code;
            result[0].srcdebit = transaction.srcdebit;
            result[0].srccredit = transaction.srccredit;
            result[0].exchange_rate = transaction.exchange_rate;
            result[0].funcdebit = transaction.funcdebit;
            result[0].funccredit = transaction.funccredit;
            result[0].comment = transaction.comment;
            result[0].account_id = transaction.account_id;
            result[0].currency_id = transaction.currency_id;
            result[0].is_auto_exch = transaction.is_auto_exch;
            result[0].is_debit_account = isDebit;
        }

        // $("#AddTransModal").modal("hide");
        //showTransactionModal('');
    }
}

// Show Comfirm delete new transaction
function deleteNewTransactionModal(line) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteNewTransaction(" + line + ")");
}

// Action when delete new transaction
function deleteNewTransaction(line) {
    $("#comfirmDeleteTransactionForm").submit(function(e){
        e.preventDefault();
    });
    var datatbl = $('#dynamic-table').DataTable();
    // get this line amount
    var thisline_d = datatbl.cell(trigger_row, $("#trs-funcdebit").index()).data();
    var thisline_c = datatbl.cell(trigger_row, $("#trs-funccredit").index()).data();
    thisline_d = float_format(thisline_d);
    thisline_c = float_format(thisline_c);

    // get this journal (total transactions) amount
    var thisjournal_d = float_format($('#txttrxdebits').val());
    var thisjournal_c = float_format($('#txttrxcredits').val());

    // Update this journal (total transactions) amount
    $('#txttrxdebits').val(comma_format((thisjournal_d-thisline_d)));
    $('#txttrxcredits').val(comma_format((thisjournal_c-thisline_c)));

    // calculate and update unbalance
    thisjournal_d = float_format($('#txttrxdebits').val());
    thisjournal_c = float_format($('#txttrxcredits').val());
    var trxunbalance = Math.abs(thisjournal_d-thisjournal_c);

    var txttrxdebits = $('#txttrxdebits').val();
    var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
    var txttrxcredits = $('#txttrxcredits').val();
    var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
    var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
    $('#txtunbalance').val(comma_format(undistributed_amount));

    $('#id_debit_amount').val($('#txttrxdebits').val());
    $('#id_credit_amount').val($('#txttrxcredits').val());

    // $("#txtunbalance").val(trxunbalance);
    // Remove row
    datatbl.row(trigger_row).remove().draw();
    var deleted_line = line;
    $.map(transaction_new, function(value, key) {
        if(value && value.line == deleted_line) {
            transaction_new.splice(key, 1);
            return true;
        }
    });
    $("#comfirmDeleteTransactionModal").modal("hide");
    // reset line number
    resetLine();
    datatbl.draw();
}

function setExchangeRate(from_currency, to_currency){
    $.ajax({
        method: "POST",
        url: '/currencies/get_exchange_rate/3/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'from_currency_id': from_currency,
            'to_currency_id': to_currency,
            'doc_date': $("#document_date").val()
        },
        success: function (data) {
            $('#txtexcrateid').val(data[0].id);
            $('#txtexcrate').val(parseFloat(data[0].rate).toFixed(10)).trigger('change');
            $('#txtexcdate').val(data[0].exchange_date);
            if (($('#curr_code').val() != $('#company_curr_id').val()) &&
              ($('#curr_code').val() != '0') &&
              ($('#input_state').val()!='2') && $('#id_auto_exch').is(':checked') == false){
                $('#btnOpentExchRateDialog').prop('disabled', false);
                // var new_excrate_datatbl = $('#exchrate-table').DataTable();
                // new_excrate_datatbl.ajax.reload();
            }
        },
        error: function () {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to load exchange rate !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

function setCurrency(account_id) {
    $.ajax({
        method: "POST",
        url: '/accounting/load_currency/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'account_id': account_id,
        },
        success: function (data) {
            var company_currency = $('#company_curr_id').val();
            var data_company_currency = false;
            $('#curr_code').empty().select2();
            $.each(data, function (key, value) {
                if (value.currency_id == company_currency) {
                    data_company_currency = true;
                }
                $('#curr_code')
                    .append($("<option></option>")
                        .attr("value", value.currency_id)
                        .attr("data-name", value.currency_name)
                        .attr("data-is_currency_decimal", value.is_decimal)
                        .text(value.currency_code));
            });
            if (g_curr_id) {
                $('#curr_code').val(g_curr_id);
                g_curr_id = '';
            } else {
                if (data[0].default) {
                    $('#curr_code').val(data[0].default).trigger('change');
                } else if (data_company_currency) {
                    $('#curr_code').val(company_currency).trigger('change');
                } else {
                    $('#curr_code').val(data[0].currency_id).trigger('change');
                }
            }
        },
        error: function () {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to load currency !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

// Show modal to new base on old transation
function NewTransactionModal(id, line) {
    clearTransactionForm();
    old_trx = true;
    var result = $.grep(transaction_new, function (e) {
        return e.line == line;
    });
    if (result.length == 0) {
        result = $.grep(transaction_update, function (e) {
            return e.line == line;
        });
    }
    if (id > 0 && result.length == 0) {
        $.ajax({
            method: "POST",
            url: '/transactions/get-gl-info-transaction/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'transaction_id': id
            },
            success: function (data) {
                var transaction = new Transaction();
                transaction.account_id = data[0].account_id;
                transaction.account_code = data[0].account_code;
                transaction.account_name = data[0].account_name;
                transaction.currency_id = data[0].currency_id;
                transaction.currency_code = data[0].currency_code;
                transaction.currency_name = data[0].currency_name;
                transaction.exchange_rate = float_format(data[0].exchange_rate).toFixed(10);
                transaction.rate_date = data[0].rate_date;
                transaction.is_decimal = data[0].is_decimal;
                setTransactionForm(transaction);
            },
            error: function () {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Failed to load transaction records !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    } else {
        setTransactionForm(result[0]);
    }

    $('#line_number').val(trigger_line + 1);
    $("#AddTransModal").modal("show");
    $("#save-trs").attr("onclick", "addTransaction()");
    new_line = true;
}

function insertTransactionModal() {
    clearTransactionForm();
    $('#txtacccode').val(1).trigger("change");
    old_trx = true;
    try {
        var line = $('#dynamic-table').DataTable().row( trigger_row ).data()[18];
        var result = $.grep(transaction_new, function (e) {
            return e.line == line;
        });
        if (result.length != 0) {
            setTransactionForm(result[0]);
        }
    } catch(e) {

    }


    $('#line_number').val(trigger_line + 1);
    $("#AddTransModal").modal("show");
    $("#save-trs").attr("onclick", "addTransaction()");
    new_line = true;
    setTimeout(() => {
        $('#txtref').select();
    }, 500);
    
}

// Show modal to edit old transation
function editOldTransactionModal(id, line) {
    clearTransactionForm();
    old_trx = true;
    var result = $.grep(transaction_update, function (e) {
        return e.line == line;
    });
    if (result.length == 0) {
        $.ajax({
            method: "POST",
            url: '/transactions/get-gl-info-transaction/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'transaction_id': id
            },
            success: function (data) {
                var transaction = new Transaction();
                transaction.reference = filter_special_char(data[0].reference);
                transaction.description = filter_special_char(data[0].description);
                transaction.account_id = data[0].account_id;
                transaction.account_code = data[0].account_code;
                transaction.account_name = filter_special_char(data[0].account_name);
                transaction.currency_id = data[0].currency_id;
                transaction.currency_code = data[0].currency_code;
                transaction.currency_name = data[0].currency_name;
                transaction.exchange_rate = float_format(data[0].exchange_rate).toFixed(10);
                transaction.comment = data[0].remark;
                transaction.rate_date = data[0].rate_date;
                transaction.is_debit_account = data[0].is_debit_account;
                transaction.is_auto_exch = data[0].is_auto_exch;
                if (transaction.is_debit_account==1){
                    transaction.srcdebit = float_format(data[0].amount).toFixed(2);
                    transaction.srccredit = 0;
                } else {
                    transaction.srcdebit = 0;
                    transaction.srccredit = float_format(data[0].amount).toFixed(2);
                }
                transaction.functional_balance_type = data[0].functional_balance_type;
                if (transaction.functional_balance_type=='1'){
                    transaction.funcdebit = float_format(data[0].functional_amount).toFixed(2);
                    transaction.funccredit = 0;
                } else {
                    transaction.funcdebit = 0;
                    transaction.funccredit = float_format(data[0].functional_amount).toFixed(2);
                }
                transaction.is_decimal = data[0].is_decimal;
                if ((transaction.srccredit == 0 && transaction.funccredit != 0) || (transaction.srcdebit == 0 && transaction.funcdebit != 0)) {
                    special_trx = true;
                    transaction.is_auto_exch = true;
                }
                setTransactionForm(transaction);
            },
            error: function () {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Failed to load transaction records !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    } else if (result.length == 1) {
        if ((result[0].srccredit == 0 && result[0].funccredit != 0) || (result[0].srcdebit == 0 && result[0].funcdebit != 0)) {
            special_trx = true;
            result[0].is_auto_exch = true;
        }
        setTransactionForm(result[0]);
    }
    $('#line_number').val(trigger_line);
    $("#AddTransModal").modal("show");
    $("#save-trs").attr("onclick", "editOldTransaction(" + line + ")");
}

// Save Update Old Transaction
function editOldTransaction(line) {
    var validate = checkTransaction();
    if (validate != "success") {
        $("#div_transaction_error").removeClass('hide_column');
        $("#transaction_error").text(validate);
    } else {
        var transaction = getTransactionForm();
        var datatbl = $('#dynamic-table').DataTable();
        var row = trigger_row;

        // load old amount of this row
        var old_funcdebit = float_format(datatbl.cell(row, $("#trs-funcdebit").index()).data());
        var old_funccredit = float_format(datatbl.cell(row, $("#trs-funccredit").index()).data());
        var old_funcamount = old_funcdebit > 0.000000 ? old_funcdebit : old_funccredit;
        var oldIsDebit = old_funcdebit > 0.000000 ? true : false ;

        // Draw data into table
        datatbl.cell(row, $("#trs-reference").index()).data(filter_special_char(transaction.reference));
        datatbl.cell(row, $("#trs-description").index()).data(filter_special_char(transaction.description));
        datatbl.cell(row, $("#trs-account").index()).data(transaction.account_code+' - '+transaction.account_name);
        datatbl.cell(row, $("#trs-currency").index()).data(transaction.currency_code);
        datatbl.cell(row, $("#trs-srcdebit").index()).data(comma_format(transaction.srcdebit));
        datatbl.cell(row, $("#trs-srccredit").index()).data(comma_format(transaction.srccredit));
        datatbl.cell(row, $("#trs-exchange_rate").index()).data(float_format(transaction.exchange_rate).toFixed(10));
        datatbl.cell(row, $("#trs-funcdebit").index()).data(comma_format(transaction.funcdebit));
        datatbl.cell(row, $("#trs-funccredit").index()).data(comma_format(transaction.funccredit));
        datatbl.cell(row, $("#trs-comment").index()).data(transaction.comment);
        datatbl.cell(row, $("#trs-id").index()).data(transaction.id);
        datatbl.cell(row, $("#trs-account_id").index()).data(transaction.account_id);
        datatbl.cell(row, $("#trs-currency_id").index()).data(transaction.currency_id);
        datatbl.cell(row, $("#trs-is_auto_exch").index()).data(transaction.is_auto_exch);
        datatbl.cell(row, $("#trs-row_number").index()).data(line);
        datatbl.cell(row, $("#trs-rate_date").index()).data(transaction.rate_date);
        datatbl.draw();

        // calculateTrxAmount, detect credit/debit side changes, wtf !
        var isDebit = float_format(transaction.funcdebit)>0.00 ? true : false ;
        if (isDebit) {
            trxdebits0 = float_format($("#txttrxdebits").val());
            if (oldIsDebit){
                trxdebits1 = trxdebits0-old_funcamount+float_format(transaction.funcdebit);
            } else {
                trxdebits1 = trxdebits0+float_format(transaction.funcdebit);
                trxcredits0 = float_format($("#txttrxcredits").val());
                trxcredits1 = trxcredits0-old_funcamount;
                $("#txttrxcredits").val(comma_format(trxcredits1));
            }
            if(!is_decimal) {
                $("#txttrxdebits").val(comma_format(trxdebits1, 0));
            } else {
                $("#txttrxdebits").val(comma_format(trxdebits1));
            }
        } else {
            trxcredits0 = float_format($("#txttrxcredits").val());
            if (!oldIsDebit){
                trxcredits1 = trxcredits0-old_funcamount+float_format(transaction.funccredit);
            } else {
                trxcredits1 = trxcredits0+float_format(transaction.funccredit);
                trxdebits0 = float_format($("#txttrxdebits").val());
                trxdebits1 = trxdebits0-old_funcamount;
                $("#txttrxdebits").val(comma_format(trxdebits1));
            }
            if(!is_decimal) {
                $("#txttrxcredits").val(comma_format(trxcredits1, 0));
            } else {
                $("#txttrxcredits").val(comma_format(trxcredits1));
            }
        }
        $('#id_debit_amount').val($('#txttrxdebits').val());
        $('#id_credit_amount').val($('#txttrxcredits').val());
        trxdebits0 = float_format($("#txttrxdebits").val());
        trxcredits0 = float_format($("#txttrxcredits").val());
        trxunbalance = Math.abs(trxdebits0-trxcredits0);

        var txttrxdebits = $('#txttrxdebits').val();
        var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
        var txttrxcredits = $('#txttrxcredits').val();
        var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
        var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
        if(!is_decimal) {
            $('#txtunbalance').val(comma_format(undistributed_amount, 0));
        } else {
            $('#txtunbalance').val(comma_format(undistributed_amount));
        }
        // Update old transaction list, not save in database
        transaction.line = line;
        transaction.row_number = line;
        transaction.is_debit_account = isDebit;
        transaction.is_decimal = is_currency_decimal;

        // Find object
        var result = $.grep(transaction_update, function (e) {
            return e.line == line;
        });
        if (result.length == 0) {
            transaction_update.push(transaction);
        } else if (result.length == 1) {
            result[0].line = transaction.line;
            result[0].reference = filter_special_char(transaction.reference);
            result[0].description = filter_special_char(transaction.description);
            result[0].account_code = transaction.account_code;
            result[0].account_name = filter_special_char(transaction.account_name);
            result[0].currency_code = transaction.currency_code;
            result[0].srcdebit = transaction.srcdebit;
            result[0].srccredit = transaction.srccredit;
            result[0].exchange_rate = transaction.exchange_rate;
            result[0].funcdebit = transaction.funcdebit;
            result[0].funccredit = transaction.funccredit;
            result[0].comment = transaction.comment;
            result[0].account_id = transaction.account_id;
            result[0].currency_id = transaction.currency_id;
            result[0].is_auto_exch = transaction.is_auto_exch;
            result[0].is_debit_account = isDebit;
        }
        //$("#AddTransModal").modal("hide");
        //special_trx = false;
        //showTransactionModal('');
    }
}

$('#AddTransModal').on('hidden.bs.modal', function (ev) {
    special_trx = false;
});


// Show Comfirm delete old transaction
function deleteOldTransactionModal(trxid,isdebit,trxamount,jornalid) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteOldTransaction("+ trxid +','+ isdebit +','+ trxamount +','+ jornalid + ")");
}

function deleteOldTransaction(p1,p2,p3,p4){
    if (p2){
        var trxdebits = float_format($("#txttrxdebits").val())-float_format(p3);
        $("#txttrxdebits").val(comma_format(trxdebits));
    } else {
        var trxcredits = float_format($("#txttrxcredits").val())-float_format(p3);
        $("#txttrxcredits").val(comma_format(trxcredits));
    }
    var trxunbalance = Math.abs(float_format($("#txttrxdebits").val())-float_format($("#txttrxcredits").val()));

    var txttrxdebits = $('#txttrxdebits').val();
    var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
    var txttrxcredits = $('#txttrxcredits').val();
    var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
    var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
    $('#txtunbalance').val(comma_format(undistributed_amount));

    var url = '/accounting/delete/GL_JE_TRX/'+ p1 +'/'+ p4 +'/';
    $("#comfirmDeleteTransactionForm").attr("action", url);

    $('#id_debit_amount').val($('#txttrxdebits').val());
    $('#id_credit_amount').val($('#txttrxcredits').val());
}

$('#entry_num_sub').on('click', function(){
    var Dont_Save = false;
    var isDataChange = false;
    var jDesc = $("#id_name").val();
    var jDate = $("#document_date").val();
    // var jSrcCode = $("#txtsource_code").val();
    var jSrcCode = $("#source_type").val();
    if ((transaction_new.length>0)||
        (transaction_update.length>0)||
        (jDesc!=header_data["journal_desc"])||
        (jDate!=header_data["journal_date"])||
        (jSrcCode!=header_data["journal_srccode"])){
        isDataChange = true;
    }
    $("#div_journal_errorr").addClass('hide_column');
    var form_state = parseInt($('#input_state').val());
    var unbalance = float_format($("#txtunbalance").val()).toFixed(2);
    var trxdebits = float_format($('#txttrxdebits').val()).toFixed(2);
    var trxcredits = float_format($('#txttrxcredits').val()).toFixed(2);
    var batch_id = $('#BatchID').val();
    if  (!batch_id || 0 === batch_id.length){
        batch_id = 0
    }
    var journal_id = $('#JournalID').val();
    if  (!journal_id || 0 === journal_id.length){
        journal_id = 0
    }
    var trx_num = parseInt($('#trxnum').val());
    var trx_num_sub1 = trx_num-1;
    // only get previous transactions when currenct transaction is not the first transactions
    if (trx_num>1){
        if (((unbalance>0.000000) || (trxdebits==0&&trxcredits==0)) && (isDataChange==true)){
            Dont_Save = true;
        }
        $.ajax({
            method: "POST",
            url: '/accounting/journal_GL_get_trx/'+batch_id+'/'+trx_num_sub1+'/0/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if ((isDataChange==true)&&(Dont_Save==false)){
                    addOrEditTrx(false,batch_id,journal_id,trx_num);
                }
                var trx = updateTrxDataTables(data);
                $("#txttrxdebits").val(comma_format(trx.debitsum));
                $("#txttrxcredits").val(comma_format(trx.creditsum));
                $('#id_debit_amount').val($('#txttrxdebits').val());
                $('#id_credit_amount').val($('#txttrxcredits').val());

                var txttrxdebits = $('#txttrxdebits').val();
                var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
                var txttrxcredits = $('#txttrxcredits').val();
                var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
                var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
                $('#txtunbalance').val(comma_format(undistributed_amount));
                $('#span_journal_no').text(leftPad(data.journal_code,5));
                // setHeaderData($("#id_name").val(),$("#document_date").val(),$("#txtsource_code").val());
                setHeaderData($("#id_name").val(),$("#document_date").val(),$("#source_type").val());
            },
            error: function (e) {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Some error occurred !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    }
});

$('#entry_num_backward').on('click', function(){
    var Dont_Save = false;
    var isDataChange = false;
    var jDesc = $("#id_name").val();
    var jDate = $("#document_date").val();
    // var jSrcCode = $("#txtsource_code").val();
    var jSrcCode = $("#source_type").val();
    if ((transaction_new.length>0)||
        (transaction_update.length>0)||
        (jDesc!=header_data["journal_desc"])||
        (jDate!=header_data["journal_date"])||
        (jSrcCode!=header_data["journal_srccode"])){
        isDataChange = true;
    }
    $("#div_journal_errorr").addClass('hide_column');
    var form_state = parseInt($('#input_state').val());
    var unbalance = float_format($("#txtunbalance").val()).toFixed(2);
    var trxdebits = float_format($('#txttrxdebits').val()).toFixed(2);
    var trxcredits = float_format($('#txttrxcredits').val()).toFixed(2);
    var batch_id = $('#BatchID').val();
    if  (!batch_id || 0 === batch_id.length){
        batch_id = 0
    }
    var journal_id = $('#JournalID').val();
    if  (!journal_id || 0 === journal_id.length){
        journal_id = 0
    }
    var trx_num = parseInt($('#trxnum').val());
    var trx_num_backward = 1;
    // only get previous transactions when currenct transaction is not the first transactions
    if (trx_num>1){
        if (((unbalance>0.000000) || (trxdebits==0&&trxcredits==0)) && (isDataChange==true)){
            Dont_Save = true;
        }
        $.ajax({
            method: "POST",
            url: '/accounting/journal_GL_get_trx/'+batch_id+'/'+trx_num_backward+'/0/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if ((isDataChange==true)&&(Dont_Save==false)){
                    addOrEditTrx(false,batch_id,journal_id,trx_num);
                }
                var trx = updateTrxDataTables(data);
                $("#txttrxdebits").val(comma_format(trx.debitsum));
                $("#txttrxcredits").val(comma_format(trx.creditsum));
                $('#id_debit_amount').val($('#txttrxdebits').val());
                $('#id_credit_amount').val($('#txttrxcredits').val());

                var txttrxdebits = $('#txttrxdebits').val();
                var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
                var txttrxcredits = $('#txttrxcredits').val();
                var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
                var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
                $('#txtunbalance').val(comma_format(undistributed_amount));
                $('#span_journal_no').text(leftPad(data.journal_code,5));
                // setHeaderData($("#id_name").val(),$("#document_date").val(),$("#txtsource_code").val());
                setHeaderData($("#id_name").val(),$("#document_date").val(),$("#source_type").val());
            },
            error: function (e) {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Some error occurred !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    }
});

function updateTrxDataTables(data){
    var form_state = parseInt($('#input_state').val());
    var trx = {
        "debitsum":0,
        "creditsum":0,
        "unbalance":0,
        "journal_id":0
    };//update journal info
    $("#JournalID").val(data.journal_id);
    $("#id_name").val(data.journal_desc);
    $("#document_date").val(data.journal_date).trigger('change');
    // $("#txtsource_code").val(data.Journal_srccode).trigger('focusout');
    $("#source_type").val(data.Journal_srccode).trigger('change');
    $("#journal_curr_id").val(data.Journal_currency);
    $("#journal_curr_code").val(data.Journal_currcode);
    $("#year_period").val(data.journal_prd + '-' + data.journal_year).trigger('change');
    $("#trxnum").val(data.journal_code);
    if (data.is_auto_reverse==true){
        $('#is_auto_reverse').prop('checked', true);
        $('#div_rv_period_opt').removeClass('hide');
        $('#rv_period_opt').val(data.rv_period_opt).trigger('change');
        $('#rv_period').val(data.rv_period);
    } else {
        $('#is_auto_reverse').prop('checked', false);
        $('#div_rv_period_opt').addClass('hide');
        $('#div_rv_period').addClass('hide');
    }

    //clear trx data and fill with loaded transactions
    transaction_mix.length = 0;
    var datatbl = $('#dynamic-table').DataTable();
    datatbl.clear().draw();
    for (var i = 0, len = data.array.length; i < len; i++) {
        var transaction = new Transaction();
        transaction.id = data.array[i].id;
        transaction.reference = filter_special_char(data.array[i].reference);
        transaction.description = filter_special_char(data.array[i].description);
        transaction.account_id = data.array[i].account_id;
        transaction.account_code = data.array[i].account_code;
        transaction.account_name = filter_special_char(data.array[i].account_name);
        transaction.currency_id = data.array[i].currency_id;
        transaction.currency_code = data.array[i].currency_code;
        transaction.currency_name = data.array[i].currency_name;
        transaction.functional_currency_id = data.array[i].functional_currency_id;
        transaction.exchange_rate = float_format(data.array[i].exchange_rate).toFixed(10);
        transaction.comment = data.array[i].remark;
        transaction.is_auto_exch = data.array[i].is_auto_exch;
        transaction.is_debit_account = data.array[i].is_debit_account;
        if (transaction.is_debit_account==1){
            transaction.srcdebit = float_format(data.array[i].total_amount).toFixed(2);
            transaction.srccredit = '0.00';
        } else {
            transaction.srcdebit = '0.00';
            transaction.srccredit = float_format(data.array[i].total_amount).toFixed(2);
        }
        transaction.functional_balance_type = data.array[i].functional_balance_type;
        if (transaction.functional_balance_type=='1'){
            transaction.funcdebit = float_format(data.array[i].functional_amount).toFixed(2);
            transaction.funccredit = '0.00';
        } else {
            transaction.funcdebit = '0.00';
            transaction.funccredit = float_format(data.array[i].functional_amount).toFixed(2);
        }

        var line = parseInt(datatbl.page.info().recordsTotal) + 1;
        var button = '<div class="btn-group dropdown">'
            + '<button type="button" class="btn btn-primary btn-sm dropdown-toggle set_line" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="min-width: 40px!important;">Action'
            + '<span class="caret" style="margin-left:15px;"></span><span class="sr-only">Toggle Dropdown</span>'
            + '</button>'
            + '<ul class="dropdown-menu dropdown-menu-right">';
        if (form_state<2){
            // button += '<li><a onclick="showTransactionModal(' + line + ')">New</a></li>'
            button += ''
            + '<li><a onclick="editOldTransactionModal('+ transaction.id +','+ line + ')">Edit</a></li>'
            + '<li><a onclick="deleteOldTransactionModal(' + transaction.id +','+ transaction.is_debit_account +','+ float_format(data.array[i].functional_amount).toFixed(2) +','+ data.journal_id + ')">Delete</a></li>'
            + '</ul>'
            + '</div>';
        } else {
            button += '<li><a onclick="editOldTransactionModal('+ transaction.id +','+ line + ')">View</a></li></ul></div>';
        }

        datatbl.row.add( [
            line,
            filter_special_char(transaction.reference),
            filter_special_char(transaction.description),
            transaction.account_code+' - '+filter_special_char(transaction.account_name),
            transaction.currency_code,
            comma_format(transaction.srcdebit),
            comma_format(transaction.srccredit),
            transaction.exchange_rate,
            comma_format(transaction.funcdebit),
            comma_format(transaction.funccredit),
            transaction.comment,
            button,
            transaction.id,
            transaction.account_id,
            transaction.currency_id,
            "",
            transaction.is_auto_exch,
            transaction.is_decimal,
            line
        ] ).draw( false );

        trx.debitsum += float_format(transaction.funcdebit);
        trx.creditsum += float_format(transaction.funccredit);
        transaction.line = line;
        transaction.row_number = line;
        transaction.is_decimal = transaction.is_decimal;
        //for entry mode
        transaction_mix.push(transaction);
    }
    trx.unbalance = Math.abs(trx.debitsum-trx.creditsum);
    // setHeaderData($("#id_name").val(),$("#document_date").val(),$("#txtsource_code").val());
    setHeaderData($("#id_name").val(),$("#document_date").val(),$("#source_type").val());
    // if(history.pushState) {
    //     history.pushState(null, null, "/accounting/edit/GL/"+data.journal_id+"/");
    // }
    return trx;
}

$('#entry_num_add').on('click', function(){
    var isDataChange = false;
    var jDesc = $("#id_name").val();
    var jDate = $("#document_date").val();
    // var jSrcCode = $("#txtsource_code").val();
    var jSrcCode = $("#source_type").val();
    if ((transaction_new.length>0)||
        (transaction_update.length>0)||
        (jDesc!=header_data["journal_desc"])||
        (jDate!=header_data["journal_date"])||
        (jSrcCode!=header_data["journal_srccode"])){
        isDataChange = true;
    }
    $("#div_journal_errorr").addClass('hide_column');
    var form_state = parseInt($('#input_state').val());
    var unbalance = float_format($("#txtunbalance").val()).toFixed(2);
    var trxdebits = float_format($('#txttrxdebits').val()).toFixed(2);
    var trxcredits = float_format($('#txttrxcredits').val()).toFixed(2);
    var batch_id = $('#BatchID').val();
    if  (!batch_id || 0 === batch_id.length){
        batch_id = 0
    }
    var journal_id = $('#JournalID').val();
    if  (!journal_id || 0 === journal_id.length){
        journal_id = 0
    }
    var trx_num = parseInt($('#trxnum').val());
    var trx_num_add1 = trx_num+1;

    if ((unbalance>0.000000) && (isDataChange==true)){
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('There is an unbalance amount in this entry !');
        $('#notificationModal_text2').text("Can't save this journal entry. ");
        $("#notificationModal").modal("show");
    } else if (trxdebits==0&&trxcredits==0){
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('No entries data found !');
        $('#notificationModal_text2').text("Can't save this journal entry. ");
        $("#notificationModal").modal("show");
    } else {
        $.ajax({
            method: "POST",
            url: '/accounting/journal_GL_get_trx/'+batch_id+'/'+trx_num_add1+'/1/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if (data.array.length>0){
                    if (isDataChange==true){
                        addOrEditTrx(false,batch_id,journal_id,trx_num);
                    }
                    var trx = updateTrxDataTables(data);
                    $("#txttrxdebits").val(comma_format(trx.debitsum));
                    $("#txttrxcredits").val(comma_format(trx.creditsum));
                    $('#id_debit_amount').val($('#txttrxdebits').val());
                    $('#id_credit_amount').val($('#txttrxcredits').val());

                    var txttrxdebits = $('#txttrxdebits').val();
                    var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
                    var txttrxcredits = $('#txttrxcredits').val();
                    var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
                    var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
                    $('#txtunbalance').val(comma_format(undistributed_amount));
                    $('#span_journal_no').text(leftPad(data.journal_code,5));
                }
                // } else {
                //     if (form_state<3){
                //         $("#entry_add_dialog").modal("show");
                //         $("#entry_add_dialog_OK").attr("onclick", "addTrxOk(true,"+batch_id+","+journal_id+","+trx_num+","+isDataChange+")");
                //     } else {
                //         $('#notificationModal_title').text('Information');
                //         $('#notificationModal_text1').text('No more transactions to show.');
                //         $('#notificationModal_text2').text("Current entry is the last entry for this Batch.");
                //         $("#notificationModal").modal("show");
                //     }
                // }
            },
            error: function (e) {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Some error occurred !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    }
});

$('#entry_num_foward').on('click', function(){
    var isDataChange = false;
    var jDesc = $("#id_name").val();
    var jDate = $("#document_date").val();
    // var jSrcCode = $("#txtsource_code").val();
    var jSrcCode = $("#source_type").val();
    if ((transaction_new.length>0)||
        (transaction_update.length>0)||
        (jDesc!=header_data["journal_desc"])||
        (jDate!=header_data["journal_date"])||
        (jSrcCode!=header_data["journal_srccode"])){
        isDataChange = true;
    }
    $("#div_journal_errorr").addClass('hide_column');
    var form_state = parseInt($('#input_state').val());
    var unbalance = float_format($("#txtunbalance").val()).toFixed(2);
    var trxdebits = float_format($('#txttrxdebits').val()).toFixed(2);
    var trxcredits = float_format($('#txttrxcredits').val()).toFixed(2);
    var batch_id = $('#BatchID').val();
    if  (!batch_id || 0 === batch_id.length){
        batch_id = 0
    }
    var journal_id = $('#JournalID').val();
    if  (!journal_id || 0 === journal_id.length){
        journal_id = 0
    }
    var trx_num = parseInt($('#trxnum').val());
    var trx_num_add1 = $('#journal_count').val();

    if ((unbalance>0.000000) && (isDataChange==true)){
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('There is an unbalance amount in this entry !');
        $('#notificationModal_text2').text("Can't save this journal entry. ");
        $("#notificationModal").modal("show");
    } else if (trxdebits==0&&trxcredits==0){
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('No entries data found !');
        $('#notificationModal_text2').text("Can't save this journal entry. ");
        $("#notificationModal").modal("show");
    } else {
        $.ajax({
            method: "POST",
            url: '/accounting/journal_GL_get_trx/'+batch_id+'/'+trx_num_add1+'/1/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if (data.array.length>0){
                    if (isDataChange==true){
                        addOrEditTrx(false,batch_id,journal_id,trx_num);
                    }
                    var trx = updateTrxDataTables(data);
                    $("#txttrxdebits").val(comma_format(trx.debitsum));
                    $("#txttrxcredits").val(comma_format(trx.creditsum));
                    $('#id_debit_amount').val($('#txttrxdebits').val());
                    $('#id_credit_amount').val($('#txttrxcredits').val());

                    var txttrxdebits = $('#txttrxdebits').val();
                    var int_txttrxdebits= txttrxdebits.replace(/,/g , '');
                    var txttrxcredits = $('#txttrxcredits').val();
                    var int_txttrxcredits = txttrxcredits.replace(/,/g ,'');
                    var undistributed_amount = float_format(int_txttrxdebits) - float_format(int_txttrxcredits);
                    $('#txtunbalance').val(comma_format(undistributed_amount));
                    $('#span_journal_no').text(leftPad(data.journal_code,5));
                }
                // } else {
                //     if (form_state<3){
                //         $("#entry_add_dialog").modal("show");
                //         $("#entry_add_dialog_OK").attr("onclick", "addTrxOk(true,"+batch_id+","+journal_id+","+trx_num+","+isDataChange+")");
                //     } else {
                //         $('#notificationModal_title').text('Information');
                //         $('#notificationModal_text1').text('No more transactions to show.');
                //         $('#notificationModal_text2').text("Current entry is the last entry for this Batch.");
                //         $("#notificationModal").modal("show");
                //     }
                // }
            },
            error: function (e) {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Some error occurred !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    }
});

function addOrEditTrx(isAdd,batch_id,journal_id,journal_num){
    var array = [];
    var transaction_list_data = JSON.stringify(array);
    // get currenct trx data
    var table = $('#dynamic-table').DataTable();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        var rowData = this.data();
        var transaction_list = {};
        transaction_list.reference = filter_special_char(rowData[$("#trs-reference").index()]);
        transaction_list.description = filter_special_char(rowData[$("#trs-description").index()]);
        transaction_list.srcdebit = float_format(rowData[$("#trs-srcdebit").index()]).toFixed(2);
        transaction_list.srccredit = float_format(rowData[$("#trs-srccredit").index()]).toFixed(2);
        transaction_list.exchange_rate = float_format(rowData[$("#trs-exchange_rate").index()]).toFixed(10);
        transaction_list.funcdebit = float_format(rowData[$("#trs-funcdebit").index()]).toFixed(2);
        transaction_list.funccredit = float_format(rowData[$("#trs-funccredit").index()]).toFixed(2);
        transaction_list.comment = rowData[$("#trs-comment").index()];
        transaction_list.id = rowData[$("#trs-id").index()];
        transaction_list.account_id = rowData[$("#trs-account_id").index()];
        transaction_list.currency_id = rowData[$("#trs-currency_id").index()];
        transaction_list.is_auto_exch = rowData[$("#trs-is_auto_exch").index()];
        if (transaction_list.srcdebit>0.000000){
            transaction_list.is_debit_account = 1;
            transaction_list.is_credit_account = 0;
        } else {
            transaction_list.is_debit_account = 0;
            transaction_list.is_credit_account = 1;
        }
        array.push(transaction_list);
    });

    transaction_list_data = JSON.stringify(array);

    var journal_amt = $('#txttrxdebits').val();
    var new_total_amt = journal_amt.replace(/,/g , '');
    $('#total_amt').val(new_total_amt);
    // call journal_GL_add_trx to save current trx data to db
    var hdrdata0 = $(".hdrdata");
    var hdrdata = {};
    var hdrdataArr = [];
    hdrdata.batchdesc = $(hdrdata0[0]).val();
    hdrdata.journaldesc = $(hdrdata0[1]).val();
    hdrdata.journaldate = $(hdrdata0[2]).val();
    hdrdata.srccode = $(hdrdata0[3]).val();
    hdrdata.journalamount = $(hdrdata0[4]).val();
    hdrdata.journalcurr = $(hdrdata0[5]).val();
    hdrdata.journalnum = journal_num;
    hdrdata.excrateid = $("#txtexcrateid").val();
    if ($('#is_auto_reverse').is(":checked"))
    {
        hdrdata.is_auto_reverse = '1';
    } else {
        hdrdata.is_auto_reverse = null;
    }
    hdrdata.rv_period_opt = $("#rv_period_opt").val();
    hdrdata.rv_period = $("#rv_period").val();
    hdrdata.perd_month = $("#year_period").val().split('-')[0];
    hdrdata.perd_year = $("#year_period").val().split('-')[1];
    hdrdataArr.push(hdrdata);
    var hdr_data = JSON.stringify(hdrdataArr);

    $.ajax({
        method: "POST",
        url: '/accounting/journal_GL_add_trx/'+batch_id+'/'+journal_id+'/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            "trxdata": transaction_list_data,
            "hdr_data": hdr_data
        },
        success: function (data) {
            if (parseInt(data[0].status)<3){ /* ORDER_STATUS['Received'] */
                $('#notificationModal_title').text('Warning');
                $('#notificationModal_text1').text('Entries saved with some uncomplete data.');
                $('#notificationModal_text2').text('Please check your data entry.');
                $("#notificationModal").modal("show");
            }
            $("#BatchID").val(data[0].batch_id);
            if (isAdd==true){
                $("#trxnum").val(journal_num+1);
            }
            $("#journal_count").val(data[0].no_entries);
            $("#id_debit_amount").val(float_format(data[0].batch_amount).toFixed(2));
            $("#id_credit_amount").val(float_format(data[0].batch_amount).toFixed(2));
            // setHeaderData($("#id_name").val(),$("#document_date").val(),$("#txtsource_code").val());
            setHeaderData($("#id_name").val(),$("#document_date").val(),$("#source_type").val());
            transaction_new = [];
            transaction_update = [];
        },
        error: function (e) {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Some error occurred !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

function addTrxOk(isAdd,bid,jid,jnum,isChange){
    $("#entry_add_dialog").modal("hide");
    if (isChange==true){
        addOrEditTrx(isAdd,bid,jid,jnum);
    }
    $('#trxnum').val(jnum+1);
    $("#id_name").val('');
    // $("#txtsource_code").val('');
    $("#source_type").val('');
    $("#source_type_name").val('');
    $("#txttrxdebits").val('0');
    $("#txttrxcredits").val('0');
    $("#txtunbalance").val('0');
    $("#journal_curr_id").val('');
    $("#journal_curr_code").val('');
    $("#JournalID").val('0');
    // if(history.pushState) {
    //     history.pushState(null, null, "/accounting/edit/GL/0/");
    // }
    var datatbl = $('#dynamic-table').DataTable();
    datatbl.clear().draw();
}

function load_unposted_batch(){
    $('#unposted_batch_table').DataTable().destroy();
    $('#unposted_batch_table').dataTable({
        "iDisplayLength": 5,
        "aLengthMenu": [[5, 10, 15, -1], [5, 10, 15, "All"]],
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/UnpostedBatch__asJson/",
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.batch_type = batch_type;
                d.source_ledger = source_ledger;
            }
        },
        "columns": [
            {
                "data": null,
                "render": function (data, type, full, meta) {
                    return leftPad(full['batch_num'],6);
                }
            },
            {"data": "batch_desc"},
            {"data": "input_type"},
            {"data": "status"},
            {"data": "source_ledger"},
            {"data": "batch_amount"},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, full, meta) {
                    var button_radio = '<input type="radio" name="choices" id="'+full['id']+'" data-batch_desc="'+full['batch_desc']+'" class="call-radio" value="'+full['batch_num']+'">'
                    return button_radio;
                }
            },
        ],
        "columnDefs": [
            { className: "text-left", targets: [ 0,1,2,3 ] },
            { className: "text-right", targets: [ 5 ] }
        ]
    });
}

function showReverseTrxModal() {
    var is_period_closed = $('#is_period_closed').val();
    var period_month = $('#perd_month').val();
    var period_year = $('#perd_year').val();
    if (is_period_closed!='True'){
        load_unposted_batch();
        $("#ReverseTrxModal").modal("show");
    } else {
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('Period '+period_month+' in fiscal year '+period_year+' is locked for');
        $('#notificationModal_text2').text('General Ledger in Common Services Fiscal Calendar.');
        $("#notificationModal").modal("show");
    }

}

function submitReverseTransaction(source_batch_id,journal_id) {
    var reverse_batch_id = $('#reverse_batch_num').data('batch_id');
    if (parseInt(reverse_batch_id)>0){
        $("#comfirmReverseTransactionModal").modal("show");
        $("#ReverseTransaction_yes").attr("onclick", "CreateReverseBatch("+source_batch_id+','+journal_id+")");
    } else {
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('Target Batch 000000 is not valid !');
        $('#notificationModal_text2').text('Please select a Batch or add a new Batch.');
        $("#notificationModal").modal("show");
    }
}

function CreateReverseBatch(source_batch_id,journal_id) {
    $("#comfirmReverseTransactionModal").modal("hide");
    $.ajax({
        method: "POST",
        url: '/accounting/create_reverse_batch/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'source_batch_id': source_batch_id,
            'journal_id_reverse':journal_id,
            'reverse_batch_id': $('#reverse_batch_num').data('batch_id'),
            'reverse_type': $('input[name=reverse_option]:checked').val(),
            'batch_desc': $('#reverse_batch_desc').val(),
            'entry_desc': $('#reverse_entry_desc').val()
        },
        success: function (data) {
            $("#ReverseTrxModal").modal("hide");
            if (data['result']==true){
                $('#notificationModal_title').text('Success');
            } else {
                $('#notificationModal_title').text('Error');
            }
            $('#notificationModal_text1').text(data['status']);
            $('#notificationModal_text2').text('');
            $("#notificationModal").modal("show");
        },
        error: function () {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to create reverse Batch !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

function leftPad(number, targetLength) {
    var output = number + '';
    while (output.length < targetLength) {
        output = '0' + output;
    }
    return output;
}

function openNewBatch(batch_id,batch_type){
    $.ajax({
        method: "POST",
        url: '/accounting/new_empty_batch/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'batch_id': batch_id,
            'batch_type': batch_type
        },
        success: function (data) {
            var batch_no = leftPad(data['batch_no'],6);
            $('#reverse_batch_num').data('batch_id',data['batch_id']);
            $('#reverse_batch_num').val(batch_no);
            $('#reverse_batch_desc').val(data['batch_desc']);
            load_unposted_batch();

            var obj = {};
            obj.id = data['batch_id'];
            obj.batch_no = data['batch_no'];
            obj.batch_type = data['batch_type'];
            obj.description = data['batch_desc'];
            unpostd_batch.push(obj);

            $('#btnNewBatch').attr('disabled', 'disabled');
        },
        error: function () {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to generate new Batch !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

function deleteEmptyBatch(batch_type) {
    $.ajax({
        method: "POST",
        url: '/accounting/delete_empty_batch/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'batch_type': batch_type
        },
        success: function (data) {
            $('#btnNewBatch').attr('disabled', false);
            $('#reverse_batch_num').val('');
            $('#reverse_batch_desc').val('');
        },
        error: function () {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to Delete Empty Batch !');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
        }
    });
}

function FillYearPeriodOptLst(){
    var year_part = 0;
    var month_part = 0;

    var yr_prd = $('#perd_year').val();
    if ((yr_prd)&&(parseInt(yr_prd)>0)){
        year_part = yr_prd;
    } else {
        yr_prd = new Date($('#document_date').val());
        year_part = yr_prd.getFullYear();
        month_part = yr_prd.getMonth()+1;
    }
    var list_period = [];
    for (i = 1; i <= 15; i++) {
        var prd = {};
        prd.year = year_part;
        prd.period = i;
        list_period.push(prd);
    }
    $.each(list_period, function(key, value) {
        var period_part = value.period>9 ? value.period : '0'+value.period;
        period_part = value.period==14 ? 'ADJ' : period_part;
        period_part = value.period==15 ? 'CLS' : period_part;
        var year_period_text = value.year+'-'+period_part;
        if (value.period!=13){
            $('#year_period')
                    .append($("<option></option>")
                    .attr("value",value.period)
                    .text(year_period_text));
        }
    });
    if ((saved_prd)&&(parseInt(saved_prd)>0)){
        $('#year_period').val(saved_prd).trigger('change');
    } else {
        $('#year_period').val(month_part).trigger('change');
    }
    $('#year_period').select2();
}

function ResetYearPeriodOptLst(){
    $('#year_period').empty().append('<option value="0">kosong</option>');
    FillYearPeriodOptLst();
    $("#year_period option[value='0']").remove();
}
