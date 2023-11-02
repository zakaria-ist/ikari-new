$('#sandbox-container input').datepicker({
    format: "mm-yyyy",
    startView: 1,
    minViewMode: 1,
    autoclose: true
});

var sfl_supplier_list = [];
var cfl_customer_list = [];
global_order_code = '';
var global_url = '';
var EMPTY_DATE_MSG = 'Please select a valid date!';
$(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
    var keycode = (e.keyCode ? e.keyCode : e.which);
    if(keycode == '9'){
        $(this).closest(".select2-container").siblings('select:enabled').select2('open');
    }
});

$(document).ready(function () {
    load_report_list();

    // $('#date_fromSA').datepicker('setDate', current_period_from);
    // $('#date_toSA').datepicker('setDate', current_period_to);

    $('#is_confirm').select2({});
    
    $('#SR7303_supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#SR7303_supplier_to').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#SR7303_document').select2({
        allowClear: true,
        placeholder: "Select Document"
    });
    $('#SR7303_document_to').select2({
        allowClear: true,
        placeholder: "Select Document"
    });
    $('#SR7303_customer_po').select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $('#SR7303_customer_po_to').select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $('#SR7303_part_no').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#SR7303_part_no_to').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#SR7303_sort').select2({
    });
    $('#toSACustomerPo').select2({
        allowClear: true,
        placeholder: "Select Cust. PO"
    });
    $('#fromSACustomerPo').select2({
        allowClear: true,
        placeholder: "Select Cust. PO"
    });
    $('#toSAPartNo').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#fromSAPartNo').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#fromSACustomer').select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $('#toSACustomer').select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $('#SR7603_customer').select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $('#SR7603_customer_to').select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $('#SR7603_document').select2({
        allowClear: true,
        placeholder: "Select Document"
    });
    $('#SR7603_document_to').select2({
        allowClear: true,
        placeholder: "Select Document"
    });
    $('#SR7603_customer_po').select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $('#SR7603_customer_po_to').select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $('#SR7603_part_no').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#SR7603_part_no_to').select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $('#SR7603_sort').select2({
    });

    $('#CL2100_code').select2({
    });
    $('#TL1200_tax_code').select2({
        allowClear: true,
        placeholder: "Select Tax Code"
    });
    $('#TL1200_tax_code_to').select2({
        allowClear: true,
        placeholder: "Select Tax Code"
    });
    $('#lbSR7202Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7202ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR8801Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR8801ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7203Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7203ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR8301Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR8301ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7204Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7204ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7205Supplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $('#lbSR7205ToSupplier').select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });

    // $('#report_category').select2({});
    $("#report_list").select2({});

    $("#lbSL3A0Document").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSL3A0ToDocument").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSL330Document").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSL330ToDocument").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSL3A0Supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier",
    });
    $("#lbSL3A0ToSupplier").select2({
        allowClear: true,
        placeholder: "Select Supplier",
    });
    $("#lbSL330CCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer",
    });
    $("#lbSL330ToCCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer",
    });
    $("#lbSR834Document").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSR834ToDocument").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSL3A0Cutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSL3A0ToCutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSL330Cutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSL330ToCutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSR7201Document").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSR7201ToDocument").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#lbSR7203Cutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSR7203ToCutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSR8301Cutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#lbSR8301ToCutomer").select2({
        allowClear: true,
        placeholder: "Select Customer PO"
    });
    $("#sl2100_part_no").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2100_part_no_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2100_part_grp").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2100_part_grp_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2100_supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#sl2100_supplier_to").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#sl2200_part_no").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2200_part_no_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2200_part_grp").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2200_part_grp_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2200_customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#sl2200_customer_to").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#sl2201_part_no").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2201_part_no_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2201_part_grp").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2201_part_grp_to").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#sl2201_supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#sl2201_supplier_to").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#sl2201_customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#sl2201_customer_to").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7204PartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7204ToPartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7205PartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7205ToPartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7404PartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7404ToPartNo").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#lbSR7404PartGrp").select2({
        allowClear: true,
        placeholder: "Select Part Grp"
    });
    $("#lbSR7404ToPartGrp").select2({
        allowClear: true,
        placeholder: "Select Part Grp"
    });
    $("#lbSR7402Customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7402ToCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7403Customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7403ToCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7403Supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#lbSR7403ToSupplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#lbSR7404Customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR7404ToCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR8400Customer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR8400ToCustomer").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbCL2400Supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#lbCL2400ToSupplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#lbDL2400Supplier").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbDL2400ToSupplier").select2({
        allowClear: true,
        placeholder: "Select Customer"
    });
    $("#lbSR8300Supplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#lbSR8300ToSupplier").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });

    $("#lbSR7102PartGrp").select2({
        allowClear: true,
        placeholder: "Select Part Grp."
    });
    $("#lbSR7102ToPartGrp").select2({
        allowClear: true,
        placeholder: "Select Part Grp."
    });

    $("#txtPartNoSR7503").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#txtPartNoToSR7503").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#txtSuppplierNoSR7504").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#txtToSuppplierNoSR7504").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });

    $("#txtSuppplierCodeSR7601").select2({
        allowClear: true,
        placeholder: "Select "
    });
    $("#totxtSuppplierCodeSR7601").select2({
        allowClear: true,
        placeholder: "Select "
    });
    $("#txtSuppplierCodeSR7602").select2({
        allowClear: true,
        placeholder: "Select "
    });
    $("#totxtSuppplierCodeSR7602").select2({
        allowClear: true,
        placeholder: "Select "
    });

    $("#txt7300SuppplierNo").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#txt7300ToSuppplierNo").select2({
        allowClear: true,
        placeholder: "Select Supplier"
    });
    $("#txtDocumentNoSR7300").select2({
        allowClear: true,
        placeholder: "Select Document No"
    });
    $("#txtDocumentNoSR7300_to").select2({
        allowClear: true,
        placeholder: "Select Document No"
    });

    $("#txtPartNoSR7301").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#txtPartNoToSR7301").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#txtCustomerPoSR7301").select2({
        allowClear: true,
        placeholder: "Select Cust. PO No"
    });
    $("#txtCustomerPoToSR7301").select2({
        allowClear: true,
        placeholder: "Select Cust. PO No"
    });

    $("#txtDocumentNoSR7302").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });
    $("#txtDocumentNoToSR7302").select2({
        allowClear: true,
        placeholder: "Select Document No",
    });

    $("#txtPartNoSR7302").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });
    $("#txtPartNoToSR7302").select2({
        allowClear: true,
        placeholder: "Select Part No"
    });

    $("#txtPartGrpSR7503").select2({
        allowClear: true,
        placeholder: "Select Category"
    });
    $("#txtPartGrpToSR7503").select2({
        allowClear: true,
        placeholder: "Select Category"
    });

    $("#txtDocNoFromSR7401").select2({
        allowClear: true,
        placeholder: "Select Document No"
    });
    $("#txtDocNoToSR7401").select2({
        allowClear: true,
        placeholder: "Select Document No"
    });
    $("#txtCustPONoFromSR7401").select2({
        allowClear: true,
        placeholder: "Select Cust. PO No"
    });
    $("#txtCustPONoToSR7401").select2({
        allowClear: true,
        placeholder: "Select Cust. PO No"
    });

    $("#txtCustPONoFromSR7503").select2({
        allowClear: true,
        placeholder: "Select Cust. PO"
    });
    $("#txtCustPONoToSR7503").select2({
        allowClear: true,
        placeholder: "Select Cust. PO"
    });

    $("#fromPONo").select2({
        allowClear: true,
        placeholder: "Select P/O"
    });
    $("#toPONo").select2({
        allowClear: true,
        placeholder: "Select P/O"
    });
    $("#po_alternate_address").select2({
        allowClear: true,
        placeholder: "Select Address",
    });
    $("#do_alternate_address").select2({
        allowClear: true,
        placeholder: "Select Address",
    });
    $("#sr8500PartNo").select2({
        allowClear: true,
        placeholder: "Select Part No",
    });
    $("#sr8500ToPartNo").select2({
        allowClear: true,
        placeholder: "Select Part No",
    });
    $("#sr8500Location").select2({
        allowClear: true,
        placeholder: "Select Location",
    });

    get_inv_location();


    $("#loadpage").hide();

    //Set height of report view
    var header = $('.header');
    var divViewPDF = $('#divViewPDF');
    var height = ($(this).height()/8) - (header.height() * 2);
    divViewPDF.height(height);
    var window = $(window).on('resize', function () {
        divViewPDF.height(height);
    }).trigger('resize'); //on page load

    // =====================Print Order : get order_type and order_id=======================
    var hd_category_id = $('#hdCategoryId').val();
    var hd_order_type = $('#hdOrderType').val();
    var hd_order_id = $('#hdOrderID').val();
    var hd_print_type = $('#hdPrintType').val();
    var po_print_header = $('input[name=po-group-print-header]:checked').val();
    var do_print_header = $('input[name=do-group-print-header]:checked').val();
    var frViewPDF = $('#frViewPDF')[0];
    if (hd_order_type != 0 && hd_order_id != 0) {
        if (hd_order_type == 2) {//Print Purchase Order
            url = '/reports/print_po_order/' + hd_order_id + '/' + po_print_header + '/0/0/1/0';
            frViewPDF.setAttribute("src", url);
            divViewPDF.innerHTML = frViewPDF.outerHTML;

            $('#secReportList').css("display", "none");
            $('.filter').css("display", "none");
            $('#divPO').removeAttr("style");
            get_alter_address();
        }
        else if (hd_order_type == 6) {
            if (hd_print_type == 5) {
                // $('#do_pay_mode').css('display', 'block');
                $('#do_alt_address').css('display', 'block');
            } else {
                // $('#do_pay_mode').css('display', 'none');
                $('#do_alt_address').css('display', 'none');
            }
            if (hd_print_type == 2) {//Print Tax Invoice
                url = '/reports/print_tax_invoice/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 1) {//Print Delivery Order
                url = '/reports/print_do/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 3) {//Print Paking List
                url = '/reports/print_packing_list/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 4) {//Print Invoice
                url = '/reports/print_invoice/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 5) {//Print Shipping Invoice ver 1
                get_alter_address();
                url = '/reports/print_shipping_invoice/' + hd_order_id + '/' + do_print_header + '/0/0';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 6) {//Print Shipping Invoice ver 2
                get_alter_address();
                url = '/reports/print_shipping_invoice_2/' + hd_order_id + '/' + do_print_header + '/0/0';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
        }
    } else {
        $("#report_list").trigger('change');
    }
    // ====================================End print order==================================
});


function load_report_list() {
    var cat_id = $('#hdCategoryId').val();

    if (cat_id) {
        $.ajax({
            method: "POST",
            url: '/reports/get_reports_by_category/' + cat_id + '/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            responseTime: 200,
            success: function (json) {
                var report_list = $("#report_list");
                report_list.empty();
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        report_list.append('<option value="' + json[j][0] + '">' + json[j][0] + ' - ' + json[j][1] + '</option>');
                    }
                }
                report_list.trigger('change');
                $("#report_list").focus();
                $("#report_list").select2('open');
            }
        });
    }

}

$("#report_list").change(function () {
    var frViewPDF = $('#frViewPDF')[0];
    var divViewPDF = $('#divViewPDF')[0];

    var ord_code = "";
    $("#report_list option:selected").each(function () {
        ord_code = $(this).val();
        $('#hdReportId').val(ord_code);
    });

    //var cat_id = '';
    // $("#report_category option:selected").each(function () {
    //     cat_id = $(this).val();
    // });

    $('.filter').css("display", "none");
    $('.div' + ord_code + ' .default-date-picker').datepicker("setDate", '');
    $('.div' + ord_code).removeAttr("style");
    frViewPDF.setAttribute("src", "");
    // divViewPDF.innerHTML = frViewPDF.outerHTML;

    if (ord_code == '0') {
        $('.divButton').css("display", "none");
    }
    else {
        $('#divButton').removeAttr("style");
    }
    var hd_order_type = $('#hdOrderType').val();

    global_order_code = ord_code;

    if (global_order_code == 'SR7504') {
        if (!$('#is_confirm_2').data('select2')) {
            $('#is_confirm_2').select2({});
        }
    } else {
        if ($('#is_confirm_2').data('select2')) {
            $('#is_confirm_2').select2('destroy');
        }
    }
    //filter excel report
    switch(ord_code) {
        case 'SR7101':
        case 'SR7102':
        case 'SR7103':
        case 'SR7201':
        case 'SR7202':
        case 'SR7203':
        case 'SR7204':
        case 'SR7303':
        // case 'SR7205':
        case 'SR7402':
        case 'SR7403':
        case 'SR7404':
        case 'SR7501':
        case 'SR7502':
        case 'SR7503':
        case 'SR7504':
        case 'SR7603':
        case 'SR8600':
        case 'SR8601':
        case 'SR8602':
        case 'SR8603':
        case 'SR8500':
        case 'SL2100':
        case 'SL2200':
        case 'SL2201':
            if(hd_order_type != 2 && hd_order_type != 6){
                $('#export_excel').css('display', 'inline-block');
            }
            break;
        default:
            $('#export_excel').css('display', 'none');
    }

    if(ord_code == 'SR7502' || ord_code == 'SR7503') {
        $('#date_fromSR7503').datepicker('setDate', current_period_from);
        $('#date_toSR7503').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR7501' || ord_code == 'SR7504') {
        $('#date_fromSR7504').datepicker('setDate', current_period_from);
        $('#date_toSR7504').datepicker('setDate', current_period_to);

        date_from = $('#date_fromSR7504').val().split("-").reverse().join("-");
        date_to = $('#date_toSR7504').val().split("-").reverse().join("-");
        get_gr_supplier(date_from, date_to);
    }
    else if(ord_code == 'SR7101' || ord_code == 'SR7103') {
        $('#date_fromSA').datepicker('setDate', current_period_from);
        $('#date_toSA').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR7102') {
        $('#date_fromSR7102').datepicker('setDate', current_period_from);
        $('#date_toSR7102').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR8801') {
        $('#date_fromSR8801').datepicker('setDate', current_period_from);
        $('#date_toSR8801').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR8301') {
        $('#date_fromSR8301').datepicker('setDate', current_period_from);
        $('#date_toSR8301').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR7205') {
        $('#date_fromSR7205').datepicker('setDate', current_period_from);
        $('#date_toSR7205').datepicker('setDate', current_period_to);
    }
    else if(ord_code == 'SR7303') {
        $('#issue_fromSR7303').datepicker('setDate', current_period_from);
        $('#issue_toSR7303').datepicker('setDate', current_period_to);
        load_all_filters('issue');
    }
    else if(ord_code == 'SR7601') {
        $('#year_monthSR7601').datepicker('setDate', current_period);
    }
    else if(ord_code == 'SR7602') {
        $('#year_monthSR7602').datepicker('setDate', current_period);
    }
    else if(ord_code == 'SR7603') {
        $('#issue_fromSR7603').datepicker('setDate', current_period_from);
        $('#issue_toSR7603').datepicker('setDate', current_period_to);
        load_all_filters('issue');
    }
    else if(ord_code == 'SR7300') {
        $('#year_monthSR7300').datepicker('setDate', current_period);
        $('#divSR7301').css('display', 'none');
        $('#divSR7302').css('display', 'none');
    }
    else if(ord_code == 'SR7301') {
        $('#year_monthSR7300').datepicker('setDate', current_period);
        $('#divSR7301').css('display', 'block');
        $('#divSR7302').css('display', 'none');
    }
    else if(ord_code == 'SR7302') {
        $('#year_monthSR7300').datepicker('setDate', current_period);
        $('#divSR7301').css('display', 'none');
        $('#divSR7302').css('display', 'block');
    }
    else if(ord_code == 'SR8700' || ord_code == 'SR8700_1' || ord_code == 'SR8701' || ord_code == 'GL2200') {
        $('#divCurrentMonthCL2200').datepicker('setDate', current_period);
    }

    if(ord_code == 'SR7502') {
        $('#SR7502').css('display', 'none');
        $('#SR7502_more').css('display', 'none');
    } else {
        $('#SR7502').css('display', 'block');
        $('#SR7502_more').css('display', 'block');
    }
    if(ord_code == 'SR7501') {
        $('#SR7501').css('display', 'none');
    } else {
        $('#SR7501').css('display', 'block');
    }

    if(ord_code == 'SR8600' || ord_code == 'SR8601' || ord_code == 'SR8602' || ord_code == 'SR8603') {
        $('#inputFromSR8600').datepicker('setDate', current_period);
        $('#inputToSR8600').datepicker('setDate', current_period);
    }

    if(ord_code == 'SR8800') {
        $('#SR8800_label_from').text('Invoice Date From');
        $('#SR8800_label_to').text('Invoice Date To');
        $('#date_fromSR7402').datepicker('setDate', current_period_from);
        $('#date_toSR7402').datepicker('setDate', current_period_to);
    } else {
        $('#SR8800_label_from').text('Wanted Date From');
        $('#SR8800_label_to').text('Wanted Date To');
    }

    if(ord_code == 'SR8300') {
        $('#SR8400_customer_select').css('display', 'none');
        $('#SR8300_supplier_select').css('display', 'block');
        $('#date_fromSR834').datepicker('setDate', current_period_from);
        $('#date_toSR834').datepicker('setDate', current_period_to);
    } 
    else if(ord_code == 'SR8400') {
        $('#SR8400_customer_select').css('display', 'block');
        $('#SR8300_supplier_select').css('display', 'none');
        $('#date_fromSR834').datepicker('setDate', current_period_from);
        $('#date_toSR834').datepicker('setDate', current_period_to);
    }

    else if(ord_code == 'SL3300' || ord_code == 'SL3301') {
        $('#date_fromSL330').datepicker('setDate', current_period_from);
        $('#date_toSL330').datepicker('setDate', current_period_to);
        if (ord_code == 'SL3300') {
            $('#SL330_customer_po_select').css('display', 'none');
        } else {
            $('#SL330_customer_po_select').css('display', 'block');
        }
    }
    else if(ord_code == 'SL3A00' || ord_code == 'SL3A01') {
        $('#date_fromSL3A0').datepicker('setDate', current_period_from);
        $('#date_toSL3A0').datepicker('setDate', current_period_to);
        if (ord_code == 'SL3A00') {
            $('#SL3A0_customer_po_select').css('display', 'none');
        } else {
            $('#SL3A0_customer_po_select').css('display', 'block');
        }
    }
    else if(ord_code == 'SR7401') {
        get_oustanding_sales('0', '0', '0', '0', '0', '0', "document_no");
        get_oustanding_sales('0', '0', '0', '0', '0', '0', "customer_po");
    }
    else if(ord_code == 'SR7402') {
        get_customer_list('0', '0', 'outstanding_so');
    }
    else if(ord_code == 'SR7403') {
        get_customer_list('0', '0', 'outstanding_so');
        get_supplier_list(ord_code, '0', '0')
    }
    else if(ord_code == 'SR7404') {
        get_customer_list('0', '0', 'outstanding_so');
        get_so_part_no();
    }
    else if(ord_code == 'SR7101') {
        $('#sa_customer_div').css('display', 'none');
        date_from = $('#date_fromSA').val().split("-").reverse().join("-");
        date_to = $('#date_toSA').val().split("-").reverse().join("-");
        get_sales_analysis_data(date_from, date_to);
    }
    else if(ord_code == 'SR7103') {
        $('#sa_customer_div').css('display', 'block');
        date_from = $('#date_fromSA').val().split("-").reverse().join("-");
        date_to = $('#date_toSA').val().split("-").reverse().join("-");
        get_sales_analysis_data(date_from, date_to);
    }
    else if(ord_code == 'SR7204') {
        get_supplier_list(ord_code);
        get_po_part_no(ord_code);
    }
    else if(ord_code == 'SR7201') {
        get_document_no();
    }
    else if(ord_code == 'SR7203' || ord_code == 'SR7202') {
        get_supplier_list(ord_code);
        if(ord_code == 'SR7203') {
            $("#lbSR7203Supplier").trigger('change');
        }
    }
    else if (ord_code == 'SR8500') {
        get_location_part_no();
    }
    else if (ord_code == 'CL2400') {
        sfl_supplier_list = supplier_list;
        $("#lbCL2400Supplier").empty();
        $("#lbCL2400ToSupplier").empty();
        $("#lbCL2400Supplier").append('<option value="">Select Supplier</option>');
        $("#lbCL2400ToSupplier").append('<option value="">Select Supplier</option>');
        for (j = 0; j < supplier_list.length; j++) {
            $("#lbCL2400Supplier").append('<option value="' + supplier_list[j][0] + '">' + supplier_list[j][1] + '</option>');
            $("#lbCL2400ToSupplier").append('<option value="' + supplier_list[j][0] + '">' + supplier_list[j][1] + '</option>');
        }
    }
    else if (ord_code == 'DL2400') {
        cfl_customer_list = customer_list;
        $("#lbDL2400Supplier").empty();
        $("#lbDL2400ToSupplier").empty();
        $("#lbDL2400Supplier").append('<option value="">Select Customer</option>');
        $("#lbDL2400ToSupplier").append('<option value="">Select Customer</option>');
        for (j = 0; j < customer_list.length; j++) {
            $("#lbDL2400Supplier").append('<option value="' + customer_list[j][0] + '">' + customer_list[j][1] + '</option>');
            $("#lbDL2400ToSupplier").append('<option value="' + customer_list[j][0] + '">' + customer_list[j][1] + '</option>');
        }
    }

    update_tab_travel(ord_code);
});

function update_fields(ord_code){
    let date_from, date_to;
    switch(ord_code) {
        case 'SL3A00':
            date_from = $('#date_fromSL3A0').val().split("-").reverse().join("-");
            date_to = $('#date_toSL3A0').val().split("-").reverse().join("-");
            get_document_no(date_from, date_to);
            get_SL3_data(date_from, date_to);
            break;
        case 'SL3300':
            date_from = $('#date_fromSL330').val().split("-").reverse().join("-");
            date_to = $('#date_toSL330').val().split("-").reverse().join("-");
            get_document_no(date_from, date_to);
            get_SL3_data(date_from, date_to);
            break;
        case 'SL3A01':
            date_from = $('#date_fromSL3A0').val().split("-").reverse().join("-");
            date_to = $('#date_toSL3A0').val().split("-").reverse().join("-");
            get_document_no(date_from, date_to);
            get_SL3_data(date_from, date_to);
            get_customer_po(date_from, date_to);
            break;
        case 'SL3301':
            date_from = $('#date_fromSL330').val().split("-").reverse().join("-");
            date_to = $('#date_toSL330').val().split("-").reverse().join("-");
            get_document_no(date_from, date_to);
            get_SL3_data(date_from, date_to);
            get_customer_po(date_from, date_to);
            break;
        case 'SR7102':
            date_from = $('#date_fromSR7102').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7102').val().split("-").reverse().join("-");
            get_part_group(date_from, date_to);
            break;
        case 'SR7201':
            date_from = $('#date_fromSR7201').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7201').val().split("-").reverse().join("-");
            get_document_no(date_from, date_to);
            break;
        case 'SR8801':
            date_from = $('#date_fromSR8801').val().split("-").reverse().join("-");
            date_to = $('#date_toSR8801').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            break;
        case 'SR7202':
            date_from = $('#date_fromSR7202').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7202').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            break;
        case 'SR7203':
            date_from = $('#date_fromSR7203').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7203').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            $("#lbSR7203Supplier").trigger('change');
            break;
        case 'SR7204':
            date_from = $('#date_fromSR7204').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7204').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            get_po_part_no(ord_code, date_from, date_to);
            break;
        case 'SR7205':
            date_from = $('#date_fromSR7205').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7205').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            $("#lbSR7205Supplier").trigger('change');
            get_po_part_no(ord_code, date_from, date_to);
            break;
        case 'SA':
            date_from = $('#date_fromSA').val().split("-").reverse().join("-");
            date_to = $('#date_toSA').val().split("-").reverse().join("-");
            get_sales_analysis_data(date_from, date_to);
            break;
        case 'SR7404':
            date_from = $('#date_fromSR7404').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7404').val().split("-").reverse().join("-");
            get_customer_list(date_from, date_to, data_type);
            get_so_part_no(date_from, date_to);
            break;
        case 'SR8301':
            date_from = $('#date_fromSR8301').val().split("-").reverse().join("-");
            date_to = $('#date_toSR8301').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            $("#lbSR8301Supplier").trigger('change');
            break;
        case 'SR7403':
            date_from = $('#date_fromSR7403').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7403').val().split("-").reverse().join("-");
            data_type = 'sales invoice';
            get_customer_list(date_from, date_to, data_type);
            get_supplier_list(ord_code, date_from, date_to);
        case 'SR7402':
        case 'SR8800':
            date_from = $('#date_fromSR7402').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7402').val().split("-").reverse().join("-");
            data_type = ord_code == 'SR7402' ? 'outstanding_so' : 'sales invoice';
            get_customer_list(date_from, date_to, data_type);
            break;
        case 'SR8400':
            date_from = $('#date_fromSR834').val().split("-").reverse().join("-");
            date_to = $('#date_toSR834').val().split("-").reverse().join("-");
            data_type = 'sales order';
            get_customer_list(date_from, date_to, data_type);
            $('#lbSR8400Customer').trigger('change');
            break;
        case 'SR8300':
            date_from = $('#date_fromSR834').val().split("-").reverse().join("-");
            date_to = $('#date_toSR834').val().split("-").reverse().join("-");
            get_supplier_list(ord_code, date_from, date_to);
            $('#lbSR8300Supplier').trigger('change');
            break;
        case 'SR7502':
        case 'SR7503':
            date_from = $('#date_fromSR7503').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7503').val().split("-").reverse().join("-");
            get_part_no(date_from, date_to);
            break;
        case 'SR7501':
        case 'SR7504':
            date_from = $('#date_fromSR7504').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7504').val().split("-").reverse().join("-");
            get_gr_supplier(date_from, date_to);
            break;
        case 'SR7601':
            year_month = $('#year_monthSR7601').val().split("-").reverse().join("-");
            get_part_category(year_month);
            break;
        case 'SR7602':
            year_month = $('#year_monthSR7602').val().split("-").reverse().join("-");
            get_sales_customer(year_month);
            break;
        case 'SR7300':
            year_month = $('#year_monthSR7300').val().split("-").reverse().join("-");
            get_monthly_purchase('SR7300', year_month, '0', 'supplier');
            // $("#txt7300SuppplierNo").trigger('change');
            break;
        case 'SR7301':
            year_month = $('#year_monthSR7300').val().split("-").reverse().join("-");
            get_monthly_purchase('SR7301', year_month, '0', 'customer_po');
            // $("#txtCustomerPoSR7301").trigger('change');
            break;
        case 'SR7302':
            year_month = $('#year_monthSR7300').val().split("-").reverse().join("-");
            get_monthly_purchase('SR7302', year_month, '0', 'part_no');
            // $("#txtDocumentNoSR7302").trigger('change');
            break;
        case 'SR7401':
            date_from = $('#date_fromSR7401').val().split("-").reverse().join("-");
            date_to = $('#date_toSR7401').val().split("-").reverse().join("-");

            //get_oustanding_sales(date_from, date_to, '0', '0', '0', '0', "document_no_from");
            get_oustanding_sales(date_from, date_to, '0', '0', '0', '0', "document_no");
            get_oustanding_sales(date_from, date_to, '0', '0', '0', '0', "customer_po");
            $("#txtDocNoFromSR7401").trigger('change');
            break;
    }
}

$('#lbSR8400Customer').on('change', function(){
    var customer_id = $('#lbSR8400Customer').val();
    if(!customer_id) {
        customer_id = '0'; 
    }
    date_from = $('#date_fromSR834').val().split("-").reverse().join("-");
    date_to = $('#date_toSR834').val().split("-").reverse().join("-");
    get_document_numbers(date_from, date_to, customer_id);
});

$('#lbSR8300Supplier').on('change', function(){
    var customer_id = $('#lbSR8300Supplier').val();
    if(!customer_id) {
        customer_id = '0'; 
    }
    date_from = $('#date_fromSR834').val().split("-").reverse().join("-");
    date_to = $('#date_toSR834').val().split("-").reverse().join("-");
    get_document_numbers(date_from, date_to, customer_id);
});


var year_period_day = moment().format("DD-MM-YYYY");
$('.default-date-picker').bind('keyup', function (event) {
    if (event.which != 13) {
        temp_date = $(this).val();
        valid_date = moment(temp_date, "DD-MM-YYYY", true).isValid();
        if (valid_date) {
            year_period_day = temp_date;
            //$(this).datepicker('setDate', year_period_day);
            move_next_elem(this, 1);
        }
        return true;
    }
});
$('.default-date-picker').bind('keydown', function (event) {
    if (event.which == 13) {
        setTimeout(() => {
            $(this).datepicker('setDate', year_period_day);
            move_next_elem(this, 1);
        }, 100);
        return false;
    } else {
        adjust_input_date(this);
    }
});

$('.default-date-picker').on('blur', function(event) {
    temp_date = $(this).val();
    valid_date = moment(temp_date, "DD-MM-YYYY", true).isValid();
    if (valid_date) {
        //$(this).datepicker('setDate', temp_date);
    } else if (temp_date){
        $(this).datepicker('setDate', year_period_day);
    }
});

var year_period = moment().format("MM-YYYY");
$('#sandbox-container input').bind('keyup', function (event) {
    if (event.which != 13) {
        temp_date = $(this).val();
        valid_date = moment(temp_date, "MM-YYYY", true).isValid();
        if (valid_date) {
            year_period = temp_date;
            move_next_elem(this, 1);
        }
        return true;
    }
});
$('#sandbox-container input').bind('keydown', function (event) {
    if (event.which == 13) {
        $(this).val(moment(year_period, "MM-YYYY").format("MM-YYYY"));
        move_next_elem(this, 1);
        return false;
    } else {
        adjust_input_month_year(this);
    }
});

$('#sandbox-container input').on('blur', function (event) {
    temp_date = $(this).val();
    valid_date = moment(temp_date, "MM-YYYY", true).isValid();
    if (valid_date) {
        //$(this).datepicker('setDate', temp_date);
    } else if (temp_date){
        $(this).val(moment(year_period, "MM-YYYY").format("MM-YYYY"));
    }
});

var remove_address = 0;
$("#id_remove_address").on('change', function(e){
    if($(this).is(':checked')){
        pop_ok_cancel_dialog("Please Confirm",
            "Do you want to remove Ship to address?",
            function () {
                $('#po_alternate_address').val('').trigger('change');
                remove_address = 1;
            },
            function () {
                remove_address = 0;
                $('#id_remove_address').attr('checked', false);
            }
        );
    } else {
        remove_address = 0;
    }
});

$('#po_alternate_address').on('change', function(e){
    let addr = $('#po_alternate_address').val();
    if(addr != '' && addr != undefined && addr != null) {
        remove_address = 0;
        $('#id_remove_address').attr('checked', false);
    }
});

$("#fromPONo").on('change', function(e){
    remove_address = 0;
    $('#id_remove_address').attr('checked', false);
});

$("#year_monthSR7300").change(function () {
    var year_month = $('#year_monthSR7300');
    adjust_year_month(year_month);
    update_fields(global_order_code);
    //$('#txt7300SuppplierNo').select2('open');
});

// $("#txt7300SuppplierNo").change(function () {
//     var year_month = $('#year_monthSR7300').val().split("-").reverse().join("-");

//     var supplier_id = "0";
//     $("#txt7300SuppplierNo option:selected").each(function () {
//         if ($(this).val() != '')
//             supplier_id = $(this).val();
//     });

//     get_monthly_purchase('SR7300', year_month, supplier_id, 'document_no');
// });

$("#year_monthSR7301").change(function () {
    var year_month = $('#year_monthSR7301');
    adjust_year_month(year_month);
    update_fields(global_order_code);
    $('#txtCustomerPoSR7301').select2('open');
});

// $("#txtCustomerPoSR7301").change(function () {
//     var year_month = $('#year_monthSR7301').val().split("-").reverse().join("-");

//     var parameter_id = "0";
//     $("#txtCustomerPoSR7301 option:selected").each(function () {
//         if ($(this).val() != '')
//             parameter_id = $(this).val();
//     });

//     get_monthly_purchase('SR7301', year_month, parameter_id, 'part_no_cus_po');
// });

$("#year_monthSR7302").change(function () {
    var year_month = $('#year_monthSR7302');
    adjust_year_month(year_month);
    update_fields(global_order_code);
    $('#txtDocumentNoSR7302').select2('open');
});

// $("#txtDocumentNoSR7302").change(function () {
//     var year_month = $('#year_monthSR7302').val().split("-").reverse().join("-");

//     var parameter_id = "0";
//     $("#txtDocumentNoSR7302 option:selected").each(function () {
//         if ($(this).val() != '')
//             parameter_id = $(this).val();
//     });

//     get_monthly_purchase('SR7302', year_month, parameter_id, 'part_no_doc_no');
// });

$("#po_date_from").change(function () {
    ajax_po_date();
});
$("#po_date_to").change(function () {
    ajax_po_date();
});

function ajax_po_date(){
    var date_from = $('#po_date_from');
    var date_to = $('#po_date_to');
    adjust_date(date_from, date_to);
    date_from = $('#po_date_from').val().split("-").reverse().join("-");
    date_to = $('#po_date_to').val().split("-").reverse().join("-");
    get_po_data(date_from, date_to);
}

function ajax_SL3A0(){
    var date_from = $('#date_fromSL3A0');
    var date_to = $('#date_toSL3A0');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSL3A0").change(function () {
//     if($("#date_fromSL3A0").val()) {
//         ajax_SL3A0();
//     }
// });

$("#date_fromSL3A0").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SL3A0();
    }
});

// $("#date_toSL3A0").change(function () {
//     if($("#date_toSL3A0").val()) {
//         ajax_SL3A0();
//     }
// });

$("#date_toSL3A0").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SL3A0();
    }
});

function ajax_SL330(){
    var date_from = $('#date_fromSL330');
    var date_to = $('#date_toSL330');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSL330").change(function () {
//     if($("#date_fromSL330").val()) {
//         ajax_SL330();
//     }
// });

$("#date_fromSL330").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SL330();
    }
});

// $("#date_toSL330").change(function () {
//     if($("#date_toSL330").val()) {
//         ajax_SL330();
//     }
// });

$("#date_toSL330").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SL330();
    }
});

function ajax_SR7201(){
    var date_from = $('#date_fromSR7201');
    var date_to = $('#date_toSR7201');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7201").change(function () {
//     if($("#date_fromSR7201").val()) {
//         ajax_SR7201();
//         $("#date_toSR7201").focus();
//     }
// });

$("#date_fromSR7201").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7201();
        $("#date_toSR7201").focus();
    }
});

// $("#date_toSR7201").change(function () {
//     if($("#date_toSR7201").val()) {
//         ajax_SR7201();
//         $('#lbSR7201Document').select2('open');
//     }
// });

$("#date_toSR7201").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7201();
        $('#lbSR7201Document').select2('open');
    }
});

function ajax_SA(){
    var date_from = $('#date_fromSA');
    var date_to = $('#date_toSA');
    adjust_date(date_from, date_to);
    update_fields('SA');
}

// $("#date_fromSA").change(function () {
//     if($("#date_fromSA").val()) {
//         ajax_SA();
//     }
// });

$("#date_fromSA").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SA();
    }
});

// $("#date_toSA").change(function () {
//     if($("#date_toSA").val()) {
//         ajax_SA();
//     }
// });

$("#date_toSA").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SA();
    }
});

function ajax_SR7202(){
    var date_from = $('#date_fromSR7202');
    var date_to = $('#date_toSR7202');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7202").change(function () {
// //     if($("#date_fromSR7202").val()) {
// //         ajax_SR7202();
// //         $("#date_toSR7202").focus();
// //     }
// // });

$("#date_fromSR7202").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7202();
        $("#date_toSR7202").focus();
    }
});

// $("#date_toSR7202").change(function () {
//     if($("#date_toSR7202").val()) {
//         ajax_SR7202();
//         $('#lbSR7202Supplier').select2('open');
//     }
// });

$("#date_toSR7202").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7202();
        $('#lbSR7202Supplier').select2('open');
    }
});

function ajax_SR8801(){
    var date_from = $('#date_fromSR8801');
    var date_to = $('#date_toSR8801');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR8801").change(function () {
//     if($("#date_fromSR8801").val()) {
//         ajax_SR8801();
//     }
// });

$("#date_fromSR8801").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR8801();
    }
});

// $("#date_toSR8801").change(function () {
//     if($("#date_toSR8801").val()) {
//         ajax_SR8801();
//     }
// });

$("#date_toSR8801").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR8801();
    }
});

function ajax_SR7402(){
    var date_from = $('#date_fromSR7402');
    var date_to = $('#date_toSR7402');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7402").change(function () {
//     if($("#date_fromSR7402").val()) {
//         ajax_SR7402();
//         $("#date_toSR7402").focus();
//     }
// });

$("#date_fromSR7402").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7402();
        $("#date_toSR7402").focus();
    }
});

// $("#date_toSR7402").change(function () {
//     if($("#date_toSR7402").val()) {
//         ajax_SR7402();
//         $('#lbSR7402Customer').select2('open');
//     }
// });

$("#date_toSR7402").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7402();
        //$('#lbSR7402Customer').select2('open');
    }
});

function ajax_SR7403(){
    var date_from = $('#date_fromSR7403');
    var date_to = $('#date_toSR7403');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7403").change(function () {
//     if($("#date_fromSR7403").val()) {
//         ajax_SR7403();
//         $("#date_toSR7403").focus();
//     }
// });

$("#date_fromSR7403").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7403();
        $("#date_toSR7403").focus();
    }
});

// $("#date_toSR7403").change(function () {
//     if($("#date_toSR7403").val()) {
//         ajax_SR7403();
//     }
// });

$("#date_toSR7403").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7403();
    }
});

function ajax_SR7401(){
    var date_from = $('#date_fromSR7401');
    var date_to = $('#date_toSR7401');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7401").change(function () {
//     if($("#date_fromSR7401").val()) {
//         ajax_SR7401();
//         $("#date_toSR7401").focus();
//     }
// });

$("#date_fromSR7401").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7401();
        $("#date_toSR7401").focus();
    }
});

// $("#date_toSR7401").change(function () {
//     if($("#date_toSR7401").val()) {
//         ajax_SR7401();
//         $('#txtDocNoFromSR7401').select2('open');
//     }
// });

$("#date_toSR7401").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7401();
        $('#txtDocNoFromSR7401').select2('open');
    }
});

// $("#txtDocNoFromSR7401").change(function () {
//     var date_from = $('#date_fromSR7401').val().split("-").reverse().join("-");
//     var date_to = $('#date_toSR7401').val().split("-").reverse().join("-");

//     var doc_no_from = "0";
//     $("#txtDocNoFromSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             doc_no_from = $(this).val();
//     });

//     get_oustanding_sales(date_from, date_to, doc_no_from, '0', '0', '0', "document_no_to");
//     $("#txtDocNoToSR7401").trigger('change');
// });

// $("#txtDocNoToSR7401").change(function () {
//     var date_from = $('#date_fromSR7401').val().split("-").reverse().join("-");
//     var date_to = $('#date_toSR7401').val().split("-").reverse().join("-");

//     var doc_no_from = "0";
//     $("#txtDocNoFromSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             doc_no_from = $(this).val();
//     });

//     var doc_no_to = "0";
//     $("#txtDocNoToSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             doc_no_to = $(this).val();
//     });

//     get_oustanding_sales(date_from, date_to, doc_no_from, doc_no_to, '0', '0', "customer_po_from");
//     $("#txtCustPONoFromSR7401").trigger('change');
// });

// $("#txtCustPONoFromSR7401").change(function () {
//     var date_from = $('#date_fromSR7401').val().split("-").reverse().join("-");
//     var date_to = $('#date_toSR7401').val().split("-").reverse().join("-");

//     var doc_no_from = "0";
//     $("#txtDocNoFromSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             doc_no_from = $(this).val();
//     });

//     var doc_no_to = "0";
//     $("#txtDocNoToSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             doc_no_to = $(this).val();
//     });

//     var cus_po_from = "0";
//     $("#txtCustPONoFromSR7401 option:selected").each(function () {
//         if ($(this).val() != '')
//             cus_po_from = $(this).val();
//     });

//     get_oustanding_sales(date_from, date_to, doc_no_from, doc_no_to, cus_po_from, '0', "customer_po_to");
// });


function ajax_SR7603_issue(){
    var date_from = $('#issue_fromSR7603');
    var date_to = $('#issue_toSR7603');
    adjust_date(date_from, date_to);
    load_all_filters('issue');
}

// $("#issue_fromSR7603").change(function () {
//     if($("#issue_fromSR7603").val()) {
//         ajax_SR7603_issue();
//     }
// });

$("#issue_fromSR7603").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7603_issue();
    }
});

// $("#issue_toSR7603").change(function () {
//     if($("#issue_toSR7603").val()) {
//         ajax_SR7603_issue();
//     }
// });

$("#issue_toSR7603").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7603_issue();
    }
});

function ajax_SR7603_wanted(){
    var date_from = $('#wanted_fromSR7603');
    var date_to = $('#wanted_toSR7603');
    adjust_date(date_from, date_to);
    load_all_filters('wanted');
}

// $("#wanted_fromSR7603").change(function () {
//     if($("#wanted_fromSR7603").val()) {
//         ajax_SR7603_wanted();
//         $("#wanted_toSR7603").focus();
//     }
// });

$("#wanted_fromSR7603").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7603_wanted();
        $("#wanted_toSR7603").focus();
    }
});

// $("#wanted_toSR7603").change(function () {
//     if($("#wanted_toSR7603").val()) {
//         ajax_SR7603_wanted();
//         $('#SR7603_customer').select2('open');
//     }
// });

$("#wanted_toSR7603").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7603_wanted();
        $('#SR7603_customer').select2('open');
    }
});

function ajax_SR7303_issue(){
    var date_from = $('#issue_fromSR7303');
    var date_to = $('#issue_toSR7303');
    adjust_date(date_from, date_to);
    load_all_filters('issue');
}

// $("#issue_fromSR7303").change(function () {
//     if($("#issue_fromSR7303").val()) {
//         ajax_SR7303_issue();
//     }
// });

$("#issue_fromSR7303").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7303_issue();
    }
});

// $("#issue_toSR7303").change(function () {
//     if($("#issue_toSR7303").val()) {
//         ajax_SR7303_issue();
//     }
// });

$("#issue_toSR7303").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7303_issue();
    }
});


function ajax_SR7303_wanted(){
    var date_from = $('#wanted_fromSR7303');
    var date_to = $('#wanted_toSR7303');
    adjust_date(date_from, date_to);
    load_all_filters('wanted');
}

// $("#wanted_fromSR7303").change(function () {
//     if($("#wanted_fromSR7303").val()) {
//         ajax_SR7303_wanted();
//         $("#wanted_toSR7303").focus();
//     }
// });

$("#wanted_fromSR7303").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7303_wanted();
        $("#wanted_toSR7303").focus();
    }
});

// $("#wanted_toSR7303").change(function () {
//     if($("#wanted_toSR7303").val()) {
//         ajax_SR7303_wanted();
//         $('#SR7303_supplier').select2('open');
//     }
// });

$("#wanted_toSR7303").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7303_wanted();
        $('#SR7303_supplier').select2('open');
    }
});

function ajax_SR7203(){
    var date_from = $('#date_fromSR7203');
    var date_to = $('#date_toSR7203');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

// $("#date_fromSR7203").change(function () {
//     if($("#date_fromSR7203").val()) {
//         ajax_SR7203();
//         $("#date_toSR7203").focus();
//     }
// });

$("#date_fromSR7203").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7203();
        $("#date_toSR7203").focus();
    }
});

// $("#date_toSR7203").change(function () {
//     if($("#date_toSR7203").val()) {
//         ajax_SR7203();
//         $('#lbSR7203Supplier').select2('open');
//     }
// });

$("#date_toSR7203").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7203();
        $('#lbSR7203Supplier').select2('open');
    }
});

function ajax_SR8301(){
    var date_from = $('#date_fromSR8301');
    var date_to = $('#date_toSR8301');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR8301").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR8301();
    }
});

$("#date_toSR8301").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR8301();
    }
});

function ajax_SR7205(){
    var date_from = $('#date_fromSR7205');
    var date_to = $('#date_toSR7205');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR7205").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7205();
    }
});

$("#date_toSR7205").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7205();
    }
});

function ajax_SR7204(){
    var date_from = $('#date_fromSR7204');
    var date_to = $('#date_toSR7204');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR7204").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7204();
        $("#date_toSR7204").focus();
    }
});

$("#date_toSR7204").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7204();
        $('#lbSR7204Supplier').select2('open');
    }
});

function ajax_SR7404(){
    var date_from = $('#date_fromSR7404');
    var date_to = $('#date_toSR7404');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR7404").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7404();
        $("#date_toSR7404").focus();
    }
});

$("#date_toSR7404").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7404();
        $('#lbSR7404Customer').select2('open');
    }
});

function ajax_SR7503(){
    var date_from = $('#date_fromSR7503');
    var date_to = $('#date_toSR7503');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR7503").on('changeDate', function (ev) {
    var date_from_valid = moment($("#date_fromSR7503").val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7503();
    }
});

$("#date_toSR7503").on('changeDate', function (ev) {
    var date_from_valid = moment($("#date_toSR7503").val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7503();
    }
});

// $("#date_toSR7503").change(function () {
//     if($("#date_toSR7503").val()) {
//         ajax_SR7503();
//     }
// });

function ajax_SR8500(){
    var date_from = $('#date_fromSR8500');
    var date_to = $('#date_toSR8500');
    adjust_date(date_from, date_to);
}

$("#date_fromSR8500").change(function () {
    if($("#date_fromSR8500").val()) {
        ajax_SR8500();
        $("#date_toSR8500").focus();
    }
});

$("#date_toSR8500").change(function () {
    if($("#date_toSR8500").val()) {
        ajax_SR8500();
        $('#sr8500Location').select2('open');
    }
});

$("#year_monthSR7601").change(function () {
    var year_month = $('#year_monthSR7601');
    adjust_year_month(year_month);
    update_fields('SR7601');
    //$('#txtSuppplierCodeSR7601').select2('open');
});

$("#year_monthSR7602").change(function () {
    var year_month = $('#year_monthSR7602');
    adjust_year_month(year_month);
    update_fields('SR7602');
    $('#txtSuppplierCodeSR7602').select2('open');
});

$('#inputFromSR8600').on('change', function() {
    $('#inputToSR8600').focus();
});

function adjust_year_month(year_month){
   var pattern =/^([0-9]{1,2})\-([0-9]{4})$/;
   if (pattern.test(year_month.val()) == false){
        var today = new Date();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();

        if(mm<10) {
            mm = '0'+mm
        }
        year_month.val(mm + '-' + yyyy);
   }
}

function ajax_SR7504(){
    var date_from = $('#date_fromSR7504');
    var date_to = $('#date_toSR7504');
    adjust_date(date_from, date_to);
    update_fields('SR7504');
}

// $("#date_fromSR7504").change(function () {
//     if($("#date_fromSR7504").val()) {
//         ajax_SR7504();
//     }
// });
//
// $("#date_toSR7504").change(function () {
//     if($("#date_toSR7504").val()) {
//         ajax_SR7504();
//     }
// });


$("#date_fromSR7504").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7504();
    }
});

$("#date_toSR7504").on('changeDate', function (ev) {
    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
    if (date_from_valid){
        ajax_SR7504();
    }
});

function ajax_SR834(){
    var date_from = $('#date_fromSR834');
    var date_to = $('#date_toSR834');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR834").change(function () {
    if($("#date_fromSR834").val()) {
        ajax_SR834();
    }
});

$("#date_toSR834").change(function () {
    if($("#date_toSR834").val()) {
        ajax_SR834();
    }
});

function ajax_SR7102(){
    var date_from = $('#date_fromSR7102');
    var date_to = $('#date_toSR7102');
    adjust_date(date_from, date_to);
    update_fields(global_order_code);
}

$("#date_fromSR7102").change(function () {
    if($("#date_fromSR7102").val()) {
        ajax_SR7102();
    }
});

$("#date_toSR7102").change(function () {
    if($("#date_toSR7102").val()) {
        ajax_SR7102();
    }
});

$("#lbSR7203Supplier").change(function () {

    var date_from = $('#date_fromSR7203').val().split("-").reverse().join("-");
    var date_to = $('#date_toSR7203').val().split("-").reverse().join("-");

    var supplier_id = "0";
    $("#lbSR7203Supplier option:selected").each(function () {
        if ($(this).val() != '')
            supplier_id = $(this).val();
    });

    get_customer_po(date_from, date_to, supplier_id, global_order_code);

});

$("#lbSR8301Supplier").change(function () {

    var date_from = $('#date_fromSR8301').val().split("-").reverse().join("-");
    var date_to = $('#date_toSR8301').val().split("-").reverse().join("-");

    var supplier_id = "0";
    $("#lbSR8301Supplier option:selected").each(function () {
        if ($(this).val() != '')
            supplier_id = $(this).val();
    });

    get_customer_po(date_from, date_to, supplier_id, global_order_code);

});

$("#lbSR7205Supplier").change(function () {

    var date_from = $('#date_fromSR7205').val().split("-").reverse().join("-");
    var date_to = $('#date_toSR7205').val().split("-").reverse().join("-");

    var supplier_id = "0";
    $("#lbSR7205Supplier option:selected").each(function () {
        if ($(this).val() != '')
            supplier_id = $(this).val();
    });

});

var oir_part_list = [];
var oir_document_list = [];
var oir_customer_list = [];
var oir_customer_po_list = [];
function load_all_filters(date_type) {
    var date_from = '';
    var date_to = '';
    if(global_order_code == 'SR7603') {
        if(date_type == 'issue') {
            date_from = $('#issue_fromSR7603').val().split("-").reverse().join("-");
            date_to = $('#issue_toSR7603').val().split("-").reverse().join("-");
        } else {
            date_from = $('#wanted_fromSR7603').val().split("-").reverse().join("-");
            date_to = $('#wanted_toSR7603').val().split("-").reverse().join("-");
        }
    } else {
        if(date_type == 'issue') {
            date_from = $('#issue_fromSR7303').val().split("-").reverse().join("-");
            date_to = $('#issue_toSR7303').val().split("-").reverse().join("-");
        } else {
            date_from = $('#wanted_fromSR7303').val().split("-").reverse().join("-");
            date_to = $('#wanted_toSR7303').val().split("-").reverse().join("-");
        }
    }
    if (!date_from){
        date_from = '0';
    }
  
    if (!date_to){
        date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_report_filters/' + date_from + '/' + date_to + '/' + global_order_code + '/' + date_type + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if (json) {
                oir_part_list = json.part_list;
                oir_document_list = json.document_list;
                oir_customer_list = json.customer_list;
                oir_customer_po_list = json.customer_po_list;
                if(global_order_code == 'SR7603') {
                    $("#SR7603_customer").empty();
                    $("#SR7603_customer_to").empty();
                    $("#SR7603_customer").append('<option value="">Select Customer</option>');
                    $("#SR7603_customer_to").append('<option value="">Select Customer</option>');
                    $("#SR7603_document").empty();
                    $("#SR7603_document_to").empty();
                    $("#SR7603_document").append('<option value="">Select Document</option>');
                    $("#SR7603_document_to").append('<option value="">Select Document</option>');
                    $("#SR7603_part_no").empty();
                    $("#SR7603_part_no_to").empty();
                    $("#SR7603_part_no").append('<option value="">Select Part No</option>');
                    $("#SR7603_part_no_to").append('<option value="">Select Part No</option>');
                    $("#SR7603_customer_po").empty();
                    $("#SR7603_customer_po_to").empty();
                    $("#SR7603_customer_po").append('<option value="">Select Cust. PO</option>');
                    $("#SR7603_customer_po_to").append('<option value="">Select Cust. PO</option>');
                    for (j = 0; j < oir_part_list.length; j++) {
                        $("#SR7603_part_no").append('<option value="' + oir_part_list[j][0] + '">' + oir_part_list[j][1] + '</option>');
                        $("#SR7603_part_no_to").append('<option value="' + oir_part_list[j][0] + '">' + oir_part_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_document_list.length; j++) {
                        $("#SR7603_document").append('<option value="' + oir_document_list[j][0] + '">' + oir_document_list[j][1] + '</option>');
                        $("#SR7603_document_to").append('<option value="' + oir_document_list[j][0] + '">' + oir_document_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_customer_list.length; j++) {
                        $("#SR7603_customer").append('<option value="' + oir_customer_list[j][0] + '">' + oir_customer_list[j][1] + '</option>');
                        $("#SR7603_customer_to").append('<option value="' + oir_customer_list[j][0] + '">' + oir_customer_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_customer_po_list.length; j++) {
                        $("#SR7603_customer_po").append('<option value="' + oir_customer_po_list[j][0] + '">' + oir_customer_po_list[j][1] + '</option>');
                        $("#SR7603_customer_po_to").append('<option value="' + oir_customer_po_list[j][0] + '">' + oir_customer_po_list[j][1] + '</option>');
                    }
                } else {
                    $("#SR7303_supplier").empty();
                    $("#SR7303_supplier_to").empty();
                    $("#SR7303_supplier").append('<option value="">Select Supplier</option>');
                    $("#SR7303_supplier_to").append('<option value="">Select Supplier</option>');
                    $("#SR7303_document").empty();
                    $("#SR7303_document_to").empty();
                    $("#SR7303_document").append('<option value="">Select Document</option>');
                    $("#SR7303_document_to").append('<option value="">Select Document</option>');
                    $("#SR7303_part_no").empty();
                    $("#SR7303_part_no_to").empty();
                    $("#SR7303_part_no").append('<option value="">Select Part No</option>');
                    $("#SR7303_part_no_to").append('<option value="">Select Part No</option>');
                    $("#SR7303_customer_po").empty();
                    $("#SR7303_customer_po_to").empty();
                    $("#SR7303_customer_po").append('<option value="">Select Cust. PO</option>');
                    $("#SR7303_customer_po_to").append('<option value="">Select Cust. PO</option>');
                    for (j = 0; j < oir_part_list.length; j++) {
                        $("#SR7303_part_no").append('<option value="' + oir_part_list[j][0] + '">' + oir_part_list[j][1] + '</option>');
                        $("#SR7303_part_no_to").append('<option value="' + oir_part_list[j][0] + '">' + oir_part_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_document_list.length; j++) {
                        $("#SR7303_document").append('<option value="' + oir_document_list[j][0] + '">' + oir_document_list[j][1] + '</option>');
                        $("#SR7303_document_to").append('<option value="' + oir_document_list[j][0] + '">' + oir_document_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_customer_list.length; j++) {
                        $("#SR7303_supplier").append('<option value="' + oir_customer_list[j][0] + '">' + oir_customer_list[j][1] + '</option>');
                        $("#SR7303_supplier_to").append('<option value="' + oir_customer_list[j][0] + '">' + oir_customer_list[j][1] + '</option>');
                    }
                    for (j = 0; j < oir_customer_po_list.length; j++) {
                        $("#SR7303_customer_po").append('<option value="' + oir_customer_po_list[j][0] + '">' + oir_customer_po_list[j][1] + '</option>');
                        $("#SR7303_customer_po_to").append('<option value="' + oir_customer_po_list[j][0] + '">' + oir_customer_po_list[j][1] + '</option>');
                    }
                }
            }
        }
    });
}

var sa_part_grp_list = [];
function get_part_group(date_from, date_to){
    if (!date_from){
        date_from = '0';
    }
  
    if (!date_to){
        date_to = '0';
    }
    $.ajax({
        method: "POST",
        url: '/reports/get_part_group/' + date_from + '/' + date_to + '/' + global_order_code + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            sa_part_grp_list = json;
            $("#lbSR7102PartGrp").empty();
            $("#lbSR7102ToPartGrp").empty();
            $("#lbSR7102PartGrp").append('<option value="">Select Part Grp.</option>');
            $("#lbSR7102ToPartGrp").append('<option value="">Select Part Grp.</option>');
            if (json.length > 0) {
                for (j = 0; j < json.length; j++) {
                    $("#lbSR7102PartGrp").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    $("#lbSR7102ToPartGrp").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

var uso_supplier_list = [];
var upo_supplier_list = [];
var mpds_supplier_list = [];
var grmr_supplier_list = [];
function get_supplier_list(ord_code, date_from='0', date_to='0'){
    if (!date_from){
        date_from = '0';
    }
  
    if (!date_to){
        date_to = '0';
    }
    if(global_order_code == 'SR8300' || global_order_code == 'SR8301') {
        data_type = 'document_date';
    } else if(global_order_code == 'SR8801') {
        data_type = 'SR8801';
    } else if(global_order_code == 'SR7403') {
        data_type = 'SR7403';
    } else {
        data_type = 'outstanding_po';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_supplier_list/' + date_from + '/' + date_to + '/' + data_type + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            var lbSupplier = '';
            switch (global_order_code){
                case 'SR7403':
                    if (json.length > 0) {
                        uso_supplier_list = json;
                        $("#lbSR7403Supplier").empty();
                        $("#lbSR7403ToSupplier").empty();
                        $("#lbSR7403Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR7403ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR7403Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR7403ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR8801':
                    if (json.length > 0) {
                        mpds_supplier_list = json;
                        $("#lbSR8801Supplier").empty();
                        $("#lbSR8801ToSupplier").empty();
                        $("#lbSR8801Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR8801ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR8801Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR8801ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR7202':
                    if (json.length > 0) {
                        upo_supplier_list = json;
                        $("#lbSR7202Supplier").empty();
                        $("#lbSR7202ToSupplier").empty();
                        $("#lbSR7202Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR7202ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR7202Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR7202ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR8300':
                    if (json.length > 0) {
                        grmr_supplier_list = json;
                        $("#lbSR8300Supplier").empty();
                        $("#lbSR8300ToSupplier").empty();
                        $("#lbSR8300Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR8300ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR8300Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR8300ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR8301':
                    if (json.length > 0) {
                        grmr_supplier_list = json;
                        $("#lbSR8301Supplier").empty();
                        $("#lbSR8301ToSupplier").empty();
                        $("#lbSR8301Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR8301ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR8301Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR8301ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR7203':
                    if (json.length > 0) {
                        upo_supplier_list = json;
                        $("#lbSR7203Supplier").empty();
                        $("#lbSR7203ToSupplier").empty();
                        $("#lbSR7203Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR7203ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR7203Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR7203ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR7204':
                    if (json.length > 0) {
                        upo_supplier_list = json;
                        $("#lbSR7204Supplier").empty();
                        $("#lbSR7204ToSupplier").empty();
                        $("#lbSR7204Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR7204ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR7204Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR7204ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
                case 'SR7205':
                    if (json.length > 0) {
                        upo_supplier_list = json;
                        $("#lbSR7205Supplier").empty();
                        $("#lbSR7205ToSupplier").empty();
                        $("#lbSR7205Supplier").append('<option value="">Select Supplier</option>');
                        $("#lbSR7205ToSupplier").append('<option value="">Select Supplier</option>');
                        for (j = 0; j < json.length; j++) {
                            $("#lbSR7205Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                            $("#lbSR7205ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        }
                    }
                    break;
            }
        }
    });
}

var uso_doc_list = [];
var uso_cust_po_list = [];
function get_oustanding_sales(date_from, date_to, doc_from, doc_to, cus_po_from, cus_po_to, data_type){
    if (!date_from){
      date_from = '0';
    }

    if (!date_to){
      date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_oustanding_sales/' + date_from + '/' + date_to + '/' + doc_from + '/' + doc_to + '/' + cus_po_from + '/' + cus_po_to + '/' + data_type + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            var lbTarget = '';
            var lbTarget_1 = '';
            var lbPlaceholder = '';
            switch (data_type){
                case 'document_no':
                    lbTarget = $("#txtDocNoFromSR7401");
                    lbTarget_1 = $("#txtDocNoToSR7401");
                    break;
                case 'customer_po':
                    lbTarget = $("#txtCustPONoFromSR7401");
                    lbTarget_1 = $("#txtCustPONoToSR7401");
                    break;
                case 'document_no_from':
                    lbTarget = $("#txtDocNoFromSR7401");
                    lbTarget.empty();
                    lbTarget.append('<option value="">Select Document No</option>');
                    break;
                case 'document_no_to':
                    lbTarget = $("#txtDocNoToSR7401");
                    lbTarget.empty();
                    lbTarget.append('<option value="">Select Document No</option>');
                    break;
                case 'customer_po_from':
                    lbTarget = $("#txtCustPONoFromSR7401");
                    lbTarget.empty();
                    lbTarget.append('<option value="">Select Cust. PO No</option>');
                    break;
                case 'customer_po_to':
                    lbTarget = $("#txtCustPONoToSR7401");
                    lbTarget.empty();
                    lbTarget.append('<option value="">Select Cust. PO No</option>');
                    break;
            }
            if (data_type == 'document_no') {
                if (json.length > 0) {
                    uso_doc_list = json;
                    lbTarget.empty();
                    lbTarget_1.empty();
                    lbTarget.append('<option value="">Select Document No</option>');
                    lbTarget_1.append('<option value="">Select Document No</option>');
                    for (j = 0; j < json.length; j++) {
                        lbTarget.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        lbTarget_1.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if (data_type == 'customer_po') {
                if (json.length > 0) {
                    uso_cust_po_list = json;
                    lbTarget.empty();
                    lbTarget_1.empty();
                    lbTarget.append('<option value="">Select Cust. PO No</option>');
                    lbTarget_1.append('<option value="">Select Cust. PO No</option>');
                    for (j = 0; j < json.length; j++) {
                        lbTarget.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        lbTarget_1.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else {
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        lbTarget.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
        }
    });
}

var msr_customer_list = [];
function get_sales_customer(year_month){
    $.ajax({
        method: "POST",
        url: '/reports/get_sales_info/' + year_month + '/customer/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            var lbCustomer = $("#txtSuppplierCodeSR7602");
            var toCustomer = $("#totxtSuppplierCodeSR7602");

            if (json.length > 0) {
                msr_customer_list = json;
                lbCustomer.empty();
                toCustomer.empty();
                lbCustomer.append('<option value="">Select Customer</option>');
                toCustomer.append('<option value="">Select Customer</option>');
                for (j = 0; j < json.length; j++) {
                    lbCustomer.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    toCustomer.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

var msr_part_grp_list = [];
function get_part_category(year_month){
    $.ajax({
        method: "POST",
        url: '/reports/get_sales_info/' + year_month + '/category/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            var lbCategory = $("#txtSuppplierCodeSR7601");
            var toCategory = $("#totxtSuppplierCodeSR7601");
            if (json.length > 0) {
                msr_part_grp_list = json;
                lbCategory.empty();
                toCategory.empty();
                lbCategory.append('<option value="">Select Part Grp</option>');
                toCategory.append('<option value="">Select Part Grp</option>');
                for (j = 0; j < json.length; j++) {
                    lbCategory.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    toCategory.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}
var sa_customer_list = [];
var sa_customer_po_list = [];
var sa_part_list = [];
function get_sales_analysis_data(date_from='0', date_to='0'){
    if(!date_from)date_from = '0';
    if(!date_to)date_to = '0';

    $.ajax({
        method: "POST",
        url: '/reports/get_sales_analysis_data/' + date_from + '/' + date_to + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            sa_customer_list = json.customer_list;
            sa_customer_po_list = json.customer_po_list;
            sa_part_list = json.part_list;
            $('#fromSACustomer').empty();
            $('#toSACustomer').empty();
            $('#fromSACustomer').append('<option value="">Select Customer</option>');
            $('#toSACustomer').append('<option value="">Select Customer</option>');
            for (j = 0; j < json.customer_list.length; j++) {
                $('#fromSACustomer').append('<option value="' + json.customer_list[j][0] + '">' + json.customer_list[j][1] + '</option>');
                $('#toSACustomer').append('<option value="' + json.customer_list[j][0] + '">' + json.customer_list[j][1] + '</option>');
            }
            $('#fromSAPartNo').empty();
            $('#toSAPartNo').empty();
            $('#fromSAPartNo').append('<option value="">Select Part No</option>');
            $('#toSAPartNo').append('<option value="">Select Part No</option>');
            for (j = 0; j < json.part_list.length; j++) {
                $('#fromSAPartNo').append('<option value="' + json.part_list[j][0] + '">' + json.part_list[j][1] + '</option>');
                $('#toSAPartNo').append('<option value="' + json.part_list[j][0] + '">' + json.part_list[j][1] + '</option>');
            }
            $('#fromSACustomerPo').empty();
            $('#toSACustomerPo').empty();
            $('#fromSACustomerPo').append('<option value="">Select Cust. PO</option>');
            $('#toSACustomerPo').append('<option value="">Select Cust. PO</option>');
            for (j = 0; j < json.customer_po_list.length; j++) {
                $('#fromSACustomerPo').append('<option value="' + json.customer_po_list[j] + '">' + json.customer_po_list[j] + '</option>');
                $('#toSACustomerPo').append('<option value="' + json.customer_po_list[j] + '">' + json.customer_po_list[j] + '</option>');
            }
        }
    });
}

var uso_customer_list = [];
var grmr_customer_list = [];
function get_customer_list(date_from='0', date_to='0', data_type){
    if (!date_from){
        date_from = '0';
    }

    if (!date_to){
        date_to = '0';
    }
    $.ajax({
        method: "POST",
        url: '/reports/get_customer_list/' + date_from + '/' + date_to + '/' + data_type + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            var lbCustomer;
            if(global_order_code == 'SR8400') {
                if (json.length > 0) {
                    grmr_customer_list = json;
                    $("#lbSR8400Customer").empty();
                    $("#lbSR8400ToCustomer").empty();
                    $("#lbSR8400Customer").append('<option value="">Select Customer</option>');
                    $("#lbSR8400ToCustomer").append('<option value="">Select Customer</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR8400Customer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR8400ToCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SR7403') {
                if (json.length > 0) {
                    uso_customer_list = json;
                    $("#lbSR7403Customer").empty();
                    $("#lbSR7403ToCustomer").empty();
                    $("#lbSR7403Customer").append('<option value="">Select Customer</option>');
                    $("#lbSR7403ToCustomer").append('<option value="">Select Customer</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7403Customer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7403ToCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SR7404') {
                if (json.length > 0) {
                    uso_customer_list = json;
                    $("#lbSR7404Customer").empty();
                    $("#lbSR7404ToCustomer").empty();
                    $("#lbSR7404Customer").append('<option value="">Select Customer</option>');
                    $("#lbSR7404ToCustomer").append('<option value="">Select Customer</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7404Customer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7404ToCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else {
                if (json.length > 0) {
                    uso_customer_list = json;
                    $("#lbSR7402Customer").empty();
                    $("#lbSR7402ToCustomer").empty();
                    $("#lbSR7402Customer").append('<option value="">Select Customer</option>');
                    $("#lbSR7402ToCustomer").append('<option value="">Select Customer</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7402Customer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7402ToCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
        }
    });
}

var gr_category_list = [];
var gr_customer_po_list = [];
var gr_part_list = [];
function get_part_no(date_from, date_to){
    if (!date_from){
      date_from = '0';
    }

    if (!date_to){
      date_to = '0';
    }

    if (global_order_code == 'SR7502') {
        $.ajax({
            method: "POST",
            url: '/reports/get_gr_data/' + date_from + '/' + date_to + '/part_no/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            responseTime: 200,
            success: function (json) {
                let lbPartNo = $("#txtPartNoSR7503");
                let lbPartNoTo = $("#txtPartNoToSR7503");
                if (json.length > 0) {
                    gr_part_list = json;
                    lbPartNo.empty();
                    lbPartNoTo.empty();
                    lbPartNo.append('<option value="">Select Part No</option>')
                    lbPartNoTo.append('<option value="">Select Part No</option>')
                    for (j = 0; j < json.length; j++) {
                        lbPartNo.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>')
                        lbPartNoTo.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>')
                    }
                }
            }
        });
    } else if (global_order_code == 'SR7503') {
        $.ajax({
            method: "POST",
            url: '/reports/get_gr_data/' + date_from + '/' + date_to + '/SR7503/',
            dataType: 'JSON',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            responseTime: 200,
            success: function (json) {
                gr_part_list = json.part_list;
                gr_category_list = json.cat_list;
                gr_customer_po_list = json.customer_po_list;
                $('#txtPartGrpSR7503').empty();
                $('#txtPartGrpToSR7503').empty();
                $('#txtPartGrpSR7503').append('<option value="">Select Category</option>');
                $('#txtPartGrpToSR7503').append('<option value="">Select Category</option>');
                for (j = 0; j < json.cat_list.length; j++) {
                    $('#txtPartGrpSR7503').append('<option value="' + json.cat_list[j][0] + '">' + json.cat_list[j][1] + '</option>');
                    $('#txtPartGrpToSR7503').append('<option value="' + json.cat_list[j][0] + '">' + json.cat_list[j][1] + '</option>');
                }
                $('#txtPartNoSR7503').empty();
                $('#txtPartNoToSR7503').empty();
                $('#txtPartNoSR7503').append('<option value="">Select Part No</option>');
                $('#txtPartNoToSR7503').append('<option value="">Select Part No</option>');
                for (j = 0; j < json.part_list.length; j++) {
                    $('#txtPartNoSR7503').append('<option value="' + json.part_list[j][0] + '">' + json.part_list[j][1] + '</option>');
                    $('#txtPartNoToSR7503').append('<option value="' + json.part_list[j][0] + '">' + json.part_list[j][1] + '</option>');
                }
                $('#txtCustPONoFromSR7503').empty();
                $('#txtCustPONoToSR7503').empty();
                $('#txtCustPONoFromSR7503').append('<option value="">Select Cust. PO</option>');
                $('#txtCustPONoToSR7503').append('<option value="">Select Cust. PO</option>');
                for (j = 0; j < json.customer_po_list.length; j++) {
                    $('#txtCustPONoFromSR7503').append('<option value="' + json.customer_po_list[j] + '">' + json.customer_po_list[j] + '</option>');
                    $('#txtCustPONoToSR7503').append('<option value="' + json.customer_po_list[j] + '">' + json.customer_po_list[j] + '</option>');
                }
            }
        });
    }
}

var upo_part_list = [];
function get_po_part_no(ord_code, date_from='0', date_to='0'){
    if (!date_from){
        date_from = '0';
    }
  
    if (!date_to){
        date_to = '0';
    }
    $.ajax({
        method: "POST",
        url: '/reports/get_po_data/' + date_from + '/' + date_to + '/part_no/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if(ord_code == 'SR7205') {
                if (json.length > 0) {
                    upo_part_list = json;
                    $("#lbSR7205PartNo").empty();
                    $("#lbSR7205ToPartNo").empty();
                    $('#lbSR7205PartNo').append('<option value="">Select Part No</option>');
                    $('#lbSR7205ToPartNo').append('<option value="">Select Part No</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7205PartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7205ToPartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else {
                if (json.length > 0) {
                    upo_part_list = json;
                    $("#lbSR7204PartNo").empty();
                    $("#lbSR7204ToPartNo").empty();
                    $('#lbSR7204PartNo').append('<option value="">Select Part No</option>');
                    $('#lbSR7204ToPartNo').append('<option value="">Select Part No</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7204PartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7204ToPartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
            
        }
    });
}


function get_alter_address() {
    $.ajax({
        method: "POST",
        url: '/reports/get_delivery_addr/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if (json.length > 0) {
                $("#po_alternate_address").empty();
                $("#do_alternate_address").empty();
                $("#po_alternate_address").append('<option value="">Select Alternate</option>');
                $("#do_alternate_address").append('<option value="">Select Alternate</option>');
                for (j = 0; j < json.length; j++) {
                    $("#po_alternate_address").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    $("#do_alternate_address").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

function get_po_data(date_from, date_to){
    if (!date_from){
        date_from = '0';
    }

    if (!date_to){
        date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_po_data/' + date_from + '/' + date_to + '/po/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            let fromPONo = $("#fromPONo");
            let toPONo = $("#toPONo");
            // $("#fromPONo").empty();
            // $("#toPONo").empty();
            if (json.length > 0) {
                // $("#fromPONo").append('<option value="0">Select P/O</option>');
                // $("#toPONo").append('<option value="0">Select P/O</option>');
                for (j = 0; j < json.length; j++) {
                    fromPONo.append('<option value="' + json[j].id + '">' + json[j].doc_num + '</option>');
                    toPONo.append('<option value="' + json[j].id + '">' + json[j].doc_num + '</option>');
                }
            }
        }
    });
}

var uso_part_list = [];
var uso_part_group_list = [];
function get_so_part_no(date_from='0', date_to='0'){
    if (!date_from){
        date_from = '0';
    }

    if (!date_to){
        date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_so_data/' + date_from + '/' + date_to + '/part_no/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            uso_part_list = json.part_list;
            uso_part_group_list = json.grp_list;
            $("#lbSR7404PartNo").empty();
            $("#lbSR7404ToPartNo").empty();
            $("#lbSR7404PartGrp").empty();
            $("#lbSR7404ToPartGrp").empty();
            $("#lbSR7404PartNo").append('<option value="">Select Part No</option>');
            $("#lbSR7404ToPartNo").append('<option value="">Select Part No</option>');
            $("#lbSR7404PartGrp").append('<option value="">Select Part Grp</option>');
            $("#lbSR7404ToPartGrp").append('<option value="">Select Part Grp</option>');
            for (j = 0; j < uso_part_list.length; j++) {
                $("#lbSR7404PartNo").append('<option value="' + uso_part_list[j][0] + '">' + uso_part_list[j][1] + '</option>');
                $("#lbSR7404ToPartNo").append('<option value="' + uso_part_list[j][0] + '">' + uso_part_list[j][1] + '</option>');
            }
            for (j = 0; j < uso_part_group_list.length; j++) {
                $("#lbSR7404PartGrp").append('<option value="' + uso_part_group_list[j][0] + '">' + uso_part_group_list[j][1] + '</option>');
                $("#lbSR7404ToPartGrp").append('<option value="' + uso_part_group_list[j][0] + '">' + uso_part_group_list[j][1] + '</option>');
            }
        }
    });
}

// $('#date_fromSR8500').bind('keydown', function (event) {
//     if (event.which == 13) {
//         let date_from = $('#date_fromSR8500');
//         let valid_date = moment(date_from.val(), "DD-MM-YYYY", true).isValid();
//         if(!valid_date) {
//             setTimeout(() => {
//                 $('#date_fromSR8500').datepicker('setDate', '');
//             }, 100);
//         }
//     }
// });

// $('#date_toSR8500').bind('keydown', function (event) {
//     if (event.which == 13) {
//         let date_from = $('#date_toSR8500');
//         let valid_date = moment(date_from.val(), "DD-MM-YYYY", true).isValid();
//         if(!valid_date) {
//             setTimeout(() => {
//                 $('#date_toSR8500').datepicker('setDate', '');
//             }, 100);
//         }
//     }
// });

$("#sr8500Location").on('change', function(e){
    var date_from = $('#date_fromSR8500');
    var date_to = $('#date_toSR8500');
    adjust_date(date_from, date_to);
    let location_id = $("#sr8500Location").val();
    get_location_part_no(location_id);
});


function get_inv_location() {
    $.ajax({
        method: "POST",
        url: '/reports/get_inv_location/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            let location_data = json;
            if (location_data.length > 0) {
                for (j = 0; j < location_data.length; j++) {
                    $("#sr8500Location").append('<option value="' + location_data[j].id + '">' + location_data[j].code + '</option>')
                }
            }

        }
    });
}

var usb_part_list = [];
function get_location_part_no(location_id=0){
    $.ajax({
        method: "POST",
        url: '/reports/get_SR8500_data/' + location_id,
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            usb_part_list = json;
            if (json.length > 0) {
                $("#sr8500PartNo").empty();
                $("#sr8500ToPartNo").empty();
                $("#sr8500PartNo").append('<option value="">Select Part No</option>');
                $("#sr8500ToPartNo").append('<option value="">Select Part No</option>');
                for (j = 0; j < json.length; j++) {
                    $("#sr8500PartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    $("#sr8500ToPartNo").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

var gr_supplier_list = [];
function get_gr_supplier(date_from, date_to){
    if (!date_from){
      date_from = '0';
    }

    if (!date_to){
      date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_gr_data/' + date_from + '/' + date_to + '/supplier/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            gr_supplier_list = json;
            var lbSupplierNo = $("#txtSuppplierNoSR7504");
            var lbToSupplierNo = $("#txtToSuppplierNoSR7504");
            lbSupplierNo.empty();
            lbToSupplierNo.empty();
            lbSupplierNo.append('<option value="">Select Supplier</option>');
            lbToSupplierNo.append('<option value="">Select Supplier</option>');
            if (json.length > 0) {
                for (j = 0; j < json.length; j++) {
                    lbSupplierNo.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    lbToSupplierNo.append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

var mpr_supplier_list = [];
var mpr_doc_list = [];
var mpr_po_list = [];
var mpr_part_list = [];
function get_monthly_purchase(ord_code, year_month, parameter_id, data_type){
    $.ajax({
        method: "POST",
        url: '/reports/get_monthly_purchase/' + year_month + '/' + parameter_id + '/' + data_type +'/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            mpr_doc_list = json.doc_list;
            mpr_supplier_list = json.supplier_list;
            mpr_po_list = json.cus_po_list;
            mpr_part_list = json.part_list;

            var lbTarget = '';
            var lbTarget1 = '';
            lbTarget = $("#txtDocumentNoSR7300");
            lbTarget1 = $("#txtDocumentNoSR7300_to");
            lbTarget.empty();
            lbTarget1.empty();
            lbTarget.append('<option value="">Select Document</option>');
            lbTarget1.append('<option value="">Select Document</option>');
            for (j = 0; j < mpr_doc_list.length; j++) {
                lbTarget.append('<option value="' + mpr_doc_list[j][0] + '">' + mpr_doc_list[j][1] + '</option>');
                lbTarget1.append('<option value="' + mpr_doc_list[j][0] + '">' + mpr_doc_list[j][1] + '</option>');
            }
            
            lbTarget = $("#txt7300SuppplierNo");
            lbTarget1 = $("#txt7300ToSuppplierNo");
            lbTarget.empty();
            lbTarget1.empty();
            lbTarget.append('<option value="">Select Supplier</option>');
            lbTarget1.append('<option value="">Select Supplier</option>');
            for (j = 0; j < mpr_supplier_list.length; j++) {
                lbTarget.append('<option value="' + mpr_supplier_list[j][0] + '">' + mpr_supplier_list[j][1] + '</option>');
                lbTarget1.append('<option value="' + mpr_supplier_list[j][0] + '">' + mpr_supplier_list[j][1] + '</option>');
            }

            switch (ord_code){
                case 'SR7301':
                    lbTarget = $("#txtCustomerPoSR7301");
                    lbTarget1 = $("#txtCustomerPoToSR7301");
                    lbTarget.empty();
                    lbTarget1.empty();
                    lbTarget.append('<option value="">Select Customer PO</option>');
                    lbTarget1.append('<option value="">Select Customer PO</option>');
                    for (j = 0; j < mpr_po_list.length; j++) {
                        lbTarget.append('<option value="' + mpr_po_list[j][0] + '">' + mpr_po_list[j][1] + '</option>');
                        lbTarget1.append('<option value="' + mpr_po_list[j][0] + '">' + mpr_po_list[j][1] + '</option>');
                    }
                    break;
                case 'SR7302':
                    lbTarget = $("#txtPartNoSR7302");
                    lbTarget1 = $("#txtPartNoToSR7302");
                    lbTarget.empty();
                    lbTarget1.empty();
                    lbTarget.append('<option value="">Select Part</option>');
                    lbTarget1.append('<option value="">Select Part</option>');
                    for (j = 0; j < mpr_part_list.length; j++) {
                        lbTarget.append('<option value="' + mpr_part_list[j][0] + '">' + mpr_part_list[j][1] + '</option>');
                        lbTarget1.append('<option value="' + mpr_part_list[j][0] + '">' + mpr_part_list[j][1] + '</option>');
                    }
                    break;
            }
        }
    });
}

var upo_doc_list = [];
var oel_doc_list = [];
function get_document_no(date_from='0', date_to='0'){
    if (!date_from){
        date_from = '0';
    }

    if (!date_to){
        date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_document_no/' + date_from + '/' + date_to + '/' + global_order_code + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if (global_order_code == 'SR7201') {
                if (json.length > 0) {
                    upo_doc_list = json;
                    $("#lbSR7201Document").empty();
                    $("#lbSR7201ToDocument").empty();
                    $("#lbSR7201Document").append('<option value="">Select Document No</option>');
                    $("#lbSR7201ToDocument").append('<option value="">Select Document No</option>');
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7201Document").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7201ToDocument").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SL3A00' || global_order_code == 'SL3A01') {
                oel_doc_list = json;
                $("#lbSL3A0Document").empty();
                $("#lbSL3A0ToDocument").empty();
                $("#lbSL3A0Document").append('<option value="">Select Document No</option>');
                $("#lbSL3A0ToDocument").append('<option value="">Select Document No</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL3A0Document").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL3A0ToDocument").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SL3300' || global_order_code == 'SL3301') {
                oel_doc_list = json;
                $("#lbSL330Document").empty();
                $("#lbSL330ToDocument").empty();
                $("#lbSL330Document").append('<option value="">Select Document No</option>');
                $("#lbSL330ToDocument").append('<option value="">Select Document No</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL330Document").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL330ToDocument").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
        }
    });
}


var oel_cust_list = [];
function get_SL3_data(date_from='0', date_to='0'){
    if (!date_from){
        date_from = '0';
    }

    if (!date_to){
        date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_SL3_data/' + date_from + '/' + date_to + '/' + global_order_code + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if(global_order_code == 'SL3A00' || global_order_code == 'SL3A01') {
                oel_cust_list = json;
                $("#lbSL3A0Supplier").empty();
                $("#lbSL3A0ToSupplier").empty();
                $("#lbSL3A0Supplier").append('<option value="">Select Supplier</option>');
                $("#lbSL3A0ToSupplier").append('<option value="">Select Supplier</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL3A0Supplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL3A0ToSupplier").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SL3300' || global_order_code == 'SL3301') {
                oel_cust_list = json;
                $("#lbSL330CCustomer").empty();
                $("#lbSL330ToCCustomer").empty();
                $("#lbSL330CCustomer").append('<option value="">Select Customer</option>');
                $("#lbSL330ToCCustomer").append('<option value="">Select Customer</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL330CCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL330ToCCustomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
        }
    });
}

var grmr_doc_list = [];
function get_document_numbers(date_from, date_to, customer_id){
    if (!date_from){
      date_from = '0';
    }

    if (!date_to){
      date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_document_numbers/' + date_from + '/' + date_to + '/' + global_order_code + '/' + customer_id + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if (json.length > 0) {
                grmr_doc_list = json;
                $("#lbSR834Document").empty();
                $("#lbSR834ToDocument").empty();
                $("#lbSR834Document").append('<option value="">Select Document No</option>');
                $("#lbSR834ToDocument").append('<option value="">Select Document No</option>');
                for (j = 0; j < json.length; j++) {
                    $("#lbSR834Document").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    $("#lbSR834ToDocument").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                }
            }
        }
    });
}

var upo_cust_po_list = [];
var grmr_cust_po_list = [];
var oel_cust_po_list = [];
function get_customer_po(date_from, date_to, supplier_id='0'){
    if (!date_from){
      date_from = '0';
    }

    if (!date_to){
      date_to = '0';
    }

    $.ajax({
        method: "POST",
        url: '/reports/get_customer_po/' + date_from + '/' + date_to + '/' + supplier_id + '/' + global_order_code + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if(global_order_code == 'SR7203') {
                upo_cust_po_list = json;
                $("#lbSR7203Cutomer").empty();
                $("#lbSR7203ToCutomer").empty();
                $("#lbSR7203Cutomer").append('<option value="">Select Customer PO</option>');
                $("#lbSR7203ToCutomer").append('<option value="">Select Customer PO</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR7203Cutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR7203ToCutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SR8301') {
                grmr_cust_po_list = json;
                $("#lbSR8301Cutomer").empty();
                $("#lbSR8301ToCutomer").empty();
                $("#lbSR8301Cutomer").append('<option value="">Select Customer PO</option>');
                $("#lbSR8301ToCutomer").append('<option value="">Select Customer PO</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSR8301Cutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSR8301ToCutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SL3A01') {
                oel_cust_po_list = json;
                $("#lbSL3A0Cutomer").empty();
                $("#lbSL3A0ToCutomer").empty();
                $("#lbSL3A0Cutomer").append('<option value="">Select Customer PO</option>');
                $("#lbSL3A0ToCutomer").append('<option value="">Select Customer PO</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL3A0Cutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL3A0ToCutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            } else if(global_order_code == 'SL3301') {
                oel_cust_po_list = json;
                $("#lbSL330Cutomer").empty();
                $("#lbSL330ToCutomer").empty();
                $("#lbSL330Cutomer").append('<option value="">Select Customer PO</option>');
                $("#lbSL330ToCutomer").append('<option value="">Select Customer PO</option>');
                if (json.length > 0) {
                    for (j = 0; j < json.length; j++) {
                        $("#lbSL330Cutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                        $("#lbSL330ToCutomer").append('<option value="' + json[j][0] + '">' + json[j][1] + '</option>');
                    }
                }
            }
            
        }
    });
}

function adjust_date(date_from, date_to){
    var date_from_valid = moment(date_from.val(), "DD-MM-YYYY", true).isValid();
    var date_to_valid = moment(date_to.val(), "DD-MM-YYYY", true).isValid();

    if (date_from.val() != '' && !date_from_valid){
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();

        if(dd<10) {
            dd = '0'+dd
        }

        if(mm<10) {
            mm = '0'+mm
        }

        today = dd + '-' + mm + '-' + yyyy;

        date_from.val(today);
    }

    if (date_to.val() != '' && !date_to_valid){
        date_to.val(date_from.val());
    }

    if(Date.parse(date_to.val()) < Date.parse(date_from.val())){
        date_to.val(date_from.val());
    }

}

function param_list_string(select1, select2, data_list){
    var array_list = [];
    if (select1 != '0' && select2 != '0') {
        insert = false;
        $.each(data_list, function(i, v){
            if (select1 == v[0]) { insert = true; }
            if(insert) { array_list.push(v[0]); }
            if (select2 == v[0]) { insert = false; }
        });
    } else if (select1 != '0') {
        insert = false;
        $.each(data_list, function(i, v){
            if (select1 == v[0]) { insert = true; }
            if(insert) { array_list.push(v[0]); }
        });
    } else if (select2 != '0') {
        insert = true;
        $.each(data_list, function(i, v){
            if(insert) { array_list.push(v[0]); }
            if (select2 == v[0]) { insert = false; }
        });
    }

    return array_list;
}

$('#btnReview').on('keydown', function (e) {
    if (e.which == 13) {
        $(this).click();
    }
});

$('#btnReview').on('click', function () {
    var frViewPDF = $('#frViewPDF')[0];
    var divViewPDF = $('#divViewPDF')[0];
    var hdReportId = $('#hdReportId').val();
    var divFilter = $('.div' + hdReportId)[0];
    var url = "";

    $("#loadpage").show();
    if (hdReportId == '0') {
        frViewPDF.setAttribute("src", "");
        divViewPDF.innerHTML = frViewPDF.outerHTML;
    }
    // =====================Print Order : get order_type and order_id=======================
    var hd_order_type = $('#hdOrderType').val();
    var hd_order_id = $('#hdOrderID').val();
    var hd_print_type = $('#hdPrintType').val();
    var po_print_header = $('input[name=po-group-print-header]:checked').val();
    var do_print_header = $('input[name=do-group-print-header]:checked').val();
    if (hd_order_type != 0 && hd_order_id != 0) {
        if (hd_order_type == 2) {//Print Purchase Order
            let fromOrder = $('#fromPONo').val();
            let toOrder = $('#toPONo').val();
            let address = $('#po_alternate_address').val();
            if (address == '' || address === undefined) {
                address = 0;
            }
            let signature = 1;
            if($('#id_exclude_signature').is(':checked')) {
                signature = 0;
            }
            let part_group = 0;
            if($('#id_po_part_group').is(':checked')){
                part_group = 1;
            }

            if((fromOrder == '' || fromOrder == '0' || fromOrder == undefined) && (toOrder == '' || toOrder == '0' || toOrder == undefined)) {
                url = '/reports/print_po_order/' + hd_order_id + '/' + po_print_header + '/' + remove_address + '/' + address + '/' + signature + '/' + part_group;
            } else {
                url = '/reports/print_po_orders/' + fromOrder + '/' + toOrder + '/' + po_print_header + '/' + remove_address + '/' + address + '/' + signature + '/' + part_group;
            }

            frViewPDF.setAttribute("src", url);
            divViewPDF.innerHTML = frViewPDF.outerHTML;

            $('#secReportList').css("display", "none");
            $('.filter').css("display", "none");
            $('#divPO').removeAttr("style");
        }
        else if (hd_order_type == 6) {
            let part_group = 0;
            if($('#id_part_group').is(':checked')){
                part_group = 1;
            }
            if (hd_print_type == 2) {//Print Tax Invoice
                url = '/reports/print_tax_invoice/' + hd_order_id + '/' + do_print_header + '/' + part_group;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 1) {//Print Delivery Order
                url = '/reports/print_do/' + hd_order_id + '/' + do_print_header + '/' + part_group;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 3) {//Print Paking List
                url = '/reports/print_packing_list/' + hd_order_id + '/' + do_print_header + '/' + part_group;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 4) {//Print Invoice
                url = '/reports/print_invoice/' + hd_order_id + '/' + do_print_header + '/' + part_group;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 5) {//Print Shipping Invoice ver 1
                let address = $('#do_alternate_address').val();
                if (address == '' || address === undefined) {
                    address = 0;
                }
                // let pay_mode = 0;
                // if($('#id_pay_mode').is(':checked')){
                //     pay_mode = 1;
                // }
                url = '/reports/print_shipping_invoice/' + hd_order_id + '/' + do_print_header + '/' + part_group + '/' + address;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 6) {//Print Shipping Invoice ver 2
                let address = $('#do_alternate_address').val();
                if (address == '' || address === undefined) {
                    address = 0;
                }
                url = '/reports/print_shipping_invoice_2/' + hd_order_id + '/' + do_print_header + '/' + part_group + '/' + address;
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
        }
    }// ====================================End print order==================================
    else {
        //Print SR.... reports
        switch (hdReportId) {
            case 'SR8300':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                doc_list = param_list_string(data4, data5, grmr_doc_list);
                p_list = param_list_string(data2, data3, grmr_supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#param3').val(JSON.stringify(doc_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR8400':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                doc_list = param_list_string(data4, data5, grmr_doc_list);
                p_list = param_list_string(data2, data3, grmr_customer_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#param3').val(JSON.stringify(doc_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR8301':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                cp_list = param_list_string(data4, data5, grmr_cust_po_list);
                p_list = param_list_string(data2, data3, grmr_supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#param3').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7203':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                cp_list = param_list_string(data4, data5, upo_cust_po_list);
                p_list = param_list_string(data2, data3, upo_supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#param3').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7204':
            case 'SR7205':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                
                p_list = param_list_string(data4, data5, upo_part_list);
                sp_list = param_list_string(data2, data3, upo_supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(sp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7404':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                    data6 = selectData[4].value ? selectData[4].value : '0';
                    data7 = selectData[5].value ? selectData[5].value : '0';
                }
                grp_list = param_list_string(data6, data7, uso_part_group_list);
                p_list = param_list_string(data4, data5, uso_part_list);
                cs_list = param_list_string(data2, data3, uso_customer_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(JSON.stringify(grp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7300':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    if(data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                            data3 = selectData[2].value ? selectData[2].value : '0';
                            data4 = selectData[3].value ? selectData[3].value : '0';
                        }
                        a_list = [];
                        b_list = [];
                        
                        a_list = param_list_string(data1, data2, mpr_supplier_list);
                        b_list = param_list_string(data3, data4, mpr_doc_list);

                        url = '/reports/print_' + hdReportId + '/';
                        global_url = url;
                        $('#param0').val(data0);
                        $('#param1').val(JSON.stringify(a_list));
                        $('#param2').val(JSON.stringify(b_list));
                        $('#reportForm').attr('action', url);
                        $('#reportForm').submit();
                        // frViewPDF.setAttribute("src", url);
                        // divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7301':
            case 'SR7302':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    if(data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                            data3 = selectData[2].value ? selectData[2].value : '0';
                            data4 = selectData[3].value ? selectData[3].value : '0';
                            data5 = selectData[4].value ? selectData[4].value : '0';
                            data6 = selectData[5].value ? selectData[5].value : '0';
                            data7 = selectData[6].value ? selectData[6].value : '0';
                            data8 = selectData[7].value ? selectData[7].value : '0';
                        }
                        a_list = [];
                        b_list = [];
                        c_list = [];
                            a_list = param_list_string(data1, data2, mpr_supplier_list);
                            b_list = param_list_string(data3, data4, mpr_doc_list);
                        if (hdReportId == 'SR7301') {
                            c_list = param_list_string(data5, data6, mpr_po_list);
                        } else if (hdReportId == 'SR7302') {
                            c_list = param_list_string(data7, data8, mpr_part_list);
                        }

                        url = '/reports/print_' + hdReportId + '/';
                        global_url = url;
                        $('#param0').val(data0);
                        $('#param1').val(JSON.stringify(a_list));
                        $('#param2').val(JSON.stringify(b_list));
                        $('#param3').val(JSON.stringify(c_list));
                        $('#reportForm').attr('action', url);
                        $('#reportForm').submit();
                        // frViewPDF.setAttribute("src", url);
                        // divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7101':
                var sa_confirm = 'Y';
                // sa_confirm = $("input[name='sa_print_selection']:checked").val();
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data2 != '0' && data3 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                } else if (data2 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data3 != '0') {
                    insert = true;
                    $.each(sa_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, sa_part_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(sa_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7103':
                var sa_confirm = 'Y';
                // sa_confirm = $("input[name='sa_print_selection']:checked").val();
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data6 = selectData[0].value ? selectData[0].value : '0';
                    data7 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data2 != '0' && data3 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                } else if (data2 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data3 != '0') {
                    insert = true;
                    $.each(sa_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, sa_part_list);
                cu_list = param_list_string(data6, data7, sa_customer_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(JSON.stringify(cu_list));
                $('#param5').val(sa_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7102':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                if(data0.length > 1) {
                    selectData = divFilter.getElementsByTagName("select");
                    if (selectData.length > 0) {
                        data2 = selectData[0].value ? selectData[0].value : '0';
                        data3 = selectData[1].value ? selectData[1].value : '0';
                    }
                    pg_list = param_list_string(data2, data3, sa_part_grp_list);

                    url = '/reports/print_' + hdReportId + '/';
                    global_url = url;
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(pg_list));
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR8800':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                if(data0.length > 1) {
                    selectData = divFilter.getElementsByTagName("select");
                    if (selectData.length > 0) {
                        data2 = selectData[0].value ? selectData[0].value : '0';
                        data3 = selectData[1].value ? selectData[1].value : '0';
                    }
                    cs_list = param_list_string(data2, data3, uso_customer_list);
                    
                    url = '/reports/print_' + hdReportId + '/';
                    global_url = url;
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(cs_list));
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SL3A00':
            case 'SL3300':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                var doc_list = param_list_string(data2, data3, oel_doc_list);
                var cs_list = param_list_string(data4, data5, oel_cust_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(doc_list));
                $('#param3').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL3A01':
            case 'SL3301':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                    data6 = selectData[4].value ? selectData[4].value : '0';
                    data7 = selectData[5].value ? selectData[5].value : '0';
                }
                var doc_list = param_list_string(data2, data3, oel_doc_list);
                var cs_list = param_list_string(data4, data5, oel_cust_list);
                var cp_list = param_list_string(data6, data7, oel_cust_po_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(doc_list));
                $('#param3').val(JSON.stringify(cs_list));
                $('#param4').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7201':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                p_list = param_list_string(data2, data3, upo_doc_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7202':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                p_list = param_list_string(data2, data3, upo_supplier_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7206':
            case 'SR7405':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                }
                url = '/reports/print_' + hdReportId + '/' + data0 + '/' + data1 + '/' + data2 + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7402':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                cs_list = param_list_string(data2, data3, uso_customer_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7403':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                cs_list = param_list_string(data2, data3, uso_customer_list);
                sp_list = param_list_string(data4, data5, uso_supplier_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR8801':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                p_list = param_list_string(data2, data3, mpds_supplier_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7501':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                var sp_list = param_list_string(data2, data3, gr_supplier_list);
                
                if (data0.length > 1) {
                    url = '/reports/print_' + hdReportId + '/';
                    global_url = url;
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(sp_list));
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR7502':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[4].value ? selectData[4].value : '0';
                    data3 = selectData[5].value ? selectData[5].value : '0';
                }
                p_list = param_list_string(data2, data3, gr_part_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7503':
                var is_confirm = '';
                if (hdReportId == 'SR7503'){
                    is_confirm = $('#is_confirm').val();
                }
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data6 = selectData[0].value ? selectData[0].value : '0';
                    data7 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data6 != '0' && data7 != '0') {
                    insert = false;
                    $.each(gr_customer_po_list, function(i, v){
                        if (data6 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data7 == v) { insert = false; }
                    })
                } else if (data6 != '0') {
                    insert = false;
                    $.each(gr_customer_po_list, function(i, v){
                        if (data6 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data7 != '0') {
                    insert = true;
                    $.each(gr_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data7 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, gr_part_list);
                cu_list = param_list_string(data2, data3, gr_category_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(cu_list));
                $('#param4').val(JSON.stringify(p_list));
                $('#param5').val(is_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7504':
                var is_confirm = '';
                if (hdReportId == 'SR7504'){
                    is_confirm = $('#is_confirm_2').val();
                }
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                var sp_list = param_list_string(data2, data3, gr_supplier_list);
                
                if (data0.length > 1) {
                    url = '/reports/print_' + hdReportId + '/';
                    global_url = url;
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(sp_list));
                    $('#param3').val(is_confirm);
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR7401':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                doc_list = param_list_string(data2, data3, uso_doc_list);
                cp_list = param_list_string(data4, data5, uso_cust_po_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(doc_list));
                $('#param3').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7601':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    if(data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                        }
                        var pg_list = param_list_string(data1, data2, msr_part_grp_list);
                        data3 = document.querySelector('input[name="print_selection_SR7601"]:checked').value;

                        url = '/reports/print_' + hdReportId + '/';
                        global_url = url;
                        $('#param0').val(data0);
                        $('#param1').val(JSON.stringify(pg_list));
                        $('#param2').val(data3);
                        $('#reportForm').attr('action', url);
                        $('#reportForm').submit();
                        // frViewPDF.setAttribute("src", url);
                        // divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7602':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    if (data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                        }
                        var cs_list = param_list_string(data1, data2, msr_customer_list);
                        data3 = document.querySelector('input[name="print_selection"]:checked').value;

                        url = '/reports/print_' + hdReportId + '/';
                        global_url = url;
                        $('#param0').val(data0);
                        $('#param1').val(JSON.stringify(cs_list));
                        $('#param2').val(data3);
                        $('#reportForm').attr('action', url);
                        $('#reportForm').submit();
                        // frViewPDF.setAttribute("src", url);
                        // divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7303':
            case 'SR7603':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    data1 = inputData[1].value.split("-").reverse().join("-");
                    data2 = inputData[2].value.split("-").reverse().join("-");
                    data3 = inputData[3].value.split("-").reverse().join("-");
                }
                if (data0.length == 0)
                    data0 = '0';
                if (data1.length == 0)
                    data1 = '0';
                if (data2.length == 0)
                    data2 = '0';
                if (data3.length == 0)
                    data3 = '0';
                
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data4 = selectData[0].value ? selectData[0].value : '0';
                    data5 = selectData[1].value ? selectData[1].value : '0';
                    data6 = selectData[2].value ? selectData[2].value : '0';
                    data7 = selectData[3].value ? selectData[3].value : '0';
                    data8 = selectData[4].value ? selectData[4].value : '0';
                    data9 = selectData[5].value ? selectData[5].value : '0';
                    data10 = selectData[6].value ? selectData[6].value : '0';
                    data11 = selectData[7].value ? selectData[7].value : '0';
                    data12 = selectData[8].value ? selectData[8].value : '0';
                }

                var cs_list = param_list_string(data4, data5, oir_customer_list);
                var doc_list = param_list_string(data6, data7, oir_document_list);
                var po_list = param_list_string(data8, data9, oir_customer_po_list);
                var pt_list = param_list_string(data10, data11, oir_part_list);
                
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(data2);
                $('#param3').val(data3);
                $('#param4').val(JSON.stringify(cs_list));
                $('#param5').val(JSON.stringify(doc_list));
                $('#param6').val(JSON.stringify(po_list));
                $('#param7').val(JSON.stringify(pt_list));
                $('#param8').val(data12);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();

                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR8600':
            case 'SR8601':
            case 'SR8602':
            case 'SR8603':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    let fromMonth, toMonth = '0';
                    if (inputData[0].value.length > 0 && inputData[1].value.length > 0) {
                        fromMonth = inputData[0].value.split("-").reverse().join("-");
                        toMonth = inputData[1].value.split("-").reverse().join("-");
                        url = '/reports/print_' + hdReportId + '/' + fromMonth + '/' + toMonth;
                        frViewPDF.setAttribute("src", url);
                        divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR8500':
                inputData = divFilter.getElementsByTagName("input");
                let fromDate = '0', toDate = '0';
                if (inputData.length > 0) {
                    if (inputData[0].value.length > 0) {
                        fromDate = inputData[0].value.split("-").reverse().join("-");
                    }
                    if (inputData[1].value.length > 0) {
                        toDate = inputData[1].value.split("-").reverse().join("-");
                    }
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data0 = selectData[0].value ? selectData[0].value : '0';
                    data1 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                }
                var pt_list = param_list_string(data1, data2, usb_part_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(fromDate);
                $('#param1').val(toDate);
                $('#param2').val(data0);
                $('#param3').val(JSON.stringify(pt_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;

                break;
            // case 'SR8601':
            // case 'SR8602':
            //     inputData = divFilter.getElementsByTagName("input");
            //     if (inputData.length > 0) {
            //         if (inputData[0].value.length > 0) {
            //             url = '/reports/print_' + hdReportId + '/' + inputData[0].value.split("-").reverse().join("-") + '/';
            //             frViewPDF.setAttribute("src", url);
            //             divViewPDF.innerHTML = frViewPDF.outerHTML;
            //         }
            //         else {
            //             pop_ok_dialog("Invalid Date",
            //                 EMPTY_DATE_MSG,
            //                 function () {
            //                     $("#loadpage").hide();
            //                 }
            //             );
            //         }
            //     }
            //     break;
            // case 'SR8603':
            case 'SR8700':
            case 'SR8700_1':
            case 'SR8701':
            case 'GL2200':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    url = '/reports/print_' + hdReportId + '/' + inputData[0].value.split("-").reverse().join("-") + '/';
                    frViewPDF.setAttribute("src", url);
                    divViewPDF.innerHTML = frViewPDF.outerHTML;
                }
                break;
            case 'TL1200':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                }
                var tx_list = param_list_string(data1, data2, tax_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(tx_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'CL2100':
                selectData = divFilter.getElementsByTagName("select");
                selected = selectData[0].value ? selectData[0].value : '0';
                if (selected) {
                    url = '/reports/print_' + hdReportId + '/' + selected + '/';
                } else {
                    url = '/reports/print_' + hdReportId + '/0/';
                }
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2100':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var sp_list = param_list_string(data5, data6, supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2200':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var cs_list = param_list_string(data5, data6, customer_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2201':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                    data7 = selectData[6].value ? selectData[6].value : '0';
                    data8 = selectData[7].value ? selectData[7].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var cs_list = param_list_string(data5, data6, customer_list);
                var sp_list = param_list_string(data7, data8, supplier_list);

                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'DL2400':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                }
                var cs_list = param_list_string(data1, data2, cfl_customer_list);
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'CL2400':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                }
                var sp_list = param_list_string(data1, data2, sfl_supplier_list);
                url = '/reports/print_' + hdReportId + '/';
                global_url = url;
                $('#param0').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            default:
                frViewPDF.setAttribute("src", '/reports/print_' + hdReportId + '/');
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
        }
    }
    document.getElementById("frViewPDF").onload = function () {
        $("#loadpage").hide();
    }

});

$('#export_excel').on('keydown', function (e) {
    if (e.which == 13) {
        $(this).click();
    }
});

$('#export_excel').on('click', function () {
    var frViewPDF = $('#frViewPDF')[0];
    var divViewPDF = $('#divViewPDF')[0];
    var hdReportId = $('#hdReportId').val();
    var divFilter = $('.div' + hdReportId)[0];
    var url = "";

    $("#loadpage").show();
    if (hdReportId == '0') {
        frViewPDF.setAttribute("src", "");
        divViewPDF.innerHTML = frViewPDF.outerHTML;
    }
    // =====================Print Order : get order_type and order_id=======================
    var hd_order_type = $('#hdOrderType').val();
    var hd_order_id = $('#hdOrderID').val();
    var hd_print_type = $('#hdPrintType').val();
    var po_print_header = $('input[name=po-group-print-header]:checked').val();
    var do_print_header = $('input[name=do-group-print-header]:checked').val();
    if (hd_order_type != 0 && hd_order_id != 0) {
        if (hd_order_type == 2) {//Print Purchase Order
            url = '/reports/print_po_order/' + hd_order_id + '/' + po_print_header + '/';
            frViewPDF.setAttribute("src", url);
            divViewPDF.innerHTML = frViewPDF.outerHTML;

            $('#secReportList').css("display", "none");
            $('.filter').css("display", "none");
            $('#divPO').removeAttr("style");
        }
        else if (hd_order_type == 6) {
            if (hd_print_type == 2) {//Print Tax Invoice
                url = '/reports/print_tax_invoice/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 1) {//Print Delivery Order
                url = '/reports/print_do/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 3) {//Print Paking List
                url = '/reports/print_packing_list/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
            if (hd_print_type == 4) {//Print Invoice
                url = '/reports/print_invoice/' + hd_order_id + '/' + do_print_header + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;

                $('#secReportList').css("display", "none");
                $('.filter').css("display", "none");
                $('#divDO').removeAttr("style");
            }
        }
    }// ====================================End print order==================================
    else {
        //Print SR.... reports
        switch (hdReportId) {
            case 'SR7203':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                cp_list = param_list_string(data4, data5, upo_cust_po_list);
                p_list = param_list_string(data2, data3, upo_supplier_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#param3').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7204':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                p_list = param_list_string(data4, data5, upo_part_list);
                sp_list = param_list_string(data2, data3, upo_supplier_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(sp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            // case 'SR7205':
            case 'SR7404':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                    data6 = selectData[4].value ? selectData[4].value : '0';
                    data7 = selectData[5].value ? selectData[5].value : '0';
                }
                grp_list = param_list_string(data6, data7, uso_part_group_list);
                p_list = param_list_string(data4, data5, uso_part_list);
                cs_list = param_list_string(data2, data3, uso_customer_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(JSON.stringify(grp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7300':
            case 'SR7301':
            case 'SR7302':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    if(data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                        }
                        url = '/reports/print_xls_' + hdReportId + '/' + data0 + '/' + data1 + '/' + data2 + '/';
                        frViewPDF.setAttribute("src", url);
                        divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7101':
                var sa_confirm = 'Y';
                // sa_confirm = $("input[name='sa_print_selection']:checked").val();
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data2 != '0' && data3 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                } else if (data2 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data3 != '0') {
                    insert = true;
                    $.each(sa_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, sa_part_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(sa_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7103':
                var sa_confirm = 'Y';
                // sa_confirm = $("input[name='sa_print_selection']:checked").val();
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data6 = selectData[0].value ? selectData[0].value : '0';
                    data7 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data2 != '0' && data3 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                } else if (data2 != '0') {
                    insert = false;
                    $.each(sa_customer_po_list, function(i, v){
                        if (data2 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data3 != '0') {
                    insert = true;
                    $.each(sa_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data3 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, sa_part_list);
                cu_list = param_list_string(data6, data7, sa_customer_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(p_list));
                $('#param4').val(JSON.stringify(cu_list));
                $('#param5').val(sa_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7102':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                if(data0.length > 1) {
                    selectData = divFilter.getElementsByTagName("select");
                    if (selectData.length > 0) {
                        data2 = selectData[0].value ? selectData[0].value : '0';
                        data3 = selectData[1].value ? selectData[1].value : '0';
                    }
                    pg_list = param_list_string(data2, data3, sa_part_grp_list);

                    url = '/reports/print_xls_' + hdReportId + '/';
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(pg_list));
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR7201':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                p_list = param_list_string(data2, data3, upo_doc_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7202':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                p_list = param_list_string(data2, data3, upo_supplier_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7206':
            case 'SR7405':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                }
                url = '/reports/print_xls_' + hdReportId + '/' + data0 + '/' + data1 + '/' + data2 + '/';
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7402':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                cs_list = param_list_string(data2, data3, uso_customer_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7403':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                cs_list = param_list_string(data2, data3, uso_customer_list);
                sp_list = param_list_string(data4, data5, uso_supplier_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7501':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                var sp_list = param_list_string(data2, data3, gr_supplier_list);
                
                if (data0.length > 1) {
                    url = '/reports/print_xls_' + hdReportId + '/';
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(sp_list));
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR7502':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[4].value ? selectData[4].value : '0';
                    data3 = selectData[5].value ? selectData[5].value : '0';
                }
                p_list = param_list_string(data2, data3, gr_part_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(p_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7503':
                var is_confirm = '';
                if (hdReportId == 'SR7503'){
                    is_confirm = $('#is_confirm').val();
                }
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data6 = selectData[0].value ? selectData[0].value : '0';
                    data7 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                    data3 = selectData[3].value ? selectData[3].value : '0';
                    data4 = selectData[4].value ? selectData[4].value : '0';
                    data5 = selectData[5].value ? selectData[5].value : '0';
                }
                cp_list = [];
                if (data6 != '0' && data7 != '0') {
                    insert = false;
                    $.each(gr_customer_po_list, function(i, v){
                        if (data6 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                        if (data7 == v) { insert = false; }
                    })
                } else if (data6 != '0') {
                    insert = false;
                    $.each(gr_customer_po_list, function(i, v){
                        if (data6 == v) { insert = true; }
                        if(insert) { cp_list.push(v); }
                    })
                } else if (data7 != '0') {
                    insert = true;
                    $.each(gr_customer_po_list, function(i, v){
                        if(insert) { cp_list.push(v); }
                        if (data7 == v) { insert = false; }
                    })
                }

                p_list = param_list_string(data4, data5, gr_part_list);
                cu_list = param_list_string(data2, data3, gr_category_list);
                
                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(cp_list));
                $('#param3').val(JSON.stringify(cu_list));
                $('#param4').val(JSON.stringify(p_list));
                $('#param5').val(is_confirm);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7504':
                var is_confirm = '';
                if (hdReportId == 'SR7504'){
                    is_confirm = $('#is_confirm_2').val();
                }
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                }
                var sp_list = param_list_string(data2, data3, gr_supplier_list);
                
                if (data0.length > 1) {
                    url = '/reports/print_xls_' + hdReportId + '/';
                    $('#param0').val(data0);
                    $('#param1').val(data1);
                    $('#param2').val(JSON.stringify(sp_list));
                    $('#param3').val(is_confirm);
                    $('#reportForm').attr('action', url);
                    $('#reportForm').submit();
                    // frViewPDF.setAttribute("src", url);
                    // divViewPDF.innerHTML = frViewPDF.outerHTML;
                } else {
                    pop_ok_dialog("Invalid Date",
                        EMPTY_DATE_MSG,
                        function () {
                            $("#loadpage").hide();
                        }
                    );
                }
                break;
            case 'SR7401':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value ? inputData[0].value.split("-").reverse().join("-") : '0';
                    data1 = inputData[1].value ? inputData[1].value.split("-").reverse().join("-") : '0';
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data2 = selectData[0].value ? selectData[0].value : '0';
                    data3 = selectData[1].value ? selectData[1].value : '0';
                    data4 = selectData[2].value ? selectData[2].value : '0';
                    data5 = selectData[3].value ? selectData[3].value : '0';
                }
                doc_list = param_list_string(data2, data3, uso_doc_list);
                cp_list = param_list_string(data4, data5, uso_cust_po_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(JSON.stringify(doc_list));
                $('#param3').val(JSON.stringify(cp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR7601':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    if(data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                        }
                        var pg_list = param_list_string(data1, data2, msr_part_grp_list);
                        data3 = document.querySelector('input[name="print_selection_SR7601"]:checked').value;

                        url = '/reports/print_xls_' + hdReportId + '/';
                        $('#param0').val(data0);
                        $('#param1').val(JSON.stringify(pg_list));
                        $('#param2').val(data3);
                        $('#reportForm').attr('action', url);
                        $('#reportForm').submit();
                        // frViewPDF.setAttribute("src", url);
                        // divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7602':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    if (data0.length > 0) {
                        selectData = divFilter.getElementsByTagName("select");
                        if (selectData.length > 0) {
                            data1 = selectData[0].value ? selectData[0].value : '0';
                            data2 = selectData[1].value ? selectData[1].value : '0';
                        }
                        data3 = document.querySelector('input[name="print_selection"]:checked').value;

                        url = '/reports/print_' + hdReportId + '/' + data0 + '/' + data1 + '/' + data2 + '/' + data3 + '/';
                        frViewPDF.setAttribute("src", url);
                        divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR7303':
            case 'SR7603':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    data0 = inputData[0].value.split("-").reverse().join("-");
                    data1 = inputData[1].value.split("-").reverse().join("-");
                    data2 = inputData[2].value.split("-").reverse().join("-");
                    data3 = inputData[3].value.split("-").reverse().join("-");
                }
                if (data0.length == 0)
                    data0 = '0';
                if (data1.length == 0)
                    data1 = '0';
                if (data2.length == 0)
                    data2 = '0';
                if (data3.length == 0)
                    data3 = '0';
                
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data4 = selectData[0].value ? selectData[0].value : '0';
                    data5 = selectData[1].value ? selectData[1].value : '0';
                    data6 = selectData[2].value ? selectData[2].value : '0';
                    data7 = selectData[3].value ? selectData[3].value : '0';
                    data8 = selectData[4].value ? selectData[4].value : '0';
                    data9 = selectData[5].value ? selectData[5].value : '0';
                    data10 = selectData[6].value ? selectData[6].value : '0';
                    data11 = selectData[7].value ? selectData[7].value : '0';
                    data12 = selectData[8].value ? selectData[8].value : '0';
                }

                var cs_list = param_list_string(data4, data5, oir_customer_list);
                var doc_list = param_list_string(data6, data7, oir_document_list);
                var po_list = param_list_string(data8, data9, oir_customer_po_list);
                var pt_list = param_list_string(data10, data11, oir_part_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(data0);
                $('#param1').val(data1);
                $('#param2').val(data2);
                $('#param3').val(data3);
                $('#param4').val(JSON.stringify(cs_list));
                $('#param5').val(JSON.stringify(doc_list));
                $('#param6').val(JSON.stringify(po_list));
                $('#param7').val(JSON.stringify(pt_list));
                $('#param8').val(data12);
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SR8600':
            case 'SR8601':
            case 'SR8602':
            case 'SR8603':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    let fromMonth, toMonth = '0';
                    if (inputData[0].value.length > 0 && inputData[1].value.length > 0) {
                        fromMonth = inputData[0].value.split("-").reverse().join("-");
                        toMonth = inputData[1].value.split("-").reverse().join("-");
                        url = '/reports/print_xls_' + hdReportId + '/' + fromMonth +'/' + toMonth;
                        frViewPDF.setAttribute("src", url);
                        divViewPDF.innerHTML = frViewPDF.outerHTML;
                    } else {
                        pop_ok_dialog("Invalid Date",
                            EMPTY_DATE_MSG,
                            function () {
                                $("#loadpage").hide();
                            }
                        );
                    }
                }
                break;
            case 'SR8500':
                inputData = divFilter.getElementsByTagName("input");
                let fromDate = '0', toDate = '0';
                if (inputData.length > 0) {
                    if (inputData[0].value.length > 0) {
                        fromDate = inputData[0].value.split("-").reverse().join("-");
                    }
                    if (inputData[1].value.length > 0) {
                        toDate = inputData[1].value.split("-").reverse().join("-");
                    }
                }
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data0 = selectData[0].value ? selectData[0].value : '0';
                    data1 = selectData[1].value ? selectData[1].value : '0';
                    data2 = selectData[2].value ? selectData[2].value : '0';
                }
                var pt_list = param_list_string(data1, data2, usb_part_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(fromDate);
                $('#param1').val(toDate);
                $('#param2').val(data0);
                $('#param3').val(JSON.stringify(pt_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();

                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            // case 'SR8601':
            // case 'SR8602':
            //     inputData = divFilter.getElementsByTagName("input");
            //     if (inputData.length > 0) {
            //         if (inputData[0].value.length > 0) {
            //             url = '/reports/print_xls_' + hdReportId + '/' + inputData[0].value.split("-").reverse().join("-") + '/';
            //             frViewPDF.setAttribute("src", url);
            //             divViewPDF.innerHTML = frViewPDF.outerHTML;
            //         }
            //         else {
            //             pop_ok_dialog("Invalid Date",
            //                 EMPTY_DATE_MSG,
            //                 function () {
            //                     $("#loadpage").hide();
            //                 }
            //             );
            //         }
            //     }
            //     break;
            // case 'SR8603':
            case 'SR8700':
            case 'SR8700_1':
            case 'SR8701':
            case 'GL2200':
            case 'CL2400':
                inputData = divFilter.getElementsByTagName("input");
                if (inputData.length > 0) {
                    url = '/reports/print_' + hdReportId + '/' + inputData[0].value.split("-").reverse().join("-") + '/';
                    frViewPDF.setAttribute("src", url);
                    divViewPDF.innerHTML = frViewPDF.outerHTML;
                }
                break;
            case 'TL1200':
            case 'CL2100':
                selectData = divFilter.getElementsByTagName("select");
                selected = selectData[0].value ? selectData[0].value : '0';
                if (selected) {
                    url = '/reports/print_' + hdReportId + '/' + selected + '/';
                } else {
                    url = '/reports/print_' + hdReportId + '/0/';
                }
                frViewPDF.setAttribute("src", url);
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2100':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var sp_list = param_list_string(data5, data6, supplier_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2200':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var cs_list = param_list_string(data5, data6, customer_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(cs_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            case 'SL2201':
                selectData = divFilter.getElementsByTagName("select");
                if (selectData.length > 0) {
                    data1 = selectData[0].value ? selectData[0].value : '0';
                    data2 = selectData[1].value ? selectData[1].value : '0';
                    data3 = selectData[2].value ? selectData[2].value : '0';
                    data4 = selectData[3].value ? selectData[3].value : '0';
                    data5 = selectData[4].value ? selectData[4].value : '0';
                    data6 = selectData[5].value ? selectData[5].value : '0';
                    data7 = selectData[6].value ? selectData[6].value : '0';
                    data8 = selectData[7].value ? selectData[7].value : '0';
                }
                var pt_list = param_list_string(data1, data2, part_list);
                var pg_list = param_list_string(data3, data4, part_group_list);
                var cs_list = param_list_string(data5, data6, customer_list);
                var sp_list = param_list_string(data7, data8, supplier_list);

                url = '/reports/print_xls_' + hdReportId + '/';
                $('#param0').val(JSON.stringify(pt_list));
                $('#param1').val(JSON.stringify(pg_list));
                $('#param2').val(JSON.stringify(cs_list));
                $('#param3').val(JSON.stringify(sp_list));
                $('#reportForm').attr('action', url);
                $('#reportForm').submit();
                // frViewPDF.setAttribute("src", url);
                // divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
            default:
                frViewPDF.setAttribute("src", '/reports/print_' + hdReportId + '/');
                divViewPDF.innerHTML = frViewPDF.outerHTML;
                break;
        }
    }
    document.getElementById("frViewPDF").onload = function () {
        $("#loadpage").hide();
    }

});


$("#reportForm").submit(function (e) {
    if (global_url != '') {
        // preventing from page reload and default actions
        e.preventDefault();
        // serialize the data for sending the form data.
        var serializedData = $(this).serialize();
        // make POST ajax call
        $.ajax({
            type: 'POST',
            url: global_url,
            data: serializedData,
            success: function (data, textStatus, request) {
                var disposition = request.getResponseHeader('content-disposition');
                var matches = /"([^"]*)/.exec(disposition);
                var filename = (matches != null && matches[1] ? matches[1] : 'file.pdf');
                var frViewPDF = $('#frViewPDF')[0];

                var blob = b64toBlob(data, 'application/pdf');
                var blobUrl = URL.createObjectURL(blob);
                
                // data = Base64.encode(data);
                // data = btoa(unescape(encodeURIComponent(data)));
                // data = btoa(encodeURIComponent(data).replace(/%([0-9A-F]{2})/g,
                //         function toSolidBytes(match, p1) {
                //             return String.fromCharCode('0x' + p1);
                //     }));
                frViewPDF.setAttribute("src", blobUrl);
                // frViewPDF.setAttribute("src", 'data:application/pdf;base64,'+data);
                try{
                    $('#a_download').remove();
                } catch(e) {

                }
                var aTag = $("<a class='btn btn-danger' id='a_download' style='margin-bottom: 10px; float: right'><i class='fa fa-download' aria-hidden='true'></i>  Download</a>").attr({
                    "href": 'data:application/pdf;base64,'+data,
                    "download": filename
                });
                aTag.insertBefore($(frViewPDF));
                global_url = '';
            },
            error: function (response) {
                // alert the error if any error occured
                global_url = '';
            }
        })
    }
})

function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;
  
    var byteCharacters = atob(b64Data);
    var byteArrays = [];
  
    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      var slice = byteCharacters.slice(offset, offset + sliceSize);
  
      var byteNumbers = new Array(slice.length);
      for (var i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
  
      var byteArray = new Uint8Array(byteNumbers);
  
      byteArrays.push(byteArray);
    }
      
    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
  }

// var Base64 = {

//     // private property
//     _keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    
//     // public method for encoding
//     encode : function (input) {
//         var output = "";
//         var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
//         var i = 0;
    
//         input = Base64._utf8_encode(input);
    
//         while (i < input.length) {
    
//             chr1 = input.charCodeAt(i++);
//             chr2 = input.charCodeAt(i++);
//             chr3 = input.charCodeAt(i++);
    
//             enc1 = chr1 >> 2;
//             enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
//             enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
//             enc4 = chr3 & 63;
    
//             if (isNaN(chr2)) {
//                 enc3 = enc4 = 64;
//             } else if (isNaN(chr3)) {
//                 enc4 = 64;
//             }
    
//             output = output +
//             this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
//             this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
    
//         }
    
//         return output;
//     },
    
//     // public method for decoding
//     decode : function (input) {
//         var output = "";
//         var chr1, chr2, chr3;
//         var enc1, enc2, enc3, enc4;
//         var i = 0;
    
//         input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
    
//         while (i < input.length) {
    
//             enc1 = this._keyStr.indexOf(input.charAt(i++));
//             enc2 = this._keyStr.indexOf(input.charAt(i++));
//             enc3 = this._keyStr.indexOf(input.charAt(i++));
//             enc4 = this._keyStr.indexOf(input.charAt(i++));
    
//             chr1 = (enc1 << 2) | (enc2 >> 4);
//             chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
//             chr3 = ((enc3 & 3) << 6) | enc4;
    
//             output = output + String.fromCharCode(chr1);
    
//             if (enc3 != 64) {
//                 output = output + String.fromCharCode(chr2);
//             }
//             if (enc4 != 64) {
//                 output = output + String.fromCharCode(chr3);
//             }
    
//         }
    
//         output = Base64._utf8_decode(output);
    
//         return output;
    
//     },
    
//     // private method for UTF-8 encoding
//     _utf8_encode : function (string) {
//         string = string.replace(/\r\n/g,"\n");
//         var utftext = "";
    
//         for (var n = 0; n < string.length; n++) {
    
//             var c = string.charCodeAt(n);
    
//             if (c < 128) {
//                 utftext += String.fromCharCode(c);
//             }
//             else if((c > 127) && (c < 2048)) {
//                 utftext += String.fromCharCode((c >> 6) | 192);
//                 utftext += String.fromCharCode((c & 63) | 128);
//             }
//             else {
//                 utftext += String.fromCharCode((c >> 12) | 224);
//                 utftext += String.fromCharCode(((c >> 6) & 63) | 128);
//                 utftext += String.fromCharCode((c & 63) | 128);
//             }
    
//         }
    
//         return utftext;
//     },
    
//     // private method for UTF-8 decoding
//     _utf8_decode : function (utftext) {
//         var string = "";
//         var i = 0;
//         var c = c1 = c2 = 0;
    
//         while ( i < utftext.length ) {
    
//             c = utftext.charCodeAt(i);
    
//             if (c < 128) {
//                 string += String.fromCharCode(c);
//                 i++;
//             }
//             else if((c > 191) && (c < 224)) {
//                 c2 = utftext.charCodeAt(i+1);
//                 string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
//                 i += 2;
//             }
//             else {
//                 c2 = utftext.charCodeAt(i+1);
//                 c3 = utftext.charCodeAt(i+2);
//                 string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
//                 i += 3;
//             }
    
//         }
    
//         return string;
//     }
    
// }
