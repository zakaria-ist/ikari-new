/**
 * Created by trung.phan on 10/20/2016.
 */

var dataSet = [
    // [ "Tiger Nixon", "System Architect", "Edinburgh", "5421", "2011/04/25", "$320,800", "", "", "1"],
    // [ "Garrett Winters", "Accountant", "Tokyo", "8422", "2011/07/25", "$170,750", "", "", "2"],
];

var exclude_supplier = [];
var supplier_table_list = $('#supplier-table-list').DataTable();
var exclude_item_list = {};
var btnSaveItem = $('#btnSaveItem');
var emptySupplierError = $('#empty_supplier_error');
var item_id = $('#item_id');
var existing_suppliers = $('#existing_suppliers');
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth() + 1;
var yyyy = today.getFullYear();
var hdSuppliersJson = $('#suppliers_json');
if (dd < 10) {
    dd = '0' + dd
}
if (mm < 10) {
    mm = '0' + mm
}

$(document).ready(function () {
    disableAutoComplete();
    $(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '9'){
            $(this).closest(".select2-container").siblings('select:enabled').select2('open');
        }
    });

    $('form input').on('keypress', function (e) {
        return e.which !== 13;
    });
    emptySupplierError.css("display", "none");
    $('#supplier_error_table').css("display", "none");
    // initialize list of suppliers on btn open dialog
    function get_supplierslist_DT() {
        var filter = $('#txtFilter').val();
        if (exclude_supplier.length > 0) {
            exclude_item_list = JSON.stringify(exclude_supplier);
        }
        supplier_table_list = $('#supplier-table-list').DataTable({
            "order": [[0, "desc"]],
            "bLengthChange": false,
            "iDisplayLength": 5,
            "serverSide": true,
            "ajax": {
                "url": "/items/supplierlist/pagination",
                "type": 'POST',
                "data": {
                    "csrfmiddlewaretoken": $('input[name="csrfmiddlewaretoken"]').val(),
                    "exclude_item_list": exclude_item_list,
                    "filter": filter
                }
            },
            "columns": [
                {"data": "code", "sClass": "text-left"},
                {"data": "name", "sClass": "text-left"},
                {"data": "country_code", "sClass": "text-left"},
                {"data": "currency_code", "sClass": "text-left"},
                {
                    "orderable": false,
                    "data": null,
                    "render": function (data, type, full, meta) {
                        return '<input type="checkbox" name="choices" id="' + full.id + '" class="call-checkbox" value="' + full.currency_id + '">';
                    }
                }
            ]
        });
    }

    function eventSelect2() {
        $('.supp_code_class').on('select2:close', function () {
            var rowIndex = supplier_table.row($(this).closest('tr')).index();
            $($($('#supplier_table').DataTable().cell(rowIndex, 4).node()).find('input')[0]).focus();
        });
    }

    $('#supp_code').on('change', function() {
            var txtFilter = $('#supp_code').val();
            $.ajax({
                method: "POST",
                url: '/items/get_supplier_info1/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'supplier_code': txtFilter,
                },
                responseTime: 200,
                success: function (json) {
                    if (json['Fail']) {
                        alert("Can not find Supplier. Please type correct Supplier Code!")
                    }
                    if (json['id']) {
                        var new_data = ['', json['code'], json['name'], json['currency_code'], '', '', '', '', '', json['id']];
                        dataSet.push(new_data);
                        supplier_table.row.add(new_data).draw(false);
                        exclude_supplier.push(json['id']);

                        // var class_effective_date = $('.effective-date');
                        // // class_effective_date.datepicker('destroy');
                        // class_effective_date.datepicker({
                        //     format: 'dd-mm-yyyy',
                        //     autoclose: true
                        // });
                        validate_form();
                    }
                    $('#txtFilter').val('');
                }
            });
        // }
    });

    $('#id_code').on('keypress', function (e) {
        if (e.which === 13) {
            var item_code = $('#id_code').val();
            $.ajax({
                method: "POST",
                url: '/items/get_item_info/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'item_code': item_code,
                    'item_type': 2,
                },
                responseTime: 200,
                complete: function (xmlHttp) {
                    if (xmlHttp.status == 278) {
                        window.location.href = xmlHttp.getResponseHeader("Location").replace(/\?.*$/, "?next=" + window.location.pathname);
                    }
                },
                success: function (json) {
                    $('#id_code').next('.inputs').focus();
                }
            });
        }
    });
    // supplier_table_list = get_supplierslist_DT();
    // send ajax to get all suppliers in modal
    $('#btnAddSupplierDialog').on('click', function () {
        if (supplier_table_list) {
            supplier_table_list.clear();
            supplier_table_list.destroy();
        }
        get_supplierslist_DT();
    });
    // Initialize datatable
    if (item_id.val()) {
        var dataSetTemp = eval(existing_suppliers.val());
        if (dataSetTemp.length) {
            for (i = 0; i < dataSetTemp.length; i++) {
                dataSetTemp[i].unshift('')
                exclude_supplier.push(dataSetTemp[i][9]);
                dataSet.push(dataSetTemp[i]);
            }
        } else {
            var new_data = ['', '', '', '', '', '', '', '', '', ''];
            dataSet.push(new_data);
        }
    } else {
        var new_data = ['', '', '', '', '', '', '', '', '', ''];
        dataSet.push(new_data);
    }
    var supplier_table = $('#supplier_table').DataTable({
        data: dataSet,
        "paging": false,
        "info": false,
        "filter": false,
        "columnDefs": [
            {
                "targets": 0,
                "orderable": false,
                "render": function ( data, type, full, meta ) {
                    return '<lable class="control-label-item">'+ (meta.row + 1) +'</lable>';
                }
            },
            {
                "targets": 1,
                "orderable": false,
                "sClass": "min-small-width",
                "render": function (data, type, row) {
                    if (data) {
                        return '<lable class="control-label-item">'+ data +'</lable>';
                    } else {
                        var elementSelect = '<select class="supp_code_class">' + supp_code_select.html() + '</select>';
                        return elementSelect;
                    }
                }
            },
            {
                "targets": 2,
                "orderable": false,
                "sClass": "min-medium-width",
                "render": function (data, type, row) {
                    return '<lable class="label-item">'+ data +'</lable>';
                }
            },
            {
                "targets": 3,
                "orderable": false,
                "sClass": "tiny-width"
            },
            {
                "targets": 9,
                "orderable": false,
                "data": null,
                "sClass": "custom_align",
                "defaultContent": '<div class="btn-group" style="width:75px">' +
                    '<button type="button" class="removerow btn btn-white fa fa-trash-o code_style " value="Remove" style="color:red"></button>' +
                    '<button type="button" class="plusrow btn btn-white fa fa-plus" value=""></button>' +
                    '</div>'
            },
            {
                "targets": 4,
                "orderable": false,
                "sClass": "width-175",
                "render": function (data, type, row) {
                    data = comma_format(data, 6);
                    return '<input name="' + row[3] + '" class="form-control pos-num medium-width text-right numeric_price" type="text" value="' + data + '" required>'
                }
            },
            {
                "targets": 5,
                "sClass": "width-80",
                "orderable": false,
                "render": function (data, type, row) {
                    return '<input name="' + row[4] + '" class="form-control" style="width: 70px !important;" min="0" max="999" pattern="/^-?\\d+\\.?\\d*$/" onKeyPress="if(this.value.length==3) return false;" type="number" step="1" value="' + data + '">'
                }
            },
            {
                "targets": 7,
                "sClass": "width-175",
                "orderable": false,
                "render": function (data, type, row) {
                    data = comma_format(data, 6);
                    return '<input name="' + row[6] + '" class="form-control medium-width text-right numeric_price pos-num last-tab" type="text" value="' + data + '">'
                }
            },
            {
                "targets": 6,
                "orderable": false,
                "sClass": "width-100",
                "render": function (data, type, row) {
                    return '<input name="' + row[5] + '" class="form-control form-control-inline effective-date" style="width: 100px !important;" value="' + data + '">'
                }
            },
            {
                "targets": 8,
                "orderable": false,
                "sClass": "width-100",
                "render": function (data, type, row) {
                    return '<input name="' + row[7] + '" class="form-control form-control-inline input-medium" tabindex="-1" style="width: 100px !important;" readonly="readonly" value="' + data + '">'
                }
            }
        ],
        "order": [],
        "drawCallback": function() {
            var currentRow = $('#supplier_table  tbody tr:last').closest('tr').find('select');
            $(currentRow[0]).select2(
                {
                    placeholder: "Code",
                    allowClear: true,
                }
            );
            $($('.supp_code_class').parent('td').find('span')[0]).removeAttr("style");
            $($('.supp_code_class').parent('td').find('span')[0]).attr('style', 'width: 100px !important');

            eventSelect2();
        }
    });
    // $('.effective-date').datepicker({
    //     format: 'dd-mm-yyyy',
    //     autoclose: true
    // });

    $('#supplier_table tbody').on('keyup', '.effective-date', function (e) {
         adjust_input_date(this);
    });

    $('#supplier_table tbody').on('change', '.effective-date', function (e) {
        var date_from = get_date_from_by_val($(this).val());
        var date_from_valid = moment(date_from, "DD-MM-YYYY", true).isValid();
        var that = this;
        if (!date_from_valid) {
            pop_ok_dialog("Invalid Effective Date",
                "Effective Date (" + $(this).val() + ") is invalid !",
                function () {
                    $(that).val('');
                    $(that).focus();
                });

        }
    });

    $('#supplier_table tbody').on('keydown', '.last-tab', function (e) {
        var rowIndex = supplier_table.row($(this).closest('tr')).index();
        let code_pressed = e.which;
        if (code_pressed == 9) {
          if (rowIndex == (supplier_table.data().length - 1)) {
              $(this).closest('tr').find('.plusrow').trigger('click');
          }
          $($(supplier_table.cell((rowIndex + 1), 1).node()).find('select')[0]).focus();
          $($(supplier_table.cell((rowIndex + 1), 1).node()).find('select')[0]).select2('open');
      }
    });

    $('#supplier_table tr').on('keydown', '.select2-container', function (e) {
        var rowIndex = supplier_table.row($(this).closest('tr')).index();
        // just tab key
        let code_pressed = e.which;
        if (code_pressed == 9) {
          $($(supplier_table.cell((rowIndex + 1), 0).node()).find('input')[0]).focus();
        }
    });


    // button remove supplier
    $('#supplier_table tbody').on('click', '.removerow', function () {
        var row = supplier_table.row($(this).parents('tr'));
        data = row.data();
        dataSet = jQuery.grep(dataSet, function (n, i) {
            return n[8] !== data[8];
        });
        supplier_table.row($(this).parents('tr')).remove().draw(false);
        // pop this supplier id out of exclude_supplier list
        var index = exclude_supplier.indexOf(data[8]);
        if (index > -1) {
            exclude_supplier.splice(index, 1);
        }
        
        if (supplier_table.data().length == 0) {
            addNewRow();
        } else {
            is_table_valid();
        }
    });
    // button add supplier
    $('#supplier_table tbody').on('click', '.plusrow', function () {
        // var new_data = ['', '', '', '', '', '', '', '', '', ''];
        // dataSet.push(new_data);
        // supplier_table.row.add(new_data).draw(false);
        //
        // var class_effective_date = $('.effective-date');
        // class_effective_date.datepicker({
        //     format: 'dd-mm-yyyy',
        //     autoclose: true
        // });
        // validate_form();
        addNewRow();
    });

    $('#supplier_table tbody').on('change', 'select.supp_code_class', function (e) {
        var rowIndex = supplier_table.row($(this).closest('tr')).index();
        var currentRow = $(this).closest('tr').find('input');
        var txtFilter = $(this).val();
        if (!txtFilter) {
            var new_data = ['', '', '', '', '', '', '', '', '', ''];
            dataSet[rowIndex] = new_data;
            supplier_table.cell( rowIndex, 2 ).data('');
            supplier_table.cell( rowIndex, 3 ).data('');
            supplier_table.cell( rowIndex, 8 ).data('');
        } else {
            $.ajax({
                method: "POST",
                url: '/items/get_supplier_info1/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                    'supplier_code': txtFilter,
                },
                responseTime: 200,
                success: function (json) {
                    if (json['Fail']) {
                        alert("Can not find Supplier. Please type correct Supplier Code!");
                    }
                    if (json['id']) {
                        var new_data = ['', json['code'], json['name'], json['currency_code'], '', '', '', '', '', json['id']];
                        dataSet[rowIndex] = new_data;
                        supplier_table.cell( rowIndex, 2 ).data(json['name']);
                        supplier_table.cell( rowIndex, 3 ).data(json['currency_code']);
                        supplier_table.cell( rowIndex, 8 ).data($.datepicker.formatDate('dd-mm-yy', new Date()));
                        // supplier_table.draw();
                        validate_form();
                    }
                }
            });
        }
        supplier_table.cell( rowIndex, 4 ).data('');
        supplier_table.cell( rowIndex, 5 ).data('');
        supplier_table.cell( rowIndex, 7 ).data('');
        currentRow[2].value = ''
        return;

    });

    $('#supplier_table tbody').on('change', 'input.pos-num', function () {
        var e = $(this);
        var value = float_format($(this).val());
        if ($(this).val() > 0) {
            $(this).parents('tr').removeAttr('style');
            $('#supplier_table tr').each(function () {
                $(this).find('input').removeAttr('disabled');
                $(this).find('.removerow').removeAttr('disabled');
            });
            $('#btnSaveItem').removeAttr('disabled');
            $('#btnAddSupplierDialog').removeAttr('disabled');
            if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
                $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').removeAttr('style');
            }

            $($(this).closest('tr').find('input')[1]).focus();
            // $('#btnDelete').removeAttr('disabled');
        } else {
            // $('#btnSaveItem').attr('disabled', true);
            // $('#btnAddSupplierDialog').attr('disabled', true);
            // if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
            //     $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').css('display', 'none');
            // }
            // $('#supplier_table tr').each(function () {
            //     $(this).find('input').not(e).attr('disabled', true);
            //     $(this).find('.removerow').attr('disabled', true);
            // })
            // $(this).select();
            // $(this).focus();
        }
        $(this).val(comma_format(value, 6));
        setTimeout(() => {
            is_table_valid();
        }, 300);
        
    });
    // Button Select Supplier
    // $('#btnSupplierSelect').on('click', function () {
    //     var rowcollection = supplier_table_list.$(".call-checkbox:checked", {"page": "all"});
    //     rowcollection.each(function (index, elem) {
    //         var row = $(this).parents('tr');
    //         var row_tds = row.find('td');
    //         supplier_id = row.find('td').last().find('input').attr('id');
    //         var new_data = [row_tds[0].innerText, row_tds[1].innerText, row_tds[3].innerText, '', '', '', '', '', supplier_id.toString()];
    //         dataSet.push(new_data);
    //
    //         supplier_table.row.add(new_data).draw(false);
    //
    //         // row.attr("style", "display: none");
    //         row.find('td').last().find('input').removeAttr('checked');
    //         exclude_supplier.push(supplier_id);
    //     });
    //
    //     $(this).attr('data-dismiss', 'modal');
    //
    //     var class_effective_date = $('.effective-date');
    //     // class_effective_date.datepicker('destroy');
    //     class_effective_date.datepicker({
    //         format: 'dd-mm-yyyy',
    //         autoclose: true
    //     });
    //     validate_form();
    // });

    function is_table_valid() {
        // validation
        var is_valid = true;
        for (var i = 0; i < supplier_table.data().length; i++) {
            var rowInput = $(supplier_table.row(i).node()).find('input');
            var selects = $(supplier_table.row(i).node()).find('select');

            // dataSet[i][9] // Supplier code
            // rowInput[0].value -> Purchase Price
            if (float_format(rowInput[0].value) <= 0 || rowInput[0].value == '') {
                is_valid = false;
                $(supplier_table.row(i).node()).closest('tr').attr('style', 'background-color: red !important');
            } else if (selects.length > 0) {
                if (dataSet[i][9] == '' || dataSet[i][9] == undefined) {
                    is_valid = false;
                    $(supplier_table.row(i).node()).closest('tr').attr('style', 'background-color: red !important');
                }
            }
        }

        if (!is_valid) {
            $('#supplier_error_table').removeAttr('style');
        } else {
            $('#supplier_error_table').css('display', 'none');
        }

        return is_valid;
    }

    function addNewRow() {
        var new_data = ['', '', '', '', '', '', '', '', '', ''];
        dataSet.push(new_data);
        supplier_table.row.add(new_data).draw(false);
        disableAutoComplete();

        // var class_effective_date = $('.effective-date');
        // class_effective_date.datepicker({
        //     format: 'dd-mm-yyyy',
        //     autoclose: true
        // });
    }

    function bindingDataForm(dataItems) {
        $('#id_code').val(dataItems.code);
        $('#id_name').val(dataItems.name);
        $('#id_short_description').val(dataItems.short_description);
        $('#id_category')
            .val(dataItems.category)
            .trigger('change');
        $('#id_inv_measure')
            .val(dataItems.inv_measure)
            .trigger('change');
        $('#id_report_measure')
            .val(dataItems.report_measure)
            .trigger('change');
        $('#id_purchase_measure')
            .val(dataItems.purchase_measure)
            .trigger('change');
        $('#id_person_incharge').val(dataItems.person_incharge);
        $('#id_country')
            .val(dataItems.country)
            .trigger('change');
        $('#id_purchase_price').val(dataItems.purchase_price);
        $('#id_purchase_currency')
            .val(dataItems.purchase_currency)
            .trigger('change');
        $('#id_default_supplier').val(dataItems.ratio);
        $('#id_model_qty').val(dataItems.model_qty);
        $('#id_minimun_order').val(dataItems.minimun_order);
    }

    function validate_form() {
        if (dataSet.length > 0) {
            btnSaveItem.removeAttr('disabled');
            emptySupplierError.css('display', 'none');
            if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
                $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').removeAttr('style');
            }
            // return true;
        } else {
            btnSaveItem.attr('disabled', true);
            emptySupplierError.removeAttr('style');
            $('html, body').animate({
                scrollTop: emptySupplierError.offset().top
            }, 1000);
            if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
                $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').css('display', 'none');
            }
            return false;
        }
    }

    // button submit form
    btnSaveItem.on('click', function () {
        if (dataSet.length > 0) {
            // validation
            var is_valid = is_table_valid();
            // for (var i = 0; i < supplier_table.data().length; i++) {
            //     var rowInput = $(supplier_table.row(i).node()).find('input');
            //
            //     // dataSet[i][9] // Supplier code
            //     // rowInput[0].value -> Purchase Price
            //     if (float_format(rowInput[0].value) <= 0 || rowInput[0].value == '' || dataSet[i][9] == '' || dataSet[i][9] == undefined) {
            //         is_valid = true;
            //         $(supplier_table.row(i).node()).closest('tr').attr('style', 'background-color: red !important');
            //     }
            // }

            if (!is_valid) {
                return false;
            } else {
                btnSaveItem.removeAttr('disabled');
                emptySupplierError.css('display', 'none');
                if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
                    $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').removeAttr('style');
                }
                var myData = [];
                for (var i = 0; i < supplier_table.data().length; i++) {
                    var rowInput = $(supplier_table.row(i).node()).find('input');
                    myData.push([dataSet[i][9], rowInput[0].value, rowInput[1].value, rowInput[2].value, rowInput[3].value]);
                }
                hdSuppliersJson.val(JSON.stringify(myData));

                $('#supplier_table tbody tr').each(function () {
                    let currentRow = $(this).closest('tr').find('input');
                    currentRow[0].value = float_format(currentRow[0].value);
                    currentRow[3].value = float_format(currentRow[3].value);
                })
            }
        }
        // else {
        //     btnSaveItem.attr('disabled', true);
        //     emptySupplierError.removeAttr('style');
        //     $('html, body').animate({
        //         scrollTop: emptySupplierError.offset().top
        //     }, 1000);
        //     if ($('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger')) {
        //         $('#item_form_submit > div:nth-child(15) > div > a.btn.btn-danger').css('display', 'none');
        //     }
        //     return false;
        // }
    });

    $("#new_part").change(function() {
        if(this.checked) {
            $('#id_code').removeClass('hide');
            $('#id_code').attr('required', 'required');
            $('#cek_part').addClass('hide');
            if (supplier_table) {
                supplier_table.clear();
            }
            addNewRow();
            var dataItems = {
                'code' : '',
                'name' : '',
                'short_description' : '',
                'category' : '',
                'inv_measure' : '',
                'report_measure' : '',
                'purchase_measure' : '',
                'person_incharge' : '',
                'country' : '',
                'purchase_price' : '',
                'purchase_currency' : '',
                'ratio' : '',
                'model_qty' : '',
                'minimun_order' : '',
            }
            bindingDataForm(dataItems);
        }else{
            $('#id_code').addClass('hide');
            $('#id_code').removeAttr( "required" );
            $('#cek_part').removeClass('hide');
            $('#part_number_axis').trigger('change');
        }
    });

    $('#part_number_axis').on('change', function () {
        if ($('#part_number_axis').val() > 0) {
            itm_id = $('#part_number_axis').val();
            $.ajax({
                type: "GET",
                url: "/items/part_sale_json/"+itm_id+"/",
                success: function(data){
                var dataItems = data.data[0];
                var customers = data.suppliers;

                bindingDataForm(dataItems);

                if (customers.length){
                    var total = 1;
                    while (total < customers.length) {
                        $('#supplier_table tbody tr:last').closest('tr').find('.plusrow').trigger('click');
                        total++;
                    }
                    let i=0;
                    $('#supplier_table tbody tr').each(function () {
                        let currentRow = $(this).closest('tr').find('input');
                        let currentLabel = $(this).closest('tr').find('label');
                        let selects = $(this).closest('tr').find('select');
                        $(selects[0]).val(customers[i].customer_code).trigger('change');
                        currentRow[0].value = customers[i].sales_price;
                        currentRow[1].value = customers[i].leads;
                        currentRow[2].value = customers[i].effective_date;
                        currentRow[3].value = customers[i].new_price;
                        currentRow[4].value = customers[i].update_date;
                        i++;
                    });
                }
                }
            });
        }
    });
});
