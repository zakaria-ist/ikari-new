/**
 * Created by tho.pham on 5/26/2016.
 */

var initial_item_qty = [];

var date_0 = $('#id_document_date').val();
var allVals = [];
var country_list = [];
var emptyRow = '';
var editing_row = null;
var append_index = 0;
var location_data = [];
var order_is_decimal = 1;
var decimal_place = 2;
let storeCopyRefNumberData = [];
var remainQuantity = 0;
var rfn_exclude_list = [];
var ref_line_count = 0;
var ref_remain_quantity = 0;
var ramaining_qty_list = [];

var invalid_data_list = [];
var invalid_message_list = [];
var is_disable_show_duplicate = false;
var part_current_row = null;
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
                        <button type="button" class="editrow btn btn-white fa fa-square-o" name="editrow" value="Edit" data-toggle="modal" data-target="#doInvoiceItemModal" style="margin-left:0.4rem;"></button>
                        <button type="button" class="removerow btn btn-white fa fa-minus" name="removerow" value="Remove" style="margin-left:0.4rem;"></button>
                    </div>
                </td>
                <td>
                <label id="id_formset_item-0-line_number" class="control-label-item" name="formset_item-0-line_number">1</label>
                    <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-line_id" name="formset_item-0-line_id" style="display: none" type="text">
                </td>
                <td>
                    <div class="col-md-12" style="width: 200px; padding: 0px !important">
                        <div class="col-md-9" style="width: 170px; padding: 0px !important">
                            <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="width: 170px;" type="text">
                        </div>
                        <div class="col-md-3" style="width: 10px; padding: 0px !important">
                            <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-refer" name="search-refer" data-toggle="modal"></button>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="col-md-12" style="width: 80px; padding: 0px !important">
                        <div class="col-md-9" style="width: 50px; padding: 0px !important">
                            <input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="width: 50px;" type="text">
                        </div>
                        <div class="col-md-3" style="width: 10px; padding: 0px !important">
                            <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-refer" name="search-refer" data-toggle="modal"></button>
                        </div>
                    </div>
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="width: 150px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="display: none" type="text">
                </td>
                <td>
                    <select id="id_formset_item-0-location" class="form-control select_location" name="formset_item-0-location" style="width: 110px; text-align: center;">
                        </select>
                </td>
                <td><label id="id_formset_item-0-code" class="control-label-item" name="formset_item-0-code" style="width: 150px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                </td>
                <td style="width: 10%; display: none;">
                    <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name"></label>
                    <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" style="display: none" type="text">
                </td>
                <td style=""><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity_do" name="formset_item-0-quantity_do" style="text-align: right; width: 140px;" type="text"></td>
                <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency"></label>
                    <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none;" type="text">
                    <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_price" id="id_formset_item-0-price" required="required" name="formset_item-0-price" style="text-align: right; width: 140px;" type="text"></td>
                <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" readonly="readonly" step="0.000001" style="text-align: right; width: 80px;" type="number"></td>
                <td style="text-align: right;">
                    <label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label>
                    <input class="form-control-item text-right" id="id_formset_item-0-amount" name="formset_item-0-amount" readonly="readonly" step="0.000001" style="text-align: right; width: 100px; display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category"></label>
                    <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                </td>
                <td><label id="id_formset_item-0-order_quantity" class="control-label-item" name="formset_item-0-order_quantity"></label>
                    <input class="form-control-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" step="1" min=0 style="display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-delivery_quantity" class="control-label-item" name="formset_item-0-delivery_quantity"></label>
                    <input class="form-control-item" id="id_formset_item-0-delivery_quantity" name="formset_item-0-delivery_quantity" step="0.1" style="display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom"></label>
                    <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                </td>
                <td>
                    <div class="input-group">
                        <select id="id_select_country_code-0-country_code"
                            class="form-control select_country_code"
                            name="select_country_code-0-country_code"><option></option>
                        </select>
                        <input class="form-control input-sm" id="id_formset_item-0-origin_country_code" name="formset_item-0-origin_country_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-origin_country_id" name="formset_item-0-origin_country_id" style="display: none ; text-align: left;" type="text">
                    </div>
                </td>
                <td><input class="form-control-item" id="id_formset_item-0-carton_no" name="formset_item-0-carton_no" style="text-align: left; width: 100px;" type="text"></td>
                <td><input class="form-control-item" id="id_formset_item-0-carton_total" name="formset_item-0-carton_total" style="text-align: right; width: 100px;" type="number"></td>
                <td><input class="form-control-item" id="id_formset_item-0-pallet_no" name="formset_item-0-pallet_no" style="text-align: left; width: 100px;" type="text"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-net_weight" name="formset_item-0-net_weight" step="any" style="text-align: right; width: 100px;" type="number"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-m3_number" name="formset_item-0-m3_number" step="any" style="text-align: right; width: 100px;" type="number"></td>
                <td><label id="id_formset_item-0-supplier" class="control-label-item" name="formset_item-0-supplier"></label>
                    <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                </td>
                <td style="display: none;"><input class="form-control-item" id="id_formset_item-0-location_item_quantity" name="formset_item-0-location_item_quantity" step="0.01" style="text-align: right; width: 100px;" type="number"></td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-gross_weight" name="formset_item-0-gross_weight" step="any" style="text-align: right; width: 100px;" type="number"></td>
                </tr>`;
} else {
    emptyRow = `<tr class="gradeX" data-row_index="0">
                <td>
                    <div class="btn-group" style="width:160px">
                        <button type="button" tabindex="-1" class="prependrow btn btn-white fa fa-level-up" name="prependrow" value="Prepend" ></button>
                        <button type="button" tabindex="-1" class="appendrow btn btn-white fa fa-level-down" name="appendrow" value="Append" style="margin-left:0.4rem;"></button>
                        <button type="button" class="editrow btn btn-white fa fa-square-o" name="editrow" value="Edit" data-toggle="modal" data-target="#doInvoiceItemModal" style="margin-left:0.4rem;"></button>
                        <button type="button" tabindex="-1" class="removerow btn btn-white fa fa-minus" name="removerow" value="Remove" style="margin-left:0.4rem;"></button>
                    </div>
                </td>
                <td>
                <label id="id_formset_item-0-line_number" class="control-label-item" name="formset_item-0-line_number">1</label>
                    <input class="form-control-item" id="id_formset_item-0-line_number" name="formset_item-0-line_number" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-line_id" name="formset_item-0-line_id" style="display: none" type="text">
                </td>
                <td>
                    <div class="col-md-12" style="width: 200px; padding: 0px !important">
                        <div class="col-md-9" style="width: 170px; padding: 0px !important">
                            <input class="form-control-item" id="id_formset_item-0-ref_number" name="formset_item-0-ref_number" style="width: 170px;" type="text">
                        </div>
                        <div class="col-md-3" style="width: 10px; padding: 0px !important">
                            <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-refer" name="search-refer" data-toggle="modal"></button>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="col-md-12" style="width: 80px; padding: 0px !important">
                        <div class="col-md-9" style="width: 50px; padding: 0px !important">
                            <input class="form-control-item" id="id_formset_item-0-refer_line" name="formset_item-0-refer_line" style="width: 50px;" type="text">
                        </div>
                        <div class="col-md-3" style="width: 10px; padding: 0px !important">
                            <button tabindex="-1" type="button" style="" class="btn btn-white fa fa-search search-refer" name="search-refer" data-toggle="modal"></button>
                        </div>
                    </div>
                </td>
                <td><label class="control-label-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="width: 150px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-customer_po_no" name="formset_item-0-customer_po_no" style="display: none" type="text">
                </td>
                <td><label id="id_formset_item-0-code" class="control-label-item" name="formset_item-0-code" style="width: 150px; text-align: center;"></label>
                    <input class="form-control-item" id="id_formset_item-0-code" name="formset_item-0-code" style="display: none" type="text">
                </td>
                <td style="width: 10%; display: none;">
                    <label class="form-label-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name"></label>
                    <input class="form-control-item" id="id_formset_item-0-item_name" name="formset_item-0-item_name" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-item_id" name="formset_item-0-item_id" style="display: none" type="text">
                </td>
                <td style=""><input class="form-control-item numeric_qty" id="id_formset_item-0-quantity_do" name="formset_item-0-quantity_do" style="text-align: right; width: 140px;" type="text"></td>
                <td><label id="id_formset_item-0-original_currency" class="control-label-item lblCurrency" name="formset_item-0-original_currency"></label>
                    <input class="form-control-item" id="id_formset_item-0-original_currency" name="formset_item-0-original_currency" style="display: none;" type="text">
                    <input class="form-control-item" id="id_formset_item-0-currency_id" name="formset_item-0-currency_id" style="display: none" type="text">
                </td>
                <td><input class="form-control-item numeric_price" id="id_formset_item-0-price" required="required" name="formset_item-0-price" style="text-align: right; width: 140px;" type="text"></td>
                <td style="display: none;"><input class="form-control-item text-right" id="id_formset_item-0-exchange_rate" name="formset_item-0-exchange_rate" readonly="readonly" step="0.000001" style="text-align: right; width: 80px;" type="number"></td>
                <td style="text-align: right;">
                    <label id="id_formset_item-0-amount" class="control-label-item" name="formset_item-0-amount" style="width: 130px; text-align: right;"></label>
                    <input class="form-control-item text-right" id="id_formset_item-0-amount" name="formset_item-0-amount" readonly="readonly" step="0.000001" min=0 style="text-align: right; width: 100px; display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-category" class="control-label-item" name="formset_item-0-category"></label>
                    <input class="form-control-item" id="id_formset_item-0-category" name="formset_item-0-category" style="display: none" type="text">
                </td>
                <td><label id="id_formset_item-0-order_quantity" class="control-label-item" name="formset_item-0-order_quantity"></label>
                    <input class="form-control-item" id="id_formset_item-0-order_quantity" name="formset_item-0-order_quantity" step="1" min=0 style="display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-delivery_quantity" class="control-label-item" name="formset_item-0-delivery_quantity"></label>
                    <input class="form-control-item" id="id_formset_item-0-delivery_quantity" name="formset_item-0-delivery_quantity" step="0.1" style="display: none;" type="number">
                </td>
                <td><label id="id_formset_item-0-uom" class="control-label-item" name="formset_item-0-uom"></label>
                    <input class="form-control-item" id="id_formset_item-0-uom" name="formset_item-0-uom" style="display: none" type="text">
                </td>
                <td>
                    <div class="input-group">
                        <select id="id_select_country_code-0-country_code"
                            class="form-control select_country_code"
                            name="select_country_code-0-country_code"><option></option>
                        </select>
                        <input class="form-control input-sm" id="id_formset_item-0-origin_country_code" name="formset_item-0-origin_country_code" style="display: none" type="text">
                        <input class="form-control-item" id="id_formset_item-0-origin_country_id" name="formset_item-0-origin_country_id" style="display: none ; text-align: left;" type="text">
                    </div>
                </td>
                <td><input class="form-control-item" id="id_formset_item-0-carton_no" name="formset_item-0-carton_no" style="text-align: left; width: 100px;" type="text"></td>
                <td><input class="form-control-item" id="id_formset_item-0-carton_total" name="formset_item-0-carton_total" style="text-align: right; width: 100px;" type="number"></td>
                <td><input class="form-control-item" id="id_formset_item-0-pallet_no" name="formset_item-0-pallet_no" style="text-align: left; width: 100px;" type="text"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-net_weight" name="formset_item-0-net_weight" step="any" style="text-align: right; width: 100px;" type="number"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-m3_number" name="formset_item-0-m3_number" step="any" style="text-align: right; width: 100px;" type="number"></td>
                <td><label id="id_formset_item-0-supplier" class="control-label-item" name="formset_item-0-supplier"></label>
                    <input class="form-control-item" id="id_formset_item-0-supplier_code" name="formset_item-0-supplier_code" style="display: none" type="text">
                    <input class="form-control-item" id="id_formset_item-0-supplier_code_id" name="formset_item-0-supplier_code_id" style="display: none" type="text">
                </td>
                <td style="display: none;"><input class="form-control-item" id="id_formset_item-0-location_item_quantity" name="formset_item-0-location_item_quantity" step="0.01" style="text-align: right; width: 100px;" type="number"></td>
                <td style="display: none"><input class="form-control-item" id="id_formset_item-0-reference_id" name="formset_item-0-reference_id" type="text"></td>
                <td><input class="form-control-item text-right" id="id_formset_item-0-gross_weight" name="formset_item-0-gross_weight" step="any" style="text-align: right; width: 100px;" type="number"></td>
                </tr>`;
}


var DO_ROW_INDEX_LINE_NUMBER = 0;
var DO_ROW_INDEX_LINE_ID = DO_ROW_INDEX_LINE_NUMBER + 1;
var DO_ROW_INDEX_REFER_NO = DO_ROW_INDEX_LINE_ID + 1;
var DO_ROW_INDEX_REFER_LINE = DO_ROW_INDEX_REFER_NO + 1;
var DO_ROW_INDEX_CUSTOMER_PO = DO_ROW_INDEX_REFER_LINE + 1;
var DO_ROW_INDEX_ITEM_CODE = DO_ROW_INDEX_CUSTOMER_PO + 1;
var DO_ROW_INDEX_ITEM_NAME = DO_ROW_INDEX_ITEM_CODE + 1;
var DO_ROW_INDEX_ITEM_ID = DO_ROW_INDEX_ITEM_NAME + 1;
var DO_ROW_INDEX_ITEM_QTY = DO_ROW_INDEX_ITEM_ID + 1;
var DO_ROW_INDEX_CURRENCY_CODE = DO_ROW_INDEX_ITEM_QTY + 1;
var DO_ROW_INDEX_CURRENCY_ID = DO_ROW_INDEX_CURRENCY_CODE + 1;
var DO_ROW_INDEX_PRICE = DO_ROW_INDEX_CURRENCY_ID + 1;
var DO_ROW_INDEX_EXCHANGE_RATE = DO_ROW_INDEX_PRICE + 1;
var DO_ROW_INDEX_AMOUNT = DO_ROW_INDEX_EXCHANGE_RATE + 1;
var DO_ROW_INDEX_CATEGORY = DO_ROW_INDEX_AMOUNT + 1;
var DO_ROW_INDEX_ORDER_QTY = DO_ROW_INDEX_CATEGORY + 1;
var DO_ROW_INDEX_DELIVERY_QTY = DO_ROW_INDEX_ORDER_QTY + 1;
var DO_ROW_INDEX_UOM = DO_ROW_INDEX_DELIVERY_QTY + 1;
var DO_ROW_INDEX_COUNTRY_ORG_CD = DO_ROW_INDEX_UOM + 1;
var DO_ROW_INDEX_COUNTRY_ORG_ID = DO_ROW_INDEX_COUNTRY_ORG_CD + 1;
var DO_ROW_INDEX_CARTON_NO = DO_ROW_INDEX_COUNTRY_ORG_ID + 1;
var DO_ROW_INDEX_CARTON_TOTAL = DO_ROW_INDEX_CARTON_NO + 1;
var DO_ROW_INDEX_PALLET_NO = DO_ROW_INDEX_CARTON_TOTAL + 1;
var DO_ROW_INDEX_NET_WEIGHT = DO_ROW_INDEX_PALLET_NO + 1;
var DO_ROW_INDEX_M3_NUMBER = DO_ROW_INDEX_NET_WEIGHT + 1;
var DO_ROW_INDEX_SUPPLIER_CODE = DO_ROW_INDEX_M3_NUMBER + 1;
var DO_ROW_INDEX_SUPPLIER_ID = DO_ROW_INDEX_SUPPLIER_CODE + 1;
var DO_ROW_INDEX_LOC_ITEM_QTY = DO_ROW_INDEX_SUPPLIER_ID + 1;
var DO_ROW_INDEX_REFERENCE_ID = DO_ROW_INDEX_LOC_ITEM_QTY + 1;
var DO_ROW_INDEX_GROSS_WEIGHT = DO_ROW_INDEX_REFERENCE_ID + 1;


var DO_LABEL_INDEX_LINE_NUMBER = 0;
var DO_LABEL_INDEX_CUSTOMER_PO = DO_LABEL_INDEX_LINE_NUMBER + 1;
var DO_LABEL_INDEX_ITEM_CODE = DO_LABEL_INDEX_CUSTOMER_PO + 1;
var DO_LABEL_INDEX_ITEM_NAME = DO_LABEL_INDEX_ITEM_CODE + 1;
var DO_LABEL_INDEX_CURRENCY_CODE = DO_LABEL_INDEX_ITEM_NAME + 1;
// var DO_LABEL_INDEX_PRICE = DO_LABEL_INDEX_CURRENCY_CODE + 1;
var DO_LABEL_INDEX_AMOUNT = DO_LABEL_INDEX_CURRENCY_CODE + 1;
var DO_LABEL_INDEX_CATEGORY = DO_LABEL_INDEX_AMOUNT + 1;
var DO_LABEL_INDEX_ORDER_QTY = DO_LABEL_INDEX_CATEGORY + 1;
var DO_LABEL_INDEX_DELIVERY_QTY = DO_LABEL_INDEX_ORDER_QTY + 1;
var DO_LABEL_INDEX_UOM = DO_LABEL_INDEX_DELIVERY_QTY + 1;
var DO_LABEL_INDEX_SUPPLIER_CODE = DO_LABEL_INDEX_UOM + 1;


var DO_SELECT_INDEX_LOCATION;
var DO_SELECT_INDEX_COUNTRY_CODE;
if($('#company_is_inventory').val() == 'True') {
    DO_SELECT_INDEX_LOCATION = 0;
    DO_SELECT_INDEX_COUNTRY_CODE = DO_SELECT_INDEX_LOCATION + 1;
} else {
    DO_SELECT_INDEX_COUNTRY_CODE = 0;
}

/* DO Column Index */

var DO_COL_BUTTONS = 0;
var DO_COL_LINE_NUMBER = DO_COL_BUTTONS + 1;

if($('#company_is_inventory').val() == 'True') {
    var DO_COL_LOC_CODE = DO_COL_LINE_NUMBER + 1;
    var DO_COL_REF_NUMBER = DO_COL_LOC_CODE + 1;
} else {
    var DO_COL_REF_NUMBER = DO_COL_LINE_NUMBER + 1;
}
var DO_COL_REFER_LINE = DO_COL_REF_NUMBER + 1;
var DO_COL_CUSTOMER_PO = DO_COL_REFER_LINE + 1;
var DO_COL_PART_NO = DO_COL_CUSTOMER_PO + 1;
var DO_COL_ITEM_NAME = DO_COL_PART_NO + 1;
var DO_COL_QTY_DO = DO_COL_ITEM_NAME + 1;
var DO_COL_CURRENCY = DO_COL_QTY_DO + 1;
var DO_COL_PRICE = DO_COL_CURRENCY + 1;
var DO_COL_EXCHNG_RATE = DO_COL_PRICE + 1;
var DO_COL_AMOUNT = DO_COL_EXCHNG_RATE + 1;
var DO_COL_PART_GROUP = DO_COL_AMOUNT + 1;
var DO_COL_ORDER_QTY = DO_COL_PART_GROUP + 1;
var DO_COL_RECEV_QTY = DO_COL_ORDER_QTY + 1;
var DO_COL_UOM = DO_COL_RECEV_QTY + 1;
var DO_COL_COUNTRY = DO_COL_UOM + 1;
var DO_COL_CARTON_NO = DO_COL_COUNTRY + 1;
var DO_COL_TOTAL_CARTON = DO_COL_CARTON_NO + 1;
var DO_COL_PALLET = DO_COL_TOTAL_CARTON + 1;
var DO_COL_NET_WEIGHT = DO_COL_PALLET + 1;
var DO_COL_M3 = DO_COL_NET_WEIGHT + 1;
var DO_COL_SUPPLIER_CODE = DO_COL_M3 + 1;
var DO_COL_GROSS_WEIGHT = DO_COL_SUPPLIER_CODE + 1;


$(document).ready(function () {

    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });

    // $('button').on('keypress', function(event){
    //     var keycode = (event.keyCode ? event.keyCode : event.which);
    //     if(keycode == '13'){
    //         $(this).trigger('click');
    //     }
    // });

    $(document).on('change', '#id_customer_code', function (e) {
      $('#copy_date_doc').focus();
    });

    $(document).on('change', '#modal_ref_number', function (e) {
      $('#modal_refer_line').focus();
    });

    $(document).on('change', '#modal_refer_line', function (e) {

        if ($('#modal_refer_line').val() == '' || $('#modal_refer_line').val() == null) {
            return false;
        }

        if ($("#modal_loc_item_code_select").is(':visible')) {
            $('#modal_loc_item_code_select').focus();
            $('#modal_loc_item_code_select').select2('open');
        } else if ($("#modal_country_code select").is(':visible')) {
            $('#modal_country_code select').focus();
            $('#modal_country_code select').select2('open');
        } else {
            $('#modal_quantity_do').focus();
        }
    });

    $(document).on('select2:close', '#modal_loc_item_code select', function (e) {
        if ($("#modal_country_code select").is(':visible')) {
            $('#modal_country_code select').focus();
            $('#modal_country_code select').select2('open');
        } else {
            $('#modal_quantity_do').focus();
        }
    });

    $(document).on('select2:close', '#modal_country_code select', function (e) {
        $('#modal_quantity_do').focus();
    });

    $(document).on('focusout', '#id_cost_center', function (e) {
      $('.editrow').focus();
    });

    if($('#company_is_inventory').val() == 'True') {
        get_location_list();
    }

    initiateCountryCode();
    handleQuantity();
    $('#btnSave').attr('disabled', true);
    $('input').bind('input propertychange', function() {
        $('#btnSave').removeAttr('disabled');
    });
    $('select').change(function() {
        $('#btnSave').removeAttr('disabled');
    });
    $('textarea').bind('input propertychange', function() {
        $('#btnSave').removeAttr('disabled');
    });

    $('#id_document_date_fake').hide();

    $('#id_transaction_code').select2();
    $('.location_select select').select2();

    $('#id_cost_center').select2({
        placeholder: "Select Cost Center",
    });
    // Alternate Consignee
    $('#id_delivery').select2({
        allowClear: true,
        placeholder: "Select Alternate Consignee",
    });
    $('#id_delivery').on("select2:open", function( event ){
        prefill_select2(event);
    });

    // Unit of Measurement
    $('#hdr_uom').select2({
        allowClear: true,
        placeholder: "Select UOM",
    });
    $('#hdr_uom').on("select2:open", function( event ){
        prefill_select2(event);
    });

    // Tax
    $('#id_tax').select2({
        allowClear: true,
        placeholder: "Select Tax Code",
    });
    $('#id_tax').on("select2:open", function( event ){
        prefill_select2(event);
    });

    if (!$('#id_customer').val()){
        $('#btnOpenItemDialog').attr('disabled', 'disabled');
        $('#load_so_by_cust').attr('disabled', 'disabled');
    }

    var date_1 = dateView($('#id_document_date').val());
    $('#copy_date_doc').val(date_1);
    $('#id_document_date').addClass('hide');
    // $('form input').on('keypress', function (e) {
    //     return e.which !== 13;
    // });

    $('#id_distribution_code').select2({
        allowClear: true,
        placeholder: "Select Distribution Code",
    });
    $('#id_distribution_code').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#id_ship_from_code').select2({
        allowClear: true,
        placeholder: "Select Ship From",
    });
    $('#id_ship_from_code').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#id_ship_to_code').select2({
        allowClear: true,
        placeholder: "Select Ship To",
    });
    $('#id_ship_to_code').on("select2:open", function( event ){
        prefill_select2(event);
    });

    $('#payment_mode').select2({
        allowClear: true,
        placeholder: "Select Payment",
    });
    $('#payment_mode').on("select2:open", function( event ){
        prefill_select2(event);
    });


    $('#id_customer').on('change', function() {
        $('#btnOpenItemDialog').removeAttr('disabled');
        $('#id_subtotal').val(0);
        $('#id_total').val(0);
        $('#id_tax_amount').val(0);
        $('#dynamic-table tbody').find('tr').remove();
        $(emptyRow).insertBefore('#id_formset_item-TOTAL_FORMS');
        $('#id_formset_item-TOTAL_FORMS').val('1');
        disableAutoComplete();
        load_cuss();
        load_part_numbers();
        rfn_exclude_list = [];
        append_index = 1;
    });

    let customer = $('#hdCustomerId').val();
    $('#id_exchange_rate_value').val($('#id_exchange_rate').val());

    if (customer != null ) {
        $('#dynamic-table tbody').find('tr.gradeX:last').remove();
        let total = parseInt($('#id_formset_item-TOTAL_FORMS').val());
        total--;
        $('#id_formset_item-TOTAL_FORMS').val(total);
        if (total == 0) {
            setTimeout(() => {
                $('#id_customer_code').select();
            }, 300);
        } else {
            load_refer_numbers();
            append_index = $('#dynamic-table').find('tr.gradeX').length;
        }
    }

    
    $('#id_customer_code').focus();

    $('#id_payment_term').addClass('text-center');

    $('#invalidInputModal').on('shown.bs.modal', function () {
        if ($("#doInvoiceItemModal").is(':visible')) {
            // $('#modal_ref_number select').select2('close');
            // $('#modal_refer_line select').select2('close');
            $('#modal_country_code select').select2('close');
        } else {
            try {
                // $('#modal_ref_number select').select2('close');
                // $('#modal_refer_line select').select2('close');
                $('#modal_country_code select').select2('close');
            } catch(e) {
                
            }
        }
    });

    $('#comfirmSaveDeleteOrderModal').on('shown.bs.modal', function () {
        if ($("#comfirmSaveDeleteOrderModal").is(':visible')) {
            // $('#modal_ref_number select').select2('close');
            // $('#modal_refer_line select').select2('close');
            $('#modal_country_code select').select2('close');
        } else {
            try {
                // $('#modal_ref_number select').select2('close');
                // $('#modal_refer_line select').select2('close');
                $('#modal_country_code select').select2('close');
            } catch(e) {
                
            }
        }
    });

    let allItemQty = getAllItemQty();
    setTimeout(() => {
        get_refer_order_items(allItemQty);
    }, 2000);
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
        url: '/orders/get_order_item_by_so_no/',
        dataType: 'JSON',
        async: false,
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'so_number': all_sos,
            'customer_id': $('#hdCustomerId').val(),
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

$('#id_tax').on("select2:close", function() {
    $('#id_distribution_code').select2("open");
});

$('#id_distribution_code').on("select2:close", function() {
    $('#payment_mode').select2("open");
});

$('#payment_mode').on("select2:close", function() {
    $('#id_payment_term').focus();
});


$('#id_ship_from_code').on("select2:close", function() {
    $('#id_ship_to_code').select2("open");
});

$('#id_ship_from_code').on("select2:open", function() {
    value  = $(this).val();
    $(this).empty();
    $(this).append("<option></option>");
    for (var i in country_list) {
        $(this).append("<option data-code_data='"+JSON.stringify(country_list[i])+"' value='"+country_list[i].id+"'>"+country_list[i].code+"</option>");
    }
    $(this).val(value).trigger("change");
});

$('#id_ship_to_code').on("select2:open", function() {
    value  = $(this).val();
    $(this).empty();
    $(this).append("<option></option>");
    for (var i in country_list) {
        $(this).append("<option data-code_data='"+JSON.stringify(country_list[i])+"' value='"+country_list[i].id+"'>"+country_list[i].code+"</option>");
    }
    $(this).val(value).trigger("change");
});

$('#id_ship_to_code').on("select2:close", function() {
    $('#hdr_delivery').focus();
});


$('#hdr_uom').on("select2:close", function() {
    $('#id_cost_center').focus();
});

$('#id_delivery').on("select2:close", function() {
    $('#id_remark').focus();
});

$('#load_so_by_cust').on("select2:close", function() {
    $('#load_so_by_cust').focus();
});


$(document).ready(function () {
    var initial_item = getAllItemQty();
    for (i=0; i<initial_item.length; i++){
        initial_item_qty.push(initial_item[i]);
    }
    $('#initial_item_qty_data').val(JSON.stringify(initial_item_qty));
    var odr = $('#dynamic-table tr.gradeX:visible').length;
    for (var i = 1; i < odr; i++) {
        var j = i-1;
        var net_weight_raw = $('#id_formset_item-'+j+'-net_weight').val();
        if(net_weight_raw!= "NaN"){
            var net_weight_enhanced = float_format(net_weight_raw).toFixed(2);
            $('#id_formset_item-'+j+'-net_weight').val(net_weight_enhanced);
        }
    }
    for (var k = 1; k < odr; k++) {
        var l = k-1;
        var gross_weight_raw = $('#id_formset_item-'+l+'-gross_weight').val();
        if(gross_weight_raw!= "NaN"){
            var gross_weight_enhanced = float_format(gross_weight_raw).toFixed(2);
            $('#id_formset_item-'+l+'-gross_weight').val(gross_weight_enhanced);
        }
    }
    var copy_id = $('#copy_id').text();
    var selector = $('#dynamic-table tr.gradeX');
    var customer = $('#hdCustomerId').val();
    if ((customer != null && copy_id == '') || (customer != null && copy_id == '0')) {
        var count_row = 0;
        selector.each(function () {
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            count_row += 1;
            currentRow[DO_ROW_INDEX_LINE_NUMBER].value = count_row;
            currentLabel[DO_LABEL_INDEX_LINE_NUMBER].textContent = currentRow[DO_ROW_INDEX_LINE_NUMBER].value;
        });
        fnEnableButton();
    } else {
        // validation quantity of items
        $('#btnOpenItemDialog').css('display', 'none');
        var items_name_list = [];
        selector.each(function () {
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            var quantity_do = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
            var quantity_delivery = float_format(currentLabel[DO_LABEL_INDEX_DELIVERY_QTY].textContent);
            if (quantity_do < 0) {
                $('#minimum_order_error').removeAttr('style');
                $('#minimum_order_error').text('The quantity of product must be greater than 0');
                $(this).closest('tr').attr('style', 'background-color: red !important');
                currentRow[DO_ROW_INDEX_AMOUNT].value = 0;
                fnDisableButton();
            } else if (quantity_do == 0) {
                items_name_list.push(currentRow[DO_ROW_INDEX_ITEM_NAME].value);
                $(this).closest('tr').attr('style', 'background-color: aqua !important');
                $('#' + currentRow[DO_ROW_INDEX_ITEM_QTY].id).attr('disabled', true);
                currentRow[DO_ROW_INDEX_AMOUNT].value = 0;
                fnDisableButton();
            }
        });
        var uniqueNames = [];
        $.each(items_name_list, function (i, el) {
            if ($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
        });
        if (uniqueNames.length > 0) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The products ' + uniqueNames + ' were delivered.');
        }
    }
});


//Add Extra Label Value formset
$(document).ready(function () {
    checkDisplay();

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
});


//Load tax rate
$(document).ready(function () {
    $('#id_tax').change(function () {
        var taxid = parseInt($(this).val());
        if (isNaN(taxid)) {
            $('#id_tax_amount').val(0);
            $('#id_total').val(comma_format(
                (float_format($('#id_tax_amount').val()) -
                float_format($('#id_discount').val()) +
                float_format($('#id_subtotal').val())), decimal_place));
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
                    $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
                    $('#hdTaxRate').val(float_format(json).toFixed(2));
                    var total = float_format($('#id_subtotal').val()) + float_format(tax_amount) - float_format($('#id_discount').val());
                    $('#id_total').val(comma_format(total, decimal_place));
                }
            });
        }
    });
});

//Load and edit inline Customer information
$(document).ready(function () {
    var hdCustomerId = $('#hdCustomerId').val();
    fillCustomerInfo(hdCustomerId);

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
                fillCustomerInfo(json['id']);
                $('#id_tax').find('option').removeAttr("selected");
                $('#id_tax').find('option').removeAttr("disabled");
                $('#id_tax').find('option[value="' + json['tax_id'] + '"]').attr("selected", "selected");
                $('#id_tax').val(json['tax_id']).trigger('change');
                
                $('#customer_currency_id').val(json['currency_id']);
                // delivery info
                if (json['consignee'] == '' || json['consignee'] == null) {
                    $('#id_name').val(json['name']);
                } else {
                    $('#id_name').val(json['consignee']);
                }
                if (json['consignee_addr'] == '' || json['consignee_addr'] == null) {
                    $('#id_address').val(json['address']);
                } else {
                    $('#id_address').val(json['consignee_addr']);
                }
                $('#id_attention').val(json['consignee_contact']);
                $('#id_phone').val(json['consignee_phone']);
            }
        })
    };
    // $("#form_customer_code").keypress(function (e) {
    //     if (e.which == 13) {
    //         e.preventDefault();
    //         callback();
    //     }
    // });
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
                $('#myCustomerListModal .call-checkbox').off('click').on('click', function() {
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

    $('#btnCustomerSelect').on('click', function () { //realy ??? and i dont think select option have 'click' event
        var customer_select_id = $("input[name='choices']:checked").attr('id');
        var customer_select_code = $("input[name='choices']:checked").attr('code');
        $('#hdCustomerId').val(customer_select_id);
        $('#id_customer').val(customer_select_id).trigger('change');
        $('#id_customer_code').val(customer_select_code);
        var nRow = $("input[name='choices']:checked").parents('tr')[0];
        var jqInputs = $('td', nRow);
        $("#form_customer_code").val(jqInputs[0].innerText);
        $(this).attr('data-dismiss', 'modal');
        callback();
    });
});

$(document).on('click', '.search-refer', function () {
    part_current_row = $(this).closest('tr').find('input');
    if (refer_numbers.length) {
        $('#refer-table').DataTable().destroy();
        $('#refer-table').dataTable({
            "order": [[0, "desc"]],
            "iDisplayLength": 10,
            "bLengthChange": false,
            "data": refer_numbers,
            "columns": [
                {"data": "refer_number", "sClass": "text-left"},
                {"data": "refer_line", "sClass": "text-left"},
                {
                    "orderable": false,
                    "data": null,
                    "sClass": "hide_column",
                    "render": function (data, type, full, meta) {
                        return '<input type="radio" name="refer-choices" refer_number="'+ full.refer_number +'" refer_line="'+ full.refer_line +'" ref_id="' +
                            full.ref_id + '" class="call-checkbox" value="' + full.ref_id + '">';
                    }
                },
                {"data": "ref_id", "sClass": "text-left hide_column"},
            ],
        });
        $('#referListModal').modal('show');
    } else {
        pop_ok_dialog("Warning!",
            "Refer numbers are not loaded yet. wait some time & try again.",
            function () { }
        );
    }
});

$('#refer-table').on( 'draw.dt', function () {
    selectTableRow('#refer-table', 2);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

$('#btnReferSelect').on('click', function () {
    var refer_id = $("input[name='refer-choices']:checked").attr('ref_id');
    var refer_number = $("input[name='refer-choices']:checked").attr('refer_number');
    var refer_line = $("input[name='refer-choices']:checked").attr('refer_line');
    if (refer_id) {
        if ($("#doInvoiceItemModal").is(':visible')) {
            $('#modal_ref_number').attr('code_data', refer_id);
            $('#modal_ref_number').val(refer_number).trigger('change');
            setTimeout(() => {
                $('#modal_refer_line').val(refer_line).trigger('change');
                $('#modal_customer_po_no').focus();
            }, 600);
        } else {
            part_current_row[DO_ROW_INDEX_REFER_NO].value = refer_number;
            part_current_row[DO_ROW_INDEX_REFER_LINE].value = refer_line;
            part_current_row[DO_ROW_INDEX_REFERENCE_ID].value = refer_id;
            $('#'+part_current_row[DO_ROW_INDEX_REFER_NO].id).trigger('change');
            setTimeout(() => {
                $('#'+part_current_row[DO_ROW_INDEX_REFER_LINE].id).trigger('change');
            }, 600);
        }
        $('#referListModal').modal('hide');
    } else {
        pop_ok_dialog("Warning!",
            "Select an item first",
            function () { }
        );
    }
});

function fillCustomerInfo(hdCustomerId) {
    $.fn.editable.defaults.mode = 'inline';

    //make status editable
    $('#customer_name').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer name',
    });

    $('#cust_info1').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer information 1',
    });
    $('#cust_info2').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer information 2',
    });
    $('#cust_info3').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer information 3',
    });
    $('#cust_info4').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer information 4',
    });
    $('#cust_info5').editable({
        type: 'text',
        pk: hdCustomerId,
        title: 'Enter customer information 5',
    });
};

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
        if($('#id_formset_item-' + (curRowIndex) + '-refer_line').val() == null) {
            row_currency = ''
        }

        $selected_row.push({
            'row':newRowIndex,
            'ref_number': float_format($('#id_formset_item-'+ (curRowIndex) +'-ref_number').val()),
            'qty': $('#id_formset_item-'+ (curRowIndex) +'-quantity_do').val(),
            'line': $('#id_formset_item-'+ (curRowIndex) +'-line_number').text(),
            'po_no': $('#id_formset_item-'+ (curRowIndex) +'-customer_po_no').text(),
            'code': $('#id_formset_item-'+ (curRowIndex) +'-code').text(),
            'currency': row_currency,
            'price': float_format($('#id_formset_item-'+ (curRowIndex) +'-price').val()).toFixed(6),
            'exch_rate': $('#id_formset_item-'+ (curRowIndex) +'-exchange_rate').val(),
            'amount': $('#id_formset_item-'+ (curRowIndex) +'-amount').text(),
            'category': $('#id_formset_item-'+ (curRowIndex) +'-category').text(),
            'order_qty': $('#id_formset_item-'+ (curRowIndex) +'-order_quantity').text(),
            'delivery_qty': $('#id_formset_item-'+ (curRowIndex) +'-delivery_quantity').text(),
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
            $('#id_formset_item-'+ ($selected_row[i].row) +'-delivery_quantity').val($selected_row[i].delivery_qty);
            $('#id_formset_item-'+ ($selected_row[i].row) +'-delivery_quantity').text($selected_row[i].delivery_qty);
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
            $('#id_formset_item-'+ ($selected_row[i].row) +'-quantity_do').val($selected_row[i].qty);
        }
        $('#loading').hide();
    }

    function closeAllSelectOnTable() {
        // try{
        //     $('select[id^=id_select-][id$=-ref_number]').select2('close');
        // } catch (e){
        //     console.log(e.message);
        // }
        // try{
        //     $('select[id^=id_select-][id$=-refer_line]').select2('close');
        // } catch (e){
        //     console.log(e.message);
        // }
        try{
            $('select[id^=id_select_country_code-][id$=-country_code]').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    function removeRow(tthis) {
        closeAllSelectOnTable();
        // $selected_row = [];
        let rowIndex = parseInt($(tthis).closest('tr').attr('data-row_index'));
        last_amount = float_format($('#id_formset_item-'+(rowIndex)+'-amount').text());

        let refer_number = $('#id_formset_item-' + rowIndex +'-ref_number').val();
        let refer_line = $('#id_formset_item-' + rowIndex +'-refer_line').val();
        // if (refer_number == undefined) {
        //     refer_number = $('#id_formset_item-' + rowIndex +'-ref_number').text();
        // }
        // if (refer_line == undefined) {
        //     refer_line = $('#id_formset_item-' + rowIndex +'-refer_line').text();
        // }

        if (refer_number != '' && refer_number != undefined) {
            let idx = $(tthis).closest('tr').find('label:first').text();
            storeCopyRefNumberData = saveCopyRefNumberDO(idx, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
            storeCopyRefNumberData = changeIndexData(idx, 'minus', storeCopyRefNumberData);

            // if (rfn_exclude_list.indexOf(refer_number) != -1) {
            //     let indx = rfn_exclude_list.indexOf(refer_number);
            //     rfn_exclude_list.splice(indx, 1);
            //     filterAllReferNumber("DO", '#dynamic-table tr.gradeX', refer_number, DO_SELECT_INDEX_REF_NUMBER, -1, refer_numbers);
            // }
        }
        // if (refer_line != '' && refer_line != undefined) {
        //     filterAllReferNumber("DO", '#dynamic-table tr.gradeX', refer_number, DO_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, refer_line);
        // }
        // if (refer_number != '' && refer_line != '' && refer_line != undefined) {
        //     last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', refer_number, DO_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, refer_line, refer_line, "DO");
        // }

        currentRow = $(tthis).closest('tr').find('input');
        item_id = currentRow[DO_ROW_INDEX_ITEM_ID].value;
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
            // let rows = $('#dynamic-table').find('tr.gradeX');
            $('#dynamic-table tr.gradeX').each(function () {
                let currentRow = $(this).closest('tr').find('input');
                let currentLine = $(this).closest('tr').find('label');
                currentLine[DO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber + 1);
                currentRow[DO_ROW_INDEX_LINE_NUMBER].value = (rowNumber + 1);
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
                calculateDOTotal(last_amount, 0);
                // calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);
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
                        let rowIndex = $(tthis).closest('tr').attr('data-row_index');
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
        if (rowComplete()) {
            closeAllSelectOnTable();
            $selected_row = [];
            let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
            let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));

            storeCopyRefNumberData = changeIndexData(rowIndex.toString(), 'plus', storeCopyRefNumberData);
            let copy_refer_number = $('#id_formset_item-' + (temp_rowIndex) +'-ref_number').val();
            // if (copy_refer_number == undefined) {
            //     copy_refer_number = $('#id_formset_item-' + (temp_rowIndex) +'-ref_number').text();
            // }

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
                currentLine[DO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
                currentRow[DO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
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
            initiateRefNumber(newRow);
            // setTimeout(() => {
            //     copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
            //     if ( copy_refer_number != '') {
            //         $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
            //         $('#id_select-' + (rowNumber) + '-ref_number').select2('close');
            //     }
            //     // bindingData();
            // }, 500);
        }
    });

    $(document).on('click', "[class^=prependrow]", function (event) {
        if (rowComplete()) {
            closeAllSelectOnTable();
            // $selected_row = [];
            let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
            let temp_rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let prev_rowIndex = parseInt($(this).closest('tr').prev().attr('data-row_index'));

            storeCopyRefNumberData = changeIndexData((rowIndex - 1).toString(), 'plus', storeCopyRefNumberData);

            let copy_refer_number = $('#id_formset_item-' + (prev_rowIndex) +'-ref_number').val();
            // if (copy_refer_number == undefined) {
            //     copy_refer_number = $('#id_formset_item-' + (prev_rowIndex) +'-ref_number').text();
            // }

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
                currentLine[DO_LABEL_INDEX_LINE_NUMBER].textContent = (rowNumber+1);
                currentRow[DO_ROW_INDEX_LINE_NUMBER].value = (rowNumber+1);
                rowNumber++;
            });

            //initialize select2 of new row
            // let rows =  $('#dynamic-table').find('tr.gradeX');
            rowNumber = append_index;
            change_new_row_attr(rowIndex, rowNumber);
            append_index++;
            newRow = $('#dynamic-table tr.gradeX:nth-child('+(rowIndex)+')').closest('tr');

            initiateRefNumber(newRow);
            // setTimeout(() => {
            //     copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
            //     if ( copy_refer_number != '') {
            //         $('#id_select-' + (rowNumber) + '-ref_number').val(copy_refer_number).trigger('change');
            //         $('#id_select-' + (rowIndex) + '-ref_number').select2('close');
            //     }
            //     // bindingData();
            // }, 500);
        }
    });

    $('select[id^=id_select_country_code-][id$=-country_code]').on("select2:close", function () {
        let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        $('#id_formset_item-'+ (rowIndex) +'-carton_no').focus();
    });

    var next = false;
    var prev = false;
    var line_object = {
        'ref_num': '',
        'ref_line': '',
        'qty': '',
        'price': '',
        'current_code': '',
        'carton_no': '',
        'carton_total': '',
        'pallet_no': '',
        'net_weight': '',
        'gross_weight': '',
        'm3': '',
    }
    var dyn_tbl_sel_row_id = 0;
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
            $('#doInvoiceItemModal').modal('hide');
        }
    }

    function closeAllSelect2OnModal() {
        // try{
        //     $('#modal_ref_number select').select2('close');
        // } catch (e){
        //     console.log(e.message);
        // }
        // try{
        //     $('#modal_refer_line select').select2('close');
        // } catch (e){
        //     console.log(e.message);
        // }
        try{
            $('#modal_loc_item_code select').select2('close');
        } catch (e){
            console.log(e.message);
        }
        try{
            $('#modal_country_code select').select2('close');
        } catch (e){
            console.log(e.message);
        }
    }

    $(document).on('click', "[class^=editrow]", function (event) {
        editing_row = $(this).closest('tr');
        selectedRowId = $(this).closest('tr').attr('data-row_index');
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
        next = false;
        prev = true;
        closeAllSelect2OnModal();
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
        next = true;
        prev = false;
        action_button = 'next';
        closeAllSelect2OnModal();
        if (is_change()) {
            $('#comfirmSaveOrderModal').modal('show');
        } else {
            editing_row = editing_row.next();
            selectedRowId = parseInt(editing_row.attr('data-row_index'));
            loadOrderItemModal(selectedRowId);
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
                        loadOrderItemModal(selectedRowId);
                        $('#loading').hide();
                    }, 300);
                    $('#loading').show();
                }, 300);
            } else {
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal(selectedRowId);
                }, 500);
            }
        } else {
             $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=remove_line]", function (event) {
        removeLine();
    });

    $(document).on('click', "[id^=save_line]", function (event) {
        // $('#doInvoiceItemModal').modal('toggle');
    });

    $(document).on('click', "[id^=save_new_line]", function (event) {
        selectedRowId = dyn_tbl_sel_row_id;
        var ok = is_modal_valid();
        if (ok) {
            saveOrderItemModal(selectedRowId);
            setTimeout(() => {
                editing_row.find('.appendrow').trigger('click');
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal(selectedRowId);
                    $('#loading').hide();
                }, 300);
                $('#loading').show();
            }, 300);
        } else {
            $('#invalidInputModal').modal('show');
        }
    });

    $(document).on('click', "[id^=discard_line]", function (event) {
        closeAllSelect2OnModal();
        var ok = $.checkOrderRowValidity(dyn_tbl_sel_row_id);
        if (ok) {
            setTimeout(() => {
                editing_row.find('.appendrow').trigger('click');
                setTimeout(() => {
                    editing_row = editing_row.next();
                    selectedRowId = parseInt(editing_row.attr('data-row_index'));
                    loadOrderItemModal(selectedRowId);
                    $('#loading').hide();
                }, 500);
                $('#loading').show();
            }, 500);
        } else {
            loadOrderItemModal(dyn_tbl_sel_row_id)
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

        row = editing_row;

        valid = ($(row).length != 0);

        if (!valid) {
            return false;
        }

        $inputs = $(row).find('input');
        $selects = $(row).find('select');

        // Check each field is empty
        if ($inputs[DO_ROW_INDEX_LINE_NUMBER].value === '') {
            console.log('Error, line number empty');
            valid = false;
        }
        else if ($inputs[DO_ROW_INDEX_ITEM_CODE].value === '') {
            console.log('Error, item code empty');
            valid = false;
        }
        else if ($inputs[DO_ROW_INDEX_ITEM_NAME].value === '') {
            console.log('Error, item name empty');
            valid = false;
        }
        else if ($inputs[DO_ROW_INDEX_ITEM_ID].value === '') {
            console.log('Error, item id empty');
            valid = false;
        }
        else if ($inputs[DO_ROW_INDEX_CUSTOMER_PO].value === '') {
            console.log('Error, customer po empty');
            valid = false;
        } else if ($inputs[DO_ROW_INDEX_ITEM_QTY].value === '' || float_format($inputs[DO_ROW_INDEX_ITEM_QTY].value) == 0) {
            console.log('Error, quantity empty');
            valid = false;
        } else if ($inputs[DO_ROW_INDEX_PRICE].value === '' || float_format($inputs[DO_ROW_INDEX_PRICE].value) == 0) {
            console.log('Error, price empty');
            valid = false;
        }

        return valid;
    }

    $('#modal_quantity_do').click(function () {
        $(this).select();
    });
    $('#modal_price').click(function () {
        $(this).select();
    });

    $('#modal_net_weight').click(function () {
        $(this).select();
    });

    $('#modal_gross_weight').click(function () {
        $(this).select();
    });

    $('#modal_pallet_no').click(function () {
        $(this).select();
    });

    $('#modal_carton_no').click(function () {
        $(this).select();
    });

    $('#modal_carton_total').click(function () {
        $(this).select();
    });

    $('#modal_m3_number').click(function () {
        $(this).select();
    });

    $('#modal_loc_item_code').bind('keydown', function (event) {
        if (event.which == 9) {
            $('#modal_quantity_do').select();
            return false;
        }
    });

    function clear_modal() {
        $('#modal_supplier').val('');
        $('#modal_customer_po_no').val('');
        $('#modal_original_currency').val('');
        $('#modal_uom').val('');
        $('#modal_category').val('');
        $('#modal_part_item_code').val('');
        $('#modal_quantity_do').val('');
        $('#modal_carton_no').val('');
        $('#modal_carton_total').val('');
        $('#modal_pallet_no').val('');
        $('#modal_net_weight').val('');
        $('#modal_gross_weight').val('');
        $('#modal_m3_number').val('');
        $('#modal_price').val('');
        $('#modal_amount').val('');
        $('#modal_order_quantity').val('');
        $('#modal_delivery_quantity').val('');
    }

    function bindOrderModalEvent() {
        $('#modal_ref_number').on("change", function() {
            var hdCustomerId = $('#hdCustomerId').val();
            let doc_date = $('#id_document_date').val();
            let so_number = null;
            let check_refer_number = $('#modal_ref_number').val();
            // let found = false;
            let line = editing_row.find('label:first').text();
            // $(storeCopyRefNumberData).each(function (indx, value) {
            //     if (value.line == line) {
            //         if (check_refer_number != value.ref_number && value.ref_number != 'remove' && value.ref_number != '') {
            //             let idx = rfn_exclude_list.indexOf(value.ref_number);
            //             rfn_exclude_list.splice(idx, 1);
            //         }
            //         found = true;
            //     }
            // })
            let found = false;
            refer_numbers.map(refers => {
                if ($(this).val() == refers.refer_number) {
                    found = true;
                    so_number = refers.ref_id;
                }
            })
            if (!found) {
                pop_ok_dialog("Warning!",
                    "Refer number is not found",
                    function () { }
                );
                $(this).val('');
                clear_modal();
                return;
            }
            if (so_number !== '' && so_number !== undefined) {
                $.ajax({
                    method: "POST",
                    url: '/orders/get_orderitems_by_so_no/',
                    dataType: 'JSON',
                    data: {
                        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                        'so_number': so_number,
                        'customer_id': hdCustomerId,
                        'doc_date': doc_date,
                        'exclude_item_list': []
                    },
                    success: function (json) {
                        allVals.length = 0;
                        ref_line_count = 0;
                        $.each(json, function (i, item) {
                            let item_qty = 0;
                            let outstdg_qty = float_format(item.quantity) - float_format(item.delivery_quantity);
                            let location_qty = float_format(item.location_item_quantity);
                            if ($('#company_is_inventory').val() == 'True' && item.location_id){
                                item_qty = (outstdg_qty > location_qty) ? location_qty : outstdg_qty;
                            } else {
                                item_qty = outstdg_qty;
                            }
                            // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, item.refer_line, DO_ROW_INDEX_ITEM_QTY, DO_SELECT_INDEX_REF_NUMBER, DO_SELECT_INDEX_REFER_LINE, item_qty);
                            ref_remain_quantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+item.refer_line, item_qty);
                            if (ref_remain_quantity) {
                                ref_line_count++;
                                allVals.push({
                                    id: item.item_id, //Item ID
                                    price: item.sales_price,
                                    item_code: item.item_code, //Item Code
                                    name: item.item_name, //Item Name
                                    refer_number: item.refer_number,
                                    refer_line: item.refer_line,
                                    supplier_code: item.supplier_code,
                                    location_code: item.location_code,
                                    category: item.category,
                                    unit_price: item.sales_price,
                                    currency: item.currency_code,
                                    location_id: item.location_id,
                                    currency_id: item.currency_id,
                                    uom: item.uom,
                                    supplier_id: item.supplier_id,
                                    order_quantity: item.quantity,
                                    delivery_quantity: item.delivery_quantity,
                                    customer_po_no: item.customer_po_no,
                                    country_origin_id: item.country_origin_id,
                                    country_origin_cd: item.country_origin_cd,
                                    location_item_quantity: item.location_item_quantity,
                                    ref_id: item.refer_id,
                                    show: true
                                });
                            } else {
                                allVals.push({
                                    id: item.item_id, //Item ID
                                    price: item.sales_price,
                                    item_code: item.item_code, //Item Code
                                    name: item.item_name, //Item Name
                                    refer_number: item.refer_number,
                                    refer_line: item.refer_line,
                                    supplier_code: item.supplier_code,
                                    location_code: item.location_code,
                                    category: item.category,
                                    unit_price: item.sales_price,
                                    currency: item.currency_code,
                                    location_id: item.location_id,
                                    currency_id: item.currency_id,
                                    uom: item.uom,
                                    supplier_id: item.supplier_id,
                                    order_quantity: item.quantity,
                                    delivery_quantity: item.delivery_quantity,
                                    customer_po_no: item.customer_po_no,
                                    country_origin_id: item.country_origin_id,
                                    country_origin_cd: item.country_origin_cd,
                                    location_item_quantity: item.location_item_quantity,
                                    ref_id: item.refer_id,
                                    show: false
                                });
                            }
                        });

                        if ($('#company_is_inventory').val() == 'True') {
                            $('#modal_loc_item_code select').find('option[value=""]').prop('selected', true);
                        }
                    }
                });
                $('#modal_ref_number').removeClass('highlight-mandatory');
            } else {
                $('#modal_refer_line').val("");
            }

            clear_modal();
        });

        $('#modal_refer_line').on("change", function() {
            // var msg = check_duplicate(dyn_tbl_sel_row_id);
            // if (msg != '') {
            //     pop_ok_dialog("Duplicate Row", msg, function(){});
            // } else {
            let refer_line = $('#modal_refer_line').val();
            let check_refer_number = $('#modal_ref_number').val();
            let rowIndex = parseInt(editing_row.attr('data-row_index'));
            let item_qty = 0;

            if (!check_refer_number) {
                pop_ok_dialog("Warning!",
                    "Select refer number first",
                    function () { }
                );
                $(this).val('');
                clear_modal();
                return;
            }
            let found = false;
            refer_numbers.map(refers => {
                if (check_refer_number == refers.refer_number && refer_line == refers.refer_line) {
                    found = true;
                }
            })
            if (!found) {
                pop_ok_dialog("Warning!",
                    "Refer number and refer line is not found",
                    function () { }
                );
                $(this).val('');
                clear_modal();
                return;
            }

            // remainQuantity = getRemainQuantityDO(check_refer_number, refer_line, storeCopyRefNumberData, allVals);
            let idx = editing_row.find('label:first').text();
            storeCopyRefNumberData = saveCopyRefNumberDO(idx, check_refer_number, refer_line, 'add', storeCopyRefNumberData, allVals);
            for(var i=0; i<allVals.length; i++) {
                if(allVals[i].refer_line == refer_line) {
                    outstdg_qty = allVals[i].order_quantity - allVals[i].delivery_quantity;
                    location_qty = allVals[i].location_item_quantity;
                    if ($('#company_is_inventory').val() == 'True' && allVals[i].location_id){
                        item_qty = (outstdg_qty > location_qty) ? location_qty : outstdg_qty;
                    } else {
                        item_qty = outstdg_qty;
                    }
                    // item_qty = outstdg_qty;

                    if (item_qty < 0) {item_qty = 0;}
                    // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, refer_line, DO_ROW_INDEX_ITEM_QTY, DO_SELECT_INDEX_REF_NUMBER, DO_SELECT_INDEX_REFER_LINE, item_qty, rowIndex);
                    ref_remain_quantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+refer_line, item_qty, rowIndex);

                    $('#modal_customer_po_no').val(allVals[i].customer_po_no);
                    $('#modal_part_item_code').val(allVals[i].item_code);
                    $('#modal_supplier').val(allVals[i].supplier_code);
                    $('#modal_original_currency').val(allVals[i].currency);
                    $('#modal_uom').val(allVals[i].uom);
                    $('#modal_category').val(allVals[i].category);

                    $('#modal_price').val(float_format(allVals[i].unit_price).toFixed(6));
                    $('#modal_order_quantity').val(comma_format(allVals[i].order_quantity));
                    $('#modal_delivery_quantity').val(comma_format(allVals[i].order_quantity - ref_remain_quantity));
                    $('#modal_country_code select').val(allVals[i].country_origin_id).trigger('change');
                    if ($('#company_is_inventory').val() == 'True') {
                        if ($('#modal_loc_item_code select').data('select2')) {
                            $('#modal_loc_item_code select').select2('destroy');
                        }
                        $('#modal_loc_item_code select').empty();
                        var options = '';
                        options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                        $('#modal_loc_item_code select').append(options);
                        $('#modal_loc_item_code select').select2();
                        $('#modal_loc_item_code select').val(allVals[i].location_id).trigger('change');
                    }
                    if (ref_remain_quantity == undefined) {
                        $('#modal_quantity_do').val(comma_format(item_qty)).trigger('change');
                        ref_remain_quantity = item_qty;
                    }
                    if (ref_remain_quantity > 0) {
                        $('#modal_quantity_do').val(comma_format(ref_remain_quantity)).trigger('change');
                        // storeCopyRefNumberData = updateQuantityCopyRefNumberDO(line, check_refer_number, refer_line, storeCopyRefNumberData, ref_remain_quantity)
                    } else {
                        $('#modal_quantity_do').val(comma_format(ref_remain_quantity)).trigger('change');
                    }

                    setTimeout(() => {
                        //$('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
                    }, 300);

                    $('#modal_refer_line').removeClass('highlight-mandatory');

                    if (ref_remain_quantity > 0) {
                        $('#modal_quantity_do').removeClass('highlight-mandatory');
                    }
                    $('#modal_price').removeClass('highlight-mandatory');
                }
            }
        });

        var last_qty = 0;
        $('#modal_quantity_do').on("focus", function() {
            last_qty = float_format($(this).val());
        })
        $('#modal_quantity_do').on("change", function() {
            var quantity = float_format($('#modal_quantity_do').val());
            var price = float_format($('#modal_price').val());

            if (quantity > 0) {
                $(this).removeClass('highlight-mandatory');
            }

            let rowIndex = editing_row.find('label:first').text();
            let check_refer_number = $('#modal_ref_number').val();
            let check_refer_line = $('#modal_refer_line').val();
            outstanding_qty = getTotalMaxInputQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, rowIndex);
            // outstanding_qty = ref_remain_quantity;
            if (outstanding_qty == -1 && float_format(quantity) == 0) {
                pop_ok_dialog("Invalid Item Quantity",
                "This " + $('#modal_part_item_code').val() + " Stock Quantity : " + quantity,
                function(){
                    
                });
            } else if (float_format(quantity) > float_format(outstanding_qty) && float_format(outstanding_qty) > -1) {
                pop_ok_dialog("Invalid Item Quantity",
                "Quantity must not be greater than Outstanding Receive Quantity ("+ outstanding_qty +")",
                function(){
                    $('#modal_quantity_do').val(comma_format(outstanding_qty));
                    $('#modal_quantity_do').select();
                    $('#modal_amount').val(comma_format(price * outstanding_qty, decimal_place));
                });
            } else {
                $('#modal_amount').val(comma_format(price * quantity, decimal_place));
                $('#modal_quantity_do').val(comma_format(float_format($('#modal_quantity_do').val())));
                if (outstanding_qty == -1) {
                    outstanding_qty = float_format($('#modal_order_quantity').val()) - float_format($('#modal_delivery_quantity').val());
                }
                storeCopyRefNumberData = updateQuantityCopyRefNumberDO(rowIndex, check_refer_number, check_refer_line, storeCopyRefNumberData, $(this).val(), outstanding_qty);
                // if (quantity < last_qty) {
                //     let check_refer_number = $('#modal_ref_number').val();
                //     let check_refer_line = $('#modal_refer_line').val();
                //     if (rfn_exclude_list.indexOf(check_refer_number) != -1) {
                //         let indx = rfn_exclude_list.indexOf(check_refer_number);
                //         rfn_exclude_list.splice(indx, 1);
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, refer_numbers);
                //     } else {
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, refer_numbers, check_refer_line);
                //     }
                // }
                // if (quantity == ref_remain_quantity && ref_line_count == 1) {
                //     let check_refer_number = $('#modal_ref_number').val();
                //     if (rfn_exclude_list.indexOf(check_refer_number) == -1) {
                //         rfn_exclude_list.push(check_refer_number);
                //     }
                //     filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id);
                // } else if (quantity == ref_remain_quantity) {
                //     let check_refer_number = $('#modal_ref_number').val();
                //     let check_refer_line = $('#modal_refer_line').val();
                //     if (check_refer_number != '' && check_refer_line != '') {
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, dyn_tbl_sel_row_id, [], check_refer_line);
                //     }
                // }
            }
        })

        $('#modal_net_weight').on("change", function(e) {
            checkMaxInputForInt(99999999, $(this)[0].id);
        });

        $('#modal_gross_weight').on("change", function(e) {
            checkMaxInputForInt(99999999, $(this)[0].id);
        });

        $('#modal_m3_number').on("change", function(e) {
            checkMaxInputForInt(99999, $(this)[0].id);
        });

    }

    function is_modal_valid() {
        let valid = true;
        // Check each field is empty
        if ($('#modal_ref_number').val() === '' || $('#modal_ref_number').val() === null) {
            console.log('Error, line number empty');
            $('#modal_ref_numbert').addClass('highlight-mandatory');
            valid = false;
        }else {
            $('#modal_ref_number').removeClass('highlight-mandatory');
        }

        if ($('#modal_refer_line').val() === '' || $('#modal_refer_line').val() === null) {
            console.log('Error, item id empty');
            $('#modal_refer_line').addClass('highlight-mandatory');
            valid = false;
        }else {
            $('#modal_refer_line').removeClass('highlight-mandatory');
        }

        if ($('#modal_customer_po_no').val() === '') {
            console.log('Error, customer po empty');
            valid = false;
        }

        if ($('#modal_quantity_do').val() === '' || float_format($('#modal_quantity_do').val()) <= 0) {
            console.log('Error, quantity empty');
            $('#modal_quantity_do').addClass('highlight-mandatory');
            valid = false;
        } else {
            $('#modal_quantity_do').removeClass('highlight-mandatory');
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

    function loadOrderItemModal(selectedRowId) {
        $('#loading').show();
        $('.highlight-mandatory').removeClass('highlight-mandatory');
        dyn_tbl_sel_row_id = selectedRowId;
        let $selects = editing_row.find('select');
        if ($('#id_formset_item-' + selectedRowId + '-line_number').text()) {
            $('#modal_line_number').val(editing_row.find('label:first').text());
            $('#modal_loc_item_code').empty();
            $('#id_formset_item-' + selectedRowId + '-location')
                .clone()
                .attr('id', 'modal_loc_item_code_select')
                .attr('tabindex', '0')
                .appendTo('#modal_loc_item_code');
            if ($('#company_is_inventory').val() == 'True') {
                sel_loc = $('#id_formset_item-' + selectedRowId + '-location').val();
                $('#modal_loc_item_code select').val(sel_loc).trigger('change');
                $('#modal_loc_item_code select').removeAttr( 'style' );
                $('#modal_loc_item_code select').select2();

                $('#modal_loc_item_code select').on("select2:open", function( event ){
                    prefill_select2(event);

                    // Fix Select2 input search style
                    $('.select2-container input.select2-search__field').css({
                        // 'text-align': 'left',
                        'font-size': '12.5px'
                    });
                });

                $('#modal_loc_item_code .select2-container span.select2-selection__rendered').css({
                    'font-size': '15px'
                });
            } else {
                $('#loc_item').css('display', 'none');
                $('#modal_loc_item_code').css('display', 'none');
            }

            $('#modal_supplier').val($('#id_formset_item-' + selectedRowId + '-supplier').text());
            $('#modal_customer_po_no').val($('#id_formset_item-' + selectedRowId + '-customer_po_no').text());
            $('#modal_original_currency').val($('#id_formset_item-' + selectedRowId + '-original_currency').text());
            $('#modal_uom').val($('#id_formset_item-' + selectedRowId + '-uom').text());
            $('#modal_category').val($('#id_formset_item-' + selectedRowId + '-category').text());
            $('#modal_part_item_code').val($('#id_formset_item-' + (selectedRowId) + '-code').text());
            $('#modal_quantity_do').val($('#id_formset_item-' + selectedRowId + '-quantity_do').val());
            $('#modal_carton_no').val($('#id_formset_item-' + selectedRowId + '-carton_no').val());
            $('#modal_carton_total').val($('#id_formset_item-' + selectedRowId + '-carton_total').val());
            $('#modal_pallet_no').val($('#id_formset_item-' + selectedRowId + '-pallet_no').val());
            $('#modal_net_weight').val($('#id_formset_item-' + selectedRowId + '-net_weight').val());
            $('#modal_gross_weight').val($('#id_formset_item-' + selectedRowId + '-gross_weight').val());
            $('#modal_m3_number').val($('#id_formset_item-' + selectedRowId + '-m3_number').val());
            $('#modal_price').val($('#id_formset_item-' + selectedRowId + '-price').val());
            $('#modal_amount').val($('#id_formset_item-' + selectedRowId + '-amount').text());
            $('#modal_order_quantity').val($('#id_formset_item-' + selectedRowId + '-order_quantity').text());
            $('#modal_delivery_quantity').val($('#id_formset_item-' + selectedRowId + '-delivery_quantity').text());

            line_object['qty'] = $('#id_formset_item-' + selectedRowId + '-quantity_do').val();
            line_object['price'] = $('#id_formset_item-' + selectedRowId + '-price').val();
            line_object['carton_no'] = $('#id_formset_item-' + selectedRowId + '-carton_no').val();
            line_object['carton_total'] = $('#id_formset_item-' + selectedRowId + '-carton_total').val();
            line_object['m3'] = $('#id_formset_item-' + selectedRowId + '-m3_number').val();
            line_object['pallet_no'] = $('#id_formset_item-' + selectedRowId + '-pallet_no').val();
            line_object['net_weight'] = $('#id_formset_item-' + selectedRowId + '-net_weight').val();
            line_object['gross_weight'] = $('#id_formset_item-' + selectedRowId + '-gross_weight').val();

            // Destroy the Select2 element when is already generated
            if ($('#modal_country_code select').data('select2')) {
                $('#modal_country_code select').select2('destroy');
            }
            $('#modal_country_code').empty();
            $('#id_select_country_code-' + selectedRowId + '-country_code').trigger('select2:open');
            $('#id_select_country_code-' + selectedRowId + '-country_code').select2('close');
            $('#id_select_country_code-' + selectedRowId + '-country_code')
                .clone()
                .attr('id', 'modal_country_code_select')
                .attr('tabindex', '0')
                .appendTo('#modal_country_code');
            current_code = $('#id_select_country_code-' + selectedRowId + '-country_code').val();
            line_object['current_code'] = current_code;

            $('#modal_country_code select').val($('#id_select_country_code-' + selectedRowId + '-country_code').val());
            if ($('#id_select_country_code-' + selectedRowId + '-country_code').val() !== null) {
                setTimeout(function() {
                    // Generate Select2 element
                    $('#modal_country_code select').select2({
                        // dropdownParent: $('#doInvoiceItemModal'),
                        placeholder: '----',
                    });

                    // Fix Select2 Style
                    $('#modal_country_code .select2-container span.select2-selection__rendered').css({
                        'text-align': 'left',
                        'font-size': '15px'
                    });

                }, 100);
            }
            else {
                // Generate Select2 element
                $('#modal_country_code select').select2({
                    // dropdownParent: $('#doInvoiceItemModal'),
                    placeholder: '----'
                });
            }

            $('#modal_country_code select').val(current_code).trigger('change');
            $('#modal_country_code select').on("select2:open", function( event ){
                prefill_select2(event);

                // Fix Select2 input search style
                $('.select2-container input.select2-search__field').css({
                    'text-align': 'left',
                    'font-size': '12.5px'
                });
            });
            $('#modal_country_code  select').on("select2:select", function() {

            });
            $('#modal_country_code select').on("select2:close", function (event) {
                $('#modal_quantity_do').focus();
            });

            current_code = $('#id_formset_item-' + selectedRowId + '-ref_number').val();
            if (current_code == null || current_code == undefined) {
                current_code = ''
                line_object['ref_num'] = '';
            } else {
                line_object['ref_num'] = current_code;
            }
            $('#modal_ref_number').val($('#id_formset_item-' + selectedRowId + '-ref_number').val());
            
            current_code_l = $('#id_formset_item-' + selectedRowId + '-refer_line').val();
            if (current_code_l == null || current_code_l == undefined) {
                current_code_l = ''
                line_object['ref_line'] = '';
            } else {
                line_object['ref_line'] = current_code_l;
            }
            $('#modal_refer_line').val($('#id_formset_item-' + selectedRowId + '-refer_line').val());

            if ($('#company_is_inventory').val() == 'True' && is_sp_locked != "True") {
                setTimeout(function() {
                    $('#modal_loc_item_code select').select2('open');
                }, 500);
            } else if (is_sp_locked != "True") {
                setTimeout(function() {
                    $('#modal_country_code select').select2('open');
                }, 500);
            }

        }
        controlPrevNextBtn();
        bindOrderModalEvent();
        $('#loading').hide();
    }

    function check_duplicate(row_id) {
        var msg = '';
        $('#dynamic-table tr.gradeX').each(function () {
            let modal_ref_number = $('#modal_ref_number').val();
            let modal_refer_line = $('#modal_refer_line').val();
            let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let ref_number = '';
            let refer_line = '';
            try {
                let selects = $(this).closest('tr').find('input');
                ref_number = selects[DO_ROW_INDEX_REFER_NO].value;
                refer_line = selects[DO_ROW_INDEX_REFER_LINE].value;
            }catch (e) {
                ref_number = $('#id_formset_item-' + rowIndex + '-ref_number').val();
                refer_line = $('#id_formset_item-' + rowIndex + '-refer_line').val();
            }
            if (modal_ref_number == ref_number && modal_refer_line==refer_line && rowIndex !=row_id ) {
                msg = 'Duplicate entry at row number '+(rowIndex+1)+'<br/>Refer no: '+modal_ref_number+'<br/>Refer ln: '+modal_refer_line;
            }
        });
        return msg;
    }

    function saveOrderItemModal(selectedRowId) {
        let modal_ref_number = $('#modal_ref_number').val();
        let modal_refer_line = $('#modal_refer_line').val();

        let modal_quantity_do = float_format($('#modal_quantity_do').val());
        let modal_price = float_format($('#modal_price').val());
        let modal_carton_no = $('#modal_carton_no').val();
        let modal_carton_total = float_format($('#modal_carton_total').val());
        let modal_pallet_no = float_format($('#modal_pallet_no').val());
        let modal_net_weight = float_format($('#modal_net_weight').val());
        let modal_gross_weight = float_format($('#modal_gross_weight').val());
        let modal_m3_number = float_format($('#modal_m3_number').val());
        let modal_country_code_select = float_format($('#modal_country_code select').val());
        let location = $('#modal_loc_item_code select').val();

        let selected_ref_num = line_object['ref_num'];
        let selected_ref_line = line_object['ref_line'];

        $('#loading').modal('show');
        if (selected_ref_num != $('#modal_ref_number').val()
            && $('#modal_ref_number').val() != undefined) {
            $('#id_formset_item-' + selectedRowId + '-ref_number').val(modal_ref_number);
        }
        setTimeout(() => {
            if (selected_ref_num != $('#modal_ref_number').val()) {
                if ($('#modal_refer_line').val()
                    && $('#modal_refer_line').val() != undefined) {
                    $('#id_formset_item-' + selectedRowId + '-refer_line').val(modal_refer_line).trigger('change');
                }
            } else if (selected_ref_line != $('#modal_refer_line').val()) {
                if ( $('#modal_refer_line').val()
                    && $('#modal_refer_line').val() != undefined) {
                    $('#id_formset_item-' + selectedRowId + '-refer_line').val(modal_refer_line).trigger('change');
                }
            }
            setTimeout(function() {
                $('#id_formset_item-' + selectedRowId + '-quantity_do').val(comma_format(modal_quantity_do)).trigger('change');
                $('#id_formset_item-' + selectedRowId + '-price').val(float_format(modal_price).toFixed(6)).trigger('change');
                $('#id_formset_item-' + selectedRowId + '-carton_no').val(modal_carton_no);
                $('#id_formset_item-' + selectedRowId + '-carton_total').val(modal_carton_total);
                $('#id_formset_item-' + selectedRowId + '-pallet_no').val(modal_pallet_no);
                $('#id_formset_item-' + selectedRowId + '-net_weight').val(modal_net_weight.toFixed(2));
                $('#id_formset_item-' + selectedRowId + '-gross_weight').val(modal_gross_weight.toFixed(2));
                $('#id_formset_item-' + selectedRowId + '-m3_number').val(modal_m3_number.toFixed(4));
                $('select#id_select_country_code-' + selectedRowId + '-country_code').val(modal_country_code_select).trigger('change');
                $('#id_formset_item-' + selectedRowId + '-location').val(location).trigger('change');
                // $('#id_formset_item-' + selectedRowId + '-quantity_do').trigger('change');
                $('#loading').modal('hide');
            }, 300);
        }, 300);
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

        if (line_object['ref_num'] != $('#modal_ref_number').val()
            && $('#modal_ref_number').val() != undefined) {
            flag_change = true;
        }

        if (line_object['ref_line'] != $('#modal_refer_line').val()
            && $('#modal_refer_line').val() != undefined) {
            flag_change = true;
        }

        if (line_object['qty'] != $('#modal_quantity_do').val()) {
            flag_change = true;
        }

        if (line_object['price'] != $('#modal_price').val()) {
            flag_change = true;
        }

        if (line_object['current_code'] != $('#modal_country_code_select').val()
            && $('#modal_country_code_select').val() != undefined) {
            flag_change = true;
        }
        if (line_object['carton_no'] != $('#modal_carton_no').val()) {
            flag_change = true;
        }
        if (line_object['carton_total'] != $('#modal_carton_total').val()) {
            flag_change = true;
        }
        if (line_object['net_weight'] != $('#modal_net_weight').val()) {
            flag_change = true;
        }
        if (line_object['gross_weight'] != $('#modal_gross_weight').val()) {
            flag_change = true;
        }
        if (float_format(line_object['m3'])  != float_format($('#modal_m3_number').val())) {
            flag_change = true;
        }
        if (line_object['pallet_no'] != $('#modal_pallet_no').val()) {
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
                    loadOrderItemModal(selectedRowId);
                }, 1000);
            }, 1500);
        }
        else {
            // var rowCount = parseInt($('#id_formset_item-TOTAL_FORMS').val());
            // $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.removerow').trigger('click');
            // $('#dynamic-table tr.gradeX:nth-child(' + (rowCount-1) + ')').find('.appendrow').trigger('click');
            // setTimeout(() => {
            //     loadOrderItemModal(rowCount-1);
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
                loadOrderItemModal(selectedRowId);
            } else {
                editing_row = $('#dynamic-table tr.gradeX:nth-child(1)');
                selectedRowId = parseInt(editing_row.attr('data-row_index'));
                loadOrderItemModal(selectedRowId);
            }
        }, 800);
    }

    function orderItemCancel() {
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
            $('#doInvoiceItemModal').modal('hide');
        }
    }

    function resetReferNumber() {
        // if ($("#doInvoiceItemModal").is(':visible')) {
        //     let refer_number = $('#modal_ref_number').val();
        //     let idx = rfn_exclude_list.indexOf(refer_number);
        //     rfn_exclude_list.splice(idx, 1);
        // }
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
            $('#doInvoiceItemModal').modal('hide');
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
});


$('[id*="id_select_country_code"]').on('change', function (e) {
    let currentRow = $(this).closest('tr').find('input');
    currentRow[DO_ROW_INDEX_COUNTRY_ORG_CD].value = $(this).find(':selected').text();
    currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].value = $(this).find(':selected').val();
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
            url: '/orders/change_supplier/' + hdSupplierId + '/',
            title: 'Enter supplier name',
            success: function (response, newValue) {
                if (!response) {
                    return "Unknown error!"
                }
                if (response.success === false) {
                    return respond.msg;
                }
            }
        });

        $('#supplier_address').editable({
            type: 'text',
            pk: hdSupplierId,
            url: '/orders/change_supplier/' + hdSupplierId + '/',
            title: 'Enter supplier address',
            success: function (response, newValue) {
                if (!response) {
                    return "Unknown error!"
                }
                if (response.success === false) {
                    return respond.msg;
                }
            }
        });

        $('#supplier_email').editable({
            type: 'text',
            pk: hdSupplierId,
            url: '/orders/change_supplier/' + hdSupplierId + '/',
            title: 'Enter supplier email',
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
    };

    $('#id_supplier').change(function () {
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

$('#id_subtotal').on('change', function() {
    console.log($('#id_subtotal').val());
})
//event handle for input discount
$('#id_discount').change(function () {
    if ($(this).val() != '') {
        var sum = float_format($('#id_subtotal').val()) + float_format($('#id_tax_amount').val());
        sum -= parseInt(this.value);
        $('#id_total').val(comma_format(sum, decimal_place));
    } else {
        var sum = 0;
        $('#dynamic-table tr.gradeX').each(function () {
            var currentRow = $(this).find('input');
            amount = currentRow[DO_ROW_INDEX_AMOUNT].value;
            sum += parseInt(amount);
            $('#id_subtotal').val(comma_format(roundDecimal(sum, decimal_place), decimal_place));
            var total = sum + float_format($('#id_tax_amount').val());
            $('#id_total').val(comma_format(roundDecimal(total, decimal_place), decimal_place));
        })
    }
});

//event change quantity
function handleQuantity() {
    $('#dynamic-table tr.gradeX').each(function () {
        var last_price = 0.00;
        var last_qty_t = 0;
        currentRow = $(this).closest('tr').find('input');
        currentColumn = $(this).closest('tr').find('td');
        $ItemQty = '#' + currentRow[DO_ROW_INDEX_ITEM_QTY].id; // ID of Quantity Column
        var order_type = $('#order_type').text();
        var is_generate = $('#is_generate').text();
        var order_id = $('#order_id').text();
        var prv_qty = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);

        $($ItemQty).on('focus', function (e) {
            last_qty_t = float_format($(this).val());
        })

        $($ItemQty).off('change').on('change', function (e) {
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            is_location = $('#company_inventory').val();
            let id_refer_line = '#' + $($(this).closest('tr').find('input')[DO_ROW_INDEX_REFER_LINE]).id;
            // var code = currentRow[DO_LABEL_INDEX_ITEM_CODE].value;
            // var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value); // Quantity Value
            // if (quantity == 'NaN' || quantity < 0){
            //     quantity = 0;
            // }

            // var input_qty = quantity;
            // currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(input_qty);
            var location_item_quantity = float_format(currentRow[DO_ROW_INDEX_LOC_ITEM_QTY].value); // Location onhand_qty
            var order_quantity = float_format(currentRow[DO_ROW_INDEX_ORDER_QTY].value);
            var quantities = getItemQty(currentRow[DO_ROW_INDEX_REFER_NO].value,currentRow[DO_ROW_INDEX_ITEM_ID].value, initial_item_qty);
            var quantity = float_format($(this).val());
            // if(order_id == "") {
            //     var outstdg_qty = float_format(quantities.OutstandingQty).toFixed(2);
            // } else {
            //     var outstdg_qty = float_format(quantities.OutstandingQty + float_format(prv_qty)).toFixed(2);
            // }
            var input_qty = quantity;
            let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
            let $selects = $(this).closest('tr').find('select');
            let check_refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').val();
            let check_refer_line = $('#id_formset_item-' + (rowIndex) +'-refer_line').val();
            let old_line = false;
            // if($('#company_is_inventory').val() == 'True' && $selects.length > 2 || ($('#company_is_inventory').val() != 'True' && $selects.length > 1)) {
            //     check_refer_number = $($(this).closest('tr').find('select')[DO_SELECT_INDEX_REF_NUMBER]).val();
            //     check_refer_line = $($(this).closest('tr').find('select')[DO_SELECT_INDEX_REFER_LINE]).val();
            // } else {
            //     check_refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').text();
            //     check_refer_line = $('#id_formset_item-' + (rowIndex) +'-refer_line').text();
            //     old_line = true;
            // }

            let idx = $(this).closest('tr').find('label:first').text();
            outstdg_qty = getTotalMaxInputQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, idx);
            if (old_line) {
                outstdg_qty = float_format(quantities.OutstandingQty + quantities.ItemQty).toFixed(2);
            }
            // outstdg_qty = ref_remain_quantity;
            if ((quantity > 0 && check_refer_line == undefined) ||
                (quantity > 0 && check_refer_line == '')) {
                var unitPrice = float_format(currentRow[DO_ROW_INDEX_PRICE].value);
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

            } else if (quantity == 'NaN' || quantity <= 0) {
                if (outstdg_qty > 0) {
                    WarnQtyExceded(outstdg_qty,this,
                        "Quantity is invalid!");
                } else if (last_qty_t > 0) {
                    WarnQtyExceded(last_qty_t,this,
                        "Quantity is invalid!");
                } else {
                    WarnQtyExceded(order_quantity,this,
                        "Quantity is invalid!");
                }
            } else if (float_format(quantity) > float_format(outstdg_qty) &&
                float_format(outstdg_qty) > -1) {
                WarnQtyExceded(outstdg_qty,this,
                "Quantity must not be greater than Outstanding Receive Quantity ("+ outstdg_qty +")");
            } else if (float_format(input_qty) > float_format(order_quantity) && is_location != 'True') {
                WarnQtyExceded(order_quantity,this,
                "Quantity must not be greater than Order Quantity ("+ order_quantity +")");
            } else if (!old_line && (is_location == 'True') && (float_format(quantity) > float_format(location_item_quantity))) {
                var w_str = "Sorry, Insufficient Item Stock Quantity. Current Stock Quantity is ("+ location_item_quantity +")."
                WarnQtyExceded(location_item_quantity,this, w_str);
            } else {
                // let rowNumber = 0;
                // $('#dynamic-table tr.gradeX').each(function () {
                //     recalculateDOAmount(this, DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT, rowNumber);

                //     $(this).closest('tr').find('input').removeAttr('disabled');
                //     rowNumber++;
                // });
                var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                last_amount = float_format($('#id_formset_item-'+(row-1)+'-amount').text());
                var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
                var price = float_format(currentRow[DO_ROW_INDEX_PRICE].value);

                // $('#'+currentRow[DO_ROW_INDEX_AMOUNT].id).val(roundDecimal(quantity * price, decimal_place));
                currentRow[DO_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
                $('#id_formset_item-'+(row-1)+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
                new_amount = roundDecimal(quantity * price, decimal_place);
                calculateDOTotal(last_amount, new_amount);
                $(this).closest('tr').removeAttr('style');
                $('#items_error').css('display', 'none');
                $('#minimum_order_error').css('display', 'none');
                fnEnableButton();

                // currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(input_qty, 2);
                $(this).val(comma_format(input_qty));
                // calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);

                let rowIndex = parseInt($(this).closest('tr').attr('data-row_index'));
                // let $selects = $(this).closest('tr').find('select');
                // let check_refer_number;
                // let check_refer_line;
                // if($('#company_is_inventory').val() == 'True' && $selects.length > 2 || ($('#company_is_inventory').val() != 'True' && $selects.length > 1)) {
                //     check_refer_number = $($(this).closest('tr').find('select')[DO_SELECT_INDEX_REF_NUMBER]).val();
                //     check_refer_line = $($(this).closest('tr').find('select')[DO_SELECT_INDEX_REFER_LINE]).val();
                // } else {
                //     check_refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').text();
                //     check_refer_line = $('#id_formset_item-' + (rowIndex) +'-refer_line').text();
                // }
                if (outstdg_qty == -1) {
                    order_quantity = float_format(currentRow[DO_ROW_INDEX_ORDER_QTY].value);
                    delivery_quantity = float_format(currentRow[DO_ROW_INDEX_DELIVERY_QTY].value);
                    outstdg_qty = order_quantity - delivery_quantity;
                }
                let idx = $(this).closest('tr').find('label:first').text();
                storeCopyRefNumberData = updateQuantityCopyRefNumberDO(idx, check_refer_number, check_refer_line, storeCopyRefNumberData, $(this).val(), outstdg_qty);
                if(!old_line) {
                    ramaining_qty_list = update_remaining_qty(ramaining_qty_list, check_refer_number+'-'+check_refer_line, quantity, rowIndex);
                }

                // if (quantity < last_qty_t) {
                //     if (rfn_exclude_list.indexOf(check_refer_number) != -1) {
                //         let indx = rfn_exclude_list.indexOf(check_refer_number);
                //         rfn_exclude_list.splice(indx, 1);
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, -1, refer_numbers);
                //     } else {
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, -1, refer_numbers, check_refer_line);
                //     }
                // }

                // if (quantity == ref_remain_quantity && ref_line_count == 1) {
                //     if (rfn_exclude_list.indexOf(check_refer_number) == -1) {
                //         rfn_exclude_list.push(check_refer_number);
                //     }
                //     filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, -1);
                // } else if (quantity == ref_remain_quantity) {
                //     if (check_refer_number != '' && check_refer_line != '') {
                //         filterAllReferNumber("DO", '#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, rowIndex, [], check_refer_line);
                //     }
                // }

                // if (quantity == ref_remain_quantity) {
                //     if (check_refer_number != '' && check_refer_line != '') {
                //         last_refer_line = filterAllReferLine('#dynamic-table tr.gradeX', check_refer_number, DO_SELECT_INDEX_REF_NUMBER, rowIndex, refer_numbers, check_refer_line, last_refer_line, "DO");
                //     }
                // }
            }
            let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
            highLightMandatory(rowCheck);
        });
        $($ItemQty).click(function () {
            $(this).select();
        });

        $lastElement = '#' + currentRow[DO_ROW_INDEX_PRICE].id;
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
                    let rowIndex = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                }
            }
        });

        $ItemPrice = '#' + currentRow[DO_ROW_INDEX_PRICE].id; // ID of Quantity Column
        $($ItemPrice).off('change').on('change', function (e) {
            currentRow = $(this).closest('tr').find('input');
            currentLabel = $(this).closest('tr').find('label');
            var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
            if (quantity == 'NaN' || quantity < 0){
                quantity = 0;
            }
            currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(quantity);

            var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
            var price = float_format(currentRow[DO_ROW_INDEX_PRICE].value);
            if (price == 'NaN'){
                price = 0;
            }
            if (price <= 0) {
                WarnPriceExceded(float_format(1).toFixed(2), this,
                    "The Price of product "  + currentRow[DO_ROW_INDEX_ITEM_CODE].value +
                    " must be greater than 0.00");

                $('#'+currentRow[DO_ROW_INDEX_AMOUNT].id).val("1.00");
            } else {
                currentRow[DO_ROW_INDEX_PRICE].value = price.toFixed(6);
                // recalculateDOAmount(this, DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT, (row-1));
                var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
                last_amount = float_format($('#id_formset_item-'+(row-1)+'-amount').text());
                var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
                var price = float_format(currentRow[DO_ROW_INDEX_PRICE].value);

                // $('#'+currentRow[DO_ROW_INDEX_AMOUNT].id).val(roundDecimal(quantity * price, decimal_place));
                currentRow[DO_ROW_INDEX_AMOUNT].value = roundDecimal(quantity * price, decimal_place);
                $('#id_formset_item-'+(row-1)+'-amount').text(comma_format(roundDecimal(quantity * price, decimal_place), decimal_place));
                new_amount = roundDecimal(quantity * price, decimal_place);
                calculateDOTotal(last_amount, new_amount);
                $(this).closest('tr').removeAttr('style');
                fnEnableButton();

                // calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);

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

        $lastElement = '#' + currentRow[DO_ROW_INDEX_GROSS_WEIGHT].id; // ID of Quantity Column
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
                    }, idFirstInvalid
                );
                } else {
                    let rowIndex = parseInt($(this).closest('tr').find('label:first').text());
                    let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
                    let copy_refer_number = $('#id_formset_item-' + (rowCheck) +'-ref_number').val();
                    // if (copy_refer_number == undefined) {
                    //     copy_refer_number = $('#id_formset_item-' + (rowCheck) +'-ref_number').text();
                    // }
                    tabAddRow(rowIndex, e.which, copy_refer_number);
                }
            }
        });

        $referNo= '#' + currentRow[DO_ROW_INDEX_REFER_NO].id;
        referNoEvent($referNo);

        $referLine = '#' + currentRow[DO_ROW_INDEX_REFER_LINE].id;
        referLineEvent($referLine);
    });

    // $("input[id$='-net_weight']").val(float_format($("input[id$='-net_weight']").val()).toFixed(2));
    // $("input[id$='-m3_number']").val(float_format($("input[id$='-m3_number']").val()).toFixed(2));

    $("input[id$='-net_weight']").focusout(function (e) {
        checkMaxInputForInt(99999999, $(this)[0].id);
    });

    $("input[id$='-gross_weight']").focusout(function (e) {
        checkMaxInputForInt(99999999, $(this)[0].id);
    });

    $("input[id$='-m3_number']").focusout(function (e) {
        checkMaxInputForInt(99999, $(this)[0].id);
    });
}

function referNoEvent($referNo) {
    $($referNo).off('change').on('change', function (e) {
        let currentRow = $(this).closest('tr').find('input');
        let currentLabel = $(this).closest('tr').find('label');
        let found = false;
        let so_number = null;
        refer_numbers.map(refers => {
            if ($(this).val() == refers.refer_number) {
                found = true;
                so_number = refers.ref_id;
            }
        })
        if (!found) {
            pop_ok_dialog("Warning!",
                "Refer number is not found",
                function () { }
            );
            $(this).val('');
            refreshCurrentRow(currentRow, currentLabel);
            return;
        }

        refreshCurrentRow(currentRow, currentLabel);
        ramaining_qty_list = update_remaining_qty(ramaining_qty_list, '', 0, parseInt($(this).closest('tr').attr('data-row_index')), true);

        var hdCustomerId = $('#hdCustomerId').val();
        let doc_date = $('#id_document_date').val();
        // let so_number = currentRow[DO_ROW_INDEX_REFERENCE_ID].value;
        let check_refer_number = $(this).val();
        // let this_id = this.id;
        // let ref_line_id = 'id_select-' + (parseInt($(this).closest('tr').attr('data-row_index'))) + '-refer_line';
        // let found = false;
        let line = $(this).closest('tr').find('label:first').text();
        // $(storeCopyRefNumberData).each(function (indx, value) {
        //     if (value.line == line) {
        //         if (check_refer_number != value.ref_number) {
        //             let idx = rfn_exclude_list.indexOf(value.ref_number);
        //             rfn_exclude_list.splice(idx, 1);
        //         }
        //         found = true;
        //     }
        // });

        if(so_number != '0' && so_number != undefined && so_number != null) {
            $.ajax({
                method: "POST",
                url: '/orders/get_orderitems_by_so_no/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'so_number': so_number,
                    'customer_id': hdCustomerId,
                    'doc_date': doc_date,
                    'exclude_item_list': []
                },
                success: function (json) {
                    allVals.length = 0;
                    ref_line_count = 0;
                    $.each(json, function (i, item) {
                        let item_qty = 0;
                        let outstdg_qty = float_format(item.quantity) - float_format(item.delivery_quantity);
                        let location_qty = float_format(item.location_item_quantity);
                        if ($('#company_is_inventory').val() == 'True' && item.location_id){
                            item_qty = (outstdg_qty > location_qty) ? location_qty : outstdg_qty;
                        } else {
                            item_qty = outstdg_qty;
                        }
                        // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, item.refer_line, DO_ROW_INDEX_ITEM_QTY, DO_SELECT_INDEX_REF_NUMBER, DO_SELECT_INDEX_REFER_LINE, item_qty);
                        ref_remain_quantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+item.refer_line, item_qty);
                        if (ref_remain_quantity) {
                            ref_line_count++;
                            allVals.push({
                                id: item.item_id, //Item ID
                                price: item.sales_price,
                                item_code: item.item_code, //Item Code
                                name: item.item_name, //Item Name
                                refer_number: item.refer_number,
                                refer_line: item.refer_line,
                                supplier_code: item.supplier_code,
                                location_code: item.location_code,
                                category: item.category,
                                unit_price: item.sales_price,
                                currency: item.currency_code,
                                location_id: item.location_id,
                                currency_id: item.currency_id,
                                uom: item.uom,
                                supplier_id: item.supplier_id,
                                order_quantity: item.quantity,
                                delivery_quantity: item.delivery_quantity,
                                customer_po_no: item.customer_po_no,
                                country_origin_id: item.country_origin_id,
                                country_origin_cd: item.country_origin_cd,
                                location_item_quantity: item.location_item_quantity,
                                ref_id: item.refer_id,
                                show: true
                            });
                        } else {
                            allVals.push({
                                id: item.item_id, //Item ID
                                price: item.sales_price,
                                item_code: item.item_code, //Item Code
                                name: item.item_name, //Item Name
                                refer_number: item.refer_number,
                                refer_line: item.refer_line,
                                supplier_code: item.supplier_code,
                                location_code: item.location_code,
                                category: item.category,
                                unit_price: item.sales_price,
                                currency: item.currency_code,
                                location_id: item.location_id,
                                currency_id: item.currency_id,
                                uom: item.uom,
                                supplier_id: item.supplier_id,
                                order_quantity: item.quantity,
                                delivery_quantity: item.delivery_quantity,
                                customer_po_no: item.customer_po_no,
                                country_origin_id: item.country_origin_id,
                                country_origin_cd: item.country_origin_cd,
                                location_item_quantity: item.location_item_quantity,
                                ref_id: item.refer_id,
                                show: false
                            });
                        }
                    });
                    console.log(allVals);
                }
            });
        } else {
            // refreshCurrentRow(currentRow, currentLabel);
        }

        let rowIndex = $(this).closest('tr').find('label:first').text();
        storeCopyRefNumberData = saveCopyRefNumberDO(rowIndex, 'remove', 'remove', 'remove', storeCopyRefNumberData, allVals);
        // storeCopyRefNumberData = changeIndexData(rowIndex, 'minus', storeCopyRefNumberData);
    })
}

function referLineEvent($referLine) {
    $($referLine).off('change').on('change', function (e) {
        let selects = $(this).closest('tr').find('select');
        let outstdg_qty;
        let location_qty;
        let item_qty;
        let rowIndex = $(this).closest('tr').find('label:first').text();
        let rIndex = parseInt($(this).closest('tr').attr('data-row_index'));
        let refer_line = $(this).val();
        let currentLabel = $(this).closest('tr').find('label');
        let currentRow = $(this).closest('tr').find('input');
        let check_refer_number = $(currentRow[DO_ROW_INDEX_REFER_NO]).val();
        let check_refer_line = $(this).val();
        if (!check_refer_number) {
            pop_ok_dialog("Warning!",
                "Select refer number first",
                function () { }
            );
            $(this).val('');
            return;
        }
        let found = false;
        refer_numbers.map(refers => {
            if (check_refer_number == refers.refer_number && check_refer_line == refers.refer_line) {
                found = true;
            }
        })
        if (!found) {
            pop_ok_dialog("Warning!",
                "Refer number and refer line is not found",
                function () { }
            );
            $(this).val('');
            refreshCurrentRow(currentRow, currentLabel);
            return;
        }

        // remainQuantity = getRemainQuantityDO(check_refer_number, check_refer_line, storeCopyRefNumberData, allVals);
        storeCopyRefNumberData = saveCopyRefNumberDO(rowIndex, check_refer_number, check_refer_line, 'add', storeCopyRefNumberData, allVals);
        ramaining_qty_list = update_remaining_qty(ramaining_qty_list, '', 0, parseInt($(this).closest('tr').attr('data-row_index')), true);
        for(var i=0; i<allVals.length; i++) {
            if(allVals[i].refer_line == refer_line) {
                //add value to Input
                currentRow[DO_ROW_INDEX_LINE_NUMBER].value = currentLabel[DO_LABEL_INDEX_LINE_NUMBER].textContent;
                currentRow[DO_ROW_INDEX_ITEM_CODE].value = allVals[i].item_code;
                currentRow[DO_ROW_INDEX_ITEM_NAME].value = allVals[i].name;
                currentRow[DO_ROW_INDEX_ITEM_ID].value = allVals[i].id;
                currentRow[DO_ROW_INDEX_CUSTOMER_PO].value = allVals[i].customer_po_no;

                if ($('#company_is_inventory').val() == 'True' && allVals[i].location_id){
                    location_choice = '#' + selects[DO_SELECT_INDEX_LOCATION].id;
                    if ($(location_choice).data('select2')) {
                        $(location_choice).select2('destroy');
                    }
                    $(location_choice).empty();
                    var options = '';
                    options += "<option value="+allVals[i].location_id+">"+allVals[i].location_code+"</option>";
                    $(location_choice).append(options);
                    $(location_choice).select2();
                    // $(location_choice).find('option[value="' + allVals[i].location_id + '"]').prop('selected', true);
                    $(location_choice).val(allVals[i].location_id).trigger('change');
                    currentRow[DO_ROW_INDEX_LOC_ITEM_QTY].value = allVals[i].location_item_quantity;
                }

                outstdg_qty = float_format(allVals[i].order_quantity) - float_format(allVals[i].delivery_quantity);
                location_qty = float_format(allVals[i].location_item_quantity);
                if ($('#company_is_inventory').val() == 'True' && allVals[i].location_id){
                    item_qty = (outstdg_qty > location_qty) ? location_qty : outstdg_qty;
                } else {
                    item_qty = outstdg_qty;
                }
                // item_qty = outstdg_qty;
                if (item_qty < 0) {item_qty = 0;}
                currentRow[DO_ROW_INDEX_ITEM_QTY].value = '0.00';
                // ref_remain_quantity = get_remaining_quantity('#dynamic-table tr.gradeX', check_refer_number, check_refer_line, DO_ROW_INDEX_ITEM_QTY, DO_SELECT_INDEX_REF_NUMBER, DO_SELECT_INDEX_REFER_LINE, item_qty, rowIndex);
                ref_remain_quantity = get_remaining_qty(ramaining_qty_list, check_refer_number+'-'+check_refer_line, item_qty, rowIndex);
                if (ref_remain_quantity == undefined) {
                    currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(item_qty);
                    ref_remain_quantity = item_qty;
                } else if (ref_remain_quantity > 0) {
                    currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(ref_remain_quantity);
                    // storeCopyRefNumberData = updateQuantityCopyRefNumberDO((rowIndex), check_refer_number, check_refer_line, storeCopyRefNumberData, ref_remain_quantity)
                } else {
                    currentRow[DO_ROW_INDEX_ITEM_QTY].value = comma_format(ref_remain_quantity);
                }
                
                currentRow[DO_ROW_INDEX_PRICE].value = float_format(allVals[i].unit_price).toFixed(6);
                currentRow[DO_ROW_INDEX_CURRENCY_CODE].value = allVals[i].currency;
                currentRow[DO_ROW_INDEX_CURRENCY_ID].value = allVals[i].currency_id;
                currentRow[DO_ROW_INDEX_CATEGORY].value = allVals[i].category;
                currentRow[DO_ROW_INDEX_SUPPLIER_CODE].value = allVals[i].supplier_code;
                currentRow[DO_ROW_INDEX_SUPPLIER_ID].value = allVals[i].supplier_id;
                // currentRow[DO_ROW_INDEX_REFER_NO].value = allVals[i].refer_number;
                // currentRow[DO_ROW_INDEX_REFER_LINE].value = allVals[i].refer_line;
                currentRow[DO_ROW_INDEX_ORDER_QTY].value = float_format(allVals[i].order_quantity).toFixed(2);
                currentRow[DO_ROW_INDEX_DELIVERY_QTY].value = float_format(allVals[i].delivery_quantity).toFixed(2);

                currentRow[DO_ROW_INDEX_UOM].value = allVals[i].uom;
                currentRow[DO_ROW_INDEX_COUNTRY_ORG_CD].value = allVals[i].country_origin_cd;
                currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].value = allVals[i].country_origin_id;
                country_choice = '#' + selects[DO_SELECT_INDEX_COUNTRY_CODE].id;
                $(country_choice).val(currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].value).trigger('change');
                currentRow[DO_ROW_INDEX_LOC_ITEM_QTY].value = allVals[i].location_item_quantity;
                currentRow[DO_ROW_INDEX_REFERENCE_ID].value = allVals[i].ref_id;

                currentLabel[DO_LABEL_INDEX_ITEM_CODE].textContent = currentRow[DO_ROW_INDEX_ITEM_CODE].value; // Item Code
                currentLabel[DO_LABEL_INDEX_ITEM_NAME].textContent = currentRow[DO_ROW_INDEX_ITEM_NAME].value; // Item Name
                // currentLabel[DO_LABEL_INDEX_PRICE].textContent = currentRow[DO_ROW_INDEX_PRICE].value; // Price
                currentLabel[DO_LABEL_INDEX_CURRENCY_CODE].textContent = currentRow[DO_ROW_INDEX_CURRENCY_CODE].value; // Currency Code
                currentLabel[DO_LABEL_INDEX_CATEGORY].textContent = currentRow[DO_ROW_INDEX_CATEGORY].value; // Part Group
                currentLabel[DO_LABEL_INDEX_SUPPLIER_CODE].textContent = currentRow[DO_ROW_INDEX_SUPPLIER_CODE].value; // Supplier Code
                currentLabel[DO_LABEL_INDEX_CUSTOMER_PO].textContent = currentRow[DO_ROW_INDEX_CUSTOMER_PO].value; // Refer Line
                currentLabel[DO_LABEL_INDEX_ORDER_QTY].textContent = comma_format(currentRow[DO_ROW_INDEX_ORDER_QTY].value); // Order Quantity
                currentLabel[DO_LABEL_INDEX_DELIVERY_QTY].textContent = comma_format(currentRow[DO_ROW_INDEX_DELIVERY_QTY].value); // Delivery Quantity
                currentLabel[DO_LABEL_INDEX_UOM].textContent = currentRow[DO_ROW_INDEX_UOM].value; // UOM

                if (float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) > 0 &&
                    !$("#doInvoiceItemModal").is(':visible')) {
                    $('#' + currentRow[DO_ROW_INDEX_ITEM_QTY].id).trigger('change');
                } else if (float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) == 0) {
                    pop_ok_dialog("Invalid Item Quantity",
                    "This " + currentLabel[DO_LABEL_INDEX_ITEM_CODE].textContent + " Stock Quantity : 0",
                    function(){
                        
                    });
                }
            }
        }
        doEssentials(currentRow);
        let rowCheck = parseInt($(this).closest('tr').attr('data-row_index'));
        highLightMandatory(rowCheck);
    })
}

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
            "The Price of product "  + currentRow[DO_ROW_INDEX_ITEM_CODE].value +
            " must be greater than 0.00");
    } else {
        $('#modal_price').removeClass('highlight-mandatory');
        $('#modal_price').val(price.toFixed(6));
        $('#modal_quantity_do').trigger('change');
    }
});


//change exchange rate event
$('#dynamic-table tr.gradeX').each(function () {
    currentRow = $(this).closest('tr').find('input');
    $exchangeElement = '#' + currentRow[DO_ROW_INDEX_EXCHANGE_RATE].id; // Get ID of Exchange Rate Column
    $($exchangeElement).change(function () {
        currentRow = $(this).closest('tr').find('input');
        if ($(this)[0].value <= 0) {
            $(this).closest('tr').attr('style', 'background-color: red !important');
            $('#items_error').text('Exchange Rate must have value greater than 0');
            $('#items_error').removeAttr('style');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[DO_ROW_INDEX_EXCHANGE_RATE]).attr('disabled', true);
            });
            fnDisableButton();
        } else {
            $('#items_error').css('display', 'none');
            $(this).closest('tr').removeAttr('style');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            fnEnableButton();
        }
    });
    $($exchangeElement).click(function () {
        $(this).select();
    });
});

// event copy customer address
$('#btnCopyCustomer').click(function () {
    var hdCustomerId = $('#hdCustomerId').val();
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

// $('#id_exchange_rate').click(function(){
//     $(this).select();
// });

$('#id_tax_exchange_rate').click(function(){
    $(this).select();
});

$('#payment_term').click(function(){
    $(this).select();
});

$('#hdr_delivery').click(function(){
    $(this).select();
});

$('#copy_date_doc').click(function(){
    $(this).select();
});

$('#tax_currency').click(function(){
    $(this).select();
});

$('#id_name').click(function(){
    $(this).select();
});

$('#id_phone').click(function(){
    $(this).select();
});

$('#id_attention').click(function(){
    $(this).select();
});

$('#id_address').click(function(){
    $(this).select();
});

$('#id_remark').click(function(){
    $(this).select();
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $country_org = '#' + currentRow[DO_ROW_INDEX_COUNTRY_ORG_CD].id;
    $($country_org).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $cust_po_no = '#' + currentRow[DO_ROW_INDEX_CUSTOMER_PO].id;
    $($cust_po_no).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $carton_no = '#' + currentRow[DO_ROW_INDEX_CARTON_NO].id;
    $($carton_no).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $carton_total = '#' + currentRow[DO_ROW_INDEX_CARTON_TOTAL].id;
    $($carton_total).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $pallet_no = '#' + currentRow[DO_ROW_INDEX_PALLET_NO].id;
    $($pallet_no).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $net_weight = '#' + currentRow[DO_ROW_INDEX_NET_WEIGHT].id;
    $($net_weight).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $gross_weight = '#' + currentRow[DO_ROW_INDEX_GROSS_WEIGHT].id;
    $($gross_weight).click(function () {
        $(this).select();
    });
});

$('#dynamic-table tr.gradeX').each(function () {
    var currentRow = $(this).closest('tr').find('input');
    var $m3_number = '#' + currentRow[DO_ROW_INDEX_M3_NUMBER].id;
    $($m3_number).click(function () {
        $(this).select();
    });
});

// event change address
$('#id_customer_address').change(function () {
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

function validationItemsFormset() {
    $('#dynamic-table tr.gradeX').find('input').each(function () {
        var order_type = $('#order_type').text();
        var order_id = $('#order_id').text();
        var display = $('#dynamic-table tr.gradeX:last').css("display");
        currentItem = $(this).closest('tr').find('option:selected');
        currentRow = $(this).closest('tr').find('input');
        currentLabel = $(this).closest('tr').find('label');
        inputQuantity = '#' + currentRow[DO_ROW_INDEX_ITEM_QTY].id;
        var count = $('#dynamic-table').find('tr').filter(function () {
            var colors = ["#ffc0cb", "rgb(255, 192, 203)"];
            return $.inArray($(this).css('background-color'), colors) !== -1;
        }).length;
        var row = parseInt($(this).closest('tr').attr('data-row_index')) + 1;
        var ord_qty = float_format($('#id_formset_item-'+(row-1)+'-order_quantity').text());
        var qty_dlv = float_format($('#id_formset_item-'+(row-1)+'-delivery_quantity').text());
        if (display == 'none') {
            $('#items_error').css('display', 'none');
        } else {
            if (order_id == "" && order_type == 1) { /* ORDER_TYPE['SALES ORDER'] */
                if (float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) > (float_format(ord_qty) - float_format(qty_dlv))) {
                    $(this).closest('tr').attr('style', 'background-color: pink !important');
                    $('#items_error').text('The quantity exceeds deliverable amount !');
                    $('#items_error').removeAttr('style');
                }
                if (currentRow[DO_ROW_INDEX_PRICE].value == "" || currentRow[DO_ROW_INDEX_PRICE].value == "None") {
                    $(this).closest('tr').attr('style', 'background-color: red !important');
                    $('#validate_error').text('Price of product must be greater than 0 and not none');
                    $('#validate_error').removeAttr('style');
                    $('#btnSave').attr('disabled', true);
                }
                if (count > 0) {
                    $('#items_error').removeAttr('style');
                    $('#items_error').text('The product don’t have enough stock quantity!');
                } else {
                    $('#items_error').css('display', 'none');
                }
                ;
            } else {
                if (float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) > (float_format(ord_qty) - float_format(qty_dlv))) {
                    $(this).closest('tr').attr('style', 'background-color: pink !important');
                    $('#items_error').text('The quantity exceeds deliverable amount!');
                    $('#items_error').removeAttr('style');
                }
                if (count > 0) {
                    $('#items_error').removeAttr('style');
                    $('#items_error').text('The product don’t have enough stock quantity!');
                } else {
                    $('#items_error').css('display', 'none');
                }
                ;
            }
            ;
            $('#dynamic-table tr.gradeX').each(function () {
                var table = $('#tblData').DataTable();
                var data = table.rows().data();
                currentRow = $(this).closest('tr').find('input');
                item_id = currentRow[DO_ROW_INDEX_ITEM_ID].value;
                data.each(function (value, index) {
                    if (value[9] == item_id) {
                        var row = table.row('#' + item_id).node();
                        row.setAttribute("style", "display: none");
                    }
                });
            });
        }
    });
    $('#id_customer_address').find('option').each(function () {
        if ($('#id_name').val() == $(this).text()) {
            $(this).attr('selected', true);
        }
    });
}

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
            var item_currency_not_match = [];
            var sale_price = 0;
            var amount = 0;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    let rowCount = 0;
                    $('#dynamic-table tr.gradeX').each(function () {
                        currentRow = $(this).closest('tr').find('input');
                        currentItemName = currentRow[DO_ROW_INDEX_ITEM_NAME].value; // Get Item Name
                        if (currentRow[DO_ROW_INDEX_ITEM_ID].value == json[i].id) { // Check Item ID
                            if (json[i].rate == 0 || json[i].sale_price == "") {
                                currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value = 0;
                                currentRow[DO_ROW_INDEX_AMOUNT].value = 0;
                                $('#id_formset_item-'+rowCount+'-amount').text(comma_format(float_format(currentRow[DO_ROW_INDEX_AMOUNT].value), decimal_place));
                                $('.lblCurrency').text(json['symbol']);
                            } else {
                                sale_price = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[DO_ROW_INDEX_PRICE].value); // Calculate Quantity * Sale Price
                                currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value = float_format(json[i].rate).toFixed(10); // Set Exchange Rate
                                amount = roundDecimal(currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value * sale_price, decimal_place); // Set Sale Price * Exchange Rate
                                currentRow[DO_ROW_INDEX_AMOUNT].value = amount; // Set Amount
                                $('#id_formset_item-'+rowCount+'-amount').text(comma_format(amount, decimal_place)); // Amount
                                $('.lblCurrency').text(json['symbol']);
                            }
                        }
                        rowCount++;
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
            
            // calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);
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
            var item_currency_not_match = [];
            var sale_price = 0;
            var amount = 0;
            var row = $(currentRow[0]).parent().parent().attr('data-row_index');
            var last_amount = float_format($('#id_formset_item-'+row+'-amount').text());
            var new_amount = last_amount;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    if (currentRow[DO_ROW_INDEX_ITEM_ID].value == json[i].id) { // Check Item ID
                        if (json[i].rate == 0 || json[i].sale_price == "") {
                            currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value = 0;
                            currentRow[DO_ROW_INDEX_AMOUNT].value = 0;
                            new_amount = 0;
                            $('#id_formset_item-'+row+'-amount').text(comma_format(float_format(currentRow[DO_ROW_INDEX_AMOUNT].value), decimal_place));
                            $('.lblCurrency').text(json['symbol']);
                        } else {
                            sale_price = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value) * float_format(currentRow[DO_ROW_INDEX_PRICE].value); // Calculate Quantity * Sale Price
                            currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value = float_format(json[i].rate).toFixed(10); // Set Exchange Rate
                            amount = currentRow[DO_ROW_INDEX_EXCHANGE_RATE].value * sale_price; // Set Sale Price * Exchange Rate
                            new_amount = amount;
                            currentRow[DO_ROW_INDEX_AMOUNT].value = amount.toFixed(decimal_place); // Set Amount
                            $('#id_formset_item-'+row+'-amount').text(comma_format(float_format(currentRow[DO_ROW_INDEX_AMOUNT].value), decimal_place)); // Amount
                            $('.lblCurrency').text(json['symbol']);
                        }
                    }
                }
            }


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
            calculateDOTotal(last_amount, new_amount);
        }
    });
}

function calculateDOTotal(last_amount, new_amount) {
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


function recalculateDOAmount(element, index_qty, index_price, index_amt, rowNumber, return_value){
    return_value = (return_value !== undefined);

    if (!return_value) {
        currentRow = $(element).closest('tr').find('input');

        var quantity = float_format(currentRow[index_qty].value);
        var price = float_format(currentRow[index_price].value);

        $('#'+currentRow[index_amt].id).val(price * quantity).trigger("change");

        $('#id_formset_item-'+rowNumber+'-amount').text(comma_format(price * quantity, decimal_place));

    }
    else {
        return (float_format(index_qty) * float_format(index_price));
    }
}


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
        var qty = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
        var price = float_format(currentRow[DO_ROW_INDEX_PRICE].value);
        currentRow[DO_ROW_INDEX_ITEM_QTY].value = qty;
        currentRow[DO_ROW_INDEX_PRICE].value = price;
        if (currentRow[DO_ROW_INDEX_AMOUNT].value == '') {
            // let amount = float_format(currentLabel[DO_LABEL_INDEX_AMOUNT].textContent);
            let amount = float_format($('#id_formset_item-'+rowIndex+'-amount').text());
            currentRow[DO_ROW_INDEX_AMOUNT].value = amount;
            subtotal += amount;
        } else {
            let amount = float_format(currentRow[DO_ROW_INDEX_AMOUNT].value);
            currentRow[DO_ROW_INDEX_AMOUNT].value = amount;
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

    $('#btnSearchItem').on('click', function () {
        fnSearchDOInvocieItem();
    });
    $('#btnOpenItemDialog').on('click', function () {
        var dataTable = $('#tblData').dataTable();
        dataTable.fnClearTable(this);
        fnSearchDOInvocieItem();
    });
    // Search Countries dialog
    $('#tblDataCountry').dataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[1, "desc"], [0, "desc"]]
    });
    // $('.check-valid-item-data').on('click', function () {
    //     var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
    //     if (countRowVisible == 0) {
    //         $('#items_error').text('Please select products before save!');
    //         $('#items_error').removeAttr('style');
    //         fnDisableButton();
    //     }
    // });
    $('#form').submit(function (e) {
        // var total = float_format($('#id_total').val());
        // if (total == 0) {
        //     $('#items_error').text('Total is ZERO. Please select valid quantity');
        //     $('#items_error').removeAttr('style');
        //     fnDisableButton();
        //     e.preventDefault();
        //     return false;
        // }

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

            var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
            var unitPrice = float_format(currentRow[DO_ROW_INDEX_PRICE].value);

            
            var refer_doc = currentRow[DO_ROW_INDEX_REFER_NO].value;
            var refer_line = currentRow[DO_ROW_INDEX_REFER_LINE].value;

            if (quantity == 0 || unitPrice == 0) {
                is_valid = false;
                invalid_data_list.push({
                    ln: currentLabel[DO_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
                    refer_doc: refer_doc,
                    refer_line: refer_line,
                    quantity: currentRow[DO_ROW_INDEX_ITEM_QTY].value,
                    unitPrice: currentRow[DO_ROW_INDEX_PRICE].value,
                });
            }

            // allTableData.push({
            //     ln: currentLabel[DO_LABEL_INDEX_LINE_NUMBER].textContent.trim(),
            //     refer_doc: refer_doc,
            //     refer_line: refer_line,
            //     quantity: currentRow[DO_ROW_INDEX_ITEM_QTY].value,
            //     unitPrice: currentRow[DO_ROW_INDEX_PRICE].value,
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

        // var is_valid = true;
        // var is_duplicate = false;
        // let msg = '';
        // $('#dynamic-table tr.gradeX:visible').each(function () {
        //     var currentRow = $(this).find('input');
        //     var quantity = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
        //
        //     if (quantity == 0) {
        //         is_valid = false;
        //     }
        //
        //     // checking duplicate
        //     var currentRowSelect = $(this).find('select');
        //     let rowIndex = parseInt($(this).closest('tr').find('label:first').text())-1;
        //     let check_refer_number = '';
        //     let check_refer_line = '';
        //     currentRowSelect.each(function (selectIndex, selectValues) {
        //         if (selectIndex == DO_SELECT_INDEX_REF_NUMBER) {
        //             check_refer_number = $(this).val();
        //         }
        //         if (selectIndex == DO_SELECT_INDEX_REFER_LINE) {
        //             check_refer_line = $(this).val();
        //         }
        //     });
        //
        //     // if can not get value from group down we will get form imput hidden
        //     if (check_refer_number == '' || check_refer_line == '' ) {
        //         currentRow.each(function (selectIndex, selectValues) {
        //             if (selectIndex == DO_ROW_INDEX_REFER_NO) {
        //                 check_refer_number = $(this).val();
        //             }
        //             if (selectIndex == DO_ROW_INDEX_REFER_LINE) {
        //                 check_refer_line = $(this).val();
        //             }
        //         });
        //     }
        //
        //     // if (check_refer_number != '' && check_refer_line != '' ) {
        //     //     $('#dynamic-table tr.gradeX').each(function(){
        //     //         let selects = $(this).closest('tr').find('select');
        //     //         let inputs = $(this).closest('tr').find('input');
        //     //         let loop_row_index = parseInt($(this).closest('tr').find('label:first').text())-1;
        //     //         if(loop_row_index != rowIndex) {
        //     //             let selected_refer_number;
        //     //             let selected_refer_line;
        //     //             selects.each(function (selectIndex, selectValues) {
        //     //                 if (selectIndex == DO_SELECT_INDEX_REF_NUMBER) {
        //     //                     selected_refer_number = $(this).val();
        //     //                 }
        //     //                 if (selectIndex == DO_SELECT_INDEX_REFER_LINE) {
        //     //                     selected_refer_line = $(this).val();
        //     //                 }
        //     //             });
        //     //             if (selected_refer_number != '' || selected_refer_line != '' ) {
        //     //                 inputs.each(function (selectIndex, selectValues) {
        //     //                     if (selectIndex == DO_ROW_INDEX_REFER_NO) {
        //     //                         selected_refer_number = $(this).val();
        //     //                     }
        //     //                     if (selectIndex == DO_ROW_INDEX_REFER_LINE) {
        //     //                         selected_refer_line = $(this).val();
        //     //                     }
        //     //                 });
        //     //             }
        //     //             if(selected_refer_number == check_refer_number && selected_refer_line == check_refer_line){
        //     //                 let msg = 'Duplicate entry at row number '+(loop_row_index+1)+'<br/>Refer no: '+check_refer_number+'<br/>Refer ln: '+check_refer_line;
        //     //                 $('#items_error').html(msg);
        //     //                 $('#items_error').removeAttr('style');
        //     //                 fnDisableButton();
        //     //                 is_duplicate = true;
        //     //                 e.preventDefault();
        //     //                 return false;
        //     //             }
        //     //         }
        //     //     });
        //     // }
        // });
        // if (!is_valid) {
        //     $('#items_error').text('Please select valid quantity or unit price');
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
        //         qty = float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value);
        //         currentRow[DO_ROW_INDEX_ITEM_QTY].value = qty;
        //     });
        // } else {
        //     e.preventDefault();
        //     return false;
        // }
    });
});

var origin_country_code;
var origin_country_id;

$('.btnOpenCountryDialog').on('click', function () {
    currentRow = $(this).closest('tr').find('input');
    origin_country_code = currentRow[DO_ROW_INDEX_COUNTRY_ORG_CD].id;
    origin_country_id = currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].id;
});

$('#btnAddCountries').on('click', function () {
    var table = $('#tblDataCountry').DataTable();
    var country_selected = table.$(".call-radio:checked", {"page": "all"});
    $('#' + origin_country_code).val(country_selected[0].value);
    $('#' + origin_country_id).val(country_selected[0].id);
    $(this).attr('data-dismiss', 'modal');
    $('input[type=radio]').each(function () {
        $(this).prop('checked', false);
    });
});

function fnSearchDOInvocieItem() {
    var customerID = $('#hdCustomerId').val();
    var exclude_item_array = [];
    var exclude_item_list = {};
    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[DO_ROW_INDEX_ITEM_ID].value);
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
        "order": [[3, "desc"], [1, "asc"]],
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
            {"data": "code", "sClass": "text-left"},
            {"data": "item_name", "sClass": "text-left"},
            {"data": "refer_number", "sClass": "text-left"},
            {"data": "refer_line", "sClass": "text-left"},
            {"data": "supplier_code", "sClass": "text-left"},
            {"data": "location_code", "sClass": "text-left"},
            {"data": "category", "sClass": "text-left"},
            {"data": "sales_price", "sClass": "text-right"},
            {"data": "currency_code", "sClass": "text-left"},
            {"data": "location_id", "className": "hide_column"},
            {"data": "currency_id", "className": "hide_column"},
            {"data": "line_id", "className": "hide_column"},
            {"data": "unit", "className": "hide_column"},
            {"data": "supplier_id", "className": "hide_column"},
            {"data": "order_qty"},
            {"data": "delivery_qty"},
            {"data": "customer_po_no"},
            {"orderable": false,
             "data": null,
             "render": function (data, type, row, meta) {
                return '<input type="checkbox" name="choices" id="' + row.line_id + '"'
                    + 'class="call-checkbox" value="' + row.sales_price + '"></td>';
                }
            },
            {"data": "stock_quantity", "className": "hide_column"},
            {"data": "location_item_quantity", "className": "hide_column"
            },
        ]
    });
}

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

        var id_cus = $('#id_customer').val();
        var rate_type = 3;
        var curr_to = $('#customer_currency_id').val();
        if (id_cus > 0){
            recort_rate(curr_to,date_rate_1,rate_type);
        }
    }
});



function load_cuss(){
    var date_rate = $("#id_document_date").val();
    var id_cus = $('#id_customer').val();
    var rate_type = 3;
    //$('#copy_date_doc').select();
    if (id_cus) {
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
                $('#hdCustomerId').val(data.data[0].id);
                $('#customer_currency_id').val(data.data[0].currency_id);
                $('#customer_currency_code').val(data.data[0].currency_code);
                $('#name_currency').val(data.data[0].currency_name);
                $('#do_total').text("Total (" + data.data[0].currency_symbol + ') : ');
                $('#do_subtotal').text("Subtotal (" + data.data[0].currency_symbol + ') : ');
                $('#do_tax').text("Tax (" + data.data[0].currency_symbol + ') : ');
                $('#id_payment_term').val(data.data[0].payment_term);
                $('#payment_mode').val(data.data[0].payment_code_id).trigger('change');
                recort_rate(data.data[0].currency_id,date_rate,rate_type);
                $('#id_tax').val(data.data[0].tax_id).trigger('change');
                $('#id_attention').val(data.data[0].consignee_name);
                $('#id_name').val(data.data[0].consignee_company_name);
                $('#id_address').val(data.data[0].consignee_address);
                $('#id_phone').val(data.data[0].consignee_phone);
                $('#id_currency_symbol').val(data.data[0].currency_symbol);
                $('#contact_id').val(data.data[0].contact_id);

                $('#customer_name').editable('destroy');
                $('#cust_info1').editable('destroy');
                $('#cust_info2').editable('destroy');
                $('#customer_name').text(data.data[0].customer_name);
                $('#cust_info1').text(data.data[0].address);
                $('#cust_info2').text(data.data[0].email);
                $('#customer_name').attr('data-pk', data.data[0].id);
                $('#cust_info0_h').val(data.data[0].customer_name);
                $('#cust_info1_h').val(data.data[0].address);
                $('#cust_info2_h').val(data.data[0].email);
                fillCustomerInfo(data.data[0].id);
                $('#id_distribution_code').val(data.data[0].distribution_code_id).trigger('change');;
                }
                //$('#copy_date_doc').select();
            }
        });
    }
}

var refer_numbers = [];
function load_refer_numbers(){
    var id_cus =0;
    if( $('#id_customer').val() >0){
        id_cus =  $('#id_customer').val();
    }
    $('#load_so_by_cust').empty();
    refer_numbers = [];
    $.ajax({
        type: "GET",
        url: "/orders/do_by_all_so_as_json/"+id_cus+'/',
        dataType: 'JSON',
        success: function(data){
        if (data.data.length > 0){
            refer_numbers = data.data
            }
        }

    });
}

function load_part_numbers(){
    var id_cus =0;
    if( $('#id_customer').val() >0){
        id_cus =  $('#id_customer').val();
    }
    $('#load_so_by_cust').empty();
    refer_numbers = [];
    $.ajax({
        type: "GET",
        url: "/orders/do_by_all_so_as_json/"+id_cus+'/',
        dataType: 'JSON',
        success: function(data){
            if (data.data.length > 0){
                refer_numbers = data.data
            }
            initiateRefNumber('#dynamic-table tr.gradeX:last');
        }

    });
}

function tabAddRow(rowIndex, code_pressed, copy_refer_number) {
    if (code_pressed == '9') {
        var rowCount = ($('#dynamic-table tr.gradeX')).length;
        if (rowIndex == rowCount) {
            $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').find('.appendrow').trigger('click');
            setTimeout(() => {
                rowCount = ($('#dynamic-table tr.gradeX')).length;
                rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + rowCount + ')').attr('data-row_index');
                $('#id_formset_item-' + rowIndex + '-ref_number').focus();
                // $('#id_select-' + rowIndex + '-ref_number').select2('open');
            }, 300);
        } else {
            rowIndex = $('#dynamic-table tr.gradeX:nth-child(' + (rowIndex+1) + ')').attr('data-row_index');
            let refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').val();
            // if (refer_number == undefined) {
            //     refer_number = $('#id_formset_item-' + (rowIndex) +'-ref_number').text();
            // } 
            // if (refer_number == undefined || refer_number == '') {
            //     setTimeout(() => {
            //         copy_refer_number = getRefNumberDO(copy_refer_number, storeCopyRefNumberData);
            //         if ( copy_refer_number != '') {
            //             $('#id_select-' + (rowIndex) + '-ref_number').val(copy_refer_number).trigger('change');
            //             $('#id_select-' + (rowIndex) + '-ref_number').select2('close');
            //         }
            //     }, 300);
            // } else {
                setTimeout(() => {
                    $('#id_formset_item-' + rowIndex + '-ref_number').focus();
                    // $('#id_select-' + rowIndex + '-ref_number').select2('open');
                }, 300);
            // }
        }
    }
}

function highLightMandatory(rowCheck) {
    if ($('#id_formset_item-' + rowCheck +'-ref_number').val() == '' ||
        $('#id_formset_item-' + rowCheck +'-ref_number').val() == null ||
        $('#id_formset_item-' + rowCheck +'-ref_number').val() == undefined) {
        $('#id_formset_item-' + rowCheck +'-ref_number').addClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-ref_number').removeClass('highlight-mandatory');
    }

    if ($('#id_formset_item-' + rowCheck +'-refer_line').val() == '') {
        $('#id_formset_item-' + rowCheck +'-refer_line').addClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-refer_line').removeClass('highlight-mandatory');
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-quantity_do').val()) > 0) {
        $('#id_formset_item-' + rowCheck +'-quantity_do').removeClass('highlight-mandatory');
    } else {
        $('#id_formset_item-' + rowCheck +'-quantity_do').addClass('highlight-mandatory');
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-price').val()) > 0 ) {
        $('#id_formset_item-' + rowCheck +'-price').removeClass('highlight-mandatory');
     } else {
         $('#id_formset_item-' + rowCheck +'-price').addClass('highlight-mandatory');
     }
}

function getFirstFieldInvalid(rowCheck) {
    var idFirstInvalid = '';
    if ($('#id_formset_item-' + rowCheck +'-ref_number').val() == '' ||
        ($('#id_formset_item-' + rowCheck +'-ref_number').val() == null && $('#id_formset_item-' + rowCheck +'-ref_number').is(':visible'))) {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-ref_number';
        return idFirstInvalid;
    }

    if ($('#id_formset_item-' + rowCheck +'-refer_line').val() == '') {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-refer_line';
        return idFirstInvalid;
    }

    if ( float_format($('#id_formset_item-' + rowCheck +'-quantity_do').val()) <= 0) {
        idFirstInvalid = '#id_formset_item-' + rowCheck +'-quantity_do';
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
            if ($('#company_is_inventory').val() == 'True' && selectIndex == DO_SELECT_INDEX_LOCATION) {
                locationSelect2($(this)[0].id, location_data);
                setTimeout(() => {
                    if($selected) {
                        $(this).val($selected[3]).trigger('change');
                    }
                }, 1000);
            }
            
            if (selectIndex == DO_SELECT_INDEX_LOCATION) {
                // $(this).select2();
                $(this).on("select2:close", function (event) {
                    // $(this).closest('tr').find('select:eq('+DO_SELECT_INDEX_REF_NUMBER+')').focus();
                    $(this).closest('tr').find('input:eq('+DO_ROW_INDEX_ITEM_QTY+')').focus();
                });
            }
            
            if (selectIndex == DO_SELECT_INDEX_COUNTRY_CODE) {
                if ($(this).data('select2')) {
                    $(this).select2('destroy');
                }
                $(this).empty();
                var options = '';
                // var options = '<option data-code_data="" value="0">----</option>';
                for (var i in country_list) {
                    options += "<option data-code_data='"+JSON.stringify(country_list[i])+"' value='"+country_list[i].id+"'>"+country_list[i].code+"</option>";
                }

                $(this).html(options);

                $(this).select2({
                });

                $(this).on("select2:open", function (event) {
                    prefill_select2(event);
                });
                if($selected == null) {
                    $(this).on("select2:select", function () {
                        $select = $(this).closest('select');
                        currentRow = $(this).closest('tr').find('input');

                        selected_item = $select.find('option:selected').data('code_data');

                        currentRow[DO_ROW_INDEX_COUNTRY_ORG_CD].value = selected_item.name;
                        currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].value = selected_item.id;
                    });
                }

                $(this).on("select2:close", function () {
                    currentRow = $(this).closest('tr').find('input');
                    currentRow[DO_ROW_INDEX_CARTON_NO].focus();
                });
                $(this).prop('disable', false);
                $(this).select2('enable');
                if($selected) {
                    $(this).val($selected[2]).trigger('change');
                }
            }
        });
    });

}


function refreshCurrentRow(currentRow, currentLabel) {
    let last_amount = float_format($('#'+currentLabel[DO_LABEL_INDEX_AMOUNT].id).text());
    let new_amount = 0;
    calculateDOTotal(last_amount, new_amount);

    currentRow[DO_ROW_INDEX_ITEM_QTY].value = '0.00';
    currentRow[DO_ROW_INDEX_PRICE].value = '0.000000';
    currentLabel[DO_LABEL_INDEX_CUSTOMER_PO].textContent = '';
    currentLabel[DO_LABEL_INDEX_ITEM_CODE].textContent = '';
    currentLabel[DO_LABEL_INDEX_ITEM_NAME].textContent = '';
    // currentLabel[DO_LABEL_INDEX_PRICE].textContent = '0.000000';
    currentLabel[DO_LABEL_INDEX_CURRENCY_CODE].textContent = '';
    currentLabel[DO_LABEL_INDEX_CATEGORY].textContent = '';
    currentLabel[DO_LABEL_INDEX_SUPPLIER_CODE].textContent = '';
    currentLabel[DO_LABEL_INDEX_ORDER_QTY].textContent = '';
    currentLabel[DO_LABEL_INDEX_DELIVERY_QTY].textContent = '';
    currentLabel[DO_LABEL_INDEX_UOM].textContent = '';
    currentLabel[DO_LABEL_INDEX_AMOUNT].textContent = '0.00';

    if ($('#company_is_inventory').val() == 'True'){
        let row = $(currentRow[0]).parent().parent().attr('data-row_index');
        location_choice = '#id_formset_item-' + row + '-location';
        $(location_choice).val('').trigger('change');
    }
}


function doEssentials(currentRow){
    //Change currency
    var currency_id = parseInt($('#customer_currency_id').val());
    // var currency_name = $('#customer_currency_code').val();
    var arrItems = [];
    // $('#dynamic-table tr.gradeX').each(function () {
    //     currentRow = $(this).closest('tr').find('input');
    //     arrItems.push({
    //         item_id: currentRow[DO_ROW_INDEX_ITEM_ID].value,
    //         currency_id: currentRow[DO_ROW_INDEX_CURRENCY_ID].value
    //     });
    // });

    if (currentRow[DO_ROW_INDEX_CURRENCY_ID].value != '' && currency_id != '') {
        arrItems.push({
            item_id: currentRow[DO_ROW_INDEX_ITEM_ID].value,
            currency_id: currentRow[DO_ROW_INDEX_CURRENCY_ID].value
        });
        changeCurrency_2(arrItems, currency_id, currentRow);
    }
    fnEnableButton();
    // set customer code
    // if(allVals.length > 0) {
    //     $('#form_customer_code').val(allVals[0].customer_code);
    // }
    // change customer according to the sales order
    // var e = jQuery.Event("keypress");
    // e.which = 13;
    // $("#form_customer_code").trigger(e);

    // $('#dynamic-table tr.gradeX:first').each(function () {
    //     if($last_quantity === ''){
    //         $last_quantity = $(this).find("input[name*='quantity_do']");
    //     }
    // });

    // $('#dynamic-table tr.gradeX:last').each(function () {
    //     $quantity = $last_quantity[0].id;
    //     $quantity = $quantity.split('-');
    //     $quantity[1] = (parseInt($quantity[1]) == 0) ? 0: parseInt($quantity[1]) + 1;
    //     $quantity = $("#" + $quantity.join('-'));
    //     $last_quantity = $(this).find("input[name*='quantity_do']");

    //     // fix bug wrong quantity focus when tab
    //     // if ($quantity.length) {
    //     //     setTimeout(function() { $quantity.select();}, 300);
    //     // }
    //     calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);
    // });
    // calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);
}

// $(document).ready(function () {
//     $('#dynamic-table tr.gradeX:last').each(function () {
//         calculateDOTotal('#dynamic-table tr.gradeX', DO_ROW_INDEX_ITEM_QTY, DO_ROW_INDEX_PRICE, DO_ROW_INDEX_AMOUNT);
//     });
// })

function recort_rate(curr_to,date_rate_1,rate_type) {
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
                $('#id_exchange_rate_value').val('');
            } else {
                fnEnableButton();
                $('#exchange_rate_fk_id').val(data[0].id);
                $('#id_exchange_rate_date').val(data[0].exchange_date);
                $('#id_exchange_rate').val(data[0].rate);
                $('#id_tax_exchange_rate').val(data[0].rate);
                $('#id_exchange_rate_value').val(data[0].rate);
            }
        }
    });
}

function WarnQtyExceded(max_qty, elm, msg) {
    pop_ok_dialog("Invalid Item Quantity",
        msg,
        function(){

            setTimeout(function() {
                // $(elm).val(comma_format(max_qty)).trigger('change');
                $(elm).val(comma_format(max_qty));
                $(elm).select();
                }, 300);

            $('#dynamic-table tr.gradeX').each(function () {
                $(elm).closest('tr').find('input').removeAttr('disabled');
            });
            $(elm).closest('tr').removeAttr('style');
            fnEnableButton();
    });
}

$('#tax_currency').change(function(){
    pop_info_dialog("Error", "Changing this field is not allowed !", "error");
    $(this).val(tax_curr);
});

function getAllItemQty(){
    var AllItemQty = [];
    $('#dynamic-table tr.gradeX').each(function (rowIndex) {
        var currentRow = $(this).closest('tr').find('input');
        var currentLabel = $(this).closest('tr').find('label');
        if (currentRow[DO_ROW_INDEX_ITEM_ID].value){
            AllItemQty.push({
                id: $('#id_formset_item-' + rowIndex + '-id').val(),
                ln: currentRow[DO_ROW_INDEX_LINE_NUMBER].value,
                refer_line: currentRow[DO_ROW_INDEX_REFER_LINE].value,
                refer_doc: currentRow[DO_ROW_INDEX_REFER_NO].value,
                item_id: currentRow[DO_ROW_INDEX_ITEM_ID].value,
                ord_qty: float_format(currentRow[DO_ROW_INDEX_ORDER_QTY].value),
                qty_dlv: float_format(currentRow[DO_ROW_INDEX_DELIVERY_QTY].value),
                qty: float_format(currentRow[DO_ROW_INDEX_ITEM_QTY].value),
                order_id: $(currentLabel[1]).data('code_data')
            });
        }
    });
    return AllItemQty;
}

function getItemQty(refer_doc,item_id,doc_item){
    var OutstandingQty = 0;
    var ItemQty = 0;
    for (var i in doc_item) {
        if ((doc_item[i]['refer_doc']==refer_doc) && (doc_item[i]['item_id']==item_id)){
            OutstandingQty += float_format(doc_item[i]['ord_qty']) - float_format(doc_item[i]['qty_dlv']);
            ItemQty += doc_item[i]['qty'];
        }
    }
    return {
        OutstandingQty : OutstandingQty,
        ItemQty : ItemQty
    };
}

function initiateCountryCode(){
    $.ajax({
        type: "GET",
        url: "/countries/country_list/",
        dataType: 'JSON',
        success: function(data){
            if (data.length > 0){
                for (i in data) {
                    country_list.push({
                        id: data[i].id,
                        code: data[i].code,
                        name: data[i].name});
                }

                let rowCount = 0;
                $('#dynamic-table tr.gradeX').each(function () {
                    currentRow = $(this).closest('tr').find('input');
                    var options = '<option data-code_data="" value="0">----</option>';
                    for (var i in country_list) {
                        options += "<option data-code_data='"+JSON.stringify(country_list[i])+"' value='"+country_list[i].id+"'>"+country_list[i].code+"</option>";
                    }

                    $('#id_select_country_code-'+rowCount+'-country_code').empty();
                    $('#id_select_country_code-'+rowCount+'-country_code').html(options);
                    $('#id_select_country_code-'+rowCount+'-country_code').select2({

                    });
                    $('#id_select_country_code-'+rowCount+'-country_code').on("select2:open", function( event ){
                        prefill_select2(event);
                    });
                    $('#id_select_country_code-'+rowCount+'-country_code').val(currentRow[DO_ROW_INDEX_COUNTRY_ORG_ID].value).trigger("change");

                    // $('#id_select_country_code-'+rowCount+'-country_code').on('select2:close', function( event){
                    //     currentRow[DO_ROW_INDEX_CARTON_NO].focus();
                    // })
                    rowCount++;
                });
            }
        }
    });

}
