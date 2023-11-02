/**
 * Created by tho.pham on 10/25/2016.
 */

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
}

$('#add_more_code').click(function () {
    cloneMore('div.table-code:last', 'formset_code');
});
function cloneMore(selector, type) {
    var display = $(selector).css("display")
    if (display == 'none') {
        $(selector).removeAttr("style")
    }
    else {
        var total = $('#id_' + type + '-TOTAL_FORMS').val();
        var newElement = $(selector).clone(true);
        newElement.removeAttr("style")
        newElement.find(':input').each(function () {
            var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        });
        newElement.find('label').each(function () {
            var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
            $(this).attr('for', newFor);
        });
        total++;
        $('#id_' + type + '-TOTAL_FORMS').val(total);
        $(selector).after(newElement);
    }
}

function checkDisplay() {
    var request_method = $('#request_method').val();
    if (request_method == 'GET') {
        if ($('#id_formset_code-TOTAL_FORMS').val() > 1) {
            $('div.table-code:last').remove();
            $('#id_formset_code-TOTAL_FORMS').val($('#id_formset_code-TOTAL_FORMS').val() - 1);
        } else {
            $('div.table-code:last').css("display", "none");
        }
        if ($('#id_formset_item-TOTAL_FORMS').val() > 0) {
            $('#dynamic-table tr.gradeX:last').remove();
            $('#id_formset_item-TOTAL_FORMS').val($('#id_formset_item-TOTAL_FORMS').val() - 1);
            $('#items_error').css("display", "none");
        } else {
            $('#dynamic-table tr.gradeX:last').css("display", "none");
            $('#items_error').removeAttr('style');
        }
    } else if (request_method == 'POST') {
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

$(document).on('click', "[class^=removerow-code]", function () {
    if ($('#id_formset_code-TOTAL_FORMS').val() == 1) {
        var total = $('#id_formset_code-TOTAL_FORMS').val();
        $('div.table-code:last').find(':input').each(function () {
            var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
        });
        $(this).parents("div.table-code").css("display", "none")
    } else {
        var minus = $('input[name=formset_code-TOTAL_FORMS]').val() - 1;
        $('#id_formset_code-TOTAL_FORMS').val(minus);
        $(this).parents("div.table-code").remove();
        var i = 0;
        $('div.table-code').each(function () {
            var $tds = $(this).find('input');
            var label = $tds[0].name;
            var value = $tds[1].name;
            if (label.replace(/[^\d.]/g, '') == 0) {
                i++;
            } else {
                for (i; i < minus; i++) {
                    $tds[0].name = label.replace(/\d+/g, i);
                    $tds[0].id = 'id_' + $tds[0].name;
                    $tds[1].name = value.replace(/\d+/g, i);
                    $tds[1].id = 'id_' + $tds[1].name;
                    i++;
                    break;
                }
            }
        });
    }
});

$(document).ready(function () {
    $('#id_document_number').attr('required', 'required');
    $('#id_document_number').removeAttr('readonly');
    checkDisplay();
    $('#tblDataCountry').dataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[1, "desc"], [0, "desc"]]
    });
});

$('#btnSave').on('click', function () {
    var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
    if (countRowVisible == 0) {
        $('#items_error').removeAttr('style');
        $('#btnPrint').attr('disabled', true);
        $('#btnSave').attr('disabled', true);
        $('#btnSend').attr('disabled', true);
        $('#btnSendForEdit').attr('disabled', true);
    }
});

$('#btnSend').on('click', function () {
    var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
    if (countRowVisible == 0) {
        $('#items_error').removeAttr('style');
        $('#btnPrint').attr('disabled', true);
        $('#btnSave').attr('disabled', true);
        $('#btnSend').attr('disabled', true);
        $('#btnSendForEdit').attr('disabled', true);
    }
});

function fnSearchDOInvocieItem() {
    // var data = $('#search_input').val();
    var customerID = $('#hdCustomerId').val();
    var exclude_item_array = [];
    var exclude_item_list = {};
    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[3].value);
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
        "order": [[1, "desc"], [0, "desc"]],
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
            {"data": "order_qty"},
            {"data": "delivery_qty"},
            {"data": "customer_po_no"},
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

$('#btnOpenItemDialog').on('click', function () {
    var dataTable = $('#tblData').dataTable();
    dataTable.fnClearTable(this);
    fnSearchDOInvocieItem();
});

function loadCustomerInfo(hdCustomerId) {
    $.fn.editable.defaults.mode = 'inline';

    //make status editable
    $('#customer_name').editable({
        type: 'text',
        pk: hdCustomerId,
        url: '/orders/change_customer/' + hdCustomerId + '/',
        title: 'Enter customer name',
        success: function (response, newValue) {
            if (!response) {
                return "Unknown error!"
            }
            if (response.success === false) {
                return respond.msg;
            }
        }
    });

    $('#customer_address').editable({
        type: 'text',
        pk: hdCustomerId,
        url: '/orders/change_customer/' + hdCustomerId + '/',
        title: 'Enter customer address',
        success: function (response, newValue) {
            if (!response) {
                return "Unknown error!"
            }
            if (response.success === false) {
                return respond.msg;
            }
        }
    });

    $('#customer_email').editable({
        type: 'text',
        pk: hdCustomerId,
        url: '/orders/change_customer/' + hdCustomerId + '/',
        title: 'Enter customer email',
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

var hdCustomerId = $('#hdCustomerId').val();
loadCustomerInfo(hdCustomerId);

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
            $('#id_tax option:not(:selected)').attr('disabled', true);
            // load tax again
            var taxid = parseInt($('#id_tax').val());
            if (isNaN(taxid)) {
                $('#id_tax_amount').val(0);
                $('#id_total').val(parseFloat($('#id_tax_amount').val()) - parseFloat($('#id_discount').val()) + parseFloat($('#id_subtotal').val()));
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
                        // var tax_amount = (parseFloat(json) * parseFloat($('#id_subtotal').val())) / 100;
                        // $('#id_tax_amount').val(tax_amount.toFixed(6));
                        // var total = parseFloat($('#id_subtotal').val()) + tax_amount - parseFloat($('#id_discount').val());
                        // $('#id_total').val(total.toFixed(6));
                        $('#tax_rate').text(parseFloat(json) / 100);
                    }
                });
            }
            $('#id_currency').find('option').removeAttr('selected');
            $('#id_currency').find('option').removeAttr('disabled');
            $('#id_currency option[value=' + json['currency_id'] + ']').attr('selected', 'selected');
            $('#id_currency').val(json['currency_id']);
            $('#id_currency option:not(:selected)').attr('disabled', true);
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

$("#form_customer_code").keypress(function (e) {
    if (e.which == 13) {
        e.preventDefault();
        callback();
    }
});
$('#btnSearchCustomer').on('click', function () {
    var datatbl = $('#customer-table').DataTable();
    datatbl.destroy();
    $('#customer-table').dataTable({
        "iDisplayLength": 5,
        "bLengthChange": false,
        "order": [[0, "asc"]],
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
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="choices" id="' +
                        full.id + '" class="call-checkbox" value="' + full.id + '">';
                }
            }
        ]
    });
});

$('#btnCustomerSelect').on('click', function () {
    var customer_select_id = $("input[name='choices']:checked").attr('id');

    $('#hdCustomerId').val(customer_select_id);

    $('#id_currency option[value=' + customer_select_id + ']').attr('selected', 'selected');

    var nRow = $("input[name='choices']:checked").parents('tr')[0];
    var jqInputs = $('td', nRow);
    $("#form_customer_code").val(jqInputs[0].innerText);

    $(this).attr('data-dismiss', 'modal');
    callback();
});

$('#btnAddItems').on('click', function () {
    var allVals = [];
    var table = $('#tblData').DataTable();
    var rowcollection = table.$(".call-checkbox:checked", {"page": "all"});
    rowcollection.each(function (index, elem) {
        var row = table.row('#' + elem.id).data();
        allVals.push({
            id: row.item_id, //Item ID
            price: $(elem).val(),
            item_code: row.code, //Item Code
            name: row.item_name, //Item Name
            refer_number: row.refer_number,
            refer_line: row.refer_line,
            supplier_code: row.supplier_code,
            location_code: row.location_code,
            category: row.category,
            unit_price: row.sales_price,
            currency: row.currency_code,
            location_id: row.location_id,
            currency_id: row.currency_id,
            uom: row.unit,
            supplier_id: row.supplier_id,
            order_quantity: row.order_qty,
            delivery_quantity: row.delivery_qty,
            customer_po_no: row.customer_po_no
        });
        table.row('#' + elem.id).node().setAttribute("style", "display: none");
    });
    if (allVals.length > 0) {
        cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
        $('input[checked=checked]').each(function () {
            $(this).removeAttr('checked');
        });
        calculateTotal();
    }
    $(this).attr('data-dismiss', 'modal');
    $('#items_error').css('display', 'none');
    //Change currency
    var currency_id = parseInt($('#id_currency option:selected').val());
    var currency_name = $('#id_currency option:selected').text();
    var arrItems = [];
    $('#dynamic-table tr.gradeX').each(function () {
        currentRow = $(this).closest('tr').find('input');
        arrItems.push({
            item_id: currentRow[3].value,
            currency_id: currentRow[10].value
        });
    });
    fnEnableButton();
    // validationItemsFormset();
});

function cloneMore(selector, type, allVals) {
    var display = $(selector).css("display");
    var order_type = $('#order_type').text();
    var sum = 0;
    var i = 0;
    var item_id = 0;
    // if no item in orderitem table
    if (display == 'none') {
        //show first row of table and set Item, Price of dialog
        $(selector).removeAttr("style")
        // $(selector).find("option").each(function () {
        //     $(this).removeAttr('selected');
        //     if ($(this).val() == allVals[i].id) {
        //         $(this).prop("selected", true);
        //         // $(this).attr("selected", true);
        //     }
        // });
        $(selector).find('label').each(function () {
            var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        });
        findInput = $(selector).find('input');
        location_choice = '#' + $(selector).find('select')[0].id;
        currentLabel = $(selector).closest('tr').find('label');
        //add value to Input
        findInput[0].value = 1;
        findInput[1].value = allVals[i].item_code; //Item Code
        findInput[2].value = allVals[i].name; //Item Name
        findInput[3].value = allVals[i].id; // Item ID
        findInput[4].value = allVals[i].customer_po_no; // Item ID
        findInput[5].value = allVals[i].order_quantity;
        findInput[6].value = parseFloat(allVals[i].unit_price).toFixed(6);
        findInput[9].value = allVals[i].currency;
        findInput[10].value = allVals[i].currency_id;
        findInput[11].value = allVals[i].category;
        findInput[12].value = allVals[i].supplier_code;
        findInput[13].value = allVals[i].supplier_id;
        if (allVals[i].location_id != 'None') {
            $(location_choice).find('option[value="' + allVals[i].location_id + '"]').prop('selected', true);
        }
        findInput[14].value = allVals[i].refer_number;
        findInput[15].value = allVals[i].refer_line;
        var order_quantity = parseFloat(allVals[i].order_quantity);
        findInput[16].value = order_quantity;
        findInput[17].value = allVals[i].delivery_quantity;
        findInput[18].value = allVals[i].uom;

        currentLabel[0].textContent = findInput[0].value; // Line Number
        currentLabel[1].textContent = findInput[1].value; // Item Code
        currentLabel[2].textContent = findInput[2].value; // Item Name
        currentLabel[3].textContent = findInput[6].value; // Price
        currentLabel[5].textContent = findInput[9].value; // Currency Code
        currentLabel[6].textContent = findInput[11].value; // Part Group
        currentLabel[7].textContent = findInput[12].value; // Supplier Code
        currentLabel[8].textContent = findInput[14].value; // Refer Number
        currentLabel[9].textContent = findInput[15].value; // Refer Line
        currentLabel[10].textContent = findInput[16].value; // Order Quantity
        currentLabel[11].textContent = findInput[17].value; // Delivery Quantity
        currentLabel[12].textContent = findInput[18].value; // UOM
        // calculate total, subtotal
        sum += parseInt(findInput[8].value);
        $('#id_subtotal').val(sum);
        if (isNaN(sum)) {
            sum = 0;
            $('#id_subtotal').val(0);
            $('#id_total').val(0);
        }
        if ($('#id_tax_amount').val()) {
            var tax_rate = parseFloat($('#tax_rate').text());
            $('#id_tax_amount').val(parseFloat(sum * tax_rate).toFixed(6));
            sum += parseFloat($('#id_tax_amount').val());
        }
        if ($('#id_discount').val()) {
            sum -= parseFloat($('#id_discount').val());
        }
        $('#id_total').val(sum);
        //if selected items > 1
        i = 1;
    }
    $('#btnSave').removeAttr('disabled');
    for (i; i < allVals.length; i++) {

        if (allVals[i].id != 0) {
            var newElement = $(selector).clone(true);
            var total = $('#id_' + type + '-TOTAL_FORMS').val();
            newElement.removeAttr("style")
            newElement.find(':input').each(function () {
                var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
            });
            newElement.find('label').each(function () {
                var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
            });
            //Set selected items of dialog to Item Column
            // var value = allVals[i].id;
            // newElement.find("option").each(function () {
            //     $(this).removeAttr('selected');
            //     if ($(this).val() == value) {
            //         $(this).attr("selected", true);
            //     }
            // });
            //Set selected price of dialog to Price Column
            var a = newElement.find('input');
            var clone_location = '#' + newElement.find('select')[0].id;
            currentRow = newElement.closest('tr').find('label');
            if (a.length > 1) {
                a[0].value = parseInt($(selector).find('input')[0].value) + 1;
                a[1].value = allVals[i].item_code;
                a[2].value = allVals[i].name;
                a[3].value = allVals[i].id;
                a[4].value = allVals[i].customer_po_no;
                a[5].value = allVals[i].order_quantity - allVals[i].delivery_quantity;
                a[6].value = parseFloat(allVals[i].unit_price).toFixed(6);
                a[9].value = allVals[i].currency;
                a[10].value = allVals[i].currency_id;
                a[11].value = allVals[i].category;
                a[12].value = allVals[i].supplier_code;
                a[13].value = allVals[i].supplier_id;
                a[14].value = allVals[i].refer_number;
                a[15].value = allVals[i].refer_line;
                var order_quantity = parseFloat(allVals[i].order_quantity);
                a[16].value = order_quantity;
                a[17].value = allVals[i].delivery_quantity;
                a[18].value = allVals[i].uom;

                currentRow[0].textContent = a[0].value; // Line Number
                currentRow[1].textContent = a[1].value; // Item Code
                currentRow[2].textContent = a[2].value; // Item Name
                currentRow[3].textContent = a[6].value; // Price
                currentRow[5].textContent = a[9].value; // Currency Code
                currentRow[6].textContent = a[11].value; // Part Group
                currentRow[7].textContent = a[12].value; // Supplier Code
                currentRow[8].textContent = a[14].value; // Refer Number
                currentRow[9].textContent = a[15].value; // Refer Line
                currentRow[10].textContent = a[16].value; // Order Quantity
                currentRow[11].textContent = a[17].value; // Delivery Quantity
                currentRow[12].textContent = a[18].value; // UOM

                sum = parseInt($('#id_subtotal').val());
                sum += parseInt(a[8].value);
                $('#id_subtotal').val(sum);
                if (isNaN(sum)) {
                    sum = 0;
                    $('#id_subtotal').val(0);
                    $('#id_total').val(0);
                }
                if ($('#id_tax_amount').val()) {
                    var tax_rate = parseFloat($('#tax_rate').text());
                    $('#id_tax_amount').val(parseFloat(sum * tax_rate).toFixed(6));
                    sum += parseFloat($('#id_tax_amount').val());
                }
                if ($('#id_discount').val()) {
                    sum -= parseFloat($('#id_discount').val());
                }
                $('#id_total').val(sum);
            }
            // newElement.find('label').each(function () {
            //     var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
            //     $(this).attr('for', newFor);
            // });
            total++;
            $('#id_' + type + '-TOTAL_FORMS').val(total);
            $(selector).after(newElement);
            if (allVals[i].location_id != 'None') {
                $(clone_location).find('option[value="' + allVals[i].location_id + '"]').prop('selected', true);
            }
        }
    }
}

$(document).on('click', "[class^=removerow]", function (event) {
    currentRow = $(this).closest('tr').find('input');
    item_id = currentRow[3].value;
    if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
        $(this).closest('tr').css("background-color", "");
        $(this).closest('tr').css('display', 'none');
        $('#id_subtotal').val(0);
        $('#id_total').val(0);
        fnDisableButton()
    } else {
        fnEnableButton();
        var minus = $('input[name=formset_item-TOTAL_FORMS]').val() - 1;
        $('#id_formset_item-TOTAL_FORMS').val(minus);
        $(this).parents("tr").remove();
    }

    $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {
        $(this).find('td').each(function (colIndex, c) {
            $.each(this.childNodes, function (i, elem) {
                if (elem.nodeName == 'INPUT' || elem.nodeName == 'LABEL' || elem.nodeName == 'SELECT') {
                    if (colIndex == 0) {
                        elem.innerHTML = rowIndex + 1;
                        elem.value = rowIndex + 1;
                    }
                    elem.attributes.name.nodeValue = elem.attributes.name.nodeValue.replace(/\d+/g, rowIndex);
                    elem.id = elem.id.replace(/\d+/g, rowIndex);
                }
            });
        });
    });
    calculateTotal();
});

// calculate subtotal and total
function calculateTotal() {
    var subtotal = 0;
    var total = 0;
    $('#dynamic-table tr.gradeX').each(function () {
        var $tds = $(this).find('input');
        var label = $(this).find('label');
        price = $tds[6].value;
        amount = $tds[5].value * price;
        $tds[8].value = parseFloat(amount.toFixed(6));
        label[4].textContent = $tds[8].value;
        subtotal += parseFloat(amount);
        $('#id_subtotal').val(subtotal.toFixed(6));
        if ($('#id_discount').val() == '' || $('#id_discount').val() == null) {
            total = subtotal + parseFloat($('#id_tax_amount').val());
        } else {
            total = subtotal + parseFloat($('#id_tax_amount').val()) - parseFloat($('#id_discount').val());
        }
        var tax_rate = parseFloat($('#tax_rate').text());
        $('#id_tax_amount').val(parseFloat(subtotal * tax_rate).toFixed(6));
        total = subtotal + parseFloat($('#id_tax_amount').val());
        $('#id_total').val(total.toFixed(6));
    });
};

var origin_country_code;
var origin_country_id;

$('.btnOpenCountryDialog').on('click', function () {
    currentRow = $(this).closest('tr').find('input');
    origin_country_code = currentRow[19].id;
    origin_country_id = currentRow[20].id;
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

// insert orderitem by DO num
function addOrderItemByDO(do_number) {
    var exclude_item_array = [];
    var exclude_item_list = {};
    var hdCustomerId = $('#hdCustomerId').val();

    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[3].value);
        }
    });
    if (exclude_item_array.length > 0) {
        exclude_item_list = JSON.stringify(exclude_item_array);
    }
    if (parseInt(hdCustomerId) == 0) {
        alert('Please enter Customer');
    } else {
        $.ajax({
            method: "POST",
            url: '/orders/get_orderitems_by_do_no/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'do_number': do_number,
                'customer_id': hdCustomerId,
                'exclude_item_list': exclude_item_list
            },
            success: function (json) {
                var allVals = [];
                $.each(json, function (i, item) {
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
                        customer_po_no: item.customer_po_no
                    });
                });
                cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
                calculateTotal();
                //Change currency
                var currency_id = parseInt($('#id_currency option:selected').val());
                var currency_name = $('#id_currency option:selected').text();
                var arrItems = [];
                $('#dynamic-table tr.gradeX').each(function () {
                    currentRow = $(this).closest('tr').find('input');
                    arrItems.push({
                        item_id: currentRow[3].value,
                        currency_id: currentRow[10].value
                    });
                });
                fnEnableButton();
                // set customer code
                $('#form_customer_code').val(json[0]['customer_code']);
                // change customer according to the sales order
                var e = jQuery.Event("keypress");
                e.which = 13;
                $("#form_customer_code").trigger(e);
            }
        });
    }
}


$('#txtDONo').on('keypress', function (e) {
    if (e.which == 13) {
        addOrderItemByDO($('#txtDONo').val());
        $('#items_error').css('display', 'none');
    }
});

//event change quantity
$('#dynamic-table tr.gradeX').each(function () {
    currentRow = $(this).closest('tr').find('input');
    currentColumn = $(this).closest('tr').find('td');
    $mainElement = '#' + currentRow[5].id; // ID of Quantity Column
    var order_type = $('#order_type').text();
    var is_generate = $('#is_generate').text();
    var order_id = $('#order_id').text();
    $($mainElement).change(function () {
        currentRow = $(this).closest('tr').find('input');
        var quantity = currentRow[5].value; // Quantity Value
        var price = currentRow[6].value; // Price Value
        var order_quantity = currentRow[18].value;
        var new_delivery_quantity = parseFloat(currentRow[5].value);
        if (quantity < 1) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The quantity of product ' + currentRow[1].value + ' must be greater than 0');
            $(this).closest('tr').attr('style', 'background-color: yellow !important');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[5]).attr('disabled', true);
            });
            fnDisableButton();
        } else if (new_delivery_quantity > order_quantity) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The number quantity to delivery is not valid.');
            $(this).closest('tr').attr('style', 'background-color: yellow !important');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[5]).attr('disabled', true);
            });
            fnDisableButton();
        } else {
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $(this).closest('tr').removeAttr('style');
            $('#items_error').css('display', 'none');
            $('#minimum_order_error').css('display', 'none');
            fnEnableButton();
        }
        calculateTotal();
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