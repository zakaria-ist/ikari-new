//// start to make function for copy refer number

function saveCopyRefNumber(line, refer_number, refer_line, action, dataList, line_list) {
    if (refer_line == null || refer_line == undefined) {
        refer_line = '';
    }
    let temp_list = [];
    let is_new = true;
    for(i in dataList) {
        let temp_object = dataList[i];
        if (temp_object.line == line && action == 'add') {
            temp_object.ref_line = refer_line;
            temp_list.push(temp_object);
            is_new = false;
        } else if (temp_object.line == line && action == 'remove') {
            is_new = false;
        } else {
            temp_list.push(temp_object);
        }
    }

    if (is_new) {
        let ref_line_list = []
        for(i in line_list) {
            ref_line_list.push(line_list[i].refer_line);
        }
        temp_list.push({
            'line': line,
            'ref_number': refer_number,
            'ref_line': refer_line.toString(),
            'ref_line_list': ref_line_list,
        });
    }
    return  temp_list;
}

function getRefNumber(refer_number, dataList) {
    let return_ref_number = '';
    let data_list = dataList.filter(function (el) {
        return el.ref_number == refer_number;
    });

    let temp_list = []
    for (i in data_list) {
        if (temp_list.indexOf(data_list[i].ref_line) < 0) {
          temp_list.push(data_list[i].ref_line);
        }
    }

    if (data_list.length > 0) {
        let ref_line_list = data_list[0].ref_line_list;
        if (temp_list.length < ref_line_list.length && ref_line_list.length > 0) {
            return_ref_number = data_list[0].ref_number;
        }
    }
    return return_ref_number;
}

function changeIndexData(from_index, action, dataList) {
    let temp_list = []
    for (i in dataList) {
        let temp = dataList[i];
        if (parseInt(temp.line) > from_index) {
            if (action == 'minus') {
                temp.line = (parseInt(temp.line) - 1).toString();
            }
            if (action == 'plus') {
                 temp.line = (parseInt(temp.line) + 1).toString();
            }
        }
        temp_list.push(temp);
    }
    return temp_list;
}

function saveCopyRefNumberDO(line, refer_number, refer_line, action, dataList, line_list) {
    if (refer_line == null || refer_line == undefined) {
        refer_line = '';
    }
    let temp_list = [];
    let is_new = true;
    for(i in dataList) {
        let temp_object = dataList[i];
        if (temp_object.line == line && action == 'add') {
            temp_object.ref_line = refer_line;
            temp_object.ref_number = refer_number;
            for(y in line_list) {
                if (line_list[y].refer_line == refer_line) {
                    let quantity = 0;
                    if (line_list[y].location_item_quantity != undefined) {
                        let outstdg_qty = line_list[y].order_quantity - line_list[y].delivery_quantity;
                        let location_qty = line_list[y].location_item_quantity;
                        if (line_list[y].location_id){
                            quantity = (outstdg_qty > location_qty) ? location_qty : outstdg_qty;
                        } else {
                            quantity = outstdg_qty;
                        }
                        if (quantity < 0) {quantity = 0;}
                    } else {
                        quantity = line_list[y].outstanding_qty;
                    }

                    // if (line_list[y].order_quantity != undefined) {
                    //     // for DO
                    //     temp_object.original_item_quantity = line_list[y].order_quantity;
                    // } else {
                    //     // for GR
                    //     temp_object.original_item_quantity = line_list[y].quantity;
                    // }
                    temp_object.original_item_quantity = quantity;
                    temp_object.location_item_quantity = quantity;
                }
            }
            temp_list.push(temp_object)
            is_new = false;
        } else if (temp_object.line == line && action == 'remove') {
            is_new = false;
        } else {
            temp_list.push(temp_object);
        }
    }

    if (is_new && line_list.length > 0) {
        let ref_line_list = []
        for(i in line_list) {
            ref_line_list.push(line_list[i].refer_line);
        }
        temp_list.push({
            'line': line,
            'ref_number': refer_number,
            'original_item_quantity': 0,
            'location_item_quantity': 0,
            'ref_line': refer_line.toString(),
            'ref_line_list': ref_line_list,
        });
    }
    return  temp_list;
}

function updateQuantityCopyRefNumberDO(line, refer_number, refer_line, dataList, quantity, max_qty=0) {
    let temp_list = [];
    for(xy in dataList) {
        let temp_object = dataList[xy];
        if (temp_object.line == line &&
            temp_object.ref_number == refer_number &&
            temp_object.ref_line == refer_line) {
                if(max_qty > 0) {
                    temp_object.original_item_quantity = float_format(max_qty);
                }
            temp_object.location_item_quantity = float_format(quantity);
        }
        temp_list.push(temp_object);
    }
    return  temp_list;
}

function getRefNumberDO(refer_number, dataList, line_list) {
    let return_ref_number = refer_number;
    let data_list = dataList.filter(function (el) {
        return el.ref_number == refer_number;
    });

    let temp_list = [];
    let original_item_quantity = 0;
    let temp_total_quantity = 0;
    for (i in data_list) {
        if (temp_list.indexOf(data_list[i].ref_line) < 0) {
          temp_list.push(data_list[i].ref_line);
          original_item_quantity = original_item_quantity + float_format(data_list[i].original_item_quantity);
        }
        temp_total_quantity = temp_total_quantity + float_format(data_list[i].location_item_quantity);
    }

    if (data_list.length > 0) {
        let ref_line_list = data_list[0].ref_line_list;
        if (temp_list.length < ref_line_list.length && ref_line_list.length > 0) {
            return_ref_number = data_list[0].ref_number;
        } else if (original_item_quantity  > temp_total_quantity) {
            return_ref_number = data_list[0].ref_number;
        }
    }

    return return_ref_number;
}

function getRemainQuantityDO(refer_number, refer_line, dataList, line_list) {

    let remainQuantity;

    if (refer_number == '' || refer_line == '' || refer_line == undefined) {
        return remainQuantity;
    }

    let data_list = dataList.filter(function (el) {
        return el.ref_number == refer_number;
    });

    let temp_total_quantity = 0;
    let original_item_quantity = 0;
    for (i in data_list) {
        if (data_list[i].ref_line == refer_line) {
            temp_total_quantity = temp_total_quantity + float_format(data_list[i].location_item_quantity)
            original_item_quantity = float_format(data_list[i].original_item_quantity)
        }
    }

    if (data_list.length > 0) {
        if (original_item_quantity > temp_total_quantity) {
            remainQuantity = original_item_quantity - temp_total_quantity;
        } else if (original_item_quantity && original_item_quantity == temp_total_quantity) {
            remainQuantity = 0;
        }
    }

    return remainQuantity;
}

function getTotalMaxInputQuantityDO(refer_number, refer_line, dataList, rowIndex) {

    let temp_total_quantity = 0;

    if (refer_number == '' || refer_line == '' || refer_line == undefined) {
        return temp_total_quantity
    }

    let data_list = dataList.filter(function (el) {
        return el.ref_number == refer_number && el.ref_line == refer_line && el.line != rowIndex;
    });

    for (i in data_list) {
        temp_total_quantity = temp_total_quantity + float_format(data_list[i].location_item_quantity)
    }

    if (data_list.length > 0) {
        temp_total_quantity = float_format(data_list[0].original_item_quantity) - temp_total_quantity;

        if (temp_total_quantity < 0) {
            temp_total_quantity = 0;
        }
    } else {
        // case edit
        temp_total_quantity = -1
    }


    return temp_total_quantity;
}

//// end to make function for copy refer number

function referNumberSelect2(id, refer_numbers, exclude_list=[]) {
    // initial data for refer number
    let new_refer_numbers = refer_numbers.filter(function (el) {
        if (exclude_list.indexOf(el.refer_number) === -1) {
            return el;
        }
    });
    // let new_refer_numbers = refer_numbers;
    if ($('#' + id).data('select2')) {
        $('#' + id).select2('destroy');
    }

    $('#' + id).empty();

    var options = '<option value="">Select Ref Number</option>';
    for (i in new_refer_numbers) {
        options += "<option data-code_data="+new_refer_numbers[i].order_id+" value="+new_refer_numbers[i].refer_number+">"+new_refer_numbers[i].refer_number+"</option>";
    }
    $('#' + id).html(options);

    $('#' + id).select2({
        placeholder: "Select Ref Number",
        allowClear: true,
    });

    $('#' + id).on("select2:open", function( event ){
        prefill_select2(event);
    });
    setTimeout(function() {
        $($('#' + id).parent('td').find('span')[0]).removeAttr("style");
        $($('#' + id).parent('td').find('span')[0]).attr('style', 'width: 160px !important');
    }, 200);
}

function partNumberSelect2(id, item_info, param_options) {
    // initial data for part number
    if ($('#' + id).data('select2')) {
        $('#' + id).select2('destroy');
    }

    $('#' + id).empty();

    var options = '<option value="">Select Part No.</option>';
    if (item_info.length > 0) {
        $.each(item_info, function(i, v) {
            options += "<option data-code_data='["+JSON.stringify(v)+"]' value='"+v.identity+"'>"+v.code+"</option>";
        });
    } else {
        options = param_options;
    }

    $('#' + id).append(options);

    $('#' + id).select2({
        placeholder: 'Select Part No.',
        // data: [{id:currentRow[PO_ROW_INDEX_ITEM_ID].value, text:currentRow[PO_ROW_INDEX_CODE].value}]
    });

    $('#' + id).on("select2:open", function( event ){
        prefill_select2(event);
    });
}

function referLineSelect2(id, allVals, refer_param, from) {
    // initial data for refer line
    if ($('#' + id).data('select2')) {
        $('#' + id).select2('destroy');
    }

    $('#' + id).empty();

    var options = '<option value="">Ref Ln</option>';

    for (i in allVals) {
        if(allVals[i].ref_id == refer_param && from == 'PO') {
            options += "<option data-code_data="+allVals[i].refer_line+" value="+allVals[i].refer_line+">"+allVals[i].refer_line+"</option>";
        }

        if(allVals[i].ref_id == refer_param && from == 'DO' && allVals[i].show) {
            options += "<option data-code_data="+allVals[i].refer_line+" value="+allVals[i].refer_line+">"+allVals[i].refer_line+"</option>";
        }

        if(allVals[i].refer_number == refer_param && from == 'GR' && allVals[i].show) {
            options += "<option data-code_data="+allVals[i].refer_line+" value="+allVals[i].refer_line+">"+allVals[i].refer_line+"</option>";
        }
    }

    $('#' + id).html(options);

    $('#' + id).select2({
        placeholder: "Ref Ln"
    });

    $('#' + id).on("select2:open", function( event ){
        prefill_select2(event);
    });

    //$('#' + id).val('').trigger('change');
}

function locationSelect2(id, location_data) {
    // initial data for location
    $('#' + id).empty();
    var options = '';
    for (i in location_data) {
        options += "<option value="+location_data[i].location_id+">"+location_data[i].location_code+"</option>";
    }
    $('#' + id).append(options);
    $('#' + id).select2();
    if (location_data.length > 0) {
        $('#' + id).val(location_data[0].location_id).trigger('change');
    }
}

function checkMaxInputForInt(maxVal, elementId) {
    if (parseInt($('#' + elementId).val()) > maxVal) {
        pop_ok_dialog("Wrong input",
            'Input is wrong',
            function(){
                $('#' + elementId).focus();
            }
        );
        $('#' + elementId).val('0');

    } else {
        $('#' + elementId).val(float_format($('#' + elementId).val()).toFixed(2));
    }
}

function SortByReferNumber(a, b){
  var aName = a.refer_doc.toLowerCase();
  var bName = b.refer_doc.toLowerCase();
  return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
}

function SortBypartNo(a, b){
  var aName = a.part_no.toLowerCase();
  var bName = b.part_no.toLowerCase();
  return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
}

function show_duplicate_part_modal(duplicate_data_list, target, next_target, has_location=false) {
    $('#duplicateSoItemList').DataTable().destroy();
    if (has_location) {
        warning_table = $('#duplicateSoItemList').DataTable({
            data: duplicate_data_list,
            "paging": false,
            "info": false,
            "filter": false,
            "columnDefs": [
                { targets: '_all', 'orderable': false},
                
            ], order: []
        });
    } else {
        warning_table = $('#duplicateSoItemList').DataTable({
            data: duplicate_data_list,
            "paging": false,
            "info": false,
            "filter": false,
            "columnDefs": [
                { targets: [5], visible: false},
                { targets: '_all', 'orderable': false}
            ], order: []
        });
    }
    eventButtonDuplicatePartYesNo(warning_table, target, next_target);
    $('#duplicateSoItemModal').modal('show');
}

function eventButtonDuplicatePartYesNo(warning_table, target, next_target) {
    $('#duplicate_yes_id').on('click', function (e) {
        // $('#msg_id').html('');
        setTimeout(function() {
            $(next_target).focus();
        }, 300);
    });

    $('#duplicate_no_id').on('click', function (e) {
        // $('#msg_id').html('');
        setTimeout(function() {
            $(target).focus();
            $(target).val('').trigger('change');
        }, 300);
    });
}

function show_duplicate_cuspo_modal(duplicate_data_list, target, has_location=false, is_cust_no_duplicate=false) {
    if (!is_cust_no_duplicate) {
        $('#footer-duplicate_po').show();
        $('#footer-duplicate_ok').hide();
        $('#dupl_msg_id').html('<span>Duplicate entry found, do you want to proceed?</span>');
    } else {
        $('#footer-duplicate_po').show();
        $('#footer-duplicate_ok').hide();
        $('#dupl_msg_id').html('<span>Duplicate customer PO found, Do you want to proceed?</span>');
    }
    $('#duplicateSoItemList').DataTable().destroy();
    if (has_location) {
        warning_table = $('#duplicateSoItemList').DataTable({
            data: duplicate_data_list,
            "paging": false,
            "info": false,
            "filter": false,
            "destroy": true,
            "scrollY": 350,
            // "scrollX": true,
            "columnDefs": [
                { targets: '_all', 'orderable': false},
                
            ], order: []
        });
    } else {
        warning_table = $('#duplicateSoItemList').DataTable({
            data: duplicate_data_list,
            "paging": false,
            "info": false,
            "filter": false,
            "destroy": true,
            "scrollY": 350,
            // "scrollX": true,
            "columnDefs": [
                { targets: [5], visible: false},
                { targets: '_all', 'orderable': false}
            ], order: []
        });
    }
    setTimeout(() => {
        $('#duplicateSoItemList').DataTable().columns.adjust();
    }, 300);
    eventButtonDuplicateYesNo(warning_table, target);
    $('#duplicateSoItemModal').modal('show');
    $("#duplicateSoItemModal").on('shown.bs.modal', function(event) {
        try{
            $('#duplicate_yes_id').focus();
        } catch(e) {
            console.log(e);
            $('#duplicate_so_ok_id').focus();
        }
        try {
            document.addEventListener("keydown", function(e){
                if(e.which == 37){
                    $('#duplicate_yes_id').focus();
                }
                if(e.which == 39){
                    $('#duplicate_no_id').focus();
                }
            });
        } catch(e) {
            
        }
    });
}

function eventButtonDuplicateYesNo(warning_table, target) {
    $('#duplicate_yes_id').on('click', function (e) {
        setTimeout(function() {
            if(target != '') {
                $(target).parent().next().find('input')[0].focus();
            }
        }, 300);
    });

    $('#duplicate_no_id').on('click', function (e) {
        setTimeout(function() {
            if(target != '') {
                $(target).focus();
                $(target).val('').trigger('change');
            } else {
                // $('[id*="-customer_po_no"]').val('').trigger('change');
            }
        }, 300);
    });
    $('#duplicate_so_ok_id').off('click').on('click', function (e) {
        setTimeout(function() {
            if(target != '') {
                $(target).focus();
                $(target).val('').trigger('change');
                $(target).addClass('highlight-mandatory');
            }
        }, 300);
    });
}

function show_invalid_modal(invalid_data_list, invalid_message_list, disableShowDuplicate, enableShowDuplicate, th_object) {
    if (invalid_data_list.length > 0) {
        var msg = ''
        $.grep(invalid_message_list, function(v) {
            msg = msg + v;
        });

        $('#msg_id').html(msg);

        if (invalid_message_list.length > 0) {
            $('#modal-title').html('Invalid Information');
             $('#footer-invalid').removeClass('hide');
            $('#footer-duplicate').addClass('hide');
        } else {
            $('#modal-title').html('Similar Records Found');
            $('#footer-invalid').addClass('hide');
            $('#footer-duplicate').removeClass('hide');
        }

        var dataWarning = [];
        var less_col = false;
        $.grep(invalid_data_list, function(v) {
            if (v.part_no == undefined) {
                var new_data = [v.ln, v.refer_doc, v.refer_line, v.quantity, ''];
                less_col = true;
            } else {
                var new_data = [v.ln, v.part_no, v.quantity, v.unitPrice, v.custPO];
            }

            dataWarning.push(new_data);

        });

        $('#th-0').text(th_object["th-0"]);
        $('#th-1').text(th_object["th-1"]);
        $('#th-2').text(th_object["th-2"]);
        $('#th-3').text(th_object["th-3"]);
        $('#th-4').text(th_object["th-4"]);

        if (less_col) {
            warning_table = $('#invalid-so-list').DataTable({
                data: dataWarning,
                "paging": false,
                "info": false,
                "filter": false,
                "destroy": true,
                "columnDefs": [
                    { targets: [4], visible: false},
                    { targets: '_all', 'orderable': false},
                ], order: []
            });
        } else {
            warning_table = $('#invalid-so-list').DataTable({
                data: dataWarning,
                "paging": false,
                "info": false,
                "filter": false,
                "destroy": true,
                "columnDefs": [
                    { targets: '_all', 'orderable': false},
                ], order: []
            });
        }
        eventButtonInvalidOk(warning_table, disableShowDuplicate, enableShowDuplicate);
        $('#invalidSoModal').modal('show');
    }

}

function eventButtonInvalidOk(warning_table, fixForm) {
    $('#invalid_ok_id').on('click', function (e) {
        warning_table.clear();
        warning_table.destroy();
        $('#msg_id').html('');
    });

    $('#duplicate_cancel_id').on('click', function (e) {
        warning_table.clear();
        warning_table.destroy();
        $('#msg_id').html('');
        enableShowDuplicate();
    });

    $('#duplicate_ok_id').on('click', function (e) {
        warning_table.clear();
        warning_table.destroy();
        $('#msg_id').html('');
        disableShowDuplicate();
        $('#form').submit();
    });
}

function check_quantity_reference(refer_line, order_id, order_type, element_id, quantity_original) {
    if (order_id &&
        refer_line &&
        order_type && float_format($('#' + element_id).val()) < quantity_original) {
        $.ajax({
            method: "GET",
            url: '/orders/check_quantity_po_so_reference/' + order_id + '/' + order_type + '/' + refer_line + '/',
            dataType: 'JSON',
            success: function (json) {
                var reference_exists = json.reference_exists;
                var total_quantity = json.total_quantity;
                if(reference_exists
                    && float_format(total_quantity) > 0
                    && float_format(total_quantity) > float_format($('#' + element_id).val()) ) {

                    let dataWarning = []
                    $.grep(json.order_items, function(v) {
                        var new_data = [v.document_number, v.line_number, v.quantity];
                        dataWarning.push(new_data);

                    });

                    $('#msg_id_1').html('It is linked with other entry as below.');
                    $('#msg_id_2').html('Please input the value which is greater or equal to ' + total_quantity+ '.');

                    var warning_table = $('#warning-list').DataTable({
                        data: dataWarning,
                        "paging": false,
                        "info": false,
                        "filter": false,
                        "destroy": true,
                        "columnDefs": [
                            {
                                "targets": 0,
                                "orderable": false,
                            },
                            {
                                "targets": 1,
                                "orderable": false,
                            },
                            {
                                "targets": 2,
                                "orderable": false,
                            }
                        ], order: []
                    });
                    eventButtonWarningOk(element_id, quantity_original, warning_table);
                    $('#invalidQuantityModal').modal('show');
                }
            }
        });
    }
}

function eventButtonWarningOk(element_id, quantity_original, warning_table) {
    $('#warning_ok_id').on('click', function (e) {
        warning_table.clear();
        warning_table.destroy();
        $('#' + element_id).val(quantity_original).trigger('change');
        $('#' + element_id).focus();
    })
}

function pop_select_product(){
    pop_ok_dialog("Invalid Product",
        "Please select products before sending !",
        function(){
            $('#po_by_supp').select2("open");
    });
}

function get_remaining_quantity($selectior, refer_number, refer_line, ROW_INDEX_ITEM_QTY, SELECT_INDEX_REF_NUMBER, SELECT_INDEX_REFER_LINE, total_quantity, rowIndex = null) {
    let quantity = 0;
    $($selectior).each(function () {
        let indx = $(this).closest('tr').attr('data-row_index');
        let selects = $(this).closest('tr').find('select');
        let currentRow = $(this).closest('tr').find('input');
        // let currentLabel = $(this).closest('tr').find('label');
        cur_ref_number = $(selects[SELECT_INDEX_REF_NUMBER]).val();
        cur_ref_line = $(selects[SELECT_INDEX_REFER_LINE]).val();
        // cur_row_index = $(selects[SELECT_INDEX_REFER_LINE]).val();
        // if (cur_ref_number == undefined && cur_ref_line == undefined) {
        //     cur_ref_number = $(currentLabel[1]).text();
        //     cur_ref_line = $(currentLabel[2]).text();
        // }
        if (indx != rowIndex && cur_ref_number == refer_number && cur_ref_line == refer_line) {
            cur_quantity = float_format(currentRow[ROW_INDEX_ITEM_QTY].value);
            quantity = quantity + cur_quantity;
        }
    });

    return total_quantity - quantity;
}

function get_remaining_qty(dataList, refer, total_quantity, rowIndex=null) {
    let quantity = 0;
    let data_list = [];
    if (rowIndex) {
        data_list = dataList.filter(function (el) {
            return el.refer == refer && el.rowIndex != rowIndex;
        });
    } else {
        data_list = dataList.filter(function (el) {
            return el.refer == refer;
        });
    }

    for (i in data_list) {
        quantity = quantity + data_list[i].qty;
    }
    
    return total_quantity - quantity;
}

function update_remaining_qty(dataList, refer, qty, rowIndex, remove=false) {
    let found = false;
    let found_index = null;
    if (remove) {
        for (i in dataList) {
            if (dataList[i].rowIndex == rowIndex) {
                found = true;
                found_index = i;
                dataList[i].qty = qty;
                break;
            }
        }
        if(found) {
            dataList.splice(found_index, 1);
        }
    } else {
        for (i in dataList) {
            if (dataList[i].refer == refer && dataList[i].rowIndex == rowIndex) {
                found = true;
                found_index = i;
                dataList[i].qty = qty;
                break;
            }
        }
        if (!found) {
            dataList.push({
                'rowIndex': rowIndex,
                'refer': refer,
                'qty': qty,
            });
        }
    }

    return dataList;
}

function filterAllReferLine($selectior, refer_number, SELECT_INDEX_REF_NUMBER, skip_line=-1, refer_number_list=[], refer_line=null, last_refer_line="", type='DO') {
    if (refer_number_list.length) {
        $($selectior).each(function () {
            let rowIndex = $(this).closest('tr').attr('data-row_index');
            let selects = $(this).closest('tr').find('select');
            if ((type == 'DO' && selects.length > 2) || (type == 'GR' && selects.length >= 2)) {
                let cur_ref_number = $(selects[SELECT_INDEX_REF_NUMBER]).val();
                let cur_ref_line = $(selects[SELECT_INDEX_REF_NUMBER + 1]).val();
                let num_id = selects[SELECT_INDEX_REF_NUMBER].id;
                let line_id = selects[SELECT_INDEX_REF_NUMBER + 1].id;
                if (last_refer_line != "" && last_refer_line != undefined) {
                    if (refer_number == cur_ref_number && last_refer_line && !$('#' + line_id + ' option[value="' + last_refer_line + '"]').length > 0) {
                        $('#' + line_id).prepend("<option data-code_data=" + last_refer_line + " value=" + last_refer_line + ">" + last_refer_line + "</option>");
                        sortSelectOptions(line_id);
                        $('#' + line_id).val(cur_ref_line);
                    }
                }
                else if (refer_number == cur_ref_number && skip_line != -1 && skip_line != rowIndex && refer_line != cur_ref_line) {
                    $('#' + line_id + ' option[value="' + refer_line + '"]').remove();
                }
            }
        });
    }

    return "";
}

function sortSelectOptions(selectId, ref_number_select=false) {
    var options = $('#' + selectId + " option");
    options.detach().sort(function(a,b) {
        var at = $(a).val() ? parseInt(String($(a).val()).replace(/\D/g, "")) : 0;
        var bt = $(b).val() ? parseInt(String($(b).val()).replace(/\D/g, "")) : 0;
        if (ref_number_select) {
            return (at < bt) ? 1 : ((at > bt) ? -1 : 0);
        } else {
            return (at > bt) ? 1 : ((at < bt) ? -1 : 0);
        }
    });
    options.appendTo('#' + selectId);
}

function filterAllReferNumber(type, $selectior, refer_number, SELECT_INDEX_REF_NUMBER, skip_line=-1, refer_number_list=[], refer_line=null) {
    if (refer_number_list.length) {
        let refer_numbers = refer_number_list.filter(function (el) {
            return el.refer_number == refer_number;
        });
        $($selectior).each(function () {
            let selects = $(this).closest('tr').find('select');
            if ((type == 'DO' && selects.length > 2) || (type == 'GR' && selects.length >= 2)) {
                let cur_ref_number = $(selects[SELECT_INDEX_REF_NUMBER]).val();
                let cur_ref_line = $(selects[SELECT_INDEX_REF_NUMBER + 1]).val();
                let num_id = selects[SELECT_INDEX_REF_NUMBER].id;
                let line_id = selects[SELECT_INDEX_REF_NUMBER + 1].id;
                // if (cur_ref_number == '' || cur_ref_line == '') {
                    if (!$('#' + num_id + ' option[value="' + refer_numbers[0].refer_number + '"]').length > 0) {
                        $('#' + num_id).prepend("<option data-code_data=" + refer_numbers[0].order_id + " value=" + refer_numbers[0].refer_number + ">" + refer_numbers[0].refer_number + "</option>");
                        sortSelectOptions(num_id, true);
                        $('#' + num_id).val(cur_ref_number);
                    }
                    if (refer_number == cur_ref_number && refer_line && !$('#' + line_id + ' option[value="' + refer_line + '"]').length > 0) {
                        $('#' + line_id).prepend("<option data-code_data=" + refer_line + " value=" + refer_line + ">" + refer_line + "</option>");
                        sortSelectOptions(line_id);
                        $('#' + line_id).val(cur_ref_line);
                    }
                // }
            }
        });
    } else {
        if (refer_line) {
            $($selectior).each(function (indx) {
                let rowIndex = $(this).closest('tr').attr('data-row_index');
                if (skip_line != rowIndex) {
                    let selects = $(this).closest('tr').find('select');
                    if ((type == 'DO' && selects.length > 2) || (type == 'GR' && selects.length >= 2)) {
                        let cur_ref_number = $(selects[SELECT_INDEX_REF_NUMBER]).val();
                        let cur_ref_line = $(selects[SELECT_INDEX_REF_NUMBER + 1]).val();
                        let this_id = selects[SELECT_INDEX_REF_NUMBER + 1].id;
                        if (cur_ref_number != '' && cur_ref_line == '') {
                            $('#' + this_id + ' option[value="' + refer_line + '"]').remove();
                        }
                    }
                }
            });
        } else {
            $($selectior).each(function (indx) {
                let rowIndex = $(this).closest('tr').attr('data-row_index');
                if (skip_line != rowIndex) {
                    let selects = $(this).closest('tr').find('select');
                    if ((type == 'DO' && selects.length > 2) || (type == 'GR' && selects.length >= 2)) {
                        let cur_ref_number = $(selects[SELECT_INDEX_REF_NUMBER]).val();
                        let cur_ref_line = $(selects[SELECT_INDEX_REF_NUMBER + 1]).val();
                        let this_id = selects[SELECT_INDEX_REF_NUMBER].id;
                        if (cur_ref_number == '' || cur_ref_line == '') {
                            $('#' + this_id + ' option[value="' + refer_number + '"]').remove();
                        }
                    }
                }
            });
        }
    }

    return true;
}

$(document).on("input", ".numeric_qty", function() {
    let temp_str = this.value.replace(/[^0-9\.]/g,'');
    if (temp_str.split(".").length-1 > 1) {
        temp_str = temp_str.slice(0, -1);
    }
    if (temp_str.split(".").length > 1) {
        let temp_str_2 = temp_str.split(".")[1];
        if (temp_str_2.length > 2) {
            this.value = temp_str.split(".")[0] + '.' + temp_str_2.slice(0, -1)
        } else {
            this.value = temp_str;
        }
    } else {
        this.value = temp_str;
    }
});

$(document).on("input", ".numeric_price", function() {
    let price_str = this.value.replace(/[^0-9\.]/g,'');
    if (price_str.split(".").length-1 > 1) {
        price_str = price_str.slice(0, -1);
    }
    if (price_str.split(".").length > 1) {
        let price_str_2 = price_str.split(".")[1];
        if (price_str_2.length > 6) {
            this.value = price_str.split(".")[0] + '.' + price_str_2.slice(0, -1)
        } else {
            this.value = price_str;
        }
    } else {
        this.value = price_str;
    }
});

function reference_doc_list(del_ref_doc_list) {
    let warning_docs = [];
    del_ref_doc_list = del_ref_doc_list.split(',');
    $.each(del_ref_doc_list, function(indx, v) {
        warning_docs.push([v]);
    })
    var warning_table = $('#linked-list').DataTable({
        data: warning_docs,
        "paging": false,
        "info": false,
        "filter": false,
        "destroy": true,
        "columnDefs": [
            {
                "targets": 0,
                "orderable": false,
            },
            // {
            //     "targets": 1,
            //     "orderable": false,
            //     "visible": false
            // }
        ], order: []
    });
    eventButtonLinkedOk(warning_table);
    $('#msg_linked').html('Please remove the item from :');
    $('#warningLinkedModal').modal('show');
}

function linked_reference(founds) {
    if(founds) {
        let dataWarning = []
        let dataWarningTemp = []
        $.grep(founds, function(v) {
            // var new_data = [v.order_code, v.order_code_line];
            var new_data = [v.order_code];
            if (dataWarningTemp.indexOf(v.order_code + v.order_code_line) < 0) {
                dataWarning.push(new_data);
                dataWarningTemp.push(v.order_code + v.order_code_line);
            }
        });

        $('#msg_linked').html('Please remove the item from :');

        var warning_table = $('#linked-list').DataTable({
            data: dataWarning,
            "paging": false,
            "info": false,
            "filter": false,
            "destroy": true,
            "columnDefs": [
                {
                    "targets": 0,
                    "orderable": false,
                },
                // {
                //     "targets": 1,
                //     "orderable": false,
                //     "visible": false
                // }
            ], order: []
        });
        eventButtonLinkedOk(warning_table);
        $('#warningLinkedModal').modal('show');
    }
}

function eventButtonLinkedOk(warning_table) {
    $('#warning_ok_id').on('click', function (e) {
        warning_table.clear();
        warning_table.destroy();
    })
}

function change_new_row_attr(rowNo, arrt_change_index) {
    try {
        changeRowIndex = $('#dynamic-table tr.gradeX:nth-child('+rowNo+')').closest('tr');
        arrt_current_index = 0;
        $(changeRowIndex).attr('data-row_index', arrt_change_index);
        changeRowIndex.find(':input').each(function () {
            let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
            let id = 'id_' + name;
            $(this).attr({'name': name, 'id': id});
        });
        changeRowIndex.find('label').each(function () {
            let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
            let id = 'id_' + name;
            $(this).attr({'name': name, 'id': id});
        });
        changeRowIndex.find('select').each(function () {
            let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
            let id = 'id_' + name;
            $(this).attr({'name': name, 'id': id});
        });

        changeRowIndex.find('span.select2-selection').each(function () {
            if($(this).attr('aria-labelledby') != undefined) {
                let aria_labelledby = $(this).attr('aria-labelledby').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                $(this).attr({'aria-labelledby': aria_labelledby});
            }
        });

        changeRowIndex.find('span.select2-selection__rendered').each(function () {
            if($(this).attr('id') != undefined) {
                let id = $(this).attr('id').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                $(this).attr({'id': id});
            }
        });
    } catch (e) {
        console.log(e);
    }
}

function fix_table_row_indexes() {
    let rows =  $('#dynamic-table').find('tr.gradeX');
    let row_count = rows.length;
    for (let i=0; i<row_count; i++) {
        changeRowIndex = $('#dynamic-table tr.gradeX:nth-child('+(i+1)+')').closest('tr');
        arrt_current_index = parseInt(changeRowIndex.attr('data-row_index'));
        arrt_change_index = i;
        if (arrt_current_index != arrt_change_index) {
            changeRowIndex.find(':input').each(function () {
                let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                let id = 'id_' + name;
                $(this).attr({'name': name, 'id': id});
            });
            changeRowIndex.find('label').each(function () {
                let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                let id = 'id_' + name;
                $(this).attr({'name': name, 'id': id});
            });
            changeRowIndex.find('select').each(function () {
                let name = $(this).attr('name').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                let id = 'id_' + name;
                $(this).attr({'name': name, 'id': id});
            });

            changeRowIndex.find('span.select2-selection').each(function () {
                if($(this).attr('aria-labelledby') != undefined) {
                    let aria_labelledby = $(this).attr('aria-labelledby').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                    $(this).attr({'aria-labelledby': aria_labelledby});
                }
            });

            changeRowIndex.find('span.select2-selection__rendered').each(function () {
                if($(this).attr('id') != undefined) {
                    let id = $(this).attr('id').replace('-' + arrt_current_index + '-', '-' + arrt_change_index + '-');
                    $(this).attr({'id': id});
                }
            });
            changeRowIndex.attr('data-row_index', arrt_change_index);
        }
    }
}

function WarnPriceExceded(max_qty, elm, msg) {
    pop_ok_dialog("Invalid Item Price",
        msg,
        function(){
            // $(elm).val(max_qty).trigger('change');
            $(elm).val(comma_format(max_qty));
            $(elm).select();

            $('#dynamic-table tr.gradeX').each(function () {
                $(elm).closest('tr').find('input').removeAttr('disabled');
            });
            $(elm).closest('tr').removeAttr('style');
            fnEnableButton();
    });
}

function disableAutoComplete() {
    $("input[type='text']").each(function() {
        $(this).attr("autocomplete", "off");
    });
    $("input[type='number']").each(function() {
        $(this).attr("autocomplete", "off");
    });
}