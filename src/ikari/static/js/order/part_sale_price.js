/**
 * Created by tho.pham on 10/21/2016.
 */

function is_table_valid() {
    var is_valid = true;
    $('#dynamic-table tr.gradeX').each(function () {
        let currentRow = $(this).closest('tr').find('input');
        let selects = $(this).closest('tr').find('select');
        if (float_format(currentRow[6].value) <= 0 || currentRow[6].value == '') {
            is_valid = false;
            $(this).closest('tr').attr('style', 'background-color: red !important');
        } else if (selects.length > 0) {
            if ($('#' + selects[0].id).val() == '' || $('#' + selects[0].id).val() == undefined || $('#' + selects[0].id).val() == null) {
                is_valid = false;
                $(this).closest('tr').attr('style', 'background-color: red !important');
            }
        }
    });

    if (!is_valid) {
        $('#supplier_error_table').css('display', '');
    } else {
        $('#supplier_error_table').css('display', 'none');
    }
    return is_valid;
}

function initElement(currentRowSelect, currentRowInput) {
    $(currentRowSelect[0]).val('');
    $(currentRowSelect[0]).select2(
        {
            placeholder: "Cust. Code",
            allowClear: true,
            width: '90px',
        }
    );
    $($(currentRowSelect[0]).parent('td').find('span')[0]).removeAttr("style");
    $($(currentRowSelect[0]).parent('td').find('span')[0]).attr('style', 'width: 120px !important');

    // $(currentRowInput[8]).datepicker({
    //     format: 'dd-mm-yyyy',
    //     todayHighlight: true,
    //     autoclose: true
    // });

}

function cloneMore_2(type, allVals, rowIndex) {
    var i = 0;
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    for (i; i < allVals.length; i++) {
        if (allVals[i].id != 0) {
            var newElement = $(store_row_temporary).clone(true);
            var a = newElement.find('input');
            currentRow = newElement.closest('tr').find('label');
            if (a.length > 1) {
                a[0].value = rowIndex + 1;
                a[1].value = allVals[i].customer_code; // customer code
                a[2].value = allVals[i].customer_id; // customer id
                a[3].value = allVals[i].customer_name; // customer name
                a[4].value = allVals[i].currency_code;
                a[5].value = allVals[i].currency_id;
                // a[10].value = today;

                //add value to Label
                currentRow[0].textContent = a[0].value;
                currentRow[1].textContent = a[3].value;
                currentRow[2].textContent = a[4].value;
            }
            total++;
            $('#id_' + type + '-TOTAL_FORMS').val(total);
            if (rowIndex == 0) {
                $('#dynamic-table tbody').append(newElement);
            } else {
                $('#dynamic-table tr.gradeX').eq(rowIndex - 1).after(newElement);
            }

            newElement = $($('#dynamic-table tr.gradeX').eq(rowIndex));

            // change attribute name and id
            changeAttr(newElement,0, rowIndex);

            // add select2 and datepicker
            var currentRowSelect = newElement.find('select');
            var currentRowInput = newElement.find('input');

            initElement(currentRowSelect, currentRowInput);

            var today = $.datepicker.formatDate('dd-mm-yy', new Date());
            $(currentRowInput[10]).val(today);
            rowIndex++;
        }
    }

    while(total > rowIndex) {
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
    disableAutoComplete();
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

// function cloneMore(selector, type, allVals) {
//     var display = $(selector).css("display");
//     var i = 0;
//     var today = $.datepicker.formatDate('yy-mm-dd', new Date());
//     if (display == 'none') {
//         //show first row of table and set Item, Price of dialog
//         $(selector).removeAttr("style")
//
//         $(selector).find('label').each(function () {
//             var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
//             var id = 'id_' + name;
//             $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
//         });
//
//         findInput = $(selector).find('input');
//         currentLabel = $(selector).closest('tr').find('label');
//
//         console.log(allVals)
//
//         //add value to Input
//         findInput[0].value = 1;
//         findInput[1].value = allVals[i].customer_code;
//         findInput[2].value = allVals[i].customer_id;
//         findInput[3].value = allVals[i].customer_name;
//         findInput[4].value = allVals[i].currency;
//         findInput[5].value = allVals[i].currency_id;
//         findInput[10].value = today;
//
//         //add value to Label
//         currentLabel[0].textContent = findInput[0].value;
//         currentLabel[1].textContent = findInput[1].value;
//         currentLabel[2].textContent = findInput[3].value;
//         currentLabel[3].textContent = findInput[4].value;
//
//         //if selected items > 1
//         i = 1;
//     }
//     ;
//     $('#btnSave').removeAttr('disabled');
//     for (i; i < allVals.length; i++) {
//         $(selector).each(function () {
//             $("input[name*='effective_date']").datepicker('remove');
//         });
//         if (allVals[i].id != 0) {
//             var newElement = $(selector).clone(true);
//             var total = $('#id_' + type + '-TOTAL_FORMS').val();
//             newElement.removeAttr("style")
//             newElement.find(':input').each(function () {
//                 var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
//                 var id = 'id_' + name;
//                 $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
//             });
//             newElement.find('label').each(function () {
//                 var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
//                 var id = 'id_' + name;
//                 $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
//             });
//
//             var a = newElement.find('input');
//             currentRow = newElement.closest('tr').find('label');
//
//             if (a.length > 1) {
//                 a[0].value = parseInt($(selector).find('input')[0].value) + 1;
//                 a[1].value = allVals[i].customer_code;
//                 a[2].value = allVals[i].customer_id;
//                 a[3].value = allVals[i].customer_name;
//                 a[4].value = allVals[i].currency;
//                 a[5].value = allVals[i].currency_id;
//                 a[10].value = today;
//
//                 //add value to Label
//                 currentRow[0].textContent = a[0].value;
//                 currentRow[1].textContent = a[1].value;
//                 currentRow[2].textContent = a[3].value;
//                 currentRow[3].textContent = a[4].value;
//             }
//
//             total++;
//             $('#id_' + type + '-TOTAL_FORMS').val(total);
//             $(selector).after(newElement);
//         }
//     }
// }

// $('#btnCustomerSelect').on('click', function () {
//     var allVals = [];
//     var table = $('#customer-table').DataTable();
//     var rowcollection = table.$(".call-checkbox:checked", {"page": "all"});
//     rowcollection.each(function (index, elem) {
//         var jqInputs = elem.closest('tr').cells;
//         allVals.push({
//             customer_id: elem.id,
//             customer_name: jqInputs[1].innerText,
//             customer_code: jqInputs[0].innerText,
//             currency_id: elem.value,
//             currency: jqInputs[4].innerText
//         });
//     });
//     $('input[type=checkbox]').click(function () {
//         if ($(this).is(':checked'))
//             $(this).attr('checked', 'checked');
//         else
//             $(this).removeAttr('checked');
//     });
//     if (allVals.length > 0) {
//         cloneMore('#dynamic-table tr.gradeX:last', 'formset_customer_item', allVals);
//         $('input[checked=checked]').each(function () {
//             $(this).removeAttr('checked');
//         });
//         $('#items_error').css('display', 'none');
//     }
//     ;
//     $('#dynamic-table tr.gradeX:last').each(function () {
//         $("input[name*='effective_date']").datepicker({
//             format: 'dd-mm-yyyy',
//             todayHighlight: true,
//             autoclose: true
//         });
//     });
//     $('#dynamic-table tr.gradeX:last').each(function () {
//         $("#dynamic-table tr.gradeX:last input[name*='update_date']").val($("#dynamic-table tr.gradeX:last input[name*='update_date']").val().split("-").reverse().join("-"));
//     });
//
//     $(this).attr('data-dismiss', 'modal');
// });

// $('#cust_code').on('change', function() {
//     var txtFilter = $('#cust_code').val();
//     $.ajax({
//         method: "POST",
//         url: '/items/get_customer_info1/',
//         dataType: 'JSON',
//         data: {
//             'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
//             'customer_code': txtFilter,
//         },
//         responseTime: 200,
//         success: function (json) {
//             if (json['Fail']) {
//                 alert("Can not find Customer. Please type correct Customer Code!")
//             }
//             if (json['id']) {
//                 var new_data = [json['code'], json['name'], json['currency_code'], '', '', '', '', '', json['id']];
//                 var allVals = [];
//                 allVals.push({
//                     customer_id: json['id'],
//                     customer_name: json['name'],
//                     customer_code: json['code'],
//                     currency_id: json['currency_id'],
//                     currency: json['currency_code']
//                 });
//                 if (allVals.length > 0) {
//                     cloneMore('#dynamic-table tr.gradeX:last', 'formset_customer_item', allVals);
//                     $('input[checked=checked]').each(function () {
//                         $(this).removeAttr('checked');
//                     });
//                     $('#items_error').css('display', 'none');
//                 }
//                 $('#dynamic-table tr.gradeX:last').each(function () {
//                     $("input[name*='effective_date']").datepicker({
//                         format: 'dd-mm-yyyy',
//                         todayHighlight: true,
//                         autoclose: true
//                     });
//                 });
//                 $('#dynamic-table tr.gradeX:last').each(function () {
//                     $("#dynamic-table tr.gradeX:last input[name*='update_date']").val($("#dynamic-table tr.gradeX:last input[name*='update_date']").val().split("-").reverse().join("-"));
//                 });
//             }
//             $('#txtFilter').val('');
//         }
//     });
//     // }
// });

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
                'item_type': 1,
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


$(document).on('click', "[class^=removerow]", function (event) {
        $('#btnSave').removeAttr('disabled');
        var minus = parseInt($('input[name=formset_customer_item-TOTAL_FORMS]').val()) - 1;
        $('#id_formset_customer_item-TOTAL_FORMS').val(minus);
        $(this).parents("tr").remove();
        $('#dynamic-table tr.gradeX').each(function (rowIndex, r) {
            $(this).find('td').each(function (colIndex, c) {
                $.each(this.childNodes, function (i, elem) {
                    if (elem.nodeName == 'INPUT' || elem.nodeName == 'LABEL') {
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

        if ($('#id_formset_customer_item-TOTAL_FORMS').val() == 0) {
            let allVals = [];
            allVals.push({
                customer_id: 1,
                customer_name: '',
                customer_code: '',
                currency_id: '',
                currency_code: '',
            });
            cloneMore_2('formset_customer_item', allVals, 0);
        } else {
            is_table_valid();
        }
});



$('#dynamic-table tr.gradeX').each(function () {
    currentRow = $(this).closest('tr').find('input');
    $priceElement = '#' + currentRow[6].id;
    $($priceElement).change(function () {
        currentRow = $(this).closest('tr').find('input');
        if (float_format(currentRow[6].value) > 0) {
            $('#validate_error').css('display', 'none');
            currentRow.parents('tr').removeAttr('style');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $('#validate_error').css('display', 'none');
            $('#btnSave').removeAttr('disabled');
            $('#btnOpenItemDialog').removeAttr('disabled');
            $('#btnDelete').removeAttr('disabled');
            $('#' + currentRow[7].id).focus();
        } else {
            $('#validate_error').text('Sale Price must be greater than 0 and not none');
            $('#validate_error').removeAttr('style');
            currentRow.parents('tr').attr('style', 'background-color: red !important');
            $('#btnSave').attr('disabled', true);
            $('#btnOpenItemDialog').attr('disabled', true);
            $('#btnDelete').attr('disabled', true);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[6]).attr('disabled', true);
            });
            $(this).select();
            $(this).focus();
        }
        $(this).val(comma_format(float_format(currentRow[6].value), 6));
        is_table_valid();
    });

    $newPriceElement = '#' + currentRow[9].id;
    $($newPriceElement).change(function () {
        currentRow = $(this).closest('tr').find('input');
        if (currentRow[9].value >= 0) {
            $('#validate_error').css('display', 'none');
            currentRow.parents('tr').removeAttr('style');
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').removeAttr('disabled');
            });
            $('#validate_error').css('display', 'none');
            $('#btnSave').removeAttr('disabled');
            $('#btnOpenItemDialog').removeAttr('disabled');
            $('#btnDelete').removeAttr('disabled');
        } else {
            $('#validate_error').text('New Price must be greater than 0 and not none');
            $('#validate_error').removeAttr('style');
            currentRow.parents('tr').attr('style', 'background-color: red !important');
            $('#btnSave').attr('disabled', true);
            $('#btnOpenItemDialog').attr('disabled', true);
            $('#btnDelete').attr('disabled', true);
            $('#dynamic-table tr.gradeX').each(function () {
                $(this).closest('tr').find('input').not(currentRow[9]).attr('disabled', true);
            });
        }

        $(this).val(comma_format(float_format(currentRow[9].value), 6));
        is_table_valid();
    });

    $effectiveDateElement = '#' + currentRow[8].id;
    $($effectiveDateElement).keyup(function () {
         adjust_input_date(this);
    });

    $($effectiveDateElement).on('change', function () {
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
});

// $('#dynamic-table tr.gradeX').find('input').each(function () {
//     currentRow = $(this).closest('tr').find('input');
//     $newPriceElement = '#' + currentRow[9].id;
//     $($newPriceElement).change(function () {
//         currentRow = $(this).closest('tr').find('input');
//         if (currentRow[9].value >= 0) {
//             $('#validate_error').css('display', 'none');
//             currentRow.parents('tr').removeAttr('style');
//             $('#dynamic-table tr.gradeX').each(function () {
//                 $(this).closest('tr').find('input').removeAttr('disabled');
//             });
//             $('#validate_error').css('display', 'none');
//             $('#btnSave').removeAttr('disabled');
//             $('#btnOpenItemDialog').removeAttr('disabled');
//             $('#btnDelete').removeAttr('disabled');
//         } else {
//             $('#validate_error').text('New Price must be greater than 0 and not none');
//             $('#validate_error').removeAttr('style');
//             currentRow.parents('tr').attr('style', 'background-color: red !important');
//             $('#btnSave').attr('disabled', true);
//             $('#btnOpenItemDialog').attr('disabled', true);
//             $('#btnDelete').attr('disabled', true);
//             $('#dynamic-table tr.gradeX').each(function () {
//                 $(this).closest('tr').find('input').not(currentRow[9]).attr('disabled', true);
//             });
//         }
//
//         $(this).val(comma_format(float_format(currentRow[9].value), 6));
//         is_table_valid();
//     });
// });
