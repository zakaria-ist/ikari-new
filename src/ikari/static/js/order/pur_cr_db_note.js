$(document).ready(function () {
    $('.lblCurrency').text($('#id_currency option:selected').text());
    $('#btnSave').on('click', function () {
        var countRowVisible = $('#dynamic-table tr.gradeX:visible').length;
        if (countRowVisible == 0) {
            $('#items_error').removeAttr('style');
            $('#btnPrint').attr('disabled', true);
            $('#btnSave').attr('disabled', true);
            $('#btnSend').attr('disabled', true);
            // $('#btnSendForEdit').attr('disabled', true);
        }
    });
    calculateTotal();
});

$(document).keypress(function (e) {
    if (e.which == 13 && !$(event.target).is("textarea")) {
        e.preventDefault();
    }

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

//Add Extra Label Value formset
$(document).ready(function () {
    checkDisplay();
    var supplier = $('#hdSupplierId').val();
    if (supplier == null) {
        $('#btnSave').attr('disabled', true);
        $('#btnSend').attr('disabled', true);
        $('#btnPrint').attr('disabled', true);
        // $('#btnSendForEdit').attr('disabled', true);
    } else {
        $('#btnSave').removeAttr('disabled');
        $('#btnSend').removeAttr('disabled');
        $('#btnPrint').removeAttr('disabled');
        // $('#btnSendForEdit').removeAttr('disabled');
    }
    $('#add_more_right').click(function () {
        cloneMore('div.table-right:last', 'formset_right');
    });
    $('#add_more_left').click(function () {
        cloneMore('div.table-left:last', 'formset_left');
    });
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
            $('#dynamic-table tr.gradeX:last').css("display", "none");
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
            var item = $('#id_formset_item-0-item_id').val();
            var quantity = $('#id_formset_item-0-quantity').val();
            var price = $('#id_formset_item-0-price').val();
            var amount = $('#id_formset_item-0-amount').val();
            if (quantity == "" && price == "" && amount == "") {
                $('#dynamic-table tr.gradeX:last').css("display", "none");
                $('#items_error').removeAttr('style');
            } else $('#items_error').css("display", "none");
        }
    }

    $(document).on('click', "[class^=removerow-left]", function () {
        if ($('#id_formset_left-TOTAL_FORMS').val() == 1) {
            var total = $('#id_formset_left-TOTAL_FORMS').val();
            $('div.table-left:last').find(':input').each(function () {
                var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
            });
            $(this).parents("div.table-left:last").css("display", "none")
        } else {
            var minus = $('input[name=formset_left-TOTAL_FORMS]').val() - 1;
            $('#id_formset_left-TOTAL_FORMS').val(minus);
            $(this).parents("div.table-left").remove();
            var i = 0;
            $('div.table-left').each(function () {
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

    $(document).on('click', "[class^=removerow-right]", function () {
        if ($('#id_formset_right-TOTAL_FORMS').val() == 1) {
            var total = $('#id_formset_right-TOTAL_FORMS').val();
            $('div.table-right:last').find(':input').each(function () {
                var name = $(this).attr('name').replace('-' + total + '-', '-' + (total - 1) + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('value');
            });
            $(this).parents("div.table-right").css("display", "none");
        } else {
            var minus = $('input[name=formset_right-TOTAL_FORMS]').val() - 1;
            $('#id_formset_right-TOTAL_FORMS').val(minus);
            $(this).parents("div.table-right").remove();
            var i = 0;
            $('div.table-right').each(function () {
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
                $('#customer_credit_limit').text(json['credit_limit']);
                loadSupplierInfo(json['id']);
                $('#id_tax').find('option').removeAttr("selected");
                $('#id_tax').find('option').removeAttr("disabled");
                $('#id_tax').find('option[value="' + json['tax_id'] + '"]').attr("selected", "selected");
                $('#id_tax').val(json['tax_id']);
                $('#id_tax option:not(:selected)').attr('disabled', true);
                // load tax again
                var taxid = parseInt($('#id_tax').val());
                if (isNaN(taxid)) {
                    $('#id_tax_amount').val(0);
                    $('#id_total').val(parseFloat($('#id_tax_amount').val()) + parseFloat($('#id_subtotal').val()));
                } else {
                    $.ajax({
                        method: "POST",
                        url: '/orders/load_tax/',
                        dataType: 'JSON',
                        data: {
                            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                            'tax_id': taxid
                        },
                        success: function (json) {
                            // var tax_amount = (parseFloat(json) * parseFloat($('#id_subtotal').val())) / 100;
                            $('#tax_rate').text(parseFloat(json) / 100);
                            // var total = parseFloat($('#id_subtotal').val()) + tax_amount;
                            // $('#id_total').val(total.toFixed(6));
                        }
                    });
                }
                $('#id_currency').find('option').removeAttr('selected');
                $('#id_currency').find('option').removeAttr('disabled');
                $('#id_currency option[value=' + json['currency_id'] + ']').attr('selected', 'selected');
                $('#id_currency').val(json['currency_id']);
                $('#id_currency option:not(:selected)').attr('disabled', true);

                $('.lblCurrency').text(json['currency_code']);
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
        var datatbl = $('#supplier-table').DataTable();
        datatbl.destroy();
        $('#supplier-table').dataTable({
            "iDisplayLength": 5,
            "bLengthChange": false,
            "order": [[0, "desc"]],
            "serverSide": true,
            "ajax": {
                "url": "/orders/suppliers_list_as_json/"
            },
            "rowId": "id",
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "name", "sClass": "text-left"},
                {"data": "term_days", "sClass": "text-left"},
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

    $('#btnSupplierSelect').on('click', function () {
        var checked_box = $("input[name='choices']:checked");
        var supplier_select_id = checked_box.attr('id');
        // set lblCurrency
        my_row = checked_box.closest('tr');
        table = $('#supplier-table').DataTable();
        var data = table.row('#' + my_row.attr('id')).data();
        $('.lblCurrency').text(data.currency_code);

        $('#hdSupplierId').val(supplier_select_id);

        $('#id_currency option[value=' + supplier_select_id + ']').attr('selected', 'selected');

        var nRow = $("input[name='choices']:checked").parents('tr')[0];
        var jqInputs = $('td', nRow);
        $("#form_supplier_code").val(jqInputs[0].innerText);

        $(this).attr('data-dismiss', 'modal');
        callback();
    });

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
                var valid = valib.String.isEmailLike(value);
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

    //return false;
    $('#btnAddItems').on('click', function () {
        var allVals = [];
        var table = $('#tblData').DataTable();
        var rowcollection = table.$(".call-checkbox:checked", {"page": "all"});
        rowcollection.each(function (index, elem) {
            var row = table.row('#' + elem.id).data();
            allVals.push({
                id: row.item_id,
                location_code: row.location_code,
                purchase_price: row.purchase_price,
                item_code: row.item_code,
                item_name: row.item_name,
                category: row.category,
                location_id: row.location_id,
                uom: row.unit,
                minimun_order: row.minimun_order,
                customer_po_no: row.customer_po_no,
                reference_id: row.refer_id,
                refer_line: row.ref_line,
                ref_number: row.ref_number,
                supplier_code: row.supplier_code,
                supplier_id: row.supplier_id,
                order_quantity: row.order_qty,
                receive_quantity: row.receive_qty,
            });
            table.row('#' + elem.id).node().setAttribute("style", "display: none");
        });
        if (allVals.length > 0) {
            cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);
            $('input[checked=checked]').each(function () {
                $(this).removeAttr('checked');
            });
            $('#items_error').css('display', 'none');
        }
        $(this).attr('data-dismiss', 'modal');
        //Change currency
        // var currency_id = parseInt($('#id_currency option:selected').val());
        // var currency_name = $('#id_currency option:selected').text();
        // var arrItems = [];
        // $('#dynamic-table tr.gradeX').each(function () {
        //     currentRow = $(this).closest('tr').find('input');
        //     arrItems.push({
        //         item_id: currentRow[5].value,
        //         currency_id: currentRow[12].value
        //     });
        // });
        // changeCurrency(arrItems, currency_id, currency_name);
        // validationItemsFormset();

        $('#dynamic-table tr.gradeX:last').each(function () {
            $("input[name*='wanted_date']").datepicker({
                format: 'yyyy-mm-dd',
                todayHighlight: true,
                autoclose: true
            });
            $("input[name*='schedule_date']").datepicker({
                format: 'yyyy-mm-dd',
                todayHighlight: true,
                autoclose: true
            });
        });
    });

    // insert orderitem by GR num
    function addOrderItemByGR(gr_number) {
        var exclude_item_array = [];
        var exclude_item_list = {};
        var hdSupplierId = $('#hdSupplierId').val();
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
        $.ajax({
            method: "POST",
            url: '/orders/get_orderitems_by_gr_no/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'gr_number': gr_number,
                'supplier_id': hdSupplierId,
                'exclude_item_list': exclude_item_list
            },
            success: function (json) {
                if (json.length > 0) {
                    var allVals = [];
                    $.each(json, function (i, item) {
                        allVals.push({
                            id: item.item_id,
                            location_code: item.location_code,
                            purchase_price: item.purchase_price,
                            item_code: item.item_code,
                            item_name: item.item_name,
                            category: item.category,
                            location_id: item.location_id,
                            uom: item.uom,
                            minimun_order: item.minimun_order,
                            customer_po_no: item.customer_po_no,
                            reference_id: item.refer_id,
                            refer_line: item.refer_line,
                            ref_number: item.refer_number,
                            supplier_code: item.supplier_code,
                            supplier_id: item.supplier_id,
                            order_quantity: item.order_qty,
                            receive_quantity: item.receive_qty,
                        });
                    });
                    cloneMore('#dynamic-table tr.gradeX:last', 'formset_item', allVals);

                    $('#btnSave').removeAttr('disabled');
                    $('#btnPrint').removeAttr('disabled');
                    $('#btnSend').removeAttr('disabled');

                }
            }
        });
    }

    $('#txtGRNo').on('keypress', function (e) {
        if (e.which == 13) {
            addOrderItemByGR($('#txtGRNo').val());
            $('#items_error').css('display', 'none');
        }
    });

    function cloneMore(selector, type, allVals) {
        var display = $(selector).css("display")
        var order_type = $('#order_type').text();
        var sum = 0;
        var i = 0;
        var item_id = 0;
        if (display == 'none') {
            //show first row of table and set Item, Price of dialog
            $(selector).removeAttr("style");
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
            if (allVals[i].location_id != 'None') {
                $(location_choice).find('option[value="' + allVals[i].location_id + '"]').prop('selected', true);
            }
            findInput[1].value = allVals[i].customer_po_no;
            findInput[2].value = allVals[i].item_code;
            findInput[3].value = allVals[i].id;
            findInput[4].value = allVals[i].uom;
            findInput[5].value = allVals[i].category;
            if (allVals[i].minimun_order == '' || allVals[i].minimun_order == 'None') {
                findInput[6].value = 1;
                // findInput[10].value = 1;
            } else {
                findInput[6].value = allVals[i].minimun_order;
                // findInput[10].value = allVals[i].minimun_order;
            }
            findInput[7].value = parseFloat(allVals[i].purchase_price).toFixed(6);
            findInput[8].value = (parseFloat(findInput[6].value) * parseFloat(findInput[7].value)).toFixed(6);
            findInput[9].value = allVals[i].item_name;
            findInput[10].value = allVals[i].id;
            findInput[11].value = allVals[i].supplier_code;
            findInput[12].value = allVals[i].supplier_id;
            findInput[13].value = allVals[i].ref_number;
            findInput[14].value = allVals[i].refer_line;
            findInput[15].value = allVals[i].order_quantity;
            findInput[16].value = allVals[i].receive_quantity;
            findInput[17].value = '';
            findInput[18].value = allVals[i].reference_id;

            currentLabel[0].textContent = findInput[0].value;
            currentLabel[1].textContent = findInput[1].value;
            currentLabel[2].textContent = findInput[2].value;
            currentLabel[3].textContent = findInput[4].value;
            currentLabel[4].textContent = findInput[5].value;
            currentLabel[5].textContent = findInput[9].value;
            currentLabel[6].textContent = findInput[11].value;
            currentLabel[7].textContent = findInput[13].value;
            currentLabel[8].textContent = findInput[14].value;
            currentLabel[9].textContent = findInput[15].value;
            currentLabel[10].textContent = findInput[16].value;
            
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
            // if ($('#id_discount').val()) {
            //     sum -= parseFloat($('#id_discount').val());
            // }
            $('#id_total').val(parseFloat(sum).toFixed(6));
            //if selected items > 1
            i = 1;
        }
        $('#btnSave').removeAttr('disabled');
        $('#btnSend').removeAttr('disabled');
        for (i; i < allVals.length; i++) {
            $(selector).each(function () {
                $("input[name*='wanted_date']").datepicker('remove');
                $("input[name*='schedule_date']").datepicker('remove');
            });
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
                var a = newElement.find('input');
                var clone_location = '#' + newElement.find('select')[0].id;
                currentLabel = newElement.closest('tr').find('label');
                if (a.length > 1) {
                    a[0].value = parseInt($(selector).find('input')[0].value) + 1;
                    a[1].value = allVals[i].customer_po_no;
                    a[2].value = allVals[i].item_code;
                    a[3].value = allVals[i].id;
                    a[4].value = allVals[i].uom;
                    a[5].value = allVals[i].category;
                    if (allVals[i].minimun_order == '' || allVals[i].minimun_order == 'None') {
                        a[6].value = 1;
                    } else {
                        a[6].value = allVals[i].minimun_order;
                    }
                    a[7].value = parseFloat(allVals[i].purchase_price).toFixed(6);
                    a[8].value = (parseFloat(a[6].value) * parseFloat(a[7].value)).toFixed(6);
                    a[9].value = allVals[i].item_name;
                    a[10].value = allVals[i].id;
                    a[11].value = allVals[i].supplier_code;
                    a[12].value = allVals[i].supplier_id;
                    a[13].value = allVals[i].ref_number;
                    a[14].value = allVals[i].refer_line;
                    a[15].value = allVals[i].order_quantity;
                    a[16].value = allVals[i].receive_quantity;
                    a[17].value = '';
                    a[18].value = allVals[i].reference_id;

                    currentLabel[0].textContent = a[0].value;
                    currentLabel[1].textContent = a[1].value;
                    currentLabel[2].textContent = a[2].value;
                    currentLabel[3].textContent = a[4].value;
                    currentLabel[4].textContent = a[5].value;
                    currentLabel[5].textContent = a[9].value;
                    currentLabel[6].textContent = a[11].value;
                    currentLabel[7].textContent = a[13].value;
                    currentLabel[8].textContent = a[14].value;
                    currentLabel[9].textContent = a[15].value;
                    currentLabel[10].textContent = a[16].value;
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
                    // if ($('#id_discount').val()) {
                    //     sum -= parseFloat($('#id_discount').val());
                    // }
                    $('#id_total').val(parseFloat(sum).toFixed(6));
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
        calculateTotal();
    }


    $(document).on('click', "[class^=removerow]", function (event) {
        currentRow = $(this).closest('tr').find('input');
        item_id = currentRow[5].value;
        var order_type = $('#order_type').text();
        if ($('#id_formset_item-TOTAL_FORMS').val() == 1) {
            $(this).closest('tr').css('display', 'none');
            $(this).closest('tr').find('input').each(function () {
                $(this)[0].value = '';
            });
            $('#items_error').removeAttr('style');
            $('#id_subtotal').val(0);
            $('#id_total').val(0);
            $('#btnSave').attr('disabled', true);
            $('#btnPrint').attr('disabled', true);
            // $('#btnSendForEdit').attr('disabled', true);
            $('#btnSend').attr('disabled', true);
        } else {
            $('#btnSave').removeAttr('disabled');
            $('#btnPrint').removeAttr('disabled');
            $('#btnSend').removeAttr('disabled');
            // $('#btnSendForEdit').removeAttr('disabled');
            // var sum = parseFloat($('#id_subtotal').val());
            // sum -= parseFloat(currentRow[10].value);
            // $('#id_subtotal').val(sum.toFixed(6));
            // total = sum.toFixed(6) + parseFloat($('#id_tax_amount').val());
            // $('#id_total').val(total);
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
            var item_currency_not_match = [];
            var sale_price = 0;
            var amount = 0;
            var purchase_price = 0;
            for (var i in json) {
                if (json[i].constructor === Object) {
                    $('#dynamic-table tr.gradeX').each(function () {
                        currentRow = $(this).closest('tr').find('input');
                        currentLabel = $(this).closest('tr').find('label');
                        currentItem = currentRow[2].value;
                        if (currentRow[3].value == json[i].id) {

                            if (json[i].rate == 0 || json[i].sale_price == "") {
                                // item_currency_not_match.push({item: currentItem, currency: json[i].currency});
                                item_currency_not_match.push('Can not get Exchange Rate from ' + json[i].currency + ' to ' + currency_name);
                                currentRow[7].value = 0;
                                currentRow[8].value = 0;
                                $('.lblCurrency').text(json[i].currency);
                            } else {
                                sale_price = currentRow[5].value * currentRow[6].value;
                                currentRow[7].value = parseFloat(json[i].rate).toFixed(4);
                                amount = json[i].rate * sale_price;
                                currentRow[8].value = amount.toFixed(6);
                                $('.lblCurrency').text(json['symbol']);
                            }
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
                $('#btnSend').attr('disabled', true);
                // $('#btnSendForEdit').attr('disabled', true);
                $('#dynamic-table tr.gradeX').each(function () {
                    $(this).closest('tr').find('input').attr('disabled', true);
                });
            } else {
                $('#currency_error').css('display', 'none');
                $('#btnPrint').removeAttr('disabled');
                $('#btnSave').removeAttr('disabled');
                $('#btnSend').removeAttr('disabled');
                // $('#btnSendForEdit').removeAttr('disabled');
                $('#dynamic-table tr.gradeX').each(function () {
                    $(this).closest('tr').find('input').removeAttr('disabled');
                });
            }
            calculateTotal('#dynamic-table tr.gradeX');
        }
    });
};

// calculate subtotal and total
function calculateTotal(selector) {
    // currentRow = $(selector).closest('tr').find('input');
    // amount = currentRow[6].value * currentRow[10].value;
    // currentRow[11].value = amount.toFixed(4);
    var subtotal = 0;
    var total = 0;
    $('#dynamic-table tr.gradeX').each(function () {
        var $tds = $(this).find('input');
        purchase_price = $tds[7].value;
        amount = $tds[6].value * purchase_price;
        $tds[10].value = parseFloat(amount.toFixed(6));
        subtotal += parseFloat(amount);
    });
    $('#id_subtotal').val(subtotal.toFixed(6));
    var tax_rate = parseFloat($('#tax_rate').text());
    tax_value = '0.000000'
    if (subtotal > 0 & tax_rate > 0){
        tax_value = parseFloat(subtotal * tax_rate).toFixed(6);
    };
    $('#id_tax_amount').val(tax_value);
    total = subtotal + parseFloat($('#id_tax_amount').val());
    $('#id_total').val(total.toFixed(6));
}

function supplier_items() {
    // var data = $('#search_input').val();
    var supplier_id = $('#hdSupplierId').val();
    var exclude_item_array = [];
    var exclude_item_list = {};
    $('#dynamic-table tr.gradeX').each(function () {
        var display = $(this).css("display");
        currentRow = $(this).closest('tr').find('input');
        if (display != 'none') {
            exclude_item_array.push(currentRow[5].value);
        }
    });
    if (exclude_item_array.length > 0) {
        exclude_item_list = JSON.stringify(exclude_item_array);
    }

    // if (data.length == 0)
    //     data = '0';
    // $.ajax({
    //     method: "POST",
    //     url: '/orders/change_supplier_items/',
    //     data: {
    //         'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
    //         'supplier_id': supplier_id,
    //         // 'search_condition': data,
    //         'exclude_item_list': exclude_item_list
    //     },
    //     responseTime: 200,
    //     response: function (settings) {
    //         if (settings.data.value) {
    //             this.responseText = '{"success": true}';
    //         } else {
    //             this.responseText = '{"success": false, "msg": "required"}';
    //         }
    //     },
    //     success: function (data) {
    //         $("#myDialog").html('');
    //         $("#myDialog").html(data);
    //         $('#tblData').dataTable({
    //             "aaSorting": [[4, "desc"]],
    //             "bFilter": true,
    //             "bLengthChange": false,
    //             "iDisplayLength": 5,
    //         });
    //     }
    // });

    var datatbl = $('#tblData').DataTable();
    var exclude_item_list = {};
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
            {"data": "item_code", "sClass": "text-left"},
            {"data": 'item_name'},
            {"data": "unit"},
            {"data": "category", "sClass": "text-left"},
            {"data": "minimun_order"},
            {"data": "purchase_price"},
            {"data": "location_code", "sClass": "text-left"},
            {"data": 'supplier_code', "sClass": "text-left"},
            {"data": "customer_po_no", "sClass": "text-left"},
            {"data": 'ref_number', "sClass": "text-left"},
            {"data": 'ref_line'},
            {"data": 'order_qty'},
            {"data": 'receive_qty'},
            {
                "data": "location_id",
                "className": "hide_column"
            },
            {
                "data": "supplier_id",
                "className": "hide_column"
            },
            {
                "data": "refer_id",
                "className": "hide_column"
            },
            {
                "orderable": false,
                "data": null,
                "render": function (data, type, row, meta) {
                    return '<input type="checkbox" name="choices" id="' + row.line_id + '"'
                        + 'class="call-checkbox" value="' + row.line_id + '"></td>';
                }
            }
        ]
    });
}

// event change currency
// $('#id_currency').change(function () {
//     var currency_id = parseInt($(this).val());
//     // var currency_name = $('#id_currency option:selected').text();
//     var arrItems = [];
//     $('#dynamic-table tr.gradeX').each(function () {
//         currentRow = $(this).closest('tr').find('input');
//         arrItems.push({
//             item_id: currentRow[2].value,
//             // currency_id: currentRow[13].value
//         });
//     });
//     // changeCurrency(arrItems, currency_id, currency_name);
// });

//event change quantity
$('#dynamic-table tr.gradeX').each(function () {
    currentRow = $(this).closest('tr').find('input');
    // currentColumn = $(this).closest('tr').find('td');
    $mainElement = '#' + currentRow[8].id;
    $($mainElement).change(function () {
        currentRow = $(this).closest('tr').find('input');
        var quantity = currentRow[8].value;
        var order_quantity = currentRow[17].value;
        if (parseInt(quantity) > parseInt(order_quantity)) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The input quantity must be less than order quantity');
            $(this).closest('tr').attr('style', 'background-color: yellow !important');
            $('#btnPrint').attr('disabled', true);
            $('#btnSave').attr('disabled', true);
            $('#btnSend').attr('disabled', true);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[8]).attr('disabled', true);
            });
        } else if (parseInt(quantity) < 1) {
            $('#minimum_order_error').removeAttr('style');
            $('#minimum_order_error').text('The quantity of product ' + currentRow[4].value + ' must be greater than 0');
            $(this).closest('tr').attr('style', 'background-color: yellow !important');
            currentRow[10].value = 0;
            $('#btnPrint').attr('disabled', true);
            $('#btnSave').attr('disabled', true);
            $('#btnSend').attr('disabled', true);
            // $('#btnSendForEdit').attr('disabled', true);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[8]).attr('disabled', true);
            });
        } else {
            calculateTotal(this);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $('#minimum_order_error').css('display', 'none');
            $(this).closest('tr').removeAttr('style');
            $('#btnPrint').removeAttr('disabled');
            $('#btnSave').removeAttr('disabled');
            $('#btnSend').removeAttr('disabled');
            // $('#btnSendForEdit').removeAttr('disabled');
        }
    });
});


$(document).ready(function () {
    var order_id = $('#order_id').text();
    if (order_id != "") {
        // var currency_id = $('#id_currency').val();
        // var currency_name = $('#id_currency option:selected').text();
        var arrItems = [];
        $('#dynamic-table tr.gradeX').each(function () {
            currentRow = $(this).closest('tr').find('input');
            arrItems.push({
                item_id: currentRow[5].value,
                // currency_id: currentRow[12].value
            });
            $("input[name*='wanted_date']").datepicker({
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            $("input[name*='schedule_date']").datepicker({
                format: 'yyyy-mm-dd',
                autoclose: true
            });
        });
        // changeCurrency(arrItems, currency_id, currency_name);
    }
    // $("#search_input").keypress(function (e) {
    //     var key = e.which;
    //     if (key == 13) {
    //         supplier_items();
    //     }
    // });
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
    $('#id_tax').change(function () {
        var taxid = parseInt($(this).val());
        if (isNaN(taxid)) {
            $('#id_tax_amount').val(0);
            $('#id_total').val(parseFloat($('#id_tax_amount').val()) + parseFloat($('#id_subtotal').val()));
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
                    var tax_amount = (parseFloat(json) * parseFloat($('#id_subtotal').val())) / 100;
                    $('#tax_rate').text(tax_amount);
                    $('#id_tax_amount').val(tax_amount.toFixed(6));
                    var total = parseFloat($('#id_subtotal').val()) + tax_amount;
                    $('#id_total').val(total.toFixed(6));
                }
            });
        }
    });
});