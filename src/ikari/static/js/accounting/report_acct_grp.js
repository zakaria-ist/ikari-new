var transaction_new = [];
var transaction_update = [];

$('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
    $($.fn.dataTable.tables(true)).DataTable()
        .columns.adjust();
});

$( "#from_account" ).change(function(){
    $(".div_error_msg").addClass('hide');
    var accGrp = getTransactionFormData();
    if (accGrp.acc1_id){
        if (parseInt(accGrp.acc1_code.substr(0, 4))>parseInt(accGrp.acc2_code.substr(0, 4))){
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text("From Account must be equal to or smaller than From Account !");
            $('#notificationModal_text2').text('');
            $("#notificationModal").modal("show");
            if (accGrp.acc2_id){
                setTimeout(function(){
                    $(this).val(accGrp.acc2_id).trigger('change');
                }, 800);
            }
        } else {
            var str_to_search = accGrp.acc_code_text;
            first_account_exist = str_to_search.search('-')>=0 ? true : false;
            if (!first_account_exist){
                $("#acc_code_text").val(accGrp.acc1_code);
            } else {
                var str_to_replace = str_to_search.split('-')[0];
                var new_str = str_to_search.replace(str_to_replace, accGrp.acc1_code);
                $("#acc_code_text").val(new_str);
            }
        }
    }
});

$( "#to_account" ).change(function(){
    $(".div_error_msg").addClass('hide');
    var acc_from_id = $("#from_account").select2('data')[0]['id'];
    var acc_from_text = $("#from_account").select2('data')[0]['text'];
    var acc_to_id = $(this).select2('data')[0]['id'];
    var acc_to_text = $(this).select2('data')[0]['text'];
    var acc_code_txt = $("#acc_code_text").val();

    if (acc_from_id){
        if (parseInt(acc_to_text.substr(0, 4))<parseInt(acc_from_text.substr(0, 4))){
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text("To Account must be equal to or higher than From Account !");
            $('#notificationModal_text2').text('');
            $("#notificationModal").modal("show");
            setTimeout(function(){
                $(this).val(acc_from_id).trigger('change');
            }, 800);
        } else {
            if (acc_to_id){
                var str_to_search = $("#acc_code_text").val();
                second_account_exist = str_to_search.search('-')>=0 ? true : false;
                if (!second_account_exist){
                    $("#acc_code_text").val(acc_code_txt+'-'+acc_to_text);
                } else {
                    var str_to_replace = str_to_search.split('-')[1];
                    var new_str = str_to_search.replace(str_to_replace, acc_to_text);
                    $("#acc_code_text").val(new_str);
                }
            }
        }
    } else {
        $("#from_account").val(acc_to_id).trigger('change');
    }
});

function clearTransactionForm(form)
{
    $("#from_account").val("").trigger('change');
    $("#to_account").val("").trigger('change');
    $("#acc_code_text").val("");
    $("#description").val("");
}

function AccGrp() {
    this.acc1_code = "";
    this.acc2_code = "";
    this.acc_code_text = "";
    this.desc = "";
    this.acc1_id = "";
    this.acc2_id = "";
    this.line = "";
    this.template_type = "";
}

function isValid() {
    var isValid = true;
    var accGrp = getTransactionFormData();
    if (!accGrp.acc1_id){ isValid = false; }
    if (accGrp.acc2_id) {
        if (parseInt(accGrp.acc1_code.substr(0, 4)) > parseInt(accGrp.acc2_code.substr(0, 4))){
            isValid = false;
        }
    }
    if (!isValid){
        $("#div_error_msg").removeClass('hide');
        $("#error_msg").text('From Account cannot be empty and must be smaller than To Account !');
    }
    return isValid;
}

function getTransactionFormData() {
    var accGrp = new AccGrp();
    accGrp.acc1_id = $("#from_account").val();
    accGrp.acc1_code = $('#from_account option:selected').text();
    if ($("#to_account").val()){
        accGrp.acc2_id = $("#to_account").val();
        accGrp.acc2_code = $('#to_account option:selected').text();
    }
    accGrp.acc_code_text = $("#acc_code_text").val();
    accGrp.desc = $("#description").val();
    return accGrp;
}

function addTransaction(template_type) {
    var validate = isValid();
    if (validate) {
        var accGrp = getTransactionFormData();
        var datatbl = null;
        if (template_type=='0'){
            datatbl = $('#pl-table').DataTable();
        } else if (template_type == '1'){
            datatbl = $('#bs-table').DataTable();
        }
        var line = parseInt(datatbl.page.info().recordsTotal) + 1;
        var button = '<a class="btn btn-white fa fa-pencil" onclick="editNewTransactionModal(' + line + ',' + template_type + ')"></a>'
            +'<a class="btn btn-white fa fa-minus" onclick="deleteNewTransactionModal(' + line + ',' + template_type + ')"></a>';

        datatbl.row.add( [
            line,
            accGrp.acc1_code,
            accGrp.acc2_code,
            accGrp.acc_code_text,
            accGrp.desc,
            button,
            accGrp.acc1_id,
            accGrp.acc2_id,
            ""
        ] ).draw( false );

        accGrp.line = line;
        accGrp.template_type = template_type;
        transaction_new.push(accGrp);

        $("#AddAcctGrpRow").modal("hide");
    }
    $("#btnSavePL").prop('disabled', false);
    $("#btnSaveBS").prop('disabled', false);
}

function setTransactionForm(transaction) {
    $("#from_account").val(transaction.acc1_id).trigger('change');
    if (transaction.acc2_id){
        $("#to_account").val(transaction.acc2_id).trigger('change');
    }
    $("#acc_code_text").val(transaction.acc_code_text);
    $("#description").val(transaction.desc);
}

function editNewTransactionModal(line, template_type) {
    clearTransactionForm();
    var result = $.grep(transaction_new, function (e) {
        return e.line == line && e.template_type == template_type;
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
    $("#AddRow").attr("onclick", "editNewTransaction(" + line + "," + template_type + ")");
    $("#AddAcctGrpRow").modal("show");
}

function editNewTransaction(line, template_type) {
    var validate = isValid();
    if (validate) {
        var accGrp = getTransactionFormData();
        var datatbl = null;
        if (template_type=='0'){
            datatbl = $('#pl-table').DataTable();
        } else if (template_type == '1'){
            datatbl = $('#bs-table').DataTable();
        }
        var row = line - 1;

        datatbl.cell(row, $("#acc1_code").index()).data(accGrp.acc1_code);
        datatbl.cell(row, $("#acc2_code").index()).data(accGrp.acc2_code);
        datatbl.cell(row, $("#acc_code_txt").index()).data(accGrp.acc_code_text);
        datatbl.cell(row, $("#acc_grp_desc").index()).data(accGrp.desc);
        datatbl.cell(row, $("#acc1_id").index()).data(accGrp.acc1_id);
        datatbl.cell(row, $("#acc2_id").index()).data(accGrp.acc2_id);
        datatbl.draw();


        accGrp.line = line;
        accGrp.template_type = template_type;
        var result = $.grep(transaction_new, function (e) {
            return e.line == line && e.template_type == template_type;
        });
        if (result.length == 0) {
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Failed to update record!');
            $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
            $("#notificationModal").modal("show");
            return 0;
        } else if (result.length == 1) {
            result[0].line = accGrp.line;
            result[0].acc1_code = accGrp.acc1_code;
            result[0].acc2_code = accGrp.acc2_code;
            result[0].acc_code_text = accGrp.acc_code_text;
            result[0].desc = accGrp.desc;
            result[0].acc1_id = accGrp.acc1_id;
            result[0].acc2_id = accGrp.acc2_id;
            result[0].template_type = accGrp.template_type;
        }
        $("#AddAcctGrpRow").modal("hide");
    }
}

function deleteNewTransactionModal(line,template_type) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteNewTransaction(" + line + "," + template_type + ")");
}

function deleteNewTransaction(line, template_type) {
    $("#comfirmDeleteTransactionForm").submit(function(e){
        e.preventDefault(e);
        var datatbl = null;
        if (template_type=='0'){
            datatbl = $('#pl-table').DataTable();
        } else if (template_type == '1'){
            datatbl = $('#bs-table').DataTable();
        }

        // Remove row
        datatbl.row(line - 1).remove().draw();
        var deleted_line = line;
        $.map(transaction_new, function(value, key) {
            if(value && value.line == deleted_line) {
                transaction_new.splice(key, 1);
                return true;
            }
        });
        $("#comfirmDeleteTransactionModal").modal("hide");
    });
}

function editOldTransactionModal(id, line, template_type) {
    clearTransactionForm();

    var result = $.grep(transaction_update, function (e) {
        return e.line == line && e.template_type == template_type;
    });
    if (result.length == 0) {
        $.ajax({
            method: "POST",
            url: '/accounts/get_rpt_acc_grp/',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'rpt_acc_grp_id': id
            },
            success: function (data) {
                var accGrp = new AccGrp();
                accGrp.acc1_id = data[0].account_from_id;
                accGrp.acc1_code = data[0].account_from_code;
                accGrp.acc_code_text = data[0].account_code_text;
                accGrp.acc2_id = data[0].account_to_id;
                accGrp.acc2_code = data[0].account_to_code;
                accGrp.desc = data[0].name;
                setTransactionForm(accGrp);
            },
            error: function () {
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Failed to load transaction records !');
                $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
                $("#notificationModal").modal("show");
            }
        });
    } else if (result.length == 1) {
        setTransactionForm(result[0]);
    }
    
    $("#AddRow").attr("onclick", "editOldTransaction(" + line + "," + template_type + ")");
    $("#AddAcctGrpRow").modal("show");
}

// Save Update Old Transaction
function editOldTransaction(line,template_type) {
    var validate = isValid();
    if (validate) {
        var accGrp = getTransactionFormData();
        var datatbl = null;
        if (template_type=='0'){
            datatbl = $('#pl-table').DataTable();
        } else if (template_type == '1'){
            datatbl = $('#bs-table').DataTable();
        }
        var row = line - 1;

        datatbl.cell(row, $("#acc1_code").index()).data(accGrp.acc1_code);
        datatbl.cell(row, $("#acc2_code").index()).data(accGrp.acc2_code);
        datatbl.cell(row, $("#acc_code_txt").index()).data(accGrp.acc_code_text);
        datatbl.cell(row, $("#acc_grp_desc").index()).data(accGrp.desc);
        datatbl.cell(row, $("#acc1_id").index()).data(accGrp.acc1_id);
        datatbl.cell(row, $("#acc2_id").index()).data(accGrp.acc2_id);
        datatbl.draw();

        accGrp.line = line;
        accGrp.template_type = template_type;
        var result = $.grep(transaction_update, function (e) {
            return e.line == line && e.template_type == template_type;
        });
        if (result.length == 0) {
            transaction_update.push(accGrp);
        } else if (result.length == 1) {
            result[0].line = accGrp.line;
            result[0].acc1_code = accGrp.acc1_code;
            result[0].acc2_code = accGrp.acc2_code;
            result[0].acc_code_text = accGrp.acc_code_text;
            result[0].desc = accGrp.desc;
            result[0].acc1_id = accGrp.acc1_id;
            result[0].acc2_id = accGrp.acc2_id;
            result[0].template_type = accGrp.template_type;
        }
        $("#AddAcctGrpRow").modal("hide");
        $("#btnSavePL").prop('disabled', false);
        $("#btnSaveBS").prop('disabled', false);
    }
}

// Show Comfirm delete old transaction
function deleteOldTransactionModal(trxid,template_type) {
    $("#comfirmDeleteTransactionModal").modal("show");
    $("#comfirm-yes").attr("onclick", "deleteOldTransaction("+ trxid +","+ template_type +")");
}

function deleteOldTransaction(trxid,template_type){
    var url = '/accounts/del_rpt_acc_grp/'+ trxid +'/'+ template_type +'/';
    $("#btnSavePL").prop('disabled', false);
    $("#btnSaveBS").prop('disabled', false);
    $("#comfirmDeleteTransactionForm").attr("action", url);
}

$('#btnSavePL').on('click', function(){
    $("#frm_rpt_acctgrp").submit(function(e){
        var array = [];
        var pl_datatbl = $('#pl-table').DataTable();
        pl_datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
            rowData = this.data();
            acct_grp_row = {};
            acct_grp_row.acc1 = rowData[$("#acc1_id").index()];
            acct_grp_row.acc2 = rowData[$("#acc2_id").index()];
            acct_grp_row.acc_code_text = rowData[$("#acc_code_txt").index()];
            acct_grp_row.desc = rowData[$("#acc_grp_desc").index()];
            array.push(acct_grp_row);
        });
        $('#template_pl').val(JSON.stringify(array));
        $('#template_type').val('0');
        $('#btnSavePL').prop('disabled', true);
        return;
    })
});

$('#btnSaveBS').on('click', function(){
    $("#frm_rpt_acctgrp").submit(function(e){
        var array = [];
        var bs_datatbl = $('#bs-table').DataTable();
        bs_datatbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
            rowData = this.data();
            acct_grp_row = {};
            acct_grp_row.acc1 = rowData[$("#acc1_id").index()];
            acct_grp_row.acc2 = rowData[$("#acc2_id").index()];
            acct_grp_row.acc_code_text = rowData[$("#acc_code_txt").index()];
            acct_grp_row.desc = rowData[$("#acc_grp_desc").index()];
            array.push(acct_grp_row);
        });
        $('#template_bs').val(JSON.stringify(array));
        $('#template_type').val('1');
        $('#btnSaveBS').prop('disabled', true);
        return;
    })
});
