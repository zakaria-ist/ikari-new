/*---LEFT BAR ACCORDION----*/
$(function() {
    $('#nav-accordion').dcAccordion({
        eventType: 'click',
        autoClose: true,
        saveState: true,
        disableLink: true,
        speed: 'slow',
        showCount: false,
        autoExpand: true,
//        cookie: 'dcjq-accordion-1',
        classExpand: 'dcjq-current-parent'
    });
});


function roundDecimal(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    var interm = (value * multiplier).toFixed(1);
    return Math.round(interm) / multiplier;
}

var Script = function () {

//    sidebar dropdown menu auto scrolling

    jQuery('#sidebar .sub-menu > a').click(function () {
        var o = ($(this).offset());
        diff = 250 - o.top;
        if(diff>0)
            $("#sidebar").scrollTo("-="+Math.abs(diff),500);
        else
            $("#sidebar").scrollTo("+="+Math.abs(diff),500);
    });

//    sidebar toggle

    $(function() {
        function responsiveView() {
            // if ($('#sidebar').is(":visible") === true) {
                var wSize = $(window).width();
                if (wSize <= 768) {
                    $('#container').addClass('sidebar-close');
                    $('#sidebar > ul').hide();
                }

                if (wSize > 768) {
                    $('#container').removeClass('sidebar-close');
                    $('#sidebar > ul').show();
                }
            // }
        }
        $(window).on('load', responsiveView);
        $(window).on('resize', responsiveView);
    });

    $('.fa-bars').click(function () {
        if ($('#sidebar > ul').is(":visible") === true) {
            $('#main-content').css({
                'margin-left': '0px'
            });
            $('#sidebar').css({
                // 'margin-left': '-310px'
                'display': 'none'
            });
            try{
                if ( $.fn.DataTable.isDataTable( '.table' ) ) {
                    $('.table').DataTable().columns.adjust();
                }
            }
            catch(error){
                console.log(error);
            }
            $('#sidebar > ul').hide();
            $("#container").addClass("sidebar-closed");
            window.sessionStorage.setItem('is_sidebar', '0');
        } else {
            $('#main-content').css({
                'margin-left': '310px'
            });
            try{
                if ( $.fn.DataTable.isDataTable( '.table' ) ) {
                    $('.table').DataTable().columns.adjust();
                }
            }
            catch(error){
                console.log(error);
            }
            $('#sidebar > ul').show();
            $('#sidebar').css({
                // 'margin-left': '0'
                'display': 'block'
            });
            $("#container").removeClass("sidebar-closed");
            window.sessionStorage.setItem('is_sidebar', '1');
        }
    });

// custom scrollbar
//     $("#sidebar").niceScroll({styler:"fb",cursorcolor:"#e8403f", cursorwidth: '3', cursorborderradius: '10px', background: '#404040', spacebarenabled:false, cursorborder: ''});
//
//     $("html").niceScroll({styler:"fb",cursorcolor:"#e8403f", cursorwidth: '6', cursorborderradius: '10px', background: '#404040', spacebarenabled:false,  cursorborder: '', zindex: '1000'});

// widget tools

    jQuery('.panel .tools .fa-chevron-down').click(function () {
        var el = jQuery(this).parents(".panel").children(".panel-body");
        if (jQuery(this).hasClass("fa-chevron-down")) {
            jQuery(this).removeClass("fa-chevron-down").addClass("fa-chevron-up");
            el.slideUp(200);
        } else {
            jQuery(this).removeClass("fa-chevron-up").addClass("fa-chevron-down");
            el.slideDown(200);
        }
    });


    jQuery('.panel .tools .fa-times').click(function () {
        jQuery(this).parents(".panel").parent().remove();
    });


//    tool tips

    $('.tooltips').tooltip();

//    popovers

    $('.popovers').popover();



// custom bar chart

    if ($(".custom-bar-chart")) {
        $(".bar").each(function () {
            var i = $(this).find(".value").html();
            $(this).find(".value").html("");
            $(this).find(".value").animate({
                height: i
            }, 2000)
        })
    }

}();

function pop_info_dialog(title, text, type){
    $.confirm({
        closeIcon: true,
        title: title,
        content: text,
        buttons: {
            Ok: {
                btnClass: 'btn-success, Ok',
                action: function(){}
                }
        },
        onOpen: function() {
            $('.Ok').focus();
        }
    });
}

function pop_ok_dialog(title, text, function_call){
    $.confirm({
        closeIcon: true,
        title: title,
        content: text,
        buttons: {
            Ok: {
                btnClass: 'btn-success, Ok',
                action: function_call
                }
        },
        onOpen: function() {
            $('.Ok').focus();
        }
    });

}

function pop_focus_invalid_dialog(title, text, function_call, idFirstInvalid){
    $.confirm({
        closeIcon: true,
        title: title,
        content: text,
        scrollToPreviousElement: false,
        buttons: {
            Ok: {
                btnClass: 'btn-success, Ok',
                action: function_call
                }
        },
        onOpen: function() {
            $('.Ok').focus();
        },
        onClose: function() {
            $(idFirstInvalid).focus();
            if ($(idFirstInvalid).is('select')) {
                $(idFirstInvalid).select2('open');
            }
        }
    });
}

function pop_ok_cancel_dialog(title, text, ok_function, cancel_function, cancelText){
    $.confirm({
        closeIcon: true,
        title: title,
        content: text,
        buttons: {
            Yes: {
                btnClass: 'btn-success, Yes',
                action: ok_function
            },
            Reset: {
                btnClass: 'btn-default, Reset',
                action: cancel_function
            }
        },
        onOpen: function() {
            $('.Yes').focus();
            document.addEventListener("keydown", function(e){
                if(e.which == 37){
                  $('.Yes').focus();
                }
                if(e.which == 39){
                 $('.Reset').focus();
                }
             });
        },
        onClose: function() {
            // document.removeEventListener("keydown", function(e){});
        }
    });
}

$('body').on('keydown', function (event) {
    try {
        if ($("#dialog-ok-modal").dialog('isOpen')){
            if (event.keyCode === $.ui.keyCode.ENTER || event.keyCode === $.ui.keyCode.ESCAPE) {
                $('.dialog-ok-button').trigger('click');
                $('.dialog-ok-button').blur();
                event.stopPropagation();
            }
        } else if ($("#dialog-yes-no-modal").dialog('isOpen')) {
            if (event.keyCode === $.ui.keyCode.ESCAPE) {
                $('.dialog-no-button').trigger('click');
                $('.dialog-no-button').blur();
                event.stopPropagation();
            } else if (event.keyCode === $.ui.keyCode.ENTER) {
                if ($('.ui-dialog-buttonpane').find('button:contains("Yes")').hasClass('ui-state-focus')) {
                    $('.dialog-yes-button').trigger('click');
                    $('.dialog-yes-button').blur();
                    event.stopPropagation();
                } else {
                    $('.dialog-no-button').trigger('click');
                    $('.dialog-no-button').blur();
                    event.stopPropagation();
                }
            }
        }
    }
    
    catch(error) {
        try {
            if ($("#dialog-yes-no-modal").dialog('isOpen')){
                if (event.keyCode === $.ui.keyCode.ESCAPE) {
                    $('.dialog-no-button').trigger('click');
                    $('.dialog-no-button').blur();
                    event.stopPropagation();
                } else if (event.keyCode === $.ui.keyCode.ENTER) {
                    if ($('.ui-dialog-buttonpane').find('button:contains("Yes")').hasClass('ui-state-focus')) {
                        $('.dialog-yes-button').trigger('click');
                        $('.dialog-yes-button').blur();
                        event.stopPropagation();
                    } else {
                        $('.dialog-no-button').trigger('click');
                        $('.dialog-no-button').blur();
                        event.stopPropagation();
                    }
                }
            }
        } catch(error){

        }
    }
    
});

function int_comma (x, digit){
    return x.toLocaleString('en-US', {minimumFractionDigits: digit});
}

function dateView(date){
    var pecahin = date.split('-');
    var today = pecahin[2]+'-'+pecahin[1]+'-'+pecahin[0];
    return today;
}

function get_element_offset(current_element, filter_val, offset){
    form = $(current_element).parents('form:eq(0)');
    targetFocusElm = form.find('input, select, textarea');
    if(filter_val !== ''){
        targetFocusElm = targetFocusElm.filter(filter_val);
    }
    return targetFocusElm.eq(targetFocusElm.index(current_element) + offset);
}

function move_next_elem(elem, offset){

    nextElm = get_element_offset(elem, ':focusable', offset);
    try {
        if ($("#dialog-ok-modal").dialog("isOpen") || $("#dialog-yes-no-modal").dialog("isOpen")) {
            setTimeout(function() {

            if (nextElm.length){
                nextElm.focus();
                nextElm.select();
            }
        }, 300);

            return false;
        }
        else {
            if (nextElm.length){
                nextElm.focus();
                nextElm.select();
            }
        }
    }
    catch(error) {
        try{
            if ($("#dialog-yes-no-modal").dialog("isOpen")) {
                setTimeout(function () {

                    if (nextElm.length) {
                        nextElm.focus();
                        nextElm.select();
                    }
                }, 300);

                return false;
            } else {
                if (nextElm.length) {
                    nextElm.focus();
                    nextElm.select();
                }
            }
        } catch(error){
            if (nextElm.length) {
                nextElm.focus();
                nextElm.select();
            }
        }
    }
}

function checkFormValidity(){

    var no_item_yet = false;
    $('#dynamic-table tr.gradeX:last').each(function () {
        var $line_number = $(this).find("input[name*='line_number']").val();

        if($line_number == ''){
            no_item_yet = true;
            return;
        }
    });

    if (no_item_yet){
        return true;
    }

    var $myForm = $('#btnSave').closest("form");

    if(! $myForm[0].checkValidity()) {
      return false;
    }

    return true;
}

function set_order_item_dates(){

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

}

// calculate subtotal and total
function calculateTotal(selector, index_qty, index_price, index_amt, index_lbl_amt, decimal_place=2) {
    var subtotal = 0;
    var total = 0;
    var tax_rate = $('#hdTaxRate').val();
    // console.log('calculateTotal')
    $('#dynamic-table tr.gradeX').each(function () {
        var currentRow = $(this).find('input');
        var currentLabel = $(this).find('label');
        amount = float_format(currentRow[index_qty].value) * float_format(currentRow[index_price].value);
        amount = roundDecimal(amount, decimal_place);
        currentRow[index_amt].value = amount.toFixed(decimal_place);
        if (typeof index_lbl_amt !== 'undefined'){
            currentLabel[index_lbl_amt].textContent = comma_format(amount, decimal_place);
        }
        subtotal += amount;
    });
    $('#id_subtotal').val(comma_format(subtotal, decimal_place));
    var tax_amount = 0;
    if (tax_rate > 0){
        tax_amount = (float_format(tax_rate) * float_format($('#id_subtotal').val())) / 100;
    }
    tax_amount = roundDecimal(tax_amount, decimal_place);
    $('#id_tax_amount').val(comma_format(tax_amount, decimal_place));
    if ($('#id_discount').val() == '' || $('#id_discount').val() == null) {
        total = subtotal + float_format($('#id_tax_amount').val());
    } else {
        total = subtotal + float_format($('#id_tax_amount').val()) - float_format($('#id_discount').val());
    }
    total = roundDecimal(total, decimal_place);
    $('#id_total').val(comma_format(total, decimal_place));
}

function recalculateAmount(element, index_qty, index_price, index_amt, index_lbl_amt, return_value, decimal_place=2){
    return_value = (return_value !== undefined);
    if (!return_value) {
        currentRow = $(element).closest('tr').find('input');
        currentLabel = $(element).closest('tr').find('label');
        
        var quantity = float_format(currentRow[index_qty].value);
        var price = float_format(currentRow[index_price].value);
    
        $('#'+currentRow[index_amt].id).val(roundDecimal(price * quantity, decimal_place).toFixed(decimal_place)).trigger("change");

        if (typeof index_lbl_amt !== 'undefined') {
            currentLabel[index_lbl_amt].textContent = comma_format(roundDecimal(price * quantity, decimal_place), decimal_place);
        }
    }
    else {
        return (roundDecimal(index_qty * index_price, decimal_place));
    }
}

function adjust_input_date(element, event){
    var foo = $(element).val().split("-").join(""); // remove hyphens
    if (foo.length > 4) {
        foo = foo.substring(0,2) + '-' + foo.substring(2,4) + '-' + foo.substring(4, foo.length);
    }else if (foo.length > 2){
        foo = foo.substring(0,2) + '-' + foo.substring(2, foo.length);
    }

    $(element).val(foo);
}

function adjust_input_month_year(element, event){
    var foo = $(element).val().split("-").join(""); // remove hyphens
     if (foo.length > 2){
        foo = foo.substring(0,2) + '-' + foo.substring(2, foo.length);
    }

    $(element).val(foo);
}

function date_key_down(element){
    var current_value = $(element).val();

    if (current_value.length > 0)
        $(element).val(current_value).trigger("change");
    
    if (($(element).prop('required') && moment(current_value, "DD-MM-YYYY", true).isValid()) ||
        !$(element).prop('required') && current_value.length ==0 )
        move_next_elem(element, 1);
}

function get_date_from(id){
    var date_from = $(id).val();
    if(date_from.length == 5){
        date_from = date_from.split('-');
        if(date_from.length == 2){
            date_from = date_from.concat((new Date()).getFullYear());
            date_from = date_from.join('-');
            $(id).val(date_from);
        }
    }

    return date_from;
}

function get_date_from_by_val(val){
    var date_from = val;
    if(date_from.length == 5){
        date_from = date_from.split('-');
        if(date_from.length == 2){
            date_from = date_from.concat((new Date()).getFullYear());
            date_from = date_from.join('-');
            $(id).val(date_from);
        }
    }

    return date_from;
}

$(document).on('click, focus', 'input[type="text"]', function(){
    $(this).select();
});

$(document).on('click, focus', 'input[type="number"]', function(){
    $(this).select();
});

$(document).on('click, focus', 'textarea', function(){
    $(this).select();
});

$(document).on('keydown', '.select2-search__field', function(e){   
    var keycode = (e.keyCode ? e.keyCode : e.which);
    if(keycode == '32'){
        setTimeout(() => {
            let value = $.trim($(this).val());
            $(this).val(value).trigger('input');
        }, 1000);
    }
});

function prefill_select2(event){
/** * Pre-fills the search box with the current text from the Label. * Executes when the dropdown is opened */
    if ($( event.target ).val() !== ''){
        var input = $( event.target ).select2('data');

        if (!input[0]) {
            var search = $(".select2-search__field");

            search.val( $( event.target ).find('option[value="0"]').html() );
            search.select();
        }
        else {
            var value = input[0].text;
    
            if ( value !== null && $.trim(value) !== ""){
                var search = $(".select2-search__field");
                if ( search.length > 0){
                    search.val( value );
                    search.select();
                }
            }
        }
    }
}


function checkForm(form) {
    $('#loading').show();
    try {
        form.btnSave.disabled = true;
    } catch (e) {
        console.log(e);
    }
    try {
        form.btnSend.disabled = true;
    } catch (e) {
        console.log(e);
    }
    try {
        form.is_posted.disabled = true;
    } catch (e) {
        console.log(e);
    }
    try {
        form.btnRemove.disabled = true;
    } catch (e) {
        console.log(e);
    }
    try {
        form.btnReverse.disabled = true;
    } catch (e) {
        console.log(e);
    }
    try {
        form.customer.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.account_set.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.document_type.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.supplier.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.code.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.currency.disabled = false;
    } catch (e) {
        console.log(e);
    }
    try {
        form.sale_price.value = float_format(form.sale_price.value);
    } catch (e) {
        console.log(e);
    }
    try {
        form.purchase_price.value = float_format(form.purchase_price.value);
    } catch (e) {
        console.log(e);
    }
    try {
        form.stockist_price.value = float_format(form.stockist_price.value);
    } catch (e) {
        console.log(e);
    }
    try {
        form.price.value = float_format(form.price.value);
        form.amount.value = float_format(form.amount.value);
        form.total.value = float_format(form.total.value);
        form.subtotal.value = float_format(form.subtotal.value);
        form.tax_amount.value = float_format(form.tax_amount.value);
        form.quantity.value = float_format(form.quantity.value);
        form.quantity_do.value = float_format(form.quantity_do.value);
    }  catch (e) {
        console.log(e);
    }
    try {
        form.amount.value = float_format(form.amount.value);
        form.tax_amount.value = float_format(form.tax_amount.value);
        form.total_amount.value = float_format(form.total_amount.value);
        form.original_amount.value = float_format(form.original_amount.value);
        form.payment_amount.value = float_format(form.payment_amount.value);
        form.receipt_unapplied.value = float_format(form.receipt_unapplied.value);
        form.customer_unapplied.value = float_format(form.customer_unapplied.value);
        form.batch_amount.value = float_format(form.batch_amount.value);
    } catch (e) {
        console.log(e);
    }
    try {
        form.debit_amount.value = float_format(form.debit_amount.value);
        form.credit_amount.value = float_format(form.credit_amount.value);
    } catch (e) {
        console.log(e);
    }
    try {
        form.exchange_rate.value = float_format(form.exchange_rate.value).toFixed(10);
        form.tax_exchange_rate.value = float_format(form.tax_exchange_rate.value).toFixed(10);
    } catch (e) {
        console.log(e);
    }
    return true;
}


function checkPost() {
    $('#loading').show();
    try {
        $(this).disabled = true;
    } catch (e) {
        console.log(e);
    }
    return true;
}


function comma_format( number, decimals = 2, dec_point = '.', thousands_sep = ',' ) {
	// http://kevin.vanzonneveld.net
	// +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
	// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +	 bugfix by: Michael White (http://crestidg.com)
	// +	 bugfix by: Benjamin Lupton
	// +	 bugfix by: Allan Jensen (http://www.winternet.no)
	// +	revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)	
	// *	 example 1: number_format(1234.5678, 2, '.', '');
	// *	 returns 1: 1234.57	 
    
    // var n = number;
    var c = isNaN(decimals = Math.abs(decimals)) ? 2 : decimals;
    var s_number_arr = String(number).split('.');
    if (s_number_arr.length > 1 && s_number_arr[1].length > c) {
        s_number_arr[1] = s_number_arr[1].substring(0, (c+1));
    }
    var f_number = parseFloat(s_number_arr.join('.'));
    var n = 0;
    if (f_number < 0) {
        n = (-1) * Math.round(Math.round(Math.abs(f_number)*10**(c+1))/10)/10**c;
    } else {
        n = Math.round(Math.round(f_number*10**(c+1))/10)/10**c;
    }
    // console.log(number, f_number, n)
	var d = dec_point == undefined ? "," : dec_point;
	var t = thousands_sep == undefined ? "." : thousands_sep, s = n < 0 ? "-" : "";
	var i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
    var result = s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 
	return result;
}

// returns float equivalent of a number string
function float_format(number_str) {
    if (number_str == '') {
        number_str = '0';
    }
    return parseFloat(String(number_str).replace(/,/g , ''));
}

// returns int equivalent of a number string
function int_format(number_str) {
    return parseInt(float_format(number_str));
}



var ul_array = [];
$(document).on('click', '.table-responsive [data-toggle="dropdown"]', function () {
    // if the button is inside a modal
    if ($('body').hasClass('modal-open')) {
        throw new Error("This solution is not working inside a responsive table inside a modal, you need to find out a way to calculate the modal Z-index and add it to the element")
        return true;
    }

    ul_array.forEach(element => {
        element.css('display', 'none');
    });
    ul_array.length = 0;

    $buttonGroup = $(this).parent();
    if (!$buttonGroup.attr('data-attachedUl')) {
        var ts = +new Date;
        $ul = $(this).siblings('ul');
        $ul.attr('data-parent', ts);
        $buttonGroup.attr('data-attachedUl', ts);
        $(window).resize(function () {
            $ul.css('display', 'none').data('top');
        });
    } else {
        $ul = $('[data-parent=' + $buttonGroup.attr('data-attachedUl') + ']');
    }
    if (!$buttonGroup.hasClass('open')) {
        $ul.css('display', 'none');
        return;
    }
    ul_array.push($ul);
    dropDownFixPosition($(this).parent(), $ul);
    function dropDownFixPosition(button, dropdown) {
        var dropDownTop = button.offset().top + button.outerHeight();
        dropdown.css('top', dropDownTop + "px");
        dropdown.css('left', (button.offset().left - 100) + "px");
        dropdown.css('position', "absolute");

        dropdown.css('width', (dropdown.width() + 40));
        dropdown.css('heigt', dropdown.height());
        dropdown.css('display', 'block');
        dropdown.appendTo('body');
    }
});


$(document).on('show.bs.modal', '.modal', function () {
    ul_array.forEach(element => {
        element.css('display', 'none');
    });
    ul_array.length = 0;
});

$(document).on('click', '.dropdown-menu li', function () {
    ul_array.forEach(element => {
        element.css('display', 'none');
    });
    ul_array.length = 0;
});

$(document).on('click', function(e){
    if($(e.target).parent().hasClass('dropdown-menu') == false) {
        ul_array.forEach(element => {
            element.css('display', 'none');
        });
        ul_array.length = 0;
    }
});


$('#amount, #base_amount, #tax_amount').keydown(function (e) {
    // Allow: backspace, delete, tab, escape, enter and .
    if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 189, 190]) !== -1 ||
            // Allow: Ctrl+A, Command+A
            (e.keyCode === 65 && (e.ctrlKey === true || e.metaKey === true)) ||
            // Allow: home, end, left, right, down, up
            (e.keyCode >= 35 && e.keyCode <= 40)) {
        // let it happen, don't do anything
        return;
    }
    // Ensure that it is a number and stop the keypress
    if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
    }
});


function showBusy() {
    $('#loading').show();
}

function filter_special_char(text_str) {
    try{
        if (text_str) {
            text_str = text_str.replace(/&#39;/g, "'");
            text_str = text_str.replace(/&amp;/g, "&");
            text_str = text_str.replace(/&quot;/g, '"');
            text_str = text_str.replace(/&lt;/g, "<");
            text_str = text_str.replace(/&gt;/g, ">");
        }
    } catch(e) {
        console.log(e);
    }

    return text_str;
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

    return JSON.stringify(array_list);
}

$(document).on("input", ".default-date-picker", function() {
    let temp_str = this.value.replace(/[^0-9\-]/g,''); 
    this.value = temp_str;

});

$(document).on("input", ".month-date-picker", function() {
    let temp_str = this.value.replace(/[^0-9\-]/g,''); 
    this.value = temp_str;

});

function selectTableRow(selector, radio_column) {
    $(selector+' tbody tr').bind('click', function () {
        var radio_td = $(this).find('td').eq(radio_column);
        var radio = $(radio_td).find('input').eq(0);
        $(radio).prop("checked", true);

        $("input[type='radio']:not(:checked)").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
        $("input[type='radio']:checked").each(function () {
            $(this).closest('tr').css('background-color', '#3ff3f3');
        });
    });
}

$(document).on('keyup', '.select2-selection.select2-selection--single', function (e) {
    var keycode = (e.keyCode ? e.keyCode : e.which);
    if(keycode == '9'){
        $(this).closest(".select2-container").siblings('select:enabled').select2('open');
    }
});

function checkTransaction() {
    var account = $("#id_account_code").val();
    var amount = $("#amount").val();
    var base_amount = $("#base_amount").val();
    var tax_amount = $("#tax_amount").val();
    var tax = $('#id_tax').val();
    var taxIncluded = $('#tax-checkbox:checkbox:checked').length;
    var taxOnly = $('#tax-only-checkbox:checkbox:checked').length;
    var taxman = $('#manual-tax:checkbox:checked').length;

    if (!account) {
        return "Please select account code";
    }
    if (!taxman && (!amount || parseFloat(amount) == 0)) {
        return "Please enter amount";
    }
    
    if (tax && parseFloat(amount) > 0) {
        var rate = parseFloat($('#id_tax option:selected').attr('data-rate'));
        if (taxOnly == 0 && taxIncluded == 0) {
            if (!taxman && amount != base_amount) {
                return "Amount and Tax Base are not equal";
            }
        }
        if (taxIncluded != 0) {
            if (amount == base_amount) {
                return "Amount and Tax Base must not equal";
            }
        }
        if (taxOnly != 0) {
            if (amount != tax_amount) {
                return "Amount and Tax amount must be equal";
            }
        }
        if (rate > 0) {
            if (parseFloat(amount) >= 1 && (!tax_amount || parseFloat(tax_amount) == 0)) {
                return "Please enter tax amount";
            }
        } else {
            if (taxOnly == 0 && parseFloat(tax_amount) > 0) {
                return "Tax amount should be zero.";
            }
        }
        
    } else {
        if (!taxOnly && parseFloat(tax_amount) > 0) {
            return "Tax amount should be zero.";
        }
    }
    return "success";
}

function get_tax_reporting_rate(currency_id, document_date) {
    $.ajax({
        method: "GET",
        url: '/currencies/tax_reporting_exch_rate/' + currency_id + '/' + document_date + '/',
        dataType: 'JSON',
        success: function (data) {
            tax_reporting_rate = data.exchange_rate;
            $('#id_tax_exchange_rate').val(data.exchange_rate.toFixed(10));
            var tax_report_amount = float_format($('#id_tax_amount').val()) * tax_reporting_rate;
            $('#id_tax_report_amount').val(comma_format(tax_report_amount));
        }
    });
}

$('#id_tax_exchange_rate').on('change', function(){
    tax_reporting_rate = float_format($(this).val());
    console.log('tax_reporting_rate', tax_reporting_rate);
    var tax_report_amount = float_format($('#id_tax_amount').val()) * tax_reporting_rate;
    $('#id_tax_report_amount').val(comma_format(tax_report_amount));
})

$('#tax-exchange-table').on( 'draw.dt', function () {
    selectTableRow('#tax-exchange-table', 5);
    $("input[type='radio']").each(function () {
        $(this).closest('tr').css('background-color', '#f9f9f9');
    });
});

/* Search Enxchange Rate */
$('#btnSearchTaxExchangeRate').on('click', function () {
    $('#tax-exchange-table').DataTable().destroy();
    $('#tax-exchange-table').dataTable({
        "iDisplayLength": 10,
        // "bLengthChange": false,
        scrollY: '50vh',
        scrollCollapse: true,
        "order": [[2, "desc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/exchange_rate_list/",
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.currency_id = $('#id_currency').val();
                d.tax = 1;
            }
        },
        "columns": [
            {"data": "from_currency", "sClass": "text-left"},
            {"data": "to_currency", "sClass": "text-left"},
            {"data": "exchange_date", "sClass": "text-left"},
            {"data": "rate", "sClass": "text-left"},
            {"data": "id", "sClass": "text-left hide_column"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    return '<input type="radio" name="exchange-choices" id="' +
                        full.id + '" class="call-checkbox" value="' + meta.row + '">';
                }
            }
        ]
    });

    setTimeout(() => {
        $('#tax-exchange-table').DataTable().columns.adjust();
    }, 300);
});

function changeTaxExchangeRate() {
    var row = $("input[name='exchange-choices']:checked").val();
    if (row) {
        table = $('#tax-exchange-table').DataTable();
        id_exchange = table.cell(row, $("#exc-id").index()).data();
        rate = table.cell(row, $("#exc-rate").index()).data();

        // $("#id_exchange_rate_fk").val(id_exchange);
        $("#id_tax_exchange_rate").val(rate);
        tax_reporting_rate = parseFloat(rate);
        var tax_report_amount = float_format($('#id_tax_amount').val()) * tax_reporting_rate;
        $('#id_tax_report_amount').val(comma_format(tax_report_amount));

        setTimeout(() => {
            var exch_date = table.cell(row, $("#exc-date").index()).data();
            var year_perd = $('#doc_date_view').val();
            if (exch_date && year_perd) {
                if (exch_date.split('-')[1] != year_perd.split('-')[1]) {
                    pop_ok_dialog("Warning",
                        "This Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                        function () { });
                } else if (exch_date.split('-')[2] != year_perd.split('-')[2]) {
                    pop_ok_dialog("Warning",
                        "This Exchange Rate is not from current period. It is from (" + exch_date + ") .",
                        function () { });
                }
            }
        }, 300);

        $("#TaxExchangeRateListModal").modal("hide");
    }
    else {
        $("#account_error").text("Please choose 1 rate");
    }
}

$(document).on("input", ".numeric_rate", function() {
    let price_str = this.value.replace(/[^0-9\.]/g,'');
    if (price_str.split(".").length-1 > 1) {
        price_str = price_str.slice(0, -1);
    }
    if (price_str.split(".").length > 1) {
        let price_str_2 = price_str.split(".")[1];
        if (price_str_2.length > 10) {
            this.value = price_str.split(".")[0] + '.' + price_str_2.slice(0, -1)
        } else {
            this.value = price_str;
        }
    } else {
        this.value = price_str;
    }
});

$(document).on("input", ".numeric_amount", function() {
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