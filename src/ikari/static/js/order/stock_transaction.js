/**
 * Created by tho.pham on 11/1/2016.
 */

var ST_ROW_INDEX_LINE_NUMBER = 0;
var ST_ROW_INDEX_ITEM_CODE = ST_ROW_INDEX_LINE_NUMBER + 1;
var ST_ROW_INDEX_ITEM_ID = ST_ROW_INDEX_ITEM_CODE + 1;
var ST_ROW_INDEX_QUANTITY = ST_ROW_INDEX_ITEM_ID + 1;
var ST_ROW_INDEX_PRICE = ST_ROW_INDEX_QUANTITY + 1;
var ST_ROW_INDEX_AMOUNT = ST_ROW_INDEX_PRICE + 1;
var ST_ROW_INDEX_STOCK_QTY = ST_ROW_INDEX_AMOUNT + 1;
var ST_ROW_INDEX_ITEM_INV_UOM = ST_ROW_INDEX_STOCK_QTY + 1;
var ST_ROW_INDEX_ITEM_NAME = ST_ROW_INDEX_ITEM_INV_UOM + 1;
var ST_ROW_INDEX_ITEM_ONHAND = ST_ROW_INDEX_ITEM_NAME + 1;
var ST_ROW_INDEX_REMARK = ST_ROW_INDEX_ITEM_ONHAND + 1;


var ST_LABEL_INDEX_LINE_NUMBER = 0;
var ST_LABEL_INDEX_ITEM_CODE = ST_LABEL_INDEX_LINE_NUMBER + 1;
var ST_LABEL_INDEX_AMOUNT = ST_LABEL_INDEX_ITEM_CODE + 1;

/* ST Column Index */

var ST_COL_BUTTONS = 0;
var ST_COL_LINE_NUMBER = ST_COL_BUTTONS + 1;
var ST_COL_ITEM_NAME = ST_COL_LINE_NUMBER + 1;
var ST_COL_QTY = ST_COL_ITEM_NAME + 1;
var ST_COL_PRICE = ST_COL_QTY + 1;
var ST_COL_AMOUNT = ST_COL_PRICE + 1;
var ST_COL_STOCK_QTY = ST_COL_AMOUNT + 1;
var ST_COL_INV_MESMNT = ST_COL_STOCK_QTY + 1;
var ST_COL_ITEM_DESC = ST_COL_INV_MESMNT + 1;
var ST_COL_ONH_QTY = ST_COL_ITEM_DESC + 1;
var ST_COL_REMARK = ST_COL_ONH_QTY + 1;

var ALL_VALUES = [];

var store_row_temporary = '';

function disableAutoComplete() {
    $("input[type='text']").each(function() {
        $(this).attr("autocomplete", "off");
    });
    $("input[type='number']").each(function() {
        $(this).attr("autocomplete", "off");
    });
}

$(document).ready(function () {
    disableAutoComplete();
    store_row_temporary = $('#dynamic-table tr.gradeX:last').clone(true);
    changeAttr(store_row_temporary, parseInt($('#id_formset_customer_item-TOTAL_FORMS').val()) - 1, 0);

    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });
    load_items();

    $('#id_transaction_code').select2({
        placeholder: "Select Transaction Code",
    });
    $('#id_in_location').select2({
        placeholder: "Select In Location",
        allowClear: true
    });
    $('#id_out_location').select2({
        placeholder: "Select Out Location",
        allowClear: true
    });
    $('#id_document_date_fake').addClass('text-right');
    $(document).on('select2:close', '#id_transaction_code', function (e) {
      $('#id_document_date_fake').focus();
    });

    if (parseInt(status,10)>1){ /* ORDER_STATUS['Draft'] */
        $("#form input").prop("disabled", true);
        $("#form select").prop("disabled", true);
        $('#btnOpenItemDialog').removeAttr('href');
    }

    var odr = $('#dynamic-table tr.gradeX:visible').length;
    for (var i = 0; i < odr; i++) {
        var gorounding = parseFloat($('#id_formset_item-'+i+'-amount').val());
        var text = parseFloat($('#id_formset_item-'+i+'-amount').text());
        var dirounding = text.toFixed(2);
        if (text > 0){
            var tt ='id_formset_item-'+i+'-amount'; //onclick="myFunction()"
            $('#id_formset_item-'+i+'-quantity').attr("onclick='qty_check("+i+")'")
            $('#id_formset_item-'+i+'-amount').text(dirounding);
            $('#id_formset_item-'+i+'-amount').val(dirounding);
        }
    }
    if (!$('#id_transaction_code').val()) {
        $('#id_in_location').prop('disabled', true);
        $('#id_out_location').prop('disabled', true);
        $('#btnSearchInLocation').prop('disabled', true);
        $('#btnSearchOutLocation').prop('disabled', true);
    }

    if ($('#id_io_flag').val() == '1') {
        if (parseInt(status,10)<2){ /* ORDER_STATUS['Sent'] */
            $('#id_in_location').prop('disabled', false);
        }
        $('#id_out_location').prop('disabled', true);
        $('#btnSearchOutLocation').prop('disabled', true);
    } else if ($('#id_io_flag').val() == '2') {
        $('#id_in_location').prop('disabled', false);
        $('#id_out_location').prop('disabled', false);
        $('#btnSearchInLocation').prop('disabled', false);
        $('#btnSearchOutLocation').prop('disabled', false);
    } else if ($('#id_io_flag').val() == '3') {
        $('#id_in_location').prop('disabled', true);
        $('#btnSearchInLocation').prop('disabled', true);
        if (parseInt(status,10)<2){ /* ORDER_STATUS['Sent'] */
            $('#id_out_location').prop('disabled', false);
        }
    } else {
        $('#id_in_location').prop('disabled', true);
        $('#id_out_location').prop('disabled', true);
    }

    if (request_method == 'GET') {
        if ($('#id_formset_item-TOTAL_FORMS').val() > 0) {
            $('#dynamic-table tr.gradeX:last').remove();
            $('#id_formset_item-TOTAL_FORMS').val($('#id_formset_item-TOTAL_FORMS').val() - 1);
        }
        $('#items_error').css("display", "none");

    } else if (request_method == 'POST') {
        var item = $('#id_formset_item-0-item').val();
        var quantity = $('#id_formset_item-0-quantity').val();
        var price = $('#id_formset_item-0-price').val();
        var amount = $('#id_formset_item-0-amount').val();
        if (quantity == "" && price == "" && amount == "") {
            $('#dynamic-table tr.gradeX:last').css("display", "none");
            $('#items_error').removeAttr('style');
        } else $('#items_error').css("display", "none");
    }
    if (stock_trans_id != '') {
        fnEnableButton();
    } else {
        fnDisableButton();
    }
    if ($('#id_transaction_code').val() == '') {
        $('#btnOpenItemDialog').prop('disabled', true);
    }
    if (status == '1') { /* ORDER_STATUS['Draft'] */
        $('#btnOpenItemDialog').prop('disabled', false);
    }

    $('#id_transaction_code').select2("open");

    $("#id_transaction_code").bind('keydown', function(event) {
        if (event.which == 13) {
            setTimeout(function() {
            $Target = '#id_document_date_fake';
            $($Target).select();}, 300);
            return false;
        }
    });

    $("#id_in_location").on("select2:close", function() {
        if($('#id_io_flag').val()=='1'){
            setTimeout(function() {
            $Target = '#id_remark';
            $($Target).select();}, 300);
        }else{
            setTimeout(function() {
            $Target = '#id_out_location';
            $($Target).select2("open");}, 300);
        }
        return false;
    });

    $('#id_transaction_code').on("select2:open", function (event) {
        prefill_select2(event);
    });

    $('#id_in_location').on("select2:open", function (event) {
        prefill_select2(event);
    });

    $("#id_out_location").on("select2:close", function() {
        setTimeout(function() {
        $Target = '#id_remark';
        $($Target).select();}, 300);
        return false;
    });

    $('#id_out_location').on("select2:open", function (event) {
        prefill_select2(event);
    });
});

$('#id_document_date_fake').on('change', function() {

    var date_from = get_date_from("#id_document_date_fake");
    date_from = date_from.split('/').join('-');
    var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();
    if (!date_from_valid){

        $("#id_document_date_fake").val(moment($("#id_document_date").val(),"YYYY-MM-DD").format("DD-MM-YYYY"));
    }else{
        var date_rate_1 = dateView(date_from);
        $("#id_document_date").val(date_rate_1);
    }
});

$('#id_document_date_fake').keyup(function(event){
    adjust_input_date(this);
});

function fnDisableButton() {
    $('#btnSave').attr('disabled', true);
    $('#btnSend').attr('disabled', true);
    $('#btnSendForEdit').attr('disabled', true);
    $('#btnDelete').attr('disabled', true);
};

function fnEnableButton() {
    $('#btnSave').removeAttr('disabled');
    $('#btnSend').removeAttr('disabled');
    $('#btnSendForEdit').removeAttr('disabled');
    $('#btnDelete').removeAttr('disabled');
};


var datatbl = $('#tblTransCode').DataTable();
var dataLocation = $('#tblLocation').DataTable();

$(document).keypress(function (e) {
    if (e.which == 13 && !$(event.target).is("textarea")) {
        e.preventDefault();
    }
});

$('#id_document_date_fake').on('click', function () {
    $('#id_document_date_fake').select();
});

var temp_io_flag = '';
$('#id_transaction_code').on('change', function () {
    setTimeout(function() {
        $Target = '#id_document_date_fake';
        $($Target).select();}, 300);

    $('#id_out_location').val('').trigger('change');
    $('#id_in_location').val('').trigger('change');
    temp_io_flag = '';
    $('#loading').show();
    if ($('#id_transaction_code').val() == '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: search_transaction_code,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'transaction_code': $("#id_transaction_code").val()
        },
        success: function (json) {
            fnRemoveAllItems();
            $('#btnOpenItemDialog').attr('disabled', true);
            fnDisableButton();
            if (jQuery.isEmptyObject(json) == false) {
                $('#id_io_flag').val(json['io_flag_id']);
                $('#id_io_flag_name').val(json['io_flag']);

                $('#id_price_flag').val(json['price_flag_id']);
                $('#id_price_flag_name').val(json['price_flag']);
                if (json['auto_generate'] == true) {
                    $('#id_document_number').attr('disabled', true);
                } else {
                    $('#id_document_number').removeAttr('disabled');
                }
                if (json['io_flag'] == 'IN') {
                    $('#id_in_location').attr('required', true);
                    $('#id_in_location').prop('disabled', false);
                    $('#id_out_location').prop('disabled', true);
                    $('#btnSearchInLocation').prop('disabled', false);
                    $('#btnSearchOutLocation').prop('disabled', true);
                    $('#id_in_location').find('option:eq(0)').prop('selected', true);
                    $('#id_in_location').trigger('change');
                } else if (json['io_flag'] == 'OUT') {
                    $('#id_out_location').attr('required', true);
                    $('#id_in_location').prop('disabled', true);
                    $('#id_out_location').prop('disabled', false);
                    $('#btnSearchInLocation').prop('disabled', true);
                    $('#btnSearchOutLocation').prop('disabled', false);
                    $('#id_out_location').find('option:eq(0)').prop('selected', true);
                    $('#id_out_location').trigger('change');
                } else if (json['io_flag'] == 'Transfer') {
                    temp_io_flag = 'Transfer';
                    $('#id_in_location').attr('required', true);
                    $('#id_out_location').attr('required', true);
                    $('#id_in_location').prop('disabled', false);
                    $('#id_out_location').prop('disabled', false);
                    $('#btnSearchInLocation').prop('disabled', false);
                    $('#btnSearchOutLocation').prop('disabled', false);
                    $('#id_in_location').val('').trigger('change');
                    $('#id_out_location').val('').trigger('change');
                } else {
                    $('#id_in_location').prop('disabled', true);
                    $('#id_out_location').prop('disabled', true);
                    $('#btnSearchInLocation').prop('disabled', true);
                    $('#btnSearchOutLocation').prop('disabled', true);
                }
            } else {
                $('#btnOpenItemDialog').attr('disabled', true);
                fnDisableButton();
                $('#id_in_location').val('');
                $('#id_out_location').val('');
                $('#id_in_location').prop('readonly', true);
                $('#id_out_location').prop('readonly', true);
            }

            $('#loading').hide();
        }
    });
});

$('#id_in_location').on('change', function () {
    if ($(this).val() != '' && $(this).val() != undefined) {
        if (temp_io_flag == 'Transfer') {
            var in_loc = $('#id_in_location').val();
            var out_loc = $('#id_out_location').val();
            if (in_loc == out_loc) {
                pop_ok_dialog("Wrong selection",
                        "You can not select same location.",
                        function () { $('#id_in_location').val('').trigger('change'); });
            } else {
                $('#btnOpenItemDialog').removeAttr('disabled');
                fnEnableButton();
                fnRemoveAllItems();
                load_items();
            }
        } else {
            $('#btnOpenItemDialog').removeAttr('disabled');
            fnEnableButton();
            fnRemoveAllItems();
            load_items();
        }
    }
});

$('#id_out_location').on('change', function () {
    if ($(this).val() != '' && $(this).val() != undefined) {
        if (temp_io_flag == 'Transfer') {
            var in_loc = $('#id_in_location').val();
            var out_loc = $('#id_out_location').val();
            if (in_loc == out_loc) {
                pop_ok_dialog("Wrong selection",
                        "You can not select same location.",
                        function () { $('#id_out_location').val('').trigger('change'); });
            } else {
                $('#btnOpenItemDialog').removeAttr('disabled');
                fnEnableButton();
                fnRemoveAllItems();
                load_items();
            }
        } else {
            $('#btnOpenItemDialog').removeAttr('disabled');
            fnEnableButton();
            fnRemoveAllItems();
            load_items();
        }
    }
});


$('#btnSearchTransCode').on('click', function () {
    datatbl.destroy();
    $('#tblTransCode').dataTable({
        "order": [[0, "desc"]],
        "iDisplayLength": 5,
        "serverSide": true,
        "ajax": {
            "url": load_transaction_code_list,
        },
        "columns": [
            {"data": "update_date", "sClass": "text-left"},
            {"data": "code", "sClass": "text-left"},
            {
                "data": "code",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="choices" id="' + full.id + '" class="call-checkbox hide" value="' + full.id + '">' +
                        '<label for="exampleInputEmail1">'+full.code+'</label>';
                }
            },
            {"data": "name", "sClass": "text-left"},
            {"data": "io_flag", "sClass": "text-left"},
            {"data": "price_flag", "visible": false},
            {"data": "doc_type", "visible": false},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, full, meta) {
                    if (full.auto_generate == 'True') {
                        return '<span class="label label-success label-mini">True</span>';
                    }
                    else {
                        return '<span class="label label-danger label-mini">False</span>';
                    }
                }
            },
            {"data": "ics_prefix", "visible": false},
            // {
            //     "orderable": false,
            //     "data": null,
            //     "render": function (data, type, full, meta) {
            //         return '<input type="radio" name="choices" id="' +
            //             full.id + '" class="call-checkbox" value="' + full.id + '">';
            //     }
            // }
        ]
    });
});

function load_location(exclude_location_id) {
    // dataLocation.destroy();
    $('#tblLocation').dataTable({
        "order": [[0, "desc"]],
        "serverSide": true,
        "ajax": {
            "url": load_location_list,
            "data": {
                "exclude_location_id": exclude_location_id
            },
        },
        "columns": [
            {
                "data": "code",
                "sClass": "text-left",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="choice-location" id="' + full.id + '" class="call-checkbox hide" value="' + full.code + '">' +
                        '<label for="exampleInputEmail1">'+full.code+'</label>';
                }
            },
            {"data": "name", "sClass": "text-left"},
            {"data": "address", "sClass": "text-left"},
            // {
            //     "orderable": false,
            //     "data": null,
            //     "render": function (data, type, full, meta) {
            //         return '<input type="radio" name="choice-location" id="' + full.id + '" class="call-checkbox" value="' + full.code + '">';
            //     }
            // }
        ]
    });
}


$('#btnSearchInLocation').on('click', function () {
    $('#detectLocation').val('in');
    $('#modalLocation').modal('show');
    $('#tblLocation').DataTable().destroy();
    var exclude_location_id = 0;
    if ($('#id_out_location').val() != '') {
        exclude_location_id = $('#id_out_location').val();
    }
    load_location(exclude_location_id);
});


$('#btnAddLocation').on('click', function () {
    var location_id = $("input[name='choice-location']:checked").attr('id');
    var location_code = $("input[name='choice-location']:checked").val();
    if ($('#detectLocation').val() == 'in') {
        $('#id_in_location').val(location_id).trigger('change');
    } else if ($('#detectLocation').val() == 'out') {
        $('#id_out_location').val(location_id).trigger('change');
    }
    $('#btnOpenItemDialog').removeAttr('disabled');
    $('#tblLocation>tbody>tr.table-selected').removeClass('table-selected');
    fnEnableButton();
});


$('#btnSearchOutLocation').on('click', function () {

    $('#detectLocation').val('out');
    $('#modalLocation').modal('show');
    $('#tblLocation').DataTable().destroy();
    var exclude_location_id = 0;
    if ($('#id_in_location').val() != '') {
        exclude_location_id = $('#id_in_location').val();
    }
    load_location(exclude_location_id);
});

function fnRemoveAllItems() {
    $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {

        fnEnableButton();
        var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
        $('#id_formset_item-TOTAL_FORMS').val(minus);
        $(this)[0].remove();

        // if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
        //     $(this).closest('tr').css("background-color", "");
        //     $('#items_error').removeAttr('style');
        //     $(this).closest('tr').css('display', 'none');
        //     $(this).closest('tr').find('input').each(function () {
        //         $(this)[0].value = '';
        //     });
        //     $(this).closest('tr').find('label').each(function () {
        //         $(this)[0].textContent = '';
        //     });
        //     fnDisableButton()
        // } else {
        //     fnEnableButton();
        //     var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
        //     $('#id_formset_item-TOTAL_FORMS').val(minus);
        //     $(this)[0].remove();
        // }
        // $(this).find('td').each(function (colIndex, c) {
        //     $.each(this.childNodes, function (i, elem) {
        //         if (elem.nodeName == 'INPUT' || elem.nodeName == 'LABEL') {
        //             elem.attributes.name.nodeValue = elem.attributes.name.nodeValue.replace(/\d+/g, rowIndex);
        //             elem.id = elem.id.replace(/\d+/g, rowIndex);
        //         }
        //     });
        // });
    });
};


$('#btnAddTransCode').on('click', function () {
    $('#id_in_location').val('').trigger('change');
    $('#id_out_location').val('').trigger('change');
    $('#btnOpenItemDialog').attr('disabled', true);
    fnDisableButton();
    fnRemoveAllItems();
    var selected_id = $("input[name='choices']:checked").attr('id');
    if (selected_id != undefined) {
        var nRow = $("input[name='choices']:checked").parents('tr')[0];
        var jqInputs = $('td', nRow);
        $('#tblTransCode').DataTable().rows(nRow).every(function () {
            var data = this.data();
            $('#id_transaction_code').val(selected_id).trigger('change');
            if (data['auto_generate'] == "False") {
                $('#id_document_number').prop('readonly', false);
            } else {
                $('#id_document_number').prop('readonly', true);
            }
            $('#id_io_flag option').each(function () {
                $(this).removeAttr('selected');
                $(this).removeAttr('disabled');
                if ($(this).text() == data['io_flag']) {
                    $(this).attr('selected', 'selected');
                    if (data['io_flag'] == 'IN') {
                        $('#id_in_location').prop('readonly', false);
                        $('#id_out_location').prop('readonly', true);
                    } else if (data['io_flag'] == 'OUT') {
                        $('#id_in_location').prop('readonly', true);
                        $('#id_out_location').prop('readonly', false);
                    } else if (data['io_flag'] == 'Transfer') {
                        $('#id_in_location').prop('readonly', false);
                        $('#id_out_location').prop('readonly', false);
                    } else {
                        $('#id_in_location').prop('readonly', true);
                        $('#id_out_location').prop('readonly', true);
                    }
                }
            });
        });
        $('#tblTransCode>tbody>tr.table-selected').removeClass('table-selected');
    }
});


$('#btnOpenItemDialog').on('click', function () {
    var in_location_id = $('#id_in_location').val();
    var out_location_id = $('#id_out_location').val();
    $('#tbldataItems').DataTable().destroy();
    $('#tbldataItems').dataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[0, "desc"]],
        "serverSide": true,
        "ajax": {
            "url": load_stock_transaction_items_list,
            "data": {
                "in_location_id": in_location_id,
                "out_location_id": out_location_id
            },
        },
        "columns": [
            {"data": "item_code", "sClass": "text-left"},
            {"data": "item_name", "sClass": "text-left"},
            {"data": "stock_qty", "sClass": "text-right"},
            {"data": "location_code", "sClass": "text-left"},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, row, meta) {
                    return '<input type="checkbox" name="choices" id="' + row.id + '"'
                        + 'class="call-checkbox" value="' + row.item_code + '"></td>';
                }
            }
        ]
    });
});

$('#id_remark').click(function(){
    $(this).select();
});


$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $remark = '#' + currentRow[ST_ROW_INDEX_REMARK].id;
    $($remark).click(function () {
        $(this).select();
    });
});


function cloneMore(selector, type, allVals, insertIndex) {
    var i = 0;
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    $('#btnSave').removeAttr('disabled');
    if (insertIndex === undefined) insertIndex = 0;
    for (i; i < allVals.length; i++) {

        // if (allVals[i].item_id != 0) {
        var newElement = $(store_row_temporary).clone(true);

        newElement.removeAttr("style")
        //Set selected price of dialog to Price Column
        var currentRow = newElement.find('input');
        currentLabel = newElement.closest('tr').find('label');

        if (currentRow.length > 1) {
            currentRow[ST_ROW_INDEX_LINE_NUMBER].value = 1;
            currentRow[ST_ROW_INDEX_ITEM_CODE].value = allVals[i].item_code;
            currentRow[ST_ROW_INDEX_ITEM_ID].value = allVals[i].item_id;
            currentRow[ST_ROW_INDEX_PRICE].value = allVals[i].price;
            currentRow[ST_ROW_INDEX_REMARK].value = allVals[i].item_remark;
            currentRow[ST_ROW_INDEX_STOCK_QTY].value = allVals[i].stock_qty;
            currentRow[ST_ROW_INDEX_ITEM_INV_UOM].value = allVals[i].item_inv_measure;
            currentRow[ST_ROW_INDEX_ITEM_NAME].value = allVals[i].item_name;
            currentRow[ST_ROW_INDEX_ITEM_ONHAND].value = allVals[i].item_onhand;
            currentLabel[ST_LABEL_INDEX_LINE_NUMBER].textContent = currentRow[ST_ROW_INDEX_LINE_NUMBER].value; // Line Number
            currentLabel[ST_LABEL_INDEX_ITEM_CODE].textContent = currentRow[ST_ROW_INDEX_ITEM_CODE].value; // Item Code
        }

        var currentSelect = newElement.closest('tr').find('select');
        $(currentSelect[0]).empty();
        var item_by_loc_option = $('#item_by_loc').children().clone(true);
        $(currentSelect[0]).html(item_by_loc_option);
        $(currentSelect[0]).select2({
            placeholder: "Select item",
            allowClear: true,
        });
        $($(currentSelect[0]).parent('td').find('span')[0]).removeAttr("style");
        $($(currentSelect[0]).parent('td').find('span')[0]).attr('style', 'width: 150px !important');

        total++;

        if (insertIndex === 0) {
            if ($('#dynamic-table tr.gradeX').eq(insertIndex).length > 0) {
                $('#dynamic-table tr.gradeX').eq(insertIndex).before(newElement);
            } else {
                $('#dynamic-table tbody').append(newElement);
            }
        } else {
            $('#dynamic-table tr.gradeX').eq(insertIndex - 1).after(newElement);
        }
        insertIndex ++;
    }
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    updateLineNumber(total, insertIndex);
};

function updateLineNumber(total, insertIndex) {
    while(total >= insertIndex) {
        let changeElement = $($('#dynamic-table tr.gradeX').eq(total-1));
        let oldIndex = parseInt($(changeElement).closest('tr').find('label:first').text());
        var currentRowLabel = $(changeElement).closest('tr').find('label');
        var currentRowInput =  $(changeElement).closest('tr').find('input');
        currentRowInput[0].value = total;
        currentRowLabel[0].textContent = total;
        // change attribute name and id
        changeAttr(changeElement, (oldIndex - 1), (total-1));
        total--;
    }
}

function changeAttr(newElement, oldIndex, newIndex) {
    // change attribute name and id
    newElement.find('input').each(function () {
        var name = $(this).attr('name').replace('-' + oldIndex + '-', '-' + newIndex + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    newElement.find('select').each(function () {
        let name = $(this).attr('name').replace('-' + oldIndex + '-', '-' + newIndex + '-');
        let id = 'id_select_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    newElement.find('label').each(function () {
        var name = $(this).attr('name').replace('-' + oldIndex + '-', '-' + newIndex + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });

    newElement.find('span.select2-selection').each(function () {
        if($(this).attr('aria-labelledby') != undefined) {
            let aria_labelledby = $(this).attr('aria-labelledby').replace('-' + oldIndex + '-', '-' + newIndex + '-');
            $(this).attr({'aria-labelledby': aria_labelledby});
        }
    });

    newElement.find('span.select2-selection__rendered').each(function () {
        if($(this).attr('id') != undefined) {
            let id = $(this).attr('id').replace('-' + oldIndex + '-', '-' + newIndex + '-');
            $(this).attr({'id': id});
        }
    });
}

function highLightMandatory(rowCheck) {
    if ($('#id_select_formset_item-' + rowCheck +'-item_code').val() == '' || $('#id_select_formset_item-' + rowCheck +'-item_code').val() == undefined ) {
        $($('#select2-id_select_formset_item-' + rowCheck +'-item_code-container').parent('span')[0]).addClass('highlight-mandatory');
    } else {
        $($('#select2-id_select_formset_item-' + rowCheck +'-item_code-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-quantity').val()) > 0) {
        $('#id_formset_item-' + rowCheck +'-quantity').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-quantity').addClass('highlight-mandatory');
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-price').val()) > 0 ) {
       $('#id_formset_item-' + rowCheck +'-price').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-price').addClass('highlight-mandatory');
    }
}

function getFirstFieldInvalid(rowCheck) {
    var idFirstInvalid = '';
    if ($('#id_select_formset_item-' + rowCheck +'-item_code').val() == '') {
        idFirstInvalid = '#id_select_formset_item-' + rowCheck +'-item_code';
        return idFirstInvalid;
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-quantity').val()) <= 0) {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-quantity';
        return idFirstInvalid;
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-price').val()) <= 0 ) {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-price';
        return idFirstInvalid;
    }

    return idFirstInvalid;
}

function tabAddRow(rowIndex, keyPress) {
    if (keyPress == 9){
        var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
        if (rowIndex == rowCount) {
            $('#dynamic-table tr.gradeX').eq(rowCount - 1).find('.appendrow').trigger('click');
        }
         setTimeout(() => {
             if ($('#id_select_formset_item-' + rowIndex +'-item_code').is('select')) {
                $('#id_select_formset_item-' + rowIndex +'-item_code').focus();
                $('#id_select_formset_item-' + rowIndex +'-item_code').select2('open');
             } else {
                 $('#id_formset_item-' + rowIndex +'-quantity').focus();
                 $('#id_formset_item-' + rowIndex +'-quantity').select();
             }
        }, 300);
    }
}

function initialDataRow() {
    var allVals = [];
    allVals.push({
        item_id: '', //Item ID
        item_code: '',
        stock_qty: 0,
        price: 0,
        item_remark: '',
        item_name: '',
        item_inv_measure: '',
        item_onhand: '',
        location_code: ''
    });
    return allVals;
}

$('#btnAddItems').on('click', function () {
    var allVals = [];
    var table = $('#tbldataItems').DataTable();
    var rowcollection = table.$(".call-checkbox:checked", {"page": "all"});
    rowcollection.each(function (index, elem) {
        allVals.push({
            item_id: elem.id, //Item ID
            item_code: elem.value,
            stock_qty: elem.parentElement.parentElement.cells[2].textContent
        });
    });
    if (allVals.length > 0) {
        cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
        disableAutoComplete();
    }
    $(this).attr('data-dismiss', 'modal');
    $('#items_error').css('display', 'none');
});


$('.lastElement').on('keydown', function(e) {
    if (e.which == 9) {
        let rowCheck = parseInt($(this).closest('tr').find('label:first').text()) - 1;
        var idFirstInvalid = getFirstFieldInvalid(rowCheck);
        if (idFirstInvalid != '') {
            highLightMandatory(rowCheck);
            if (parseInt($(this).val()) == 0) {
                $(this).trigger('change');
                return;
            }
            pop_focus_invalid_dialog('Invalid Data',
            'Please fill up the required fields.',
            function(){
                $(idFirstInvalid).focus();
                if ($(idFirstInvalid).is('select')) {
                    $(idFirstInvalid).select2('open');
                }
            });
        } else {
            $(this).removeClass('highlight-mandatory');
            let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
            tabAddRow(rowIndex, e.which);
        }
    }
});

$('.select-item-code').on("select2:open", function(event) {
    prefill_select2(event);
});

$('.select-item-code').on("select2:close", function() {
    rowIndex = $(this).closest('tr').find('label:first').text() - 1;
    $('#id_formset_item-' + rowIndex + '-quantity').focus();
    $('#id_formset_item-' + rowIndex + '-quantity').select();
    let rowCheck = parseInt($(this).closest('tr').find('label:first').text()) - 1;
    highLightMandatory(rowCheck);
});

$('.select-item-code').on('change', function () {
    var item_id = $(this).val();
    var id_price_flag = $('#id_price_flag').val();

    var currentLabel = $(this).closest('tr').find('label');
    var currentInput = $(this).closest('tr').find('input');

    if (item_id != ''){
        $.ajax({
            type: "GET",
            url: '/inventory/item_per_detail/'+item_id,
            dataType: 'JSON',
            success: function(data){
                var data_items = data.data;
                if (data_items.length > 0){
                    for (i in data_items) {
                        var allVals = [];
                        var price = 0;
                        if (id_price_flag == '1'){
                            price = data_items[i].item_purchase_price;
                        }else if (id_price_flag == '2'){
                            price = data_items[i].item_stockist_price
                        }else{
                            price = data_items[i].item_sale_price;
                        }

                        allVals.push({
                            item_id: data_items[i].item_id, //Item ID
                            item_code: data_items[i].item_code,
                            stock_qty: data_items[i].stock_qty,
                            price:price,
                            item_remark: data_items[i].item_remark,
                            item_name: data_items[i].item_name,
                            item_inv_measure: data_items[i].item_inv_measure,
                            item_onhand: data_items[i].item_onhand,
                            location_code: data_items[i].location_code
                        });
                        if (allVals.length > 0) {
                            ALL_VALUES = allVals;


                            // currentRow[ST_ROW_INDEX_LINE_NUMBER].value = parseInt(line) + 1;
                            currentInput[ST_ROW_INDEX_ITEM_CODE].value = allVals[i].item_code;
                            currentInput[ST_ROW_INDEX_ITEM_ID].value = allVals[i].item_id;
                            currentInput[ST_ROW_INDEX_QUANTITY].value = 0;
                            currentInput[ST_ROW_INDEX_PRICE].value = allVals[i].price;
                            currentInput[ST_ROW_INDEX_REMARK].value = allVals[i].item_remark;
                            currentInput[ST_ROW_INDEX_STOCK_QTY].value = allVals[i].stock_qty;
                            currentInput[ST_ROW_INDEX_ITEM_INV_UOM].value = allVals[i].item_inv_measure;
                            currentInput[ST_ROW_INDEX_ITEM_NAME].value = allVals[i].item_name;
                            currentInput[ST_ROW_INDEX_ITEM_ONHAND].value = allVals[i].item_onhand;
                            // currentLabel[ST_LABEL_INDEX_LINE_NUMBER].textContent = currentRow[ST_ROW_INDEX_LINE_NUMBER].value; // Line Number
                            // currentLabel[ST_LABEL_INDEX_ITEM_CODE].textContent = currentRow[ST_ROW_INDEX_ITEM_CODE].value; // Item Code


                            // cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
                        }
                        $(this).attr('data-dismiss', 'modal');
                        $('#items_error').css('display', 'none');
                    }
                }
                    // $.tableReindex();
            }
        });

        // $('#dynamic-table tr.gradeX:last').each(function () {
        //     set_order_item_dates();
        //     var $quantity = $(this).find("input[name*='quantity']");
        //     if ($quantity.length) {
        //         setTimeout(function() { $quantity.select(); }, 300);
        //     }
        // });
    } else {
        currentInput[ST_ROW_INDEX_ITEM_CODE].value = '';
        currentInput[ST_ROW_INDEX_ITEM_ID].value = '';
        currentInput[ST_ROW_INDEX_QUANTITY].value = 0;
        currentInput[ST_ROW_INDEX_PRICE].value = 0;
        currentInput[ST_ROW_INDEX_REMARK].value = '';
        currentInput[ST_ROW_INDEX_STOCK_QTY].value = 0;
        currentInput[ST_ROW_INDEX_ITEM_INV_UOM].value = '';
        currentInput[ST_ROW_INDEX_ITEM_NAME].value = '';
        currentInput[ST_ROW_INDEX_ITEM_ONHAND].value = '';
        currentLabel[1].textContent = '';
    }
});

$('#modal_item_code_select').on('change', function () {
    var item_id = $(this).val();
    var id_price_flag = $('#id_price_flag').val();

    if (item_id != ''){
        $.ajax({
            type: "GET",
            url: '/inventory/item_per_detail/'+item_id,
            dataType: 'JSON',
            success: function(data){
                var data_items = data.data;
                if (data_items.length > 0){
                    for (i in data_items) {
                        var price = 0;
                        if (id_price_flag == '1'){
                            price = data_items[i].item_purchase_price;
                        }else if (id_price_flag == '2'){
                            price = data_items[i].item_stockist_price
                        }else{
                            price = data_items[i].item_sale_price;
                        }
                        $('#modal_item_inv_measure').val(data_items[i].item_inv_measure);
                        $('#modal_item_name').val(data_items[i].item_name);
                        $('#modal_item_onhand').val(data_items[i].item_onhand);
                        $('#modal_quantity').val('0');
                        $('#modal_price').val(price);
                        $('#modal_remarks').val('');
                        $('#modal_amount').val('0');
                        $('#modal_quantity').select();
                        check_valid_modal();
                    }
                }
            }
        });
    } else {
        $('#modal_item_inv_measure').val('');
        $('#modal_item_name').val('');
        $('#modal_item_onhand').val('');
        $('#modal_quantity').val('0');
        $('#modal_price').val('');
        $('#modal_remarks').val('');
        $('#modal_amount').val('0');
        check_valid_modal();
    }
});

$(document).on('click', "[class^=prependrow]", function (event) {
    currentRow = $(this).closest('tr').find('input');
    rowIndex = $(this).closest('tr').find('label:first').text() - 1;
    cloneMore('#dynamic-table tr.gradeX:first', 'formset_item', initialDataRow(), rowIndex);
    disableAutoComplete();
});

$(document).on('click', "[class^=appendrow]", function (event) {
    currentRow = $(this).closest('tr').find('input');
    rowIndex = $(this).closest('tr').find('label:first').text();
    cloneMore('#dynamic-table tr.gradeX:first', 'formset_item', initialDataRow(), rowIndex);
    disableAutoComplete();
});


$('#btnSend').on('click', function (){
    $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {
        highLightMandatory(rowIndex);
    });

    if($('#dynamic-table').find('input.highlight-mandatory').length > 0 ||
        $('#dynamic-table').find('span.highlight-mandatory').length > 0) {
        var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
        pop_info_dialog("Invalid data", msg , "error");
        return false;
    }
})


$(document).on('click', "[class^=removerow]", function (event) {
    var rowIndex = $(this).closest('tr').find('label:first').text() - 1;
    if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
        // $(this).closest('tr').css("background-color", "");
        // $('#items_error').removeAttr('style');
        // $(this).closest('tr').find('input').each(function () {
        //     $(this)[0].value = '';
        // });
        // $(this).closest('tr').find('label').each(function () {
        //     $(this)[0].textContent = '';
        // });
        $('#id_select_formset_item-' + rowIndex + '-item_code').val('').trigger('change');
        fnDisableButton()
    } else {
        fnEnableButton();
        var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
        $('#id_formset_item-TOTAL_FORMS').val(minus);
        $(this).parents("tr").remove();
        updateLineNumber(minus, rowIndex);
    }

    // $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {
    //     $(this).find('td').each(function (colIndex, c) {
    //         $.each(this.childNodes, function (i, elem) {
    //             if (elem.nodeName == 'INPUT' || elem.nodeName == 'LABEL') {
    //                 elem.attributes.name.nodeValue = elem.attributes.name.nodeValue.replace(/\d+/g, rowIndex);
    //                 elem.id = elem.id.replace(/\d+/g, rowIndex);
    //             }
    //         });
    //     });
    // });
});

dyn_tbl_sel_row_id = 0;

$(document).on('click', "[class^=editrow]", function (event) {
    selectedRowId = parseInt($(this).closest('tr').find('label:first').text()) - 1;
    loadOrderItemModal(selectedRowId);
});

// $(document).on('click', "[id^=btnOrderItemCancel]", function (event) {
//     selectedRowId = parseInt($('#modal_line_number').val()) - 1;
//     loadOrderItemModal(selectedRowId);
// });

function check_valid_modal() {
    var is_valid = true;
    if ($('#modal_item_code_select').val() == '') {
        $('#select2-modal_item_code_select-container').addClass('highlight-mandatory');
        is_valid = false;
    } else {
        $('#select2-modal_item_code_select-container').removeClass('highlight-mandatory');
    }

    if (float_format($('#modal_quantity').val()) <= 0) {
        $('#modal_quantity').addClass('highlight-mandatory');
        is_valid = false;
    } else {
        $('#modal_quantity').removeClass('highlight-mandatory');
    }

    if (float_format($('#modal_price').val()) <= 0) {
        $('#modal_price').addClass('highlight-mandatory');
        is_valid = false;
    } else {
        $('#modal_price').removeClass('highlight-mandatory');
    }
    return is_valid;
}
var line_object = {
    'item_code': '',
    'quantity': '',
    'price': '',
    'remark': '',
}
function loadOrderItemModal(selectedRowId, addNew) {
    $('#loading').show();
    dyn_tbl_sel_row_id = selectedRowId;

    $current_row = $('#dynamic-table tr.gradeX').eq(selectedRowId).find('input');
    $labels = $('#dynamic-table tr.gradeX').eq(selectedRowId).find('label');
    $selects = $('#dynamic-table tr.gradeX').eq(selectedRowId).find('select');

    $('#modal_line_number').val($labels[0].textContent);
    $('#modal_item_inv_measure').val($current_row[7].value);
    $('#modal_item_name').val($current_row[8].value);
    $('#modal_item_onhand').val($current_row[9].value);
    $('#modal_quantity').val($current_row[3].value);
    $('#modal_price').val($current_row[4].value);
    $('#modal_remarks').val($current_row[10].value);

    line_object['quantity'] = $current_row[3].value;
    line_object['price'] = $current_row[4].value;
    line_object['remark'] = $current_row[10].value;

    if ($('#modal_item_code_select').data('select2')) {
        $('#modal_item_code_select').select2('destroy');
    }
    $('#modal_item_code_select').empty();

    if ($selects.length > 0) {
        $('#modal_amount').val($labels[1].textContent);
        $('#modal_item_code_select').removeAttr('style');
        $('#modal_item_code').css('display', 'none');
        var item_by_loc_option = $('#item_by_loc').children().clone(true);
        $('#modal_item_code_select').html(item_by_loc_option);

        $('#modal_item_code_select').val($('#id_select_formset_item-' + selectedRowId + '-item_code').val());
        line_object['item_code'] = $('#id_select_formset_item-' + selectedRowId + '-item_code').val();

        $('#modal_item_code_select').select2({
            placeholder: "Select item",
            allowClear: true,
            // dropdownParent: $('#stockItemModal')
        });

        $('#modal_item_code_select').attr('tabindex','0');

        setTimeout(function() {
            if ($("#stockItemModal").is(':visible')) {
                $('#modal_item_code_select').focus();
                $('#modal_item_code_select').select2('open');
            }
            $('#loading').hide();
        }, 500);

        $('#modal_item_code_select').on("select2:close", function() {
            $('#modal_quantity').select();
            $('#modal_quantity').focus();
        });

        $('#modal_item_code_select').on("select2:open", function( event ){
            prefill_select2(event);

            $('.select2-container input.select2-search__field').css({
                'font-size': '12.5px',
            });
        });
    } else {
        $('#modal_amount').val($labels[2].textContent);
        $('#modal_item_code_select').css('display', 'none');
        $('#modal_item_code').removeAttr('style');
        $('#modal_item_code').val($labels[1].textContent);
        $('#modal_quantity').focus();
        $('#loading').hide();
    }
    controlPrevNextBtn();
}

function controlPrevNextBtn() {
    // disable or enable pre button
    if (dyn_tbl_sel_row_id == 0) {
        $('#btnOrderItemPrev').attr('disabled', true);
    } else {
        $('#btnOrderItemPrev').attr('disabled', false);
    }

    // disable or enable next button
    if (dyn_tbl_sel_row_id == (parseInt($('#id_formset_item-TOTAL_FORMS').val()) - 1)) {
        $('#btnOrderItemNext').attr('disabled', true);
    } else {
        $('#btnOrderItemNext').attr('disabled', false);
    }
}

function saveOrderItemModal() {
    var selectedRowId = parseInt($('#modal_line_number').val()) - 1;
    if (!check_valid_modal()) {
        var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
        pop_info_dialog("Invalid data", msg , "error");
        return false;
    }
    var item_code = $('#modal_item_code_select').val();
    var quantity = $('#modal_quantity').val();
    var price = $('#modal_price').val();
    var remark = $('#modal_remarks').val();
    if (item_code != undefined && item_code != '') {
        $('#id_select_formset_item-' + selectedRowId + '-item_code').val(item_code).trigger('change');
        setTimeout(function() {
            $('#id_formset_item-' + selectedRowId + '-price').val(float_format(price, 6));
            $('#id_formset_item-' + selectedRowId + '-remark').val(remark);
            $('#id_formset_item-' + selectedRowId + '-quantity').val(float_format(quantity, 2)).trigger('change');
        }, 500);
    } else {
        $('#id_formset_item-' + selectedRowId + '-price').val(float_format(price, 6));
        $('#id_formset_item-' + selectedRowId + '-remark').val(remark);
        $('#id_formset_item-' + selectedRowId + '-quantity').val(float_format(quantity, 2)).trigger('change');
    }
    return true;
}

// $('#stockItemModal').on('shown.bs.modal', function () {
//     $('#modal_quantity').focus();
// })

// event change quantity
$('#dynamic-table tr.gradeX').each(function () {
    currentRow = $(this).closest('tr').find('input');
    $mainElement = '#' + currentRow[ST_ROW_INDEX_QUANTITY].id;
    var order_type = $('#order_type').text();
    var order_id = $('#order_id').text();
    $($mainElement).on('change', function (e) {
        currentRow = $(this).closest('tr').find('input');
        currentLabel = $(this).closest('tr').find('label');
        var rowIndex = parseInt($(currentLabel[ST_ROW_INDEX_LINE_NUMBER]).text()) - 1;
        var indexOFAmount = ST_LABEL_INDEX_AMOUNT;
        if ($('#select2-id_select_formset_item-' + rowIndex + '-item_code-container').is(':visible')) {
            indexOFAmount = indexOFAmount - 1;
        }

        var out_location_id = $('#id_out_location_id').val();

        var quantity = parseFloat(currentRow[ST_ROW_INDEX_QUANTITY].value).toFixed(2);
        var price = currentRow[ST_ROW_INDEX_PRICE].value;
        var amount = 0;

        currentRow[ST_ROW_INDEX_QUANTITY].value = quantity;

        if (quantity <= 0) {
            // $('#items_error').removeAttr('style');
            // $('#items_error').text('The quantity of product ' + currentRow[ST_ROW_INDEX_ITEM_CODE].value + ' must be be greater than 0');
            var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
            pop_ok_dialog("Invalid data",
                msg,
                function(){
                    $($mainElement).focus();
                    $($mainElement).select();
            });
            // $(this).closest('tr').attr('style', 'background-color: yellow !important');
            currentRow[ST_ROW_INDEX_AMOUNT].value = 0;
            currentLabel[indexOFAmount].textContent = '0.00';
            fnDisableButton();

        } else if (out_location_id != '') {
            if (quantity > parseFloat(currentRow[ST_ROW_INDEX_STOCK_QTY].value)) {
                // $('#items_error').removeAttr('style');
                // $('#items_error').text('The quantity of product ' + currentRow[ST_ROW_INDEX_ITEM_CODE].value + ' must be less than Stock Quantity (' + currentRow[ST_ROW_INDEX_STOCK_QTY].value + ')');
                // $(this).closest('tr').attr('style', 'background-color: yellow !important');
                var msg = 'The quantity of product ' + currentRow[ST_ROW_INDEX_ITEM_CODE].value + ' must be less than Stock Quantity (' + currentRow[ST_ROW_INDEX_STOCK_QTY].value + ')'
                pop_ok_dialog("Invalid data",
                    msg,
                    function(){
                        $($mainElement).focus();
                        $($mainElement).select();
                });
                currentRow[ST_ROW_INDEX_AMOUNT].value = 0;
                currentLabel[indexOFAmount].textContent = '0.00';
                fnDisableButton();
                // $('#dynamic-table tr.gradeX').each(function () {
                //     $(this).closest('tr').find('input').not(currentRow[ST_ROW_INDEX_QUANTITY]).attr('disabled', true);
                // });
            } else {
                amount = quantity * price
                currentRow[ST_ROW_INDEX_AMOUNT].value = parseFloat(amount).toFixed(2);
                currentLabel[indexOFAmount].textContent = int_comma(amount,2);
                $('#dynamic-table tr.gradeX').each(function () {
                });
                $(this).closest('tr').removeAttr('style');
                $('#items_error').css('display', 'none');
                $('#items_error').css('display', 'none');
                fnEnableButton();
            }
        } else {
            amount = quantity * price;
            currentRow[ST_ROW_INDEX_AMOUNT].value = parseFloat(amount).toFixed(2);
            currentLabel[indexOFAmount].textContent = int_comma(amount, 2);
            $('#dynamic-table tr.gradeX').each(function () {
            });
            $(this).closest('tr').removeAttr('style');
            $('#items_error').css('display', 'none');
            $('#items_error').css('display', 'none');
            fnEnableButton();
        }
        //update modal after quantity & amount update
        if ($('#stockItemModal').hasClass('in')) {
            $('#modal_amount').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-amount').text());
            $('#modal_quantity').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-quantity').val());
        }

        let rowCheck = parseInt($(this).closest('tr').find('label:first').text()) - 1;
        highLightMandatory(rowCheck);
    });
    $($mainElement).click(function () {
        $(this).select();
    });
});


// event change price
$('#dynamic-table tr.gradeX').find('input').each(function () {
    currentRow = $(this).closest('tr').find('input');
    $priceElement = '#' + currentRow[ST_ROW_INDEX_PRICE].id;
    $($priceElement).off('change').on('change', function (e) {
        currentRow = $(this).closest('tr').find('input');
        currentLabel = $(this).closest('tr').find('label');
        var rowIndex = parseInt($(currentLabel[ST_ROW_INDEX_LINE_NUMBER]).text()) - 1;
        var indexOFAmount = ST_LABEL_INDEX_AMOUNT;
        if ($('#select2-id_select_formset_item-' + rowIndex + '-item_code-container').is(':visible')) {
            indexOFAmount = indexOFAmount - 1;
        }
        var amount = 0;
        if (currentRow[ST_ROW_INDEX_PRICE].value <= 0) {
            // $('#items_error').removeAttr('style');
            // $('#items_error').text('The price of product ' + currentRow[ST_ROW_INDEX_ITEM_CODE].value + ' must be be greater than 0');
            // $(this).closest('tr').attr('style', 'background-color: yellow !important');
            var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
            pop_ok_dialog("Invalid data",
                msg,
                function(){
                    $($priceElement).focus();
                    $($priceElement).select();
            });
            currentRow[ST_ROW_INDEX_AMOUNT].value = 0;
            currentLabel[indexOFAmount].textContent = '0.00';
            fnDisableButton();
            // $('#dynamic-table tr.gradeX').each(function () {
            //     $(this).closest('tr').find('input').not(currentRow[ST_ROW_INDEX_PRICE]).attr('disabled', true);
            // });
        } else {
            amount = currentRow[ST_ROW_INDEX_QUANTITY].value * currentRow[ST_ROW_INDEX_PRICE].value;
            currentRow[ST_ROW_INDEX_AMOUNT].value = parseFloat(amount).toFixed(2);
            currentLabel[indexOFAmount].textContent = int_comma(amount, 2);
            $('#dynamic-table tr.gradeX').each(function () {

            });
            $(this).closest('tr').removeAttr('style');
            $('#items_error').css('display', 'none');
            $('#items_error').css('display', 'none');
            fnEnableButton();
        }

        let rowCheck = parseInt($(this).closest('tr').find('label:first').text()) - 1;
        highLightMandatory(rowCheck);
    });
    $($priceElement).click(function () {
        $(this).select();
    });
});


function search_location_code(flag, in_location_code, out_location_code) {
    if (in_location_code != out_location_code) {
        $.ajax({
            method: "POST",
            url: url_search_location_code,
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'flag': flag,
                'in_location_code': in_location_code,
                'out_location_code': out_location_code
            },
            responseTime: 200,
            response: function (settings) {
                if (settings.data.value) {
                    this.responseText = '{"success": true}';
                }
                else {
                    this.responseTime = '{"success: false, "msg": "required"}';
                }
            },
            success: function (json) {
                if (json['msg'] != null) {
                    pop_info_dialog("Error", json['msg'], "error");
                } else {
                    if (jQuery.isEmptyObject(json) == false) {
                        if (json['flag'] == 'id_in_location') {
                            $('#id_in_location').val(json['id']);

                        } else if (json['flag'] == 'id_out_location') {
                            $('#id_out_location').val(json['id']);

                        } else {
                            $('#id_in_location').prop('readonly', true);
                            $('#id_out_location').prop('readonly', true);
                        }
                        $('#btnOpenItemDialog').removeAttr('disabled');
                        fnEnableButton();
                    } else {
                        $('#btnOpenItemDialog').attr('disabled', true);
                        fnDisableButton();
                        $('#id_in_location').val('');
                        $('#id_out_location').val('');
                        $('#id_in_location').prop('readonly', true);
                        $('#id_out_location').prop('readonly', true);
                    }
                }
            }
        });
    } else {
        pop_info_dialog("Error", "In Location must not be the same as Out Location !", "error");
        $('#btnOpenItemDialog').attr('disabled', true);
        fnDisableButton();
    }
}

// $('#id_in_location').keypress(function (e) {
//     if (e.which == 13) {
//         e.preventDefault();
//         var out_location_code = $('#id_out_location').val();
//         search_location_code(this.id, this.value, out_location_code);
//     }
// });


// $('#id_out_location').keypress(function (e) {
//     if (e.which == 13) {
//         e.preventDefault();
//         var in_location_code = $('#id_in_location').val();
//         search_location_code(this.id, in_location_code, this.value);
//     }
// });


function load_items(){
    if ($('#id_transaction_code').val() == '') {
        return false;
    }
    var in_location_id = $('#id_in_location').val();
    var out_location_id = $('#id_out_location').val();
    $('#loading').show();
    $('#item_by_loc').empty();
    if (in_location_id > 0 || out_location_id > 0) {
        $.ajax({
            type: "GET",
            url: url_item_by_loc,
            data:{
                "in_location_id": in_location_id,
                "out_location_id": out_location_id
            },
            dataType: 'JSON',
            success: function(data){
                if (data.data.length > 0){
                    var array = data.data;
                    $("#item_by_loc").append('<option value="">Select item</option>');
                    for (i in array) {
                         $("#item_by_loc").append('<option value='+array[i].item_id+'>'+array[i].item_code+'</option>');
                       }

                    ALL_VALUES = initialDataRow();
                    if (stock_trans_id == '') {
                        cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', initialDataRow(), 0);
                        disableAutoComplete();
                    }
                }
                $('#loading').hide();
            }
        });
    } else {
        $('#loading').hide();
    }
};

function is_change() {
    var flag_change = false;
    if (line_object['item_code'] != $('#modal_item_code_select').val() && $('#modal_item_code_select').val() != null) {
        flag_change = true;
    }
    if (line_object['quantity'] != $('#modal_quantity').val()) {
        flag_change = true;
    }
    if (line_object['price'] != $('#modal_price').val()) {
        flag_change = true;
    }
    if (line_object['remark'] != $('#modal_remarks').val()) {
        flag_change = true;
    }
   return flag_change;
}

function newItemModal() {
    var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
    $('#dynamic-table tr.gradeX').eq(rowCount-1).find('.appendrow').trigger('click');
    setTimeout(() => {
        loadOrderItemModal(rowCount);
    }, 200);
}

function amountCalculation(){
    var quantity = float_format($('#modal_quantity').val());
    var price = parseFloat($('#modal_price').val());
    var amount = quantity * price;
    $('#modal_quantity').val(comma_format(quantity, 2));
    $('#modal_price').val(comma_format(price, 6));
    $('#modal_amount').val(comma_format(amount, 6));
}


$('#item_by_loc').on('change', function () {
    var item_id = $('#item_by_loc').val();
    var id_price_flag = $('#id_price_flag').val();
    if (item_id != '0'){
        $.ajax({
            type: "GET",
            url: '/inventory/item_per_detail/'+item_id,
            dataType: 'JSON',
            success: function(data){
            var data_items = data.data;
            if (data_items.length > 0){
                for (i in data_items) { 
                    var allVals = [];
                    var price = 0;
                    if (id_price_flag == '1'){
                        price = data_items[i].item_purchase_price;
                    }else if (id_price_flag == '2'){
                        price = data_items[i].item_stockist_price
                    }else{
                        price = data_items[i].item_sale_price;
                    }
                    allVals.push({
                        item_id: data_items[i].item_id, //Item ID
                        item_code: data_items[i].item_code,
                        stock_qty: data_items[i].stock_qty,
                        price:price,
                        item_remark: data_items[i].item_remark,
                        item_name: data_items[i].item_name,
                        item_inv_measure: data_items[i].item_inv_measure,
                        item_onhand: data_items[i].item_onhand,
                        location_code: data_items[i].location_code
                    });
                    if (allVals.length > 0) {
                        ALL_VALUES = allVals;
                        cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
                        disableAutoComplete();
                    }
                    $(this).attr('data-dismiss', 'modal');
                    $('#items_error').css('display', 'none');
                    }
                }
                $.tableReindex();
            }
        });

        $('#dynamic-table tr.gradeX:last').each(function () {
            set_order_item_dates();
            var $quantity = $(this).find("input[name*='quantity']");
            if ($quantity.length) {
                setTimeout(function() { $quantity.select(); }, 300);
            }
        });
    }
});

$('#item_by_loc').on("select2:close", function() {
    $('#item_by_loc').focus();
});

$.tableReindex = function (selector) {
    if (selector === undefined) selector = '#dynamic-table';

    if ($(selector + ' tr.gradeX').length === 0) return;

    $(selector + ' tr.gradeX').each(function () {
        rowIndex = $(this).index();

        $(this).attr('data-row-index', rowIndex);

        $(this).find('td').each(function () {
            if ($(this).index() == ST_COL_BUTTONS) { // Col Add/Remove buttons
                var $btnAdd = $(this).find('button.addrow'), $btnEdit = $(this).find('button.editrow'), $btnRemove = $(this).find('button.removerow');

                $btnAdd.attr('id', 'addrow' + rowIndex);
                $btnAdd.attr('name', 'addrow' + rowIndex);

                $btnEdit.attr('id', 'editrow' + rowIndex);
                $btnEdit.attr('name', 'editrow' + rowIndex);

                $btnRemove.attr('id', 'removerow' + rowIndex);
                $btnRemove.attr('name', 'removerow' + rowIndex);
            }
            else if ($(this).index() == ST_COL_LINE_NUMBER) { // Col No
                var $label = $(this).find('label');

                $label.attr('id', 'id_formset_item-' + rowIndex + '-line_number');
                $label.attr('name', 'formset_item-' + rowIndex + '-line_number');
                $label.html(rowIndex + 1);

                var $input = $(this).find('input[type="text"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-line_number');
                $input.attr('name', 'formset_item-' + rowIndex + '-line_number');
            }
            else if ($(this).index() == ST_COL_ITEM_NAME) { // Col No
                var $label = $(this).find('label');

                $label.attr('id', 'id_formset_item-' + rowIndex + '-item_code');
                $label.attr('name', 'formset_item-' + rowIndex + '-item_code');
            }
            else if ($(this).index() == ST_COL_QTY) { // Col Quantity
                var $input = $(this).find('input[type="number"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-quantity');
                $input.attr('name', 'formset_item-' + rowIndex + '-quantity');
            }
            else if ($(this).index() == ST_COL_PRICE) { // Col Price
                var $input = $(this).find('input[type="number"]');
                
                $input.attr('id', 'id_formset_item-' + rowIndex + '-price');
                $input.attr('name', 'formset_item-' + rowIndex + '-price');
            }
            else if ($(this).index() == ST_COL_AMOUNT) { // Col Amount
                var $label = $(this).find('label');
                var $input = $(this).find('input[type="text"]');

                $label.attr('id', 'id_formset_item-' + rowIndex + '-amount');
                $label.attr('name', 'formset_item-' + rowIndex + '-amount');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-amount');
                $input.attr('name', 'formset_item-' + rowIndex + '-amount');
            }
            else if ($(this).index() == ST_COL_INV_MESMNT) { // Col Inventory measurement
                var $input = $(this).find('input[type="text"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-item_inv_measure');
                $input.attr('name', 'formset_item-' + rowIndex + '-item_inv_measure');
            }
            else if ($(this).index() == ST_COL_ITEM_DESC) { // Col Item Name
                var $input = $(this).find('input[type="text"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-item_name');
                $input.attr('name', 'formset_item-' + rowIndex + '-item_name');
            }
            else if ($(this).index() == ST_COL_ONH_QTY) { // Col On hand Qty
                var $input = $(this).find('input[type="text"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-item_onhand');
                $input.attr('name', 'formset_item-' + rowIndex + '-item_onhand');
            }
            else if ($(this).index() == ST_COL_REMARK) { // Col Remark
                var $input = $(this).find('input[type="text"]');

                $input.attr('id', 'id_formset_item-' + rowIndex + '-description');
                $input.attr('name', 'formset_item-' + rowIndex + '-description');
            }
        });
    });
}


$.checkOrderRowValidity = function(row_number, selector) {
    if (row_number === undefined) {
        return false;
    }

    if (selector === undefined) {
        selector = '#dynamic-table';
    }

    row = $(selector+' tr.gradeX')[row_number];

    valid = ($(row).length != 0);

    if (!valid) {
        return false;
    }

    $inputs = $(row).find('input');
    $selects = $(row).find('select');

    // Check each field is empty
    if ($inputs[ST_ROW_INDEX_QUANTITY].value === '') {
        console.log('Error, quantity empty');
        valid = false;
    }

    return valid;
}


$(document).on('click', "[id^=btnOrderItemCancel]", function (event) {
    if (is_change()) {
        $.confirm({
            title: 'Confirm!',
            content: 'Do you want to save?',

            buttons: {
                Yes: {
                    btnClass: 'btn-success, Yes',
                    action: function(){
                        saveOrderItemModal();
                    }
                },
                No: {
                    btnClass: 'btn-success, No',
                    action: function(){
                        $('#stockItemModal').modal('hide');
                    }
                },
            },
            onOpen: function() {
                $('.Yes').focus();
                document.addEventListener("keydown", function(e){
                    if(e.which == 37){
                      $('.Yes').focus();
                    }
                    if(e.which == 39){
                     $('.No').focus();
                    }
                 });
            }
        });
    } else {
        $('#stockItemModal').modal('hide');
    }
});

$('#modal_price').click(function () {
    $(this).select();
});

$('#modal_quantity').click(function () {
    $(this).select();
});

$('#modal_remarks').click(function () {
    $(this).select();
});

$('#modal_price').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#modal_remarks').select();
        return false;
    }
});

$('#modal_remarks').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#btnOrderItemSave').focus();
        return false;
    }
});

$('#btnOrderItemNew').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#btnOrderItemNew').trigger('click');
    }
});

$('#btnOrderItemSave').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#btnOrderItemSave').trigger('click');
    }
});

$('#btnOrderItemDelete').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#btnOrderItemDelete').trigger('click');
    }
});

$('#btnOrderItemCancel').bind('keydown', function (event) {
    if (event.which == 13) {
        $('#btnOrderItemCancel').trigger('click');
    }
});

$(document).on('click', "[id^=btnOrderItemDelete]", function (event) {
    selectedRowId = parseInt($('#modal_line_number').val()) - 1;
    $.confirm({
        title: 'Confirm!',
        content: 'Do you want to delete?',

        buttons: {
            Yes: {
                btnClass: 'btn-success, Yes',
                action: function(){
                    if (selectedRowId > 0) {
                        $('#dynamic-table tr.gradeX').eq(selectedRowId).find('.removerow').trigger('click');
                    } else {
                        $('#dynamic-table tr.gradeX').eq(0).find('.removerow').trigger('click');
                    }
                    setTimeout(() => {
                        if (selectedRowId > 0) {
                            loadOrderItemModal(selectedRowId - 1);
                        } else {
                            loadOrderItemModal(0);
                        }
                    }, 500);
                }
            },
            No: {
                btnClass: 'btn-success, No',
                action: function(){}
            },
        },
        onOpen: function() {
            $('.Yes').focus();
            document.addEventListener("keydown", function(e){
                if(e.which == 37){
                  $('.Yes').focus();
                }
                if(e.which == 39){
                 $('.No').focus();
                }
             });
        }
    });
});

$(document).on('click', "[id^=btnOrderItemPrev]", function (event) {
    selectedRowId = parseInt($('#modal_line_number').val()) - 2;
    if (selectedRowId >= 0) {
        // saveOrderItemModal(selectedRowId + 1);
        loadOrderItemModal(selectedRowId);
    }
});

$(document).on('click', "[id^=btnOrderItemNext]", function (event) {
    selectedRowId = parseInt($('#modal_line_number').val());
    loadOrderItemModal(selectedRowId);
});

$(document).on('click', "[id^=btnOrderItemNew]", function (event) {
    // selectedRowId = parseInt($('#modal_line_number').val());
    // saveOrderItemModal(selectedRowId - 1);
    // loadOrderItemModal(selectedRowId);
    if (is_change()) {
        $.confirm({
            title: 'Confirm!',
            content: 'Do you want to save?',

            buttons: {
                Yes: {
                    btnClass: 'btn-success, Yes',
                    action: function(){
                        saveOrderItemModal();
                    }
                },
                No: {
                    btnClass: 'btn-success, No',
                    action: function(){
                        newItemModal()
                    }
                },
            },
            onOpen: function() {
                $('.Yes').focus();
                document.addEventListener("keydown", function(e){
                    if(e.which == 37){
                      $('.Yes').focus();
                    }
                    if(e.which == 39){
                     $('.No').focus();
                    }
                 });
            }
        });
    } else {
        newItemModal()
    }
});

$(document).on('click', "[id^=btnOrderItemSave]", function (event) {
    if(saveOrderItemModal()) {
        newItemModal();
    }
});

$(document).on('change', "[id^=modal_quantity]", function (event) {
    var quantity = float_format($(this).val());
    check_valid_modal();
    if (quantity <= 0) {
        var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
        pop_ok_dialog("Invalid data",
            msg,
            function(){
                $('#modal_quantity').focus();
                $('#modal_quantity').select();
        });
    } else {
        amountCalculation();
    }
});

$(document).on('change', "[id^=modal_price]", function (event) {
    var quantity = float_format($(this).val());
    check_valid_modal();
    if (quantity <= 0) {
        var msg = 'Please fill up the required fields.' + '<br>' + 'Quantity and unit price must be be greater than 0'
        pop_ok_dialog("Invalid data",
            msg,
            function(){
                $('#modal_price').focus();
                $('#modal_price').select();
        });
    } else {
        amountCalculation();
    }
});

// ------ select table popup
$('#tblTransCode tbody').on( 'click', 'tr', function () {
    $($(this).find('input')[0]).prop("checked", true);
    $('#tblTransCode>tbody>tr.table-selected').removeClass('table-selected');
    $(this).addClass('table-selected');
});

$('#tblLocation tbody').on( 'click', 'tr', function () {
    $($(this).find('input')[0]).prop("checked", true);
    $('#tblLocation>tbody>tr.table-selected').removeClass('table-selected');
    $(this).addClass('table-selected');
});

