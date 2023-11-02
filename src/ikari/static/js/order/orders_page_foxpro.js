/**
 * Created by tho.pham on 5/26/2016.
 */
var initial_item_qty = [];
var item_supp = [];
var item_loc = [];
var item_list = [];
var item_info = [];
var allVals = [];
var emptyRow = '';
var editing_row = null;
var append_index = 0;
var location_data = [];
var $selected_row = [];
var append_or_prepend = false;
var order_is_decimal = 1;
var decimal_place = 2;
var invalid_data_list = [];
var invalid_message_list = [];
var is_disable_show_duplicate = false;
var is_copy = false;
var do_check_duplicate_again = true;
var part_current_row = null;
var th_object = {
    'th-0': 'No',
    'th-1': 'Part No',
    'th-2': 'Quantity',
    'th-3': 'Unit Price',
    'th-4': 'Customer Po'
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
                        <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none;" type="text" value="1">
                    </td>
                    <td>
                        <div class="col-md-12" style="width: 280px; padding: 0px !important">
                            <div class="col-md-9" style="width: 250px; padding: 0px !important">
                                <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="text-align: left; width: 250px;" required="required" type="text">
                            </div>
                            <div class="col-md-3" style="width: 10px; padding: 0px !important">
                                <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-partno" name="search-partno" data-toggle="modal" href="#partListModal"></button>
                            </div>
                        </div>
                    </td>
                    <td style="display: none;">
                        <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" type="text">
                        <input class="form-control-item" id="id_formset_item-0-identity" name="formset_item-0-identity" type="text">
                    </td>
                    <td><input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" required="required" style="text-align: left; width: 250px;" type="text"></td>
                    <td>
                        <input class="form-control default-date-picker" id="id_formset_item-0-wanted_fake_date" name="formset_item-0-wanted_fake_date" autocompltete="off" required="required" style="width: 110px; text-align: right;" type="text">
                        <input class="form-control hide" id="id_formset_item-0-wanted_date" name="formset_item-0-wanted_date" required="required" style="width: 110px; text-align: right;" type="text">
                    </td>

                    <td><label id="id_formset_item-0-bkord_quantity" class="control-label-item" name="formset_item-0-bkord_quantity">0.00</label>
                        <input class="form-control-item hide" id="id_formset_item-0-bkord_quantity" name="formset_item-0-bkord_quantity" readonly="True" step="0.1" min="0" style="text-align: right; width: 120px;" type="number">
                    </td>
                    <td><select class="form-control" id="id_formset_item-0-supplier" name="formset_item-0-supplier" style="width: 150px; text-align: left;"></select>
                        <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                    <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency">USD</label>
                        <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item text-right numeric_price" id="id_formset_item-0-price" value="0.000000" min="0" name="formset_item-0-price" step="0.000001" style="text-align: right; width: 140px;" type="number"></td>
                    <td style="text-align: right;"><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount">0.00</label>
                        <input class="form-control-item text-right hide" id="id_formset_item-0-amount" name="formset_item-0-amount" step="any" style="text-align: right; width: 120px;" type="number">
                    </td>
                    <td>
                        <select class="form-control" id="id_formset_item-0-location" name="formset_item-0-location" style="width: 120px; text-align: left;">
                        </select>
                    </td>
                    <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom">PIECES</label>
                        <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category" style="width: 80px;">SJ-5603</label>
                        <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                    </td>
                    <td>
                        <input class="form-control default-date-picker" id="id_formset_item-0-schedule_fake_date" name="formset_item-0-schedule_fake_date" autocompltete="off" style="width: 110px; text-align: right;" type="text">
                        <input class="form-control hide" id="id_formset_item-0-schedule_date" name="formset_item-0-schedule_date" style="width: 110px; text-align: right;" type="text">
                    </td>
                    <td><input class="form-control-item" id="id_formset_item-0-description" name="formset_item-0-description" style="text-align: left; width: 400px;" type="text"></td>
                    <td style="display: none;"><input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="text-align: right; width: 40px;" type="text"></td>
                    <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" step="0.000000001" style="text-align: right; width: 80px;" type="number"></td>
                    <td style="display: none;"><input type="text" name="txt_onhand" id="txt_onhand" value="0"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
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
                        <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none;" type="text" value="1">
                    </td>
                    <td>
                        <div class="col-md-12" style="width: 280px; padding: 0px !important">
                            <div class="col-md-9" style="width: 250px; padding: 0px !important">
                                <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="text-align: left; width: 250px;" required="required" type="text">
                            </div>
                            <div class="col-md-3" style="width: 10px; padding: 0px !important">
                                <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-partno" name="search-partno" data-toggle="modal" href="#partListModal"></button>
                            </div>
                        </div>
                    </td>
                    <td style="display: none;">
                        <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;"></label>
                        <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" type="text">
                        <input class="form-control-item" id="id_formset_item-0-identity" name="formset_item-0-identity" type="text">
                    </td>
                    <td><input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" required="required" style="text-align: left; width: 250px;" type="text"></td>
                    <td>
                        <input class="form-control default-date-picker" id="id_formset_item-0-wanted_fake_date" name="formset_item-0-wanted_fake_date" autocompltete="off" required="required" style="width: 110px; text-align: right;" type="text">
                        <input class="form-control hide" id="id_formset_item-0-wanted_date" name="formset_item-0-wanted_date" required="required" style="width: 110px; text-align: right;" type="text">
                    </td>

                    <td><label id="id_formset_item-0-bkord_quantity" class="control-label-item" name="formset_item-0-bkord_quantity">0.00</label>
                        <input class="form-control-item hide" id="id_formset_item-0-bkord_quantity" name="formset_item-0-bkord_quantity" readonly="True" step="0.1" style="text-align: right; width: 120px;" type="number">
                    </td>
                    <td><select class="form-control" id="id_formset_item-0-supplier" name="formset_item-0-supplier" style="width: 150px; text-align: left;"></select>
                        <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" value="0.00" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                    <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency">USD</label>
                        <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                    </td>
                    <td><input class="form-control-item text-right numeric_price" id="id_formset_item-0-price" value="0.000000" min="0" name="formset_item-0-price" step="0.000001" style="text-align: right; width: 140px;" type="number"></td>
                    <td style="text-align: right;"><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount">0.00</label>
                        <input class="form-control-item text-right hide" id="id_formset_item-0-amount" name="formset_item-0-amount" step="any" style="text-align: right; width: 120px;" type="number">
                    </td>

                    <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom">PIECES</label>
                        <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                    </td>
                    <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category" style="width: 80px;">SJ-5603</label>
                        <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                    </td>
                    <td>
                        <input class="form-control default-date-picker" id="id_formset_item-0-schedule_fake_date" name="formset_item-0-schedule_fake_date" autocompltete="off" style="width: 110px; text-align: right;" type="text">
                        <input class="form-control hide" id="id_formset_item-0-schedule_date" name="formset_item-0-schedule_date" style="width: 110px; text-align: right;" type="text">
                    </td>
                    <td><input class="form-control-item latest_tag" id="id_formset_item-0-description" name="formset_item-0-description" style="text-align: left; width: 400px;" type="text"></td>
                    <td style="display: none;"><input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="text-align: right; width: 40px;" type="text"></td>
                    <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" step="0.000000001" style="text-align: right; width: 80px;" type="number"></td>
                    <td style="display: none;"><input type="text" name="txt_onhand" id="txt_onhand" value="0"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-delivery_quantity" name="formset_item-0-delivery_quantity" step="0.1" style="display: none" type="number"></td>
                    <td style="display: none"><input class="form-control-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" step="0.1" style="display: none" type="number"></td>

                </tr>`;
}

var SO_ROW_INDEX_LINE_NUMBER = 0;
var SO_ROW_INDEX_CODE = SO_ROW_INDEX_LINE_NUMBER + 1;
var SO_ROW_INDEX_ITEM_NAME = SO_ROW_INDEX_CODE + 1;
var SO_ROW_INDEX_ITEM_ID = SO_ROW_INDEX_ITEM_NAME + 1;
var SO_ROW_INDEX_IDENTITY = SO_ROW_INDEX_ITEM_ID + 1;
var SO_ROW_INDEX_CUSTOMER_PO = SO_ROW_INDEX_IDENTITY + 1;
var SO_ROW_INDEX_WANTED_FAKE_DATE = SO_ROW_INDEX_CUSTOMER_PO + 1;
var SO_ROW_INDEX_WANTED_DATE = SO_ROW_INDEX_WANTED_FAKE_DATE + 1;
var SO_ROW_INDEX_BACKORDER_QTY = SO_ROW_INDEX_WANTED_DATE + 1;
var SO_ROW_INDEX_SUPPLIER_CODE = SO_ROW_INDEX_BACKORDER_QTY + 1;
var SO_ROW_INDEX_SUPPLIER_ID = SO_ROW_INDEX_SUPPLIER_CODE + 1;
var SO_ROW_INDEX_ITEM_QTY = SO_ROW_INDEX_SUPPLIER_ID + 1;
var SO_ROW_INDEX_CURRENCY_CODE = SO_ROW_INDEX_ITEM_QTY + 1;
var SO_ROW_INDEX_CURRENCY_ID = SO_ROW_INDEX_CURRENCY_CODE + 1;
var SO_ROW_INDEX_ITEM_PRICE = SO_ROW_INDEX_CURRENCY_ID + 1;
var SO_ROW_INDEX_AMOUNT = SO_ROW_INDEX_ITEM_PRICE + 1;
var SO_ROW_INDEX_UOM = SO_ROW_INDEX_AMOUNT + 1;
var SO_ROW_INDEX_CATEGORY = SO_ROW_INDEX_UOM + 1;
var SO_ROW_INDEX_SCHEDULE_FAKE_DATE = SO_ROW_INDEX_CATEGORY + 1;
var SO_ROW_INDEX_SCHEDULE_DATE = SO_ROW_INDEX_SCHEDULE_FAKE_DATE + 1;
var SO_ROW_INDEX_DESCRIPTION = SO_ROW_INDEX_SCHEDULE_DATE + 1;
var SO_ROW_INDEX_REFER_LINE = SO_ROW_INDEX_DESCRIPTION + 1;
var SO_ROW_INDEX_EXCHANGE_RATE = SO_ROW_INDEX_REFER_LINE + 1;
var SO_ROW_INDEX_QTY_RFS = SO_ROW_INDEX_EXCHANGE_RATE + 1;
var SO_ROW_INDEX_MIN_ORDER_QTY = SO_ROW_INDEX_QTY_RFS + 1;

var SO_LABEL_INDEX_LINE_NUMBER = 0;
var SO_LABEL_INDEX_ITEM_NAME = SO_LABEL_INDEX_LINE_NUMBER + 1;
var SO_LABEL_INDEX_BACKORDER_QTY = SO_LABEL_INDEX_ITEM_NAME + 1;
// var SO_LABEL_INDEX_SUPPLIER_CODE = SO_LABEL_INDEX_BACKORDER_QTY + 1;
var SO_LABEL_INDEX_CURRENCY_CODE = SO_LABEL_INDEX_BACKORDER_QTY + 1;
var SO_LABEL_INDEX_AMOUNT = SO_LABEL_INDEX_CURRENCY_CODE + 1;
var SO_LABEL_INDEX_UOM = SO_LABEL_INDEX_AMOUNT + 1;
var SO_LABEL_INDEX_CATEGORY = SO_LABEL_INDEX_UOM + 1;

// var SO_SELECT_INDEX_ITEM_CODE = 0;
var SO_SELECT_INDEX_SUPPLIER = 0;
var SO_SELECT_INDEX_LOCATION = ($('#company_is_inventory').val() == 'True') ? SO_SELECT_INDEX_SUPPLIER + 1 : -1;

/* SO Column Index */

var SO_COL_BUTTONS = 0; // 0
var SO_COL_LINE_NUMBER = SO_COL_BUTTONS + 1; // 1
var SO_COL_PART_NO = SO_COL_LINE_NUMBER + 1; // 2
var SO_COL_ITEM_NAME = SO_COL_PART_NO + 1; // 3
var SO_COL_CUSTOMER_PO = SO_COL_ITEM_NAME + 1; // 4
var SO_COL_WANTED_DATE = SO_COL_CUSTOMER_PO + 1; // 5
var SO_COL_BACK_QTY = SO_COL_WANTED_DATE + 1; // 6
var SO_COL_SUPPLIER_CODE = SO_COL_BACK_QTY + 1; // 7
var SO_COL_QTY = SO_COL_SUPPLIER_CODE + 1; // 8
var SO_COL_CURRENCY = SO_COL_QTY + 1; // 9
var SO_COL_PRICE = SO_COL_CURRENCY + 1; // 10
var SO_COL_AMOUNT = SO_COL_PRICE + 1; // 111
if($('#company_is_inventory').val() == 'True') {
    var SO_COL_LOC_CODE = SO_COL_AMOUNT + 1; // 12
    var SO_COL_UOM = SO_COL_LOC_CODE + 1; // 13
} else {
    var SO_COL_UOM = SO_COL_AMOUNT + 1; // 13
}
var SO_COL_PART_GROUP = SO_COL_UOM + 1; // 14
var SO_COL_SCHEDULE_DATE = SO_COL_PART_GROUP + 1; // 15
var SO_COL_REMARK = SO_COL_SCHEDULE_DATE + 1; // 16
var SO_COL_REF_LINE = SO_COL_REMARK + 1; // 17
var SO_COL_EXCHANGE_RATE = SO_COL_REF_LINE + 1; // 18
var SO_COL_QTY_ON_HAND = SO_COL_EXCHANGE_RATE + 1; // 19
var SO_COL_MIN_ORDER = SO_COL_QTY_ON_HAND + 1; // 20

var doc_ready = false;
function get_location_list() {
    $.ajax({
        method: "GET",
        url: '/orders/location_code_list/',
        dataType: 'JSON',
        success: function (json) {
            location_data = json;
        }
    });
}
if (!$('#id_customer').val()){
    $('#dynamic-table tbody').find('tr.gradeX:last').remove();
    let total = parseInt($('#id_formset_item-TOTAL_FORMS').val());
    total--;
    $('#id_formset_item-TOTAL_FORMS').val(total);
    append_index = $('#dynamic-table').find('tr.gradeX').length;
}
$(document).ready(function () {
    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });

    $('#id_customer').on('blur', function (e)
    {
        $('#id_document_date_fake').focus();
    });

    $('#id_cost_center').on('select2:close', function (e)
    {
        $('.editrow').focus();
    });

    if($('#company_is_inventory').val() == 'True') {
        get_location_list();
    }
    if (!$('#id_customer').val()){
        $('#id_currency').val(0);
        $('#btnOpenItemDialog').attr('disabled', 'disabled');
        $('#txtPartNo').prop('disabled', true);
    } else {
        if($('#id_customer').val()) {
            setTimeout(() => {
                if ($('#dynamic-table tr.gradeX:last').attr('data-is_database') == 'None') {
                    $('#dynamic-table tr.gradeX:last').remove();
                    $('#id_formset_item-TOTAL_FORMS').val($('#id_formset_item-TOTAL_FORMS').val() - 1);
                    $('#dynamic-table tbody').find('tr.gradeX:last').find('td:first').find('div').find('.appendrow').prop('disabled', false);
                }
                append_index = $('#dynamic-table').find('tr.gradeX').length;
            }, 200);
            load_part_numbers();
            handleQuantity();
            handleEventTable();
        }
    }
    if (($('#id_customer').val() > 0) && (!$('#id_exchange_rate').val())) {
        load_cuss();
    } else {
        $('#id_exchange_rate_value').val($('#id_exchange_rate').val());
    }
    var theday = dateView($("#id_document_date").val());
    $("#id_document_date_fake").val(theday);
    $('#id_document_date').addClass('hide');
    $('#selector_currency').addClass('hide');
    var name_curr = $("#selector_currency option:selected").text();
    $('#name_currency').val(name_curr);
    // $('#id_tax option:not(:selected)').attr('disabled', true);
    // $('form input').on('keypress', function (e) {
    //     return e.which !== 13;
    // });

    // Customer
    // $('#id_customer').select2({
    //     placeholder: "Select Customers",
    // });
    // $('#id_customer').on("select2:open", function( event ){
    //     prefill_select2(event);
    // });

    // Currency
    $('#id_currency').select2({
        placeholder: "Select currency",
    });
    $('#id_currency').on("select2:open", function( event ){
        prefill_select2(event);
    });

     $('#id_cost_center').select2({
        placeholder: "Select Cost Center",
    });

    $('#id_transaction_code').select2();
    $('.location_select select').select2();

    $('#id_customer').on('change', function() {
        $('#btnOpenItemDialog').removeAttr('disabled');
        $('#txtPartNo').prop('disabled', false);
        $('#dynamic-table tbody').find('tr').remove();
        $('#id_subtotal').val(0);
        $('#id_total').val(0);
        $('#id_tax_amount').val(0);
        $(emptyRow).insertBefore('#id_formset_item-TOTAL_FORMS');
        disableAutoComplete();
        $('#id_formset_item-TOTAL_FORMS').val('1');
        load_cuss();
        load_part_numbers();
        setTimeout(() => {
            initiatePartNumber('#dynamic-table tr.gradeX:last');
        }, 1000);
        append_index = 1;

    });

    // $("#id_reference_number").bind('keydown', function(event) {
    //     if (event.which == 13) {
    //         $('#dynamic-table tr.gradeX select:first').select2('open');
    //
    //         return false;
    //     }
    // });

    // if (!$('#id_customer').val()){
    //     $('#id_customer').select2("open");
    // }
    $('#id_customer').focus();


    if ($('#dynamic-table tr.gradeX').length == 1) {
        $('#dynamic-table tr.gradeX .removerow').prop('disabled', true);
    }

    if ($('#dynamic-table tr.gradeX input:nth-child('+SO_ROW_INDEX_ITEM_ID+')').val() == '') {
        $('#dynamic-table tr.gradeX label').html('');
    }

    // Replace currency symbol
    var currency_id = parseInt($('#id_currency option:selected').val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];

    $('#dynamic-table tr.gradeX').each(function () {
        currentRow = $(this).closest('tr').find('input');
        currentLabel = $(this).closest('tr').find('label');
        arrItems.push({
            item_id: currentRow[SO_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[SO_ROW_INDEX_CURRENCY_ID].value
        });
        currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[SO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
    });

    if (arrItems.length > 0) changeCurrency(arrItems, currency_id, currency_name);

    /** Initial code for calculate backorder */

    $('#dynamic-table tr.gradeX:visible').each(function () {
        var currentRow = $(this).find('input');
        var currentLabel = $(this).find('label');

        var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
        var backorder_qty = float_format(currentRow[SO_ROW_INDEX_BACKORDER_QTY].value);
        var onhand_qty = float_format(currentRow[SO_ROW_INDEX_QTY_RFS].value);

        if (isNaN(backorder_qty)) {
            backorder_qty = 0;
        }

        quantity = (isNaN(quantity)) ? 0.00 : quantity;

        var backorder = get_backorder_qty(onhand_qty, quantity, backorder_qty);

        currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(backorder, 2);
        currentRow[SO_ROW_INDEX_ITEM_QTY].value = comma_format(quantity, 2);
    });

    // $('#form').on('submit', function() {
    //     console.log($(this).serializeArray());
    //     return false;
    // });
});

$(document).on("input", "#id_customer_code", function() {
    this.value = this.value.toUpperCase();
});

$('#id_customer_code').on('change', function() {
    var cus_code = $(this).val();
    $.ajax({
        type: "GET",
        url: "/customers/get_by_code/"+cus_code+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                $('#id_customer').val(data.data[0].id).trigger('change');
            } else {
                $('#dynamic-table tbody').find('tr').remove();
                pop_ok_dialog("Invalid Customer Code",
                cus_code + " is not found in the system, try again.",
                function () {
                    $('#id_customer_code').val('');
                    $('#id_customer_code').focus();
                });
            }
        }
    });
})

function check_linked(refer_line) {
    let is_linked = false;
    if ($('#id_document_number').val()) {

        var founds = $.grep(order_items, function(v) {
            if (v.refer_line == refer_line && v.refer_number == $('#id_document_number').val()) {
                return v;
            }
        });

        if (founds.length > 0) {
            linked_reference(founds);
            is_linked = true;
        }
    }
    return is_linked;
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
    //fix table index
    fix_table_row_indexes();

    change_refer_line();
    $('#index_order_items').val(JSON.stringify(order_items));

    $('#id_subtotal').val(float_format($('#id_subtotal').val()));
    $('#id_total').val(float_format($('#id_total').val()));
    $('#id_tax_amount').val(float_format($('#id_tax_amount').val()));

    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).find('input');
        qty = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
        currentRow[SO_ROW_INDEX_ITEM_QTY].value = qty;
    });
}

function disableShowDuplicate() {
    is_disable_show_duplicate = true;
}

function enableShowDuplicate() {
    is_disable_show_duplicate = false;
}

function validate_cuspo_so_copy() {
    // check duplicate customer_po
    var duplicate_cuspo_list = [];
    var has_location = false;
    if ($('#company_is_inventory').val() == 'True') {
        has_location = true;
    }
    $('#dynamic-table tr.gradeX').each(function (i, v) {
        var cRow = $(this).closest('tr').find('input');
        var cLabel = $(this).closest('tr').find('label');
        var cpo = cRow[SO_ROW_INDEX_CUSTOMER_PO].value;
        var citem = cRow[SO_ROW_INDEX_CODE].value;
        var s_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_SUPPLIER].id;
        var csup = $(s_select).select2('data')[0].text;
        var loc = '';
        if ($('#company_is_inventory').val() == 'True') {
            $l_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_LOCATION].id;
            loc = $($l_select).select2('data')[0].text;
        }
        var data = {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'cust_po_no': cpo,
            'item_id': cRow[SO_ROW_INDEX_ITEM_ID].value,
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
                        duplicate_cuspo_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, loc]);
                    }
                } else {
                    duplicate_cuspo_list.push([data[0].ln_no, data[0].doc_no, citem, cpo, csup, '']);
                    duplicate_cuspo_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, '']);
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
            $('#form').attr('action','/orders/order_edit/' + order_id + '/1/1/0/');
            $('#form').submit();
        }
        $('#loading').hide();
    }, 1500);
}

$(document).ready(function () {
    // Remove required attribute on modal
    $('#modal_w_date').removeAttr('required');
    $('#modal_customer_po_no').removeAttr('required');    

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

            var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
            var unitPrice = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);

            if (quantity == 0 || unitPrice == 0) {
                is_valid = false;
                invalid_data_list.push({
                    ln: currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
                    // part_no: $('#'+currentSelect[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').text(),
                    part_no: currentRow[SO_ROW_INDEX_CODE].value,
                    quantity: currentRow[SO_ROW_INDEX_ITEM_QTY].value,
                    unitPrice: currentRow[SO_ROW_INDEX_ITEM_PRICE].value,
                    custPO: currentRow[SO_ROW_INDEX_CUSTOMER_PO].value,
                    // refer_line: currentRow[DO_ROW_INDEX_REFER_LINE].value,
                    // refer_doc: currentRow[DO_ROW_INDEX_REFER_NO].value,
                    // item_id: currentRow[DO_ROW_INDEX_ITEM_ID].value,
                    // ord_qty: float_format(currentRow[DO_ROW_INDEX_ORDER_QTY].value),
                    // qty_dlv: float_format(currentRow[DO_ROW_INDEX_DELIVERY_QTY].value),
                    // qty: float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value),
                    // order_id: $(currentLabel[1]).data('code_data')
                });


            }

            // allTableData.push({
            //     ln: currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent,
            //     part_no: $('#'+currentSelect[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').text(),
            //     quantity: currentRow[SO_ROW_INDEX_ITEM_QTY].value,
            //     unitPrice: currentRow[SO_ROW_INDEX_ITEM_PRICE].value,
            //     custPO: currentRow[SO_ROW_INDEX_CUSTOMER_PO].value,
            // });
        });
        if (!is_valid) {
            invalid_message_list.push("Please insert a valid quantity or unit price. The value can't be 0.");
            show_invalid_modal(invalid_data_list, invalid_message_list, disableShowDuplicate(), enableShowDuplicate(), th_object);
            e.preventDefault();
            return false;
        } else {
            // check duplicate
            // allTableData.sort(SortBypartNo);

            // var duplicate_data_list = [];
            // for (var i = 0; i < allTableData.length - 1; i++) {
            //     if (allTableData[i + 1].part_no == allTableData[i].part_no) {
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
                if (is_copy && do_check_duplicate_again) {
                    $('#loading').show();
                    validate_cuspo_so_copy();
                    e.preventDefault();
                    return false;
                } else {
                    fixForm();
                    checkForm(this);
                }
            // }
        }
    });
});

// $(document).keypress(function (e) {
//     if (e.which == 13){
//         if (!$(event.target).is("textarea")) {
//             e.preventDefault();
//         }
//     };
// });

//Add Extra Label Value formset
$(document).ready(function () {
    checkDisplay();

    $('#add_more_right').click(function () {
        cloneMore('div.table-right:last', 'formset_right');
    });
    $('#add_more_left').click(function () {
        cloneMore('div.table-left:last', 'formset_left');
    });
    $('#add_more_code').click(function () {
        cloneMore('div.table-code:last', 'formset_code');
    });

    function checkDisplay() {
        var request_method = $('#request_method').val();
        if (request_method == 'GET') {
            if ($('#id_formset_right-TOTAL_FORMS').val() > 1) {
                $('div.table-right:last').remove();
                $('#id_formset_right-TOTAL_FORMS').val($('#id_formset_right-TOTAL_FORMS').val() - 1);
            } else {
                $('div.table-right:last').css("display", "none");
            }
            if ($('#id_formset_left-TOTAL_FORMS').val() > 1) {
                $('div.table-left:last').remove();
                $('#id_formset_left-TOTAL_FORMS').val($('#id_formset_left-TOTAL_FORMS').val() - 1);
            } else {
                $('div.table-left:last').css("display", "none");
            }
            if ($('#id_formset_code-TOTAL_FORMS').val() > 1) {
                $('div.table-code:last').remove();
                $('#id_formset_code-TOTAL_FORMS').val($('#id_formset_code-TOTAL_FORMS').val() - 1);
            } else {
                $('div.table-code:last').css("display", "none");
            }
            if ($('#dynamic-table').find('tr.gradeX').length <= 1) {
                // $('#dynamic-table tr.gradeX:last select:first').select2({
                //     placeholder: 'Select Part Number'
                // });
            }
            else {
                $('#dynamic-table tr.gradeX:last').hide();
            }
            $('#items_error').css("display", "none");
        } else if (request_method == 'POST') {
            var right_label = $('#id_formset_right-0-label').val();
            var right_somevalue = $('#id_formset_right-0-value').val();
            if (right_label == "" && right_somevalue == "") {
                $('div.table-right:last').css("display", "none");
            }
            var left_label = $('#id_formset_left-0-label').val();
            var left_somevalue = $('#id_formset_left-0-value').val();
            if (left_label == "" && left_somevalue == "") {
                $('div.table-left:last').css("display", "none");
            }
            var code_label = $('#id_formset_code-0-label').val();
            var code_somevalue = $('#id_formset_code-0-value').val();
            if (code_label == "" && code_somevalue == "") {
                $('div.table-code:last').css("display", "none");
            }
            var item = $('#id_formset_item-0-item').val();
            var quantity = $('#id_formset_item-0-quantity').val();
            var price = $('#id_formset_item-0-price').val();
            var amount = $('#id_formset_item-0-amount').val();
            if (quantity == "" && price == "" && amount == "") {
                $('#dynamic-table tr.gradeX:last').css("display", "none");
                $('#items_error').removeAttr('style');
            } else $('#items_error').css("display", "none");
        }
    }

    // $(document).on('click', "[class^=removerow-left]", function () {
    //     if ($('#id_formset_left-TOTAL_FORMS').val() == 1) {
    //         var total = $('#id_formset_left-TOTAL_FORMS').val();
    //         $('div.table-left:last').find(':input').each(function () {
    //             var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
    //             var id = 'id_' + name;
    //             $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
    //         });
    //         $(this).parents("div.table-left:last").css("display", "none")
    //     } else {
    //         var minus = $('input[name=formset_left-TOTAL_FORMS]').val() - 1;
    //         $('#id_formset_left-TOTAL_FORMS').val(minus);
    //         $(this).parents("div.table-left").remove();
    //         var i = 0;
    //         $('div.table-left').each(function () {
    //             var currentRow = $(this).find('input');
    //             var label = currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //             var value = currentRow[SO_ROW_INDEX_CODE].name;
    //             if (label.replace(/[^\d.]/g, '') == 0) {
    //                 i++;
    //             } else {
    //                 for (i; i < minus; i++) {
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].name = label.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].id = 'id_' + currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //                     currentRow[SO_ROW_INDEX_CODE].name = value.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_CODE].id = 'id_' + currentRow[SO_ROW_INDEX_CODE].name;
    //                     i++;
    //                     break;
    //                 }
    //             }
    //         });
    //     }
    // });

    // $(document).on('click', "[class^=removerow-right]", function () {
    //     if ($('#id_formset_right-TOTAL_FORMS').val() == 1) {
    //         var total = $('#id_formset_right-TOTAL_FORMS').val();
    //         $('div.table-right:last').find(':input').each(function () {
    //             var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
    //             var id = 'id_' + name;
    //             $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
    //         });
    //         $(this).parents("div.table-right").css("display", "none");
    //     } else {
    //         var minus = $('input[name=formset_right-TOTAL_FORMS]').val() - 1;
    //         $('#id_formset_right-TOTAL_FORMS').val(minus);
    //         $(this).parents("div.table-right").remove();
    //         var i = 0;
    //         $('div.table-right').each(function () {
    //             var currentRow = $(this).find('input');
    //             var label = currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //             var value = currentRow[SO_ROW_INDEX_CODE].name;
    //             if (label.replace(/[^\d.]/g, '') == 0) {
    //                 i++;
    //             } else {
    //                 for (i; i < minus; i++) {
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].name = label.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].id = 'id_' + currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //                     currentRow[SO_ROW_INDEX_CODE].name = value.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_CODE].id = 'id_' + currentRow[SO_ROW_INDEX_CODE].name;
    //                     i++;
    //                     break;
    //                 }
    //             }
    //         });
    //     }
    // });
    //
    // $(document).on('click', "[class^=removerow-code]", function () {
    //     if ($('#id_formset_code-TOTAL_FORMS').val() == 1) {
    //         var total = $('#id_formset_code-TOTAL_FORMS').val();
    //         $('div.table-code:last').find(':input').each(function () {
    //             var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
    //             var id = 'id_' + name;
    //             $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
    //         });
    //         $(this).parents("div.table-code").css("display", "none")
    //     } else {
    //         var minus = $('input[name=formset_code-TOTAL_FORMS]').val() - 1;
    //         $('#id_formset_code-TOTAL_FORMS').val(minus);
    //         $(this).parents("div.table-code").remove();
    //         var i = 0;
    //         $('div.table-code').each(function () {
    //             var currentRow = $(this).find('input');
    //             var label = currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //             var value = currentRow[SO_ROW_INDEX_CODE].name;
    //             if (label.replace(/[^\d.]/g, '') == 0) {
    //                 i++;
    //             } else {
    //                 for (i; i < minus; i++) {
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].name = label.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_LINE_NUMBER].id = 'id_' + currentRow[SO_ROW_INDEX_LINE_NUMBER].name;
    //                     currentRow[SO_ROW_INDEX_CODE].name = value.replace(/\d+/g, i);
    //                     currentRow[SO_ROW_INDEX_CODE].id = 'id_' + currentRow[SO_ROW_INDEX_CODE].name;
    //                     i++;
    //                     break;
    //                 }
    //             }
    //         });
    //     }
    // });

    // $(document).on('focusout', "input[id^=id_formset_item-][id$=-description]", function () {
        // $('select[id^=id_select-][id$=-ref_number]')
        // 0-description

    // });
});

// $('input[id^=id_formset_item-][id$=-description]').on("keydown", function (e) {
//     let code_pressed = e.which;
//     let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
//     tabAddRow(rowIndex, code_pressed);
//     // just tab key
// });

$('#id_document_date_fake').on('change', function() {

    var date_from = get_date_from("#id_document_date_fake");
    date_from = date_from.split('/').join('-');
    var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();
    if (!date_from_valid){

        $("#id_document_date_fake").val(moment($("#id_document_date").val(),"YYYY-MM-DD").format("DD-MM-YYYY"));
    }else{

        var date_rate_1 = dateView(date_from);
        $("#id_document_date").val(date_rate_1);

        var rate_type = 3
        var curr_to = $('#id_currency').val();
        if ($('#id_customer').val() > 0){
            recort_rate(curr_to,date_rate_1,rate_type)
        }
    }
});

$('#id_document_date_fake').keyup(function(event){
    adjust_input_date(this);
});


//Load tax rate
$(document).ready(function () {
    $('#id_tax').change(function (e) {
        var taxid = parseInt($(this).val());
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
                    $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
                    var total = float_format($('#id_subtotal').val()) + tax_amount - float_format($('#id_discount').val());
                    $('#id_total').val(comma_format(total, decimal_place));
                }
            });
        }
    });
});

//Load and edit inline Customer information
$(document).ready(function () {
    var callback = function () {
        $.ajax({
            method: "POST",
            url: '/orders/customer_search_by_code/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'customer_code': $("#form_customer_code").val()
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
                $('#hdCustomerId').val(json['id']);
                $("#form_customer_code").val(json['code']);
                $('#customer_name').editable('destroy');
                $('#customer_address').editable('destroy');
                $('#customer_email').editable('destroy');

                $('#customer_name').attr('data-pk', json['id']);
                $('#customer_name').text(json['name']);
                $('#customer_address').text(json['address']);

                $('#customer_email').attr('data-pk', json['id']);
                $('#customer_email').text(json['email']);
                $('#customer_payment_term').text(json['term'] + ' days');
                $('#customer_payment_mode').text(json['payment_mode']);
                $('#customer_credit_limit').text(json['credit_limit']);
                loadCustomerInfo(json['id']);
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
                            $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
                            var total = float_format($('#id_subtotal').val()) + tax_amount - float_format($('#id_discount').val());
                            $('#id_total').val(comma_format(total, decimal_place));
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
    $("#form_customer_code").keypress(function (e) {

        if (e.which == 13) {
            e.preventDefault();
            callback();
        }
    });

    $('#btnSearchCustomer').on('click', function () {
        $('#customer-table').DataTable().destroy();
        $('#customer-table').dataTable({
            "iDisplayLength": 5,
            "bLengthChange": false,
            "order": [[0, "desc"]],
            "serverSide": true,
            "ajax": {
                "url": "/orders/customers_list_as_json/"
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "name", "sClass": "text-left"},
                {"data": "payment_term", "sClass": "text-left"},
                {"data": "payment_mode", "sClass": "text-left"},
                {"data": "credit_limit", "sClass": "text-left"},
                {
                    "orderable": false,
                    "data": null,
                    "sClass": "hide_column",
                    "render": function (data, type, full, meta) {
                        return '<input type="radio" name="choices" code="'+ full.code +'" id="' +
                            full.id + '" class="call-checkbox" value="' + full.id + '">';
                    }
                }
            ],
            "drawCallback": function(settings) {
                $('#myCustomerListModal .call-checkbox').on('click', function() {
                    if ($(this).is(':checked')) {
                        $('#id_customer').val($(this).val());
                        $('#id_customer option[value="'+$(this).val()+'"]').attr('selected', 'selected');
                        $('#id_customer').trigger('change');
                    }
                });

                $('#myCustomerListModal .call-checkbox[value="'+$('#id_customer').val()+'"]').attr('checked', 'checked');
            }
        });
    });

    $('#customer-table').on( 'draw.dt', function () {
        selectTableRow('#customer-table', 5);
        $("input[type='radio']").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
    });

    $('#btnCustomerSelect').on('click', function () {

        var customer_select_id = $("input[name='choices']:checked").attr('id');
        var customer_select_code = $("input[name='choices']:checked").attr('code');

        $('#hdCustomerId').val(customer_select_id);
        $('#id_customer').val(customer_select_id).trigger('change');
        $('#id_customer_code').val(customer_select_code);

        $('#id_currency option[value=' + customer_select_id + ']').attr('selected', 'selected');

        var nRow = $("input[name='choices']:checked").parents('tr')[0];
        var jqInputs = $('td', nRow);
        $("#form_customer_code").val(jqInputs[0].innerText);

        $(this).attr('data-dismiss', 'modal');
        callback();
    });

    $(document).on('click', '.search-partno', function () {
        part_current_row = $(this).closest('tr').find('input');
        if (item_list.length) {
            $('#part-table').DataTable().destroy();
            $('#part-table').dataTable({
                "iDisplayLength": 10,
                "bLengthChange": false,
                "data": item_list,
                "columns": [
                    {"data": "code", "sClass": "text-left"},
                    {"data": "name", "sClass": "text-left"},
                    {
                        "orderable": false,
                        "data": null,
                        "sClass": "hide_column",
                        "render": function (data, type, full, meta) {
                            return '<input type="radio" name="part-choices" code="'+ full.code +'" id="' +
                                full.id + '" class="call-checkbox" value="' + full.id + '">';
                        }
                    },
                    {"data": "id", "sClass": "text-left hide_column"},
                ],
            });
        } else {
            pop_ok_dialog("Warning!",
                "Part numbers are not loaded yet. wait some time & try again.",
                function () { }
            );
        }
    });

    $('#part-table').on( 'draw.dt', function () {
        selectTableRow('#part-table', 2);
        $("input[type='radio']").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
    });

    $('#btnPartSelect').on('click', function () {
        var part_id = $("input[name='part-choices']:checked").attr('id');
        var part_code = $("input[name='part-choices']:checked").attr('code');
        if (part_id) {
            if ($("#orderItemModal").is(':visible')) {
                $('#modal_part_item_code').val(part_code).trigger('change');
                setTimeout(() => {
                    $('#modal_customer_po_no').focus();
                }, 600);
            } else {
                part_current_row[SO_ROW_INDEX_ITEM_ID].value = part_id;
                $('#'+part_current_row[SO_ROW_INDEX_CODE].id).val(part_code).trigger('change');
                setTimeout(() => {
                    $('#'+part_current_row[SO_ROW_INDEX_CUSTOMER_PO].id).focus();
                }, 600);
            }
            $('#partListModal').modal('hide');
        } else {
            pop_ok_dialog("Warning!",
                "Select an item first",
                function () { }
            );
        }
    });

    function loadCustomerInfo(hdCustomerId) {
        $.fn.editable.defaults.mode = 'inline';

        //make status editable
        $('#customer_name').editable({
            type: 'text',
            pk: hdCustomerId,
            title: 'Enter customer name',
        });

        $('#customer_address').editable({
            type: 'text',
            pk: hdCustomerId,
            title: 'Enter customer address',
        });

        $('#customer_email').editable({
            type: 'text',
            pk: hdCustomerId,
            title: 'Enter customer email',
        });
    };

    var hdCustomerId = $('#id_customer').val();
    loadCustomerInfo(hdCustomerId);
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
    if ($('#id_formset_item-TOTAL_FORMS').val() > 1) {
        var display = $('#dynamic-table tr.gradeX:last').css("display");
        if (display == 'none') {
            $('#dynamic-table tr.gradeX:last').removeAttr("style");
            $('#dynamic-table tr.gradeX:last').remove();
            $('#id_formset_item-TOTAL_FORMS').val($('#id_formset_item-TOTAL_FORMS').val() - 1);
        }
    }

    function store_row_index(newRowIndex, curRowIndex) {
        var row_currency = $('#id_formset_item-'+ (curRowIndex) +'-currency_id').val();
        if($('#id_select-' + (curRowIndex) + '-refer_line').val() == null) {
            row_currency = '';
        }

        $selected_row.push({
            'row':newRowIndex,
            'ref_number': $('#id_formset_item-'+ (curRowIndex) +'-ref_number').val(),
            'qty': float_format($('#id_formset_item-'+ (curRowIndex) +'-quantity').val()),
            'po_no': $('#id_formset_item-'+ (curRowIndex) +'-customer_po_no').val(),
            'code': $('#id_formset_item-'+ (curRowIndex) +'-code').val(),
            'currency': row_currency,
            'price': float_format($('#id_formset_item-'+ (curRowIndex) +'-price').val()).toFixed(6),
            // 'exch_rate': $('#id_formset_item-'+ (rowIndex+1) +'-exchange_rate').val(),
            'amount': float_format($('#id_formset_item-'+ (curRowIndex) +'-amount').text()).toFixed(decimal_place),
            'category': $('#id_formset_item-'+ (curRowIndex) +'-category').text(),
            'bkord_quantity': $('#id_formset_item-'+ (curRowIndex) +'-bkord_quantity').text(),
            'wanted_date': $('#id_formset_item-'+ (curRowIndex) +'-wanted_date').val(),
            'wanted_fake_date': $('#id_formset_item-'+ (curRowIndex) +'-wanted_fake_date').val(),
            'schedule_date': $('#id_formset_item-'+ (curRowIndex) +'-schedule_date').val(),
            'schedule_fake_date': $('#id_formset_item-'+ (curRowIndex) +'-schedule_fake_date').val(),
            'description': $('#id_formset_item-'+ (curRowIndex) +'-description').val(),
            // 'supplier': $('#id_formset_item-'+ (curRowIndex) +'-supplier').text(),
            'supplier_code': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code').val(),
            'supplier_id': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code_id').val(),
            'uom': $('#id_formset_item-'+ (curRowIndex) +'-uom').text(),
        });

    }

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
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier').text($selected_row[i].supplier);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code').val($selected_row[i].supplier_code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code_id').val($selected_row[i].supplier_id);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-bkord_quantity').val($selected_row[i].bkord_quantity);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-bkord_quantity').text(comma_format($selected_row[i].bkord_quantity));
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').val($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').text($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').val(row_amout);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').text(comma_format(row_amout, decimal_place));
            $('#id_formset_item-'+ ($selected_row[i].row) +'-exchange_rate').val($selected_row[i].exch_rate);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-price').val($selected_row[i].price);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-price').text($selected_row[i].price);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-currency_id').val($selected_row[i].currency);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-code').val($selected_row[i].code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-code').text($selected_row[i].code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').val($selected_row[i].po_no);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').text($selected_row[i].po_no);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-quantity').val(comma_format($selected_row[i].qty, 2));
        }
        $('#loading').hide();
    }

    // var last_so_nimber = '';
    $(document).on('click', "[class^=removerow]", function (event) {
        // check refer line and Document Number had to link, if linked -> can not remove
        let line_number = $(this).closest('tr').attr('data-line_number');
        if (!is_copy && check_linked(line_number) == true) {
            return;
        }

        // remove logic
        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        last_amount = float_format($('#id_formset_item-'+(rowIndex)+'-amount').text());

        currentRow = $(this).closest('tr').find('input');
        item_id = currentRow[SO_ROW_INDEX_ITEM_ID].value;
        if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
            $(this).parents("tr").remove();
            $('#id_subtotal').val(0);
            $('#id_total').val(0);
            $('#id_tax_amount').val(0);
            let newRow = emptyRow;
            $('#id_formset_item-TOTAL_FORMS').before(newRow);
            newRow = $('#dynamic-table tr.gradeX:nth-child(1)').closest('tr');
            disableAutoComplete();
            initiatePartNumber(newRow);

        } else {
            fnEnableButton();
            var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
            $('#id_formset_item-TOTAL_FORMS').val(minus);
            $(this).parents("tr").remove();

            let rowNumber = 0;
            // let rows = $('#dynamic-table').find('tr.gradeX');
            $('#dynamic-table tr.gradeX').each(function () {
                let currentRow = $(this).closest('tr').find('input');
                let currentLine = $(this).closest('tr').find('label');
                currentLine[SO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber + 1);
                currentRow[SO_ROW_INDEX_LINE_NUMBER].value = (rowNumber + 1);
                rowNumber++;
            });
            // rowNumber = rows.length - 1;
            // $selected_row.length = 0;

            // while (rowNumber >= rowIndex) {
            //     store_row_index(rowNumber, rowNumber + 1);
            //     change_row_attr(rowNumber + 1, rowNumber + 1, rowNumber);
            //     rowNumber--;
            // }

            // if ($selected_row.length) {
            //     $('#loading').show();
            // }

            setTimeout(() => {
                // bindingData();
                calculateTotal('#dynamic-table tr.gradeX', SO_ROW_INDEX_ITEM_QTY, SO_ROW_INDEX_ITEM_PRICE,
                    SO_ROW_INDEX_AMOUNT, SO_LABEL_INDEX_AMOUNT, decimal_place);
                // store the new refer line
                change_refer_line();
            }, 100);
        }

    });

    function rowComplete() {
        let status = true;
        $('#dynamic-table tr.gradeX').each(function () {
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            var idFirstInvalid = getFirstFieldInvalid(rowCheck);
            if (idFirstInvalid != '') {
                highLightMandatory(rowCheck);
                // $(idFirstInvalid).focus();
                // if ($(idFirstInvalid).is('select')) {
                //     $(idFirstInvalid).select2('open');
                // }
                status = false;
                pop_focus_invalid_dialog('Warning!',
                'Please fill up the required fields.',
                function(){}
                , idFirstInvalid);
            }
        });
        return status;
    }

    $(document).on('click', "[class^=appendrow]", function (event) {
        // append logic
        if (rowComplete()) {
            let inputs = $(this).closest('tr').find('input');
            let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
            let cus_po_no = inputs[SO_ROW_INDEX_CUSTOMER_PO].value;
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
                currentLine[SO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
                currentRow[SO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
                rowNumber++;
            });
            // rowNumber = rows.length-1;
            // $selected_row.length = 0;

            // while(rowNumber > rowIndex) {
            //     store_row_index(rowNumber, rowNumber - 1);
            //     change_row_attr(rowNumber + 1, rowNumber - 1, rowNumber);
            //     rowNumber--;
            // }

            // if ($selected_row.length) {
            //     $('#loading').show();
            // }
            rowNumber = append_index;
            change_new_row_attr(rowIndex+1, rowNumber);
            append_index++;

            newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex+1)+')').closest('tr');
            initiatePartNumber(newRow);

            setTimeout(() => {
                // bindingData();
                $('#id_formset_item-' + rowNumber + '-customer_po_no').val(cus_po_no);
                // store the new refer line
                change_refer_line();
            }, 100);
        }
    });

    $(document).on('click', "[class^=prependrow]", function (event) {
        if (rowComplete()) {
            let inputs = $(this).closest('tr').find('input');
            let cus_po_no = inputs[SO_ROW_INDEX_CUSTOMER_PO].value;
            let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
            let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let prev_rowIndex = parseInt($(this).closest('tr').prev().attr('data-row_index'));
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
                currentLine[SO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
                currentRow[SO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
                rowNumber++;
            });

            // if ($selected_row.length) {
            //     $('#loading').show();
            // }

            //initialize select2 of new row
            rowNumber = append_index;
            change_new_row_attr(rowIndex, rowNumber);
            append_index++;
            newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').closest('tr');

            initiatePartNumber(newRow);

            setTimeout(() => {
                // bindingData();
                $('#id_formset_item-' + (rowNumber) + '-customer_po_no').val(cus_po_no);
                // store the new refer line
                change_refer_line();
            }, 100);
        }
    });

    var next = false;
    var prev = false;
    var dyn_tbl_sel_row_id = 0;
    var line_object = {
        'part_item': '',
        'cust_po': '',
        'w_date': '',
        's_date': '',
        'qty': '',
        'price': '',
        'remark': ''
    }
    var action_button = '';

    function next_prev_action() {
        if(next) {
            // selectedRowId = dyn_tbl_sel_row_id + 1;
            // var row = $('#dynamic-table tr.gradeX')[selectedRowId];
            // var valid = ($(row).length != 0);
            // if (valid) {
            //     loadOrderItemModal(selectedRowId);
            // }
            if (editing_row.next().hasClass('gradeX')) {
                editing_row = editing_row.next();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            }

        } else if (prev) {
            // selectedRowId = dyn_tbl_sel_row_id - 1;
            // if(selectedRowId >= 0) {
            //     loadOrderItemModal(selectedRowId);
            // }
            if ((editing_row.prev()).length) {
                editing_row = editing_row.prev();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            }

        } else {
            $('#orderItemModal').modal('toggle');
        }
    }

    $(document).on('click', "[class^=editrow]", function (event) {
        editing_row = $(this).closest('tr');
        selectedRowId = parseInt($(this).closest('tr').attr('data-row_index'));
        loadOrderItemModal(selectedRowId);
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
        closeAllSelect2OnModal();
        next = false;
        prev = true;

        action_button = 'prev';
        if(is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            // var ok = is_modal_valid();
            // if (!ok) {
            //     var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            //     $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
            // }
            editing_row = editing_row.prev();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal(selectedRowId);
        }
    });

    $(document).on('click', "[id^=btnOrderItemNext]", function (event) {
        closeAllSelect2OnModal();
        next = true;
        prev = false;

        action_button = 'next';
        if (is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            editing_row = editing_row.next();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal(selectedRowId);
        }
    });


    function save_order_item() {
        selectedRowId = dyn_tbl_sel_row_id;
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            // var row = $('#dynamic-table tr.gradeX')[selectedRowId + 1];
            // var valid = ($(row).length != 0);
            // if (!valid) {
            if (!editing_row.next().hasClass('gradeX')) {
                setTimeout(() => {
                    //  $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId+1) + ')').find('.appendrow').trigger('click');
                    editing_row.find('.appendrow').trigger('click');
                    setTimeout(() => {
                        editing_row = editing_row.next();
                        selectedRowId = parseInt(editing_row.attr('data-row_index'));
                        loadOrderItemModal(selectedRowId);
                        $('#loading').hide();
                    }, 100);
                    $('#loading').show();
                }, 1000);
            } else {
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal(selectedRowId);
                }, 1000);
            }
        } else {
             $('#invalidInputModal').modal('show');
        }
    }

    $(document).on('click', "[id^=btnOrderItemSave]", function (event) {
        closeAllSelect2OnModal();
        save_order_item()
    });

    // $('#btnOrderItemSave').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         save_order_item()
    //     }
    // });

    function removeLine() {
        var selectedRowId = parseInt(editing_row.find('label:first').text());
        editing_row.find('.removerow').trigger('click');
        setTimeout(() => {
            if (selectedRowId > 1) {
                editing_row = $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId-1) + ')');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            } else {
                editing_row = $('#dynamic-table tr.gradeX:nth-child(1)');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            }
        }, 800);
    }

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
                    loadOrderItemModal(selectedRowId);
                    $('#loading').hide();
                }, 100);
                $('#loading').show();
            }, 1000);
        } else {
           $('#invalidInputModal').modal('show');
        }
    });

    $('#save_new_line').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            $('#save_new_line').trigger('click');
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
                    loadOrderItemModal(selectedRowId);
                    $('#loading').hide();
                }, 100);
                $('#loading').show();
            }, 1000);
        } else {
            loadOrderItemModal(dyn_tbl_sel_row_id)
        }
    });

    $(document).on('click', "[id^=reset_line]", function (event) {
        resetLine();
    });

    function resetLine() {
        var selectedRowId = parseInt(editing_row.find('label:first').text()) - 1;
        // var is_database = $('#dynamic-table tr.gradeX:nth-child(' + (dyn_tbl_sel_row_id+1) + ')').attr('data-is_database');
        var is_database = editing_row.attr('data-is_database');
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
                        }, 600);
                    }
                }
                // process_button(selectedRowId);
            }
        } else {
            // rollBack_data();
            process_button(selectedRowId);
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
                loadOrderItemModal(selectedRowId);
            }
            break;
          case 'next':
            if (editing_row.next().hasClass('gradeX')) {
                editing_row = editing_row.next();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            }
            break;
          default:
            action_button = ''
        }
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
                loadOrderItemModal(selectedRowId);
            }, 500);
        }
        else {
            $('#comfirmSaveNewOrderModal').modal('show');
        }
    }

    function closeAllSelect2OnModal() {
        // try{
        //     $('#modal_part_item_code select').select2('close');
        // } catch (e){
        //     console.log(e.message);
        // }
        try{
            $('#modal_supplier select').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('#modal_location select').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    function orderItemNew() {
        if (is_change()) {
            $('#comfirmSaveNewOrderModal').modal('show');
        } else {
            itemNewRow();
        }
    }

    $(document).on('click', "[id^=btnOrderItemNew]", function (event) {
        closeAllSelect2OnModal();
        orderItemNew();
    });

    // $('#btnOrderItemNew').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         orderItemNew()
    //     }
    // });

    function orderItemCancel() {
        if (is_change()) {
            next = false;
            prev = false;
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            var selectedRowId = dyn_tbl_sel_row_id;
            var ok = is_modal_valid();
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
            setTimeout(() => {
                $('.select2-container').removeClass('select2-container--open');
            }, 500);
        }
    }

    $(document).on('click', "[id^=btnOrderItemCancel]", function (event) {
        closeAllSelect2OnModal();
        action_button = 'cancel';
        orderItemCancel();
    });

    $(document).on('click', "[id^=btnOrderItemDelete]", function (event) {
        closeAllSelect2OnModal();
        $('#comfirmSaveDeleteOrderModal').modal('show');
    });

    $('#modal_w_date').bind('keyup', function (event) {
        adjust_input_date(this);
    });

    $('#modal_s_date').bind('keyup', function (event) {
        adjust_input_date(this);
    });

    $('#modal_w_date').on('change', function (e) {
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
                    function () { $('#modal_w_date').val(date_from); $('#modal_quantity').select();},
                    function () {
                        // wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                        $('#modal_w_date').val('');
                        $('#modal_w_date').focus();
                    });
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
                            function () { $('#modal_w_date').val(date_from); $('#modal_quantity').select(); },
                            function () {
                                // wanted_date = $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val();
                                $('#modal_w_date').val('');
                                $('#modal_w_date').focus();
                            });
                    }
                }
            }

            if (resultOK) {
                $('#modal_w_date').val(date_from);
                // $('#id_formset_item-' + dyn_tbl_sel_row_id + '-wanted_fake_date').val($(this).val());
                $('#modal_quantity').select();
                $('#modal_w_date').removeClass('highlight-mandatory');
            } else {
                $('#modal_w_date').val('');
                $('#modal_w_date').focus();
                // $('#modal_quantity').select();
            }
        }
    });

    $('#modal_w_date').click(function () {
        $(this).select();
    });

    $('#modal_s_date').on('change', function (e) {
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
                                $('#modal_s_date').val('');
                                $('#modal_s_date').focus();
                            });
                    }
                }
            }

            if (resultOK) {
                $('#modal_s_date').val(date_from);
            } else {
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

    $('#btnOrderItemNext').bind('keydown', function (event) {
        if (event.which == 13) {
            $(this).click();
            return false;
        }
    });

    function is_change() {
        var flag_change = false;
        if (line_object['part_item'] != $('#modal_part_item_code').val()) {
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
        if (line_object['price'] != $('#modal_price').val()) {
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



    function loadOrderItemModal(selectedRowId, addNew=false) {
        var last_price = 0.00;
        // $('#loading').show();
        $('.highlight-mandatory').removeClass('highlight-mandatory');
        dyn_tbl_sel_row_id = selectedRowId;
        if (addNew === undefined) {
            addNew = !$.checkOrderRowValidity(selectedRowId);
        }

        if (!addNew) {
            // selectedRowId++; // nth-child start with 1 not 0

            var $current_row = editing_row.find('input');
            var $labels = editing_row.find('label');
            var $selects = editing_row.find('select');

            if ($current_row.length == 0) {
                editing_row = editing_row.prev();
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId, false);
                return;
            }

            $('#modal_line_number').val($labels[SO_LABEL_INDEX_LINE_NUMBER].textContent);
            if ($($labels[SO_LABEL_INDEX_LINE_NUMBER]).attr('data-original') != undefined) {
                $('#modal_line_number').attr('data-original', $($labels[SO_LABEL_INDEX_LINE_NUMBER]).attr('data-original'));
            } else {
                $('#modal_line_number').attr('data-original', '0');
            }

            $('#modal_part_name').val($current_row[SO_ROW_INDEX_ITEM_NAME].value);

            $('#modal_supplier').empty();
            $($selects[SO_SELECT_INDEX_SUPPLIER]).clone().appendTo('#modal_supplier');
            $('#modal_supplier select').removeAttr( 'style' );
            $('#modal_supplier select').val($selects[SO_SELECT_INDEX_SUPPLIER].value).trigger('change');
            // $('#modal_location select option[value="'+$selects[SO_SELECT_INDEX_LOCATION].value+'"]').attr('selected', 'selected');
            $('#modal_supplier select').select2({placeholder: 'Select Supplier'});
            // Part item location
            if ($('#company_is_inventory').val() == 'True') {
                $('#modal_location').empty();
                $($selects[SO_SELECT_INDEX_LOCATION]).clone().appendTo('#modal_location');
                $('#modal_location select').removeAttr( 'style' );
                $('#modal_location select').val($selects[SO_SELECT_INDEX_LOCATION].value).trigger('change');
                // $('#modal_location select option[value="'+$selects[SO_SELECT_INDEX_LOCATION].value+'"]').attr('selected', 'selected');
                $('#modal_location select').select2({placeholder: 'Select Location'});

                $('#modal_location select').on("select2:close", function (event) {
                    $('#modal_customer_po_no').focus();
                });

                $('#modal_location select').on("select2:open", function (event) {
                    prefill_select2(event);
                });
            }

            $('#modal_supplier select').on("select2:close", function (event) {
                if ($('#company_is_inventory').val() == 'True') {
                     $('#modal_location select').focus();
                    $('#modal_location select').select2('open');
                } else {
                    $('#modal_customer_po_no').focus();
                }
            });

            // $('#modal_supplier select').on("select2:open", function( event ){
            //     prefill_select2(event);
            // });

            // Destroy the Select2 element when is already generated
            // if ($('#modal_part_item_code select').data('select2')) {
            //     $('#modal_part_item_code select').select2('destroy');
            // }

            // Part item code
            // $($selects[SO_SELECT_INDEX_ITEM_CODE]).trigger('select2:open');

            // $('#modal_part_item_code').empty();
            // $($selects[SO_SELECT_INDEX_ITEM_CODE])
            //     .clone()
            //     .attr('id', 'modal_part_item_code_select')
            //     .attr('tabindex','0')
            //     .appendTo('#modal_part_item_code');

            current_code = $current_row[SO_ROW_INDEX_CODE].value;
            line_object['part_item'] = current_code;
            $('#modal_part_item_code').val(current_code).trigger('change');
            // $('#modal_part_item_code select').val($($selects[SO_SELECT_INDEX_ITEM_CODE]).val());

            // if ($($selects[SO_SELECT_INDEX_ITEM_CODE]).val() !== null) {
            //     setTimeout(function() {
            //         // Generate Select2 element
            //         $('#modal_part_item_code select').select2({
            //             // dropdownParent: $('#orderItemModal'),
            //             placeholder: 'Select Part Number'
            //         });

            //         // Fix Select2 Style
            //         $('#modal_part_item_code .select2-container span.select2-selection__rendered').css({
            //             // 'text-align': 'left',
            //             'font-size': '15px'
            //         });
            //         setTimeout(function() {
            //             if ($("#orderItemModal").is(':visible')) {
            //                 $('#modal_part_item_code select').select2('open');
            //             }
            //             $('#loading').hide();
            //         }, 300);
            //     }, 100);
            // }
            // else {
            //     // Generate Select2 element
            //     $('#modal_part_item_code select').select2({
            //         // dropdownParent: $('#orderItemModal'),
            //         placeholder: 'Select Part Number'
            //     });
            // }

            // // Fix Select2 Style
            // $('#modal_part_item_code .select2-container span.select2-selection__rendered').css({
            //     // 'text-align': 'left',
            //     'font-size': '15px'
            // });

            // $('#modal_part_item_code select').on("select2:open", function( event ){
            //     prefill_select2(event);
            //     $('.select2-container input.select2-search__field').css({
            //         'font-size': '12.5px',
            //         'padding-top': '3px',
            //         'padding-bottom': '3px',
            //     });
            // });

            // $('#modal_part_item_code select').on("select2:close", function (event) {
            //     $('#modal_supplier select').focus();
            //     $('#modal_supplier select').select2('open');
            // });

            $('#modal_quantity').off('keyup').on('keyup', function() {
                // is_change = true;
                if (float_format($('#modal_quantity').val()) < 0) {
                    pop_ok_dialog("Invalid Quantity",
                    "The quantity of product must be greater than 0",
                    function(){
                        $('#modal_quantity').select();
                    });
                } else {
                    var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true, decimal_place);
                    $('#modal_amount').val(comma_format(amount, decimal_place));
                    var qty = float_format($('#modal_quantity').val());
                    try{
                        var selected_item;
                        $.each(item_info, function(k, v){
                            if (v.code === $('#modal_part_item_code').val()) {
                                selected_item = v;
                            }
                        });
                        console.log('selected_item', selected_item);
                        if (selected_item === null && selected_item === undefined) return;
                        $.getJSON(url_get_item_backorder+'?item_id='+selected_item.id, function(data) {
                            var backorder_qty = 0;

                            if (data.length > 0) {
                                backorder_qty = data[0].rfs_qty;
                            }

                            var backorder = get_backorder_qty(selected_item.qty_rfs, qty, backorder_qty);

                            if (isNaN(backorder)) backorder = 0;
                            $('#modal_bkord_quantity').val(comma_format(backorder, 2));
                        });
                    }
                    catch(e){
                        console.log(e.message)
                    }
                }
            });

            $('#modal_quantity').off('change').on('change', function(e) {
                if (float_format($('#modal_quantity').val()) < 0) {
                    pop_ok_dialog("Invalid Quantity",
                    "The quantity of product must be greater than 0",
                    function(){
                        $('#modal_quantity').select();
                    });
                } else {
                    var quantity_original = float_format($(this).attr('data-original'));
                    var refer_line = $('#modal_line_number').attr('data-original');
                    check_quantity_reference(refer_line, order_id, 'SO', e.target.id, quantity_original);
                    $('#modal_quantity').val(comma_format(float_format($('#modal_quantity').val())));
                    if (float_format($(this).val()) > 0 ) {
                        $(this).removeClass('highlight-mandatory');
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
                            $('#modal_quantity').val(minoq).trigger('keyup');
                            $('#modal_quantity').trigger('change');
                            $('#modal_quantity').select();
                        }
                        function ok_function(){
                            $('#modal_price').focus();
                        }
                        var selected_item = $('#modal_part_item_code').val();
                        pop_ok_cancel_dialog("",
                                             "Order Quantity ("+quantity+") of part number "+selected_item+
                                             " is less than it Minimum order Quantity ("+minoq+
                                             "). Continue anyway ?",
                                             ok_function,
                                             cancel_function,
                                             'No, reset to Minimum Order Quantity !');
                    }
                }
            });
            
            $('#modal_price').on('focus', function() {
                last_price = float_format($(this).val());
            })
            $('#modal_price').off('change').on('change', function() {
                if (float_format($(this).val()) > 0) {
                    var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true, decimal_place);
                    if (isNaN(amount)) amount = 0;
                    $('#modal_amount').val(comma_format(amount, decimal_place));
                    $('#modal_price').val(
                        comma_format(float_format($(this).val()), 6)
                    );
                    $(this).removeClass('highlight-mandatory');
                } else {
                    $('#modal_price').val(last_price.toFixed(6));
                }
            });

            $('#modal_customer_po_no').off('change').on('change', function () {
                if ($(this).val() != '' ) {
                    $(this).removeClass('highlight-mandatory');
                }
                has_location = false;
                cur_loc= '';
                c_line = $('#modal_line_number').val();
                $cust_po_no = '#modal_customer_po_no';
                $target_id = '#modal_w_date';
                current_so_doc_no = $('#id_document_number').val();
                cuspo = $(this).val();
                try{
                    cusitem = $('#modal_item_code').val();
                } catch {
                    cusitem = '';
                }
                cur_sup = $('#modal_supplier select').select2('data')[0].text;
                if ($('#company_is_inventory').val() == 'True') {
                    has_location = true;
                    cur_loc = $('#modal_location select').select2('data')[0].text;
                }
                var is_local_check = false;
                // $('#dynamic-table tr.gradeX').each(function (i, v) {
                //     var cRow = $(this).closest('tr').find('input');
                //     var cLabel = $(this).closest('tr').find('label');
                //     var cSelect = $(this).closest('tr').find('select');
                //     var cpo = cRow[SO_ROW_INDEX_CUSTOMER_PO].value;
                //     var csup = $('#'+ cSelect[SO_SELECT_INDEX_SUPPLIER].id).select2('data')[0].text;
                //     var citem = $('#'+ cSelect[SO_SELECT_INDEX_ITEM_CODE].id).select2('data')[0].text;
                //     if ($('#company_is_inventory').val() == 'True') {
                //         try{
                //             cloc = $('#'+ cSelect[SO_SELECT_INDEX_LOCATION].id).select2('data')[0].text;
                //         } catch {
                //             cloc = '';
                //         }
                //     }
                //     if (cpo != '' && cusitem && cuspo == cpo && cusitem == citem && 
                //         cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent != c_line &&
                //         cur_sup == csup) {
                //         if (has_location) {
                //             if (cur_loc == cloc) {
                //                 var duplicate_data_list = [];
                //                 duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, cloc]);
                //                 duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, cur_loc]);
                //                 is_local_check = true;
                //                 show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location);
                //             }
                //         } else {
                //             var duplicate_data_list = [];
                //             duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, '']);
                //             duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, '']);
                //             is_local_check = true;
                //             show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location);
                //         }
                //     }
                // })

                if ($($cust_po_no).val() && !is_local_check) {
                    var item_id;
                    $.each(item_list, function(k, v){
                        if (v.code === $('#modal_part_item_code').val()) {
                            item_id = v.id;
                        }
                    });
                    var data = {
                        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                        'cust_po_no': cuspo,
                        'item_id': item_id,
                        'type': 'SO',
                        'ref_number': current_so_doc_no
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
                                if (cur_loc == data[0].loc_code) {
                                    var duplicate_data_list = [];
                                    duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, cuspo, cur_sup, data[0].loc_code]);
                                    duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, cur_loc]);
                                    show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
                                }
                            } else {
                                var duplicate_data_list = [];
                                duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, cuspo, cur_sup, '']);
                                duplicate_data_list.push([c_line, 'Current Doc', cusitem, cuspo, cur_sup, '']);
                                show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
                            }
                        }
                    })
                }
            });

            $('#modal_part_item_code').on("change", function() {
                var selected_item;
                var select_val = $('#modal_part_item_code').val();

                if (selected_item === undefined) {
                    $.each(item_list, function(k, v){
                        if (v.code === select_val) {
                            selected_item = v;
                            select_val = selected_item.id;
                        }
                    });
                }
                if (selected_item) {
                    has_location = false;
                    cur_loc= '';
                    cur_sup = '';
                    c_line = $('#modal_line_number').val();
                    $cust_po_no = $('#modal_customer_po_no').val();
                    cusitem = $('#modal_part_item_code').val();
                    try {
                        cur_sup = $('#modal_supplier select').select2('data')[0].text;
                        if ($('#company_is_inventory').val() == 'True') {
                            has_location = true;
                            cur_loc = $('#modal_location select').select2('data')[0].text;
                        }
                    } catch (e) {

                    }
                    $('#dynamic-table tr.gradeX').each(function (i, v) {
                        var cRow = $(this).closest('tr').find('input');
                        var cLabel = $(this).closest('tr').find('label');
                        var cSelect = $(this).closest('tr').find('select');
                        var cpo = cRow[SO_ROW_INDEX_CUSTOMER_PO].value;
                        // var citem = $('#'+ cSelect[SO_SELECT_INDEX_ITEM_CODE].id).select2('data')[0].text;
                        var citem = cRow[SO_ROW_INDEX_CODE].value;
                        var csup = $('#'+ cSelect[SO_SELECT_INDEX_SUPPLIER].id).select2('data')[0].text;
                        if ($('#company_is_inventory').val() == 'True') {
                            cloc = $('#'+ cSelect[SO_SELECT_INDEX_LOCATION].id).select2('data')[0].text;
                        } else {
                            cloc = '';
                        }
                        
                        if (cpo != '' && cusitem && cusitem == citem &&
                            cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent != c_line &&
                            cur_sup == csup) {
                            if (has_location) {
                                if (cur_loc == cloc) {
                                    var duplicate_data_list = [];
                                    duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, cloc]);
                                    duplicate_data_list.push([c_line, 'Current Doc', cusitem, $cust_po_no, cur_sup, cur_loc]);
                                    show_duplicate_part_modal(duplicate_data_list, '#modal_part_item_code', '#modal_supplier select', has_location);
                                }
                            } else {
                                var duplicate_data_list = [];
                                duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', citem, cpo, csup, '']);
                                duplicate_data_list.push([c_line, 'Current Doc', cusitem, $cust_po_no, cur_sup, '']);
                                show_duplicate_part_modal(duplicate_data_list, '#modal_part_item_code', '#modal_supplier select', has_location);
                            }
                        }
                    })
                    $('#modal_part_item_code').removeClass('highlight-mandatory');
                    load_part_infos(select_val);
                } else {
                    $('#modal_part_item_code').addClass('highlight-mandatory');
                    $('#modal_part_item_code').val('');
                    if (select_val != '') {
                        pop_focus_invalid_dialog('Invalid Part No.',
                            'This part number can not be found',
                            function(){
                                
                            }, '#modal_part_item_code');
                    }

                    $('#modal_uom').val("");
                    $('#modal_category').val("");
                    $('#modal_w_date').val("");
                    $('#modal_original_currency').val("");
                    $('#modal_bkord_quantity').val("");
                    $('#modal_quantity').val("");
                    $('#modal_price').val("");
                    $('#modal_amount').val("");
                    $('#modal_part_name').val("");
                    $('#modal_s_date').val("");
                    $('#modal_remarks').val("");
                    try {
                        $('#modal_supplier select').empty().trigger('change');
                        if ($('#company_is_inventory').val() == 'True') {
                            $('#modal_location select').empty().trigger('change');
                        }
                    } catch (e) {

                    }
                }
            });

            if ($current_row[SO_ROW_INDEX_CUSTOMER_PO].value) {
                $('#modal_customer_po_no').val($current_row[SO_ROW_INDEX_CUSTOMER_PO].value);
            }

            $('#modal_uom').val($current_row[SO_ROW_INDEX_UOM].value);
            $('#modal_category').val($current_row[SO_ROW_INDEX_CATEGORY].value);

            $('#modal_w_date').val($current_row[SO_ROW_INDEX_WANTED_FAKE_DATE].value);
            $('#modal_original_currency').val($current_row[SO_ROW_INDEX_CURRENCY_CODE].value);
            $('#modal_bkord_quantity').val($labels[SO_LABEL_INDEX_BACKORDER_QTY].textContent);
            $('#modal_quantity').val($current_row[SO_ROW_INDEX_ITEM_QTY].value);
            $('#modal_quantity').data('minoq', $current_row[SO_ROW_INDEX_MIN_ORDER_QTY].value)


            $('#modal_price').val($current_row[SO_ROW_INDEX_ITEM_PRICE].value);
            $('#modal_amount').val($labels[SO_LABEL_INDEX_AMOUNT].textContent);
            $('#modal_s_date').val($current_row[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value);
            $('#modal_remarks').val($current_row[SO_ROW_INDEX_DESCRIPTION].value);

            $('#modal_quantity').trigger('keyup');

            line_object['cust_po'] = $('#modal_customer_po_no').val();
            line_object['w_date'] = $current_row[SO_ROW_INDEX_WANTED_FAKE_DATE].value;
            line_object['s_date'] = $current_row[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value;
            line_object['qty'] = $current_row[SO_ROW_INDEX_ITEM_QTY].value;
            line_object['price'] = $current_row[SO_ROW_INDEX_ITEM_PRICE].value;
            line_object['remark'] = $current_row[SO_ROW_INDEX_DESCRIPTION].value;

            // store original Quantity
            var is_database = $('#dynamic-table tr.gradeX:nth-child(' + (selectedRowId+1) + ')').attr('data-is_database');
            if (is_database != '' && is_database != undefined) {
                $('#modal_quantity').attr('data-original', $($current_row[SO_ROW_INDEX_ITEM_QTY]).closest('td').attr('data-original'));
            }

        }
        controlPrevNextBtn();
    }

    function saveOrderItemModal(selectedRowId) {
        var wanted_date = $('#modal_w_date').val();
        var schedule_date = $('#modal_s_date').val();
        var modal_location = $('#modal_location select').val();
        var modal_supplier = $('#modal_supplier select').val();
        var modal_part_item_code = $('#modal_part_item_code').val();
        var modal_bkord_quantity = $('#modal_bkord_quantity').val();
        var modal_customer_po_no = $('#modal_customer_po_no').val();
        var modal_quantity = $('#modal_quantity').val();
        var modal_price = $('#modal_price').val();
        var modal_remarks = $('#modal_remarks').val();
        var modal_amount = $('#modal_amount').val();

        var date_wanted_valid = moment(wanted_date, "DD-MM-YYYY", true).isValid();
        var date_schedule_valid = moment(schedule_date, "DD-MM-YYYY", true).isValid();

        // sel_cust_po_id = '#id_formset_item-' + (selectedRowId) + '-customer_po_no';
        // sel_cust_po_no = modal_customer_po_no;
        // sel_part_code = modal_part_item_code;

        $('#id_formset_item-' + selectedRowId +'-code').val(modal_part_item_code).trigger('change')
        setTimeout(function() {
            // selectedRowId++; // nth-child start with 1 not 0
            var $current_row = editing_row.find('input');
            var $labels = editing_row.find('label');
            var $selects = editing_row.find('select');

            if (wanted_date) {
                if (!date_wanted_valid) {
                    $current_row[SO_ROW_INDEX_WANTED_FAKE_DATE].value = moment(wanted_date, "DD-MM-YYYY").format("DD-MM-YYYY");
                } else {
                    $current_row[SO_ROW_INDEX_WANTED_FAKE_DATE].value = wanted_date;
                }
                $current_row[SO_ROW_INDEX_WANTED_DATE].value = moment(wanted_date, "DD-MM-YYYY").format("YYYY-MM-DD");
            }

            if (schedule_date) {
                if (!date_schedule_valid) {
                    $current_row[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value = moment(schedule_date, "DD-MM-YYYY").format("DD-MM-YYYY");
                } else {
                    $current_row[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value = schedule_date;
                }
                $current_row[SO_ROW_INDEX_SCHEDULE_DATE].value = moment(schedule_date, "DD-MM-YYYY").format("YYYY-MM-DD");
            } else {
                $current_row[SO_ROW_INDEX_SCHEDULE_DATE].value = schedule_date;
            }

            setTimeout(() => {
                if ($('#company_is_inventory').val() == 'True'){
                    $($selects[SO_SELECT_INDEX_LOCATION]).val(modal_location).trigger('change');
                }
            }, 1000);
            setTimeout(() => {
                $($selects[SO_SELECT_INDEX_SUPPLIER]).val(modal_supplier).trigger('change');
            }, 500);

            // $current_row[SO_ROW_INDEX_WANTED_FAKE_DATE].value = wanted_date;
            $current_row[SO_ROW_INDEX_CUSTOMER_PO].value = modal_customer_po_no;
            // $current_row[SO_ROW_INDEX_BACKORDER_QTY].value = $('#modal_bkord_quantity').val();
            $current_row[SO_ROW_INDEX_ITEM_QTY].value = modal_quantity;
            $current_row[SO_ROW_INDEX_ITEM_PRICE].value = float_format(modal_price).toFixed(6);
            $current_row[SO_ROW_INDEX_AMOUNT].value = float_format(modal_amount);
            $current_row[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value = schedule_date;
            $current_row[SO_ROW_INDEX_DESCRIPTION].value = modal_remarks;

            // $labels[SO_LABEL_INDEX_LINE_NUMBER].textContent = $current_row[SO_ROW_INDEX_LINE_NUMBER].value;
            $labels[SO_LABEL_INDEX_ITEM_NAME].textContent = $current_row[SO_ROW_INDEX_ITEM_NAME].value;
            $labels[SO_LABEL_INDEX_BACKORDER_QTY].textContent = modal_bkord_quantity;
            $labels[SO_LABEL_INDEX_CURRENCY_CODE].textContent = $current_row[SO_ROW_INDEX_CURRENCY_CODE].value;
            $labels[SO_LABEL_INDEX_AMOUNT].textContent = modal_amount;

            $('#modal_customer_po_no').val(modal_customer_po_no);
        }, 600);
    }

});

//Company Information
$(document).ready(function () {

    //toggle `popup` / `inline` mode
    $.fn.editable.defaults.mode = 'inline';
    //Get company id
    var company_id = $('#company_id').val();
    //make status editable
    $('#companyname').editable({
        type: 'text',
        pk: company_id,
        url: '/orders/change_company/' + company_id + '/',
        title: 'Enter company name',
        success: function (response, newValue) {

            if (!response) {
                return "Unknown error!"
            }
            if (response.success === false) {
                return respond.msg;
            }
        }
    });

    $('#address').editable({
        type: 'text',
        pk: company_id,
        url: '/orders/change_company/' + company_id + '/',
        title: 'Enter company address',
        success: function (response, newValue) {

            if (!response) {
                return "Unknown error!"
            }
            if (response.success === false) {
                return respond.msg;
            }
        }
    });

    $('#email').editable({
        type: 'text',
        pk: company_id,
        url: '/orders/change_company/' + company_id + '/',
        title: 'Enter company email',
        validate: function (value) {
            var valid = valib.String.isEmailLike(value)
            if (valid == false) return 'Please insert valid email'
        },
        success: function (response, newValue) {

            if (!response) {
                return "Unknown error!"
            }
            if (response.success === false) {
                return respond.msg;
            }
        }
    });

});
//Supplier Information
$(document).ready(function (hdSupplierId) {
    var hdSupplierId = $('#hdSupplierId').val();
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


    $('#id_supplier').change(function (e) {
        var supplier_id = parseInt($(this).val());
        $.ajax({
            method: "POST",
            url: '/orders/supplier/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'supplier_id': supplier_id,
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
                $('#hdSupplierId').val(json['id']);

                $('#supplier_name').editable('destroy');
                $('#supplier_address').editable('destroy');
                $('#supplier_email').editable('destroy');

                $('#supplier_name').attr('data-pk', json['id']);
                $('#supplier_name').text(json['name']);
                $('#supplier_address').attr('data-pk', json['id']);
                $('#supplier_address').text(json['address']);
                $('#supplier_email').attr('data-pk', json['id']);
                $('#supplier_email').text(json['email']);

                loadSupplierInfo(json['id']);

                //filter product by supplier
                var $tableSel = $('#tblData').dataTable();
                $tableSel.fnFilter(json['name']);
            }
        });
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
            amount = currentRow[SO_ROW_INDEX_AMOUNT].value;
            sum += parseInt(amount);
            $('#id_subtotal').val(comma_format(float_format(sum).toFixed(decimal_place), decimal_place));
            var total = sum + float_format($('#id_tax_amount').val())
            $('#id_total').val(comma_format(total), decimal_place);
        })
    }
});

function checkLesserQuantity(is_so_po_reference, quantity, original, target_id) {
    if(is_so_po_reference) {
        if (original > quantity) {
            pop_ok_dialog("Warning Quantity",
            "The quantity Less than original ("+ original + ")!",
            function(){
                    $ItemQty = '#' + target_id;
                    $($ItemQty).select();
            });
            original = comma_format(original, 2)
            $('#'+target_id).val(original).trigger('change');
        }
    }
}

function quantityEvent($ItemQty) {
    let last_qty = 0.00;
    $($ItemQty).on('focus', function (e) {
        last_qty = float_format($(this).val());
    })
    $($ItemQty).off('change').on('change', function (e) {
        if (float_format($(this).val()) <= 0) {
            pop_ok_dialog("Invalid Quantity",
            "The quantity of product must be greater than 0",
            function(){
                $($ItemQty).val(comma_format(last_qty));
                $($ItemQty).select();
            });
        } else {
            var currentRow = $(this).closest('tr').find('input');
            var selects = $(this).closest('tr').find('select');
            var currentLabel = $(this).closest('tr').find('label');

            var quantity_original = float_format($(this).closest('td').attr('data-original'));
            var refer_line = $(currentLabel[SO_ROW_INDEX_LINE_NUMBER]).attr('data-original');
            check_quantity_reference(refer_line, order_id, 'SO', e.target.id, quantity_original);

            // var code = $('#'+selects[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').text();
            var code = currentRow[SO_ROW_INDEX_CODE].value;
            var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
            var backorder_qty = float_format(currentRow[SO_ROW_INDEX_BACKORDER_QTY].value);
            var onhand_qty = float_format(currentRow[SO_ROW_INDEX_QTY_RFS].value);
            var minoq = float_format(currentRow[SO_ROW_INDEX_MIN_ORDER_QTY].value);

            if (isNaN(backorder_qty)) {
                backorder_qty = 0;
            }
            try {
                if (isNaN(minoq)) {
                    // minoq = item_info[$('#'+selects[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').index()-1].minoq;
                    // currentRow[SO_ROW_INDEX_MIN_ORDER_QTY].value = item_info[$('#'+selects[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').index()-1].minoq;
                    $.each(item_info, function(k, v){
                        if (v.code === code) {
                            minoq = v.minoq;
                            currentRow[SO_ROW_INDEX_MIN_ORDER_QTY].value = v.minoq;
                        }
                    });
                }
            } catch {
                minoq = 0;
            }

            quantity = (isNaN(quantity)) ? 0.00 : quantity;

            var backorder = get_backorder_qty(onhand_qty, quantity, backorder_qty);

            currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(backorder);
            currentRow[SO_ROW_INDEX_ITEM_QTY].value = comma_format(quantity);

            var price = currentRow[SO_ROW_INDEX_ITEM_PRICE].value;
            if (quantity > 0 && float_format(quantity) < float_format(minoq)) {
                $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place)).trigger('change');
                WarnLessThanMinOrder(code, quantity, minoq, onhand_qty, this, currentRow[SO_ROW_INDEX_BACKORDER_QTY].value);
            }else if (float_format(quantity) >= 0) {
                var price = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);
                $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place).toFixed(decimal_place)).trigger("change");
                currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(price * quantity, decimal_place), decimal_place);

                $(this).closest('tr').removeAttr('style');
                $('#items_error').css('display', 'none');
                $('#minimum_order_error').css('display', 'none');
                $('#btnPrint').removeAttr('disabled');
                $('#btnSave').removeAttr('disabled');
            }

            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            var idFirstInvalid = getFirstFieldInvalid(rowCheck);
            if (idFirstInvalid != '') {
                pop_focus_invalid_dialog('Warning!',
                'Please fill up the required fields.',
                function(){
                    $(idFirstInvalid).focus();
                    if ($(idFirstInvalid).is('select')) {
                        $(idFirstInvalid).select2('open');
                    }
                }, idFirstInvalid);
            }
        }
        let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
        highLightMandatory(rowCheck);
    });
    $($ItemQty).click(function () {
        $(this).select();
    });
}


//event handle calculate subtotal and total base on quantity
function handleQuantity() {
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var $ItemQty = '#' + currentRow[SO_ROW_INDEX_ITEM_QTY].id;
        // var selects = $(this).closest('tr').find('select');
        // var order_type = $('#order_type').text();
        // var order_id = $('#order_id').text();

        quantityEvent($ItemQty);
        // $($ItemQty).bind('keydown', function(e) {
        //     if (e.which == 13){
        //
        //         var currentRow = $(this).closest('tr').find('input');
        //         var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
        //         if (quantity == 'NaN'){
        //             quantity = 0;
        //         }
        //         if (float_format(quantity) <= 0) {
        //             var code = $('#'+selects[SO_SELECT_INDEX_ITEM_CODE].id+' option:selected').text();
        //             pop_ok_dialog("Invalid Quantity",
        //                 "The quantity of product "+ code +" must be greater than 0",
        //                 function(){
        //                         $ItemQty = '#' + e.target.id;
        //                         $($ItemQty).select();
        //             });
        //             $(this).closest('tr').attr('style', 'background-color: yellow !important');
        //             $('#'+e.target.id).val("0.00");
        //             $('#btnPrint').attr('disabled', true);
        //             $('#btnSave').attr('disabled', true);
        //             $('#dynamic-table tr.gradeX').each(function () {
        //                 recalculateAmount(this, SO_ROW_INDEX_ITEM_QTY, SO_ROW_INDEX_ITEM_PRICE, SO_ROW_INDEX_AMOUNT, SO_LABEL_INDEX_AMOUNT, undefined, decimal_place);
        //             });
        //         }
        //     }
        // });


    });
}

function handleEventTable() {
    // event change price
    var last_price = 0.00;
    $('#dynamic-table tr.gradeX').find('input').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        // currentItem = $(this).closest('tr').find('option:selected');
        var $priceElement = '#' + currentRow[SO_ROW_INDEX_ITEM_PRICE].id;
        $($priceElement).on('focus', function (e) {
            last_price = float_format($(this).val());
        })
        $($priceElement).off('change').on('change', function (e) {
            var currentRow = $(this).closest('tr').find('input');
            var currentLabel = $(this).closest('tr').find('label');
            $('#'+ currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value) *
                                                        float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value) *
                                                        float_format(currentRow[SO_ROW_INDEX_EXCHANGE_RATE].value), decimal_place)).trigger("change");
            if (currentRow[SO_ROW_INDEX_ITEM_PRICE].value > 0) {
                $('#validate_error').css('display', 'none');
                currentRow.parents('tr').removeAttr('style');

                var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
                var price = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);
                $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place).toFixed(decimal_place)).trigger("change");
                currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(price * quantity, decimal_place), decimal_place);
                $('#validate_error').css('display', 'none');
                $('#btnPrint').removeAttr('disabled');
                $('#btnSave').removeAttr('disabled');
                $(this).val(float_format($(this).val()).toFixed(6));
            } else {
                pop_ok_dialog('Invalid Price',
                'Price of product must be greater than 0',
                function(){
                    setTimeout(function() {
                        $($priceElement).val(last_price.toFixed(6));
                        $($priceElement).select();
        
                        var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
                        var price = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);
                        $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place).toFixed(decimal_place)).trigger("change");
                        currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(price * quantity, decimal_place), decimal_place);
                    }, 300);
                });
            }
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });
        $($priceElement).click(function () {
            $(this).select();
        });

        var $lastElement = '#' + currentRow[SO_ROW_INDEX_DESCRIPTION].id;
        $($lastElement).off('keydown').on("keydown", function (e) {
            if (e.which == 9) {
                let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                var idFirstInvalid = getFirstFieldInvalid(rowCheck);
                if (idFirstInvalid != '') {
                    highLightMandatory(rowCheck);
                    pop_focus_invalid_dialog('Warning!',
                    'Please fill up the required fields.',
                    function(){
                        $(idFirstInvalid).focus();
                        if ($(idFirstInvalid).is('select')) {
                            $(idFirstInvalid).select2('open');
                        }
                    }, idFirstInvalid);
                } else {
                    // just tab key
                    let code_pressed = e.which;
                    let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
                    tabAddRow(rowIndex, code_pressed)
                }
            }
        });
    });

    //change amount event
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var $amountElement = '#' + currentRow[SO_ROW_INDEX_AMOUNT].id;

        $($amountElement).on('change', function (e) {

            var currentRow = $(this).closest('tr').find('input');
            var currentLabel = $(this).closest('tr').find('label');
            var amount = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value) * float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value) ;
            var subtotal = 0;
            if (float_format($(this)[0].value) < 0) {
                // $(this).closest('tr').attr('style', 'background-color: red !important');
                $('#items_error').text('The product ' + currentRow[SO_ROW_INDEX_CODE].value + ' must have amount greater than 0');
                $('#items_error').removeAttr('style');
                $('#btnPrint').attr('disabled', true);
                $('#btnSave').attr('disabled', true);
                // $('#dynamic-table tr.gradeX').each(function () {
                //     $(this).closest('tr').find('input').not(currentRow[SO_ROW_INDEX_AMOUNT]).attr('disabled', true);
                // });
                // $('#id_subtotal').val(0);
                // $('#id_total').val(0);
            } else {
                $('#items_error').css('display', 'none');
                $(this).closest('tr').removeAttr('style');
                $('#btnPrint').removeAttr('disabled');
                $('#btnSave').removeAttr('disabled');
                currentRow[SO_ROW_INDEX_AMOUNT].value = roundDecimal(amount, decimal_place);
                currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(amount, decimal_place));
                calculateTotal('#dynamic-table tr.gradeX', SO_ROW_INDEX_ITEM_QTY, SO_ROW_INDEX_ITEM_PRICE,
                    SO_ROW_INDEX_AMOUNT, SO_LABEL_INDEX_AMOUNT, decimal_place);
            }
        });
        $($amountElement).click(function () {
            $(this).select();
        });
    });

    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var $wanted_fake_date = '#' + currentRow[SO_ROW_INDEX_WANTED_FAKE_DATE].id;
        var $wanted_date = '#' + currentRow[SO_ROW_INDEX_WANTED_DATE].id;
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

        $($wanted_fake_date).on('change', function (e) {
            var date_from = get_date_from('#'+e.target.id);
            date_from = date_from.split('/').join('-');
            var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();
            var currentRow = $(this).closest('tr').find('input');

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
                if (input_date.getTime() < current_date.getTime()){
                    resultOK = false;
                    pop_ok_cancel_dialog("Invalid Wanted Date",
                                         "Wanted Date ("+$('#' + e.target.id).val() +
                                         ") is back dated !<br/> Do you want to proceed?",
                                         function(){change_wanted_date(date_from, e.target.id)},
                                         function(){revert_wanted_date(e.target.id)});
                } else {
                    $('#dynamic-table tr.gradeX').each(function () {
                        $('#'+e.target.id).closest('tr').find('input').removeAttr('disabled');
                    });
                    $('#'+e.target.id).closest('tr').removeAttr('style');
                    fnEnableButton();


                    var sched_date = new Date(moment(currentRow[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].value, "DD-MM-YYYY").format("YYYY-MM-DD"));
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

                if (resultOK){
                    change_wanted_date(date_from, e.target.id);
                    // move_next_elem($("#" + e.target.id), 1);
                }

                let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                highLightMandatory(rowCheck);
            }
        });

        $($wanted_fake_date).click(function () {
            $(this).select();
        });
    });


    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).closest('tr').find('input');
        var $schedule_fake_date = '#' + currentRow[SO_ROW_INDEX_SCHEDULE_FAKE_DATE].id;
        var $schedule_date = '#' + currentRow[SO_ROW_INDEX_SCHEDULE_DATE].id;
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

            $('#load_code_by_cust').focus();
            $('#load_code_by_cust').select2('open');
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

                    var wanted_date = new Date(moment(currentRow[SO_ROW_INDEX_WANTED_FAKE_DATE].value, "DD-MM-YYYY").format("YYYY-MM-DD"));
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
    });

    $('#dynamic-table tr.gradeX').each(function (index, value) {
        var currentRow = $(this).closest('tr').find('input');
        var $cuspoElement = '#' + currentRow[SO_ROW_INDEX_CUSTOMER_PO].id;

        $($cuspoElement).on('change', function (e) {
            has_location = false;
            cur_loc= '';
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            // $item_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_ITEM_CODE].id;
            $item_select = currentRow[SO_ROW_INDEX_CODE].value;
            $cust_po_no = '#' + e.target.id;
            var rowNo = parseInt(currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent) - 1;
            $target_id = '#id_formset_item-' + rowNo+ '-wanted_fake_date';
            current_so_doc_no = $('#id_document_number').val();
            cuspo = currentRow[SO_ROW_INDEX_CUSTOMER_PO].value;
            cusitem = currentRow[SO_ROW_INDEX_CODE].value;
            sup_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_SUPPLIER].id;
            cur_sup = $(sup_select).select2('data')[0].text;
            if ($('#company_is_inventory').val() == 'True' && $($cust_po_no).val()) {
                has_location = true;
                $loc_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_LOCATION].id;
                cur_loc = $($loc_select).select2('data')[0].text;
            }
            // $('#dynamic-table tr.gradeX').each(function (i, v) {
            //     var cRow = $(this).closest('tr').find('input');
            //     var cLabel = $(this).closest('tr').find('label');
            //     var cpo = cRow[SO_ROW_INDEX_CUSTOMER_PO].value;
            //     var citem = cRow[SO_ROW_INDEX_CODE].value;
            //     var s_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_SUPPLIER].id;
            //     var csup = $(s_select).select2('data')[0].text;
            //     if ($('#company_is_inventory').val() == 'True') {
            //         $l_select = '#' + $(this).closest('tr').find('select')[SO_SELECT_INDEX_LOCATION].id;
            //         loc = $($l_select).select2('data')[0].text;
            //     }
            //     if (cpo != '' && cusitem && cuspo == cpo && cusitem == citem && 
            //         cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent != currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent &&
            //         cur_sup == csup) {
            //         if (has_location) {
            //             if (cur_loc == loc) {
            //                 var duplicate_data_list = [];
            //                 duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cRow[SO_ROW_INDEX_CODE].value, cRow[SO_ROW_INDEX_CUSTOMER_PO].value, csup, loc]);
            //                 duplicate_data_list.push([currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, cur_loc]);
            //                 if (!$("#orderItemModal").is(':visible')) {
            //                     show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location);
            //                 }
            //             }
            //         } else {
            //             var duplicate_data_list = [];
            //             duplicate_data_list.push([cLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cRow[SO_ROW_INDEX_CODE].value, cRow[SO_ROW_INDEX_CUSTOMER_PO].value, csup, '']);
            //             duplicate_data_list.push([currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, '']);
            //             if (!$("#orderItemModal").is(':visible')) {
            //                 show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location);
            //             }
            //         }
            //     }
            // })

            if ($($cust_po_no).val()) {
                var data = {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'cust_po_no': currentRow[SO_ROW_INDEX_CUSTOMER_PO].value,
                    'item_id': currentRow[SO_ROW_INDEX_ITEM_ID].value,
                    'type': 'SO',
                    'ref_number': current_so_doc_no,
                };
                $.ajax({
                        url: '/orders/get_orderitems_by_cust_po_no/',
                        type: 'POST',
                        data: data,
                        cache: false,
                    })
                    .done(function (data) {
                        if (data.length != 0 && current_so_doc_no != data[0].doc_no) {
                            if (has_location) {
                                if (cur_loc == data[0].loc_code) {
                                    var duplicate_data_list = [];
                                    duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, data[0].loc_code]);
                                    duplicate_data_list.push([currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, cur_loc]);
                                    if (!$("#orderItemModal").is(':visible')) {
                                        show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
                                    }
                                }
                            } else {
                                var duplicate_data_list = [];
                                duplicate_data_list.push([data[0].ln_no, data[0].doc_no, cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, '']);
                                duplicate_data_list.push([currentLabel[SO_LABEL_INDEX_LINE_NUMBER].textContent, 'Current Doc', cusitem, currentRow[SO_ROW_INDEX_CUSTOMER_PO].value, cur_sup, '']);
                                if (!$("#orderItemModal").is(':visible')) {
                                    show_duplicate_cuspo_modal(duplicate_data_list, $cust_po_no, has_location, true);
                                }
                            }
                            // var title = "Duplicate Entry Error";
                            // var text = "Customer PO No " + currentRow[SO_ROW_INDEX_CUSTOMER_PO].value +
                            //     " is already in use for S/O " + data[0].doc_no + " !<br/> Do you want to proceed?"

                            // function ok_function() {$('#' + currentRow[SO_ROW_INDEX_WANTED_FAKE_DATE].id).focus();}
                            // function cancel_function() {
                            //     setTimeout(function() {
                            //         $($cust_po_no).focus();
                            //         $($cust_po_no).select();
                            //     }, 300);
                            // }
                            // pop_ok_cancel_dialog(title, text, ok_function, cancel_function);

                        } else {
                            // $('#dynamic-table tr.gradeX').each(function () {
                            //     $($cust_po_no).closest('tr').find('input').removeAttr('disabled');
                            // });
                            $($cust_po_no).closest('tr').find('input').removeAttr('disabled');
                            $($cust_po_no).closest('tr').removeAttr('style');
                            fnEnableButton();
                        }
                    })
                    .fail(function (e) {
                        pop_info_dialog("Error", "Some errors happended. Please refresh and try again or contact administrator for support.", "error");
                        $($cust_po_no).closest('tr').attr('style', 'background-color: yellow !important');
                        $('#dynamic-table tr.gradeX').each(function () {
                            $($cust_po_no).closest('tr').find('input').not(currentRow[SO_ROW_INDEX_CUSTOMER_PO]).attr('disabled', true);
                        });
                        fnDisableButton();
                    })
            } else {
                // $('#dynamic-table tr.gradeX').each(function () {
                //     $($cust_po_no).closest('tr').find('input').removeAttr('disabled');
                // });
                $($cust_po_no).closest('tr').find('input').removeAttr('disabled');
                $($cust_po_no).closest('tr').removeAttr('style');
                fnEnableButton();
            }

            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });
        $($cuspoElement).click(function () {
            $(this).select();
        });
    });
}

function get_backorder_qty(onhand_qty, quantity, backorder_qty){
    onhand_qty =  parseInt(onhand_qty);
    quantity =  parseInt(quantity);
    backorder_qty =  parseInt(backorder_qty);

    if (backorder_qty === undefined) backorder_qty = 0;

    if (onhand_qty<=0) {
        backorder_qty = backorder_qty + quantity;
    } else if ((onhand_qty>0) && (onhand_qty<quantity)) {
        backorder_qty = backorder_qty + (quantity-onhand_qty);
    }

    return float_format(backorder_qty);
}


$('#id_exchange_rate').on('change', function () {
    $('#id_exchange_rate_value').val($(this).val());
});


$('#id_document_date_fake').click(function () {
    $(this).select();
});

// event copy customer address
$('#btnCopyCustomer').click(function () {
    var hdCustomerId = $('#id_customer').val();
    $.ajax({
        method: "POST",
        url: '/orders/customer/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'customer_id': hdCustomerId,
        },
        success: function (json) {
            $('#id_name').val($('#customer_name').text());
            $('#id_address').val($('#customer_address').text());
            $('#id_email').val($('#customer_email').text());
            $('#id_code').val(json['code']);
            $('#id_phone').val(json['phone']);
            $('#id_fax').val(json['fax']);
        }
    });
});

// event change address
$('#id_customer_address').change(function (e) {
    var address_id = $(this).val();
    $.ajax({
        method: "POST",
        url: '/orders/change_address/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'address_id': address_id,
        },
        success: function (json) {
            if ($('#id_customer_address option:selected').text() == "") {
                $('#id_name').val("");
                $('#id_address').val("");
                $('#id_email').val("");
                $('#id_code').val("");
                $('#id_phone').val("");
                $('#id_fax').val("");
                $('#id_attention').val("");
                $('#id_note_1').val("");
                $('#id_note_2').val("");
            } else {
                $('#id_name').val($('#id_customer_address option:selected').text());
                $('#id_address').val(json['address']);
                $('#id_email').val(json['email']);
                $('#id_code').val(json['code']);
                $('#id_phone').val(json['phone']);
                $('#id_fax').val(json['fax']);
                $('#id_attention').val(json['attention']);
                $('#id_note_1').val(json['note_1']);
                $('#id_note_2').val(json['note_2']);
            }
        }
    });
});

// event change exchange rate //no longer use because exchange rate now set in order header, so we need to move this logic to header 'exchangerate' column
$('#dynamic-table tr.gradeX').find('input').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $exchangeRate = '#' + currentRow[SO_ROW_INDEX_EXCHANGE_RATE].id;
    $($exchangeRate).change(function (e) {
        currentRow = $(this).closest('tr').find('input');
        var exchange_rate = currentRow[SO_ROW_INDEX_EXCHANGE_RATE].value;
        var price = currentRow[SO_ROW_INDEX_ITEM_PRICE].value;
        var quantity = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value);
        if (exchange_rate <= 0) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The exchange rate of product ' + currentRow[SO_ROW_INDEX_CODE].value + ' must be greater than 0');
            $(this).closest('tr').attr('style', 'background-color: red !important');
            $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(0.00).trigger('change');
            $('#btnPrint').attr('disabled', true);
            $('#btnSave').attr('disabled', true);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[SO_ROW_INDEX_EXCHANGE_RATE]).attr('disabled', true);
            });
        } else {
            $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity * exchange_rate, decimal_place)).trigger('change');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $('#minimum_order_error').css('display', 'none');
            $(this).closest('tr').removeAttr('style');
            $('#btnPrint').removeAttr('disabled');
            $('#btnSave').removeAttr('disabled');
        }
    });
    $($exchangeRate).click(function () {
        $(this).select();
    });
});

// function random Colors
var safeColors = ['00', '33', '66', '99', 'cc', 'ff'];
var rand = function () {
    return Math.floor(Math.random() * 6);
};
var randomColor = function () {

    var r = safeColors[rand()];
    var g = safeColors[rand()];
    var b = safeColors[rand()];
    return "#" + r + g + b;
};

function changeCurrency(arrItems, currency_id, currency_name, doc_date='') {
    if (doc_date == '') {
        doc_date = $('#id_document_date').val();
    }
    $.ajax({
        method: "POST",
        url: '/orders/load_currency/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'arrItems': JSON.stringify(arrItems),
            'currency_id': currency_id,
            'doc_date':doc_date
        },
        success: function (json) {

            var item_currency_not_match = [];
            var sale_price = 0;
            var amount = 0;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    $('#dynamic-table tr.gradeX').each(function () {
                        currentRow = $(this).closest('tr').find('input');
                        currentLabel = $(this).closest('tr').find('label');

                        if (currentRow[SO_ROW_INDEX_ITEM_ID].value == json[i].id) {
                            if (json[i].rate == 0 || json[i].sale_price == "") {
                                item_currency_not_match.push('Can not get Exchange Rate from ' + json[i].currency + ' to ' + currency_name);
                                currentRow[SO_ROW_INDEX_EXCHANGE_RATE].value = 0;
                                currentRow[SO_ROW_INDEX_AMOUNT].value = 0.00;
                                $('.lblCurrency').text(json['code']);
                            } else {
                                sale_price = float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);
                                currentRow[SO_ROW_INDEX_EXCHANGE_RATE].value = float_format(json[i].rate).toFixed(8);
                                currentRow[SO_ROW_INDEX_AMOUNT].value = roundDecimal(sale_price, decimal_place);
                                $('.lblCurrency').text(json['code']);
                            }
                            currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[SO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
                        }
                    });
                }
            }
            ;
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
                $('#btnPrint').attr('disabled', true);
                $('#btnSave').attr('disabled', true);
                $('#dynamic-table tr.gradeX').each(function () {
                   //  $(this).closest('tr').find('input').attr('disabled', true);
                });
            } else {
                $('#currency_error').css('display', 'none');
                $('#btnPrint').removeAttr('disabled');
                $('#btnSave').removeAttr('disabled');
                $('#dynamic-table tr.gradeX').each(function () {
                    $(this).closest('tr').find('input').removeAttr('disabled');
                });
            }
        }
    });
}

// event change currency
$('#id_currency').change(function (e) {
    var currency_id = parseInt($(this).val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];
    var doc_date = $('#id_document_date').val();
    $('#dynamic-table tr.gradeX').each(function () {
        currentRow = $(this).closest('tr').find('input');
        arrItems.push({
            item_id: currentRow[SO_ROW_INDEX_ITEM_ID].value,
            currency_id: $('#id_currency').val()
        });
    });
    changeCurrency(arrItems, currency_id,currency_name , doc_date);
});


//event generate document number by order date
$('#id_order_date').change(function (e) {
    var order_date = $('#id_order_date').val();
    var order_type = $('#order_type').text();
    var document_number = $('#id_document_number').val()
    $.ajax({
        method: "POST",
        url: '/orders/generate_document_number/',
        dataType: 'text',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'order_date': order_date,
            'order_type': order_type,
            'document_number': document_number
        },
        success: function (data) {
            $('#id_document_number').val(data);
        }
    });
});

function customer_items() {
    // var data = $('#search_input').val();
    var customerID = $('#id_customer').val();
    var exclude_item_array = [];
    var exclude_item_list = {};

    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            if (currentRow[SO_ROW_INDEX_ITEM_ID].value){
                exclude_item_array.push(currentRow[SO_ROW_INDEX_ITEM_ID].value);
            }
        }
    });

    var datatbl = $('#tblData').DataTable();
    datatbl.destroy();
    var list_url = $('#list_url').text();
    $('#tblData').DataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[4, "asc"]],
        "serverSide": true,
        "ajax": {
            "url": list_url,
            "data": {
                "csrfmiddlewaretoken": $('input[name="csrfmiddlewaretoken"]').val(),
                "customer_id": customerID,
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
            {"data": "location_code", "sClass": "text-left"},
            {"data": "code", "sClass": "text-left"},
            {"data": "category", "sClass": "text-left"},
            {"data": "new_price", "sClass": "text-right"},
            {"data": "currency_code", "sClass": "text-left"},
            {
                "data": "location_id",
                "className": "hide_column"
            },
            {
                "data": "currency_id",
                "className": "hide_column"
            },
            {
                "data": "line_id",
                "className": "hide_column"
            },
            {
                "data": "unit",
                "className": "hide_column"
            },
            {
                "data": "supplier_id",
                "className": "hide_column"
            },
            {
                "data": "sales_price",
                "className": "hide_column"
            },
            {
                "data": "rfs_qty",
                "className": "hide_column"
            },
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, row, meta) {
                    return '<input type="checkbox" name="choices" id="' + row.line_id + '"'
                        + 'class="call-checkbox" value="' + row.sales_price + '"></td>';
                }
            }
        ]
    });
}

$(document).ready(function () {
    var order_id = $('#order_id').text();
    if (order_id != "") {
        var currency_id = $('#id_currency').val();
        var currency_name = $('#id_currency option:selected').text();
        var arrItems = [];
        $('#dynamic-table tr.gradeX').each(function () {
            currentRow = $(this).closest('tr').find('input');
            arrItems.push({
                item_id: currentRow[SO_ROW_INDEX_ITEM_ID].value,
                currency_id: currentRow[SO_ROW_INDEX_CURRENCY_ID].value
            });
            initial_item_qty.push({
                item_id: currentRow[SO_ROW_INDEX_ITEM_ID].value,
                qty: float_format(currentRow[SO_ROW_INDEX_ITEM_QTY].value)
            });
            set_order_item_dates();
        });
        $('#initial_item_qty_data').val(JSON.stringify(initial_item_qty));
    }
    $('#btnSearchItem').on('click', function () {
        customer_items();
    });
    $('#btnOpenItemDialog').on('click', function () {
        var dataTable = $('#tblData').dataTable();
        dataTable.fnClearTable(this);
        customer_items();
    });
});


function WarnLessThanMinOrder(prtno, ord_qty, min_qty, onhand_qty, elm, backorder_qty) {
    function cancel_function(){
        currentLabel = $(elm).closest('tr').find('label');
        currentRow = $(elm).closest('tr').find('input');
        $(elm).val(comma_format(min_qty));
        $(elm).select();
        currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(min_qty);
        currentRow = $(elm).closest('tr').find('input');
        
        var quantity = min_qty;
        var price = float_format(currentRow[SO_ROW_INDEX_ITEM_PRICE].value);
        $('#'+currentRow[SO_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity, decimal_place).toFixed(decimal_place)).trigger("change");
        currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(price * quantity, decimal_place), decimal_place);
    }

    function ok_function(){
        currentLabel = $(elm).closest('tr').find('label');
        currentRow = $(elm).closest('tr').find('input');
        $('#'+currentRow[SO_ROW_INDEX_ITEM_PRICE].id).focus();
        // $(elm).val(ord_qty);
        var backorder = get_backorder_qty(onhand_qty, ord_qty, backorder_qty);
        currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = backorder;
        $('#dynamic-table tr.gradeX').each(function () {
            $(elm).closest('tr').find('input').removeAttr('disabled');
        });
        $(elm).closest('tr').removeAttr('style');
        $('#btnPrint').removeAttr('disabled');
        $('#btnSave').removeAttr('disabled');
    }

    pop_ok_cancel_dialog("",
        "Order Quantity ("+ord_qty+") of part number "+prtno+
        " is less than it Minimum order Quantity ("+min_qty+
        "). Continue anyway ?",
        ok_function,
        cancel_function,
        'No, reset to Minimum Order Quantity !');
}


function fnDisableButton() {
    $('#btnPrint').attr('disabled', true);
    $('#btnSave').attr('disabled', true);
}

function fnEnableButton() {
    $('#btnPrint').removeAttr('disabled');
    $('#btnSave').removeAttr('disabled');
    $('#items_error').css("display", "none");
}

$(document).ready(function () {
    $('#dynamic-table tr.gradeX').each(function () {
        recalculateAmount(this, SO_ROW_INDEX_ITEM_QTY, SO_ROW_INDEX_ITEM_PRICE, SO_ROW_INDEX_AMOUNT, SO_LABEL_INDEX_AMOUNT, undefined, decimal_place);
    });
})


function setPartSupLOCRows($selects, currentRow, currentLabel, item_supp, item_loc) {
    $selects.each(function (selectIndex, selectValues) {
        if (selectIndex == SO_SELECT_INDEX_SUPPLIER) {
            var selected = currentRow[SO_ROW_INDEX_SUPPLIER_ID].value;
            if ($(this).data('select2')) {
                $(this).select2('destroy');
            }
            $(this).empty();

            var options = '';
            if (selected == '' || selected == undefined) {
                selected = item_supp[0].supplier_id;
            }
            for (i in item_supp) {
                options += "<option value="+item_supp[i].supplier_id+">"+item_supp[i].supplier_code+"</option>";
            }

            $(this).append(options);
            $(this).select2();

            setTimeout(() => {
                if (!$("#orderItemModal").is(':visible')) {
                    $(this).val(selected).trigger('change');
                }
            }, 100);
            $(this).on("select2:close", function (event) {
                $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_ITEM_QTY+')').focus();
            });

            handlePartInfo(this.id, false);
        }
        if ($('#company_is_inventory').val() == 'True' && selectIndex == SO_SELECT_INDEX_LOCATION) {
            var selected = $($selects[SO_SELECT_INDEX_LOCATION]).val();
            if ($(this).data('select2')) {
                $(this).select2('destroy');
            }
            $(this).empty();

            var options = '';
            if (selected == undefined || selected == null || selected == '') {
                selected = item_loc[0].location_id;
            }
            for (i in item_loc) {
                options += "<option value="+item_loc[i].location_id+">"+item_loc[i].location_code+"</option>";
            }

            $(this).append(options);
            $(this).select2();

            // setTimeout(() => {
            //     $(this).val(selected).trigger('change');
            // }, 100);
            $(this).on("select2:close", function (event) {
                $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_SCHEDULE_FAKE_DATE+')').focus();
            });
        }
    });
}
function setPartRows() {
    $('#dynamic-table tr.gradeX').each(function () {
        var selects = $(this).closest('tr').find('select');
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');
        var cur_item_id = currentRow[SO_ROW_INDEX_ITEM_ID].value;
        // var cur_supplier_id = currentRow[SO_ROW_INDEX_SUPPLIER_ID].value;
        // var cur_location_id = $(selects[SO_SELECT_INDEX_LOCATION]).val();
        // var cur_identity = '';
        var id_cus = 0;
        if ($('#id_customer').val() > 0){
            id_cus = $('#id_customer').val();
        }
        if (cur_item_id && id_cus) {
            $.ajax({
                type: "GET",
                url: '/orders/so_item_supp_info/'+id_cus+'/'+cur_item_id+'/',
                dataType: 'JSON',
                success: function(data){
                    var item_supp = data.data['sup'];
                    var item_loc = data.data['loc'];

                    setPartSupLOCRows(selects, currentRow, currentLabel, item_supp, item_loc);
                }
            });
        }

        // selects.each(function (selectIndex, selectValue) {
        //     if (selectIndex == SO_SELECT_INDEX_ITEM_CODE) {
        //         if ($(this).data('select2')) $(this).select2('destroy');

        //         $(this).empty();

        //         var options = '<option value="">Select Part Number</option>';
        //         $.each(item_list, function(i, v) {
        //             options += "<option data-code_data='["+JSON.stringify(v)+"]' value='"+v.id+"'>"+v.code+"</option>";
        //         });

        //         $(this).append(options);

        //         $(this).select2({
        //             placeholder: 'Select Part Number',
        //         });
        //         $(this).on("select2:open", function (event) {
        //             prefill_select2(event);
        //         });
        //         $(this).on("select2:close", function (event) {
        //             $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_CUSTOMER_PO+')').focus();
        //         });
        //         if (cur_item_id != '') {
        //             setTimeout(() => {
        //                 $(this).val(cur_item_id).trigger('change');
        //             }, 100);
        //         }
        //         // $(this).val(currentRow[SO_ROW_INDEX_IDENTITY].value).trigger('change');
        //         $(this).on("change", function( event ){
        //             var $select = $(this).closest('select');
        //             var currentRow = $(this).closest('tr').find('input');
        //             var currentLabel = $(this).closest('tr').find('label');
        //             var $selects = $(this).closest('tr').find('select');

        //             var selected_item = $select.find('option:selected').data('code_data');
        //             select_val = $select.val();

        //             if (selected_item === undefined) {
        //                 $.each(item_list, function(k, v){
        //                     if (v.id === select_val) {
        //                         $select.find('option:selected').attr('data-code_data', JSON.stringify(v));
        //                         selected_item = v;
        //                         select_val = selected_item.id;
        //                     }
        //                 });
        //             } else {
        //                 selected_item = selected_item[0];
        //                 if (selected_item !== undefined) {
        //                     select_val = selected_item.id;
        //                 }
        //             }

        //             var id_cus = 0;
        //             if ($('#id_customer').val() > 0){
        //                 id_cus = $('#id_customer').val();
        //             }
        //             if (select_val != '') {
        //                 $.ajax({
        //                     type: "GET",
        //                     url: '/orders/so_item_supp_info/'+id_cus+'/'+select_val+'/',
        //                     dataType: 'JSON',
        //                     success: function(data){
        //                         var item_supp = data.data['sup'];
        //                         var item_loc = data.data['loc'];

        //                         setPartSupLOCRows($selects, currentRow, currentLabel, item_supp, item_loc);
        //                     }
        //                 });
        //             }
        //             // handlePartNumber(this.id);
        //         });
        //     }
        // });
    });
    if($('#company_is_inventory').val() == 'True' && old_loc.length && !doc_ready && order_id) {
        setTimeout(() => {
            $('#dynamic-table tr.gradeX').each(function (idx) {
                selects = $(this).closest('tr').find('select');
                $(selects[SO_SELECT_INDEX_LOCATION]).val(old_loc[idx]).trigger('change');
            });
        }, 2000);
    }
}


function load_part_numbers(){
    var id_cus = 0;
    if ($('#id_customer').val() > 0){
        id_cus = $('#id_customer').val();
    }
    $.ajax({
        type: "GET",
        url: "/orders/so_items_list/"+id_cus+'/',
        dataType: 'JSON',
        success: function(data){
            item_list.length = 0;
            if (data.data.length > 0){
                var array = data.data;
                for (i in array) {
                    item_list.push({
                        id: array[i].item_id,
                        code: array[i].code,
                        name: array[i].item_name
                    });
                }
                if(!doc_ready && order_id) {
                    setPartRows();
                    setTimeout(() => {
                        doc_ready = true;
                    }, 8000);
                } else {
                    doc_ready = true;
                }
            }
        },
        error: function(){
            doc_ready = true;
        }

    });
}

function load_part_infos(item_id, $selects=null){
    if (item_id != '') {
        var id_cus = 0;
        if ($('#id_customer').val() > 0){
            id_cus = $('#id_customer').val();
        }
        $.ajax({
            type: "GET",
            url: '/orders/so_item_supp_info/'+id_cus+'/'+item_id+'/',
            dataType: 'JSON',
            success: function(data){
                item_supp = data.data['sup'];
                item_loc = data.data['loc'];
                
                handleItemSupLoc($selects);
            }
        });
    }
}

function tabAddRow(rowIndex, code_pressed) {
    if (code_pressed == 9) {
        var rowCount = ($('#dynamic-table tr.gradeX')).length;
        if (rowIndex == rowCount) {
            $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
            setTimeout(() => {
                rowCount = ($('#dynamic-table tr.gradeX')).length;
                rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').attr('data-row_index');
                $('#id_formset_item-' + rowIndex +'-code').focus();
            }, 300);
        } else {
            rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + (rowIndex+1) + ')').attr('data-row_index');
            setTimeout(() => {
                $('#id_formset_item-' + rowIndex +'-code').focus();
            }, 300);
        }
    }
}

function handleItemSupLoc($selects) {
    if ($selects != null) {
        $selects.each(function (selectIndex, selectValues) {
            if ($('#company_is_inventory').val() == 'True' && selectIndex == SO_SELECT_INDEX_LOCATION) {
                var selected;
                if ($(this).data('select2')) {
                    $(this).select2('destroy');
                }
                $(this).empty();

                var options = '';
                if (selected == undefined || selected == null || selected == '') {
                    selected = item_loc[0].location_id;
                }
                for (i in item_loc) {
                    options += "<option value="+item_loc[i].location_id+">"+item_loc[i].location_code+"</option>";
                }

                $(this).append(options);
                $(this).select2();

                setTimeout(() => {
                    $(this).val(selected).trigger('change');
                }, 100);
                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_SCHEDULE_FAKE_DATE+')').focus();
                    // $('#modal_customer_po_no').focus();
                });
            }
            if (selectIndex == SO_SELECT_INDEX_SUPPLIER) {
                var selected;
                if ($(this).data('select2')) {
                    $(this).select2('destroy');
                }
                $(this).empty();

                var options = '';
                for (i in item_supp) {
                    options += "<option value="+item_supp[i].supplier_id+">"+item_supp[i].supplier_code+"</option>";
                    if (item_supp[i].supplier_id == item_supp[i].item_def_supp) {
                        selected = item_supp[i].item_def_supp;
                    }
                }

                $(this).append(options);
                $(this).select2();
                if (selected == undefined || selected == null || selected == '') {
                    selected = item_supp[0].supplier_id;
                }
                setTimeout(() => {
                    if (!$("#orderItemModal").is(':visible')) {
                        $(this).val(selected).trigger('change');
                    }
                }, 100);
                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_ITEM_QTY+')').focus();
                });
                
                handlePartInfo(this.id, false);
            }
        })
    } else {
        if ($('#company_is_inventory').val() == 'True' ) {
            var selected;
            if ($('#modal_location select').data('select2')) {
                $('#modal_location select').select2('destroy');
            }
            $('#modal_location select').empty();

            var options = '';
            if (selected == undefined || selected == null || selected == '') {
                selected = item_loc[0].location_id;
            }
            for (i in item_loc) {
                options += "<option value="+item_loc[i].location_id+">"+item_loc[i].location_code+"</option>";
            }

            $('#modal_location select').append(options);
            $('#modal_location select').select2();

            // setTimeout(() => {
            //     $('#modal_location select').val(selected).trigger('change');
            // }, 100);
            $('#modal_location select').on("select2:close", function (event) {
                $('#modal_customer_po_no').focus();
            });
        }
        var selected_supp;
        if ($('#modal_supplier select').data('select2')) {
            $('#modal_supplier select').select2('destroy');
        }
        $('#modal_supplier select').empty();

        var options = '';
        for (i in item_supp) {
            options += "<option value="+item_supp[i].supplier_id+">"+item_supp[i].supplier_code+"</option>";
            if (item_supp[i].supplier_id == item_supp[i].item_def_supp) {
                selected_supp = item_supp[i].item_def_supp;
            }
        }

        $('#modal_supplier select').append(options);
        $('#modal_supplier select').select2();
        if (selected_supp == undefined || selected_supp == null || selected_supp == '') {
            selected_supp = item_supp[0].supplier_id;
        }
        setTimeout(() => {
            $('#modal_supplier select').val(selected_supp).trigger('change');
        }, 100);

        $('#modal_supplier select').on("select2:close", function (event) {
            $('#modal_location select').focus();
            $('#modal_location select').select2('open');
        });

        handlePartInfo('#modal_supplier select', true);
    }
}

function handlePartInfo(tag_id, modal){
    if (modal) {
        $(tag_id).on("change", function( event ){
            var selected_item;
            var select_val = $(tag_id).val();
            if (select_val) {
                if (selected_item === undefined) {
                    id_cus = $('#id_customer').val();
                    var item_id;
                    $.each(item_list, function(k, v){
                        if (v.code === $('#modal_part_item_code').val()) {
                            item_id = v.id;
                        }
                    });
                    $.ajax({
                        type: "GET",
                        url: '/orders/so_orderitem_select/'+id_cus+'/'+item_id+'/',
                        dataType: 'JSON',
                        success: function(data){
                            if (data.data.length > 0){
                                item_info = data.data;
                                $.each(item_info, function(k, v){
                                    if (v.supplier_id === select_val) {
                                        selected_item = v;
                                    }
                                });
                                if (selected_item && selected_item.code === undefined) {

                                    $(this).closest('select option:selected').removeAttr('selected');
                
                                    $('#modal_uom').val('');
                                    // $('#modal_supplier').val('');
                                    $('#modal_category').val('');
                                    $('#modal_bkord_quantity').val('');
                                    $('#modal_amount').val('');
                
                                } else {
                                    $('#modal_location select').val(selected_item.location_id).trigger('change');
                                    $('#modal_part_name').val(selected_item.name);
                                    $('#modal_uom').val(selected_item.uom);
                                    $('#modal_category').val(selected_item.category);
                
                                    $('#modal_original_currency').val(selected_item.currency);
                                    $('#modal_bkord_quantity').val('0.00');
                                    if (float_format(selected_item.unit_price) > 0) {
                                        $('#modal_price').removeClass('highlight-mandatory');
                                    }
                                    $('#modal_price').val(float_format(selected_item.unit_price).toFixed(6));
                
                                    $('#modal_quantity').data('minoq', selected_item.minoq)
                                    $('#modal_quantity').trigger('keyup');
                                    $('#modal_customer_po_no').trigger('change');
                                    $('#modal_customer_po_no').focus();
                                }
                            }
                        }
                    });
                }
            }
        })
    } else {
        $('#' + tag_id).on("change", function( event ){
            var $select = $(this).closest('select');
            var currentRow = $(this).closest('tr').find('input');
            var currentLabel = $(this).closest('tr').find('label');
            var $selects = $(this).closest('tr').find('select');

            var selected_item;
            var select_val = $select.val();

            if (selected_item === undefined) {
                id_cus = $('#id_customer').val();
                var item_id = currentRow[SO_ROW_INDEX_ITEM_ID].value;
                if (item_id == '' || item_id == undefined) {
                    $.each(item_list, function(k, v){
                        if (v.code === currentRow[SO_ROW_INDEX_CODE].value) {
                            item_id = v.id;
                        }
                    });
                }
                $.ajax({
                    type: "GET",
                    url: '/orders/so_orderitem_select/'+id_cus+'/'+item_id+'/',
                    dataType: 'JSON',
                    success: function(data){
                        if (data.data.length > 0){
                            item_info = data.data;
                            $.each(item_info, function(k, v){
                                if (v.supplier_id === select_val) {
                                    selected_item = v;
                                }
                            });
                            if (selected_item && selected_item.code === undefined) {

                                $.each(currentRow, function(i, v) {
                                    if (i == SO_ROW_INDEX_CUSTOMER_PO) return;
                
                                    $($(this)).val('');
                                });
                
                                $(this).closest('tr').find('select option:selected').removeAttr('selected');
                
                                currentLabel[SO_LABEL_INDEX_UOM].textContent = '';
                                // currentLabel[SO_LABEL_INDEX_SUPPLIER_CODE].textContent = '';
                                currentLabel[SO_LABEL_INDEX_CATEGORY].textContent = '';
                                currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = '';
                                currentLabel[SO_LABEL_INDEX_CURRENCY_CODE].textContent = '';
                                currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = '';
                            } else if (selected_item !== undefined){
                                $.getJSON(url_get_item_backorder+'?item_id='+select_val, function(data) {
                                    var backorder_qty = 0;
                
                                    if (data.length > 0) {
                                        backorder_qty = data[0].rfs_qty;
                                    }
                
                                    currentRow[SO_ROW_INDEX_CODE].value =
                                        selected_item.code != undefined ? selected_item.code : '';
                                    currentRow[SO_ROW_INDEX_ITEM_NAME].value = selected_item.name;
                                    currentRow[SO_ROW_INDEX_ITEM_ID].value = selected_item.id;
                                    currentRow[SO_ROW_INDEX_IDENTITY].value = selected_item.identity;
                                    if (!$("#orderItemModal").is(':visible') && doc_ready) {
                                        currentRow[SO_ROW_INDEX_ITEM_PRICE].value = float_format(selected_item.unit_price).toFixed(6);
                                    }
                                    currentRow[SO_ROW_INDEX_CURRENCY_CODE].value = selected_item.currency;
                                    currentRow[SO_ROW_INDEX_CURRENCY_ID].value = selected_item.currency_id;
                
                                    if ($('#company_is_inventory').val() == 'True'){
                                        $($selects[SO_SELECT_INDEX_LOCATION]).val(selected_item.location_id).trigger('change');
                                        // $($selects[SO_SELECT_INDEX_LOCATION]).find('option[value="' + selected_item.location_id + '"]').prop('selected', true);
                                    }
                
                                    currentRow[SO_ROW_INDEX_UOM].value = selected_item.uom;
                                    currentRow[SO_ROW_INDEX_SUPPLIER_CODE].value = selected_item.supplier;
                                    currentRow[SO_ROW_INDEX_SUPPLIER_ID].value = selected_item.supplier_id;
                                    currentRow[SO_ROW_INDEX_CATEGORY].value = selected_item.category;
                                    currentRow[SO_ROW_INDEX_BACKORDER_QTY].value = backorder_qty;
                                    currentRow[SO_ROW_INDEX_QTY_RFS].value = float_format(selected_item.qty_rfs).toFixed(2);
                                    currentRow[SO_ROW_INDEX_MIN_ORDER_QTY].value = float_format(selected_item.minoq).toFixed(2);
                
                                    //add value to Label
                                    currentLabel[SO_LABEL_INDEX_UOM].textContent = currentRow[SO_ROW_INDEX_UOM].value;
                                    // currentLabel[SO_LABEL_INDEX_SUPPLIER_CODE].textContent = currentRow[SO_ROW_INDEX_SUPPLIER_CODE].value;
                                    currentLabel[SO_LABEL_INDEX_CATEGORY].textContent = currentRow[SO_ROW_INDEX_CATEGORY].value;
                                    currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = comma_format(currentRow[SO_ROW_INDEX_BACKORDER_QTY].value);
                                    currentLabel[SO_LABEL_INDEX_CURRENCY_CODE].textContent = currentRow[SO_ROW_INDEX_CURRENCY_CODE].value;
                                    // currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = int_comma(float_format(currentRow[SO_ROW_INDEX_AMOUNT].value).toFixed(2), 6);
                                    currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = comma_format(roundDecimal(currentRow[SO_ROW_INDEX_AMOUNT].value, decimal_place), decimal_place);
                                    if (doc_ready) {
                                        $('#' + currentRow[SO_ROW_INDEX_CUSTOMER_PO].id).trigger('change');
                                    }
                                    setTimeout(() => {
                                        $('#' + currentRow[SO_ROW_INDEX_ITEM_PRICE].id).trigger('change');
                                    }, 500);
                                });
                            }
                        }
                    }
                });
            }
        });
    }
}

function handlePartNumber(tag_id) {

    var part = $('#' + tag_id).val();
    $('#' + tag_id).on("keyup", function( event ){
        let line_number = $(this).closest('tr').attr('data-line_number');
        var that = this;
        if (!is_copy && check_linked(line_number) == true) {
            setTimeout(() => {
                 $(that).val(part);
                 $(that).attr('disabled', true);
            }, 200);
            return;
        }
    });


    $('#' + tag_id).on("change", function( event ){
        // var $select = $(this).closest('select');
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');
        var $selects = $(this).closest('tr').find('select');

        select_val = currentRow[SO_ROW_INDEX_CODE].value;
        var found = false;
        $.each(item_list, function(k, v){
            if (v.code === select_val) {
                select_val = v.id;
                found = true;
            }
        });
        if (found) {
            load_part_infos(select_val, $selects);
        } else {
            if (select_val == '') {
                $(this).addClass('highlight-mandatory');
            } else {
                currentRow[SO_ROW_INDEX_CODE].value = '';
                currentRow[SO_ROW_INDEX_ITEM_ID].value = '';
                $(this).trigger('change');
                currentRow[SO_ROW_INDEX_CODE].value = '';
                currentRow[SO_ROW_INDEX_ITEM_QTY].value = '0.00';
                currentRow[SO_ROW_INDEX_ITEM_PRICE].value = '0.000000';
                currentLabel[SO_LABEL_INDEX_UOM].textContent = '';
                currentLabel[SO_LABEL_INDEX_CATEGORY].textContent = '';
                currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = '';
                currentLabel[SO_LABEL_INDEX_CURRENCY_CODE].textContent = '';
                currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = '0.00';
                try {
                    $('#'+$selects[SO_SELECT_INDEX_SUPPLIER].id).empty().trigger("change");
                    if ($('#company_is_inventory').val() == 'True') {
                        $('#'+$selects[SO_SELECT_INDEX_LOCATION].id).empty().trigger("change");
                    }
                } catch (e) {
                    console.log(e);
                }
                pop_focus_invalid_dialog('Invalid Part No.',
                    'This part number can not be found',
                    function(){
                        
                    }, '#' + tag_id);
            }
        }
    });
}


function highLightMandatory(rowCheck) {
    if ( $('#id_formset_item-' + rowCheck +'-code').val() != '') {
        $('#id_formset_item-' + rowCheck +'-code').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-code').addClass('highlight-mandatory');
    }
    if ($('#id_formset_item-' + rowCheck +'-supplier').val() == '' || $('#id_formset_item-' + rowCheck +'-supplier').val() == undefined ) {
        $($('#select2-id_formset_item-' + rowCheck +'-supplier-container').parent('span')[0]).addClass('highlight-mandatory');
    } else {
        $($('#select2-id_formset_item-' + rowCheck +'-supplier-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ( $('#id_formset_item-' + rowCheck +'-customer_po_no').val() != '') {
        $('#id_formset_item-' + rowCheck +'-customer_po_no').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-customer_po_no').addClass('highlight-mandatory');
    }

    if ( $('#id_formset_item-' + rowCheck +'-wanted_fake_date').val() != '') {
        $('#id_formset_item-' + rowCheck +'-wanted_fake_date').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-wanted_fake_date').addClass('highlight-mandatory');
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

    if ( $('#id_formset_item-' + rowCheck +'-code').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-code';
        return idFirstInvalid;
    }

    if ($('#id_formset_item-' + rowCheck +'-supplier').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-supplier';
        return idFirstInvalid;
    }

    if ( $('#id_formset_item-' + rowCheck +'-customer_po_no').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-customer_po_no';
        return idFirstInvalid;
    }

    if ( $('#id_formset_item-' + rowCheck +'-wanted_fake_date').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-wanted_fake_date';
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


function initiatePartNumber($selector, $selected=null){
    $($selector).each(function () {
        let selects = $(this).closest('tr').find('select');
        let currentRow = $(this).closest('tr').find('input');
        let currentLabel = $(this).closest('tr').find('label');
        // var cur_item_id = currentRow[SO_ROW_INDEX_ITEM_ID].value;
        // var cur_supplier_id = currentRow[SO_ROW_INDEX_SUPPLIER_ID].value;
        // var cur_location_id = $(selects[SO_SELECT_INDEX_LOCATION]).val();
        // var cur_identity = '';
        // let rowIndex = parseInt($(this).closest('tr').find('label:first').text())-1;

        if($selected == null) {
            refreshCurrentRow(currentRow, currentLabel);
            // handleQuantity();
            handleEventTable();
            var $ItemQty = '#' + currentRow[SO_ROW_INDEX_ITEM_QTY].id;
            quantityEvent($ItemQty);
        }
        handlePartNumber(currentRow[SO_ROW_INDEX_CODE].id);

        selects.each(function (selectIndex, selectValues) {

            // if (selectIndex == SO_SELECT_INDEX_ITEM_CODE) {

            //     if ($(this).data('select2')) {
            //         $(this).select2('destroy');
            //     }

            //     $(this).empty();

            //     var options = '<option value="">Select Part Number</option>';

            //     $.each(item_list, function(i, v) {
            //         options += "<option data-code_data='["+JSON.stringify(v)+"]' value='"+v.id+"'>"+v.code+"</option>";
            //     });

            //     $(this).append(options);

            //     $(this).select2({
            //         placeholder: 'Select Part Number',
            //     });

            //     $(this).on("select2:open", function( event ){
            //         prefill_select2(event);
            //     });

            //     $(this).on("select2:close", function (event) {
            //         $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_CUSTOMER_PO+')').focus();
            //         let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            //         highLightMandatory(rowCheck);
            //     });

            //     $(this).prop('disable', false);
            //     $(this).select2('enable');

            //     if($selected == null) {
            //         handlePartNumber(this.id);
            //     }

            // }
            if ($('#company_is_inventory').val() == 'True' && selectIndex == SO_SELECT_INDEX_LOCATION) {
                if ($(this).data('select2')) {
                    $(this).select2('destroy');
                }
                $(this).empty();

                options = '<option value="">Select Location</option>';
                $(this).append(options);
                $(this).select2({
                    placeholder: 'Select Location',
                });

                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_SCHEDULE_DATE+')').focus();
                });
            }
            if (selectIndex == SO_SELECT_INDEX_SUPPLIER) {
                if ($(this).data('select2')) {
                    $(this).select2('destroy');
                }
                $(this).empty();

                options = '<option value="">Select Supplier</option>';
                $(this).append(options);
                $(this).select2({
                    placeholder: 'Select Supplier',
                });

                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('input:eq('+SO_ROW_INDEX_ITEM_QTY+')').focus();
                });
            }
        });
    });

}


function refreshCurrentRow(currentRow, currentLabel) {
    currentRow[SO_ROW_INDEX_CODE].value = '';
    currentRow[SO_ROW_INDEX_ITEM_QTY].value = '0.00';
    currentRow[SO_ROW_INDEX_ITEM_PRICE].value = '0.000000';
    $('#'+currentRow[SO_ROW_INDEX_ITEM_QTY].id).trigger('change');
    currentLabel[SO_LABEL_INDEX_UOM].textContent = '';
    // currentLabel[SO_LABEL_INDEX_SUPPLIER_CODE].textContent = '';
    currentLabel[SO_LABEL_INDEX_CATEGORY].textContent = '';
    currentLabel[SO_LABEL_INDEX_BACKORDER_QTY].textContent = '';
    currentLabel[SO_LABEL_INDEX_CURRENCY_CODE].textContent = '';
    currentLabel[SO_LABEL_INDEX_AMOUNT].textContent = '0.00';

    // set empty customer no
    $('#modal_customer_po_no').val('');
}


function load_cuss(){
    var date_rate = $("#id_document_date").val();
    var id_cus = $('#id_customer').val();
    var rate_type = 3;
    $.ajax({
        type: "GET",
        url: "/customers/get_by_pk/"+id_cus+'/'+date_rate+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                order_is_decimal = data.data[0].is_decimal;
                if (order_is_decimal) {
                    decimal_place = 2;
                } else {
                    decimal_place = 0;
                }
                $('#id_customer').val(data.data[0].id)
                $('#id_currency').val(data.data[0].currency_id).trigger('change');
                $('#name_currency').val(data.data[0].currency_name);
                $('#so_total').text("Total (" + data.data[0].currency_symbol + ') : ');
                $('#customer_payment_term').text(data.data[0].payment_term+' Days');
                $('#customer_payment_mode').text(data.data[0].payment_code);
                $('#customer_credit_limit').text(data.data[0].credit_limit);
                $('#customer_name').text(data.data[0].customer_name);
                $('#customer_address').text(data.data[0].address);
                $('#customer_email').text(data.data[0].email);
                recort_rate(data.data[0].currency_id,date_rate,rate_type);
            }
        }
    });
}

function recort_rate(curr_to, date_rate_1, rate_type) {
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

    row = $(selector+' tr.gradeX')[row_number];

    valid = ($(row).length != 0);

    if (!valid) {
        return false;
    }

    $labels = $(row).find('label');
    $inputs = $(row).find('input');
    $selects = $(row).find('select');

    // Check each field is empty
    if ($labels[SO_LABEL_INDEX_LINE_NUMBER].text === '') {
        console.log('Error, line number empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_CODE].value === '') {
        console.log('Error, item code empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_ITEM_NAME].value === '') {
        console.log('Error, item name empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_ITEM_ID].value === '') {
        console.log('Error, item id empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_SUPPLIER_CODE].value === '') {
        console.log('Error, supplier code empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_SUPPLIER_ID].value === '') {
        console.log('Error, supplier id empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_CUSTOMER_PO].value === '') {
        console.log('Error, customer po empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_WANTED_FAKE_DATE].value === '') {
        console.log('Error, wanted date empty');
        valid = false;
    }
    else if ($inputs[SO_ROW_INDEX_ITEM_QTY].value === '' || float_format($inputs[SO_ROW_INDEX_ITEM_QTY].value) == 0) {
        console.log('Error, quantity empty');
        valid = false;
    }

    return valid;
}


function is_modal_valid() {
        let valid = true;
        // Check each field is empty
        if ($('#modal_line_number').val() === '') {
            $('#modal_line_number').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_line_number').removeClass('highlight-mandatory');
        }

        if ($('#modal_part_item_code').val() === '') {
            $('#modal_part_item_code').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_part_item_code').removeClass('highlight-mandatory');
        }

        if ($('#modal_supplier select').val() == '' || $('#modal_supplier select').val() == undefined ) {
            $('#modal_supplier .select2').addClass('highlight-mandatory');
        } else {
            $('#modal_supplier .select2').removeClass('highlight-mandatory');
        }

         if ($('#modal_customer_po_no').val() === '') {
             $('#modal_customer_po_no').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_customer_po_no').removeClass('highlight-mandatory');
        }

         if ($('#modal_w_date').val() === '') {
            $('#modal_w_date').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_w_date').removeClass('highlight-mandatory');
        }

         if ($('#modal_quantity').val() === '' || float_format($('#modal_quantity').val()) <= 0) {
            $('#modal_quantity').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_quantity').removeClass('highlight-mandatory');
        }

         if ($('#modal_price').val() === '' || float_format($('#modal_price').val()) <= 0) {
            $('#modal_price').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_price').removeClass('highlight-mandatory');
        }
        return valid;
    }

// $("input[id*='-customer_po_no']").bind('keydown', function (event) {
//     if (event.which == 13) {
//         currentRow = $(this).closest('tr').find('input');
//         sel_cust_po_id = '#' + currentRow[SO_ROW_INDEX_CUSTOMER_PO].id;
//         sel_cust_po_no = $(sel_cust_po_id).val();
//         sel_part_code = currentRow[SO_ROW_INDEX_CODE].value;

//         $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {
//             $currentRow = $(this).closest('tr').find('input');
//             $cust_po_id = '#' + $currentRow[SO_ROW_INDEX_CUSTOMER_PO].id;
//             $cust_po_no = $($cust_po_id).val();
//             $part_code = $currentRow[SO_ROW_INDEX_CODE].value;
//             if (sel_cust_po_id != $cust_po_id) {
//                 if (sel_cust_po_no == $cust_po_no && sel_part_code == $part_code) {
//                     var title = "Duplicate Entry Error";
//                     var text = "Item "+ currentRow[SO_ROW_INDEX_CODE].value +
//                                 " in Customer PO No "+ currentRow[SO_ROW_INDEX_CUSTOMER_PO].value +
//                                 " is already in use !<br/> Do you want to proceed?"
//                     function ok_function() {move_next_elem($(sel_cust_po_id), 1);}
//                     function cancel_function(){$(sel_cust_po_id).select();}
//                     pop_ok_cancel_dialog(title, text, ok_function, cancel_function);
//                 }
//             }
//         });
//     }
// });
