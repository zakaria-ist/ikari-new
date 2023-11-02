/**
 * Created by tho.pham on 8/16/2016.
 */
var initial_item_qty = [];
var item_info = [];
var allVals = [];
var emptyRow = '';
var editing_row = null;
var append_index = 0;
var location_data = [];
var $selected_row = [];
// var append_or_prepend = false;
var order_is_decimal = 1;
var decimal_place = 2;
var total_line_quantity = 0;

var invalid_data_list = [];
var invalid_message_list = [];
var is_disable_show_duplicate = false;
var is_copy = false;
var do_check_duplicate_again = true;
var th_object = {
    'th-0': 'No',
    'th-1': 'Refer number',
    'th-2': 'Refer line',
    'th-3': 'Quantity'
};

if($('#company_is_inventory').val() == 'True') {
    emptyRow = `<tr class="gradeX" data-row_index="0">
                    <td>
                        <div class="btn-group" style="width:160px">
                            <button type="button" class="prependrow btn btn-white fa fa-level-up" name="prependrow" value="Prepend" ></button>
                            <button type="button" class="appendrow btn btn-white fa fa-level-down" name="appendrow" value="Append" style="margin-left:0.4rem;"></button>
                            <button type="button" class="editrow btn btn-white fa fa-square-o" name="editrow" value="Edit" data-toggle="modal" data-target="#orderItemModal" style="margin-left:0.4rem;"></button>
                            <button type="button" class="removerow btn btn-white fa fa-minus" name="removerow" value="Remove" style="margin-left:0.4rem;"></button>
                        </div>
                    </td>
                    <td><label id="id_formset_item-0-line_number" class="control-label-item" name="formset_item-0-line_number">1</label>
                        <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none;" type="text">
                    </td>
                    <td>
                        <select id="id_select-0-ref_number" class="form-control select_ref_number" name="select-0-ref_number">
                            <option value="">Select Ref Number</option>
                        </select>
                        <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="display: none" type="text">
                    </td>
                    <td>
                        <select id="id_select-0-refer_line" class="form-control select_refer_line" name="select-0-refer_line">
                            <option value="">Ref Ln</option>
                        </select>
                        <div style="display: none;"><input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="text-align: right; width: 40px;" type="text"></div>
                    </td>
                    <td>
                        <select id="id_select-0-item_code" class="form-control select_item_code" name="select-0-item_code" required="required">
                            <option value="">Select Part No.</option>
                        </select>
                        <label id="id_formset_item-0-code" class="control-label-item" name="formset_item-0-code" style="display: none"></label>
                        <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                    </td>
                    <td style="display: none;">
                        <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" type="text">
                        <input class="form-control-item" id="id_formset_item-0-identity" name="formset_item-0-identity" type="text">
                    </td>
                    <td><input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" required="required" style="text-align: left; width: 250px;" type="text"></td>
                    <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                    <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency"></label>
                        <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item text-right numeric_price" id="id_formset_item-0-price" min="0" name="formset_item-0-price" step="0.000001" style="text-align: right; width: 140px;" type="number"></td>
                    <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" step="0.000000001" style="text-align: right; width: 80px;" type="number"></td>
                    <td style="text-align: right;"><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label>
                        <input class="form-control-item text-right hide" id="id_formset_item-0-amount" name="formset_item-0-amount" step="any" style="text-align: right; width: 120px;" type="number">
                    </td>
                                                    
                    <td>
                        <select id="id_formset_item-0-location" class="form-control select_location" name="formset_item-0-location" style="width: 110px; text-align: center;">
                            </select>
                    </td>
                    
                    <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom"></label>
                        <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category" style="width: 80px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                    </td>
                    <td><input class="form-control default-date-picker" id="id_formset_item-0-wanted_fake_date" name="formset_item-0-wanted_fake_date" autocompltete="off" required="required" style="width: 110px; text-align: right;" type="text"><input class="form-control hide" id="id_formset_item-0-wanted_date" name="formset_item-0-wanted_date" required="required" style="width: 110px; text-align: right;" type="text"></td>
                    <td><input class="form-control default-date-picker" id="id_formset_item-0-schedule_fake_date" name="formset_item-0-schedule_fake_date" autocompltete="off" style="width: 110px; text-align: right;" type="text"><input class="form-control hide" id="id_formset_item-0-schedule_date" name="formset_item-0-schedule_date" style="width: 110px; text-align: right;" type="text"></td>
                    <td><input class="form-control-item" id="id_formset_item-0-description" name="formset_item-0-description" style="text-align: left; width: 400px;" type="text"></td>
                    <td><label id="id_formset_item-0-supplier" class="control-label-item" name="formset_item-0-supplier" style="width: 100px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-backorder_qty" class="control-label-item backorder-qty" name="formset_item-0-backorder_qty">0</label>
                        <input class="form-control-item" id="id_formset_item-0-backorder_qty" name="formset_item-0-backorder_qty" style="display: none" type="text">
                    </td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-delivery_quantity" name="formset_item-0-delivery_quantity" step="0.1" style="display: none" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" step="0.1" style="display: none" type="number"></td>
                </tr>`;
} else {
    emptyRow = `<tr class="gradeX" data-row_index="0">
                    <td>
                        <div class="btn-group" style="width:160px">
                            <button type="button" tabindex="-1" class="prependrow btn btn-white fa fa-level-up" name="prependrow" value="Prepend" ></button>
                            <button type="button" tabindex="-1" class="appendrow btn btn-white fa fa-level-down" name="appendrow" value="Append" style="margin-left:0.4rem;"></button>
                            <button type="button" class="editrow btn btn-white fa fa-square-o" name="editrow" value="Edit" data-toggle="modal" data-target="#orderItemModal" style="margin-left:0.4rem;"></button>
                            <button type="button" tabindex="-1" class="removerow btn btn-white fa fa-minus" name="removerow" value="Remove" style="margin-left:0.4rem;"></button>
                        </div>
                    </td>
                    <td><label id="id_formset_item-0-line_number" class="control-label-item" name="formset_item-0-line_number">1</label>
                        <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none;" type="text">
                    </td>
                    <td>
                        <select id="id_select-0-ref_number" class="form-control select_ref_number" name="select-0-ref_number">
                            <option value="">Select Ref Number</option>
                        </select>
                        <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="display: none" type="text">
                    </td>
                    <td>
                        <select id="id_select-0-refer_line" class="form-control select_refer_line" name="select-0-refer_line">
                            <option value="">Ref Ln</option>
                        </select>
                        <div style="display: none;"><input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="text-align: right; width: 40px;" type="text"></div>
                    </td>
                    <td>
                        <select id="id_select-0-item_code" class="form-control select_item_code" name="select-0-item_code" required="required">
                            <option value="">Select Part No.</option>
                        </select>
                        <label id="id_formset_item-0-code" class="control-label-item" name="formset_item-0-code" style="display: none"></label>
                        <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                    </td>
                    <td style="display: none;">
                        <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" type="text">
                        <input class="form-control-item" id="id_formset_item-0-identity" name="formset_item-0-identity" type="text">
                    </td>
                    <td><input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" required="required" style="text-align: left; width: 250px;" type="text"></td>
                    <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                    <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency"></label>
                        <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item text-right numeric_price" id="id_formset_item-0-price" min="0" name="formset_item-0-price" step="0.000001" style="text-align: right; width: 140px;" type="number"></td>
                    <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" step="0.000000001" style="text-align: right; width: 80px;" type="number"></td>
                    <td style="text-align: right;"><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label>
                        <input class="form-control-item text-right hide" id="id_formset_item-0-amount" name="formset_item-0-amount" step="any" style="text-align: right; width: 120px;" type="number">
                    </td>
                    
                    <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom"></label>
                        <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category" style="width: 80px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                    </td>
                    <td><input class="form-control default-date-picker" id="id_formset_item-0-wanted_fake_date" name="formset_item-0-wanted_fake_date" autocompltete="off" required="required" style="width: 110px; text-align: right;" type="text"><input class="form-control hide" id="id_formset_item-0-wanted_date" name="formset_item-0-wanted_date" required="required" style="width: 110px; text-align: right;" type="text"></td>
                    <td><input class="form-control default-date-picker" id="id_formset_item-0-schedule_fake_date" name="formset_item-0-schedule_fake_date" autocompltete="off" style="width: 110px; text-align: right;" type="text"><input class="form-control hide" id="id_formset_item-0-schedule_date" name="formset_item-0-schedule_date" style="width: 110px; text-align: right;" type="text"></td>
                    <td><input class="form-control-item" id="id_formset_item-0-description" name="formset_item-0-description" style="text-align: left; width: 400px;" type="text"></td>
                    <td><label id="id_formset_item-0-supplier" class="control-label-item" name="formset_item-0-supplier" style="width: 100px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-backorder_qty" class="control-label-item backorder-qty" name="formset_item-0-backorder_qty">0</label>
                        <input class="form-control-item" id="id_formset_item-0-backorder_qty" name="formset_item-0-backorder_qty" style="display: none" type="text">
                    </td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-delivery_quantity" name="formset_item-0-delivery_quantity" step="0.1" style="display: none" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" step="0.1" style="display: none" type="number"></td>
                </tr>`;
}

var PO_ROW_INDEX_LINE_NUMBER = 0;
var PO_ROW_INDEX_REFER_NO = PO_ROW_INDEX_LINE_NUMBER + 1;
var PO_ROW_INDEX_REFER_LINE = PO_ROW_INDEX_REFER_NO + 1;
var PO_ROW_INDEX_CODE = PO_ROW_INDEX_REFER_LINE + 1;
var PO_ROW_INDEX_ITEM_NAME = PO_ROW_INDEX_CODE + 1;
var PO_ROW_INDEX_ITEM_ID = PO_ROW_INDEX_ITEM_NAME + 1;
var PO_ROW_INDEX_IDENTITY = PO_ROW_INDEX_ITEM_ID + 1;
var PO_ROW_INDEX_CUSTOMER_PO = PO_ROW_INDEX_IDENTITY + 1;
// var PO_ROW_INDEX_BACKORDER_QTY = PO_ROW_INDEX_CUSTOMER_PO + 1;
// var PO_ROW_INDEX_ITEM_QTY = PO_ROW_INDEX_BACKORDER_QTY + 1;
var PO_ROW_INDEX_ITEM_QTY = PO_ROW_INDEX_CUSTOMER_PO + 1;
var PO_ROW_INDEX_CURRENCY_CODE = PO_ROW_INDEX_ITEM_QTY + 1;
var PO_ROW_INDEX_CURRENCY_ID = PO_ROW_INDEX_CURRENCY_CODE + 1;
var PO_ROW_INDEX_ITEM_PRICE = PO_ROW_INDEX_CURRENCY_ID + 1;
var PO_ROW_INDEX_EXCHANGE_RATE = PO_ROW_INDEX_ITEM_PRICE + 1;
var PO_ROW_INDEX_AMOUNT = PO_ROW_INDEX_EXCHANGE_RATE + 1;
var PO_ROW_INDEX_UOM = PO_ROW_INDEX_AMOUNT + 1;
var PO_ROW_INDEX_CATEGORY = PO_ROW_INDEX_UOM + 1;
var PO_ROW_INDEX_WANTED_FAKE_DATE = PO_ROW_INDEX_CATEGORY + 1;
var PO_ROW_INDEX_WANTED_DATE = PO_ROW_INDEX_WANTED_FAKE_DATE + 1;
var PO_ROW_INDEX_SCHEDULE_FAKE_DATE = PO_ROW_INDEX_WANTED_DATE + 1;
var PO_ROW_INDEX_SCHEDULE_DATE = PO_ROW_INDEX_SCHEDULE_FAKE_DATE + 1;
var PO_ROW_INDEX_DESCRIPTION = PO_ROW_INDEX_SCHEDULE_DATE + 1;
var PO_ROW_INDEX_SUPPLIER_CODE = PO_ROW_INDEX_DESCRIPTION + 1;
var PO_ROW_INDEX_SUPPLIER_ID = PO_ROW_INDEX_SUPPLIER_CODE + 1;
var PO_ROW_INDEX_BACKORDER_QTY = PO_ROW_INDEX_SUPPLIER_ID + 1;
var PO_ROW_INDEX_MIN_ORDER_QTY = PO_ROW_INDEX_BACKORDER_QTY + 1;
var PO_ROW_INDEX_REFERENCE_ID = PO_ROW_INDEX_MIN_ORDER_QTY + 1;


var PO_LABEL_INDEX_LINE_NUMBER = 0;
// var PO_LABEL_INDEX_REFER_NO = PO_LABEL_INDEX_LINE_NUMBER + 1;
// var PO_LABEL_INDEX_REFER_LINE = PO_LABEL_INDEX_REFER_NO + 1;
var PO_LABEL_INDEX_ITEM_CODE = PO_LABEL_INDEX_LINE_NUMBER + 1;
var PO_LABEL_INDEX_ITEM_NAME = PO_LABEL_INDEX_ITEM_CODE + 1;
// var PO_LABEL_INDEX_BACKORDER_QTY = PO_LABEL_INDEX_ITEM_NAME + 1;
// var PO_LABEL_INDEX_CURRENCY_CODE = PO_LABEL_INDEX_BACKORDER_QTY + 1;
var PO_LABEL_INDEX_CURRENCY_CODE = PO_LABEL_INDEX_ITEM_NAME + 1;
var PO_LABEL_INDEX_AMOUNT = PO_LABEL_INDEX_CURRENCY_CODE + 1;
var PO_LABEL_INDEX_UOM = PO_LABEL_INDEX_AMOUNT + 1;
var PO_LABEL_INDEX_CATEGORY = PO_LABEL_INDEX_UOM + 1;
var PO_LABEL_INDEX_SUPPLIER_CODE = PO_LABEL_INDEX_CATEGORY + 1;
var PO_LABEL_INDEX_BACKORDER_QTY = PO_LABEL_INDEX_SUPPLIER_CODE + 1;

var PO_SELECT_INDEX_REF_NUMBER = 0;
var PO_SELECT_INDEX_REFER_LINE = PO_SELECT_INDEX_REF_NUMBER + 1;
var PO_SELECT_INDEX_ITEM_CODE = PO_SELECT_INDEX_REFER_LINE + 1;
if($('#company_is_inventory').val() == 'True') {
    var PO_SELECT_INDEX_LOCATION = PO_SELECT_INDEX_ITEM_CODE + 1;
}

/* PO Column Index */

var PO_COL_BUTTONS = 0; // 0
var PO_COL_LINE_NUMBER = PO_COL_BUTTONS + 1; // 1
var PO_COL_REF_NUMBER = PO_COL_LINE_NUMBER + 1; // 2
var PO_COL_REFER_LINE = PO_COL_REF_NUMBER + 1; // 3
var PO_COL_PART_NO = PO_COL_REFER_LINE + 1; // 4
var PO_COL_ITEM_NAME = PO_COL_PART_NO + 1; // 5
var PO_COL_CUSTOMER_PO = PO_COL_ITEM_NAME + 1; // 6
var PO_COL_QTY = PO_COL_CUSTOMER_PO + 1; // 7
var PO_COL_CURRENCY = PO_COL_QTY + 1; // 8
var PO_COL_PRICE = PO_COL_CURRENCY + 1; // 9
var PO_COL_EXCHNG_RATE = PO_COL_PRICE + 1; // 10
var PO_COL_AMOUNT = PO_COL_EXCHNG_RATE + 1; // 11
if($('#company_is_inventory').val() == 'True') {
    var PO_COL_LOC_CODE = PO_COL_AMOUNT + 1; // 12
    var PO_COL_UOM = PO_COL_LOC_CODE + 1; // 13
} else {
    var PO_COL_UOM = PO_COL_AMOUNT + 1; // 13
}
var PO_COL_PART_GROUP = PO_COL_UOM + 1; // 14
var PO_COL_WANTED_DATE = PO_COL_PART_GROUP + 1; // 15
var PO_COL_SCHEDULE_DATE = PO_COL_WANTED_DATE + 1; // 16
var PO_COL_REMARK = PO_COL_SCHEDULE_DATE + 1; // 17
var PO_COL_SUPPLIER_CODE = PO_COL_REMARK + 1; // 18
var PO_COL_BACKORDER_QTY = PO_COL_SUPPLIER_CODE + 1; // 19
var PO_COL_MIN_ORDER = PO_COL_BACKORDER_QTY + 1; // 20
var PO_COL_REF_ID = PO_COL_MIN_ORDER + 1; // 21


function check_linked(refer_line, remove=true) {
    let is_linked = false;
    if ($('#id_document_number').val()) {

        var founds = $.grep(order_items, function(v) {
            if (v.refer_line == refer_line && v.refer_number == $('#id_document_number').val()) {
                return v;
            }
        });

        if (founds.length > 0) {
            if (remove) linked_reference(founds);
            is_linked = true;
        }
    }

    return is_linked;
}

function get_location_list() {
    $.ajax({
        method: "GET",
        url: '/orders/location_code_list/',
        dataType: 'JSON',
        success: function (json) {
            location_data = json;
            if ($('#company_is_inventory').val() == 'True' && order_id) {
                $('#dynamic-table tr.gradeX').each(function () {
                    let line_number = $(this).closest('tr').attr('data-line_number');
                    let selects = $(this).closest('tr').find('select');
                    if (line_number && check_linked(line_number, false) == true) {
                        selects.each(function (selectIndex, selectValue) {
                            if (selectIndex == 0) {
                                location_choice = '#' + selects[0].id;
                                let loc_val = $(location_choice).val();
                                $.each(location_data, function(indx, item) {
                                    if (loc_val != item.location_id) {
                                        $(location_choice + ' option[value="' + item.location_id + '"]').remove();
                                    }
                                });
                            }
                        });
                    }
                });
            }
        }
    });
}

let storeCopyRefNumberData = [];

$(document).ready(function () {

    // on first focus (bubbles up to document), open the menu
    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });

    $(document).on('select2:close', '#modal_ref_number_select', function (e) {
      $('#modal_refer_line_select').focus();
    });

    $(document).on('select2:close', '#modal_refer_line_select', function (e) {
        if ($('#modal_ref_number_select').val() != '') {
            $('#modal_customer_po_no').focus();
        } else {
            $('#modal_item_code select').focus();
        }
    });

    $(document).on('select2:close', '#modal_part_item_code_select', function (e) {
        $('#modal_customer_po_no').focus();
    });

    $(document).on('select2:close', '#modal_location select', function (e) {
        $('#modal_quantity').focus();
    });


    // $(document).on('focusout', '#modal_part_item_code_select', function (e) {
    //   $('#modal_customer_po_no').focus();
    // });

    // $('button').keypress(function(event){
    //     var keycode = (event.keyCode ? event.keyCode : event.which);
    //     if(keycode == '13'){
    //         $(this).trigger('click');
    //     }
    // });

    $('#items_error').css("display", "none");
    if($('#company_is_inventory').val() == 'True') {
        setTimeout(() => {
            get_location_list();
        }, 1500);
        
    }
    handleQuantity();
    handleDates();
    load_part_numbers_supp();

    if (!$('#id_supplier').val()){
        $('#id_currency').val(0);
        $('#btnOpenItemDialog').attr('disabled', 'disabled');
        $('#txtPartNo').prop('disabled', true);

        $('#dynamic-table tbody').find('tr.gradeX:last').remove();
        let total = parseInt($('#id_formset_item-TOTAL_FORMS').val());
        total--;
        $('#id_formset_item-TOTAL_FORMS').val(total);
        append_index = $('#dynamic-table').find('tr.gradeX').length;
    } else {
        if(float_format($('#id_subtotal').val())) {
            setTimeout(() => {
                $('#dynamic-table tr.gradeX:last').remove();
                $('#id_formset_item-TOTAL_FORMS').val($('#id_formset_item-TOTAL_FORMS').val() - 1);
                $('#dynamic-table tbody').find('tr.gradeX:last').find('td:first').find('div').find('.appendrow').prop('disabled', false);
                append_index = $('#dynamic-table').find('tr.gradeX').length;
            }, 200);
        }
    }

    $('#id_document_date').addClass('hide');
    var theday = dateView($("#id_document_date").val());
    $("#id_document_date_fake").val(theday);
    $('#selector_currency').addClass('hide');
    var name_curr = $("#selector_currency option:selected").text();
    $('#name_currency').val(name_curr);
    // $('#id_tax option:not(:selected)').attr('disabled', true);

    // Remove required attribute on modal
    $('#modal_w_date').removeAttr('required');
    $('#modal_customer_po_no').removeAttr('required');

    //Supplier
    $('#id_supplier').select2({
        placeholder: "Select supplier",
    });
    $('#id_supplier').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#id_transaction_code').select2();
    $('.location_select select').select2();

    //Part Number
    $('#load_code_by_supp').select2({
        placeholder: "Select Part Number",
    });

    if (!$('#id_supplier').val()){
        $('#id_supplier').select2("open");
    }

    $('#id_cost_center').select2({
        placeholder: "Select Cost Center",
    });

    $('#id_supplier').on('select2:close', function (e)
    {
        $('#id_document_date_fake').focus();
    });

    $('#id_cost_center').on('select2:close', function (e)
    {
        $('#id_transport_responsibility').focus();
    });

    // Replace currency symbol
    var currency_id = parseInt($('#id_currency option:selected').val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];

    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');

        if (currentRow[PO_ROW_INDEX_ITEM_ID].value === '' || currentRow[PO_ROW_INDEX_CURRENCY_ID].value === '')
            return;

        arrItems.push({
            item_id: currentLabel[PO_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[PO_ROW_INDEX_CURRENCY_ID].value
        });

        let line = currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent;
        let ref_number = currentLabel[PO_LABEL_INDEX_ITEM_CODE].textContent;
        let ref_line = currentLabel[PO_LABEL_INDEX_ITEM_NAME].textContent;
        // storeCopyRefNumberData = saveCopyRefNumberDO(line, ref_number, ref_line, 'add', storeCopyRefNumberData, allVals);

        currentLabel[PO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[PO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
    });

    if (arrItems.length > 0) changeCurrency(arrItems, currency_id, currency_name);

    $('#invalidInputModal').on('shown.bs.modal', function () {
        if ($("#orderItemModal").is(':visible')) {
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#modal_item_code select').select2('close');
        }
    });

    $('#comfirmSaveDeleteOrderModal').on('shown.bs.modal', function () {
        if ($("#comfirmSaveDeleteOrderModal").is(':visible')) {
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#modal_item_code select').select2('close');
        }
    });

    let allItemQty = getAllItemQty();

    setTimeout(() => {
        get_refer_order_items(allItemQty);
    }, 2000);

});

$('#id_supplier').on('change', function() {
    load_part_numbers_purch();
    $('#btnOpenItemDialog').removeAttr('disabled');
    $('#txtPartNo').prop('disabled', false);
    $('#dynamic-table tbody').find('tr').remove();
    $('#id_subtotal').val(0);
    $('#id_total').val(0);
    $('#id_tax_amount').val(0);
    $(emptyRow).insertBefore('#id_formset_item-TOTAL_FORMS');
    $('#id_formset_item-TOTAL_FORMS').val('1');
    disableAutoComplete();
    load_supp();
    append_index = 1;
});

function getAllItemQty(){
    var AllItemQty = [];
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');
        if (currentRow[PO_ROW_INDEX_ITEM_ID].value){
            AllItemQty.push({
                ln: currentRow[PO_ROW_INDEX_LINE_NUMBER].value,
                refer_line: currentRow[PO_ROW_INDEX_REFER_LINE].value,
                refer_doc: currentRow[PO_ROW_INDEX_REFER_NO].value,
                item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
                qty: float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value),
                order_id: $(currentLabel[1]).data('code_data')
            });
        }
    });
    return AllItemQty;
}

function get_refer_order_items(allItemQty) {
    var all_so = [];
    for (j in allItemQty) {
        if (allItemQty[j].order_id) {
            all_so.push(allItemQty[j].order_id);
        }
    }
    var all_sos = JSON.stringify(all_so);
    $.ajax({
        method: "POST",
        url: '/orders/get_so_order_item_for_po/',
        dataType: 'JSON',
        async: false,
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'so_number': all_sos,
            'supplier_id': $('#id_supplier').val(),
            'exclude_item_list': []
        },
        success: function (json) {
            if (json != 'something went wrong' && json.length) {
                for (j in allItemQty) {
                    var temp_object = allItemQty[j];
                    var ref_line_list = [];
                    $.each(json, function (i, item) {
                        if (item.refer_id == allItemQty[j].order_id) {
                            ref_line_list.push(item.refer_line);
                        }
                    });
                    storeCopyRefNumberData.push({
                        'line': temp_object.refer_line,
                        'ref_number': temp_object.refer_doc,
                        'location_item_quantity': temp_object.qty,
                        'original_item_quantity': temp_object.qty,
                        'ref_line': temp_object.refer_line,
                        'ref_line_list': ref_line_list,
                    });
                }
            }
        }
    });
}

function change_refer_line() {
    // this function to renew the refer line of orderItem table
    // We will use order_items data for auto change the refer line  base on the entry already linked
    if ($('#id_document_number').val()) {
        let new_order_items = []
        $(".gradeX[data-line_number]").map(function(){
            let line_number =  $(this).attr('data-line_number');
            let rowIndex = parseInt($(this).find('label:first').text());
            $.grep(order_items, function(v) {
                if (v.refer_line == line_number && v.refer_number == $('#id_document_number').val()) {
                    v.new_refer_line = rowIndex;
                    new_order_items.push(v);
                }
            });
        })
        if (new_order_items.length > 0) {
            order_items = new_order_items;
        }
    }
}

function fixForm() {
    fix_table_row_indexes();
    change_refer_line();
    $('#index_order_items').val(JSON.stringify(order_items));

    var subtotal = 0;
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).find('input');
        var currentLabel = $(this).find('label');
        let rowIndex = $(this).attr('data-row_index');
        let qty = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value);
        currentRow[PO_ROW_INDEX_ITEM_QTY].value = qty;

        if (currentRow[PO_ROW_INDEX_AMOUNT].value == '') {
            // let amount = float_format(currentLabel[PO_LABEL_INDEX_AMOUNT].textContent);
            let amount = float_format($('#id_formset_item-'+rowIndex+'-amount').text());
            currentRow[PO_ROW_INDEX_AMOUNT].value = amount;
            subtotal += amount;
        } else {
            // let amount = float_format(currentRow[PO_ROW_INDEX_AMOUNT].value);
            let amount = float_format($('#id_formset_item-'+rowIndex+'-amount').val());
            currentRow[PO_ROW_INDEX_AMOUNT].value = amount;
            subtotal += amount;
        }
    });

    var tax_rate = float_format($('#hdTaxRate').val());
    var tax_amount = 0;
    var total = 0;
    subtotal = roundDecimal(subtotal, decimal_place);
    $('#id_subtotal').val(subtotal);
    if (tax_rate > 0){
        tax_amount = (float_format(tax_rate) * subtotal) / 100;
    }
    tax_amount = roundDecimal(tax_amount, decimal_place);
    $('#id_tax_amount').val(float_format(tax_amount, decimal_place));
    if ($('#id_discount').val() == '' || $('#id_discount').val() == null) {
        total = subtotal + float_format($('#id_tax_amount').val());
    } else {
        total = subtotal + float_format($('#id_tax_amount').val()) - float_format($('#id_discount').val());
    }
    total = roundDecimal(total, decimal_place);
    $('#id_total').val(total);
}

function disableShowDuplicate() {
    is_disable_show_duplicate = true;
}

function enableShowDuplicate() {
    is_disable_show_duplicate = false;
}


function validate_cuspo_po_copy() {
    // check duplicate customer_po
    var duplicate_cuspo_list = [];
    var has_location = false;
    if ($('#company_is_inventory').val() == 'True') {
        has_location = true;
    }
    $('#dynamic-table tr.gradeX').each(function (i, v) {
        var cRow = $(this).closest('tr').find('input');
        var cLabel = $(this).closest('tr').find('label');
        var cpo = cRow[PO_ROW_INDEX_CUSTOMER_PO].value;
        var citem = cRow[PO_ROW_INDEX_CODE].value;
        var csup = $('#id_supplier option:selected').text();
        var line = parseInt($(this).closest('tr').attr('data-row_index'));
        var loc = '';
        if ($('#company_is_inventory').val() == 'True') {
            // $l_select = '#' + $(this).closest('tr').find('select')[PO_SELECT_INDEX_LOCATION].id;
            loc = $('#id_formset_item-' + line + '-location').select2('data')[0].text;
        }
        var data = {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'cust_po_no': cpo,
            'item_id': cRow[PO_ROW_INDEX_ITEM_ID].value,
            'type': 'SO'
        };
        $.ajax({
            url: '/orders/get_orderitems_by_cust_po_no/',
            type: 'POST',
            data: data,
            cache: false,
        })
        .done(function (data) {
            if (data.length != 0 && data[0].doc_no) {
                if (has_location) {
                    if (loc == data[0].loc_code) {
                        duplicate_cuspo_list.push([data[0].ln_no, data[0].doc_no, citem, cpo, csup, data[0].loc_code]);
                        duplicate_cuspo_list.push([cLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, loc]);
                    }
                } else {
                    duplicate_cuspo_list.push([data[0].ln_no, data[0].doc_no, citem, cpo, csup, '']);
                    duplicate_cuspo_list.push([cLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, '']);
                }
            }
        });
    });
    setTimeout(() => {
        if (duplicate_cuspo_list.length) {
            duplicate_cuspo_list.sort(function(a, b) { 
                return parseInt(a[0]) > parseInt(b[0]) ? 1 : -1;
            });
            show_duplicate_cuspo_modal(duplicate_cuspo_list, '', has_location, true);
        } else {
            do_check_duplicate_again = false;
            $('#form').attr('action','/orders/order_edit/' + order_id + '/2/1/0/');
            $('#form').submit();
        }
        $('#loading').hide();
    }, 1500);
}

$(document).ready(function () {
    // $('#btnSave').on('click', function (e) {
    $('#form').submit(function (e) {

        if ($('#id_exchange_rate_value').val() == '' || $('#id_exchange_rate').val() == '') {
            pop_ok_dialog("Invalid Exchange Rate",
                "Exchange Rate not found for current period.",
                function () { }
            );
            e.preventDefault();
            return false;
        }

        var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
        if (countRowVisible == 0) {
            pop_select_product();
            e.preventDefault();
            return false;
        }

        var is_valid = true;
        invalid_data_list = [];
        invalid_message_list = [];
        var allTableData = [];
        $('#dynamic-table tr.gradeX:visible').each(function () {
            var currentRow = $(this).find('input');
            var currentSelect = $(this).find('select');
            var currentLabel = $(this).find('label');

            var quantity = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value);
            var unitPrice = float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value);

            // id_formset_item-0-ref_number
            // id_formset_item-0-refer_line

            var refer_doc = '';
            var refer_line = '';
            if (currentSelect.length == 1 && $('#company_is_inventory').val() == 'True' || currentSelect.length == 0) {
                refer_doc = currentLabel[1].textContent.trim();
                refer_line = currentLabel[2].textContent.trim();
            } else {
                refer_doc = currentSelect[PO_SELECT_INDEX_REF_NUMBER].value;
                refer_line = currentSelect[PO_SELECT_INDEX_REFER_LINE].value;
            }

            if (quantity == 0 || unitPrice == 0) {
                is_valid = false;
                invalid_data_list.push({
                    ln: currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
                    refer_doc: refer_doc,
                    refer_line: refer_line,
                    quantity: currentRow[PO_ROW_INDEX_ITEM_QTY].value,
                    unitPrice: currentRow[PO_ROW_INDEX_ITEM_PRICE].value,
                });
            }

            // allTableData.push({
            //     ln: currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
            //     refer_doc: refer_doc,
            //     refer_line: refer_line,
            //     quantity: currentRow[PO_ROW_INDEX_ITEM_QTY].value,
            //     unitPrice: currentRow[PO_ROW_INDEX_ITEM_PRICE].value,
            // });
        });
        if (!is_valid) {
            invalid_message_list.push('Please select valid quantity or unit price. <br>');
            invalid_message_list.push('Total is ZERO. Please select valid quantity.');
            show_invalid_modal(invalid_data_list, invalid_message_list, disableShowDuplicate(), enableShowDuplicate(), th_object);
            e.preventDefault();
            return false;
        } else {
            // check duplicate
            // allTableData.sort(SortByReferNumber);

            // var duplicate_data_list = [];
            // for (var i = 0; i < allTableData.length - 1; i++) {
            //     if (allTableData[i + 1].refer_doc == allTableData[i].refer_doc &&
            //         allTableData[i + 1].refer_line == allTableData[i].refer_line) {
            //         let data_list_filter = duplicate_data_list.filter(function (el) {
            //             return el.ln == allTableData[i].ln;
            //         });
            //         if (data_list_filter.length < 1 ) {
            //             duplicate_data_list.push(allTableData[i]);
            //         }
            //         duplicate_data_list.push(allTableData[i + 1]);
            //     }
            // }
            // if (duplicate_data_list.length > 0 && !is_disable_show_duplicate) {
            //     show_invalid_modal(duplicate_data_list, [], disableShowDuplicate(), enableShowDuplicate(), th_object);
            //     e.preventDefault();
            //     return false;
            // } else {
                $('#loading').show();
                // if (is_copy && do_check_duplicate_again) {
                //     validate_cuspo_po_copy();
                //     e.preventDefault();
                //     return false;
                // } else {
                    fixForm();
                    checkForm(this);
                // }
            // }
        }
    });

    $('#id_delivery').select2({
        allowClear: true,
        placeholder: "Select Alternate Consignee",
    });
    $('#id_delivery').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#id_delivery').on("select2:close", function() {
        $('#id_remark').focus();
    });
});

$('#id_delivery').change(function () {
    var delivery_id = parseInt($(this).val());
    $.ajax({
        method: "POST",
        url: '/orders/change_address/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'delivery_id': delivery_id
        },
        responseTime: 200,
        response: function (settings) {
            if (settings.data.value) {
                this.responseText = '{"success": true}';
            } else {
                this.responseText = '{"success": false, "msg": "required"}';
            }
        },
        success: function (json) {
            $('#id_name').val(json['name']);
            $('#id_attention').val(json['attention']);
            $('#id_address').val(json['address']);
            $('#id_phone').val(json['phone']);
            $('#id_note_1').val(json['note_1']);
        }
    });
});

// $(document).keypress(function (e) {
//     if (e.which == 13 && !$(event.target).is("textarea")) {
//         e.preventDefault();
//     }
// });

//Add Extra Label Value formset
$(document).ready(function () {
    // checkDisplay();
    var supplier = $('#id_supplier').val();
    
    if ((supplier > 0) && (!$('#id_exchange_rate').val())) {
        load_supp();
    } else {
        $('#id_exchange_rate_value').val($('#id_exchange_rate').val());
    }
    if (supplier == null) {
        fnDisableButton();
    } else {
        fnEnableButton();
        load_refer_numbers();
    }
});

//Company Information
$(document).ready(function () {

    //toggle `popup` / `inline` mode
    $.fn.editable.defaults.mode = 'inline';
    //Get company id
    var company_id = $('#company_id').val();
    //make status editable
    // $('#companyname').editable({
    //     type: 'text',
    //     pk: company_id,
    //     url: '/orders/change_company/' + company_id + '/',
    //     title: 'Enter company name',
    //     success: function (response, newValue) {
    //
    //         if (!response) {
    //             return "Unknown error!"
    //         }
    //         if (response.success === false) {
    //             return respond.msg;
    //         }
    //     }
    // });

    // $('#address').editable({
    //     type: 'text',
    //     pk: company_id,
    //     url: '/orders/change_company/' + company_id + '/',
    //     title: 'Enter company address',
    //     success: function (response, newValue) {
    //         if (!response) {
    //             return "Unknown error!"
    //         }
    //         if (response.success === false) {
    //             return respond.msg;
    //         }
    //     }
    // });
    //
    // $('#email').editable({
    //     type: 'text',
    //     pk: company_id,
    //     url: '/orders/change_company/' + company_id + '/',
    //     title: 'Enter company email',
    //     validate: function (value) {
    //         var valid = valib.String.isEmailLike(value)
    //         if (valid == false) return 'Please insert valid email'
    //     },
    //     success: function (response, newValue) {
    //
    //         if (!response) {
    //             return "Unknown error!"
    //         }
    //         if (response.success === false) {
    //             return respond.msg;
    //         }
    //     }
    // });

});
//Supplier Information
$(document).ready(function (hdSupplierId) {
    var hdSupplierId = $('#id_supplier').val();
    loadSupplierInfo(hdSupplierId);

    var callback = function () {
        $.ajax({
            method: "POST",
            url: '/orders/supplier_search_by_code/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'supplier_code': $("#form_supplier_code").val()
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
                $('#hdSupplierId').val(json['id']);
                $("#form_supplier_code").val(json['code']);
                $('#supplier_name').editable('destroy');
                $('#supplier_address').editable('destroy');
                $('#supplier_email').editable('destroy');

                $('#supplier_name').attr('data-pk', json['id']);
                $('#supplier_name').text(json['name']);
                $('#supplier_address').text(json['address']);

                $('#supplier_email').attr('data-pk', json['id']);
                $('#supplier_email').text(json['email']);
                $('#customer_payment_term').text(json['term'] + ' days');
                $('#customer_payment_mode').text(json['payment_mode']);
                $('#customer_credit_limit').text( json['credit_limit']);
                loadSupplierInfo(json['id']);
                $('#id_tax').find('option').removeAttr("selected");
                $('#id_tax').find('option').removeAttr("disabled");
                $('#id_tax').find('option[value="' + json['tax_id'] + '"]').attr("selected", "selected");
                $('#id_tax').val(json['tax_id']);
                // $('#id_tax option:not(:selected)').attr('disabled', true);
                // load tax again
                var taxid = parseInt($('#id_tax').val());
                if (isNaN(taxid)) {
                    $('#id_tax_amount').val(0);
                    $('#id_total').val(comma_format(float_format($('#id_tax_amount').val()) - float_format($('#id_discount').val()) + float_format($('#id_subtotal').val()), decimal_place));
                } else {
                    $.ajax({
                        method: "POST",
                        url: '/orders/load_tax/',
                        dataType: 'JSON',
                        data: {
                            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                            'tax_id': taxid,
                        },
                        success: function (json) {
                            var tax_amount = (float_format(json) * float_format($('#id_subtotal').val())) / 100;
                            $('#hdTaxRate').val(float_format(json));
                            $('#id_tax_amount').val(comma_format(float_format(tax_amount.toFixed(decimal_place)), decimal_place));
                            var total = float_format($('#id_subtotal').val()) + tax_amount;
                            $('#id_total').val(comma_format(float_format(total.toFixed(decimal_place)), decimal_place));
                        }
                    });
                }
                $('#id_currency').find('option').removeAttr('selected');
                $('#id_currency').find('option').removeAttr('disabled');
                $('#id_currency option[value=' + json['currency_id'] + ']').attr('selected', 'selected');
                $('#id_currency').val(json['currency_id']);
                $('#id_currency option:not(:selected)').attr('disabled', true);
            }
        })
    };
    $("#form_supplier_code").keypress(function (e) {
        if (e.which == 13) {
            e.preventDefault();
            callback();
        }
    });
    $('#btnSearchSupplier').on('click', function () {
        $('#supplier-table').DataTable().destroy();
        $('#supplier-table').dataTable({
            "iDisplayLength": 5,
            "bLengthChange": false,
            "order": [[0, "desc"]],
            "serverSide": true,
            "ajax": {
                "url": "/orders/suppliers_list_as_json/"
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "name", "sClass": "text-left"},
                {"data": "term_days", "sClass": "text-left"},
                {"data": "payment_mode", "sClass": "text-left"},
                {"data": "credit_limit", "sClass": "text-left"},
                {
                    "orderable": false,
                    "data": null,
                    "sClass": "hide_column",
                    "render": function (data, type, full, meta) {
                        return '<input type="radio" name="choices" id="' +
                            full.id + '" class="call-checkbox" value="' + full.id + '">';
                    }
                }
            ],
            "drawCallback": function(settings) {
                $('#mySupplierListModal .call-checkbox').off('click').on('click', function() {
                    if ($(this).is(':checked')) {
                        $('#id_supplier').val($(this).val());
                        $('#id_supplier option[value="'+$(this).val()+'"]').attr('selected', 'selected');
                        $('#id_supplier').trigger('change');
                    }
                });

                $('#mySupplierListModal .call-checkbox[value="'+$('#id_supplier').val()+'"]').attr('checked', 'checked');
            }
        });
    });
    $('#supplier-table').on( 'draw.dt', function () {
        selectTableRow('#supplier-table', 5);
        $("input[type='radio']").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
    });

    $('#btnSupplierSelect').on('click', function () {
        var supplier_select_id = $("input[name='choices']:checked").attr('id');

        $('#hdSupplierId').val(supplier_select_id);
        $('#id_supplier').val(supplier_select_id).trigger('change');

        $('#id_currency option[value=' + supplier_select_id + ']').attr('selected', 'selected');

        var nRow = $("input[name='choices']:checked").parents('tr')[0];
        var jqInputs = $('td', nRow);
        $("#form_supplier_code").val(jqInputs[0].innerText);

        $(this).attr('data-dismiss', 'modal');
        callback();
    });

    var hdSupplierId = $('#id_supplier').val();
    loadSupplierInfo(hdSupplierId);

    function loadSupplierInfo(hdSupplierId) {
        $.fn.editable.defaults.mode = 'inline';

        //make status editable
        $('#supplier_name').editable({
            type: 'text',
            pk: hdSupplierId,
            title: 'Enter supplier name',
        });

        $('#supplier_address').editable({
            type: 'text',
            pk: hdSupplierId,
            title: 'Enter supplier address',
        });

        $('#supplier_email').editable({
            type: 'text',
            pk: hdSupplierId,
            title: 'Enter supplier email',
        });
    };
});

//Event check checkbox
$('input[type=checkbox]').click(function () {
    if ($(this).is(':checked'))
        $(this).attr('checked', 'checked');
    else
        $(this).removeAttr('checked');
});



//Add order item
$(document).ready(function () {


    function store_row_index(newRowIndex, curRowIndex) {
        // let $selected = [];
        // $selected.push($('#id_select-' + (curRowIndex) + '-ref_number').val());
        // $selected.push($('#id_select-' + (curRowIndex) + '-refer_line').val());
        // if ($('#id_select-' + (curRowIndex) + '-item_code').find('option:selected').data('code_data') != null) {
        //     $selected.push($('#id_select-' + (curRowIndex) + '-item_code').find('option:selected').data('code_data')[0]);
        // }
        // $selected.push($('#id_formset_item-' + (curRowIndex) + '-location').val());
        //
        var row_currency = $('#id_formset_item-'+ (curRowIndex) +'-currency_id').val();
        if($('#id_select-' + (curRowIndex) + '-refer_line').val() == null) {
            row_currency = ''
        }

        $selected_row.push({
            'row':newRowIndex,
            'ref_number': $('#id_formset_item-'+ (curRowIndex) +'-ref_number').val(),
            'qty': $('#id_formset_item-'+ (curRowIndex) +'-quantity').val(),
            // 'line': $('#id_formset_item-'+ (rowIndex+1) +'-line_number').text(),
            'po_no': $('#id_formset_item-'+ (curRowIndex) +'-customer_po_no').val(),
            // 'code': $('#id_formset_item-'+ (rowIndex+1) +'-code').text(),
            'currency': row_currency,
            'price': float_format($('#id_formset_item-'+ (curRowIndex) +'-price').val()).toFixed(6),
            'exch_rate': $('#id_formset_item-'+ (curRowIndex) +'-exchange_rate').val(),
            'amount': $('#id_formset_item-'+ (curRowIndex) +'-amount').text(),
            'category': $('#id_formset_item-'+ (curRowIndex) +'-category').text(),
            'backorder_qty': $('#id_formset_item-'+ (curRowIndex) +'-backorder_qty').text(),
            'wanted_date': $('#id_formset_item-'+ (curRowIndex) +'-wanted_date').val(),
            'wanted_fake_date': $('#id_formset_item-'+ (curRowIndex) +'-wanted_fake_date').val(),
            'schedule_date': $('#id_formset_item-'+ (curRowIndex) +'-schedule_date').val(),
            'schedule_fake_date': $('#id_formset_item-'+ (curRowIndex) +'-schedule_fake_date').val(),
            'description': $('#id_formset_item-'+ (curRowIndex) +'-description').val(),
            'supplier': $('#id_formset_item-'+ (curRowIndex) +'-supplier').val(),
            'supplier_code': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code').text(),
            'supplier_id': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code_id').val(),
            'uom': $('#id_formset_item-'+ (curRowIndex) +'-uom').text(),
        });

        // return  $selected;
    };

    function change_row_attr(rowNo, arrt_current_index, arrt_change_index) {
        changeRowIndex = $('#dynamic-table tr.gradeX:nth-child('+rowNo+')').closest('tr');
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
    }

    function bindingData() {
        for(i in $selected_row) {
            var row_amout = '0.00';
            if ($selected_row[i].amount != 'NaN') {
                row_amout = $selected_row[i].amount;
            }
            $('#id_formset_item-'+ ($selected_row[i].row) +'-wanted_date').val($selected_row[i].wanted_date);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-wanted_fake_date').val($selected_row[i].wanted_fake_date);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-schedule_date').val($selected_row[i].schedule_date);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-schedule_fake_date').val($selected_row[i].schedule_fake_date);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-description').val($selected_row[i].description);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-uom').val($selected_row[i].uom);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-uom').text($selected_row[i].uom);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier').val($selected_row[i].supplier);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code').val($selected_row[i].supplier_code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code').text($selected_row[i].supplier_code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code_id').val($selected_row[i].supplier_id);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-backorder_qty').val($selected_row[i].backorder_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-backorder_qty').text($selected_row[i].backorder_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').val($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').text($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').val(float_format(row_amout).toFixed(decimal_place));
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').text(row_amout);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-exchange_rate').val($selected_row[i].exch_rate);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-price').val($selected_row[i].price);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-price').text($selected_row[i].price);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-currency_id').val($selected_row[i].currency);
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-code').val($selected_row[i].code);
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-code').text($selected_row[i].code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').val($selected_row[i].po_no);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').text($selected_row[i].po_no);
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-line_number').val($selected_row[i].line);
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-quantity').val($selected_row[i].qty).trigger('change');
            $('#id_formset_item-'+ ($selected_row[i].row) +'-quantity').val($selected_row[i].qty);
        }
        $('#loading').hide();
    }

    function closeAllSelectOnTable() {
        try{
            $('select[id^=id_select-][id$=-ref_number]').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('select[id^=id_select-][id$=-refer_line]').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('select[id^=id_select-][id$=-item_code]').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    $(document).on('click', "[class^=removerow]", function (event) {
        closeAllSelectOnTable();

        // check refer line and Document Number had to link, if linked -> can not remove
        let line_number = $(this).closest('tr').attr('data-line_number');
        if (!is_copy && check_linked(line_number) == true) {
            return;
        }

        // $selected_row = [];
        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        last_amount = float_format($('#id_formset_item-'+(rowIndex)+'-amount').text());

        let refer_number = $('#id_select-' + rowIndex +'-ref_number').val();
        if (refer_number == undefined) {
            refer_number = $('#id_formset_item-' + rowIndex +'-ref_number').text();
        }

        if (refer_number != '' && refer_number != undefined) {
            let idx = $(this).closest('tr').find('label:first').text();
            storeCopyRefNumberData = saveCopyRefNumberDO(idx, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
            storeCopyRefNumberData = changeIndexData(idx, 'minus', storeCopyRefNumberData);
        }

        currentRow = $(this).closest('tr').find('input');
        item_id = currentRow[PO_ROW_INDEX_ITEM_ID].value;
        if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
            $(this).parents("tr").remove();
            $('#id_subtotal').val(0);
            $('#id_total').val(0);
            $('#id_tax_amount').val(0);
            let newRow = emptyRow;
            $('#id_formset_item-TOTAL_FORMS').before(newRow);
            newRow = $('#dynamic-table tr.gradeX:nth-child(1)').closest('tr');
            disableAutoComplete();

            initiateRefNumber(newRow);

        } else {
            fnEnableButton();

            var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
            $('#id_formset_item-TOTAL_FORMS').val(minus);
            $(this).parents("tr").remove();

            let rowNumber = 0;
            // let rows =  $('#dynamic-table').find('tr.gradeX');
            $('#dynamic-table tr.gradeX').each(function () {
                let currentRow = $(this).closest('tr').find('input');
                let currentLine = $(this).closest('tr').find('label');
                currentLine[PO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
                currentRow[PO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
                rowNumber++;
            });
            // rowNumber = rows.length-1;
            // $selected_row.length = 0;

            // while(rowNumber >= rowIndex) {
            //     store_row_index(rowNumber, rowNumber + 1);
            //     change_row_attr(rowNumber + 1, rowNumber + 1, rowNumber);
            //     rowNumber--;
            // }

            setTimeout(() => {
                // bindingData();
                // calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
                calculatePOTotal(last_amount, 0);
                // store the new refer line
                change_refer_line();
            }, 100);

        }

    });

    $(document).on('click', "[class^=appendrow]", function (event) {
        closeAllSelectOnTable();
        // $selected_row = [];
        let inputs = $(this).closest('tr').find('input');
        let cus_po_no = inputs[PO_ROW_INDEX_CUSTOMER_PO].value;
        let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
        let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));

        storeCopyRefNumberData = changeIndexData(rowIndex.toString(), 'plus', storeCopyRefNumberData);
        let copy_refer_number = $('#id_select-' + (temp_rowIndex) +'-ref_number').val();
        if (copy_refer_number == undefined) {
            copy_refer_number = $('#id_formset_item-' + (temp_rowIndex) +'-ref_number').text();
        }

        let total = $('#id_formset_item-TOTAL_FORMS').val();
        total = parseInt(total);
        let newRow = emptyRow;
        $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').after(newRow);
        total++;
        $('#id_formset_item-TOTAL_FORMS').val(total);
        disableAutoComplete();

        let rowNumber = 0;
        // let rows =  $('#dynamic-table').find('tr.gradeX');
        $('#dynamic-table tr.gradeX').each(function () {
            let currentRow = $(this).closest('tr').find('input');
            let currentLine = $(this).closest('tr').find('label');
            currentLine[PO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
            currentRow[PO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
            rowNumber++;
        });
        // rowNumber = rows.length-1;
        // $selected_row.length = 0;

        // append_or_prepend = true;
        // while(rowNumber > rowIndex) {
        //     store_row_index(rowNumber, rowNumber - 1);
        //     change_row_attr(rowNumber + 1, rowNumber - 1, rowNumber);
        //     rowNumber--;
        // }

        // if ($selected_row.length) {
        //     $('#loading').show();
        // }

        // change_row_attr(rowIndex+1, 0, rowIndex);
        rowNumber = append_index;
        change_new_row_attr(rowIndex+1, rowNumber);
        append_index++;

        //initialize select2 of new row
        newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex+1)+')').closest('tr');
        initiateRefNumber(newRow);
        schedule_fake_date(newRow)

        copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData, allVals);
        if ( copy_refer_number != '' && $('#id_select-' + (rowNumber) + '-ref_number option[value="' + copy_refer_number + '"]').length > 0) {
             $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
        }

        setTimeout(() => {
            // bindingData();
            $('#id_formset_item-' + rowNumber + '-customer_po_no').val(cus_po_no);
            // store the new refer line
            change_refer_line();
        }, 100);
    });

    $(document).on('click', "[class^=prependrow]", function (event) {
        closeAllSelectOnTable();
        // $selected_row = [];
        let inputs = $(this).closest('tr').find('input');
        let cus_po_no = inputs[PO_ROW_INDEX_CUSTOMER_PO].value;
        let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
        let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        let prev_rowIndex = parseInt($(this).closest('tr').prev().attr('data-row_index'));

        storeCopyRefNumberData = changeIndexData((rowIndex - 1).toString(), 'plus', storeCopyRefNumberData);
        let copy_refer_number = $('#id_select-' + (prev_rowIndex) +'-ref_number').val();
        if (copy_refer_number == undefined) {
            copy_refer_number = $('#id_formset_item-' + (prev_rowIndex) +'-ref_number').text();
        }

        let rowNumber = 0;
        // let rows =  $('#dynamic-table').find('tr.gradeX');
        // rowNumber = rows.length;
        // while(rowNumber >= rowIndex) {
        //     store_row_index(rowNumber, rowNumber -1);
        //     change_row_attr(rowNumber, rowNumber - 1, rowNumber);
        //     rowNumber--;
        // }

        let total = $('#id_formset_item-TOTAL_FORMS').val();
        total = parseInt(total);
        let newRow = emptyRow;
        $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').before(newRow);
        total++;
        $('#id_formset_item-TOTAL_FORMS').val(total);
        disableAutoComplete();

        rowNumber = 0;
        $('#dynamic-table tr.gradeX').each(function () {
            let currentRow = $(this).closest('tr').find('input');
            let currentLine = $(this).closest('tr').find('label');
            currentLine[PO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
            currentRow[PO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
            rowNumber++;
        });

        // if ($selected_row.length) {
        //     $('#loading').show();
        // }

        //initialize select2 of new row
        // change_row_attr(rowIndex, 0, rowIndex-1);
        // let rows =  $('#dynamic-table').find('tr.gradeX');
        rowNumber = append_index;
        change_new_row_attr(rowIndex, rowNumber);
        append_index++;
        newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').closest('tr');

        initiateRefNumber(newRow);
        schedule_fake_date(newRow);

        copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData, allVals);
        if ( copy_refer_number != '' && $('#id_select-' + (rowNumber) + '-ref_number option[value="' + copy_refer_number + '"]').length > 0) {
             $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
        }

        setTimeout(() => {
            // bindingData();
            $('#id_formset_item-' + (rowNumber) + '-customer_po_no').val(cus_po_no);
            //calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
            // store the new refer line
            change_refer_line();
        }, 100);

    });

    // $('input[id^=id_formset_item-][id$=-description]').on('keydown', function(e) {
    //     let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
    //     let code_pressed = e.keyCode || e.which;
    //     tabAddRow(rowIndex, code_pressed);
    // });

    var next = false;
    var prev = false;
    var dyn_tbl_sel_row_id = 0;
    var line_object = {
        'ref_num': '',
        'ref_line': '',
        'part_item': '',
        'cust_po': '',
        'w_date': '',
        's_date': '',
        'qty': '',
        'price': '',
        'remark': ''
    }
    var action_button = '';
    let store_current_row = '';

    function next_prev_action() {
        if(next) {
            // selectedRowId = dyn_tbl_sel_row_id + 1;
            // var row = $('#dynamic-table tr.gradeX')[selectedRowId];
            // var valid = ($(row).length != 0);
            // if (valid) {
            //     loadOrderItemModal_2(selectedRowId);
            // }
            if (editing_row.next().hasClass('gradeX')) {
                editing_row = editing_row.next();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }

        } else if (prev) {
            // selectedRowId = dyn_tbl_sel_row_id - 1;
            // if(selectedRowId >= 0) {
            //     loadOrderItemModal_2(selectedRowId);
            // }
            if ((editing_row.prev()).length) {
                editing_row = editing_row.prev();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }

        } else {
            $('#orderItemModal').modal('toggle');
        }
    }

    function closeAllSelect2OnModal() {
        try{
            $('#modal_ref_number select').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('#modal_refer_line select').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('#modal_item_code select').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('#modal_location select').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    $(document).on('click', "[class^=editrow]", function (event) {
        editing_row = $(this).closest('tr');
        selectedRowId = parseInt($(this).closest('tr').attr('data-row_index'));
        loadOrderItemModal_2(selectedRowId);
    });

    $(document).on('click', "[id^=saves_line]", function (event) {
        selectedRowId = dyn_tbl_sel_row_id;
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            setTimeout(() => {
                next_prev_action();
            }, 1000);
        } else {
            $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=btnOrderItemPrev]", function (event) {
        next = false;
        prev = true;

        action_button = 'prev';
        if(is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            // var ok = $.checkOrderRowValidity(dyn_tbl_sel_row_id);
            // if (!ok) {
            //     var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            //     $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
            // }
            editing_row = editing_row.prev();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal_2(selectedRowId);
        }

    });

    $(document).on('click', "[id^=btnOrderItemNext]", function (event) {
        next = true;
        prev = false;
        action_button = 'next';
        if (is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            editing_row = editing_row.next();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal_2(selectedRowId);
        }
    });

    $(document).on('click', "[id^=btnOrderItemSave]", function (event) {
        selectedRowId = dyn_tbl_sel_row_id;
        // var ok = $.checkOrderRowValidity(selectedRowId);
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            // var row = $('#dynamic-table tr.gradeX')[selectedRowId + 1];
            // var valid = ($(row).length != 0);
            // if (!valid) {
            if (!editing_row.next().hasClass('gradeX')) {
                setTimeout(() => {
                    // $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId+1) + ')').find('.appendrow').trigger('click');
                    editing_row.find('.appendrow').trigger('click');
                    setTimeout(() => {
                        editing_row = editing_row.next();
                        selectedRowId = parseInt(editing_row.attr('data-row_index'));
                        loadOrderItemModal_2(selectedRowId);
                        $('#loading').hide();
                    }, 1500);
                    $('#loading').show();
                }, 1500);
            } else {
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal_2(selectedRowId);
                }, 1000);
            }
        } else {
             $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=remove_line]", function (event) {
        removeLine();
    });

    $(document).on('click', "[id^=save_line]", function (event) {
        // $('#orderItemModal').modal('toggle');
    });

    $(document).on('click', "[id^=save_new_line]", function (event) {
        selectedRowId = dyn_tbl_sel_row_id;
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            // var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            setTimeout(() => {
                // $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
                editing_row.find('.appendrow').trigger('click');
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal_2(selectedRowId);
                    $('#loading').hide();
                }, 1500);
                $('#loading').show();
            }, 1500);
        } else {
            $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=discard_line]", function (event) {
        var ok = $.checkOrderRowValidity(dyn_tbl_sel_row_id);
        if (ok) {
            // var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            setTimeout(() => {
                // $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
                editing_row.find('.appendrow').trigger('click');
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal_2(selectedRowId);
                    $('#loading').hide();
                }, 1500);
                $('#loading').show();
            }, 1500);
        } else {
            loadOrderItemModal_2(dyn_tbl_sel_row_id)
        }
    });

    $(document).on('click', "[id^=reset_line]", function (event) {
        resetLine();
    });

    $(document).on('click', "[id^=btnOrderItemNew]", function (event) {
        if (is_change()) {
            $('#comfirmSaveNewOrderModal').modal('show');
        } else {
            itemNewRow();
        }
    });

    $(document).on('click', "[id^=btnOrderItemCancel]", function (event) {
        action_button = 'cancel';
        orderItemCancel();
    });


    $(document).on('click', "[id^=btnOrderItemDelete]", function (event) {
        try{
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#modal_item_code select').select2('close');
        } catch(e) {
            console.log(e)
        }
        $('#comfirmSaveDeleteOrderModal').modal('show');
    });


    // $('#modal_w_date').bind('keydown', function (event) {
    //     if (event.which == 9) {
    //          if ($('#company_is_inventory').val() == 'True') {
    //              $('#modal_location select').focus();
    //              $('#modal_location select').select2('open');
    //          } else {
    //              $('#modal_quantity').focus();
    //          }
    //     }
    // });

    $('#modal_w_date').bind('keyup', function (event) {
        adjust_input_date(this);
    });

    // $('#modal_s_date').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         date_key_down(this);
    //         return false;
    //     }
    // });

    $('#modal_s_date').bind('keyup', function (event) {
        adjust_input_date(this);
    });

    $('#modal_w_date').on('change, focusout', function (e) {
        if ($(this).val() == '') {
            return false;
        }
        var date_from = get_date_from('#' + e.target.id);
        date_from = date_from.split('/').join('-');
        var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();

        if (!date_from_valid) {
            pop_ok_dialog("Invalid Wanted Date",
                "Wanted Date (" + $('#' + e.target.id).val() + ") is invalid !",
                function () {
                    // wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                    $('#modal_w_date').val('');
                    $('#modal_w_date').focus();
                });

        } else {
            var doc_date = $('#id_document_date').val();
            // var current_date = new Date();
            var current_date = new Date(moment(doc_date, "YYYY-MM-DD").format("YYYY-MM-DD"));
            current_date.setHours(0, 0, 0, 0);
            var input_date = new Date(moment($('#' + e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
            var resultOK = true;
            if (input_date.getTime() < current_date.getTime()) {
                resultOK = false;
                pop_ok_cancel_dialog("Invalid Wanted Date",
                    "Wanted Date (" + $('#' + e.target.id).val() +
                    ") is back dated !<br/> Do you want to proceed?",
                    function () {
                        $('#modal_w_date').val(date_from); $('#modal_quantity').select();
                        $('#modal_w_date').removeClass('highlight-mandatory');
                        },
                    function () {
                        wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                        $('#modal_w_date').val(wanted_date);
                        $('#modal_w_date').select();
                        $('#modal_w_date').removeClass('highlight-mandatory');
                    });
            } else {
                var so_date = $(this).attr('so_date');
                if (so_date){
                    // var current_date = new Date();
                    var current_date = new Date(moment(so_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
                    current_date.setHours(0,0,0,0);
                    var input_date = new Date(moment($('#'+e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
                    input_date.setHours(0,0,0,0);
                    if (input_date.getTime() > current_date.getTime()) {
                        resultOK = false;
                        pop_ok_dialog("Invalid Wanted Date",
                                "Wanted Date ("+$('#' + e.target.id).val() +
                                ") cannot be later than S/O wanted date",
                                function(){
                                    $('#modal_w_date').val(so_date);
                                    $('#modal_w_date').select();
                                    $('#modal_w_date').removeClass('highlight-mandatory');
                                });
                    }
                } else {
                    var sched_date = new Date(moment($('#modal_s_date').val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
                    if (sched_date) {
                        ssched_date = new Date(sched_date);
                        if (input_date.getTime() < ssched_date.getTime()) {
                            resultOK = false;
                            pop_ok_cancel_dialog("Invalid Wanted Date",
                                "Wanted Date (" + $('#' + e.target.id).val() +
                                ") must be greater than or equal to Schedule Date (" + sched_date +
                                ") !<br/> Do you want to proceed?",
                                function () {
                                    $('#modal_w_date').val(date_from);
                                    $('#modal_w_date').removeClass('highlight-mandatory');
                                },
                                function () {
                                    wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                                    $('#modal_w_date').val(wanted_date);
                                    $('#modal_w_date').select();
                                    $('#modal_w_date').removeClass('highlight-mandatory');
                                });
                        }
                    }
                }
            }

            if (resultOK) {
                $('#modal_w_date').val(date_from);
                // $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val(date_from);
                $(this).removeClass('highlight-mandatory');
            } else {
                wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                $('#modal_w_date').val(wanted_date);
            }
        }
    });

    $('#modal_w_date').click(function () {
        $(this).select();
    });

    $('#modal_s_date').on('change, focusout', function (e) {
        if ($(this).val() == '') {
            return false
        }
        var date_from = get_date_from('#' + e.target.id);
        date_from = date_from.split('/').join('-');
        var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();

        if (!date_from_valid) {
            pop_ok_dialog("Invalid Schedule Date",
                "Schedule Date (" + $('#' + e.target.id).val() + ") is invalid !",
                function () {
                    // schedule_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-schedule_fake_date').val();
                    $('#modal_s_date').val('');
                    $('#modal_s_date').focus();
                });

        } else {
            var doc_date = $('#id_document_date').val();
            // var current_date = new Date();
            var current_date = new Date(moment(doc_date, "YYYY-MM-DD").format("YYYY-MM-DD"));
            current_date.setHours(0, 0, 0, 0);
            var input_date = new Date(moment($('#' + e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
            var resultOK = true;
            if (input_date.getTime() < current_date.getTime()) {
                resultOK = false;
                pop_ok_cancel_dialog("Invalid Schedule Date",
                    "Schedule Date (" + $('#' + e.target.id).val() +
                    ") is back dated !<br/> Do you want to proceed?",
                    function () { $('#modal_s_date').val(date_from); },
                    function () {
                        // schedule_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-schedule_fake_date').val();
                        $('#modal_s_date').val('');
                        $('#modal_s_date').focus();
                    });
            } else {
                var want_date = new Date(moment($('#modal_w_date').val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
                if (want_date) {
                    wwant_date = new Date(want_date);
                    if (input_date.getTime() < wwant_date.getTime()) {
                        resultOK = false;
                        pop_ok_cancel_dialog("Invalid Schedule Date",
                            "Schedule Date (" + $('#' + e.target.id).val() +
                            ") must be greater than or equal to Wanted Date (" + want_date +
                            ") !<br/> Do you want to proceed?",
                            function () { $('#modal_s_date').val(date_from); },
                            function () {
                                // schedule_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-schedule_fake_date').val();
                                $('#modal_s_date').val('');
                                $('#modal_s_date').focus();
                            });
                    }
                }
            }

            if (resultOK) {
                $('#modal_s_date').val(date_from);
            } else {
                // schedule_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-schedule_fake_date').val();
                $('#modal_s_date').val('');
                $('#modal_s_date').focus();
            }
        }
    });

    $('#modal_s_date').click(function () {
        $(this).select();
    });

    $('#modal_customer_po_no').click(function () {
        $(this).select();
    });

    $('#modal_quantity').click(function () {
        $(this).select();
    });

    $('#modal_remarks').click(function () {
        $(this).select();
    });

    // $('#modal_customer_po_no').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_customer_po_no').trigger('change');
    //         return false;
    //     }
    // });

    // $('#modal_w_date').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_quantity').select();
    //         return false;
    //     }
    // });

    // $('#modal_quantity').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $(this).val(comma_format($(this).val()));
    //         $('#modal_price').select();
    //         return false;
    //     }
    // });

    // $('#modal_price').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_remarks').select();
    //         return false;
    //     }
    // });

    // $('#modal_part_item_code').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $(this).find('select').trigger('select2:open');
    //         return false;
    //     }
    // });
    //
    // $('#modal_remarks').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_s_date').select();
    //         return false;
    //     }
    // });

    // $('#modal_s_date').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#btnOrderItemSave').focus();
    //         return false;
    //     }
    // });

    $('#btnOrderItemNext').bind('keydown', function (event) {
        if (event.which == 13) {
            $(this).click();

            return false;
        }
    });

    function bindItemCodeEvent() {
        $('#modal_item_code select').on("change", function() {
            let item_code = $('#modal_item_code select').find('option:selected').data('code_data')[0];
            if(item_code) {
                // $('#modal_customer_po_no').val(item_code.customer_po_no);
                $('#modal_item_code').val(item_code.code);
                $('#modal_supplier').val(item_code.supplier);
                $('#modal_original_currency').val(item_code.currency);
                $('#modal_uom').val(item_code.uom);
                $('#modal_category').val(item_code.category);
                $('#modal_quantity').val(comma_format(item_code.quantity)).trigger('change');
                $('#modal_quantity').data('minoq', item_code.minimun_order)
                $('#modal_price').val(float_format(item_code.purchase_price).toFixed(6));
                // $('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
                $('#modal_backorder_qty').val(comma_format(item_code.backorder_qty));
                $('#modal_remark').val(item_code.description);
                if ($('#company_is_inventory').val() == 'True' && item_code.location_list.length){
                    if ($('#modal_location select').data('select2')) {
                        $('#modal_location select').select2('destroy');
                    }
                    $('#modal_location select').empty();
                    var options = '';
                    $.each(item_code.location_list, function(indx, loc) {
                        options += "<option value="+loc.id+">"+loc.code+"</option>";
                    });
                    $('#modal_location select').append(options);
                    $('#modal_location select').select2();
                    $('#modal_location select').val(item_code.location_list[0].id).trigger('change');
                }
                $($('#select2-modal_part_item_code_select-container').parent('span')[0]).removeClass('highlight-mandatory');
            } else {
                $($('#select2-modal_part_item_code_select-container').parent('span')[0]).addClass('highlight-mandatory');
            }

            setTimeout(() => {
                $('#modal_customer_po_no').select();
                $('#modal_customer_po_no').trigger('change');
            }, 1000);
        });
    }

    function bindOrderModalEvent() {
        var last_price = 0.00;
        $('#modal_ref_number select').on("change", function() {

            let is_update = false;
            let so_number = $('#modal_ref_number select').find('option:selected').data('code_data');
            let supp_id = $('#id_supplier').val();

            if (so_number != null && supp_id != null) {
                $.ajax({
                    method: "POST",
                    url: '/orders/get_so_orderitems_for_po/',
                    dataType: 'JSON',
                    data: {
                        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                        'so_number': so_number,
                        'supplier_id': supp_id,
                        'exclude_item_list': []
                    },
                    success: function (json) {
                        allVals.length = 0;
                        if (json.length > 0) {
                            allVals = json;
                        }
                        // $.each(json, function (i, item) {
                        //     if(item.supplier_id == supp_id) {
                        //         allVals.push({
                        //             id: item.item_id, //Item ID
                        //             price: item.sales_price,
                        //             item_code: item.item_code, //Item Code
                        //             name: item.item_name, //Item Name
                        //             refer_number: item.refer_number,
                        //             refer_line: item.refer_line,
                        //             supplier_code: item.supplier_code,
                        //             location_code: item.location_code,
                        //             category: item.category,
                        //             unit_price: item.unit_price,
                        //             currency: item.currency_code,
                        //             location_id: item.location_id,
                        //             currency_id: item.currency_id,
                        //             uom: item.uom,
                        //             wanted_date: item.wanted_date,
                        //             schedule_date: item.schedule_date,
                        //             description: item.description,
                        //             supplier_id: item.supplier_id,
                        //             backorder_qty: item.backorder_qty,
                        //             order_quantity: item.quantity,
                        //             delivery_quantity: item.delivery_quantity,
                        //             customer_po_no: item.customer_po_no,
                        //             country_origin_id: item.country_origin_id,
                        //             country_origin_cd: item.country_origin_cd,
                        //             location_item_quantity: item.location_item_quantity,
                        //             minimum_order: item.minimum_order,
                        //             ref_id: item.refer_id,
                        //         });
                        //     }
                        // });
                        $('#modal_supplier').val('');
                        // $('#modal_customer_po_no').val('');
                        $('#modal_original_currency').val('');
                        $('#modal_uom').val('');
                        $('#modal_category').val('');
                        $('#modal_item_code').val('');
                        $('#modal_quantity').val('');
                        $('#modal_price').val('');
                        $('#modal_amount').val('0.00');
                        $('#modal_backorder_qty').val('');
                        $('#modal_w_date').val('');
                        $('#modal_s_date').val('');
                        $('#modal_remark').val('');

                        if ($('#modal_refer_line select').data('select2')) {
                            $('#modal_refer_line select').select2('destroy');
                        }

                        $('#modal_refer_line select').empty();

                        var options = '<option value="">Ref Ln</option>';

                        for (i in allVals) {
                            options += "<option data-code_data="+allVals[i].refer_line+" value="+allVals[i].refer_line+">"+allVals[i].refer_line+"</option>";
                        }

                        $('#modal_refer_line select').html(options);

                        $('#modal_refer_line select').select2({
                            placeholder: "Ref Ln"
                        });

                        $('#modal_refer_line select').on("select2:open", function( event ){
                            prefill_select2(event);

                            // Fix Select2 input search style
                            $('.select2-container input.select2-search__field').css({
                            //     // 'text-align': 'left',
                                'font-size': '12.5px'
                            });
                        });

                        setTimeout(function() {
                            if ($("#orderItemModal").is(':visible')) {
                                $('#modal_refer_line select').select2('open');
                            }
                            if (allVals.length == 1) {
                                $('#modal_refer_line select').val(allVals[0].refer_line).trigger('change');
                                $('#modal_refer_line select').select2('close');
                                setTimeout(function() {
                                    $('#modal_customer_po_no').focus();
                                    $('#modal_customer_po_no').select();
                                }, 200);
                            }
                            if (allVals.length != 1) {
                                if (so_number != '') {
                                    $('#id_select-'+dyn_tbl_sel_row_id+'-item_code').select2('destroy');
                                    $('#id_select-'+dyn_tbl_sel_row_id+'-item_code').empty();
                                }
                                if ($('#modal_item_code select').data('select2')) {
                                    $('#modal_item_code select').select2('destroy');
                                }
                                $('#modal_item_code select').empty();
                                $('#modal_item_code select').prop("disabled", true);
                            }
                        }, 300);
                    }
                });
            } else {
                $('#modal_refer_line select').empty();
                if ($('#modal_item_code select').data('select2')) {
                    $('#modal_item_code select').select2('destroy');
                }
                $('#modal_item_code select').empty();
                $('#modal_supplier').val('');
                // $('#modal_customer_po_no').val('');
                $('#modal_original_currency').val('');
                $('#modal_uom').val('');
                $('#modal_category').val('');
                // $('#modal_item_code').val('');
                $('#modal_quantity').val('');
                $('#modal_price').val('');
                $('#modal_amount').val('0.00');
                $('#modal_backorder_qty').val('');
                $('#modal_w_date').val('');
                $('#modal_s_date').val('');
                $('#modal_remark').val('');

                $('#modal_item_code').empty();
                let part_number_id = 'id_select-' + dyn_tbl_sel_row_id + '-item_code';
                $('#'+part_number_id).removeAttr('disabled');
                partNumberSelect2(part_number_id, item_info, null);
                $('#id_select-' + dyn_tbl_sel_row_id + '-item_code').trigger('select2:open');
                current_code = $('#id_select-' + dyn_tbl_sel_row_id + '-item_code').val();
                line_object['part_item'] = current_code;
                $('#id_select-' + dyn_tbl_sel_row_id + '-item_code').select2('close');
                $('#id_select-' + dyn_tbl_sel_row_id + '-item_code')
                    .clone()
                    .attr('id', 'modal_part_item_code_select')
                    .attr('tabindex','0').appendTo('#modal_item_code');
                // $('#modal_item_code select').val($('#id_select-' + dyn_tbl_sel_row_id + '-item_code').val());
                if ($('#id_select-' + dyn_tbl_sel_row_id + '-item_code').val() !== null) {
                    setTimeout(function() {
                        $('#modal_item_code select').select2({
                            placeholder: 'Select Part No.',
                        });

                    }, 100);
                }
                else {
                    // Generate Select2 element
                    $('#modal_item_code select').select2({
                        placeholder: 'Select Part No.'
                    });
                }
                $('#modal_item_code select').val(current_code).trigger('change');
                $('#modal_item_code select').on("select2:open", function( event ){
                    prefill_select2(event);
                });

                bindItemCodeEvent();
            }
        });

        $('#modal_refer_line select').on("change", function( event ){

            // var msg = check_duplicate(dyn_tbl_sel_row_id);
            // if (msg != '') {
            //     pop_ok_dialog("Duplicate Row", msg, function(){});
            // } else {
            $('#modal_part_item_code_select').prop("disabled", false);
            let refer_line = $('#modal_refer_line select').find('option:selected').data('code_data');

            // let check_refer_number = $('#modal_ref_number select').val();
            // let line = editing_row.find('label:first').text();
            // storeCopyRefNumberData = saveCopyRefNumber(line, check_refer_number, refer_line, 'add', storeCopyRefNumberData, allVals);
            // getTotalInputQuantityDO


            // let remainQuantity = getRemainQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, allVals);
            // storeCopyRefNumberData = saveCopyRefNumberDO(line, check_refer_number, refer_line, 'add', storeCopyRefNumberData, allVals);
            for(var i=0; i<allVals.length; i++) {
                if(allVals[i].refer_line == refer_line) {
                    $('#modal_customer_po_no').val(allVals[i].customer_po_no);
                    $('#modal_supplier').val(allVals[i].supplier_code);
                    $('#modal_original_currency').val(allVals[i].currency);
                    $('#modal_uom').val(allVals[i].uom);
                    $('#modal_category').val(allVals[i].category);
                    // total_line_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, refer_line, PO_ROW_INDEX_ITEM_QTY, PO_SELECT_INDEX_REF_NUMBER, PO_SELECT_INDEX_REFER_LINE, allVals[i].order_quantity);
                    // if (remainQuantity == undefined) {
                        $('#modal_quantity').val(comma_format(allVals[i].order_quantity)).trigger('change');
                    // } else if (remainQuantity > 0) {
                    //     $('#modal_quantity').val(comma_format(remainQuantity)).trigger('change');
                    //     // storeCopyRefNumberData = updateQuantityCopyRefNumberDO(line, check_refer_number, refer_line, storeCopyRefNumberData, remainQuantity)
                    // } else {
                    //     $('#modal_quantity').val(comma_format(remainQuantity)).trigger('change');
                    // }

                    $('#modal_price').val(float_format(allVals[i].unit_price).toFixed(6));
                    $('#modal_backorder_qty').val(comma_format(allVals[i].backorder_qty));
                    $('#modal_remark').val(allVals[i].description);
                    $('#modal_w_date').val(allVals[i].wanted_date.split('-').reverse().join('-')).trigger('change');
                    $('#modal_s_date').val(allVals[i].schedule_date.split('-').reverse().join('-'));
                    $('#modal_w_date').attr('so_date', $('#modal_w_date').val());
                    $('#modal_s_date').attr('so_date', $('#modal_s_date').val());
                    if ($('#company_is_inventory').val() == 'True' && allVals[i].location_id){
                        if ($('#modal_location select').data('select2')) {
                            $('#modal_location select').select2('destroy');
                        }
                        $('#modal_location select').empty();
                        var options = '';
                        options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                        $('#modal_location select').append(options);
                        $('#modal_location select').select2();
                        $('#modal_location select').val(allVals[i].location_id).trigger('change');
                    }
                    var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true);
                    if (isNaN(amount)) amount = 0;
                    $('#modal_amount').val(comma_format(amount, decimal_place));

                    if ($('#modal_item_code select').data('select2')) $('#modal_item_code select').select2('destroy');
                    $('#modal_item_code select').empty();
                    var options = '<option data-code_data="['+  allVals[i].id+']" value="'+ allVals[i].id +'">'+allVals[i].item_code+'</option>';
                    $('#modal_item_code select').append(options);
                    $('#modal_item_code select').select2({});
                    $('#modal_item_code select').on("select2:open", function (event) {
                        prefill_select2(event);
                    });
                    $('#modal_item_code select').on("select2:close", function (event) {
                        $(this).closest('tr').find('input:eq('+PO_ROW_INDEX_CUSTOMER_PO+')').focus();
                    });
                    $('#modal_item_code select').val(allVals[i].id);

                    // if (remainQuantity > 0) {
                        $('#modal_quantity').removeClass('highlight-mandatory');
                    // }
                    is_modal_valid();
                }
            }
            // }
        });

        $('#modal_quantity').off('change, focusout').on('change, focusout', function(e) {
            var quantity_original = float_format($(this).attr('data-original'));
            var refer_line = $('#modal_refer_line_input').val();
            check_quantity_reference(refer_line, order_id, 'PO', e.target.id, quantity_original);
            if (float_format($(this).val()) > 0) {
                $(this).removeClass('highlight-mandatory');
            } else {
                $(this).addClass('highlight-mandatory');
            }

            $('#modal_quantity').val(comma_format(float_format($('#modal_quantity').val())));
            var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true);
            if (isNaN(amount)) amount = 0;
            $('#modal_amount').val(comma_format(float_format(amount).toFixed(decimal_place), decimal_place));
        });

        $('#modal_quantity').off('change').on('change', function (e) {
            if ($('#modal_ref_number select').val()) {
                return false;
            }

            var minoq = 0;
            try {
                minoq = float_format($('#modal_quantity').data().minoq);
            } catch {
                minoq = 0;
            }
            var quantity = float_format($('#modal_quantity').val());
            if (quantity > 0 && quantity < minoq) {
                 function cancel_function(){
                    $('#modal_quantity').val(comma_format(minoq, decimal_place)).trigger('keyup');
                    $('#modal_quantity').trigger('change');
                    $('#modal_quantity').select();
                }
                function ok_function(){
                    $('#modal_price').focus();
                }
                var selected_item = $('#modal_item_code select').find('option:selected').data('code_data')[0];
                pop_ok_cancel_dialog("",
                                     "Order Quantity ("+quantity+") of part number "+selected_item.code+
                                     " is less than it Minimum order Quantity ("+minoq+
                                     "). Continue anyway ?",
                                     ok_function,
                                     cancel_function,
                                     'No, reset to Minimum Order Quantity !');
            }
        })

        $('#modal_price').on('focus', function() {
            last_price = float_format($(this).val());
        })
        $('#modal_price').off('change, focusout').on('change, focusout', function() {
            if (float_format($(this).val()) > 0) {
                var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true);
                if (isNaN(amount)) amount = 0;
                $('#modal_amount').val(comma_format(amount, decimal_place));
                $('#modal_price').val(
                    comma_format(float_format($(this).val()), 6)
                );
                $(this).removeClass('highlight-mandatory');
            } else {
                $('#modal_price').val(
                    last_price.toFixed(6)
                );
                $(this).addClass('highlight-mandatory');
            }
        });

        $('#modal_customer_po_no').on('change, focusout', function() {
            if ($(this).val() != '') {
                $(this).removeClass('highlight-mandatory');
            } else {
                $(this).addClass('highlight-mandatory');
                return false;
            }

            if ($('#modal_item_code select').val() == '') {
                return false;
            }

            // has_location = false;
            // cur_loc= '';
            // c_line = $('#modal_line_number').val();
            // $cust_po_no = '#modal_customer_po_no';
            // current_so_doc_no = $('#id_document_number').val();
            // cuspo = $(this).val();
            // cusitem = $('#modal_item_code select').select2('data')[0].text;
            // cur_sup = $('#modal_supplier').val();
            // ref_number = $('#modal_ref_number select').val();
            // if ($('#company_is_inventory').val() == 'True') {
            //     has_location = true;
            //     cur_loc = $('#modal_location select').select2('data')[0].text;
            // }
            // var data = {
            //     'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            //     'cust_po_no': cuspo,
            //     'item_id': $('#modal_item_code select').val(),
            //     'type': 'PO',
            //     'ref_number': ref_number
            // };
            // $.ajax({
            //     url: '/orders/get_orderitems_by_cust_po_no/',
            //     type: 'POST',
            //     data: data,
            //     cache: false,
            // })
            // .done(function (data) {
            //     if (data.length != 0 && data[0].doc_no) {
            //         closeAllSelect2OnModal();
            //         if (has_location) {
            //             if (cur_loc == data[0].loc_code) {
            //                 var duplicate_data_list = [];
            //                 duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, cuspo, cur_sup, data[0].loc_code]);
            //                 duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, cur_loc]);
            //                 show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
            //             }
            //         } else {
            //             var duplicate_data_list = [];
            //             duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, cuspo, cur_sup, '']);
            //             duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, '']);
            //             show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
            //         }
            //     }
            // })
        });

        $('#modal_w_date').on('change', function() {
            if ($(this).val() != '') {
                $(this).removeClass('highlight-mandatory');
            } else {
                $(this).addClass('highlight-mandatory');
            }
        });

        // $('#modal_location select').on("select2:close", function (event) {
        //     $('#modal_quantity').focus();
        // });
    }

    function bindingItemCode(selectedRowId) {
        $('#modal_item_code').empty();
        let part_number_id = 'id_select-' + selectedRowId + '-item_code';
        if (!$('#'+part_number_id).data('select2')) {
            partNumberSelect2(part_number_id, item_info, null);
        }
        $('#id_select-' + selectedRowId + '-item_code').trigger('select2:open');
        current_code = $('#id_select-' + selectedRowId + '-item_code').val();
        line_object['part_item'] = current_code;
        $('#id_select-' + selectedRowId + '-item_code').select2('close');
        $('#id_select-' + selectedRowId + '-item_code')
            .clone()
            .attr('id', 'modal_part_item_code_select')
            .attr('tabindex','0').appendTo('#modal_item_code');
        $('#modal_item_code select').val($('#id_select-' + selectedRowId + '-item_code').val());
        if ($('#id_select-' + selectedRowId + '-item_code').val() !== null) {
            setTimeout(function() {
                // Generate Select2 element
                $('#modal_item_code select').select2({
                    // dropdownParent: $('#orderItemModal'),
                    placeholder: 'Select Part No.',
                });

                // Fix Select2 Style
                // $('#modal_item_code .select2-container span.select2-selection__rendered').css({
                //     // 'text-align': 'left',
                //     'font-size': '12.5px',
                //     'padding-top': '3px',
                //     'padding-bottom': '3px',
                // });

            }, 100);
        }
        else {
            // Generate Select2 element
            $('#modal_item_code select').select2({
                // dropdownParent: $('#orderItemModal'),
                placeholder: 'Select Part No.'
            });
        }
        $('#modal_item_code select').val(current_code).trigger('change');
        $('#modal_item_code select').on("select2:open", function( event ){
            prefill_select2(event);

            // Fix Select2 input search style
            // $('.select2-container input.select2-search__field').css({
            //     // 'text-align': 'left',
            //     'font-size': '12.5px',
            //     'padding-top': '3px',
            //     'padding-bottom': '3px',
            // });
        });

        bindItemCodeEvent();
    }


    function loadOrderItemModal_2(selectedRowId, addNew=false) {
        $('#loading').show();
        dyn_tbl_sel_row_id = selectedRowId;
        $('.highlight-mandatory').removeClass('highlight-mandatory');
        if (!addNew) {
             $('#modal_quantity').attr('data-original', '0');
            // selectedRowId++; // nth-child start with 1 not 0
            // store_current_row = $('#dynamic-table tr.gradeX:nth-child('+ (selectedRowId+1) +')');
            // var $current_row = $('#dynamic-table tr.gradeX:nth-child('+ (selectedRowId+1) +')').find('input');
            // var $labels = $('#dynamic-table tr.gradeX:nth-child('+ (selectedRowId+1) +')').find('label');
            // var $selects = $('#dynamic-table tr.gradeX:nth-child('+ (selectedRowId+1) +')').find('select');
            store_current_row = editing_row;
            var $current_row = store_current_row.find('input');
            var $labels = store_current_row.find('label');
            var $selects = store_current_row.find('select');

            if ($current_row.length == 0) {
                // When error, load previous row id
                editing_row = editing_row.prev();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId, false);
                return;
            }

            $('#modal_line_number').val($labels[PO_LABEL_INDEX_LINE_NUMBER].textContent);
            $('#modal_quantity').val($current_row[PO_ROW_INDEX_ITEM_QTY].value);
            $('#modal_backorder_qty').val($labels[PO_LABEL_INDEX_BACKORDER_QTY].textContent);

            // Part item location
            if ($('#company_is_inventory').val() == 'True') {
                $('#modal_location').empty();
                $('#id_formset_item-' + selectedRowId + '-location')
                    .clone()
                    .attr('id', 'id_modal_location_select')
                    .attr('tabindex','0')
                    .appendTo('#modal_location');
                $('#modal_location select').removeAttr( 'style' );
                $('#modal_location select').val($('#id_formset_item-' + selectedRowId + '-location').val());
                $('#modal_location select').select2();
                $('#modal_location select').on("select2:open", function (event) {
                    prefill_select2(event);
                });
            } else {
                $('#loc_item').css('display', 'none');
                $('#modal_location').css('display', 'none');
            }
            if($selects.length > 1) {
                // binding data for ref number
                if ($('#modal_ref_number select').data('select2')) {
                    $('#modal_ref_number select').select2('destroy');
                }
                $('#modal_ref_number').empty();
                $('#id_select-' + selectedRowId + '-ref_number').trigger('select2:open');
                $('#id_select-' + selectedRowId + '-ref_number')
                    .clone()
                    .attr('id', 'modal_ref_number_select')
                    .attr('tabindex','0').appendTo('#modal_ref_number');
                current_code = $('#id_select-' + selectedRowId + '-ref_number').val();
                line_object['ref_num'] = current_code;
                $('#modal_ref_number select').val($('#id_select-' + selectedRowId + '-ref_number').val());
                if ($('#id_select-' + selectedRowId + '-ref_number').val() !== null) {
                    setTimeout(function() {
                        // Generate Select2 element
                        $('#modal_ref_number select').select2({
                            // dropdownParent: $('#orderItemModal'),
                            placeholder: 'Select Ref Number',
                            allowClear: true,
                        });

                        // Fix Select2 Style
                        // $('#modal_ref_numer .select2-container span.select2-selection__rendered').css({
                        //     // 'text-align': 'left',
                        //     'font-size': '12.5px',
                        //     'padding-top': '3px',
                        //     'padding-bottom': '3px',
                        // });

                        // $('#modal_ref_number select').trigger('change');

                        setTimeout(function() {
                            if ($("#orderItemModal").is(':visible')) {
                                $('#modal_ref_number select').select2('open');
                                if ($('#id_select-' + selectedRowId + '-ref_number').val() !== '') {
                                    if ($('#id_select-'+dyn_tbl_sel_row_id+'-item_code option').length > 1) {
                                        $('#id_select-'+dyn_tbl_sel_row_id+'-item_code').select2('destroy');
                                        $('#id_select-'+dyn_tbl_sel_row_id+'-item_code').empty();
                                        if ($('#modal_item_code select').data('select2')) {
                                            $('#modal_item_code select').select2('destroy');
                                        }
                                        $('#modal_item_code select').empty();
                                        $('#modal_item_code select').prop("disabled", true);
                                    }
                                    
                                }
                            }
                        }, 300);
                    }, 100);
                }
                else {
                    // Generate Select2 element
                    $('#modal_ref_number select').select2({
                        // dropdownParent: $('#orderItemModal'),
                        placeholder: 'Select Ref Number'
                    });

                    // Fix Select2 Style
                    // $('#modal_ref_numer .select2-container span.select2-selection__rendered').css({
                    //     // 'text-align': 'left',
                    //     'font-size': '12.5px',
                    //     'padding-top': '3px',
                    //     'padding-bottom': '3px',
                    // });
                }
                $('#modal_ref_number select').val(current_code).trigger('change');
                $('#modal_ref_number select').on("select2:open", function( event ){
                    prefill_select2(event);

                    // Fix Select2 input search style
                    // $('.select2-container input.select2-search__field').css({
                    //     // 'text-align': 'left',
                    //     'font-size': '12.5px',
                    //     'padding-top': '3px',
                    //     'padding-bottom': '3px',
                    // });
                });

                // binding data for ref line
                if ($('#modal_refer_line select').data('select2')) {
                    $('#modal_refer_line select').select2('destroy');
                }

                $('#modal_refer_line').empty();
                $('#id_select-' + selectedRowId + '-refer_line').trigger('select2:open');
                current_code_l = $('#id_select-' + selectedRowId + '-refer_line').val();
                line_object['ref_line'] = current_code_l;
                $('#id_select-' + selectedRowId + '-refer_line').select2('close');
                $('#id_select-' + selectedRowId + '-refer_line')
                    .clone()
                    .attr('id', 'modal_refer_line_select')
                    .attr('tabindex','0').appendTo('#modal_refer_line');
                $('#modal_refer_line select').val($('#id_select-' + selectedRowId + '-refer_line').val());
                if ($('#id_select-' + selectedRowId + '-refer_line').val() !== null) {
                    setTimeout(function() {
                        // Generate Select2 element
                        $('#modal_refer_line select').select2({
                            // dropdownParent: $('#orderItemModal'),
                            placeholder: 'Ref Ln',
                        });

                        // Fix Select2 Style
                        // $('#modal_refer_line .select2-container span.select2-selection__rendered').css({
                        //     // 'text-align': 'left',
                        //     'font-size': '12.5px',
                        //     'padding-top': '3px',
                        //     'padding-bottom': '3px',
                        // });

                    }, 100);
                }
                else {
                    // Generate Select2 element
                    $('#modal_refer_line select').select2({
                        // dropdownParent: $('#orderItemModal'),
                        placeholder: 'Ref Ln'
                    });
                }
                $('#modal_refer_line select').val(current_code_l).trigger('change');
                $('#modal_refer_line select').on("select2:open", function( event ){
                    prefill_select2(event);

                    // Fix Select2 input search style
                    // $('.select2-container input.select2-search__field').css({
                    //     // 'text-align': 'left',
                    //     'font-size': '12.5px',
                    //     'padding-top': '3px',
                    //     'padding-bottom': '3px',
                    // });
                });

                // binding data for item code
                bindingItemCode(selectedRowId);
            } else {
                $('#modal_ref_number').empty();
                $('#modal_ref_number').html('<input id="modal_ref_number_input"  class="form-control" readonly="readonly" type="text" name="modal_ref_number_input"></input>');
                $('#modal_refer_line').empty();
                $('#modal_refer_line').html('<input id="modal_refer_line_input"  class="form-control" readonly="readonly" type="text" name="modal_refer_line_input"></input>');
                $('#modal_item_code').empty();
                $('#modal_item_code').html('<input id="modal_item_code_input"  class="form-control" readonly="readonly" type="text" name="modal_item_code_input"></input>');
                $('#modal_ref_number_input').val($('#id_formset_item-' + selectedRowId + '-ref_number').text());
                $('#modal_refer_line_input').val($('#id_formset_item-' + selectedRowId + '-refer_line').text());
                $('#modal_item_code_input').val($('#id_formset_item-' + selectedRowId + '-code').text());
                $('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
                setTimeout(function() {
                    $('#modal_customer_po_no').focus();
                }, 400);
            }

            if ($current_row[PO_ROW_INDEX_CUSTOMER_PO].value) {
                $('#modal_customer_po_no').val($current_row[PO_ROW_INDEX_CUSTOMER_PO].value);
            }

            line_object['cust_po'] = $('#modal_customer_po_no').val();
            line_object['w_date'] = $current_row[PO_ROW_INDEX_WANTED_FAKE_DATE].value;
            line_object['s_date'] = $current_row[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value;
            line_object['qty'] = $current_row[PO_ROW_INDEX_ITEM_QTY].value;
            line_object['price'] = $current_row[PO_ROW_INDEX_ITEM_PRICE].value
            line_object['remark'] = $current_row[PO_ROW_INDEX_DESCRIPTION].value

            $('#modal_backorder_qty').val($current_row[PO_ROW_INDEX_BACKORDER_QTY].value);
            $('#modal_supplier').val($current_row[PO_ROW_INDEX_SUPPLIER_CODE].value);
            $('#modal_uom').val($current_row[PO_ROW_INDEX_UOM].value);
            $('#modal_category').val($current_row[PO_ROW_INDEX_CATEGORY].value);

            $('#modal_w_date').val($current_row[PO_ROW_INDEX_WANTED_FAKE_DATE].value);
            $('#modal_original_currency').val($current_row[PO_ROW_INDEX_CURRENCY_CODE].value);

            $('#modal_quantity').val($current_row[PO_ROW_INDEX_ITEM_QTY].value);
            $('#modal_quantity').data('minoq', $current_row[PO_ROW_INDEX_MIN_ORDER_QTY].value)

            var modal_price = comma_format(float_format($current_row[PO_ROW_INDEX_ITEM_PRICE].value, 6), 6);
            $('#modal_price').val(modal_price);
            var modal_amount = float_format($('#id_formset_item-' + selectedRowId + '-amount').text(), 6)
            $('#modal_amount').val(comma_format(modal_amount, decimal_place));
            $('#modal_s_date').val($current_row[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value);
            $('#modal_remarks').val($current_row[PO_ROW_INDEX_DESCRIPTION].value);

            // store original Quantity
            // var is_database = $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId+1) + ')').attr('data-is_database');
            var is_database = store_current_row.attr('data-is_database');
            if (is_database != '' && is_database != undefined) {
                $('#modal_quantity').attr('data-original', $($current_row[PO_ROW_INDEX_ITEM_QTY]).closest('td').attr('data-original'));
            }
        }

        bindOrderModalEvent();
        controlPrevNextBtn();
        $('#loading').hide();
    }

    function is_modal_valid() {
        let valid = true;
        if ($('#modal_ref_number select').val() != '') {
            if ($('#modal_refer_line select').val() == '') {
                $($('#select2-modal_refer_line_select-container').parent('span')[0]).addClass('highlight-mandatory');
            } else {
                $($('#select2-modal_refer_line_select-container').parent('span')[0]).removeClass('highlight-mandatory');
            }
        }

        if ($('#modal_item_code select').val() === '' || $('#modal_item_code select').val() === null) {
            console.log('Error, item id empty');
            $($('#select2-modal_part_item_code_select-container').parent('span')[0]).addClass('highlight-mandatory');
            valid = false;
        } else {
            $($('#select2-modal_part_item_code_select-container').parent('span')[0]).removeClass('highlight-mandatory');
        }

        if ($('#modal_customer_po_no').val() === '') {
            console.log('Error, customer po empty');
            $('#modal_customer_po_no').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_customer_po_no').removeClass('highlight-mandatory');
        }
        if ($('#modal_w_date').val() === '') {
            console.log('Error, wanted date empty');
            $('#modal_w_date').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_w_date').removeClass('highlight-mandatory');
        }
        if ($('#modal_quantity').val() === '' || float_format($('#modal_quantity').val()) <= 0) {
            console.log('Error, quantity empty');
            $('#modal_quantity').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_quantity').removeClass('highlight-mandatory');
        }
        if ($('#modal_price').val() === '' || float_format($('modal_price').val()) <= 0) {
            console.log('Error, price empty');
            $('#modal_price').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_price').removeClass('highlight-mandatory');
        }
        return valid;
    }

    function bindDataToRow(modal_customer_po_no, modal_quantity, wanted_date, schedule_date, modal_remarks, modal_price, modal_location, rowIndex, modal_item_code) {
        $('#id_formset_item-' + rowIndex + '-customer_po_no').val(modal_customer_po_no);
        $('#modal_customer_po_no').val(modal_customer_po_no);
        // $('#id_formset_item-' + rowIndex + '-quantity').val(comma_format(modal_quantity)).trigger('change');
        $('#id_formset_item-' + rowIndex + '-quantity').val(comma_format(modal_quantity));
        if (float_format($('#id_formset_item-' + rowIndex + '-price')) != modal_price) {
            $('#id_formset_item-' + rowIndex + '-price').val(modal_price.toFixed(6)).trigger('change');
        }
        // var date_wanted_valid = moment(wanted_date, "DD-MM-YYYY", true).isValid();
        // var date_schedule_valid = moment(schedule_date, "DD-MM-YYYY", true).isValid();
        if (wanted_date) {
            $('#id_formset_item-' + rowIndex + '-wanted_fake_date').val(moment(wanted_date, "DD-MM-YYYY").format("DD-MM-YYYY"));
            $('#id_formset_item-' + rowIndex + '-wanted_date').val(moment(wanted_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
        }
        if (schedule_date) {
            $('#id_formset_item-' + rowIndex + '-schedule_fake_date').val(moment(schedule_date, "DD-MM-YYYY").format("DD-MM-YYYY"));
            $('#id_formset_item-' + rowIndex + '-schedule_date').val(moment(schedule_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
        } else {
            $('#id_formset_item-' + rowIndex + '-schedule_fake_date').val('');
            $('#id_formset_item-' + rowIndex + '-schedule_date').val('');
        }
        $('#id_formset_item-' + rowIndex + '-description').val(modal_remarks);
        if (modal_item_code == null) {
            $('#id_select-' + rowIndex + '-item_code').val('').trigger('change');
            $('#id_formset_item-' + rowIndex + '-code').val('');
        }

        if ($('#company_is_inventory').val() == 'True') {
            $('#id_formset_item-' + rowIndex + '-location').val(modal_location).trigger('change');
        }
    }

    function check_duplicate(row_id) {
        var msg = '';
        $('#dynamic-table tr.gradeX').each(function () {
            let modal_ref_number = $('#modal_ref_number select').val();
            let modal_refer_line = $('#modal_refer_line select').val();
            // let rowIndex = parseInt($(this).closest('tr').find('label:first').text()) - 1;
            let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let ref_number = '';
            let refer_line = '';
            try {
                let selects = $(this).closest('tr').find('select');
                ref_number = selects[PO_SELECT_INDEX_REF_NUMBER].value;
                refer_line = selects[PO_SELECT_INDEX_REFER_LINE].value;
            }catch (e) {
                ref_number = $('#id_formset_item-' + rowIndex + '-ref_number').text();
                refer_line = $('#id_formset_item-' + rowIndex + '-refer_line').text();
            }
            if (modal_ref_number == ref_number && modal_refer_line==refer_line && rowIndex !=row_id ) {
                msg = 'Duplicate entry at row number '+(rowIndex+1)+'<br/>Refer no: '+modal_ref_number+'<br/>Refer ln: '+modal_refer_line;
            }
        });
        return msg;
    }

    function saveOrderItemModal(selectedRowId) {
        let modal_ref_number = $('#modal_ref_number select').val();
        let modal_refer_line = $('#modal_refer_line select').val();
        let modal_item_code = $('#modal_item_code select').val();
        let modal_customer_po_no = $('#modal_customer_po_no').val();
        let modal_quantity = float_format($('#modal_quantity').val());
        let modal_price = float_format($('#modal_price').val());
        let wanted_date = $('#modal_w_date').val();
        let schedule_date = $('#modal_s_date').val();
        let modal_remarks = $('#modal_remarks').val();
        let modal_location = '';
        if ($('#company_is_inventory').val() == 'True') {
            modal_location = $('#modal_location select').val();
        }

        $('#loading').show();
        if (modal_ref_number != '') {
            let selected_ref_num = line_object['ref_num'];
            let selected_ref_line = line_object['ref_line'];
            if (selected_ref_num != $('#modal_ref_number select').val()
                && $('#modal_ref_number select').val() != undefined) {
                $('#id_select-' + selectedRowId + '-ref_number').val(modal_ref_number).trigger('change');
            }
            //$('#id_select-' + selectedRowId + '-ref_number').val(modal_ref_number).trigger('change');
            setTimeout(function() {
                if (modal_refer_line != '') {
                    if (selected_ref_num != $('#modal_ref_number select').val()) {
                        if ($('#modal_refer_line select').val()
                            && $('#modal_refer_line select').val() != undefined) {
                            $('#id_select-' + selectedRowId + '-refer_line').val(modal_refer_line).trigger('change');
                        }
                    } else if (selected_ref_line != $('#modal_refer_line select').val()) {
                        if ( $('#modal_refer_line select').val()
                            && $('#modal_refer_line select').val() != undefined) {
                            $('#id_select-' + selectedRowId + '-refer_line').val(modal_refer_line).trigger('change');
                        }
                    }
                } else {
                    $('#id_select-' + selectedRowId + '-item_code').val(modal_item_code).trigger('change');
                }
                setTimeout(function() {
                    bindDataToRow(modal_customer_po_no, modal_quantity,
                        wanted_date, schedule_date, modal_remarks, modal_price, modal_location, selectedRowId, modal_item_code);
                    $('#loading').hide();
                }, 600);
            }, 1000);
        } else {
            $('#id_select-' + selectedRowId + '-ref_number').val('').trigger('change');
            $('#id_select-' + selectedRowId + '-item_code').val(modal_item_code).trigger('change');
            setTimeout(function() {
                bindDataToRow(modal_customer_po_no, modal_quantity, wanted_date, schedule_date, modal_remarks, modal_price, modal_location, selectedRowId, modal_item_code);
                // $('#loading').hide();
            }, 600);
        }
    }

    function controlPrevNextBtn() {
        // disable or enable pre button
        if ((editing_row.prev()).length) {
            $('#btnOrderItemPrev').attr('disabled', false);
        } else {
            $('#btnOrderItemPrev').attr('disabled', true);
        }

        // disable or enable next button
        if (editing_row.next().hasClass('gradeX')) {
            $('#btnOrderItemNext').attr('disabled', false);
        } else {
            $('#btnOrderItemNext').attr('disabled', true);
        }
    }

    function is_change() {
        var flag_change = false;

        // PO
        if (line_object['ref_num'] != $('#modal_ref_number_select').val()
            && $('#modal_ref_number_select').val() != undefined) {
            flag_change = true;
        }

        if (line_object['ref_line'] != $('#modal_refer_line_select').val()
            && $('#modal_refer_line_select').val() != undefined) {
            flag_change = true;
        }

        // SO
        if (line_object['part_item'] != $('#modal_part_item_code_select').val()
            && $('#modal_part_item_code_select').val() != undefined) {
            flag_change = true;
        }
        if (line_object['cust_po'] != $('#modal_customer_po_no').val()) {
            flag_change = true;
        }
        if (line_object['w_date'] != $('#modal_w_date').val()) {
            flag_change = true;
        }
        if (line_object['qty'] != $('#modal_quantity').val()) {
            flag_change = true;
        }
        if (line_object['price'] != float_format($('#modal_price').val())) {
            flag_change = true;
        }
        if (line_object['remark'] != $('#modal_remarks').val()) {
            flag_change = true;
        }
        if (line_object['s_date'] != $('#modal_s_date').val()) {
            flag_change = true;
        }

       return flag_change;
    }

    function itemNewRow() {
        var selectedRowId = dyn_tbl_sel_row_id;
        var ok = $.checkOrderRowValidity(selectedRowId);
        if (ok) {
            // saveOrderItemModal(selectedRowId);
            var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
            setTimeout(() => {
                var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
                editing_row = $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }, 500);
        }
        else {
            // var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            // $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
            // $('#dynamic-table tr.gradeX:nth-child(' + (rowCount-1) + ')').find('.appendrow').trigger('click');
            // setTimeout(() => {
            //     loadOrderItemModal_2(rowCount-1);
            // }, 500);
            $('#comfirmSaveNewOrderModal').modal('show');
        }
    }

    function removeLine() {
        try{
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#modal_item_code select').select2('close');
        } catch(e) {
            console.log(e)
        }
        var selectedRowId = parseInt(editing_row.find('label:first').text());
        editing_row.find('.removerow').trigger('click');
        setTimeout(() => {
            if (selectedRowId > 1) {
                editing_row = $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId-1) + ')');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            } else {
                editing_row = $('#dynamic-table tr.gradeX:nth-child(1)');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }
        }, 800);
    }

    function orderItemCancel() {
        try{
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#modal_item_code select').select2('close');
        } catch(e) {
            console.log(e)
        }
        if (is_change()) {
            next = false;
            prev = false;
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            var selectedRowId = dyn_tbl_sel_row_id;
            var ok = $.checkOrderRowValidity(selectedRowId);
            if (!ok) {
                // reset line
                var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
                selectedRowId = parseInt(editing_row.find('label:first').text()) - 1;
                if (selectedRowId == rowCount - 1 && rowCount != 1) {
                    next_prev_action();
                    $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                } else if (selectedRowId == rowCount - 1 && rowCount == 1) {
                    next_prev_action();
                    $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                    setTimeout(() => {
                        $('#dynamic-table tr.gradeX:nth-child(' + (rowCount-1) + ')').find('.appendrow').trigger('click');
                    }, 600);
                }
            }
            $('#orderItemModal').modal('hide');
        }
    }

    function resetLine() {
        var is_database = editing_row.attr('data-is_database');
        var selectedRowId = parseInt(editing_row.find('label:first').text()) - 1;
        if (is_database == '' || is_database == undefined) {
            var ok = is_modal_valid();
            if (!ok) {
                // reset line
                var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
                if (selectedRowId == rowCount - 1 && rowCount != 1) {
                    next_prev_action();
                    $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                } else if (selectedRowId == rowCount - 1 && rowCount == 1) {
                    next_prev_action();
                    $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                    setTimeout(() => {
                        $('#dynamic-table tr.gradeX:nth-child(' + (rowCount-1) + ')').find('.appendrow').trigger('click');
                    }, 600);
                }
            } else {
                // rollBack_data();
                var ok = $.checkOrderRowValidity(selectedRowId);
                if (!ok) {
                    // reset line
                    var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
                    if (selectedRowId == rowCount - 1 && rowCount != 1) {
                        next_prev_action();
                        $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                    } else if (selectedRowId == rowCount - 1 && rowCount == 1) {
                        next_prev_action();
                        $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
                        setTimeout(() => {
                            $('#dynamic-table tr.gradeX:nth-child(' + (rowCount-1) + ')').find('.appendrow').trigger('click');
                            next_prev_action();
                        }, 600);
                    }
                }
                // process_button(selectedRowId)
            }
        } else {
            // rollBack_data();
            process_button(selectedRowId)
        }
    }

    function process_button(selectedRowId) {
        switch(action_button) {
          case 'cancel':
            // code block
            $('#orderItemModal').modal('hide');
            break;
          case 'prev':
            if ((editing_row.prev()).length) {
                editing_row = editing_row.prev();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }
            break;
          case 'next':
            if (editing_row.next().hasClass('gradeX')) {
                editing_row = editing_row.next();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }
            break;
          default:
            action_button = ''
        }
    }


    // function rollBack_data() {
    //     if (is_change()) {
    //         // PO
    //         $('#loading').modal('show');
    //         $('#modal_ref_number_select').val(line_object['ref_num']).trigger('change');
    //
    //         setTimeout(() => {
    //             $('#modal_refer_line_select').val(line_object['ref_line']).trigger('change');
    //         }, 1000);
    //
    //         setTimeout(() => {
    //             $('#modal_part_item_code_select').val(line_object['part_item']);
    //             $('#modal_refer_line_select').select2('close');
    //             $('#modal_part_item_code_select').select2('close');
    //             $('#modal_customer_po_no').val(line_object['cust_po']);
    //             $('#modal_w_date').val(line_object['w_date']);
    //             $('#modal_quantity').val(line_object['qty']);
    //             $('#modal_price').val(line_object['price']);
    //             $('#modal_remarks').val(line_object['remark']);
    //             $('#modal_s_date').val(line_object['s_date']);
    //             selectedRowId = dyn_tbl_sel_row_id;
    //             saveOrderItemModal(selectedRowId);
    //             $('#loading').modal('hide');
    //             process_button(selectedRowId);
    //         }, 1500);
    //     }
    // }
});

$('#orderItemModal').on('shown.bs.modal', function () {
    $.getJSON(url_get_item_backorder+'?item_id='+$('#modal_item_code select').val(), function(data) {
        var backorder_qty = 0;

        if (data.length > 0) {
            backorder_qty = data[0].rfs_qty;
        }

        $('#modal_backorder_qty').val(backorder_qty);
    });

    // $('#modal_location select').focus();
})

function changeCurrency(arrItems, currency_id, currency_name) {
    if (arrItems["item_id"] != undefined && arrItems["currency_id"] != undefined) {
        $.ajax({
            method: "POST",
            url: '/orders/load_currency/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'arrItems': JSON.stringify(arrItems),
                'currency_id': currency_id,
            },
            success: function (json) {
                var item_currency_not_match = [];
                var sale_price = 0;
                var amount = 0;
                var purchase_price = 0;
                for (var i in json) {
                    if (json[i].constructor === Object) {
                        $('#dynamic-table tr.gradeX').each(function () {
                            var currentRow = $(this).closest('tr').find('input');
                            var currentLabel = $(this).closest('tr').find('label');
                            var currentItem = currentRow[PO_ROW_INDEX_ITEM_NAME].value;
                            if (currentRow[PO_ROW_INDEX_ITEM_ID].value == json[i].id) {

                                if (json[i].rate == 0 || json[i].sale_price == "") {
                                    item_currency_not_match.push('Can not get Exchange Rate from ' + json[i].currency + ' to ' + currency_name);
                                    currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value = 0;
                                    currentRow[PO_ROW_INDEX_AMOUNT].value = 0;
                                    if(json[i].currency != 'NONE') {
                                        $('.lblCurrency').text(json[i].currency);
                                    }
                                } else {
                                    sale_price = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value);
                                    currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value = float_format(json[i].rate).toFixed(10);
                                    amount = json[i].rate * sale_price;
                                    currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(amount, decimal_place);
                                    $('.lblCurrency').text(json['symbol']);
                                }
                                currentLabel[PO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[PO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
                            }
                        });
                    }
                };

                if (item_currency_not_match.length > 0) {
                    $("#currency_error").text("");
                    var uniqueNames = [];
                    $.each(item_currency_not_match, function (i, el) {
                        if ($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
                    });
                    for (i = 0; i < uniqueNames.length; i++) {
                        document.getElementById('currency_error').innerHTML += uniqueNames[i] + '<br>';
                    }
                    $('#currency_error').removeAttr('style');
                    fnDisableButton();
                    $('#dynamic-table tr.gradeX').each(function () {
                        $(this).closest('tr').find('input').attr('disabled', true);
                    });
                } else {
                    $('#currency_error').css('display', 'none');
                    fnEnableButton();
                    $('#dynamic-table tr.gradeX').each(function () {
                        $(this).closest('tr').find('input').removeAttr('disabled');
                    });
                }
            }
        });
    }

};

function changeCurrency_2(arrItems, currency_id, currentRow, currency_name) {
    var doc_date = $('#id_document_date').val();
    if (arrItems[0].item_id != undefined &&
        arrItems[0].currency_id != undefined &&
        arrItems[0].item_id != '' &&
        arrItems[0].currency_id != '') {
        $.ajax({
            method: "POST",
            url: '/orders/load_currency/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'arrItems': JSON.stringify(arrItems),
                'currency_id': currency_id,
                'doc_date': doc_date
            },
            success: function (json) {
                var item_currency_not_match = [];
                var sale_price = 0;
                var amount = 0;
                var purchase_price = 0;
                for (var i in json) {
                    if (json[i].constructor === Object) {
                        if (currentRow[PO_ROW_INDEX_ITEM_ID].value == json[i].id) {
                            if (json[i].rate == 0 || json[i].sale_price == "") {
                                item_currency_not_match.push('Can not get Exchange Rate from ' + json[i].currency + ' to ' + currency_name);
                                currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value = 0;
                                currentRow[PO_ROW_INDEX_AMOUNT].value = 0;
                                // if(json[i].currency != 'NONE') {
                                //     $('.lblCurrency').text(json[i].currency);
                                // } else {
                                $('.lblCurrency').text(json['symbol']);
                                // }
                            } else {
                                sale_price = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value);
                                currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value = float_format(json[i].rate).toFixed(10);
                                // amount = json[i].rate * sale_price;
                                // currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(amount, decimal_place);
                                $('.lblCurrency').text(json['symbol']);
                            }
                            // currentLabel[PO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[PO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
                        }
                    }
                };

                if (item_currency_not_match.length > 0) {
                    $("#currency_error").text("");
                    var uniqueNames = [];
                    $.each(item_currency_not_match, function (i, el) {
                        if ($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
                    });
                    for (i = 0; i < uniqueNames.length; i++) {
                        document.getElementById('currency_error').innerHTML += uniqueNames[i] + '<br>';
                    }
                    $('#currency_error').removeAttr('style');
                    fnDisableButton();
                    $('#dynamic-table tr.gradeX').each(function () {
                        $(this).closest('tr').find('input').attr('disabled', true);
                    });
                } else {
                    $('#currency_error').css('display', 'none');
                    fnEnableButton();
                    $('#dynamic-table tr.gradeX').each(function () {
                        $(this).closest('tr').find('input').removeAttr('disabled');
                    });
                }
            }
        });
    }

};

function supplier_items() {
    var supplier_id = $('#id_supplier').val();
    var exclude_item_array = [];
    var exclude_item_list = {};
    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        var currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[PO_ROW_INDEX_ITEM_ID].value);
        }
    });
    if (exclude_item_array.length > 0) {
        exclude_item_list = JSON.stringify(exclude_item_array);
    }

    var datatbl = $('#tblData').DataTable();
    datatbl.destroy();
    var list_url = $('#list_url').text();
    $('#tblData').DataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[1, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": list_url,
            "data": {
                "csrfmiddlewaretoken": $('input[name="csrfmiddlewaretoken"]').val(),
                "supplier_id": supplier_id,
                "exclude_item_list": exclude_item_list
            }
        },
        "rowId": "line_id",
        "columns": [
            {
                "data": "item_id",
                "className": "hide_column"
            },
            {"data": "item_name", "sClass": "text-left"},
            {"data": "supplier_code", "sClass": "text-left"},
            {"data": "refer_number", "sClass": "text-left"},
            {"data": "refer_line", "sClass": "text-left"},
            {"data": "location_code", "sClass": "text-left"},
            {"data": "code", "sClass": "text-left"},
            {"data": "category", "sClass": "text-left"},
            {"data": "new_price", "sClass": "text-right"},
            {"data": "currency_code", "sClass": "text-left"},
            {"data": "location_id", "className": "hide_column"},
            {"data": "currency_id", "className": "hide_column"},
            {"data": "line_id", "className": "hide_column"},
            {"data": "unit", "className": "hide_column"},
            {"data": "supplier_id", "className": "hide_column"},
            {"data": "minimun_order", "className": "hide_column"},
            {"data": "refer_id", "className": "hide_column"},
            {"data": "customer_po_no", "className": "hide_column"},
            {"data": "default_location_id", "className": "hide_column"},
            {"data": "purchase_price", "className": "hide_column"},
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, row, meta) {
                    return '<input type="checkbox" name="choices" id="' + row.line_id + '"'
                        + 'class="call-checkbox" value="' + row.purchase_price + '"></td>';
                }
            }
        ]
    });
}

$('#id_exchange_rate').on('change', function () {
    $('#id_exchange_rate_value').val($(this).val());
});

$('#id_document_date_fake').click(function () {
    $(this).select();
});

// event change currency
$('#id_currency').change(function (e) {
    var currency_id = parseInt($(this).val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        if(currentRow[PO_ROW_INDEX_ITEM_ID].value) {
            arrItems.push({
                item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
                currency_id: currency_id
            });
        }
    });
    changeCurrency(arrItems, currency_id, currency_name);
});


// $(document).ready(function () {
//     $('#dynamic-table tr.gradeX:last').each(function () {
//         calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
//     });
// })

//event handle calculate subtotal and total base on quantity
function handleQuantity() {
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        $ItemQty = '#' + currentRow[PO_ROW_INDEX_ITEM_QTY].id;
        quantityEvent($ItemQty);

        $priceElement = '#' + currentRow[PO_ROW_INDEX_ITEM_PRICE].id;
        unitPriceEvent($priceElement)

        $lastElement = '#' + currentRow[PO_ROW_INDEX_DESCRIPTION].id;
        lastElementEvent($lastElement);

        $custNoElement = '#' + currentRow[PO_ROW_INDEX_CUSTOMER_PO].id;
        custNoElementEvent($custNoElement);
    });
}

function lastElementEvent($lastElement) {
    $($lastElement).off('keydown').on("keydown", function (e) {
        if (e.which == 9) {
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            var idFirstInvalid = getFirstFieldInvalid(rowCheck);
            if (idFirstInvalid != '') {
                highLightMandatory(rowCheck);
                pop_focus_invalid_dialog('Invalid Data',
                'Please fill up the required fields.',
                function(){
                    $(idFirstInvalid).focus();
                    if ($(idFirstInvalid).is('select')) {
                        $(idFirstInvalid).select2('open');
                    }
                });
            } else {
                // just tab key
                let code_pressed = e.keyCode || e.which;
                let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
                console.log('rowLabel', rowIndex);
                tabAddRow(rowIndex, code_pressed);
            }
        }
    });
}

function custNoElementEvent($custNoElement) {
    $($custNoElement).off('change').on("change", function (e) {
        if ($(this).val() != '' ) {
            $(this).removeClass('highlight-mandatory');
        } else {
            $(this).addClass('highlight-mandatory');
            return false;
        }
        var cRow = $(this).closest('tr').find('input');

        if (cRow[PO_ROW_INDEX_ITEM_ID].value == '') {
            return false;
        }

        // var cLabel = $(this).closest('tr').find('label');
        // var ref_number = $($(this).closest('tr').find('select')[PO_SELECT_INDEX_REF_NUMBER]).val();
        // var cpo = cRow[PO_ROW_INDEX_CUSTOMER_PO].value;
        // var citem = cRow[PO_ROW_INDEX_CODE].value;
        // var csup = $('#id_supplier option:selected').text();
        // var line = parseInt(cLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent) - 1;
        // var loc = '';
        // var has_location = false;
        // if ($('#company_is_inventory').val() == 'True') {
        //     // $l_select = '#' + $(this).closest('tr').find('select')[PO_SELECT_INDEX_LOCATION].id;
        //     loc = $('#id_formset_item-' + line + '-location').select2('data')[0].text;
        //     has_location = true;
        // }
        // var data = {
        //     'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
        //     'cust_po_no': cpo,
        //     'item_id': cRow[PO_ROW_INDEX_ITEM_ID].value,
        //     'type': 'PO',
        //     'ref_number': ref_number
        // };
        // $.ajax({
        //     url: '/orders/get_orderitems_by_cust_po_no/',
        //     type: 'POST',
        //     data: data,
        //     cache: false,
        // })
        // .done(function (data) {
        //     if (data.length != 0 && data[0].doc_no) {
        //         var duplicate_data_list = [];
        //         if (has_location) {
        //             if (loc == data[0].loc_code) {
        //                 duplicate_data_list.push([data[0].ln_no, data[0].doc_no, citem, cpo, csup, data[0].loc_code]);
        //                 duplicate_data_list.push([cLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, loc]);
        //                 if (!$("#orderItemModal").is(':visible')) {
        //                     show_duplicate_cuspo_modal(duplicate_data_list, $custNoElement, has_location, true);
        //                 }
        //             }
        //         } else {
        //             duplicate_data_list.push([data[0].ln_no, data[0].doc_no, citem, cpo, csup, '']);
        //             duplicate_data_list.push([cLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, '']);
        //             if (!$("#orderItemModal").is(':visible')) {
        //                 show_duplicate_cuspo_modal(duplicate_data_list, $custNoElement, has_location, true);
        //             }
        //         }
        //     }
        // });
    });
}

function quantityEvent($ItemQty) {
    $($ItemQty).off('change').on('change', function (e) {
        var currentLabel = $(this).closest('tr').find('label');
        var quantity_original = float_format($(this).closest('td').attr('data-original'));
        var refer_line = $(currentLabel[PO_ROW_INDEX_REFER_LINE]).text();
        check_quantity_reference(refer_line, order_id, 'PO', e.target.id, quantity_original);

        var currentRow = $(this).closest('tr').find('input');
        var selects = $(this).closest('tr').find('select');

        var code = currentRow[PO_ROW_INDEX_CODE].value;
        var quantity = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value);
        var minoq = float_format(currentRow[PO_ROW_INDEX_MIN_ORDER_QTY].value);
        var price = float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value);

        currentRow[PO_ROW_INDEX_ITEM_QTY].value = comma_format(quantity);
        //var price = currentRow[PO_ROW_INDEX_ITEM_PRICE].value;
        // refer_line = $('#' + selects[PO_SELECT_INDEX_REFER_LINE].id).val();

        // if (refer_line && float_format(quantity) > float_format(total_line_quantity) && float_format(total_line_quantity) > 0 ) {
        //     console.log(refer_line);
        //     pop_ok_dialog("Invalid Quantity",
        //     "The quantity of product "+ code +" must not be greater than (" + total_line_quantity + ") qty",
        //     function(){
        //             $ItemQty = '#' + e.target.id;
        //             $($ItemQty).select();
        //     });
        //
        //     $('#'+e.target.id).val(comma_format(total_line_quantity));
        //     $('#dynamic-table tr.gradeX').each(function () {
        //         recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, undefined, decimal_place);
        //     });
        // } else
        if (float_format(quantity) < float_format(minoq) && float_format(quantity) > 0) {
            let row = parseInt($(this).closest('tr').attr('data-row_index'));
            var nextElm = '#id_formset_item-' + row + '-price';
            //$('#'+currentRow[PO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place)).trigger('change');
            let last_amount = float_format($('#id_formset_item-'+row+'-amount').text());
            //currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
            $('#id_formset_item-'+row+'-amount').val(roundDecimal(quantity * price, decimal_place)).trigger('change');
            $('#id_formset_item-'+row+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
            let new_amount = roundDecimal(quantity * price, decimal_place);
            calculatePOTotal(last_amount, new_amount);

            $(this).closest('tr').removeAttr('style');
            fnEnableButton();
            // currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(quantity, 2);
            $(this).val(comma_format(quantity));
            WarnLessThanMinOrder(code,quantity,minoq,this, nextElm);
        } else if (float_format(quantity) <= 0) {
            pop_ok_dialog("Invalid Quantity",
            "The quantity of product "+ code +" must be greater than 0",
            function(){
                    $ItemQty = '#' + e.target.id;
                    $($ItemQty).select();
            });

            // $('#'+e.target.id).val('0.00');
            // $('#dynamic-table tr.gradeX').each(function () {
            //     recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, undefined, decimal_place);
            // });
        } else if (float_format(quantity) > 0) {
            // $('#dynamic-table tr.gradeX').each(function () {
            //     recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, undefined, decimal_place);
            //     $(this).closest('tr').find('input').removeAttr('disabled');
            // });
            $(this).closest('tr').removeAttr('style');
            fnEnableButton();
            let row = parseInt($(this).closest('tr').attr('data-row_index'));
            let last_amount = float_format($('#id_formset_item-'+row+'-amount').text());
            //currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
            $('#id_formset_item-'+row+'-amount').val(roundDecimal(quantity * price, decimal_place)).trigger('change');
            $('#id_formset_item-'+row+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
            let new_amount = roundDecimal(quantity * price, decimal_place);
            calculatePOTotal(last_amount, new_amount);
            // calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);

            let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let check_refer_number = $($(this).closest('tr').find('select')[PO_SELECT_INDEX_REF_NUMBER]).val();
            let check_refer_line = $($(this).closest('tr').find('select')[PO_SELECT_INDEX_REFER_LINE]).val();

            if (check_refer_number == undefined || check_refer_line == undefined) {
                check_refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').text();
                check_refer_line = $('#id_formset_item-' + (rowIndex) +'-refer_line').text();
            }
            let idx = $(this).closest('tr').find('label:first').text();
            storeCopyRefNumberData = updateQuantityCopyRefNumberDO(idx, check_refer_number, check_refer_line, storeCopyRefNumberData, $(this).val());
        }
        let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
        highLightMandatory(rowCheck);
    });
    $($ItemQty).click(function () {
        $(this).select();
    });
}

// event change price
var last_price = 0.00;
function unitPriceEvent($priceElement) {

    $($priceElement).on('focus', function (e) {
        last_price = float_format($(this).val());
    })
    $($priceElement).off('change').on('change', function (e) {
        var currentRow = $(this).closest('tr').find('input');
        // $('#'+ currentRow[PO_ROW_INDEX_AMOUNT].id).val(roundDecimal(float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value) *
        //                                        float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value) *
        //                                        float_format(currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value), decimal_place)).trigger("change");
        if (currentRow[PO_ROW_INDEX_ITEM_PRICE].value > 0) {
            $('#validate_error').css('display', 'none');
            currentRow.parents('tr').removeAttr('style');

            // $('#dynamic-table tr.gradeX').each(function () {
            //     recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT);
            //     $(this).closest('tr').find('input').removeAttr('disabled');
            // });
            $('#validate_error').css('display', 'none');
            fnEnableButton();
            let quantity = float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value);
            let price = float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value);
            let row = parseInt($(this).closest('tr').attr('data-row_index'));
            let last_amount = float_format($('#id_formset_item-'+row+'-amount').text());
            // currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
            $('#id_formset_item-'+row+'-amount').val(roundDecimal(quantity * price, decimal_place)).trigger('change');
            $('#id_formset_item-'+row+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
            let new_amount = roundDecimal(quantity * price, decimal_place);
            calculatePOTotal(last_amount, new_amount);
            // calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
            // validationItemsFormset();
        } else {
            pop_ok_dialog("Invalid Price",
              "Price of product must be greater than 0",
              function(){
                // $('#dynamic-table tr.gradeX').each(function () {
                    // recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT);
                // });
                setTimeout(function() {
                    $Target = '#' + e.target.id;
                    $($Target).val(last_price.toFixed(6)).trigger('change');
                    $($Target).select();
                }, 300);
            });
        }
        let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
        highLightMandatory(rowCheck);
        $(this).val(float_format($(this).val()).toFixed(6));
    });
    $($priceElement).click(function () {
        $(this).select();
    });
}

// event change exchange rate
$('#dynamic-table tr.gradeX').find('input').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    $exchangeRate = '#' + currentRow[PO_ROW_INDEX_EXCHANGE_RATE].id;
    $($exchangeRate).change(function (e) {
        var currentRow = $(this).closest('tr').find('input');
        var exchange_rate = currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value;
        var price = currentRow[PO_ROW_INDEX_ITEM_PRICE].value;
        var quantity = currentRow[PO_ROW_INDEX_ITEM_QTY].value;
        if (exchange_rate <= 0) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The exchange rate of product ' + currentRow[PO_ROW_INDEX_CODE].value + ' must be greater than 0');
            $(this).closest('tr').attr('style', 'background-color: red !important');
            $('#'+currentRow[PO_ROW_INDEX_AMOUNT].id).val(0.00).trigger('change');
            fnDisableButton();
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[PO_ROW_INDEX_EXCHANGE_RATE]).attr('disabled', true);
            });
        } else {
            $('#'+currentRow[PO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity * exchange_rate), decimal_place).trigger('change');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $('#minimum_order_error').css('display', 'none');
            $(this).closest('tr').removeAttr('style');
            fnEnableButton();
        }
    });
    $($exchangeRate).click(function () {
        $(this).select();
    });
});


$(document).ready(function () {
    var order_id = $('#order_id').text();
    if (order_id != "") {
        var currency_id = $('#id_currency').val();
        var currency_name = $('#id_currency option:selected').text();
        var arrItems = [];
        $('#dynamic-table tr.gradeX').each(function () {
            var currentRow = $(this).closest('tr').find('input');
            arrItems.push({
                item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
                currency_id: currentRow[PO_ROW_INDEX_CURRENCY_ID].value
            });
            initial_item_qty.push({
                ln: currentRow[PO_ROW_INDEX_LINE_NUMBER].value,
                item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
                qty: float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value),
                refer_doc: currentRow[PO_ROW_INDEX_REFER_NO].value,
                refer_line: currentRow[PO_ROW_INDEX_REFER_LINE].value,
            });
            set_order_item_dates();
        });
        $('#initial_item_qty_data').val(JSON.stringify(initial_item_qty));
    }
    $('#btnSearchItem').on('click', function () {
        supplier_items();
    });
    $('#btnOpenItemDialog').on('click', function () {
        var dataTable = $('#tblData').dataTable();
        dataTable.fnClearTable(this);
        supplier_items();
    });
});

//Load tax rate
$(document).ready(function () {
    $('#id_tax').change(function (e) {
        var taxid = parseInt($(this).val());
        if (isNaN(taxid)) {
            $('#id_tax_amount').val(0);
            $('#id_total').val(float_format($('#id_tax_amount').val()) + float_format($('#id_subtotal').val()));
        } else {
            $.ajax({
                method: "POST",
                url: '/orders/load_tax/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'tax_id': taxid,
                },
                success: function (json) {
                    var tax_amount = (float_format(json) * float_format($('#id_subtotal').val())) / 100;
                    $('#hdTaxRate').val(float_format(json));
                    $('#id_tax_amount').val(comma_format(float_format(tax_amount.toFixed(decimal_place)), decimal_place));
                    var total = float_format($('#id_subtotal').val()) + tax_amount;
                    $('#id_total').val(comma_format(float_format(total.toFixed(decimal_place)), decimal_place));
                }
            });
        }
    });
});

//event handle for input discount
$('#id_discount').change(function (e) {
    if ($(this).val() != '') {
        var sum = float_format($('#id_subtotal').val()) + float_format($('#id_tax_amount').val());
        sum -= parseInt(this.value);
        $('#id_total').val(sum);
    } else {
        var sum = 0;
        $('#dynamic-table tr.gradeX').each(function () {
            var currentRow = $(this).find('input');
            amount = currentRow[PO_ROW_INDEX_AMOUNT].value;
            sum += parseInt(amount).toFixed(decimal_place);
            sum = roundDecimal(sum, decimal_place)
            $('#id_subtotal').val(comma_format(sum, decimal_place));
            var total = sum + float_format($('#id_tax_amount').val())
            total = roundDecimal(total, decimal_place);
            $('#id_total').val(comma_format(total, decimal_place));
        })
    }
});

// event change price
// var last_price = 0.00;
// $('#dynamic-table tr.gradeX').find('input').each(function () {
//     var currentRow = $(this).closest('tr').find('input');
//     // currentItem = $(this).closest('tr').find('option:selected');
//     $priceElement = '#' + currentRow[PO_ROW_INDEX_ITEM_PRICE].id;
//     $($priceElement).on('focus', function (e) {
//         last_price = float_format($(this).val());
//     })
//     $($priceElement).change(function (e) {
//         var currentRow = $(this).closest('tr').find('input');
//         $('#'+ currentRow[PO_ROW_INDEX_AMOUNT].id).val(roundDecimal(float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value) *
//                                                float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value) *
//                                                float_format(currentRow[PO_ROW_INDEX_EXCHANGE_RATE].value), decimal_place)).trigger("change");
//         if (currentRow[PO_ROW_INDEX_ITEM_PRICE].value > 0) {
//             $('#validate_error').css('display', 'none');
//             currentRow.parents('tr').removeAttr('style');
//
//             $('#dynamic-table tr.gradeX').each(function () {
//                 // recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT);
//                 $(this).closest('tr').find('input').removeAttr('disabled');
//             });
//             $('#validate_error').css('display', 'none');
//             fnEnableButton();
//             // validationItemsFormset();
//         } else {
//             pop_ok_dialog("Invalid Price",
//               "Price of product must be greater than 0",
//               function(){
//                 $('#dynamic-table tr.gradeX').each(function () {
//                     // recalculateAmount(this, PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT);
//                 });
//                 setTimeout(function() {
//                     $Target = '#' + e.target.id;
//                     $($Target).val(last_price.toFixed(6));
//                     $($Target).select();
//                 }, 300);
//             });
//         }
//         $(this).val(float_format($(this).val()).toFixed(6));
//     });
//     $($priceElement).click(function () {
//         $(this).select();
//     });
// });

//change amount event
// $('#dynamic-table tr.gradeX').each(function () {
//     var currentRow = $(this).closest('tr').find('input');
//     $amountElement = '#' + currentRow[PO_ROW_INDEX_AMOUNT].id;
//     $($amountElement).on('change', function (e) {
//         var currentRow = $(this).closest('tr').find('input');
//         var currentLabel = $(this).closest('tr').find('label');
//         let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
//         var amount = float_format(currentRow[PO_ROW_INDEX_ITEM_PRICE].value) * float_format(currentRow[PO_ROW_INDEX_ITEM_QTY].value) ;
//         currentRow[PO_ROW_INDEX_AMOUNT].value = roundDecimal(amount, decimal_place);
//         currentLabel[PO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[PO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place) ;
//         $('#id_formset_item-'+ (rowIndex-1) +'-amount').text(comma_format(currentRow[PO_ROW_INDEX_AMOUNT].value));
//         var subtotal = 0;
//         var total = 0;
//         if ($(this)[0].value < 0) {
//             $(this).closest('tr').attr('style', 'background-color: red !important');
//             $('#items_error').text('The product ' + currentRow[PO_ROW_INDEX_CODE].value + ' must have amount greater than 0');
//             $('#items_error').removeAttr('style');
//             fnDisableButton();
//             $('#dynamic-table tr.gradeX').each(function () {
//                 $(this).closest('tr').find('input').not(currentRow[PO_ROW_INDEX_AMOUNT]).attr('disabled', true);
//             });
//         } else {
//             $('#items_error').css('display', 'none');
//             $(this).closest('tr').removeAttr('style');
//             fnEnableButton();
//         }
//         calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE,
//             PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
//     });
//     $($amountElement).click(function () {
//         $(this).select();
//     });
// });

function WarnLessThanMinOrder(prtno, ord_qty, min_qty, elm, nextElm) {
    function cancel_function(){
        $(elm).val(float_format(min_qty).toFixed(2)).trigger('change');
        $(elm).select();
        $('#dynamic-table tr.gradeX').each(function () {
            $(elm).closest('tr').find('input').removeAttr('disabled');
        });
        $(elm).closest('tr').removeAttr('style');
        $('#btnPrint').removeAttr('disabled');
        $('#btnSave').removeAttr('disabled');
    }

    function ok_function(){
        $(elm).val(comma_format(ord_qty, decimal_place));
        $('#dynamic-table tr.gradeX').each(function () {
            $(elm).closest('tr').find('input').removeAttr('disabled');
        });
        $(elm).closest('tr').removeAttr('style');
        $('#btnPrint').removeAttr('disabled');
        $('#btnSave').removeAttr('disabled');

        $(nextElm).focus();
        $(nextElm).select();
    }

    pop_ok_cancel_dialog("Warning!",
                         "Order Quantity ("+ord_qty+") of part number "+prtno+
                         " is less than it Minimum order Quantity ("+min_qty+
                         "). Continue anyway ?",
                         ok_function,
                         cancel_function,
                         'No, reset to Minimum Order Quantity !');
}

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var currentLabel = $(this).closest('tr').find('label');
    var $cust_po_no = '#' + currentRow[PO_ROW_INDEX_CUSTOMER_PO].id;
    var is_inventory = $('#company_is_inventory').val();

    $($cust_po_no).click(function () {
        $(this).select();
    });

    // $($cust_po_no).trigger('change');
});


function handleDates() {
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var $wanted_fake_date = '#' + currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].id;
        var $wanted_date = '#' + currentRow[PO_ROW_INDEX_WANTED_DATE].id;
        wanted_date = $($wanted_date).val()
        if(wanted_date !== "")
            $($wanted_fake_date).val(moment(wanted_date,"YYYY-MM-DD").format("DD-MM-YYYY"));
        var current_val = ""

        // $($wanted_fake_date).bind('keydown', function(event) {
        //     if (event.which == 13) {
        //         date_key_down(this);
        //         return false;
        //     }
        // });

        $($wanted_fake_date).bind('keyup', function(event) {
            adjust_input_date(this);
        });

        function change_wanted_date(date_from, element_id){
            $wanted_fake_date = '#' + element_id;
            $wanted_date = '#' + get_element_offset($($wanted_fake_date), '', 1)[0].id;

            var date_rate_1 = dateView(date_from);
            $($wanted_date).val(date_rate_1);
            $($wanted_fake_date).val(date_from);

            // move_next_elem($($wanted_fake_date), 1);
        }

        function revert_wanted_date(element_id){
            $wanted_fake_date = '#' + element_id;
            $wanted_date = '#' + get_element_offset($($wanted_fake_date), '', 1)[0].id;

            $($wanted_fake_date).focus();
            $($wanted_fake_date).select();

            if ($($wanted_date).val() != ""){
                $($wanted_fake_date).val(moment($($wanted_date).val(),"YYYY-MM-DD").format("DD-MM-YYYY"));
            }else{
                $($wanted_fake_date).val("");
            }
            // move_next_elem($($wanted_fake_date), 0);

        }

        $($wanted_fake_date).off('change').on('change', function (e) {
            var date_from = get_date_from('#'+e.target.id);
            date_from = date_from.split('/').join('-');
            var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();

            if (!date_from_valid){
                pop_ok_dialog("Invalid Wanted Date",
                            "Wanted Date ("+$('#'+e.target.id).val()+") is invalid !",
                            function(){
                                    $wanted_fake_date = '#' + e.target.id;
                                    $wanted_date = '#' + get_element_offset($($wanted_fake_date), '', 1)[0].id;
                                    $($wanted_fake_date).val($($wanted_date).val());
                                    revert_wanted_date(e.target.id);
                            });

            }else{
                var doc_date = $('#id_document_date').val();
                // var current_date = new Date();
                var current_date = new Date(moment(doc_date, "YYYY-MM-DD").format("YYYY-MM-DD"));
                current_date.setHours(0,0,0,0);
                var input_date = new Date(moment($('#'+e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
                var resultOK = true;
                if (input_date.getTime() < current_date.getTime()) {
                    resultOK = false;
                    pop_ok_cancel_dialog("Invalid Wanted Date",
                                        "Wanted Date ("+$('#' + e.target.id).val() +
                                        ") is back dated !<br/> Do you want to proceed?",
                                        function(){
                                            change_wanted_date(date_from, e.target.id)
                                        },
                                        function(){
                                            revert_wanted_date(e.target.id)
                                        });
                
                } else {
                    var so_date = $(this).attr('so_date');
                    if (so_date){
                        var current_date = new Date(moment(so_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
                        current_date.setHours(0,0,0,0);
                        var input_date = new Date(moment($('#'+e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
                        input_date.setHours(0,0,0,0);
                        if (input_date.getTime() > current_date.getTime()) {
                            resultOK = false;
                            pop_ok_dialog("Invalid Wanted Date",
                                                "Wanted Date ("+$('#' + e.target.id).val() +
                                                ") cannot be later than S/O wanted date",
                                                function(){
                                                    change_wanted_date(so_date, e.target.id)
                                                });
                        }
                    } else {
                        $('#dynamic-table tr.gradeX').each(function () {
                            $('#'+e.target.id).closest('tr').find('input').removeAttr('disabled');
                        });
                        $('#'+e.target.id).closest('tr').removeAttr('style');
                        fnEnableButton();
    
                        var sched_date = new Date(moment(currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value, "DD-MM-YYYY").format("YYYY-MM-DD"));
                        if (sched_date){
                            ssched_date = new Date(sched_date);
                            if (input_date.getTime() < ssched_date.getTime()){
                                resultOK = false;
                                pop_ok_cancel_dialog("Invalid Wanted Date",
                                                    "Wanted Date (" + $('#' + e.target.id).val() +
                                                    ") must be greater than or equal to Schedule Date (" + sched_date +
                                                    ") !<br/> Do you want to proceed?",
                                                    function(){change_wanted_date(date_from, e.target.id)},
                                                    function(){revert_wanted_date(e.target.id)});
                            }
                        }
                    }
                }

                if (resultOK){
                    change_wanted_date(date_from, e.target.id);
                    // move_next_elem($("#" + e.target.id), 1);
                }
            }
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });

        $($wanted_fake_date).click(function () {
            $(this).select();
        });
    });
}


$('#dynamic-table tr.gradeX').each(function () {
    trElement = $(this).closest('tr');
    schedule_fake_date(trElement);
});

function schedule_fake_date(element) {
    var currentRow = $(element).find('input');
    var $schedule_fake_date = '#' + currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].id;
    var $schedule_date = '#' + currentRow[PO_ROW_INDEX_SCHEDULE_DATE].id;
    schedule_date = $($schedule_date).val();
    if(schedule_date !== "")
        $($schedule_fake_date).val(moment(schedule_date,"YYYY-MM-DD").format("DD-MM-YYYY"));
    var current_val = ""


    // $($schedule_fake_date).bind('keydown', function(event) {
    //     if (event.which == 13) {
    //         date_key_down(this);
    //         return false;
    //     }
    // });

    $($schedule_fake_date).bind('keyup', function(event) {
        adjust_input_date(this);
    });


    function change_schedule_date(date_from, element_id){
        $schedule_fake_date = '#' + element_id;
        $schedule_date = '#' + get_element_offset($($schedule_fake_date), '', 1)[0].id;

        var date_rate_1 = dateView(date_from);
        $($schedule_date).val(date_rate_1);
        $($schedule_fake_date).val(date_from);

        // move_next_elem($($schedule_fake_date),2);
    }

    function revert_schedule_date(element_id){
        $schedule_fake_date = '#' + element_id;
        $schedule_date = '#' + get_element_offset($($schedule_fake_date), '', 1)[0].id;

        $($schedule_fake_date).focus();
        $($schedule_fake_date).select();

        if ($($schedule_date).val() != ""){
            $($schedule_fake_date).val(moment($($schedule_date).val(),"YYYY-MM-DD").format("DD-MM-YYYY"));
        }else{
            $($schedule_fake_date).val("");
        }
        // move_next_elem($($schedule_fake_date),0);
    }

    $($schedule_fake_date).on('change', function (e) {
        var date_from = get_date_from('#' + e.target.id);
        date_from = date_from.split('/').join('-');
        var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();


        if (!date_from_valid){
            pop_ok_dialog("Invalid Schedule Date",
                          "Schedule Date ("+$('#' + e.target.id).val()+") is invalid !",
                          function(){
                                $schedule_fake_date = '#' + e.target.id;
                                $schedule_date = '#' + get_element_offset($($schedule_fake_date), '', 1)[0].id;
                                $($schedule_fake_date).val($($schedule_date).val());
                                revert_schedule_date(e.target.id);
                          });
        }else{
            var doc_date = $('#id_document_date').val();
            // var current_date = new Date();
            var current_date = new Date(moment(doc_date, "YYYY-MM-DD").format("YYYY-MM-DD"));
            current_date.setHours(0,0,0,0);
            var input_date = new Date(moment($('#'+e.target.id).val(), "DD-MM-YYYY").format("YYYY-MM-DD"));
            var resultOK = true;
            if (input_date.getTime() < current_date.getTime()){
                resultOK = false;
                pop_ok_cancel_dialog("Invalid Schedule Date",
                                     "Schedule Date ("+$('#' + e.target.id).val() +
                                     ") is back dated !<br/> Do you want to proceed?",
                                     function(){change_schedule_date(date_from, e.target.id)},
                                     function(){revert_schedule_date(e.target.id)});
            } else {
                $('#dynamic-table tr.gradeX').each(function () {
                    $('#'+e.target.id).closest('tr').find('input').removeAttr('disabled');
                });
                $('#'+e.target.id).closest('tr').removeAttr('style');
                fnEnableButton();

                var wanted_date = new Date(moment(currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].value, "DD-MM-YYYY").format("YYYY-MM-DD"));
                if (wanted_date){
                    wwanted_date = new Date(wanted_date);
                    if (input_date.getTime() < wwanted_date.getTime()){
                        resultOK = false;
                        pop_ok_cancel_dialog("Invalid Schedule Date",
                                             "Schedule Date ("+$('#' + e.target.id).val()+
                                             ") must be greater than or equal to Wanted Date ("+wanted_date+
                                             ") !<br/> Do you want to proceed?",
                                             function(){change_schedule_date(date_from, e.target.id)},
                                             function(){revert_schedule_date(e.target.id)});
                    }
                }
            }
            if (resultOK){
                change_schedule_date(date_from, e.target.id);
                // move_next_elem($('#'+e.target.id), 1);
            }
        }
    });

    $($schedule_fake_date).click(function () {
        $(this).select();
    });
}

function fnDisableButton() {
    $('#btnPrint').attr('disabled', true);
    $('#btnSave').attr('disabled', true);
    $('#btnSend').attr('disabled', true);
    $('#btnSendForEdit').attr('disabled', true);
}

function fnEnableButton() {
    $('#btnPrint').removeAttr('disabled');
    $('#btnSave').removeAttr('disabled');
    $('#btnSend').removeAttr('disabled');
    $('#btnSendForEdit').removeAttr('disabled');
    $('#items_error').css("display", "none");
}

$('#id_document_date_fake').keyup(function(){
    adjust_input_date(this);
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

        var id_cus = $('#id_supplier').val();
        var is_req = 1 // request from supplier
        var rate_type = 3
        var curr_to = $('#id_currency').val();
        if (id_cus > 0){
            recort_rate_po(curr_to,date_rate_1,rate_type)
        }
    }
});

function load_supp() {
    var date_rate = $("#id_document_date").val();
    var id_sup = $('#id_supplier').val();
    // $('#id_document_date_fake').select();
    $.ajax({
        type: "GET",
        url: "/suppliers/get_by_pk/"+id_sup+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                order_is_decimal = data.data[0].is_decimal;
                if (order_is_decimal) {
                    decimal_place = 2;
                } else {
                    decimal_place = 0;
                }
                $('#id_supplier').val(data.data[0].id)
                $('#id_currency').val(data.data[0].currency_id).trigger('change');
                $('#name_currency').val(data.data[0].currency_name);
                $('#po_total').text("Total (" + data.data[0].currency_symbol + ') : ');
                $('#customer_payment_term').text(data.data[0].payment_term+' Days');
                $('#customer_payment_mode').text(data.data[0].payment_code);
                $('#customer_credit_limit').text(data.data[0].credit_limit);
                $('#supplier_name').text(data.data[0].supplier_name);
                $('#supplier_address').text(data.data[0].address);
                $('#supplier_email').text(data.data[0].email);
                recort_rate_po(data.data[0].currency_id,date_rate,3)
                // $('#id_document_date_fake').select();
            }
        }
    });
}

function load_part_numbers_purch(){
    var id_sup = 0;
    if ($('#id_supplier').val() > 0){
        id_sup = $('#id_supplier').val();
    }

    item_info.length = 0;
    $.ajax({
        type: "GET",
        url: "/orders/po_select_list_json/"+id_sup+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                item_info = data.data;
                // for (i in array) {
                //     object = {
                //         identity: array[i].identity,
                //         id: array[i].item_id,
                //         name: array[i].item_name,
                //         supplier: array[i].supplier_code,
                //         ref_no: array[i].refer_number,
                //         ref_line: array[i].refer_line,
                //         location_code: array[i].location_code,
                //         purchase_price: array[i].new_price,
                //         code: array[i].code,
                //         category: array[i].category,
                //         currency: array[i].currency_code,
                //         location_id: array[i].location_id,
                //         currency_id: array[i].currency_id,
                //         uom: array[i].unit,
                //         supplier_id: array[i].supplier_id,
                //         minimun_order: array[i].minimun_order,
                //         ref_id: array[i].refer_id,
                //         customer_po_no: array[i].customer_po_no,
                //         backorder_qty: array[i].backorder_qty
                //     }
                //     if(array[i].location_id) {
                //         object.location_id = array[i].location_id;
                //     }
                //     else if(array[i].default_location_id) {
                //         object.location_id = array[i].default_location_id;
                //     }
                //     else {
                //         object.location_id = "";
                //     }
                //     item_info.push(object);
                // }
            }
            load_part_numbers();
        }

    });
}

function load_part_numbers_supp(){
    var id_sup = 0;
    if ($('#id_supplier').val() > 0){
        id_sup = $('#id_supplier').val();
    }

    item_info.length = 0;
    $.ajax({
        type: "GET",
        url: "/orders/po_select_list_json/"+id_sup+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                item_info = data.data;
                // for (i in array) {
                //     object = {
                //         identity: array[i].identity,
                //         id: array[i].item_id,
                //         name: array[i].item_name,
                //         supplier: array[i].supplier_code,
                //         ref_no: array[i].refer_number,
                //         ref_line: array[i].refer_line,
                //         location_code: array[i].location_code,
                //         purchase_price: array[i].new_price,
                //         code: array[i].code,
                //         category: array[i].category,
                //         currency: array[i].currency_code,
                //         location_id: array[i].location_id,
                //         currency_id: array[i].currency_id,
                //         uom: array[i].unit,
                //         supplier_id: array[i].supplier_id,
                //         minimun_order: array[i].minimun_order,
                //         ref_id: array[i].refer_id,
                //         customer_po_no: array[i].customer_po_no,
                //         backorder_qty: array[i].backorder_qty
                //     }
                //     if(array[i].location_id) {
                //         object.location_id = array[i].location_id;
                //     }
                //     else if(array[i].default_location_id) {
                //         object.location_id = array[i].default_location_id;
                //     }
                //     else {
                //         object.location_id = "";
                //     }
                //     item_info.push(object);
                // }
            }
        }

    });
}

function recort_rate_po(curr_to,date_rate_1,rate_type) {
    $.ajax({
        type: "GET",
        url :'/currencies/get_exchange_by_date/'+1+'/'+curr_to+'/'+date_rate_1+'/'+rate_type+'/',
        dataType: 'JSON',
        success: function(data){
            if (parseFloat(data[0].rate) == 0) {
                pop_ok_dialog("Invalid Exchange Rate",
                    "Exchange Rate not found for current period for " + data[0].from_code + " to " + data[0].to_code +".",
                    function () { }
                );
                fnDisableButton();
                $('#exchange_rate_fk_id').val('');
                $('#id_exchange_rate_date').val('');
                $('#id_exchange_rate').val('');
                $('#id_exchange_rate_value').val('');
            } else {
                fnEnableButton();
                $('#exchange_rate_fk_id').val(data[0].id);
                $('#id_exchange_rate_date').val(data[0].exchange_date);
                $('#id_exchange_rate').val(data[0].rate);
                $('#id_exchange_rate_value').val(data[0].rate);
            }
        }
    });
}


$.checkOrderRowValidity = function(row_number, selector) {
    if (row_number === undefined) {
        return false;
    }

    if (selector === undefined) {
        selector = '#dynamic-table';
    }

    // row = $(selector+' tr.gradeX')[row_number];
    row = editing_row;

    valid = ($(row).length != 0);

    if (!valid) {
        return false;
    }

    $inputs = $(row).find('input');
    $selects = $(row).find('select');

    // Check each field is empty
    if ($inputs[PO_ROW_INDEX_LINE_NUMBER].value === '') {
        console.log('Error, line number empty');
        valid = false;
    }

    else if ($inputs[PO_ROW_INDEX_ITEM_ID].value === '') {
        console.log('Error, item id empty');
        valid = false;
    }
    else if ($inputs[PO_ROW_INDEX_CUSTOMER_PO].value === '') {
        console.log('Error, customer po empty');
        valid = false;
    }
    else if ($inputs[PO_ROW_INDEX_WANTED_FAKE_DATE].value === '') {
        console.log('Error, wanted date empty');
        valid = false;
    }
    else if ($inputs[PO_ROW_INDEX_ITEM_QTY].value === '' || float_format($inputs[PO_ROW_INDEX_ITEM_QTY].value) == 0) {
        console.log('Error, quantity empty');
        valid = false;
    }

    return valid;
}


var refer_numbers = [];
function load_refer_numbers(){
    var id_cus = 0;
    if( $('#id_supplier').val()>0){
        id_cus = $('#id_supplier').val();
    }
    $('#load_so_by_cust').empty();
    refer_numbers = [];
    $.ajax({
        type: "GET",
        url: "/orders/po_select_so_json/"+id_cus+'/',
        dataType: 'JSON',
        success: function(data){
        if (data.data.length > 0){
            refer_numbers = data.data
            }
        }

    });
}

function load_part_numbers(){
    var id_cus = 0;
    if( $('#id_supplier').val()>0){
        id_cus = $('#id_supplier').val();
    }
    $('#load_so_by_cust').empty();
    refer_numbers = [];
    $.ajax({
        type: "GET",
        url: "/orders/po_select_so_json/"+id_cus+'/',
        dataType: 'JSON',
        success: function(data){
        if (data.data.length > 0){
            refer_numbers = data.data
            }
            initiateRefNumber('#dynamic-table tr.gradeX:last');
        }

    });
}

// var last_so_number = '';
// var refer_line_selected = [];
// var remain_count = -1;

function tabAddRow(rowIndex, code_pressed) {
    if (code_pressed == '9') {
        var rowCount = ($('#dynamic-table tr.gradeX')).length;
        if (rowIndex == rowCount) {
            $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
            setTimeout(() => {
                rowCount = ($('#dynamic-table tr.gradeX')).length;
                rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').attr('data-row_index');
                $('#id_select-' + rowIndex + '-ref_number').focus();
                $('#id_select-' + rowIndex + '-ref_number').select2('open');
            }, 300);
        } else {
            rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + (rowIndex+1) + ')').attr('data-row_index');
            setTimeout(() => {
                $('#id_select-' + rowIndex + '-ref_number').focus();
                $('#id_select-' + rowIndex + '-ref_number').select2('open');
            }, 300);
        }
    }
}


function highLightMandatory(rowCheck) {
    if ($('#id_select-' + rowCheck +'-ref_number').val() != '') {
        if ($('#id_select-' + rowCheck +'-refer_line').val() == '') {
            $($('#select2-id_select-' + rowCheck +'-refer_line-container').parent('span')[0]).addClass('highlight-mandatory');
        } else {
            $($('#select2-id_select-' + rowCheck +'-refer_line-container').parent('span')[0]).removeClass('highlight-mandatory');
        }
    }

    if ($('#id_select-' + rowCheck +'-item_code').val() == '') {
        $($('#select2-id_select-' + rowCheck +'-item_code-container').parent('span')[0]).addClass('highlight-mandatory');
    } else {
        $($('#select2-id_select-' + rowCheck +'-item_code-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ( $('#id_formset_item-' + rowCheck +'-customer_po_no').val() != '') {
        $('#id_formset_item-' + rowCheck +'-customer_po_no').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-customer_po_no').addClass('highlight-mandatory');
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

    if ( $('#id_formset_item-' + rowCheck +'-wanted_fake_date').val() != '') {
        $('#id_formset_item-' + rowCheck +'-wanted_fake_date').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-wanted_fake_date').addClass('highlight-mandatory');
    }
}

function getFirstFieldInvalid(rowCheck) {
    var idFirstInvalid = '';

    if ($('#id_select-' + rowCheck +'-ref_number').val() != '') {
        if ($('#id_select-' + rowCheck +'-refer_line').val() == '') {
            idFirstInvalid = '#id_select-' + rowCheck +'-refer_line';
            return idFirstInvalid;
        }
    }

    if ($('#id_select-' + rowCheck +'-item_code').val() == '') {
        idFirstInvalid = '#id_select-' + rowCheck +'-item_code';
        return idFirstInvalid;
    }

    if ( $('#id_formset_item-' + rowCheck +'-customer_po_no').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-customer_po_no';
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

    if ( $('#id_formset_item-' + rowCheck +'-wanted_fake_date').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-wanted_fake_date';
        return idFirstInvalid;
    }

    return idFirstInvalid;
}


function initiateRefNumber($selector, $selected=null){
    $($selector).each(function () {
        let selects = $(this).closest('tr').find('select');
        let currentRow = $(this).closest('tr').find('input');
        let currentLabel = $(this).closest('tr').find('label');
        // let rowIndex = parseInt($(this).closest('tr').find('label:first').text())-1;

        var cur_item_id = currentRow[PO_ROW_INDEX_ITEM_ID].value;
        var cur_supplier_id = currentRow[PO_ROW_INDEX_SUPPLIER_ID].value;
        var cur_location_id = $(selects[PO_SELECT_INDEX_LOCATION]).val();
        var cur_identity = '';
        handleQuantity();
        if($selected == null) {
            refreshCurrentRow(currentRow, currentLabel);
            // var $ItemQty = '#' + currentRow[PO_ROW_INDEX_ITEM_QTY].id;
            // quantityEvent($ItemQty)
            handleDates();
            schedule_fake_date($(this).closest('tr'))
        }

        selects.each(function (selectIndex, selectValues) {
            if ($('#company_is_inventory').val() == 'True' && selectIndex == PO_SELECT_INDEX_LOCATION) {
                locationSelect2($(this)[0].id, location_data);

                setTimeout(() => {
                    if($selected) {
                        $(this).val($selected[3]).trigger('change');
                    }
                }, 1000);
            }

            if (selectIndex == PO_SELECT_INDEX_LOCATION) {
                // $(this).select2();
                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('input:eq('+PO_ROW_INDEX_WANTED_FAKE_DATE+')').focus();
                });
            }
            if (selectIndex == PO_SELECT_INDEX_ITEM_CODE) {

                partNumberSelect2($(this)[0].id, item_info, null);

                // $.each(item_info, function(i, v) {
                //     if (v.id == cur_item_id && v.supplier_id == cur_supplier_id){
                //         if (v.location_id == cur_location_id || v.location_id == '' || v.location_id == undefined) {
                //             cur_identity = v.identity;
                //             currentRow[PO_ROW_INDEX_IDENTITY].value = v.identity;
                //         }
                //     }
                // });

                if($selected == null) {
                    $(this).on("change", function( event ){
                        let sum = 0;
                        let currentLabel = $(this).closest('tr').find('label');
                        let currentRow = $(this).closest('tr').find('input');
                        if ($(this).find('option:selected').data('code_data') != null) {
                            let v = $(this).find('option:selected').data('code_data')[0];

                            currentRow[PO_ROW_INDEX_LINE_NUMBER].value = currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent;
                            // currentRow[PO_ROW_INDEX_CODE].value = v.code;
                            currentRow[PO_ROW_INDEX_ITEM_NAME].value = v.name;
                            currentRow[PO_ROW_INDEX_ITEM_ID].value = v.id;
                            // currentRow[PO_ROW_INDEX_CUSTOMER_PO].value = v.customer_po_no;

                            if ($('#company_is_inventory').val() == 'True' && v.location_list.length){
                                location_choice = '#' + selects[PO_SELECT_INDEX_LOCATION].id;
                                if ($(location_choice).data('select2')) {
                                    $(location_choice).select2('destroy');
                                }
                                $(location_choice).empty();
                                var options = '';
                                $.each(v.location_list, function(indx, loc) {
                                    options += "<option value="+loc.id+">"+loc.code+"</option>";
                                });
                                $(location_choice).append(options);
                                $(location_choice).select2();
                                $(location_choice).val(v.location_list[0].id).trigger('change');
                            }

                            currentRow[PO_ROW_INDEX_ITEM_PRICE].value = float_format(v.purchase_price).toFixed(6);
                            currentRow[PO_ROW_INDEX_CURRENCY_CODE].value = v.currency;
                            currentRow[PO_ROW_INDEX_CURRENCY_ID].value = v.currency_id;
                            currentRow[PO_ROW_INDEX_CATEGORY].value = v.category;
                            currentRow[PO_ROW_INDEX_SUPPLIER_CODE].value = v.supplier;
                            currentRow[PO_ROW_INDEX_SUPPLIER_ID].value = v.supplier_id;
                            currentRow[PO_ROW_INDEX_REFER_NO].value = v.ref_no;
                            currentRow[PO_ROW_INDEX_REFER_LINE].value = v.ref_line;
                            currentRow[PO_ROW_INDEX_BACKORDER_QTY].value = v.backorder_qty;
                            currentRow[PO_ROW_INDEX_UOM].value = v.uom;
                            currentRow[PO_ROW_INDEX_REFERENCE_ID].value = v.ref_id;
                            currentRow[PO_ROW_INDEX_MIN_ORDER_QTY].value = v.minimun_order;

                            // currentLabel[PO_LABEL_INDEX_ITEM_CODE].textContent = $(this).text(); // Item Code
                            currentLabel[PO_LABEL_INDEX_ITEM_NAME].textContent = currentRow[PO_ROW_INDEX_ITEM_NAME].value; // Item Name
                            // currentLabel[PO_LABEL_INDEX_PRICE].textContent = currentRow[PO_ROW_INDEX_PRICE].value; // Price
                            currentLabel[PO_LABEL_INDEX_CURRENCY_CODE].textContent = currentRow[PO_ROW_INDEX_CURRENCY_CODE].value; // Currency Code
                            currentLabel[PO_LABEL_INDEX_CATEGORY].textContent = currentRow[PO_ROW_INDEX_CATEGORY].value; // Part Group
                            currentLabel[PO_LABEL_INDEX_SUPPLIER_CODE].textContent = currentRow[PO_ROW_INDEX_SUPPLIER_CODE].value; // Supplier Code
                            // currentLabel[PO_LABEL_INDEX_CUSTOMER_PO].textContent = currentRow[PO_ROW_INDEX_CUSTOMER_PO].value; // Refer Line
                            currentLabel[PO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(currentRow[PO_ROW_INDEX_BACKORDER_QTY].value); // Back Order Quantity
                            currentLabel[PO_LABEL_INDEX_UOM].textContent = currentRow[PO_ROW_INDEX_UOM].value; // UOM

                            // sum = float_format($('#id_subtotal').val());
                            // sum += float_format(currentRow[PO_ROW_INDEX_AMOUNT].value);
                            // sum = roundDecimal(sum, decimal_place)
                            // $('#id_subtotal').val(comma_format(sum, decimal_place));
                            // if (isNaN(sum)) {
                            //     sum = 0;
                            //     $('#id_subtotal').val(0);
                            //     $('#id_total').val(0);
                            // }
                            // if ($('#id_tax_amount').val()) {
                            //     sum += float_format($('#id_tax_amount').val()).toFixed(decimal_place);
                            // }
                            // if ($('#id_discount').val()) {
                            //     sum -= float_format($('#id_discount').val()).toFixed(decimal_place);
                            // }
                            // sum = roundDecimal(sum, decimal_place)
                            // $('#id_total').val(comma_format(sum, decimal_place));

                            // let row = parseInt(currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent)
                            let row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                            $('#dynamic-table tr.gradeX:nth-child('+row+')').each(function () {
                                selects = $(this).closest('tr').find('select');
                                currentRow = $(this).closest('tr').find('input');
                                selects.each(function (selectIndex, selectValue) {
                                    if (selectIndex == PO_SELECT_INDEX_LOCATION) {
                                        if ($('#company_is_inventory').val() == 'True') {
                                            $(this).find('option[value="' + v.location_id + '"]').prop('selected', true);
                                        }
                                    }
                                });
                            });

                            doEssentials(currentRow);
                        }
                    });
                }

                $(this).on("select2:close", function (event) {
                    // $(currentRow[SO_ROW_INDEX_CUSTOMER_PO]).focus();
                    $(this).closest('tr').find('input:eq('+PO_ROW_INDEX_CUSTOMER_PO+')').focus();
                    // let rowCheck = parseInt($(this).closest('tr').find('label:first').text()) - 1;
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    highLightMandatory(rowCheck);
                });

                // if (currentRow[PO_ROW_INDEX_ITEM_ID].value != '') {
                //     $(this).val(currentRow[PO_ROW_INDEX_ITEM_ID].value).trigger('change');
                // }

                $(this).prop('disable', false);
                $(this).select2('enable');

                // if (cur_identity != '') {
                //     $(this).val(cur_identity).trigger('change');
                // }
                setTimeout(() => {
                    if($selected) {
                        if ($selected[2] != '0') {
                            $(this).val($selected[2]).trigger('change');
                        } 
                        // else {
                        //     $(this).val($selected[2].identity).trigger('change');
                        // }
                    }
                }, 1000);
            }
            if (selectIndex == PO_SELECT_INDEX_REF_NUMBER) {

                referNumberSelect2($(this)[0].id, refer_numbers);

                if($selected) {
                    // $(this).val($selected[0]);
                    if ($selected[0] != '0') {
                        $(this).val($selected[0]).trigger('change');
                    }
                }
                if($selected == null) {
                    $(this).on("change", function( event ){
                        let last_amount = float_format($('#'+currentLabel[PO_LABEL_INDEX_AMOUNT].id).text());
                        let new_amount = 0;
                        calculatePOTotal(last_amount, new_amount);

                        let so_number = $(this).find('option:selected').data('code_data');
                        let tthis = this;
                        // let is_update = false;
                        let supp_id = $('#id_supplier').val();
                        let ref_line_id = 'id_select-' + (parseInt($(this).closest('tr').attr('data-row_index'))) + '-refer_line';
                        if(so_number != '0' && so_number != undefined && so_number != null) {
                            $.ajax({
                                method: "POST",
                                url: '/orders/get_so_orderitems_for_po/',
                                dataType: 'JSON',
                                data: {
                                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                                    'so_number': so_number,
                                    'supplier_id': supp_id,
                                    'exclude_item_list': []
                                },
                                success: function (json) {
                                    allVals.length = 0;
                                    if (json.length > 0) {
                                        allVals = json;
                                    }
                                    // $.each(json, function (i, item) {
                                    //     if(item.supplier_id == supp_id) {
                                    //         allVals.push({
                                    //             id: item.item_id, //Item ID
                                    //             price: item.sales_price,
                                    //             item_code: item.item_code, //Item Code
                                    //             name: item.item_name, //Item Name
                                    //             refer_number: item.refer_number,
                                    //             refer_line: item.refer_line,
                                    //             supplier_code: item.supplier_code,
                                    //             location_code: item.location_code,
                                    //             category: item.category,
                                    //             unit_price: item.unit_price,
                                    //             currency: item.currency_code,
                                    //             location_id: item.location_id,
                                    //             currency_id: item.currency_id,
                                    //             uom: item.uom,
                                    //             wanted_date: item.wanted_date,
                                    //             schedule_date: item.schedule_date,
                                    //             description: item.description,
                                    //             supplier_id: item.supplier_id,
                                    //             backorder_qty: item.backorder_qty,
                                    //             order_quantity: item.quantity,
                                    //             delivery_quantity: item.delivery_quantity,
                                    //             customer_po_no: item.customer_po_no,
                                    //             country_origin_id: item.country_origin_id,
                                    //             country_origin_cd: item.country_origin_cd,
                                    //             location_item_quantity: item.location_item_quantity,
                                    //             minimum_order: item.minimum_order,
                                    //             ref_id: item.refer_id,
                                    //         });
                                    //     }
                                    // });

                                    refreshCurrentRow(currentRow, currentLabel);
                                    // let part_number_id = 'id_select-' + (parseInt($(tthis).closest('tr').find('label:first').text())-1) + '-item_code';
                                    // partNumberSelect2(part_number_id, [], null);
                                    referLineSelect2(ref_line_id, allVals, so_number, 'PO');

                                    if (!$("#orderItemModal").is(':visible')) {
                                        setTimeout(function() {
                                            $(selects[PO_SELECT_INDEX_REF_NUMBER]).select2('close');
                                            $(selects[PO_SELECT_INDEX_ITEM_CODE]).select2('destroy');
                                            $(selects[PO_SELECT_INDEX_ITEM_CODE]).empty();
                                            $(selects[PO_SELECT_INDEX_ITEM_CODE]).prop("disabled", true);
                                            if (allVals.length == 1) {
                                                $('#' + ref_line_id).val(allVals[0].refer_line).trigger('change');
                                            } else {
                                                $(selects[PO_SELECT_INDEX_REFER_LINE]).select2('open');
                                            }
                                        }, 300);
                                    }
                                }
                            });
                        } else {
                            refreshCurrentRow(currentRow, currentLabel);
                            let part_number_id = 'id_select-' + (parseInt($(this).closest('tr').attr('data-row_index'))) + '-item_code';
                            $('#'+part_number_id).removeAttr('disabled');
                            partNumberSelect2(part_number_id, item_info, null);
                            referLineSelect2(ref_line_id, [], '', 'PO');
                        }

                        let rowIndex = $(this).closest('tr').find('label:first').text();
                        storeCopyRefNumberData = saveCopyRefNumberDO(rowIndex, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
                        // storeCopyRefNumberData = changeIndexData(rowIndex, 'minus', storeCopyRefNumberData);

                    });
                }

                $(this).on("select2:close", function (event) {
                    if ($(this).val()) {
                        $(this).closest('tr').find('select:eq('+PO_SELECT_INDEX_REFER_LINE+')').focus();
                    } else {
                        $(this).closest('tr').find('select:eq('+PO_SELECT_INDEX_ITEM_CODE+')').focus();
                    }
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    highLightMandatory(rowCheck);
                });

            }
            if (selectIndex == PO_SELECT_INDEX_REFER_LINE) {

                referLineSelect2($(this)[0].id, [], '', 'PO');

                if($selected == null) {
                    $(this).on("change", function( event ){
                        $(selects[PO_SELECT_INDEX_ITEM_CODE]).prop("disabled", false);
                        let sum = 0;
                        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
                        let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                        let line = $(this).closest('tr').find('label:first').text();
                        let refer_line = $(this).find('option:selected').data('code_data');
                        let currentLabel = $(this).closest('tr').find('label');
                        let currentRow = $(this).closest('tr').find('input');
                        let check_refer_number = $(selects[PO_SELECT_INDEX_REF_NUMBER]).val();
                        let check_refer_line = $(this).val();

                        // let remainQuantity = getRemainQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, allVals);
                        storeCopyRefNumberData = saveCopyRefNumberDO(line, check_refer_number, check_refer_line, 'add', storeCopyRefNumberData, allVals);
                        for(var i=0; i<allVals.length; i++) {
                            if(allVals[i].refer_line == refer_line) {
                                // total_line_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, check_refer_line, PO_ROW_INDEX_ITEM_QTY, PO_SELECT_INDEX_REF_NUMBER, PO_SELECT_INDEX_REFER_LINE, allVals[i].order_quantity);
                                //add value to Input
                                currentRow[PO_ROW_INDEX_LINE_NUMBER].value = currentLabel[PO_LABEL_INDEX_LINE_NUMBER].textContent;
                                currentRow[PO_ROW_INDEX_CODE].value = allVals[i].item_code;
                                currentRow[PO_ROW_INDEX_ITEM_NAME].value = allVals[i].name;
                                currentRow[PO_ROW_INDEX_ITEM_ID].value = allVals[i].id;
                                currentRow[PO_ROW_INDEX_CUSTOMER_PO].value = allVals[i].customer_po_no;
                                currentRow[PO_ROW_INDEX_WANTED_DATE].value = allVals[i].wanted_date;
                                currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].value = (allVals[i].wanted_date).split('-').reverse().join('-');
                                currentRow[PO_ROW_INDEX_SCHEDULE_DATE].value = allVals[i].schedule_date;
                                currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value = (allVals[i].schedule_date).split('-').reverse().join('-');
                                currentRow[PO_ROW_INDEX_DESCRIPTION].value = allVals[i].description;
                                $('#'+currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].id).attr('so_date', currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].value);
                                $('#'+currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].id).attr('so_date', currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value);

                                if ($('#company_is_inventory').val() == 'True' && allVals[i].location_id){
                                    location_choice = '#' + selects[PO_SELECT_INDEX_LOCATION].id;
                                    if ($(location_choice).data('select2')) {
                                        $(location_choice).select2('destroy');
                                    }
                                    $(location_choice).empty();
                                    var options = '';
                                    options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                                    $(location_choice).append(options);
                                    $(location_choice).select2();
                                    $(location_choice).val(allVals[i].location_id).trigger('change');
                                    // currentRow[DO_ROW_INDEX_LOC_ITEM_QTY].value = allVals[i].location_item_quantity;
                                }

                                // if (remainQuantity == undefined) {
                                    currentRow[PO_ROW_INDEX_ITEM_QTY].value = float_format(allVals[i].order_quantity).toFixed(2);
                                // } else {
                                //     if (remainQuantity > 0) {
                                //         currentRow[PO_ROW_INDEX_ITEM_QTY].value = float_format(remainQuantity).toFixed(2);
                                //         storeCopyRefNumberData = updateQuantityCopyRefNumberDO(line, check_refer_number, check_refer_line, storeCopyRefNumberData, remainQuantity)
                                //     } else {
                                //         currentRow[PO_ROW_INDEX_ITEM_QTY].value = float_format(remainQuantity).toFixed(2);
                                //     }
                                // }

                                // $('#'+ currentRow[PO_ROW_INDEX_ITEM_QTY].id).trigger('change');
                                currentRow[PO_ROW_INDEX_ITEM_PRICE].value = float_format(allVals[i].unit_price).toFixed(6);
                                currentRow[PO_ROW_INDEX_CURRENCY_CODE].value = allVals[i].currency;
                                currentRow[PO_ROW_INDEX_CURRENCY_ID].value = allVals[i].currency_id;
                                currentRow[PO_ROW_INDEX_CATEGORY].value = allVals[i].category;
                                currentRow[PO_ROW_INDEX_SUPPLIER_CODE].value = allVals[i].supplier_code;
                                currentRow[PO_ROW_INDEX_SUPPLIER_ID].value = allVals[i].supplier_id;
                                currentRow[PO_ROW_INDEX_REFER_NO].value = allVals[i].refer_number;
                                currentRow[PO_ROW_INDEX_REFER_LINE].value = allVals[i].refer_line;
                                currentRow[PO_ROW_INDEX_BACKORDER_QTY].value = float_format(allVals[i].backorder_qty).toFixed(2);
                                currentRow[PO_ROW_INDEX_UOM].value = allVals[i].uom;
                                currentRow[PO_ROW_INDEX_REFERENCE_ID].value = allVals[i].ref_id;
                                currentRow[PO_ROW_INDEX_MIN_ORDER_QTY].value = allVals[i].minimum_order;

                                // currentLabel[PO_LABEL_INDEX_ITEM_CODE].textContent = allVals[i].item_code; // Item Code
                                currentLabel[PO_LABEL_INDEX_ITEM_NAME].textContent = currentRow[PO_ROW_INDEX_ITEM_NAME].value; // Item Name
                                // currentLabel[PO_LABEL_INDEX_PRICE].textContent = currentRow[PO_ROW_INDEX_PRICE].value; // Price
                                currentLabel[PO_LABEL_INDEX_CURRENCY_CODE].textContent = currentRow[PO_ROW_INDEX_CURRENCY_CODE].value; // Currency Code
                                currentLabel[PO_LABEL_INDEX_CATEGORY].textContent = currentRow[PO_ROW_INDEX_CATEGORY].value; // Part Group
                                currentLabel[PO_LABEL_INDEX_SUPPLIER_CODE].textContent = currentRow[PO_ROW_INDEX_SUPPLIER_CODE].value; // Supplier Code
                                // currentLabel[PO_LABEL_INDEX_CUSTOMER_PO].textContent = currentRow[PO_ROW_INDEX_CUSTOMER_PO].value; // Refer Line
                                currentLabel[PO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(currentRow[PO_ROW_INDEX_BACKORDER_QTY].value); // Back Order Quantity
                                currentLabel[PO_LABEL_INDEX_UOM].textContent = currentRow[PO_ROW_INDEX_UOM].value; // UOM

                                // sum = float_format($('#id_subtotal').val());
                                // sum += float_format(currentRow[PO_ROW_INDEX_AMOUNT].value);
                                // sum = roundDecimal(sum, decimal_place);
                                // $('#id_subtotal').val(comma_format(sum, decimal_place));
                                // if (isNaN(sum)) {
                                //     sum = 0;
                                //     $('#id_subtotal').val(0);
                                //     $('#id_total').val(0);
                                // }
                                // if ($('#id_tax_amount').val()) {
                                //     sum += float_format($('#id_tax_amount').val()).toFixed(decimal_place);
                                // }
                                // if ($('#id_discount').val()) {
                                //     sum -= float_format($('#id_discount').val()).toFixed(decimal_place);
                                // }
                                // sum = roundDecimal(sum, decimal_place);
                                // $('#id_total').val(comma_format(float_format(sum.toFixed(decimal_place)), decimal_place));

                                // let row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                                // $('#dynamic-table tr.gradeX:nth-child('+row+')').each(function () {
                                //     let selects = $(this).closest('tr').find('select');
                                //     //let currentRow = $(this).closest('tr').find('input');
                                //     selects.each(function (selectIndex, selectValue) {
                                //         if (selectIndex == PO_SELECT_INDEX_ITEM_CODE) {
                                //             let options = '<option data-code_data="['+allVals[i].id+']" value="'+ allVals[i].id +'">'+allVals[i].item_code+'</option>';
                                //             partNumberSelect2($(this)[0].id, [], options);

                                //             $(this).on("select2:close", function (event) {
                                //                 $(this).closest('tr').find('input:eq('+PO_ROW_INDEX_CUSTOMER_PO+')').focus();
                                //             });
                                //             $(this).val(allVals[i].id);
                                //         }
                                //         // if (selectIndex == PO_SELECT_INDEX_LOCATION) {
                                //         //     if ($('#company_is_inventory').val() == 'True') {
                                //         //         $(this).find('option[value="' + allVals[i].location_id + '"]').prop('selected', true);
                                //         //     }
                                //         // }
                                //     });
                                // });
                                code_choice = '#' + selects[PO_SELECT_INDEX_ITEM_CODE].id;
                                if ($(code_choice).data('select2')) {
                                    $(code_choice).select2('destroy');
                                }
                                $(code_choice).empty();
                                options = '<option data-code_data="['+allVals[i].id+']" value="'+ allVals[i].id +'">'+allVals[i].item_code+'</option>';
                                $(code_choice).append(options);
                                $(code_choice).select2();
                                $(code_choice).val(allVals[i].id);

                                $('#' + currentRow[PO_ROW_INDEX_CUSTOMER_PO].id).trigger('change');

                                highLightMandatory(rowCheck);
                            }
                        }
                        doEssentials(currentRow);
                        if ($(this).val() !== '' && $(this).val() !== null) {
                            if (!$("#orderItemModal").is(':visible')) {
                                if ($('#' + currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].id).val()) {
                                    $('#' + currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].id).trigger('change');
                                }
                                $('#'+ currentRow[PO_ROW_INDEX_ITEM_QTY].id).trigger('change');
                            }
                        }
                    });
                }

                $(this).on("select2:close", function (event) {
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    if ($('#id_select-' + rowCheck +'-ref_number').val() == '') {
                        $(this).closest('tr').find('select:eq('+PO_SELECT_INDEX_ITEM_CODE+')').select2('open');
                    } else {
                        $(this).closest('tr').find('input:eq('+PO_ROW_INDEX_CUSTOMER_PO+')').focus();
                    }
                    highLightMandatory(rowCheck);
                });

                $(this).prop('disable', false);
                $(this).select2('enable');
                setTimeout(() => {
                    if($selected) {
                        // $(this).val($selected[1]);
                        if ($selected[1] != '0') {
                            $(this).val($selected[1]).trigger('change');
                            $(this).select2('close');
                        }
                    }
                }, 2000);
            }
        });
    });

}


function refreshCurrentRow(currentRow, currentLabel) {
    currentRow[PO_ROW_INDEX_ITEM_QTY].value = '0.00';
    // $('#'+currentRow[PO_ROW_INDEX_ITEM_QTY].id).trigger('change');
    currentLabel[PO_LABEL_INDEX_ITEM_CODE].textContent = '';
    currentLabel[PO_LABEL_INDEX_ITEM_NAME].textContent = '';
    currentLabel[PO_LABEL_INDEX_CURRENCY_CODE].textContent = '';
    currentLabel[PO_LABEL_INDEX_CATEGORY].textContent = '';
    currentLabel[PO_LABEL_INDEX_SUPPLIER_CODE].textContent = '';
    currentLabel[PO_LABEL_INDEX_BACKORDER_QTY].textContent = '';
    currentLabel[PO_LABEL_INDEX_UOM].textContent = '';
    currentLabel[PO_LABEL_INDEX_AMOUNT].textContent = '0.00';

    currentRow[PO_ROW_INDEX_CUSTOMER_PO].value = '';
    currentRow[PO_ROW_INDEX_WANTED_FAKE_DATE].value = '';
    currentRow[PO_ROW_INDEX_SCHEDULE_FAKE_DATE].value = '';
    currentRow[PO_ROW_INDEX_DESCRIPTION].value = '';
    currentRow[PO_ROW_INDEX_ITEM_QTY].value = '0.00';
    currentRow[PO_ROW_INDEX_ITEM_PRICE].value = '0.000000';

    // set empty customer no
    // $('#modal_customer_po_no').val('');
}


function doEssentials(currentRow){
    //Change currency
    var currency_id = parseInt($('#id_currency option:selected').val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];

    if (currentRow[PO_ROW_INDEX_CURRENCY_ID].value != '' && currency_id != '') {
        arrItems.push({
            item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[PO_ROW_INDEX_CURRENCY_ID].value
        });
        changeCurrency_2(arrItems, currency_id, currentRow, currency_name);
    }


    // $('#dynamic-table tr.gradeX').each(function () {
    //     currentRow = $(this).closest('tr').find('input');
    //     if(currentRow[PO_ROW_INDEX_ITEM_ID].value) {
    //         arrItems.push({
    //             item_id: currentRow[PO_ROW_INDEX_ITEM_ID].value,
    //             currency_id: currentRow[PO_ROW_INDEX_CURRENCY_ID].value
    //         });
    //     }
    // });
    // changeCurrency_2(arrItems, currency_id, currentRow, currency_name);

    // $("#load_code_by_supp").val($('#load_code_by_supp option:first-child').val()).trigger('change');
    // $('#dynamic-table tr.gradeX:last').each(function () {
    //     set_order_item_dates();
    //     // var $customer_po_no = $(this).find("input[name*='customer_po_no']");
    //     // if ($customer_po_no.length) {
    //     //     setTimeout(function() { $customer_po_no.select(); $customer_po_no.change(); }, 300);
    //     // }
    //     calculateTotal('#dynamic-table tr.gradeX', PO_ROW_INDEX_ITEM_QTY, PO_ROW_INDEX_ITEM_PRICE, PO_ROW_INDEX_AMOUNT, PO_LABEL_INDEX_AMOUNT, decimal_place);
    // });
}

function calculatePOTotal(last_amount, new_amount) {
    // console.log(last_amount, new_amount, $('#id_subtotal').val());
    var tax_rate = float_format($('#hdTaxRate').val());
    var last_subtotal = float_format($('#id_subtotal').val());
    var new_subtotal = last_subtotal - last_amount + new_amount;
    
    $('#id_subtotal').val(comma_format(new_subtotal, decimal_place)).trigger('change');
    var tax_amount = 0;
    var total = 0;
    if (tax_rate > 0){
        tax_amount = (float_format(tax_rate) * new_subtotal) / 100;
    }
    tax_amount = roundDecimal(tax_amount, decimal_place)
    $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
    if ($('#id_discount').val() == '' || $('#id_discount').val() == null) {
        total = new_subtotal + float_format($('#id_tax_amount').val());
    } else {
        total = new_subtotal + float_format($('#id_tax_amount').val()) - float_format($('#id_discount').val());
    }
    total = roundDecimal(total, decimal_place)
    $('#id_total').val(comma_format(total, decimal_place));
}
