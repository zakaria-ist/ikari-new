var Script = function () {


    //checkbox and radio btn

    var d = document;
    var safari = (navigator.userAgent.toLowerCase().indexOf('safari') != -1) ? true : false;
    var gebtn = function (parEl, child) {
        return parEl.getElementsByTagName(child);
    };
    onload = function () {

        var body = gebtn(d, 'body')[0];
        body.className = body.className && body.className != '' ? body.className + ' has-js' : 'has-js';

        if (!d.getElementById || !d.createTextNode) return;
        var ls = gebtn(d, 'label');
        for (var i = 0; i < ls.length; i++) {
            var l = ls[i];
            if (l.className.indexOf('label_') == -1) continue;
            var inp = gebtn(l, 'input')[0];
            if (l.className == 'label_check') {
                l.className = (safari && inp.checked == true || inp.checked) ? 'label_check c_on' : 'label_check c_off';
                l.onclick = check_it;
            }
            ;
            if (l.className == 'label_radio') {
                l.className = (safari && inp.checked == true || inp.checked) ? 'label_radio r_on' : 'label_radio r_off';
                l.onclick = turn_radio;
            }
            ;
        }
        ;
    };
    var check_it = function () {
        var inp = gebtn(this, 'input')[0];
        if (this.className == 'label_check c_off' || (!safari && inp.checked)) {
            this.className = 'label_check c_on';
            if (safari) inp.click();
        } else {
            this.className = 'label_check c_off';
            if (safari) inp.click();
        }
        ;
    };
    var turn_radio = function () {
        var inp = gebtn(this, 'input')[0];
        if (this.className == 'label_radio r_off' || inp.checked) {
            var ls = gebtn(this.parentNode, 'label');
            for (var i = 0; i < ls.length; i++) {
                var l = ls[i];
                if (l.className.indexOf('label_radio') == -1)  continue;
                l.className = 'label_radio r_off';
            }
            ;
            this.className = 'label_radio r_on';
            if (safari) inp.click();
        } else {
            this.className = 'label_radio r_off';
            if (safari) inp.click();
        }
        ;
    };

}();


var url = window.location.pathname;
var confirmIsOk = false;
var title = '';
var codes = null;
var add = false;

$(document).ready(function() {
    if(url.search('edit') != '-1') $('input[id=id_code], input[id=code]').attr('readonly', 'true');
    
    title = document.title.toLowerCase();
    title = title.replace('add', '');
    add = url.search('add') != '-1' ? true : false;

    if(add)
        loadCodes(title);
});

function loadCodes(strTitle) {

    $.ajax({
        url: '/search/code/',
        type: 'get',
        dataType: 'json',
        data: {search : strTitle},
    })
    .done(function(e) {
        if(e.status == 200) {
            codes = e.object;
        }
            
        if(e.status == 300)
            console.log(e.message);
    })
    .fail(function(e) {
        console.log(e.responseText)    
    });   
}

var lenOldVal = '';
$('#id_code, #code').focusout(function(event) {
    if(title == 'part sale price' || title == 'purchase item ') {
        event.preventDefault();
        if(add && codes != null) {
            checkItemExist($(this));        
        }
    }
});

$('.item_code_search, #form_customer_code, #form_supplier_code, #txtFilter, #id_code, #txtPartNo, #txtPONo, #txtDONo, #txtSONo, #txtGRNo, #id_transaction_code, #id_in_location, #id_out_location, #code').on('change paste keyup', function () {
    try{
        var i = $(this);
        var id = i.attr('id');
        if (lenOldVal != i.val().length) $(this).val(function () {
            return this.value.toUpperCase()
        });
        lenOldVal = i.val().length;
        if(add && (id == 'id_code' || id == 'code') && lenOldVal > 0 && codes != null) {
            if(title != 'part sale price' && title != 'purchase item ')
                checkTypedCode($(this));
        }
    } catch (e){
    }
});

function checkTypedCode(elm) {
    for (var i = codes.data.length - 1; i >= 0; i--) {
        if(codes.data[i].code != null && (codes.data[i].code.length == elm.val().length) && (codes.data[i].code.toUpperCase() == elm.val())) {
            if(!$('#codewarning').length) {
                elm.closest('div').append('<span id="codewarning" class="help-inline text-warning">code already exist !</span>');
            }
            $('#codewarning').show();
            $('button[type=submit]').attr('disabled', 'true');
            i = -1;
        } else {
            if($('#codewarning').is(':visible')) {
                $('#codewarning').hide();
                $('button[type=submit]').removeAttr('disabled');
            }
        }
    }
}

function checkItemExist(elm) {
    if(codes.use_inventory) {
        for (var i = codes.data.length - 1; i >= 0; i--) {
            if(codes.data[i].code != null && (codes.data[i].code.length == elm.val().length) && (codes.data[i].code.toUpperCase() == elm.val())) {
                if(!$('#codewarning').length) {
                    elm.closest('div').append('<span id="codewarning" class="help-inline text-success">code ok <i class="fa fa-check"></i></span>');
                } else {
                    $('#codewarning').attr('class', 'help-inline text-success').html('code ok <i class="fa fa-check"></i></span>');
                }
                if(!$('#codewarning').is(':visible')) {
                    $('#codewarning').show();
                }
                $('button[type=submit]').removeAttr('disabled');

                i = -1;
            } else {
                if($('#codewarning').is(':visible')) {
                    $('button[type=submit]').attr({'disabled' : 'true' });
                    $('#codewarning').attr({'class' : 'help-inline text-warning'}).html("code doesn't exist !");
                } else {
                    if(!$('#codewarning').length) {
                        elm.closest('div').append('<span id="codewarning" class="help-inline text-success">code ok <i class="fa fa-check"></i></span>');
                    } else {
                        $('#codewarning').attr('class', 'help-inline text-success').html('code ok <i class="fa fa-check"></i></span>');
                    } 
                    
                    if(!$('#codewarning').is(':visible')) {
                        $('#codewarning').show();
                    }
                    $('button[type=submit]').removeAttr('disabled');  
                }
            }
        }

    }
    
}

$('body').on('keydown', 'input, select, textarea', function (e) {
    var elm = $(this), form = elm.parents('form:eq(0)'), targetFocusElm, nextELm, result=true;
    if (e.keyCode == 13) {

        try {
            if ($("#dialog-ok-modal").dialog("isOpen")) {
                setTimeout(function () {}, 300);
                return false;
            }
        } catch (error) {
            // console.log(error);
        }
        try {
            if ($("#dialog-yes-no-modal").dialog("isOpen")) {
                setTimeout(function () {}, 300);
                return false;
            }
        } catch (error) {
            // console.log(error);
        }

        var v = this.value;
        if ($(this)[0].nodeName == 'TEXTAREA') {
            var curPos = getCaret(this);
            var newStr = v.substring(0, curPos) + "\n" + v.substring(curPos, v.length);
            this.value = newStr;
            e.preventDefault();

            return false;
        }

        var targetFocusElm = form.find('input, textarea').filter(':focusable');
        // var targetFocusSelecElm = form.find('select').filter(':focusable');
        // var nextElm = targetFocusSelecElm.eq(targetFocusSelecElm.index(this) + 1);
        var currentElm = targetFocusElm.eq(targetFocusElm.index(this));
        // if (nextElm.length){
        //     nextElm.focus();
        //     nextElm.select();
        // } else
        if (currentElm.length){
            currentElm.select();
        }
        return false;
    }

});


$('body').on('keydown', function (e) {
    if (e.keyCode == 13) {
        try {
            if ($("#dialog-ok-modal").dialog("isOpen")) {
                setTimeout(function() { }, 300);
                return false;
            }
        } catch(error){
            // console.log(error);
        }
        try {
            if ($("#dialog-yes-no-modal").dialog("isOpen")) {
                setTimeout(function() { }, 300);
                return false;
            }
        } catch(error){
            // console.log(error);
        }
    }
});



function getCaret(el) {
    if (el.selectionStart) {
        return el.selectionStart;
    } else if (document.selection) {
        el.focus();
        var r = document.selection.createRange();
        if (r == null) {
            return 0;
        }
        var re = el.createTextRange(), rc = re.duplicate();
        re.moveToBookmark(r.getBookmark());
        rc.setEndPoint('EndToStart', re);
        return rc.text.length;
    }
    return 0;
}
