/**
 * Created by tho.pham on 12/8/2016.
 */
$('#btnSearchBank').on('click', function () {
    $('#bank-table').DataTable().destroy();
    $('#bank-table').dataTable({
        "order": [[0, "desc"]],
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
});

$('#bank-table').on( 'draw.dt', function () {
    selectTableRow('#bank-table', 4);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});


$('#btnSelectBank').on('click', function () {
    var selected_row = [];
    var dtTable = $('#bank-table').DataTable();
    $("input[name='choices']:checked").each(function () {
        selected_row.push(this.value);
        var dtRow = dtTable.row($(this).parents('tr')[0]).data();
        selected_row.push(dtRow['currency_id']);
        selected_row.push(dtRow['name']);
        selected_row.push(dtRow['account']);
    });
    if (selected_row.length > 0) {
        $('#id_bank option').removeAttr('selected');
        $('#id_bank option[value="' + selected_row[0] + '"]').prop('selected', true);
        $('#select2-id_bank-container').text($('#id_bank option:selected').text());
        $('#id_currency option').removeAttr('selected');
        $('#id_currency option[value="' + selected_row[1] + '"]').prop('selected', true)
        $('#id_description').val(selected_row[2]);
        $('#id_bank_account_number').val(selected_row[3]);
        $('#btnAddTransactionDialog').removeAttr('disabled');
        $('#btnPost').prop('disabled', false);
    } else {
        $('#btnAddTransactionDialog').attr('disabled', true);
        $('#btnPost').prop('disabled', true);
    }
});


$('#id_bank').on('change', function () {
    $('#btnAddTransactionDialog').removeAttr('disabled');
    $('#btnPost').prop('disabled', false);
    var bank_id = parseInt($(this).val());
    $.ajax({
        method: "POST",
        url: url_load_currency,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'bank_id': bank_id
        },
        success: function (json) {
            if (json['name'] != null) {
                $('#id_description').val(json['name']);
            } else {
                $('#id_description').val('');
            }
            $('#id_currency option').removeAttr('selected');
            if (json['currency_id'] != null) {
                $('#id_currency option[value="' + json['currency_id'] + '"]').prop('selected', true);
            } else {
                $('#id_currency option:empty').prop('selected', true);
            }
            if (json['account_number'] != null) {
                $('#id_bank_account_number').val(json['account_number']);
            } else {
                $('#id_bank_account_number').val('');
            }
        }
    });
});


$('#btnAddTransactionDialog').on('click', function () {
    advance_search();
});

$('#id_journal_type').on('change', function () {
    if ($('#id_bank').val()){
    var journal_type = parseInt($(this).val());
    $('#transaction-table').DataTable().destroy();
    $('#document-journal-table').DataTable().destroy();
    if (journal_type == 3) { /* TRANSACTION_TYPES['AR Receipt'] */
        $('#transaction-table').DataTable({
            'bFilter': false,
            'bLengthChange': false,
            'bSort': false,
            'columnDefs': [
                {
                    "title": "Customer Number",
                    targets: [1],
                },
                {
                    "title": "Customer Name",
                    targets: [2],
                },
                {
                    "title": "Check/Receipt No.",
                    targets: [3],
                },
                {
                    "title": "Receipt Amount",
                    targets: [4],
                },
                {
                    "title": "Receipt Date",
                    targets: [5],
                },
                {
                    "visible": false,
                    targets: [7],
                }
            ]
        });
        $('#document-journal-table').DataTable({
            'columnDefs': [
                {
                    "title": "Customer Number",
                    targets: [0],
                },
                {
                    "title": "Customer Name",
                    targets: [1],
                },
            ]
        });
    } else {
        $('#transaction-table').DataTable({
            'bFilter': false,
            'bLengthChange': false,
            'bSort': false,
            'columnDefs': [
                {
                    "title": "Vendor Number",
                    "targets": [1],
                },
                {
                    "title": "Vendor Name",
                    targets: [2],
                },
                {
                    "title": "Check/Payment No.",
                    targets: [3],
                },
                {
                    "title": "Payment Amount",
                    targets: [4],
                },
                {
                    "title": "Payment Date",
                    targets: [5],
                },
                {
                    "visible": false,
                    targets: [7],
                }
            ]
        });
        $('#document-journal-table').DataTable({
            'columnDefs': [
                {
                    "title": "Vendor Number",
                    targets: [0],
                },
                {
                    "title": "Vendor Name",
                    targets: [1],
                },
            ]
        });
    }
    load_advance_search_from(journal_type);
    advance_search();
    }
});

function JournalTransaction() {
    this.reversal_date = null;
    this.vendor_customer_number = null;
    this.vendor_customer_name = null;
    this.payment_check_no = null;
    this.amount = null;
    this.transaction_date = null;
    this.reason = null;
    this.journal_id = null;
}

function getTransactionForm(row) {
    var transaction = new JournalTransaction();
    datatbl = $('#document-journal-table').DataTable();
    var currentRow = datatbl.row(row).data();
    transaction.vendor_customer_number = currentRow.vendor_customer_number;
    transaction.vendor_customer_name = currentRow.vendor_customer_name;
    transaction.payment_check_no = currentRow.payment_check_no;
    transaction.amount = currentRow.functional_amount;
    transaction.transaction_date = currentRow.transaction_date;
    transaction.journal_id = currentRow.journal_id;
    return transaction;
}

function selectDocuments() {
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
            var rowTransaction = getTransactionForm(selected_row[i]);
            var button = '<button id="removerow' + row_number + '" type="button" class="btn btn-white fa fa-minus" value="Delete" onclick="deleteTransaction(' + row_number + ')">'
                + '</button>';
            reversalDate = '<input class="form-control-item" id="reversalDate-' + row_number + '" name="reversalDate" type="datetime" style="width: 100%">'
            reasonReversal = '<input class="form-control-item" id="reasonReversal-' + row_number + '" name="reasonReversal" type="text" style="width: 100%">'
            array_row = [
                reversalDate,
                rowTransaction.vendor_customer_number,
                rowTransaction.vendor_customer_name,
                rowTransaction.payment_check_no,
                rowTransaction.amount,
                rowTransaction.transaction_date,
                reasonReversal,
                rowTransaction.journal_id,
                button,
            ]
            row_number++;
            table.row.add(array_row).draw(false);
        }
        ;
        $('#transaction-table tr:last').each(function () {
            $("input[name*='reversalDate']").datepicker({
                format: 'dd-mm-yyyy',
                todayHighlight: true,
                autoclose: true,
            });
        });
        $("input[name*='reversalDate']").datepicker("update", new Date());

        $("#TransactionModal").modal("hide");

    } else {
        $("#message_error").text("Please choose at least 1 document");
    }
}


function deleteTransaction(row) {
    var table = $('#transaction-table').DataTable();
    table.row(row).remove().draw();
    table.rows().every(function (rowIdx, tableLoop, rowLoop) {
        table.cell(rowIdx, $("#trs-rev-date").index()).node().firstChild.id = 'reversalDate-' + rowIdx;
        table.cell(rowIdx, $("#trs-reason").index()).node().firstChild.id = 'reasonReversal-' + rowIdx;
        var button_delete = table.cell(rowIdx, $("#removerow-" + rowIdx).index()).node().firstElementChild.id;
        $('#' + button_delete).attr("onclick", "deleteTransaction(" + rowIdx + ")");
        $('#' + button_delete).attr("id", "removerow" + rowIdx);
    });
};


$('#btnPost').on('click', function () {
    var allVals = [];
    datatbl = $('#transaction-table').DataTable();
    var text_input = $('#transaction-table').dataTable().fnGetNodes();
    var rows = $('#transaction-table').dataTable().fnGetData();
    for (var i = 0; i < rows.length; i++) {
        var transaction = new JournalTransaction();
        transaction.reversal_date = text_input[i].cells[0].firstChild.value.split("-").reverse().join("-");
        transaction.vendor_customer_number = rows[i][1];
        transaction.vendor_customer_name = rows[i][2];
        transaction.payment_check_no = rows[i][3];
        transaction.amount = rows[i][4];
        transaction.transaction_date = rows[i][5];
        transaction.reason = text_input[i].cells[6].firstChild.value;
        transaction.journal_id = rows[i][7];
        allVals.push(transaction);
    }
    $('#listTrans').val(JSON.stringify(allVals));
});


$('#btnAdvanceSearch').click(function () {
    $('#advanceSearchForm').slideToggle(1000, 'swing');
});

function advance_search() {
    var bank_id = parseInt($('#id_bank').val());
    var journal_type = parseInt($('#id_journal_type').val());
    var exclude_transaction_list = [];
    var datatbl = $('#document-journal-table').DataTable();
    var transactionTbl = $('#transaction-table').DataTable();
    transactionTbl.rows().every(function (rowIdx, tableLoop, rowLoop) {
        journal_id = this.data()[7];
        exclude_transaction_list.push(journal_id);
    });
    datatbl.destroy();
    datatbl.clear().draw();
    $('#document-journal-table').dataTable({
        'bFilter': false,
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[0, "desc"]],
        "serverSide": true,
        "ajax": {
            "url": url_advance_search,
            "data": {
                'bank_id': bank_id,
                'journal_type': journal_type,
                "exclude_transaction_list": JSON.stringify(exclude_transaction_list),
                'payment_check_no': JSON.stringify($('#payment_check').val()),
                'vendor_customer': JSON.stringify($('#vendor_customer').val()),
                'from_date': $('.dpd1').val().split("-").reverse().join("-"),
                'to_date': $('.dpd2').val().split("-").reverse().join("-"),
                'from_amount': $('#from_amount').val(),
                'to_amount': $('#to_amount').val()
            }
        },
        "columns": [
            {"data": "vendor_customer_number", "sClass": "text-left"},
            {"data": "vendor_customer_name", "sClass": "text-left"},
            {"data": "functional_amount", "sClass": "text-left"},
            {"data": "batch_number", "sClass": "text-left"},
            {"data": "entry_number", "sClass": "text-left"},
            {"data": "payment_code", "sClass": "text-left"},
            {"data": "transaction_date", "sClass": "text-left"},
            {"data": "payment_check_no", "sClass": "text-left"},
            {"data": "journal_id", "sClass": "text-left", "visible": false},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, full, meta) {
                    return '<input type="checkbox" name="document-choices" id="check-' +
                        meta.row + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });
}


function load_advance_search_from(journal_type) {
    $.ajax({
        method: "POST",
        url: url_advance_search_form,
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'journal_type': journal_type,
        },
        success: function (data) {
            $('#advanceSearchForm').html(data);
            $('#payment_check').select2();
            $('#vendor_customer').select2();
            $(".dpd1").datepicker({
                format: 'dd-mm-yyyy',
                todayHighlight: true,
                autoclose: true,
            });
            $('.dpd1').datepicker("update", new Date());
            $(".dpd2").datepicker({
                format: 'dd-mm-yyyy',
                todayHighlight: true,
                autoclose: true,
            });
            $('.dpd2').datepicker("update", new Date());
            $('#btnSearch').on("click", function () {
                advance_search();
            });
            if (parseInt(journal_type) == 3) { /* TRANSACTION_TYPES['AR Receipt'] */
                $('#lblCheckNo').html('Check/Receipt No.');
                $('#lblNumber').html('Customer Number');
                $('#lblDate').html('Receipt Date');
                $('#lblAmount').html('Receipt Amount');
            } else {
                $('#lblCheckNo').html('Check/Payment No.');
                $('#lblNumber').html('Vender Number');
                $('#lblDate').html('Payment Date');
                $('#lblAmount').html('Payment Amount');
            }
        }
    });
}


$(document).ready(function () {
    var journal_type = $('#id_journal_type').val();
    load_advance_search_from(journal_type);
})
