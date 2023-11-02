var initial_item_qty = [];
var date_0 = $('#id_document_date').val();
var allVals = [];
var emptyRow = '';
var editing_row = null;
var append_index = 0;
var location_data = [];
var order_is_decimal = 1;
var decimal_place = 2;
var remainQuantity = 0;
var rfn_exclude_list = [];
var ref_line_count = 0;
var ref_remain_quantity = 0;
var ramaining_qty_list = [];

var invalid_data_list = [];
var invalid_message_list = [];
var is_disable_show_duplicate = false;
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
                    <td><label class="control-label-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number">1</label>
                    <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-line_id" name="formset_item-0-line_id" style="display: none" type="text">
                </td>
                <td>
                    <select id="id_select-0-ref_number" class="form-control select_ref_number" name="select-0-ref_number" required="required">

                        </select>
                    <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="display: none" type="text">
                </td>
                <td>
                    <select id="id_select-0-refer_line" class="form-control select_refer_line" name="select-0-refer_line" required="required">

                        </select>
                    <input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="display: none" type="text">
                </td>

                <td>
                    <label class="control-label-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="width: 180px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="display: none" type="text">
                </td>
                <td>
                    <select id="id_formset_item-0-location" class="form-control select_location" name="formset_item-0-location" style="width: 110px; text-align: center;">
                        </select>
                </td>
                <td>
                    <label class="control-label-item" id="id_formset_item-0-code" name="formset_item-0-code" style="width: 160px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                </td>
                <td style="width: 10%; display: none;">
                    <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;">None</label>
                    <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" required="required" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                <td><label class="control-label-item lblCurrency" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency"></label>
                    <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_price" id="id_formset_item-0-price" required="required" name="formset_item-0-price" style="text-align: right; width: 140px;" type="text"></td>
                <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" min="0" name="formset_item-0-exchange_rate" readonly="readonly" step="0.001" style="text-align: right; width: 80px;" type="number"></td>
                <td><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label><input class="form-control-item text-right" id="id_formset_item-0-amount" readonly="readonly" min="0" name="formset_item-0-amount" step="0.1" style="text-align: right; width: 80px; display: none;" type="number">
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-category" name="formset_item-0-category" style="width: 70px;"></label>
                    <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                </td>
                <td>
                    <label class="control-label-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" style="width: 65px; text-align: right;"></label>
                    <input class="form-control-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" step="0.1" min=0 style="display: none" type="number">
                </td>
                <td>
                    <label class="control-label-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" style="width: 65px; text-align: right;"></label>
                    <input class="form-control-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" step="0.1" min=0 style="display: none" type="number">
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-supplier" name="formset_item-0-supplier" style="width: 80px;"></label>
                    <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                </td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
                <td style="display: none;"><input type="text" name="txt_outstanding_qty" value="0"></td>
                <td><label class="control-label-item" id="id_formset_item-0-uom" name="formset_item-0-uom"></label>
                    <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                </td>
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
                    <td><label class="control-label-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number">1</label>
                    <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-line_id" name="formset_item-0-line_id" style="display: none" type="text">
                </td>

                <td>
                    <select id="id_select-0-ref_number" class="form-control select_ref_number" name="select-0-ref_number" required="required">

                        </select>
                    <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="display: none" type="text">
                </td>
                <td>
                    <select id="id_select-0-refer_line" class="form-control select_refer_line" name="select-0-refer_line" required="required">

                        </select>
                    <input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="display: none" type="text">
                </td>

                <td>
                    <label class="control-label-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="width: 180px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="display: none" type="text">
                </td>

                <td>
                    <label class="control-label-item" id="id_formset_item-0-code" name="formset_item-0-code" style="width: 160px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                </td>
                <td style="width: 10%; display: none;">
                    <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="width: 220px;">None</label>
                    <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity" required="required" name="formset_item-0-quantity" style="text-align: right; width: 140px;" type="text"></td>
                <td><label class="control-label-item lblCurrency" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency"></label>
                    <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_price" id="id_formset_item-0-price" required="required" name="formset_item-0-price" style="text-align: right; width: 140px;" type="text"></td>
                <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" min="0" name="formset_item-0-exchange_rate" readonly="readonly" step="0.001" style="text-align: right; width: 80px;" type="number"></td>
                <td><label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label><input class="form-control-item text-right" id="id_formset_item-0-amount" readonly="readonly" min="0" name="formset_item-0-amount" step="0.1" style="text-align: right; width: 80px; display: none;" type="number">
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-category" name="formset_item-0-category" style="width: 70px;"></label>
                    <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                </td>
                <td>
                    <label class="control-label-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" style="width: 65px; text-align: right;"></label>
                    <input class="form-control-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" style="display: none" step="0.1" min=0 type="number">
                </td>
                <td>
                    <label class="control-label-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" style="width: 65px; text-align: right;"></label>
                    <input class="form-control-item" id="id_formset_item-0-receive_quantity" name="formset_item-0-receive_quantity" style="display: none" step="0.1" min=0 type="number">
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-supplier" name="formset_item-0-supplier" style="width: 80px;"></label>
                    <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                </td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-minimun_order" name="formset_item-0-minimun_order" type="number"></td>
                <td style="display: none;"><input type="text" name="txt_outstanding_qty" value="0"></td>
                <td><label class="control-label-item" id="id_formset_item-0-uom" name="formset_item-0-uom"></label>
                    <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                </td>
                </tr>`;
}


var GR_ROW_INDEX_LINE_NUMBER = 0;
var GR_ROW_INDEX_LINE_ID = GR_ROW_INDEX_LINE_NUMBER + 1;
var GR_ROW_INDEX_REFER_NO = GR_ROW_INDEX_LINE_ID + 1;
var GR_ROW_INDEX_REFER_LINE = GR_ROW_INDEX_REFER_NO + 1;
var GR_ROW_INDEX_CUSTOMER_PO = GR_ROW_INDEX_REFER_LINE + 1;
var GR_ROW_INDEX_ITEM_CODE = GR_ROW_INDEX_CUSTOMER_PO + 1;
var GR_ROW_INDEX_ITEM_NAME = GR_ROW_INDEX_ITEM_CODE + 1;
var GR_ROW_INDEX_ITEM_ID = GR_ROW_INDEX_ITEM_NAME + 1;
var GR_ROW_INDEX_ITEM_QTY = GR_ROW_INDEX_ITEM_ID + 1;
var GR_ROW_INDEX_CURRENCY_CODE = GR_ROW_INDEX_ITEM_QTY + 1;
var GR_ROW_INDEX_CURRENCY_ID = GR_ROW_INDEX_CURRENCY_CODE + 1;
var GR_ROW_INDEX_PRICE = GR_ROW_INDEX_CURRENCY_ID + 1;
var GR_ROW_INDEX_EXCHANGE_RATE = GR_ROW_INDEX_PRICE + 1;
var GR_ROW_INDEX_AMOUNT = GR_ROW_INDEX_EXCHANGE_RATE + 1;
var GR_ROW_INDEX_CATEGORY = GR_ROW_INDEX_AMOUNT + 1;
var GR_ROW_INDEX_ORDER_QTY = GR_ROW_INDEX_CATEGORY + 1;
var GR_ROW_INDEX_RECEIVE_QTY = GR_ROW_INDEX_ORDER_QTY + 1;
var GR_ROW_INDEX_SUPPLIER_CODE = GR_ROW_INDEX_RECEIVE_QTY + 1;
var GR_ROW_INDEX_SUPPLIER_ID = GR_ROW_INDEX_SUPPLIER_CODE + 1;
var GR_ROW_INDEX_REF_ID = GR_ROW_INDEX_SUPPLIER_ID + 1;
var GR_ROW_INDEX_MIN_ORDER = GR_ROW_INDEX_REF_ID + 1;
var GR_ROW_INDEX_OUTSTANDING_QTY = GR_ROW_INDEX_MIN_ORDER + 1;
var GR_ROW_INDEX_UOM = GR_ROW_INDEX_OUTSTANDING_QTY + 1;

var GR_LABEL_INDEX_LINE_NUMBER = 0;
var GR_LABEL_INDEX_CUSTOMER_PO_NO = GR_LABEL_INDEX_LINE_NUMBER + 1;
var GR_LABEL_INDEX_ITEM_CODE = GR_LABEL_INDEX_CUSTOMER_PO_NO + 1;
var GR_LABEL_INDEX_ITEM_NAME = GR_LABEL_INDEX_ITEM_CODE + 1;
var GR_LABEL_INDEX_CURRENCY_CODE = GR_LABEL_INDEX_ITEM_NAME + 1;
var GR_LABEL_INDEX_AMOUNT = GR_LABEL_INDEX_CURRENCY_CODE + 1;
var GR_LABEL_INDEX_CATEGORY = GR_LABEL_INDEX_AMOUNT + 1;
var GR_LABEL_INDEX_ORDER_QTY = GR_LABEL_INDEX_CATEGORY + 1;
var GR_LABEL_INDEX_RECEIVE_QTY = GR_LABEL_INDEX_ORDER_QTY + 1;
var GR_LABEL_INDEX_SUPPLIER_CODE = GR_LABEL_INDEX_RECEIVE_QTY + 1;
var GR_LABEL_INDEX_UOM = GR_LABEL_INDEX_SUPPLIER_CODE + 1;

var GR_SELECT_INDEX_LOCATION;
var GR_SELECT_INDEX_REF_NUMBER = 0;
var GR_SELECT_INDEX_REFER_LINE = GR_SELECT_INDEX_REF_NUMBER + 1;
if($('#company_is_inventory').val() == 'True') {
    GR_SELECT_INDEX_LOCATION = GR_SELECT_INDEX_REFER_LINE + 1;
}


/* GR Column Index */

var GR_COL_BUTTONS = 0;
var GR_COL_LINE_NUMBER = GR_COL_BUTTONS + 1;

if($('#company_is_inventory').val() == 'True') {
    var GR_COL_LOC_CODE = GR_COL_LINE_NUMBER + 1;
    var GR_COL_REF_NUMBER = GR_COL_LOC_CODE + 1;
} else {
    var GR_COL_REF_NUMBER = GR_COL_LINE_NUMBER + 1;
}

var GR_COL_REFER_LINE = GR_COL_REF_NUMBER + 1;
var GR_COL_CUSTOMER_PO = GR_COL_REFER_LINE + 1;
var GR_COL_PART_NO = GR_COL_CUSTOMER_PO + 1;
var GR_COL_ITEM_NAME = GR_COL_PART_NO + 1;
var GR_COL_QTY = GR_COL_ITEM_NAME + 1;
var GR_COL_CURRENCY = GR_COL_QTY + 1;
var GR_COL_PRICE = GR_COL_CURRENCY + 1;
var GR_COL_EXCHNG_RATE = GR_COL_PRICE + 1;
var GR_COL_AMOUNT = GR_COL_EXCHNG_RATE + 1;
var GR_COL_PART_GROUP = GR_COL_AMOUNT + 1;
var GR_COL_ORDER_QTY = GR_COL_PART_GROUP + 1;
var GR_COL_RECEV_QTY = GR_COL_ORDER_QTY + 1;
var GR_COL_SUPPLIER_CODE = GR_COL_RECEV_QTY + 1;
var GR_COL_UOM = GR_COL_SUPPLIER_CODE + 4;

let storeCopyRefNumberData = [];
$(document).ready(function () {

    // on first focus (bubbles up to document), open the menu
    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });


    // $('button').keypress(function(event){
    //     var keycode = (event.keyCode ? event.keyCode : event.which);
    //     if(keycode == '13'){
    //         $(this).trigger('click');
    //     }
    // });

    $(document).on('select2:close', '#id_supplier', function (e) {
      $('#id_document_number').focus();
    });

    $(document).on('select2:close', '#id_tax', function (e) {
      $('.editrow').focus();
    });

    $(document).on('select2:close', '#modal_ref_number_select', function (e) {
      $('#modal_refer_line_select').focus();
    });

    $(document).on('select2:close', '#modal_refer_line_select', function (e) {
        if ($('#modal_refer_line_select').val() == '' || $('#modal_refer_line_select').val() == null) {
            return false;
        }
        if ($("#modal_loc_item_code select").is(':visible')) {
            $("#modal_loc_item_code select").focus();
            $("#modal_loc_item_code select").select2('open');
        } else {
            $('#modal_quantity').focus();
        }
    });

    $(document).on('select2:close', '#modal_loc_item_code select', function (e) {
        $('#modal_quantity').focus();
    });

    $('#items_error').css("display", "none");
    if($('#company_is_inventory').val() == 'True') {
        get_location_list();
    }
    handleQuantity();
    // $('#btnSave').attr('disabled', true);
    $('input').bind('input propertychange', function() {
        $('#btnSave').removeAttr('disabled');
    });
    $('select').change(function() {
        $('#btnSave').removeAttr('disabled');
    });
    $('textarea').bind('input propertychange', function() {
        $('#btnSave').removeAttr('disabled');
    });

    $('#id_tax').select2();
    $('#id_tax').on("select2:open", function( event ){
        prefill_select2(event);
    });


    $('#id_distribution_code').select2();
    $('#id_distribution_code').on("select2:open", function( event ){
        prefill_select2(event);
    });

    if (!order_id){
        $('#id_currency').val(0);
        $('#id_tax').val(0);
        $('#id_document_type').val('B');
    }

    $('#id_exchange_rate_value').val($('#id_exchange_rate').val());
    if (!$('#id_supplier').val()){
        $('#id_currency').val(0);
        $('#btnOpenItemDialog').attr('disabled', 'disabled');
        $('#txtPONo').prop('disabled', true);
    }
    if (($('#id_supplier').val() != '') && ($('#id_supplier').val() > 0) && (!$('#id_exchange_rate').val())) {
        load_supp();
    }
    var cust_edit = $("#selector_currency option:selected").text();
    $('#selector_currency').addClass('hide');

    $('#name_currency').val(cust_edit);

    $('#id_transaction_code').select2();
    $('.location_select select').select2();

    $('#po_by_supp').select2({
        placeholder: "PO Number",
    });

    $('#id_supplier').select2({
        placeholder: "Select supplier",
    });
    $('#id_supplier').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#id_document_type').select2({
        placeholder: "Select Doc Type",
    });
    $('#id_document_type').on("select2:open", function( event ){
        prefill_select2(event);
    });

    var date_1 = dateView($('#id_document_date').val());
    $('#copy_date_doc').val(date_1);
    $('#id_document_date').addClass('hide');
    // $('form input').on('keypress', function (e) {
    //     return e.which !== 13;
    // });
    $('#id_supplier').on('change', function() {
        $('#btnOpenItemDialog').removeAttr('disabled');
        $('#txtPONo').prop('disabled', false);
        $('#dynamic-table tbody').find('tr').remove();
        $('#id_subtotal').val(0);
        $('#id_total').val(0);
        $('#id_tax_amount').val(0);
        $(emptyRow).insertBefore('#id_formset_item-TOTAL_FORMS');
        $('#id_formset_item-TOTAL_FORMS').val('1');
        disableAutoComplete();
        load_supp();
        load_po_numbers();
        fnEnableButton();
        rfn_exclude_list = [];
        append_index = 1;
    });

    if (!$('#id_supplier').val()){
        $('#id_supplier').select2("open");
    }

    $('#invalidInputModal').on('shown.bs.modal', function () {
        if ($("#orderItemModal").is(':visible')) {
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
        } else {
            try {
                $('#modal_ref_number select').select2('close');
                $('#modal_refer_line select').select2('close');
            } catch(e) {
                
            }
        }
    });

    $('#comfirmSaveDeleteOrderModal').on('shown.bs.modal', function () {
        if ($("#comfirmSaveDeleteOrderModal").is(':visible')) {
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
        } else {
            try {
                $('#modal_ref_number select').select2('close');
                $('#modal_refer_line select').select2('close');
            } catch(e) {
                
            }
        }
    });

    let allItemQty = getAllItemQty();

    setTimeout(() => {
        get_refer_order_items(allItemQty);
    }, 2000);

});

function get_refer_order_items(allItemQty) {
    var all_po = [];
    for (j in allItemQty) {
        if (allItemQty[j].order_id) {
            all_po.push(allItemQty[j].order_id);
        }
    }
    var all_pos = JSON.stringify(all_po);
    $.ajax({
        method: "POST",
        url: '/orders/get_order_item_by_po_no/',
        dataType: 'JSON',
        async: false,
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'po_number': all_pos,
            'supplier_id': $('#hdSupplierId').val(),
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
                        'original_item_quantity': temp_object.ord_qty,
                        'ref_line': temp_object.refer_line,
                        'ref_line_list': ref_line_list,
                    });
                }
            }
        }
    });
}


$('#id_document_type').on("select2:close", function() {
    $('#id_supllier_exchange_rate').focus();
});


$('#id_distribution_code').on("select2:close", function() {
    $('#id_tax').select2("open");
});

// $('#id_tax').on("select2:close", function() {
//     $('#po_by_supp').select2("open");
// });

$('#po_by_supp').on("select2:close", function() {
    $('#po_by_supp').focus();
});

function get_location_list() {
    $.ajax({
        method: "GET",
        url: '/orders/location_code_list/',
        dataType: 'JSON',
        success: function (json) {
            location_data = json;

            if ($('#company_is_inventory').val() == 'True' && order_id) {
                $('#dynamic-table tr.gradeX').each(function () {
                    selects = $(this).closest('tr').find('select');
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
                });
            }
        }
    });
}

//Pagination and search item
$(document).ready(function () {
    var initial_item = getAllItemQty();
    for (i=0; i<initial_item.length; i++){
        initial_item_qty.push(initial_item[i]);
    }
    $('#initial_item_qty_data').val(JSON.stringify(initial_item_qty));
});

//Add Extra Label Value formset
$(document).ready(function () {
    checkDisplay();
    var status = $('#status').text();
    var supplier = $('#hdSupplierId').val();
    if (supplier != null) {
        $('#dynamic-table tbody').find('tr.gradeX:last').remove();
        let total = parseInt($('#id_formset_item-TOTAL_FORMS').val());
        total--;
        $('#id_formset_item-TOTAL_FORMS').val(total);
        if (total == 0) {
            setTimeout(() => {
                $('#id_supplier').select2('open');
            }, 300);
        } else {
            load_refer_numbers();
            append_index = $('#dynamic-table').find('tr.gradeX').length;
        }
        if (status == '0') { /* ORDER_STATUS['Undefined'] */
            $('#btnOpenItemDialog').css('display', 'none');
            var items_name_list = [];
            selector.each(function () {
                currentRow = $(this).closest('tr').find('input');
                currentLabel = $(this).closest('tr').find('label');
                var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
                var quantity_receive = float_format(currentLabel[GR_LABEL_INDEX_RECEIVE_QTY].textContent);
                if (quantity <= 0) {
                    pop_ok_dialog("Invalid Quantity",
                        "The quantity of product " +
                        currentRow[GR_ROW_INDEX_ITEM_CODE].value +
                        " must be greater than 0",
                        function(){
                            $('#'+currentRow[GR_ROW_INDEX_ITEM_QTY].id).val(0).trigger("change");
                            $current_element = '#' + e.target.id;
                            $($current_element).select();
                    });
                }
                else if (float_format(quantity) == 0) {
                    items_name_list.push(currentRow[GR_ROW_INDEX_ITEM_NAME].value);
                    $(this).closest('tr').attr('style', 'background-color: aqua !important');
                    $('#' + currentRow[GR_ROW_INDEX_ITEM_QTY].id).attr('disabled', true);
                }
            });
            var uniqueNames = [];
            $.each(items_name_list, function (i, el) {
                if ($.inArray(el, uniqueNames) === -1) {
                    uniqueNames.push(el);
                }
            });
            if (uniqueNames.length > 0) {
                pop_ok_dialog("Invalid Part No",
                    "The products "+uniqueNames+" were already received !",
                    function(){
                        currentRow[GR_ROW_INDEX_AMOUNT].value = 0;
                        fnDisableButton();
                        $current_element = '#' + e.target.id;
                        $($current_element).select();
                });
            }
        }
    } else {
        fnDisableButton();
    }

    // $('#add_more_right').click(function () {
    //     cloneMore('div.table-right:last', 'formset_right');
    // });
    // $('#add_more_left').click(function () {
    //     cloneMore('div.table-left:last', 'formset_left');
    // });
    // $('#add_more_code').click(function () {
    //     cloneMore('div.table-code:last', 'formset_code');
    // });
    // function cloneMore(selector, type) {
    //     var display = $(selector).css("display")
    //     if (display == 'none') {
    //         $(selector).removeAttr("style")
    //     }
    //     else {
    //         var total = $('#id_' + type + '-TOTAL_FORMS').val();
    //         var newElement = $(selector).clone(true);
    //         newElement.removeAttr("style")
    //         newElement.find(':input').each(function () {
    //             var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
    //             var id = 'id_' + name;
    //             $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    //         });
    //         newElement.find('label').each(function () {
    //             var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
    //             $(this).attr('for', newFor);
    //         });
    //         total++;
    //         $('#id_' + type + '-TOTAL_FORMS').val(total);
    //         $(selector).after(newElement);
    //     }
    // }

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
            }
        }
    }
});


//Load tax rate
$(document).ready(function () {
    $('#id_tax').change(function () {
        console.log('TAX change');
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
                    $('#id_tax_amount').val(comma_format(float_format(tax_amount)));
                    $('#hdTaxRate').val(float_format(json).toFixed(2));
                    var total = float_format($('#id_subtotal').val()) +
                        tax_amount -
                        float_format($('#id_discount').val());
                    $('#id_total').val(comma_format(float_format(total), decimal_place));
                }
            });
        }
    });
});

//Event check checkbox
$('input[type=checkbox]').click(function () {
    if ($(this).is(':checked'))
        $(this).attr('checked', 'checked');
    else
        $(this).removeAttr('checked');
});

var $last_quantity = '';

var $selected_row = [];
var append_or_prepend = false;

var dyn_tbl_sel_row_id = 0;
var next = false;
var prev = false;
var action_button = '';

var line_object = {
    'ref_num': '',
    'ref_line': '',
    'qty': '',
    'price': ''
}

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
            row_currency = ''
        }

        $selected_row.push({
            'row':newRowIndex,
            'ref_number': $('#id_formset_item-'+ (curRowIndex) +'-ref_number').val(),
            'qty': $('#id_formset_item-'+ (curRowIndex) +'-quantity').val(),
            'line': $('#id_formset_item-'+ (curRowIndex) +'-line_number').text(),
            'po_no': $('#id_formset_item-'+ (curRowIndex) +'-customer_po_no').text(),
            'code': $('#id_formset_item-'+ (curRowIndex) +'-code').text(),
            'currency': row_currency,
            'price': float_format($('#id_formset_item-'+ (curRowIndex) +'-price').val()).toFixed(6),
            'exch_rate': $('#id_formset_item-'+ (curRowIndex) +'-exchange_rate').val(),
            'amount': $('#id_formset_item-'+ (curRowIndex) +'-amount').text(),
            'category': $('#id_formset_item-'+ (curRowIndex) +'-category').text(),
            'order_qty': $('#id_formset_item-'+ (curRowIndex) +'-order_quantity').text(),
            'receive_qty': $('#id_formset_item-'+ (curRowIndex) +'-receive_quantity').text(),
            'supplier': $('#id_formset_item-'+ (curRowIndex) +'-supplier').val(),
            'supplier_code': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code').text(),
            'supplier_id': $('#id_formset_item-'+ (curRowIndex) +'-supplier_code_id').val(),
            'uom': $('#id_formset_item-'+ (curRowIndex) +'-uom').text(),
        });
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
            $('#id_formset_item-'+ ($selected_row[i].row) +'-uom').val($selected_row[i].uom);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-uom').text($selected_row[i].uom);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier').val($selected_row[i].supplier);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code').val($selected_row[i].supplier_code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code').text($selected_row[i].supplier_code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-supplier_code_id').val($selected_row[i].supplier_id);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-receive_quantity').val($selected_row[i].receive_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-receive_quantity').text($selected_row[i].receive_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-order_quantity').val($selected_row[i].order_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-order_quantity').text($selected_row[i].order_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').val($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-category').text($selected_row[i].category);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').val(float_format(row_amout).toFixed(decimal_place));
            $('#id_formset_item-'+ ($selected_row[i].row) +'-amount').text(row_amout);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-exchange_rate').val($selected_row[i].exch_rate);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-price').val($selected_row[i].price);
            // $('#id_formset_item-'+ ($selected_row[i].row) +'-price').text($selected_row[i].price);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-currency_id').val($selected_row[i].currency);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-code').val($selected_row[i].code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-code').text($selected_row[i].code);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').val($selected_row[i].po_no);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-customer_po_no').text($selected_row[i].po_no);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-line_number').val($selected_row[i].line);
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
            $('#modal_loc_item_code select').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    function removeRow(tthis) {
        // $selected_row = [];
        let rowIndex = $(tthis).closest('tr').attr('data-row_index');
        last_amount = float_format($('#id_formset_item-'+(rowIndex)+'-amount').text());

        let refer_number = $('#id_select-' + rowIndex +'-ref_number').val();
        let refer_line = $('#id_select-' + rowIndex +'-refer_line').val();
        if (refer_number == undefined) {
            refer_number = $('#id_formset_item-' + rowIndex +'-ref_number').text();
        }
        if (refer_line == undefined) {
            refer_line = $('#id_formset_item-' + rowIndex +'-refer_line').text();
        }

        if (refer_number != '' && refer_number != undefined) {
            let idx = $(tthis).closest('tr').find('label:first').text();
            storeCopyRefNumberData = saveCopyRefNumberDO(idx, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
            storeCopyRefNumberData = changeIndexData(idx, 'minus', storeCopyRefNumberData);

            if (rfn_exclude_list.indexOf(refer_number) != -1) {
                let indx = rfn_exclude_list.indexOf(refer_number);
                rfn_exclude_list.splice(indx, 1);
                filterAllReferNumber("GR", '#dynamic-table tr.gradeX', refer_number, GR_SELECT_INDEX_REF_NUMBER, -1, refer_numbers);
            }
        }
        if (refer_line != '' && refer_line != undefined) {
            filterAllReferNumber("GR", '#dynamic-table tr.gradeX', refer_number, GR_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, refer_line);
        }
        if (refer_number != '' && refer_line != '' && refer_line != undefined) {
            last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', refer_number, GR_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, refer_line, refer_line, "GR");
        }

        currentRow = $(tthis).closest('tr').find('input');
        item_id = currentRow[GR_ROW_INDEX_ITEM_ID].value;
        if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
            $(tthis).parents("tr").remove();
            $('#id_subtotal').val(0);
            $('#id_total').val(0);
            $('#id_tax_amount').val(0);
            let newRow = emptyRow;
            $('#id_formset_item-TOTAL_FORMS').before(newRow);
            newRow = $('#dynamic-table tr.gradeX:nth-child(1)').closest('tr');
            disableAutoComplete();

            setTimeout(() => {
                initiateRefNumber(newRow);
            }, 500);

        } else {
            // $('#loading').show();
            fnEnableButton();
            var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
            $('#id_formset_item-TOTAL_FORMS').val(minus);
            $(tthis).parents("tr").remove();

            let rowNumber = 0;
            let rows = $('#dynamic-table').find('tr.gradeX');
            $('#dynamic-table tr.gradeX').each(function () {
                let currentRow = $(this).closest('tr').find('input');
                let currentLine = $(this).closest('tr').find('label');
                currentLine[GR_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber + 1);
                currentRow[GR_ROW_INDEX_LINE_NUMBER].value = (rowNumber + 1);
                rowNumber++;
            });
            // rowNumber = rows.length - 1;
            // $selected_row.length = 0;

            // while (rowNumber >= rowIndex) {
            //     store_row_index(rowNumber, rowNumber + 1);
            //     change_row_attr(rowNumber + 1, rowNumber + 1, rowNumber);
            //     rowNumber--;
            // }

            setTimeout(() => {
                // bindingData();
                calculateGRTotal(last_amount, 0);
                // calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);
            }, 100);
        }
    }

    function showConfirm(tthis) {
        $.confirm({
            title: 'Confirmation',
            content: 'This cannot be reversable. Are you sure?',
            buttons: {
                Yes: {
                    btnClass: 'btn-success, Yes',
                    action: function(){
                        let rowIndex = parseInt($(tthis).closest('tr').attr('data-row_index'));
                        let row_id = $('#id_formset_item-' + rowIndex + '-id').val();
                        deleteSingleRow(row_id, tthis);
                    }
                },
                No: {
                    btnClass: 'btn-success, No',
                    action: function(){
                        
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
    }

    function deleteSingleRow(row_id, tthis) {
        $.ajax({
            method: "POST",
            url: '/orders/delete_order_single_row/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'row_id': row_id,
                'transaction_code': $('#id_transaction_code').val(),
            },
            success: function (json) {
                if (json.message == "Success") {
                    // load refer numbers again
                    load_refer_numbers();

                    // reset the initial list
                    let r_id = null;
                    $.each(initial_item_qty, function(idx, item) {
                        if (item.id == row_id) {
                            r_id = idx;
                        }
                    });
                    if (r_id) {
                        initial_item_qty.splice(r_id, 1);
                        $('#initial_item_qty_data').val(JSON.stringify(initial_item_qty));
                    }

                    // remove the row
                    removeRow(tthis);
                } else {
                    pop_ok_dialog("Delete failed", json.message, function(){});
                }
            }
        });
    }

    $(document).on('click', "[class^=removerow]", function (event) {
        closeAllSelectOnTable();
        var is_database = $(this).closest('tr').attr('data-is_database');
        if (is_database == '' || is_database == undefined) {
            ramaining_qty_list = update_remaining_qty(ramaining_qty_list, '', 0, parseInt($(this).closest('tr').attr('data-row_index')), true);
            removeRow(this);
        } else {
            showConfirm(this);
        }
    });

    $(document).on('click', "[class^=appendrow]", function (event) {
        // $('#loading').show();
        closeAllSelectOnTable();
        // $selected_row = [];
        let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
        let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));

        storeCopyRefNumberData = changeIndexData(rowIndex, 'plus', storeCopyRefNumberData);
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
            currentLine[GR_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
            currentRow[GR_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
            rowNumber++;
        });
        // rowNumber = rows.length-1;
        // $selected_row.length = 0;

        // while(rowNumber > rowIndex) {
        //     store_row_index(rowNumber, rowNumber - 1);
        //     change_row_attr(rowNumber + 1, rowNumber - 1, rowNumber);
        //     rowNumber--;
        // }

        rowNumber = append_index;
        change_new_row_attr(rowIndex+1, rowNumber);
        append_index++;

        newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex+1)+')').closest('tr');
        $(newRow).find('.editrow').prop('disabled', true);
        setTimeout(() => {
            $(newRow).find('.editrow').prop('disabled', false);
        }, 600);
        initiateRefNumber(newRow);
        setTimeout(() => {
            copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
            if ( copy_refer_number != '' && $('#id_select-' + (rowNumber) + '-ref_number option[value="' + copy_refer_number + '"]').length > 0) {
                $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
                $('#id_select-' + (rowNumber) + '-ref_number').select2('close');
            }
            // bindingData();
        }, 500);

    });

    $(document).on('click', "[class^=prependrow]", function (event) {
        // $('#loading').show();
        closeAllSelectOnTable();
        // $selected_row = [];
        let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
        let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        let prev_rowIndex = parseInt($(this).closest('tr').prev().attr('data-row_index'));

        storeCopyRefNumberData = changeIndexData((rowIndex - 1), 'plus', storeCopyRefNumberData);
        let copy_refer_number = $('#id_select-' + (prev_rowIndex) +'-ref_number').val();
        if (copy_refer_number == undefined) {
            copy_refer_number = $('#id_formset_item-' + (prev_rowIndex) +'-ref_number').text();
        }

        let rowNumber = 0;
        // let rows =  $('#dynamic-table').find('tr.gradeX');
        // rowNumber = rows.length;
        // timestart = window.performance.now();
        // $selected_row.length = 0;
        // while(rowNumber >= rowIndex) {
        //     store_row_index(rowNumber, rowNumber -1);
        //     change_row_attr(rowNumber, rowNumber - 1, rowNumber);
        //     rowNumber--;
        // }
        // timeend = window.performance.now();
        // whileTime = timeend-timestart;
        // console.log('whileTime', whileTime);

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
            currentLine[GR_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
            currentRow[GR_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
            rowNumber++;
        });

        //initialize select2 of new row
        let rows =  $('#dynamic-table').find('tr.gradeX');
        rowNumber = append_index;
        change_new_row_attr(rowIndex, rowNumber);
        append_index++;

        newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').closest('tr');
        $(newRow).find('.editrow').prop('disabled', true);
        setTimeout(() => {
            $(newRow).find('.editrow').prop('disabled', false);
        }, 600);
        initiateRefNumber(newRow);
        setTimeout(() => {
            copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
            if ( copy_refer_number != '' && $('#id_select-' + (rowNumber) + '-ref_number option[value="' + copy_refer_number + '"]').length > 0) {
                $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
                $('#id_select-' + (rowIndex) + '-ref_number').select2('close');
            }
            // bindingData();
        }, 500);
    });

    $(document).on('click', "[class^=editrow]", function (event) {
        editing_row = $(this).closest('tr');
        selectedRowId = $(this).closest('tr').attr('data-row_index');
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
        $('#modal_ref_number select').select2('close');
        $('#modal_refer_line select').select2('close');
        action_button = 'prev';
        if(is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            // var ok = is_modal_valid();
            // if (!ok) {
            //     var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            //     $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
            // }
            // selectedRowId = dyn_tbl_sel_row_id - 1;
            editing_row = editing_row.prev();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal_2(selectedRowId);
        }



    });

    $(document).on('click', "[id^=btnOrderItemNext]", function (event) {
        closeAllSelect2OnModal();
        next = true;
        prev = false;
        action_button = 'next';
        $('#modal_ref_number select').select2('close');
        $('#modal_refer_line select').select2('close');
        if (is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            // selectedRowId = dyn_tbl_sel_row_id + 1;
            editing_row = editing_row.next();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal_2(selectedRowId);
        }
    });

    $(document).on('click', "[id^=btnOrderItemSave]", function (event) {
        closeAllSelect2OnModal();
        selectedRowId = parseInt(editing_row.attr('data-row_index'));
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
            $('#modal_ref_number select').select2('close');
            $('#modal_refer_line select').select2('close');
            $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=save_new_line]", function (event) {
        closeAllSelect2OnModal();
        selectedRowId = dyn_tbl_sel_row_id;
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            setTimeout(() => {
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
        $('#modal_ref_number select').select2('close');
        $('#modal_refer_line select').select2('close');
        var ok = $.checkOrderRowValidity(dyn_tbl_sel_row_id);
        if (ok) {
            setTimeout(() => {
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

    $(document).on('click', "[id^=btnOrderItemNew]", function (event) {
        closeAllSelect2OnModal();
        if (is_change()) {
            $('#comfirmSaveNewOrderModal').modal('show');
        } else {
            itemNewRow();
        }
    });

    $(document).on('click', "[id^=remove_line]", function (event) {
        removeLine();
    });

    $(document).on('click', "[id^=save_line]", function (event) {
        // $('#orderItemModal').modal('toggle');
    });

    $(document).on('click', "[id^=reset_line]", function (event) {
        closeAllSelect2OnModal();
        resetLine();
    });

    $(document).on('click', "[id^=btnOrderItemCancel]", function (event) {
        closeAllSelect2OnModal();
        action_button = 'cancel';
        orderItemCancel();
    });

    $(document).on('click', "[id^=btnOrderItemDelete]", function (event) {
        closeAllSelect2OnModal();
        $('#comfirmSaveDeleteOrderModal').modal('show');
    });

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
        if ($inputs[GR_ROW_INDEX_LINE_NUMBER].value === '') {
            console.log('Error, line number empty');
            valid = false;
        }
        else if ($inputs[GR_ROW_INDEX_ITEM_CODE].value === '') {
            console.log('Error, item code empty');
            valid = false;
        }
        else if ($inputs[GR_ROW_INDEX_ITEM_NAME].value === '') {
            console.log('Error, item name empty');
            valid = false;
        }
        else if ($inputs[GR_ROW_INDEX_ITEM_ID].value === '') {
            console.log('Error, item id empty');
            valid = false;
        }
        else if ($inputs[GR_ROW_INDEX_CUSTOMER_PO].value === '') {
            console.log('Error, customer po empty');
            valid = false;
        }
        else if ($inputs[GR_ROW_INDEX_ITEM_QTY].value === '' || float_format($inputs[GR_ROW_INDEX_ITEM_QTY].value) == 0) {
            console.log('Error, quantity empty');
            valid = false;
        }

        return valid;
    }

    $('#modal_quantity').click(function () {
        $(this).select();
    });

    $('#modal_remarks').click(function () {
        $(this).select();
    });

    // $('#modal_loc_item_code').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_quantity').select();
    //         return false;
    //     }
    // });

    // $('#modal_quantity').bind('keydown', function (event) {
    //     if (event.which == 13) {
    //         $('#modal_quantity').val(comma_format($('#modal_quantity').val()));
    //         $('#btnOrderItemSave').focus();
    //         return false;
    //     }
    // });

    modal_quantity_change();
});

function modal_quantity_change() {
    var last_qty = 0;
    $('#modal_quantity').on("focus", function() {
        last_qty = float_format($(this).val());
    })
    $('#modal_quantity').off('change').on('change', function(e) {
        let rowId = parseInt(editing_row.attr('data-row_index'));
        let outstanding_qty = $('#modal_quantity').attr('outstanding_qty')
        let ord_qty = $('#modal_quantity').attr('ord_qty')
        let refer_line = $('#modal_refer_line select').find('option:selected').data('code_data');
        let check_refer_number = $('#modal_ref_number select').val();
        let line = editing_row.find('label:first').text();
        outstanding_qty = getTotalMaxInputQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, line);

        if (float_format($('#modal_quantity').val()) > float_format(outstanding_qty) && float_format(outstanding_qty) > 0) {
                WarnQtyExceded(outstanding_qty,this,
                "Quantity must not be greater than Outstanding Receive Quantity ("+ outstanding_qty +")");
        }
        else if (float_format($('#modal_quantity').val()) > float_format(ord_qty)) {
            WarnQtyExceded(ord_qty,this,
            "Quantity must not be greater than Order Quantity ("+ ord_qty +")");
        } else {
            $('#modal_quantity').removeClass('highlight-mandatory');
            $('#modal_quantity').val(comma_format(float_format($('#modal_quantity').val())));
            var amount = recalculateAmount(undefined, float_format($('#modal_quantity').val()), float_format($('#modal_price').val()), undefined, undefined, true);
            if (isNaN(amount)) amount = 0;
            $('#modal_amount').val(comma_format(float_format(amount).toFixed(decimal_place), decimal_place));

            var quantity = float_format($('#modal_quantity').val());
            if (outstanding_qty == -1) {
                outstanding_qty = float_format($('#modal_order_quantity').val()) - float_format($('#modal_receive_quantity').val());
            }
            storeCopyRefNumberData = updateQuantityCopyRefNumberDO(line, check_refer_number, refer_line, storeCopyRefNumberData, quantity, outstanding_qty);
            if (quantity < last_qty) {
                let check_refer_number = $('#modal_ref_number select').val();
                let check_refer_line = $('#modal_refer_line select').val();
                if (rfn_exclude_list.indexOf(check_refer_number) != -1) {
                    let indx = rfn_exclude_list.indexOf(check_refer_number);
                    rfn_exclude_list.splice(indx, 1);
                    filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, refer_numbers);
                } else {
                    filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, refer_numbers, check_refer_line);
                }
            }
            if (quantity == remainQuantity && ref_line_count == 1) {
                let check_refer_number = $('#modal_ref_number select').val();
                if (rfn_exclude_list.indexOf(check_refer_number) == -1) {
                    rfn_exclude_list.push(check_refer_number);
                }
                filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id);
            } else if (quantity == remainQuantity) {
                let check_refer_number = $('#modal_ref_number select').val();
                let check_refer_line = $('#modal_refer_line select').val();
                if (check_refer_number != '' && check_refer_line != '') {
                    filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, [], check_refer_line);
                }
            }

            // if (quantity == remainQuantity) {
            //     let check_refer_number = $('#modal_ref_number select').val();
            //     let check_refer_line = $('#modal_refer_line select').val();
            //     if (check_refer_number != '' && check_refer_line != '') {
            //         last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, rowIndex, refer_numbers, check_refer_line, last_refer_line, "GR");
            //     }
            // }
        }
    });
}


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

function doEssentials(currentRow){
    //Change currency
    var currency_id = parseInt($('#id_currency option:selected').val());
    // var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];
    if (currentRow[GR_ROW_INDEX_CURRENCY_ID].value != '' && currency_id != '') {
        arrItems.push({
            item_id: currentRow[GR_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[GR_ROW_INDEX_CURRENCY_ID].value
        });
        changeCurrency_2(arrItems, currency_id, currentRow);
    }
    // $('#dynamic-table tr.gradeX').each(function () {
    //     currentRow = $(this).closest('tr').find('input');
    //     arrItems.push({
    //         item_id: currentRow[GR_ROW_INDEX_ITEM_ID].value,
    //         currency_id: currentRow[GR_ROW_INDEX_CURRENCY_ID].value
    //     });
    // });
    fnEnableButton();
    // set customer code
    // if (allVals[0].supplier_code) {
    //     $('#form_supplier_code').val(allVals[0].supplier_code);
    // }
    // change customer according to the sales order
    // var e = jQuery.Event("keypress");
    // e.which = 13;
    // $("#form_supplier_code").trigger(e);

    // $('#dynamic-table tr.gradeX:first').each(function () {
    //     if($last_quantity === ''){
    //         $last_quantity = $(this).find("input[name*='quantity']");
    //     }
    // });

    // $('#dynamic-table tr.gradeX:last').each(function () {
    //     $quantity = $last_quantity[0].id;
    //     $quantity = $quantity.split('-');
    //     $quantity[1] = (float_format($quantity[1]) == 0) ? 0: float_format($quantity[1]) + 1;
    //     $quantity = $("#" + $quantity.join('-'));
    //     $last_quantity = $(this).find("input[name*='quantity']");
    //     // fix bug wrong quantity focus when tab
    //     // if ($quantity.length) {
    //     //     setTimeout(function() { $quantity.select();}, 300);
    //     // }
        
    // });
    // calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);
}

// $(document).ready(function () {
//     $('#dynamic-table tr.gradeX:last').each(function () {
//         calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);
//     });
// })

function calculateGRTotal(last_amount, new_amount) {
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
    tax_amount = roundDecimal(tax_amount, decimal_place);
    $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
    if ($('#id_discount').val() == '' || $('#id_discount').val() == null) {
        total = new_subtotal + float_format($('#id_tax_amount').val());
    } else {
        total = new_subtotal + float_format($('#id_tax_amount').val()) - float_format($('#id_discount').val());
    }
    total = roundDecimal(total, decimal_place);
    $('#id_total').val(comma_format(total, decimal_place));
}


function recalculateGRAmount(element, index_qty, index_price, index_amt, rowNumber, return_value){
    return_value = (return_value !== undefined);

    if (!return_value) {
        currentRow = $(element).closest('tr').find('input');
        currentLabel = $(element).closest('tr').find('label');

        var quantity = float_format(currentRow[index_qty].value);
        var price = float_format(currentRow[index_price].value);

        $('#'+currentRow[index_amt].id).val(roundDecimal(quantity * price, decimal_place));
        currentLabel[GR_LABEL_INDEX_AMOUNT].textContent = roundDecimal(quantity * price, decimal_place);
        // $('#id_formset_item-'+rowNumber+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));

        return roundDecimal(quantity * price, decimal_place);

    }
    else {
        return (roundDecimal(index_qty * index_price, decimal_place));
    }
}

function is_modal_valid() {
    let valid = true;
    // Check each field is empty
    if ($('#modal_ref_number select').val() === '' || $('#modal_ref_number select').val() === null) {
        console.log('Error, ref number empty');
        $($('#select2-modal_ref_number_select-container').parent('span')[0]).addClass('highlight-mandatory');
        valid = false;
    } else {
        $($('#select2-modal_ref_number_select-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ($('#modal_refer_line select').val() === '' || $('#modal_refer_line select').val() === null) {
        console.log('Error, ref  empty');
        $($('#select2-modal_refer_line_select-container').parent('span')[0]).addClass('highlight-mandatory');
        valid = false;
    } else {
        $($('#select2-modal_ref_number_select-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ($('#modal_quantity').val() === '' || float_format($('#modal_quantity').val()) <= 0) {
        console.log('Error, quantity empty');
        $('#modal_quantity').addClass('highlight-mandatory');
        valid = false;
    } else {
        $('#modal_quantity').removeClass('highlight-mandatory');
    }

    if ($('#modal_price').val() === '' || float_format($('#modal_price').val()) <= 0) {
        console.log('Error, price empty');
        $('#modal_price').addClass('highlight-mandatory');
        valid = false;
    } else {
        $('#modal_price').removeClass('highlight-mandatory');
    }
    return valid;
}


function bindOrderModalEvent() {
    $('#modal_ref_number select').on("change", function() {
        var hdSupplierId = $('#hdSupplierId').val();
        let po_number = $('#modal_ref_number select').find('option:selected').data('code_data');
        let refer_number = $('#modal_ref_number select').val();
        let found = false;
        let line = editing_row.find('label:first').text();
        $(storeCopyRefNumberData).each(function (indx, value) {
            if (value.line == line) {
                if (refer_number != value.ref_number && value.ref_number != 'remove' && value.ref_number != '') {
                    let idx = rfn_exclude_list.indexOf(value.ref_number);
                    rfn_exclude_list.splice(idx, 1);
                }
                found = true;
            }
        })
        if (po_number !== '' && po_number !== undefined) {
            $.ajax({
                method: "POST",
                url: '/orders/get_orderitems_by_po_no/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'po_number': po_number,
                    'supplier_id': hdSupplierId,
                    'exclude_item_list': []
                },
                success: function (json) {
                    allVals.length = 0;
                    ref_line_count = 0;
                    $.each(json, function (i, item) {
                        item_qty = item.outstanding_qty;
                        // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', refer_number, item.refer_line, GR_ROW_INDEX_ITEM_QTY, GR_SELECT_INDEX_REF_NUMBER, GR_SELECT_INDEX_REFER_LINE, item_qty);
                        ref_remain_quantity = get_remaining_qty(ramaining_qty_list, refer_number+'-'+item.refer_line, item_qty);
                        if (ref_remain_quantity) {
                            ref_line_count++;
                            allVals.push({
                                id: item.item_id,
                                price: item.purchase_price,
                                item_code: item.code,
                                name: item.item_name,
                                refer_number: item.refer_number,
                                refer_line: item.refer_line,
                                supplier_code: item.supplier_code,
                                location_code: item.location_code,
                                category: item.category,
                                unit_price: item.purchase_price,
                                currency: item.currency_code,
                                location_id: item.location_id,
                                currency_id: item.currency_id,
                                uom: item.uom,
                                supplier_id: item.supplier_id,
                                minimun_order: item.minimun_order,
                                ref_id: item.refer_id,
                                customer_po_no: item.customer_po_no,
                                quantity: item.quantity,
                                receive_quantity: item.receive_quantity,
                                outstanding_qty: item.outstanding_qty,
                                show: true
                            });
                        } else {
                            allVals.push({
                                id: item.item_id,
                                price: item.purchase_price,
                                item_code: item.code,
                                name: item.item_name,
                                refer_number: item.refer_number,
                                refer_line: item.refer_line,
                                supplier_code: item.supplier_code,
                                location_code: item.location_code,
                                category: item.category,
                                unit_price: item.purchase_price,
                                currency: item.currency_code,
                                location_id: item.location_id,
                                currency_id: item.currency_id,
                                uom: item.uom,
                                supplier_id: item.supplier_id,
                                minimun_order: item.minimun_order,
                                ref_id: item.refer_id,
                                customer_po_no: item.customer_po_no,
                                quantity: item.quantity,
                                receive_quantity: item.receive_quantity,
                                outstanding_qty: item.outstanding_qty,
                                show: false
                            });
                        }
                    });
                    if (!ref_line_count) {
                        $('#modal_ref_number select option[value="'+ refer_number +'"]').remove();
                        setTimeout(() => {
                            if ($("#orderItemModal").is(':visible')) {
                                $('#modal_ref_number select').select2('open');
                            }
                        }, 500);
                        if (rfn_exclude_list.indexOf(refer_number) == -1) {
                            rfn_exclude_list.push(refer_number);
                        }
                        filterAllReferNumber("GR", '#dynamic-table tr.gradeX', refer_number, GR_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id);
                    }

                    if ($('#company_is_inventory').val() == 'True') {
                        $('#modal_loc_item_code select').find('option[value=""]').prop('selected', true);
                    }

                    if ($('#modal_refer_line select').data('select2')) {
                        $('#modal_refer_line select').select2('destroy');
                    }

                    $('#modal_refer_line select').empty();

                    var options = '<option value="">Ref Ln</option>';

                    for (i in allVals) {
                        if (allVals[i].show) {
                            options += "<option data-code_data="+allVals[i].refer_line+" value="+allVals[i].refer_line+">"+allVals[i].refer_line+"</option>";
                        }
                    }

                    $('#modal_refer_line select').html(options);

                    $('#modal_refer_line select').select2({
                        placeholder: 'Ref Ln'
                    });

                    $('#modal_refer_line select').on("select2:open", function( event ){
                        prefill_select2(event);
                    });

                    setTimeout(function() {
                        if ($("#orderItemModal").is(':visible')) {
                            $('#modal_refer_line select').select2('open');
                        }
                        if (allVals.length == 1) {
                            $('#modal_refer_line select').val(allVals[0].refer_line).trigger('change');
                            $('#modal_refer_line select').select2('close');
                        }if ($('#modal_refer_line select option').length == 2) {
                            $('#modal_refer_line select').val($('#modal_refer_line select option:eq(1)').val()).trigger('change');
                            $('#modal_refer_line select').select2('close');
                        }
                    }, 300);
                }
            });
            $($('#select2-modal_ref_number_select-container').parent('span')[0]).removeClass('highlight-mandatory');
        } else {
            $('#modal_refer_line select').empty();
        }
        $('#modal_customer_po_no').val('');
        $('#modal_code').val('');
        $('#modal_supplier').val('');
        $('#modal_original_currency').val('');
        $('#modal_uom').val('');
        $('#modal_category').val('');
        $('#modal_quantity').val('').trigger('change');
        $('#modal_price').val('');
        $('#modal_amount').val('');
        $('#modal_order_quantity').val('');
        $('#modal_receive_quantity').val('');
    });

    $('#modal_refer_line select').on("change", function() {
        // var msg = check_duplicate(dyn_tbl_sel_row_id);
        // if (msg != '') {
        //     pop_ok_dialog("Duplicate Row", msg, function(){});
        // } else {
        // let refer_line = $('#modal_refer_line select').find('option:selected').data('code_data');
        let refer_line = $('#modal_refer_line select').val();

        let check_refer_number = $('#modal_ref_number select').val();
        let rowIndex = parseInt(editing_row.attr('data-row_index'));
        let line = editing_row.find('label:first').text();
        // remainQuantity = getRemainQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, allVals);
        // if (remainQuantity == undefined) {
        //     if (0 < getTotalMaxInputQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, line)) {
        //         remainQuantity = getTotalMaxInputQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, line);
        //     }
        // }
        storeCopyRefNumberData = saveCopyRefNumberDO(line, check_refer_number, refer_line, 'add', storeCopyRefNumberData, allVals);

        for(var i=0; i<allVals.length; i++) {
            if(allVals[i].refer_line == refer_line) {
                $('#modal_customer_po_no').val(allVals[i].customer_po_no);
                $('#modal_code').val(allVals[i].item_code);
                $('#modal_supplier').val(allVals[i].supplier_code);
                $('#modal_original_currency').val(allVals[i].currency);
                $('#modal_uom').val(allVals[i].uom);
                $('#modal_category').val(allVals[i].category);
                $('#modal_price').val(float_format(allVals[i].unit_price).toFixed(6));
                $('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
                $('#modal_order_quantity').val(comma_format(allVals[i].quantity));
                // if (remainQuantity == undefined) {
                //     remainQuantity = allVals[i].outstanding_qty;
                // }
                // $('#modal_receive_quantity').val(comma_format(allVals[i].quantity - float_format(remainQuantity)));
                if ($('#company_is_inventory').val() == 'True') {
                    if (allVals[i].location_id) {
                        if ($('#modal_loc_item_code select').data('select2')) {
                            $('#modal_loc_item_code select').select2('destroy');
                        }
                        $('#modal_loc_item_code select').empty();
                        var options = '';
                        options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                        $('#modal_loc_item_code select').append(options);
                        $('#modal_loc_item_code select').select2();
                        $('#modal_loc_item_code select').val(allVals[i].location_id).trigger('change');
                    } else {
                        $('#modal_loc_item_code select').val(1).trigger('change');
                    }
                }
                // remainQuantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, refer_line, GR_ROW_INDEX_ITEM_QTY, GR_SELECT_INDEX_REF_NUMBER, GR_SELECT_INDEX_REFER_LINE, allVals[i].outstanding_qty, rowIndex);
                remainQuantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+refer_line, allVals[i].outstanding_qty, rowIndex);
                $('#modal_quantity').attr({'outstanding_qty': allVals[i].outstanding_qty});
                $('#modal_quantity').attr({'ord_qty': allVals[i].quantity});
                if (remainQuantity == undefined) {
                    remainQuantity = allVals[i].outstanding_qty;
                    $('#modal_quantity').val(comma_format(remainQuantity)).trigger('change');
                } else if (remainQuantity > 0) {
                    $('#modal_quantity').val(comma_format(remainQuantity)).trigger('change');
                    // storeCopyRefNumberData = updateQuantityCopyRefNumberDO(line, check_refer_number, refer_line, storeCopyRefNumberData, remainQuantity)
                } else {
                    $('#modal_quantity').val(comma_format(remainQuantity)).trigger('change');
                }
                $('#modal_receive_quantity').val(comma_format(float_format($('#modal_order_quantity').val()) - float_format(remainQuantity)));

                $('#modal_price').removeClass('highlight-mandatory');
                $('#modal_quantity').removeClass('highlight-mandatory');
            }
        }
        if ($('#company_is_inventory').val() != 'True') {
            setTimeout(() => {
                $('#modal_quantity').select();
            }, 1000);
        }

    });

    modal_quantity_change();
}

function loadOrderItemModal_2(selectedRowId) {
    $('#loading').show();
    dyn_tbl_sel_row_id = selectedRowId;
    if ($('#id_formset_item-' + selectedRowId + '-line_number').text()) {
        let $selects = editing_row.find('select');
        $('#modal_line_number').val(editing_row.find('label:first').text());
        $('#modal_customer_po_no').val($('#id_formset_item-' + selectedRowId + '-customer_po_no').text());
        $('#modal_code').val($('#id_formset_item-' + selectedRowId + '-code').text());
        $('#modal_supplier').val($('#id_formset_item-' + selectedRowId + '-supplier').text());
        $('#modal_original_currency').val($('#id_formset_item-' + selectedRowId + '-original_currency').text());
        $('#modal_uom').val($('#id_formset_item-' + selectedRowId + '-uom').text());
        $('#modal_category').val($('#id_formset_item-' + selectedRowId + '-category').text());
        $('#modal_quantity').val($('#id_formset_item-' + selectedRowId + '-quantity').val());
        $('#modal_quantity').attr({'ord_qty': $('#id_formset_item-' + selectedRowId + '-order_quantity').text()});
        line_object['qty'] = $('#id_formset_item-' + selectedRowId + '-quantity').val();
        $('#modal_price').val($('#id_formset_item-' + selectedRowId + '-price').val());
        line_object['price'] = $('#id_formset_item-' + selectedRowId + '-price').val();
        $('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
        $('#modal_order_quantity').val($('#id_formset_item-' + selectedRowId + '-order_quantity').text());
        $('#modal_receive_quantity').val($('#id_formset_item-' + selectedRowId + '-receive_quantity').text());
        $('#modal_loc_item_code').empty();
        $('#id_formset_item-' + selectedRowId + '-location')
            .clone()
            .attr('id', 'modal_loc_item_code_select')
            .attr('tabindex','0')
            .appendTo('#modal_loc_item_code');
        if ($('#company_is_inventory').val() == 'True') {
            sel_loc = $('#id_formset_item-' + selectedRowId + '-location').val();
            $('#modal_loc_item_code select').removeAttr( 'style' );
            $('#modal_loc_item_code select').select2();
            $('#modal_loc_item_code select').val(sel_loc).trigger('change');
            $('#modal_loc_item_code select').on("select2:open", function (event) {
                prefill_select2(event);
            });
        } else {
            $('#loc_item').css('display', 'none');
            $('#modal_loc_item_code').css('display', 'none');
        }
        if(($('#company_is_inventory').val() == 'True' && $selects.length > 1) || ($('#company_is_inventory').val() != 'True' && $selects.length)) {//checking for GR edit mode
            if ($('#modal_ref_number select').data('select2')) {
                $('#modal_ref_number select').select2('destroy');
            }
            $('#modal_ref_number').empty();
            $('#id_select-' + selectedRowId + '-ref_number').trigger('select2:open');
            $('#id_select-' + selectedRowId + '-ref_number').select2('close');
            $('#id_select-' + selectedRowId + '-ref_number')
                .clone()
                .attr('id', 'modal_ref_number_select')
                .attr('tabindex','0')
                .appendTo('#modal_ref_number');
            current_code = $('#id_select-' + selectedRowId + '-ref_number').val();
            if (current_code == null || current_code == undefined) {
                current_code = ''
                line_object['ref_num'] = '';
            } else {
                line_object['ref_num'] = current_code;
            }

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
                    $('.select2-container span.select2-selection__rendered').css({
                        // 'text-align': 'left',
                        'font-size': '15px'
                    });
                    setTimeout(function() {
                        if ($("#orderItemModal").is(':visible')) {
                            if (current_code == '') {
                                $('#modal_ref_number select').select2('open');
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
                setTimeout(function() {
                    if ($("#orderItemModal").is(':visible')) {
                        $('#modal_ref_number select').select2('open');
                    }
                }, 300);
            }

            $('#modal_ref_number select').val(current_code).trigger('change');
            $('#modal_ref_number select').on("select2:open", function( event ){
                prefill_select2(event);

                // Fix Select2 input search style
                $('.select2-container input.select2-search__field').css({
                    // 'text-align': 'left',
                    'font-size': '12.5px'
                });
            });


            if ($('#modal_refer_line select').data('select2')) {
                $('#modal_refer_line select').select2('destroy');
            }
            $('#modal_refer_line').empty();
            $('#id_select-' + selectedRowId + '-refer_line').trigger('select2:open');
            current_code_l = $('#id_select-' + selectedRowId + '-refer_line').val();
            if (current_code_l == null || current_code_l == undefined) {
                current_code_l = ''
                line_object['ref_line'] = '';
            } else {
                line_object['ref_line'] = current_code_l;
            }
            $('#id_select-' + selectedRowId + '-refer_line').select2('close');
            $('#id_select-' + selectedRowId + '-refer_line')
                .clone()
                .attr('id', 'modal_refer_line_select')
                .attr('tabindex','0')
                .appendTo('#modal_refer_line');
            // $('#modal_refer_line select').val($('#id_select-' + selectedRowId + '-refer_line').val());
            if ($('#id_select-' + selectedRowId + '-customer_po_no').val() !== null) {
                setTimeout(function() {
                    // Generate Select2 element
                    $('#modal_refer_line select').select2({
                        // dropdownParent: $('#orderItemModal'),
                        placeholder: 'Ref Ln',
                    });

                    // Fix Select2 Style
                    $('#modal_refer_line .select2-container span.select2-selection__rendered').css({
                        // 'text-align': 'left',
                        'font-size': '15px'
                    });
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
                $('.select2-container input.select2-search__field').css({
                    // 'text-align': 'left',
                    'font-size': '12.5px'
                });
            });

            setTimeout(function() {
                if (current_code != '' && current_code_l == '') {
                    $('#modal_refer_line select').select2('open');
                    if ($('#modal_refer_line select option').length == 2) {
                        $('#modal_refer_line select').val($('#modal_refer_line select option:eq(1)').val()).trigger('change');
                        $('#modal_refer_line select').select2('close');
                    }
                }
            }, 300);

        } else {
            $('#modal_ref_number').empty();
            $('#modal_ref_number').html('<input id="modal_ref_number_input" tabindex="-1"  class="form-control" readonly="readonly" type="text" name="modal_ref_number_input"></input>');
            $('#modal_refer_line').empty();
            $('#modal_refer_line').html('<input id="modal_refer_line_input" tabindex="-1"  class="form-control" readonly="readonly" type="text" name="modal_refer_line_input"></input>');
            $('#modal_ref_number_input').val($('#id_formset_item-' + selectedRowId + '-ref_number').text());
            $('#modal_refer_line_input').val($('#id_formset_item-' + selectedRowId + '-refer_line').text());

             if ($('#company_is_inventory').val() == 'True' && is_sp_locked != "True") {
                setTimeout(function() {
                    $('#modal_loc_item_code select').select2('open');
                }, 500);
            } else if (is_sp_locked != "True") {
                setTimeout(function() {
                    $('#modal_quantity').focus();
                }, 500);
            }
        }

    }
    bindOrderModalEvent()
    controlPrevNextBtn();
    $('#loading').hide();
}

function check_duplicate(row_id) {
    var msg = '';
    $('#dynamic-table tr.gradeX').each(function () {
        let modal_ref_number = $('#modal_ref_number select').val();
        let modal_refer_line = $('#modal_refer_line select').val();
        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        let ref_number = '';
        let refer_line = '';
        try {
            let selects = $(this).closest('tr').find('select');
            ref_number = selects[GR_SELECT_INDEX_REF_NUMBER].value;
            refer_line = selects[GR_SELECT_INDEX_REFER_LINE].value;
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
    let modal_quantity = float_format($('#modal_quantity').val());
    let modal_price = float_format($('#modal_price').val());
    let location = $('#modal_loc_item_code select').val();
    $('#loading').modal('show');

    let selected_ref_num = line_object['ref_num'];
    let selected_ref_line = line_object['ref_line'];
    if (selected_ref_num != $('#modal_ref_number select').val()
        && $('#modal_ref_number select').val() != undefined) {
        $('#id_select-' + selectedRowId + '-ref_number').val(modal_ref_number).trigger('change');
    }
    setTimeout(() => {
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
        setTimeout(function() {
            $('#id_formset_item-' + selectedRowId + '-quantity').val(comma_format(modal_quantity)).trigger('change');
            $('#id_formset_item-' + selectedRowId + '-price').val(float_format(modal_price).toFixed(6)).trigger('change');

            $('#id_formset_item-' + selectedRowId + '-location').val(location).trigger('change');
            // $('#id_formset_item-' + selectedRowId + '-quantity').trigger('change');
            $('#loading').modal('hide');
        }, 600);
    }, 800);
}

// $('#orderItemModal').on('shown.bs.modal', function () {
//     $('#modal_loc_item_code select').focus();
// })

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
                $('#supplier_address').attr('data-pk', json['id']);
                $('#supplier_address').text(json['address']);
                $('#supplier_email').attr('data-pk', json['id']);
                $('#supplier_email').text(json['email']);

                $('#supplier_payment_term').text(json['term'] + ' days');
                $('#supplier_payment_mode').text(json['payment_mode']);
                $('#supplier_credit_limit').text(json['credit_limit']);
                loadSupplierInfo(json['id']);
                $('#id_tax').find('option').removeAttr("selected");
                $('#id_tax').find('option').removeAttr("disabled");
                $('#id_tax').find('option[value="' + json['tax_id'] + '"]').attr("selected", "selected");
                $('#id_tax').val(json['tax_id']).trigger('change');
                
                $('#id_currency').find('option').removeAttr('selected');
                $('#id_currency').find('option').removeAttr('disabled');
                $('#id_currency option[value=' + json['currency_id'] + ']').attr('selected', 'selected');
                $('#id_currency').val(json['currency_id']);
                $('#id_currency option:not(:selected)').attr('disabled', true);
            }
        })
    };
    
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
//event handle for input discount
$('#id_discount').change(function () {
    if ($(this).val() != '') {
        var sum = float_format($('#id_subtotal').val()) + float_format($('#id_tax_amount').val());
        sum -= float_format(this.value);
        $('#id_total').val(comma_format(float_format(sum), decimal_place));
    } else {
        var sum = 0;
        $('#dynamic-table tr.gradeX').each(function () {
            var currentRow = $(this).find('input');
            amount = currentRow[GR_ROW_INDEX_AMOUNT].value;
            sum += roundDecimal(amount, decimal_place);
            $('#id_subtotal').val(comma_format(sum, decimal_place));
            var total = sum + float_format($('#id_tax_amount').val());
            $('#id_total').val(comma_format(float_format(total), decimal_place));
        })
    }
});

$('#copy_date_doc').click(function(){
    $(this).select();
});

// $('#id_exchange_rate').click(function(){
//     $(this).select();
// });

$('#id_tax_exchange_rate').click(function(){
    $(this).select();
});

$('#id_supllier_exchange_rate').click(function(){
    $(this).select();
});

$('#id_document_number').click(function(){
    $(this).select();
});

$('#tax_currency').click(function(){
    $(this).select();
});


//event handle calculate subtotal and total base on quantity
function handleQuantity() {
    var last_price = 0.00;
    var last_qty_t = 0;
    $('#dynamic-table tr.gradeX').each(function () {
        currentRow = $(this).closest('tr').find('input');
        $ItemQty = '#' + currentRow[GR_ROW_INDEX_ITEM_QTY].id; // ID of Quantity Column
        var prv_qty = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);

        $($ItemQty).on('focus', function (e) {
            last_qty_t = float_format($(this).val());
        })

        $($ItemQty).off('change').on('change', function (e) {

            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');

            let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let $selects = $(this).closest('tr').find('select');
            let check_refer_number;
            let check_refer_line;
            let id_refer_line = '#' + $($(this).closest('tr').find('select')[GR_SELECT_INDEX_REFER_LINE]).id;
            let id_unit_price = '#id_formset_item-' + (rowIndex) + '-price';
            let old_line = false
            if(($('#company_is_inventory').val() == 'True' && $selects.length > 1) || ($('#company_is_inventory').val() != 'True' && $selects.length)) {
                check_refer_number = $($(this).closest('tr').find('select')[GR_SELECT_INDEX_REF_NUMBER]).val();
                check_refer_line = $($(this).closest('tr').find('select')[GR_SELECT_INDEX_REFER_LINE]).val();
            } else {
                check_refer_number = $('#id_formset_item-' + rowIndex +'-ref_number').text();
                check_refer_line = $('#id_formset_item-' + rowIndex +'-refer_line').text();
                old_line = true;
            }

            var quantity = float_format($(this).val());
            // if (quantity == 'NaN' || quantity < 0){
            //     quantity = 0;
            // }

            if ((quantity > 0 && check_refer_line == undefined) ||
                (quantity > 0 && check_refer_line == '')) {
                // pop_ok_dialog("Refer Line Empty",
                //     "Please select the refer line first",
                //     function(){
                //         $(id_refer_line).focus();
                //         $(id_refer_line).select2('open');
                //     }
                // );
                var unitPrice = float_format(currentRow[GR_ROW_INDEX_PRICE].value);
                var msgTitle = 'Refer Line Empty';
                var msgBody = 'Please select the refer line first.';
                if (check_refer_number == undefined || check_refer_number == '') {
                    msgTitle = 'Invalid Data';
                    msgBody = 'Please fill up the refer number, refer line.';

                    if (float_format(unitPrice) <= 0) {
                        msgBody = 'Please fill up the refer number, refer line, unit price.';
                    }
                }
                pop_ok_dialog(msgTitle,
                    msgBody,
                    function(){
                        if (check_refer_number != undefined && check_refer_number != '') {
                            $(id_refer_line).focus();
                            $(id_refer_line).select2('open');
                        }
                    }
                );
            } else {
                var row = $(this).closest('tr').find('label:first').text();
                var ord_qty = float_format($('#id_formset_item-'+(rowIndex)+'-order_quantity').text());
                var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);
                var quantities = getOutstandingQty(currentRow[GR_ROW_INDEX_REFER_NO].value, currentRow[GR_ROW_INDEX_ITEM_ID].value, initial_item_qty);
                var outstanding_qty = 0;

                // if(order_id == "") {
                //     outstanding_qty = float_format(getOutstandingQty(currentRow[GR_ROW_INDEX_REFER_NO].value, currentRow[GR_ROW_INDEX_ITEM_ID].value, initial_item_qty)).toFixed(2);
                // } else {
                //     outstanding_qty = float_format(getOutstandingQty(currentRow[GR_ROW_INDEX_REFER_NO].value, currentRow[GR_ROW_INDEX_ITEM_ID].value, initial_item_qty) + float_format(prv_qty)).toFixed(2);
                // }
                outstanding_qty = getTotalMaxInputQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, row);
                if (old_line) {
                    outstanding_qty = float_format(quantities.OutstandingQty + quantities.ItemQty).toFixed(2);
                }

                // currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(quantity);
                if (quantity == 'NaN' || quantity <= 0) {
                    if (outstanding_qty > 0) {
                        WarnQtyExceded(outstanding_qty,this,
                            "Quantity is invalid!");
                    } else if (last_qty_t > 0) { 
                        WarnQtyExceded(last_qty_t,this,
                            "Quantity is invalid!");
                    } else {
                        WarnQtyExceded(ord_qty,this,
                            "Quantity is invalid!");
                    }
                } else if (float_format(quantity) > float_format(outstanding_qty) &&
                    float_format(outstanding_qty) > 0) {
                    WarnQtyExceded(outstanding_qty, this,
                    "Quantity must not be greater than Outstanding Receive Quantity ("+ outstanding_qty +")");
                }
                else if (float_format(quantity) > float_format(ord_qty)) {
                    WarnQtyExceded(ord_qty, this,
                    "Quantity must not be greater than Order Quantity ("+ ord_qty +")");
                }
                else {
                    last_amount = float_format($('#id_formset_item-'+(rowIndex)+'-amount').text());
                    var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
                    var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);

                    // $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val(roundDecimal(quantity * price, decimal_place));
                    currentRow[GR_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
                    $('#id_formset_item-'+(rowIndex)+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
                    new_amount = roundDecimal(quantity * price, decimal_place);
                    calculateGRTotal(last_amount, new_amount);
                    $(this).closest('tr').removeAttr('style');
                    fnEnableButton();
                    // currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(quantity, 2);
                    $(this).val(comma_format(quantity));
                    // calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);

                    if (outstanding_qty == -1) {
                        order_quantity = float_format(currentRow[GR_ROW_INDEX_ORDER_QTY].value);
                        receive_quantity = float_format(currentRow[GR_ROW_INDEX_RECEIVE_QTY].value);
                        outstanding_qty = order_quantity - receive_quantity;
                    }
                    storeCopyRefNumberData = updateQuantityCopyRefNumberDO(row, check_refer_number, check_refer_line, storeCopyRefNumberData, $(this).val(), outstanding_qty);
                    if(!old_line) {
                        ramaining_qty_list = update_remaining_qty(ramaining_qty_list, check_refer_number+'-'+check_refer_line, quantity, rowIndex);
                    }

                    if (quantity < last_qty_t) {
                        if (rfn_exclude_list.indexOf(check_refer_number) != -1) {
                            let indx = rfn_exclude_list.indexOf(check_refer_number);
                            rfn_exclude_list.splice(indx, 1);
                            filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, -1, refer_numbers);
                        } else {
                            filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, check_refer_line);
                        }
                    }
                    
                    if (quantity == remainQuantity && ref_line_count == 1) {
                        if (rfn_exclude_list.indexOf(check_refer_number) == -1) {
                            rfn_exclude_list.push(check_refer_number);
                        }
                        filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, -1);
                    } else if (quantity == remainQuantity) {
                        if (check_refer_number != '' && check_refer_line != '') {
                            filterAllReferNumber("GR", '#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, rowIndex, [], check_refer_line);
                        }
                    }
                    if (quantity == remainQuantity) {
                        if (check_refer_number != '' && check_refer_line != '') {
                            last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, rowIndex, refer_numbers, check_refer_line, last_refer_line, "GR");
                        }
                    } else if (quantity < remainQuantity) {
                        if (check_refer_number != '' && check_refer_line != '') {
                            last_refer_line = check_refer_line;
                            last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', check_refer_number, GR_SELECT_INDEX_REF_NUMBER, rowIndex, refer_numbers, check_refer_line, last_refer_line, "GR");
                        }
                    }
                }
                if ($('#orderItemModal').hasClass('in')) {
                    $('#modal_amount').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-amount').text());
                    $('#modal_quantity').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-quantity').val());
                }
            }
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });
        $($ItemQty).click(function () {
            $(this).select();
        });

        $lastElement = '#' + currentRow[GR_ROW_INDEX_PRICE].id;
        $($lastElement).off('keydown').on('keydown', function(e) {
            if (e.which == 9) {
                let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
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
                    }, idFirstInvalid);
                } else {
                    $(this).removeClass('highlight-mandatory');
                    let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    let copy_refer_number = $('#id_select-' + (rowCheck) +'-ref_number').val();
                    if (copy_refer_number == undefined) {
                        copy_refer_number = $('#id_formset_item-' + (rowCheck) +'-ref_number').text();
                    }
                    tabAddRow(rowIndex, e.which, copy_refer_number);
                }
            }
        });

        $ItemPrice = '#' + currentRow[GR_ROW_INDEX_PRICE].id; // ID of Quantity Column

        $($ItemPrice).off('change').on('change', function (e) {
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
            if (quantity == 'NaN' || quantity < 0){
                quantity = 0;
            }
            currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(quantity);

            var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
            var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);
            if (price == 'NaN'){
                price = 0;
            }
            if (price <= 0) {
                WarnPriceExceded(float_format(1).toFixed(2), this,
                    "The Price of product "  + currentRow[GR_ROW_INDEX_ITEM_CODE].value +
                    " must be greater than 0.00");

                $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val("1.00");
            } else {
                last_amount = float_format($('#id_formset_item-'+(row-1)+'-amount').text());
                var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
                var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);

                // $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val(roundDecimal(quantity * price, decimal_place));
                currentRow[GR_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
                $('#id_formset_item-'+(row-1)+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
                new_amount = roundDecimal(quantity * price, decimal_place);
                $(this).closest('tr').removeAttr('style');
                fnEnableButton();

                calculateGRTotal(last_amount, new_amount);
                // calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);

            }
            if ($('#orderItemModal').hasClass('in')) {
                $('#modal_amount').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-amount').text());
                $('#modal_price').val($('#id_formset_item-' + dyn_tbl_sel_row_id + '-price').val());
            }

            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });
        $($ItemPrice).click(function () {
            $(this).select();
        });
    });

    $('#modal_price').on('focus', function() {
        last_price = float_format($(this).val());
    })
    $('#modal_price').off('change').on('change', function (e) {
        var price = float_format($(this).val());
        if (price == 'NaN'){
            price = 0;
        }
        if (price <= 0) {
            WarnPriceExceded(last_price.toFixed(6), this,
                "The Price of product "  + currentRow[GR_ROW_INDEX_ITEM_CODE].value +
                " must be greater than 0.00");
        } else {
            $('#modal_price').removeClass('highlight-mandatory');
            $('#modal_quantity').trigger('change');
            // $('#btnOrderItemSave').focus();
        }
    });
}

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $cust_po_no = '#' + currentRow[GR_ROW_INDEX_CUSTOMER_PO].id;
    $($cust_po_no).click(function () {
        $(this).select();
    });
});

// event copy supplier address
$('#btnCopySupplier').click(function () {
    var hdSupplierId = $('#hdSupplierId').val();
    $.ajax({
        method: "POST",
        url: '/orders/supplier/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'supplier_id': hdSupplierId,
        },
        success: function (json) {
            $('#id_name').val($('#supplier_name').text());
            $('#id_address').val($('#supplier_address').text());
            $('#id_email').val($('#supplier_email').text());
            $('#id_code').val(json['code']);
            $('#id_phone').val(json['phone']);
            $('#id_fax').val(json['fax']);
        }
    });
});

// event change address
$('#id_supplier_address').change(function () {
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
            if ($('#id_supplier_address option:selected').text() == "") {
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
                $('#id_name').val($('#id_supplier_address option:selected').text());
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


// event change exchange rate
$('#dynamic-table tr.gradeX').find('input').each(function () {
    currentRow = $(this).closest('tr').find('input');
    $exchangeRate = '#' + currentRow[GR_ROW_INDEX_EXCHANGE_RATE].id;
    $($exchangeRate).change(function () {
        currentRow = $(this).closest('tr').find('input');
        var exchange_rate = float_format(currentRow[GR_ROW_INDEX_EXCHANGE_RATE].value);
        var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);
        var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
        if (exchange_rate <= 0) {
            pop_ok_dialog("Invalid Exchange Rate",
                "The exchange rate of product " +
                currentRow[GR_ROW_INDEX_ITEM_CODE].value +
                " must be greater than 0 !",
                function(){
                    $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val(0).trigger("change");
                    fnDisableButton();
                    $exchangeRate.select();
                    $('#dynamic-table tr.gradeX').each(function () {
                        $(this).closest('tr').find('input').not(currentRow[GR_ROW_INDEX_EXCHANGE_RATE]).attr('disabled', true);
                    });
                }
            );

        } else {
            $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val(roundDecimal(price * quantity * exchange_rate, decimal_place)).trigger("change");
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $(this).closest('tr').removeAttr('style');
            fnEnableButton();
        }
    });
    $($exchangeRate).click(function () {
        $(this).select();
    });
});


function changeCurrency(arrItems, currency_id, currency_name) {
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
            var amount = 0;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    $('#dynamic-table tr.gradeX').each(function () {
                        currentRow = $(this).closest('tr').find('input');
                        currentLabel = $(this).closest('tr').find('label');
                        currentItem = currentRow[GR_ROW_INDEX_ITEM_CODE].value;
                        var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                        if (currentRow[GR_ROW_INDEX_ITEM_ID].value == json[i].id) {
                            currentRow[GR_ROW_INDEX_EXCHANGE_RATE].value = 1;
                            amount = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[GR_ROW_INDEX_PRICE].value);
                            $('#' + currentRow[GR_ROW_INDEX_AMOUNT].id).val(roundDecimal(amount, decimal_place)).trigger("change");
                            $('#id_formset_item-'+(row-1)+'-amount').text(comma_format(roundDecimal(amount, decimal_place)));
                            $('.lblCurrency').text(json['symbol']);
                        }
                    });
                }
            }
        }
    });
}

function changeCurrency_2(arrItems, currency_id, currentRow) {
    var doc_date = $('#id_document_date').val();
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
            var amount = 0;
            var row = $(currentRow[0]).parent().parent().attr('data-row_index');
            var last_amount = float_format($('#id_formset_item-'+row+'-amount').text());
            var new_amount = last_amount;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    if (currentRow[GR_ROW_INDEX_ITEM_ID].value == json[i].id) {
                        currentRow[GR_ROW_INDEX_EXCHANGE_RATE].value = 1;
                        var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
                        var price = float_format(currentRow[GR_ROW_INDEX_PRICE].value);
                        currentRow[GR_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
                        // $('#'+currentRow[GR_ROW_INDEX_AMOUNT].id).val(roundDecimal(quantity * price, decimal_place));
                        $('#id_formset_item-'+(row)+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
                        new_amount = roundDecimal(quantity * price, decimal_place);
                        // amount = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[GR_ROW_INDEX_PRICE].value);
                        // $('#' + currentRow[GR_ROW_INDEX_AMOUNT].id).val(float_format(amount).toFixed(decimal_place));
                        // $('#id_formset_item-'+(row-1)+'-amount').text(comma_format(float_format(currentRow[GR_ROW_INDEX_AMOUNT].value), decimal_place));
                        $('.lblCurrency').text(json['symbol']);
                        // new_amount = float_format($('#id_formset_item-'+(row-1)+'-amount').text());
                    }
                }
            }
            calculateGRTotal(last_amount, new_amount);
            // calculateGRTotal('#dynamic-table tr.gradeX', GR_ROW_INDEX_ITEM_QTY, GR_ROW_INDEX_PRICE, GR_ROW_INDEX_AMOUNT);
        }
    });
}

// event change currency
$('#id_currency').change(function () {

    var currency_id = parseInt($(this).val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];
    $('#dynamic-table tr.gradeX').each(function () {
        currentRow = $(this).closest('tr').find('input');
        arrItems.push({
            item_id: currentRow[GR_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[GR_ROW_INDEX_CURRENCY_ID].value
        });
    });
    // changeCurrency(arrItems, currency_id, currency_name);
});

//event generate document number by order date
$('#id_order_date').change(function () {
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


function fixForm() {
    // fix the row index
    fix_table_row_indexes();

    var subtotal = 0;
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).find('input');
        var currentLabel = $(this).find('label');
        let rowIndex = $(this).attr('data-row_index');
        qty = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
        currentRow[GR_ROW_INDEX_ITEM_QTY].value = qty;

        if (currentRow[GR_ROW_INDEX_AMOUNT].value == '') {
            // let amount = float_format(currentLabel[GR_LABEL_INDEX_AMOUNT].textContent);
            let amount = float_format($('#id_formset_item-'+rowIndex+'-amount').text());
            currentRow[GR_ROW_INDEX_AMOUNT].value = amount;
            subtotal += amount;
        } else {
            let amount = float_format(currentRow[GR_ROW_INDEX_AMOUNT].value);
            currentRow[GR_ROW_INDEX_AMOUNT].value = amount;
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


$(document).ready(function () {

    $("#search_input").keypress(function (e) {
        var key = e.which;
        if (key == 13) {
            supplier_items();
        }
    });
    $('#btnOpenItemDialog').on('click', function () {
        var dataTable = $('#tblData').DataTable();
        dataTable.clear();
        $('#tblData_filter > label > input').val(' ');
        supplier_items();
        // $('#tblData_filter > label > input').val('');
    });
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

            var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
            var unitPrice = float_format(currentRow[GR_ROW_INDEX_PRICE].value);

            var refer_doc = '';
            var refer_line = '';
            if (currentSelect.length == 1 && $('#company_is_inventory').val() == 'True' || currentSelect.length == 0) {
                refer_doc = currentLabel[1].textContent.trim();
                refer_line = currentLabel[2].textContent.trim();
            } else {
                refer_doc = currentSelect[GR_SELECT_INDEX_REF_NUMBER].value;
                refer_line = currentSelect[GR_SELECT_INDEX_REFER_LINE].value;
            }

            if (quantity == 0 || unitPrice == 0) {
                is_valid = false;
                invalid_data_list.push({
                    ln: currentLabel[GR_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
                    refer_doc: refer_doc,
                    refer_line: refer_line,
                    quantity: currentRow[GR_ROW_INDEX_ITEM_QTY].value,
                    unitPrice: currentRow[GR_ROW_INDEX_PRICE].value,
                });
            }

            // allTableData.push({
            //     ln: currentLabel[GR_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
            //     refer_doc: refer_doc,
            //     refer_line: refer_line,
            //     quantity: currentRow[GR_ROW_INDEX_ITEM_QTY].value,
            //     unitPrice: currentRow[GR_ROW_INDEX_PRICE].value,
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
            //     e.preventDefault();
            //     show_invalid_modal(duplicate_data_list, [], disableShowDuplicate(), enableShowDuplicate(), th_object);
            // } else {
                fixForm();
                checkForm(this);
            // }
        }

        // var total = float_format($('#id_total').val());
        // if (total == 0) {
        //     $('#items_error').text('Total is ZERO. Please select valid quantity');
        //     $('#items_error').removeAttr('style');
        //     fnDisableButton();
        //     e.preventDefault();
        //     return false;
        // }

        // var is_valid = true;
        // var is_duplicate = false;
        // $('#dynamic-table tr.gradeX:visible').each(function () {
            //checking duplicate
            // let check_refer_number = $(selects[GR_SELECT_INDEX_REF_NUMBER]).val();
            // let check_refer_line = $(this).val();
            // $('#dynamic-table tr.gradeX').each(function(){
            //     let selects = $(this).closest('tr').find('select');
            //     let loop_row_index = parseInt($(this).closest('tr').find('label:first').text())-1;
            //     if(loop_row_index != rowIndex) {
            //         let selected_refer_number;
            //         let selected_refer_line;
            //         selects.each(function (selectIndex, selectValues) {
            //             if (selectIndex == GR_SELECT_INDEX_REF_NUMBER) {
            //                 selected_refer_number = $(this).val();
            //             }
            //             if (selectIndex == GR_SELECT_INDEX_REFER_LINE) {
            //                 selected_refer_line = $(this).val();
            //             }
            //         });
            //         if(selected_refer_number == check_refer_number && selected_refer_line == check_refer_line){
            //             let msg = 'Duplicate entry at row number '+(loop_row_index+1)+'<br/>Refer no: '+check_refer_number+'<br/>Refer ln: '+check_refer_line;
            //             pop_ok_dialog("Duplicate Row",
            //                 msg,
            //                 function(){
            //
            //                 }
            //             );
            //         }
            //     }
            // });

            // var currentRow = $(this).find('input');
            //
            // var quantity = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
            //
            // if (quantity == 0) {
            //     is_valid = false;
            // }
            //
            // // checking duplicate
            // let rowIndex = parseInt($(this).closest('tr').find('label:first').text())-1;
            // var currentRowSelect = $(this).find('select');
            // let check_refer_number = '';
            // let check_refer_line = '';
            // currentRowSelect.each(function (selectIndex, selectValues) {
            //     if (selectIndex == GR_SELECT_INDEX_REF_NUMBER) {
            //         check_refer_number = $(this).val();
            //     }
            //     if (selectIndex == GR_SELECT_INDEX_REFER_LINE) {
            //         check_refer_line = $(this).val();
            //     }
            // });

            // if can not get value from group down we will get form imput hidden
            // if (check_refer_number == '' || check_refer_line == '' ) {
            //     currentRow.each(function (selectIndex, selectValues) {
            //         if (selectIndex == GR_ROW_INDEX_REFER_NO) {
            //             check_refer_number = $(this).val();
            //         }
            //         if (selectIndex == GR_ROW_INDEX_REFER_LINE) {
            //             check_refer_line = $(this).val();
            //         }
            //     });
            // }

            // if (check_refer_number != '' && check_refer_line != '' ) {
            //     $('#dynamic-table tr.gradeX').each(function(){
            //         let selects = $(this).closest('tr').find('select');
            //         let inputs = $(this).closest('tr').find('input');
            //         let loop_row_index = parseInt($(this).closest('tr').find('label:first').text())-1;
            //         if(loop_row_index != rowIndex) {
            //             let selected_refer_number;
            //             let selected_refer_line;
            //             selects.each(function (selectIndex, selectValues) {
            //                 if (selectIndex == GR_SELECT_INDEX_REF_NUMBER) {
            //                     selected_refer_number = $(this).val();
            //                 }
            //                 if (selectIndex == GR_SELECT_INDEX_REFER_LINE) {
            //                     selected_refer_line = $(this).val();
            //                 }
            //             });
            //             if (selected_refer_number != '' || selected_refer_line != '' ) {
            //                 inputs.each(function (selectIndex, selectValues) {
            //                     if (selectIndex == GR_ROW_INDEX_REFER_NO) {
            //                         selected_refer_number = $(this).val();
            //                     }
            //                     if (selectIndex == GR_ROW_INDEX_REFER_LINE) {
            //                         selected_refer_line = $(this).val();
            //                     }
            //                 });
            //             }
            //             if(selected_refer_number == check_refer_number && selected_refer_line == check_refer_line){
            //                 let msg = 'Duplicate entry at row number '+(loop_row_index+1)+'<br/>Refer no: '+check_refer_number+'<br/>Refer ln: '+check_refer_line;
            //                 $('#items_error').html(msg);
            //                 $('#items_error').removeAttr('style');
            //                 fnDisableButton();
            //                 is_duplicate = true;
            //                 e.preventDefault();
            //                 return false;
            //             }
            //         }
            //     });
            // }




        // });
        // if (!is_valid) {
        //     $('#items_error').text('Please select valid quantity');
        //     $('#items_error').removeAttr('style');
        //     fnDisableButton();
        //     e.preventDefault();
        //     return false;
        // }
        // if (!is_duplicate) {
        //     $('#id_subtotal').val(float_format($('#id_subtotal').val()));
        //     $('#id_total').val(float_format($('#id_total').val()));
        //     $('#id_tax_amount').val(float_format($('#id_tax_amount').val()));
        //
        //     $('#dynamic-table tr.gradeX').each(function () {
        //         var currentRow = $(this).find('input');
        //         qty = float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value);
        //         currentRow[GR_ROW_INDEX_ITEM_QTY].value = qty;
        //     });
        // } else {
        //     e.preventDefault();
        //     return false;
        // }

    });
    $('#btnSend').on('click', function () {
        var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
        if (countRowVisible == 0) {
            pop_select_product();
        }
    });
    $('#btnSendForEdit').on('click', function () {
        var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
        if (countRowVisible == 0) {
            pop_select_product();
        }
    });
});


function supplier_items() {

    // var data = $('#search_input').val();
    var supplier_id = $('#hdSupplierId').val();
    var exclude_item_array = [];
    var exclude_item_list = {};
    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[GR_ROW_INDEX_ITEM_ID].value);
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
        "order": [[6, "asc"]],
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
                // "visible": false,
                "className": "hide_column"
            },
            {"data": "item_name", "sClass": "text-left"},
            {"data": "supplier_code", "sClass": "text-left"},
            {"data": "refer_number", "sClass": "text-left"},
            {"data": "refer_line", "sClass": "text-left"},
            {"data": "location_code", "sClass": "text-left"},
            {"data": "code", "sClass": "text-left"},
            {"data": "category", "sClass": "text-left"},
            {"data": "purchase_price", "sClass": "text-right"},
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
                "data": "minimun_order",
                "className": "hide_column"
            },
            {
                "data": "refer_id",
                "className": "hide_column"
            },
            {
                "data": "customer_po_no",
                "className": "hide_column"
            },
            {"data": "order_qty"},
            {"data": "receive_qty"},
            {
                "data": "outstanding_qty",
                "className": "hide_column"
            },
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

function WarnQtyExceded(max_qty, elm, msg) {
    pop_ok_dialog("Invalid Item Quantity",
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

$('#tax_currency').change(function(e){

    pop_ok_dialog("Invalid Operation",
        "Changing to this field is not allowed.",
        function(){
            $(this).val(tax_curr);
            $current_element = '#' + e.target.id;
            $($current_element).select();
    });

});

$('#id_document_number').change(function(e){
    var doc_no = $(this).val();
    var data = {'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),'doc_no': doc_no};
    $.ajax({
        url: '/orders/is_doc_no_exist/',
        type: 'POST',
        data: data,
        cache : false,
    })
    .done(function(data) {
        if (data){
            pop_ok_dialog("Invalid Document Number",
                "Document Number " + doc_no + " exists. Please use another number.",
                function(){
                    setTimeout(() => {
                        fnDisableButton();
                        $('#id_document_number').val("");
                        $('#id_document_number').select();
                    }, 500);
                    
            });

        } else {
            fnEnableButton();
        }
    })
    .fail(function(e){
        pop_ok_dialog("Exception",
            "Some errors happened. Please refresh and try again or contact administrator for support.",
            function(){
                fnDisableButton();
                $current_element = '#' + e.target.id;
                $($current_element).select();
        });
    })
});

function fnDisableButton() {
    $('#btnPrint').attr('disabled', true);
    $('#btnSave').attr('disabled', true);
    $('#btnRemove').attr('disabled', true);

}

function fnEnableButton() {
    $('#btnPrint').removeAttr('disabled');
    $('#btnSave').removeAttr('disabled');
    $('#btnRemove').removeAttr('disabled');
    $('#items_error').css("display", "none");
}

function getOutstandingQty(refer_doc,item_id,doc_item){
    var OutstandingQty = 0;
    var ItemQty = 0;
    for (var i in doc_item) {
        if ((doc_item[i]['refer_doc']==refer_doc) && (doc_item[i]['item_id']==item_id)){
            OutstandingQty += (doc_item[i]['ord_qty']-doc_item[i]['qty_rcv']);
            ItemQty += doc_item[i]['qty'];
        }
    }
    return {
        OutstandingQty : OutstandingQty,
        ItemQty : ItemQty
    };
}

function is_valid_date(p1){
    var pattern =/^([0-9]{1,2})\-([0-9]{1,2})\-([0-9]{4})$/; // expected format : DD-MM-YYYY
    return pattern.test(p1);
}

$('#copy_date_doc').keyup(function(event){
    adjust_input_date(this);
});

$('#copy_date_doc').on('change', function() {

    var date_from = get_date_from("#copy_date_doc");
    date_from = date_from.split('/').join('-');
    var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();
    if (!date_from_valid){

        $("#copy_date_doc").val(moment($("#id_document_date").val(),"YYYY-MM-DD").format("DD-MM-YYYY"));
    }else{

        var date_rate_1 = dateView(date_from);
        $("#id_document_date").val(date_rate_1);
        var id_cus = $('#id_supplier').val();
        var rate_type = 3;
        var curr_to = $('#id_currency').val();
        if (id_cus > 0){
            recort_rate_po(curr_to,date_rate_1,rate_type);
        }
    }

});

var refer_numbers = [];
function load_refer_numbers(){
    // var ExcludeList = setExcludeList(getAllItemQty());
    var ExcludeList = [];
    var id_cus = 0 ;
    if ( $('#id_supplier').val() > 0){
        id_cus =  $('#id_supplier').val()
    }
    $.ajax({
        type: "POST",
        url: "/orders/gr_select_po_json/"+id_cus+'/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'exclude_list': JSON.stringify(ExcludeList),
        },
        success: function(data){
            if (data.data.length > 0){
                refer_numbers = data.data
                }
            }
    });
}

function load_po_numbers(){
    // var ExcludeList = setExcludeList(getAllItemQty());
    var ExcludeList = [];
    var id_cus = 0 ;
    if ( $('#id_supplier').val() > 0){
        id_cus =  $('#id_supplier').val()
    }
    refer_numbers = [];
    $.ajax({
        type: "POST",
        url: "/orders/gr_select_po_json/"+id_cus+'/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'exclude_list': JSON.stringify(ExcludeList),
        },
        success: function(data){
            if (data.data.length > 0){
                refer_numbers = data.data
            }

            initiateRefNumber('#dynamic-table tr.gradeX:last');
            }
    });
}

// var last_po_number = '';
// var refer_line_selected = [];
// var remain_count = -1;

function tabAddRow(rowIndex, keyPress, copy_refer_number) {
    if (keyPress == 9){
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
            let refer_number = $('#id_select-' + (rowIndex) +'-ref_number').val();
            if (refer_number == undefined) {
                refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').text();
            } 
            if (refer_number == undefined || refer_number == '') {
                setTimeout(() => {
                    copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
                    if ( copy_refer_number != '') {
                        $('#id_select-' + (rowIndex) + '-ref_number').val(copy_refer_number).trigger('change');
                        $('#id_select-' + (rowIndex) + '-ref_number').select2('close');
                    }
                }, 300);
            } else {
                setTimeout(() => {
                    $('#id_select-' + rowIndex + '-ref_number').focus();
                    $('#id_select-' + rowIndex + '-ref_number').select2('open');
                }, 300);
            }
        }
    }
}

function highLightMandatory(rowCheck) {
    if ($('#id_select-' + rowCheck +'-ref_number').val() == '' || $('#id_select-' + rowCheck +'-ref_number').val() == undefined ) {
        $($('#select2-id_select-' + rowCheck +'-ref_number-container').parent('span')[0]).addClass('highlight-mandatory');
    } else {
        $($('#select2-id_select-' + rowCheck +'-ref_number-container').parent('span')[0]).removeClass('highlight-mandatory');
    }

    if ($('#id_select-' + rowCheck +'-refer_line').val() == '' || $('#id_select-' + rowCheck +'-refer_line').val() == undefined ) {
        $($('#select2-id_select-' + rowCheck +'-refer_line-container').parent('span')[0]).addClass('highlight-mandatory');
    } else {
        $($('#select2-id_select-' + rowCheck +'-refer_line-container').parent('span')[0]).removeClass('highlight-mandatory');
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
    if ($('#id_select-' + rowCheck +'-ref_number').val() == '') {
        idFirstInvalid = '#id_select-' + rowCheck +'-ref_number';
        return idFirstInvalid;
    }

    if ($('#id_select-' + rowCheck +'-refer_line').val() == '') {
        idFirstInvalid = '#id_select-' + rowCheck +'-refer_line';
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

var last_refer_line = "";

function initiateRefNumber($selector, $selected=null){

    $($selector).each(function () {
        let selects = $(this).closest('tr').find('select');
        let currentRow = $(this).closest('tr').find('input');
        let currentLabel = $(this).closest('tr').find('label');
        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));

        if($selected == null) {
            refreshCurrentRow(currentRow, currentLabel);
            handleQuantity();
        }

        selects.each(function (selectIndex, selectValues) {
            if ($('#company_is_inventory').val() == 'True' && selectIndex == GR_SELECT_INDEX_LOCATION) {

                locationSelect2($(this)[0].id, location_data);

                setTimeout(() => {
                    if($selected) {
                        $(this).val($selected[2]);
                    }
                }, 1000);
            }
            if (selectIndex == GR_SELECT_INDEX_LOCATION) {
                // $(this).select2();
                $(this).on("select2:close", function (event) {
                    // $(this).closest('tr').find('select:eq('+GR_SELECT_INDEX_REF_NUMBER+')').focus();
                    $(this).closest('tr').find('input:eq(7)').focus();
                });
            }
            if (selectIndex == GR_SELECT_INDEX_REF_NUMBER) {
                referNumberSelect2($(this)[0].id, refer_numbers, rfn_exclude_list);

                if (!$("#orderItemModal").is(':visible') && parseInt($('#id_formset_item-TOTAL_FORMS').val()) > 1) {
                    setTimeout(() => {
                        $(this).select2('open');
                    }, 300);
                }

                if($selected) {
                    $(this).val($selected[0]).trigger('change');
                    $(this).select2('close');
                }

                if($selected == null) {
                    $(this).on("change", function( event ){
                        refreshCurrentRow(currentRow, currentLabel);
                        ramaining_qty_list = update_remaining_qty(ramaining_qty_list, '', 0, parseInt($(this).closest('tr').attr('data-row_index')), true);

                        var hdSupplierId = $('#hdSupplierId').val();
                        let po_number = $(this).find('option:selected').data('code_data');
                        let refer_number = $(this).val();
                        let this_id = this.id;
                        let ref_line_id = 'id_select-' + (parseInt($(this).closest('tr').attr('data-row_index'))) + '-refer_line';
                        let found = false;
                        let line = $(this).closest('tr').find('label:first').text();
                        $(storeCopyRefNumberData).each(function (indx, value) {
                            if (value.line == line) {
                                if (refer_number != value.ref_number && value.ref_number != 'remove' && value.ref_number != '') {
                                    let idx = rfn_exclude_list.indexOf(value.ref_number);
                                    rfn_exclude_list.splice(idx, 1);
                                }
                                found = true;
                            }
                        });

                        if(po_number != '0' && po_number != undefined && po_number != null) {
                            $.ajax({
                                method: "POST",
                                url: '/orders/get_orderitems_by_po_no/',
                                dataType: 'JSON',
                                data: {
                                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                                    'po_number': po_number,
                                    'supplier_id': hdSupplierId,
                                    'exclude_item_list': []
                                },
                                success: function (json) {
                                    allVals.length = 0;
                                    ref_line_count = 0;
                                    $.each(json, function (i, item) {
                                        item_qty = item.outstanding_qty;
                                        // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', refer_number, item.refer_line, GR_ROW_INDEX_ITEM_QTY, GR_SELECT_INDEX_REF_NUMBER, GR_SELECT_INDEX_REFER_LINE, item_qty);
                                        ref_remain_quantity = get_remaining_qty(ramaining_qty_list, refer_number+'-'+item.refer_line, item_qty);
                                        if (ref_remain_quantity) {
                                            ref_line_count++;
                                            allVals.push({
                                                id: item.item_id,
                                                price: item.purchase_price,
                                                item_code: item.code,
                                                name: item.item_name,
                                                refer_number: item.refer_number,
                                                refer_line: item.refer_line,
                                                supplier_code: item.supplier_code,
                                                location_code: item.location_code,
                                                category: item.category,
                                                unit_price: item.purchase_price,
                                                currency: item.currency_code,
                                                location_id: item.location_id,
                                                currency_id: item.currency_id,
                                                uom: item.uom,
                                                supplier_id: item.supplier_id,
                                                minimun_order: item.minimun_order,
                                                ref_id: item.refer_id,
                                                customer_po_no: item.customer_po_no,
                                                quantity: item.quantity,
                                                receive_quantity: item.receive_quantity,
                                                outstanding_qty: item.outstanding_qty,
                                                show: true
                                            });
                                        } else {
                                            allVals.push({
                                                id: item.item_id,
                                                price: item.purchase_price,
                                                item_code: item.code,
                                                name: item.item_name,
                                                refer_number: item.refer_number,
                                                refer_line: item.refer_line,
                                                supplier_code: item.supplier_code,
                                                location_code: item.location_code,
                                                category: item.category,
                                                unit_price: item.purchase_price,
                                                currency: item.currency_code,
                                                location_id: item.location_id,
                                                currency_id: item.currency_id,
                                                uom: item.uom,
                                                supplier_id: item.supplier_id,
                                                minimun_order: item.minimun_order,
                                                ref_id: item.refer_id,
                                                customer_po_no: item.customer_po_no,
                                                quantity: item.quantity,
                                                receive_quantity: item.receive_quantity,
                                                outstanding_qty: item.outstanding_qty,
                                                show: false
                                            });
                                        }
                                    });

                                    if (!ref_line_count) {
                                        $('#' + this_id + ' option[value="'+ refer_number +'"]').remove();
                                        setTimeout(() => {
                                            $('#' + this_id).select2('open');
                                        }, 500);
                                        if (rfn_exclude_list.indexOf(refer_number) == -1) {
                                            rfn_exclude_list.push(refer_number);
                                        }
                                        filterAllReferNumber("GR", '#dynamic-table tr.gradeX', refer_number, GR_SELECT_INDEX_REF_NUMBER, -1);
                                    }

                                    referLineSelect2(ref_line_id, allVals, refer_number, 'GR');

                                    if (!$("#orderItemModal").is(':visible')) {
                                        setTimeout(function() {
                                            $(selects[GR_SELECT_INDEX_REF_NUMBER]).select2('close');
                                            $(selects[GR_SELECT_INDEX_REFER_LINE]).select2('open');
                                            if (allVals.length == 1) {
                                                $('#' + ref_line_id).val(allVals[0].refer_line).trigger('change');
                                                $(selects[GR_SELECT_INDEX_REFER_LINE]).select2('close');
                                            } else if ($('#' + ref_line_id + ' option').length == 2) {
                                                $('#' + ref_line_id).val($('#' + ref_line_id + ' option:eq(1)').val()).trigger('change');
                                                $(selects[GR_SELECT_INDEX_REFER_LINE]).select2('close');
                                            }
                                        }, 300);
                                    }
                                }
                            });
                        } else {
                            // refreshCurrentRow(currentRow, currentLabel);
                            referLineSelect2(ref_line_id, [], '', 'GR');
                        }
                        let rowIndex = $(this).closest('tr').find('label:first').text();
                        storeCopyRefNumberData = saveCopyRefNumberDO(rowIndex, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
                        // storeCopyRefNumberData = changeIndexData(rowIndex, 'minus', storeCopyRefNumberData);
                    });
                }

                $(this).on("select2:close", function (event) {
                    $(this).closest('tr').find('select:eq('+GR_SELECT_INDEX_REFER_LINE+')').focus();
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    highLightMandatory(rowCheck);
                });

                $(this).prop('disable', false);
                $(this).select2('enable');
            }
            if (selectIndex == GR_SELECT_INDEX_REFER_LINE) {
                referLineSelect2($(this)[0].id, [], '', 'GR');

                if($selected == null) {
                    $(this).on("change", function( event ){
                        var sum = 0;
                        let refer_line = $(this).find('option:selected').data('code_data');
                        let currentLabel = $(this).closest('tr').find('label');
                        let currentRow = $(this).closest('tr').find('input');
                        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
                        // if (refer_line_selected.indexOf(refer_line.toString()) > -1) {
                        //   refer_line_selected.splice(refer_line_selected.indexOf(refer_line.toString()), 1);
                        // }
                        let check_refer_number = $(selects[GR_SELECT_INDEX_REF_NUMBER]).val();
                        let check_refer_line = $(this).val();
                        // remainQuantity = getRemainQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, allVals);
                        // if (remainQuantity == undefined) {
                        //     if (0 < getTotalMaxInputQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, (rowIndex+1))) {
                        //         remainQuantity = getTotalMaxInputQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, (rowIndex+1));
                        //     }
                        // }
                        let idx = $(this).closest('tr').find('label:first').text();
                        storeCopyRefNumberData = saveCopyRefNumberDO(idx, check_refer_number, check_refer_line, 'add', storeCopyRefNumberData, allVals);
                        ramaining_qty_list = update_remaining_qty(ramaining_qty_list, '', 0, parseInt($(this).closest('tr').attr('data-row_index')), true);
                        for(var i=0; i<allVals.length; i++) {
                            if(allVals[i].refer_line == refer_line) {
                                //add value to Input
                                currentRow[GR_ROW_INDEX_LINE_NUMBER].value = currentLabel[GR_LABEL_INDEX_LINE_NUMBER].textContent;
                                currentRow[GR_ROW_INDEX_ITEM_CODE].value = allVals[i].item_code;
                                currentRow[GR_ROW_INDEX_ITEM_NAME].value = allVals[i].name;
                                currentRow[GR_ROW_INDEX_ITEM_ID].value = allVals[i].id;
                                currentRow[GR_ROW_INDEX_CUSTOMER_PO].value = allVals[i].customer_po_no;
                                if ($('#company_is_inventory').val() == 'True'){
                                    if (allVals[i].location_id) {
                                        location_choice = '#' + selects[GR_SELECT_INDEX_LOCATION].id;
                                        if ($(location_choice).data('select2')) {
                                            $(location_choice).select2('destroy');
                                        }
                                        $(location_choice).empty();
                                        var options = '';
                                        options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                                        $(location_choice).append(options);
                                        $(location_choice).select2();
                                        $(location_choice).val(allVals[i].location_id).trigger('change');
                                    } else {
                                        $(location_choice).val(1).trigger('change');
                                    }
                                }
                                // remainQuantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, check_refer_line, GR_ROW_INDEX_ITEM_QTY, GR_SELECT_INDEX_REF_NUMBER, GR_SELECT_INDEX_REFER_LINE, allVals[i].outstanding_qty, rowIndex);
                                remainQuantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+check_refer_line, allVals[i].outstanding_qty, rowIndex);
                                if (remainQuantity == undefined) {
                                    currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(allVals[i].outstanding_qty);
                                    remainQuantity = allVals[i].outstanding_qty;
                                } else if (remainQuantity > 0) {
                                    currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(remainQuantity);
                                    // storeCopyRefNumberData = updateQuantityCopyRefNumberDO((rowIndex + 1), check_refer_number, check_refer_line, storeCopyRefNumberData, remainQuantity)
                                } else {
                                    currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(remainQuantity);
                                }
                                // currentRow[GR_ROW_INDEX_ITEM_QTY].value = comma_format(remainQuantity);
                                currentRow[GR_ROW_INDEX_PRICE].value = float_format(allVals[i].unit_price).toFixed(6);
                                currentRow[GR_ROW_INDEX_CURRENCY_CODE].value = allVals[i].currency;
                                currentRow[GR_ROW_INDEX_CURRENCY_ID].value = allVals[i].currency_id;
                                currentRow[GR_ROW_INDEX_CATEGORY].value = allVals[i].category;
                                currentRow[GR_ROW_INDEX_SUPPLIER_CODE].value = allVals[i].supplier_code;
                                currentRow[GR_ROW_INDEX_SUPPLIER_ID].value = allVals[i].supplier_id;
                                currentRow[GR_ROW_INDEX_REFER_NO].value = allVals[i].refer_number;
                                currentRow[GR_ROW_INDEX_REFER_LINE].value = allVals[i].refer_line;
                                currentRow[GR_ROW_INDEX_UOM].value = allVals[i].uom;
                                currentRow[GR_ROW_INDEX_REF_ID].value = allVals[i].ref_id;
                                currentRow[GR_ROW_INDEX_MIN_ORDER].value = float_format(allVals[i].minimun_order).toFixed(2);
                                currentRow[GR_ROW_INDEX_OUTSTANDING_QTY].value = float_format(allVals[i].outstanding_qty).toFixed(2);
                                currentRow[GR_ROW_INDEX_ORDER_QTY].value = float_format(allVals[i].quantity).toFixed(2); // Order Quantity
                                currentRow[GR_ROW_INDEX_RECEIVE_QTY].value = float_format(allVals[i].receive_quantity).toFixed(2); // Receive Quantity


                                currentLabel[GR_LABEL_INDEX_ITEM_CODE].textContent = currentRow[GR_ROW_INDEX_ITEM_CODE].value; // Item Code
                                currentLabel[GR_LABEL_INDEX_ITEM_NAME].textContent = currentRow[GR_ROW_INDEX_ITEM_NAME].value; // Item Name
                                // currentLabel[GR_LABEL_INDEX_PRICE].textContent = currentRow[GR_ROW_INDEX_PRICE].value; // Price
                                currentLabel[GR_LABEL_INDEX_CURRENCY_CODE].textContent = currentRow[GR_ROW_INDEX_CURRENCY_CODE].value; // Currency Code
                                currentLabel[GR_LABEL_INDEX_CATEGORY].textContent = currentRow[GR_ROW_INDEX_CATEGORY].value; // Part Group
                                currentLabel[GR_LABEL_INDEX_SUPPLIER_CODE].textContent = currentRow[GR_ROW_INDEX_SUPPLIER_CODE].value; // Supplier Code

                                currentLabel[GR_LABEL_INDEX_CUSTOMER_PO_NO].textContent = currentRow[GR_ROW_INDEX_CUSTOMER_PO].value; // Refer Line
                                currentLabel[GR_LABEL_INDEX_ORDER_QTY].textContent = comma_format(allVals[i].quantity); // Order Quantity
                                currentLabel[GR_LABEL_INDEX_RECEIVE_QTY].textContent = comma_format(allVals[i].receive_quantity); // Receive Quantity
                                currentLabel[GR_LABEL_INDEX_UOM].textContent = currentRow[GR_ROW_INDEX_UOM].value; // UOM

                                if (float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value) > 0 &&
                                    !$("#orderItemModal").is(':visible')) {
                                    $('#' + currentRow[GR_ROW_INDEX_ITEM_QTY].id).trigger('change');
                                }

                            }
                        }
                        doEssentials(currentRow);
                    });
                }

                $(this).on("select2:open", function (event) {
                    last_refer_line = $(this).val();
                 });

                $(this).on("select2:close", function (event) {
                    if ($('#company_is_inventory').val() == 'True') {
                        $(selects[GR_SELECT_INDEX_LOCATION]).focus();
                        // $(selects[GR_SELECT_INDEX_LOCATION]).select2('open');
                    } else {
                        $('#id_formset_item-' + rowIndex + '-quantity').focus();
                    }

                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    highLightMandatory(rowCheck);
                 });

                $(this).prop('disable', false);
                $(this).select2('enable');
            }
        });
    });
}

function controlPrevNextBtn() {
        // disable or enable pre button
        // if (dyn_tbl_sel_row_id == 0) {
        //     $('#btnOrderItemPrev').attr('disabled', true);
        // } else {
        //     $('#btnOrderItemPrev').attr('disabled', false);
        // }
        if ((editing_row.prev()).length) {
            $('#btnOrderItemPrev').attr('disabled', false);
        } else {
            $('#btnOrderItemPrev').attr('disabled', true);
        }

        // disable or enable next button
        // if (dyn_tbl_sel_row_id == (parseInt($('#id_formset_item-TOTAL_FORMS').val()) - 1)) {
        //     $('#btnOrderItemNext').attr('disabled', true);
        // } else {
        //     $('#btnOrderItemNext').attr('disabled', false);
        // }
        if (editing_row.next().hasClass('gradeX')) {
            $('#btnOrderItemNext').attr('disabled', false);
        } else {
            $('#btnOrderItemNext').attr('disabled', true);
        }
    }

function is_change() {
    var flag_change = false;

    if (line_object['ref_num'] != $('#modal_ref_number_select').val()
        && $('#modal_ref_number_select').val() != undefined) {
        flag_change = true;
    }

    if (line_object['ref_line'] != $('#modal_refer_line_select').val()
        && $('#modal_refer_line_select').val() != undefined) {
        flag_change = true;
    }

    if (line_object['qty'] != $('#modal_quantity').val()) {
        flag_change = true;
    }
    if (line_object['price'] != $('#modal_price').val()) {
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
        setTimeout(() => {
            $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
            setTimeout(() => {
                var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
                editing_row = $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal_2(selectedRowId);
            }, 1000);
        }, 1500);
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
    resetReferNumber();
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
    $('#modal_ref_number select').select2('close');
    $('#modal_refer_line select').select2('close');
    if (is_change()) {
        next = false;
        prev = false;
        $('#comfirmSaveOrderModal').modal('show');
    } else {
        var ok = is_modal_valid();
        if (!ok) {
            // reset line
            var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            var selectedRowId = parseInt(editing_row.find('label:first').text()) - 1;
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
        resetReferNumber();
        $('#orderItemModal').modal('hide');
    }
}

function resetReferNumber() {
    if ($("#orderItemModal").is(':visible')) {
        let refer_number = $('#modal_ref_number select').val();
        let idx = rfn_exclude_list.indexOf(refer_number);
        rfn_exclude_list.splice(idx, 1);
    }
}

function resetLine() {
    resetReferNumber();
    var selectedRowId = parseInt(editing_row.find('label:first').text()) - 1;
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
                        $('#dynamic-table tr.gradeX:nth-child(' + (rowCount - 1) + ')').find('.appendrow').trigger('click');
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


function refreshCurrentRow(currentRow, currentLabel) {
    let last_amount = float_format($('#'+currentLabel[GR_LABEL_INDEX_AMOUNT].id).text());
    let new_amount = 0;
    calculateGRTotal(last_amount, new_amount);

    currentRow[GR_ROW_INDEX_ITEM_QTY].value = '0.00';
    currentRow[GR_ROW_INDEX_PRICE].value = '0.000000';
    // $('#'+currentRow[GR_ROW_INDEX_ITEM_QTY].id).trigger('change');
    currentLabel[GR_LABEL_INDEX_CUSTOMER_PO_NO].textContent = '';
    currentLabel[GR_LABEL_INDEX_ITEM_CODE].textContent = '';
    currentLabel[GR_LABEL_INDEX_ITEM_NAME].textContent = '';
    // currentLabel[GR_LABEL_INDEX_PRICE].textContent = '0.000000';
    currentLabel[GR_LABEL_INDEX_CURRENCY_CODE].textContent = '';
    currentLabel[GR_LABEL_INDEX_CATEGORY].textContent = '';
    currentLabel[GR_LABEL_INDEX_SUPPLIER_CODE].textContent = '';
    currentLabel[GR_LABEL_INDEX_ORDER_QTY].textContent = '';
    currentLabel[GR_LABEL_INDEX_RECEIVE_QTY].textContent = '';
    currentLabel[GR_LABEL_INDEX_UOM].textContent = '';
    currentLabel[GR_LABEL_INDEX_AMOUNT].textContent = '0.00';

    if ($('#company_is_inventory').val() == 'True'){
        let indx = $(currentRow[0]).parent().parent().attr('data-row_index');
        location_choice = '#id_formset_item-' + indx + '-location';
        $(location_choice).val('').trigger('change');
    }
}



function load_supp() {
    var date_rate = $("#id_document_date").val();
    var id_sup = $('#id_supplier').val();
    $('#id_document_number').select();
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
                $('#hdSupplierId').val(data.data[0].id)
                $('#id_currency').val(data.data[0].currency_id).trigger('change');
                $('#name_currency').val(data.data[0].currency_name);
                $('#customer_payment_term').text(data.data[0].payment_term+' Days');
                $('#customer_payment_mode').text(data.data[0].payment_code);
                $('#customer_credit_limit').text(data.data[0].credit_limit);
                $('#gr_total').text("Total (" + data.data[0].currency_symbol + ') : ');
                $('#gr_subtotal').text("Subtotal (" + data.data[0].currency_symbol + ') : ');
                $('#gr_tax').text("Tax (" + data.data[0].currency_symbol + ') : ');
                $('#supplier_name').text(data.data[0].supplier_name);
                $('#supplier_address').text(data.data[0].address);
                $('#supplier_email').text(data.data[0].email);
                $('#id_distribution_code').val(data.data[0].distribution_id).trigger('change');
                recort_rate_po(data.data[0].currency_id,date_rate,3);
                $('#id_tax').val(data.data[0].tax_id).trigger('change');
                $('#footer_currency1').text(data.data[0].currency_symbol);
                $('#footer_currency2').text(data.data[0].currency_symbol);
                $('#footer_currency3').text(data.data[0].currency_symbol);
                $('#id_document_number').select();
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
                $('#id_tax_exchange_rate').val('');
                $('#id_supllier_exchange_rate').val('');
                $('#id_exchange_rate_value').val('');
            } else {
                fnEnableButton();
                $('#exchange_rate_fk_id').val(data[0].id);
                $('#id_exchange_rate').val(data[0].rate);
                $('#id_exchange_rate_date').val(data[0].exchange_date);
                $('#id_tax_exchange_rate').val(data[0].rate);
                $('#id_supllier_exchange_rate').val(data[0].rate);
                $('#id_exchange_rate_value').val(data[0].rate);
            }
        }
    });
}

function setExcludeList(item_info){
    ExcludeList = [];
    if (item_info){
        for (i in item_info){
            ExcludeList.push(item_info[i]['refer_doc']);
        }
    }
    return ExcludeList;
}

function getAllItemQty(){
    var AllItemQty = [];
    $('#dynamic-table tr.gradeX').each(function (rowIndex) {
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');
        if (currentRow[GR_ROW_INDEX_ITEM_ID].value){
            AllItemQty.push({
                id: $('#id_formset_item-' + rowIndex + '-id').val(),
                ln: currentRow[GR_ROW_INDEX_LINE_NUMBER].value,
                refer_line: currentRow[GR_ROW_INDEX_REFER_LINE].value,
                refer_doc: currentRow[GR_ROW_INDEX_REFER_NO].value,
                item_id: currentRow[GR_ROW_INDEX_ITEM_ID].value,
                ord_qty: float_format(currentRow[GR_ROW_INDEX_ORDER_QTY].value),
                qty_rcv: float_format(currentRow[GR_ROW_INDEX_RECEIVE_QTY].value),
                qty: float_format(currentRow[GR_ROW_INDEX_ITEM_QTY].value),
                order_id: $(currentLabel[1]).data('code_data')
            });
        }
    });
    return AllItemQty;
}
