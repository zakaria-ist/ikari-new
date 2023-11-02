function leftPad(number, targetLength) {
    var output = number + '';
    while (output.length < targetLength) {
        output = '0' + output;
    }
    return output;
}

$('input[name=batch_type_options]').on('change', function() {
    $("#start_batch").val('000001');
    $("#end_batch").val('999999');
});

$('input[name=post_options]').on('change', function() {
    var selected_post_option = $('input[name=post_options]:checked').val();
    if (selected_post_option=='1'){
        $('#batch_selection').addClass('hide');
    } else {
        $('#batch_selection').removeClass('hide');
    }
});

$('#btnFindFirstBatch').on('click', function () {
    batch_range_type=1;
    load_batch_list();
});

$('#btnFindLastBatch').on('click', function () {
    batch_range_type=2;
    load_batch_list();
});

$("#start_batch").focus(function() { 
    var save_this = $(this);
    window.setTimeout (function(){ 
       save_this.select(); 
    },5);
});

$("#end_batch").focus(function() { 
    var save_this = $(this);
    window.setTimeout (function(){ 
       save_this.select(); 
    },5);
});

$('#start_batch').focusout(function() {
    var batch_no = $('#start_batch').val();
    if (batch_no!='000001'){
        var selected_batch_type = parseInt($('input[name=batch_type_options]:checked').val());
        if (!selected_batch_type){
            selected_batch_type = 5;
        }
        batch_range_type=1;
        var batch_no_extended = leftPad(batch_no,6);
        $('#start_batch').val(batch_no_extended);

        if (!isNumber(batch_no)){
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Invalid Input.');
            $('#notificationModal_text2').text('Batch '+batch_no_extended+' does not exist');
            $("#notificationModal").modal("show");
        } else {
            batch_no = parseInt(batch_no,10);
            var batch_exist = false;
            for (var i = 0; i < unpostd_batch.length; i++) {
                if ((unpostd_batch[i].batch_no==batch_no)&&(unpostd_batch[i].batch_type==selected_batch_type)){
                    batch_exist = true;
                    $('#start_batch').data('batch_id',unpostd_batch[i].id);
                    break;
                }
            }
            if (!batch_exist){
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Invalid Input.');
                $('#notificationModal_text2').text('Batch '+batch_no_extended+' does not exist');
                $("#notificationModal").modal("show");
            }
        }
    }
});

$('#end_batch').focusout(function() {
    var batch_no = $('#end_batch').val();
    if (batch_no!='999999'){
        var selected_batch_type = parseInt($('input[name=batch_type_options]:checked').val());
        if (!selected_batch_type){
            selected_batch_type = 5;
        }
        batch_range_type=2;
        var batch_no_extended = leftPad(batch_no,6);
        $('#end_batch').val(batch_no_extended);

        if (!isNumber(batch_no)){
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('Invalid Input.');
            $('#notificationModal_text2').text('Batch '+batch_no_extended+' does not exist');
            $("#notificationModal").modal("show");
        } else {
            batch_no = parseInt(batch_no,10);
            var batch_exist = false;
            for (var i = 0; i < unpostd_batch.length; i++) {
                if ((unpostd_batch[i].batch_no==batch_no)&&(unpostd_batch[i].batch_type==selected_batch_type)){
                    batch_exist = true;
                    $('#end_batch').data('batch_id',unpostd_batch[i].id);
                    break;
                }
            }
            if (!batch_exist){
                $('#notificationModal_title').text('Error');
                $('#notificationModal_text1').text('Invalid Input.');
                $('#notificationModal_text2').text('Batch '+batch_no_extended+' does not exist');
                $("#notificationModal").modal("show");
            }
        }
    }
});

$('#notification_ok').focusout(function() {
    reset_batches_range(batch_range_type);
});

function reset_batches_range(batch_range_type){
    if (batch_range_type==1){
        $('#start_batch').data('batch_id','0');
        $('#start_batch').val('000001');
    } else {
        $('#end_batch').data('batch_id','0');
        $('#end_batch').val('999999');
    }
}

function isNumber(p){
    if (typeof p == 'number'){
        result = true;
    } else if (!isNaN(p)) {
        result = true;
    } else {
        result = false;
    }
    return result;
}

function load_batch_list(){
    var selected_batch_type = parseInt($('input[name=batch_type_options]:checked').val());
    if (!selected_batch_type){
        selected_batch_type = 5;
    }

    $('#batch_list_table').DataTable().destroy();
    $('#batch_list_table').dataTable({
        "iDisplayLength": 5,
        "aLengthMenu": [[5, 10, 15, -1], [5, 10, 15, "All"]],
        "order": [[0, "asc"]],
        "serverSide": true,
        "ajax": {
            "type": "POST",
            "url": "/accounting/UnpostedBatch__asJson/",
            "data": function (d) {
                d.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
                d.batch_type = selected_batch_type;
                d.source_ledger = source_ledger;
                d.is_post_batches = true;
            }
        },
        "columns": [
            {
                "data": null,
                "render": function (data, type, full, meta) {
                    return leftPad(full['batch_num'],6);
                }
            },
            {"data": "batch_desc"},
            {"data": "input_type"},
            {"data": "status"},
            {"data": "source_ledger"},
            {"data": "batch_amount"},
            {
                "orderable": false,
                "data": null,
                "sClass": "hide_column",
                "render": function (data, type, full, meta) {
                    var button_radio = '<input type="radio" name="choices" id="'+full['id']+'" data-batch_desc="'+full['batch_desc']+'" class="call-radio" value="'+full['batch_num']+'">'
                    return button_radio;
                }
            },
        ],
        "columnDefs": [
            { className: "text-left", targets: [ 0,1,2,3 ] },
            { className: "text-right", targets: [ 5 ] }
        ]
    });

    $('#batch_list_table').on('draw.dt', function () {
        selectTableRow('#batch_list_table', 6);
        $("input[type='radio']").each(function () {
            $(this).closest('tr').css('background-color', '#f9f9f9');
        });
    });
}

function setParameter(){
    var selected_batch_type = parseInt($('input[name=batch_type_options]:checked').val());
    if (!selected_batch_type){
        selected_batch_type = 5;
    }
    var selected_post_option = $('input[name=post_options]:checked').val();
    var start_batch = $('#start_batch').data('batch_id');
    var end_batch = $('#end_batch').data('batch_id');
    $('#selected_batch_type').val(selected_batch_type);
    $('#selected_post_option').val(selected_post_option);
    $('#first_batch').val(start_batch);
    $('#last_batch').val(end_batch);
}

function confirm_post_batches() {
    $("#comfirmPostingModal").modal("show");
    $("#comfirm-yes").attr("onclick", "try_to_post()");
}

var counter = 0;
var post_result = {"success":0,"fail":0};
var bar_width = 0;
function try_to_post() {
    $("#comfirmPostingModal").modal("hide");
    $('#loading').show();
    setParameter();
    $.ajax({
        url: '/accounting/get_batches/'+ source_ledger +'/',
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'selected_batch_type': $("#selected_batch_type").val(),
            'selected_post_option': $("#selected_post_option").val(),
            'first_batch': $("#first_batch").val(),
            'last_batch': $("#last_batch").val()
        }
    })
    .done(function(data) {
        if (data.length<=0){
            $('#notificationModal_title').text('Error');
            $('#notificationModal_text1').text('No record to process !');
            $('#notificationModal_text2').text('All batch within your selected batch range are already posted');
            $("#notificationModal").modal("show");
            $('#loading').hide();
        } else {
            $('#btnProcess').prop('disabled', true);
            $("#div_progressbar").show();
            post_batch(data[0].batches);
        }
    })
    .fail(function(e) {
        $('#notificationModal_title').text('Error');
        $('#notificationModal_text1').text('Failed to get batch !');
        $('#notificationModal_text2').text('Please refresh and try again or contact administrator for support.');
        $("#notificationModal").modal("show");
        $('#loading').hide();
    })
}

function post_batch(btch){
    var target_percentage = 100;
    var bar_growth = btch.length>0 ? target_percentage/btch.length: target_percentage;
    var btch_id = null;
    btch_id = btch[counter];
    $.ajax({
        url: '/accounting/post_batch/'+ btch_id +'/',
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        }
    })
    .done(function(data) {
        if ((data)||(data=='true')){ post_result['success']++; } 
        else { post_result['fail']++; }
    })
    .fail(function(e) {
        post_result['fail']++;
    })
    .always(function(e){
        counter++;
        bar_width = Math.ceil(bar_width+bar_growth)>target_percentage? target_percentage : Math.ceil(bar_width+bar_growth);
        $("#progress_status").text('Processing ... ( '+bar_width+'% )');
        $("#myBar").css("width", bar_width+"%");
        if (bar_width >= target_percentage) {
            $("#progress_status").text('Processing ... ( '+bar_width+'% )');
            $("#myBar").css("width", bar_width+"%");
            setTimeout(function(){
                $('#loading').hide();
                $("#div_progressbar").hide(1000);
                $("#progress_status").text('Processing ... ( 0% )');
                $("#myBar").css("width", "0%");
                $("#btnProcess").prop('disabled', false);
                if (counter>=btch.length){
                    $("#post_state").val(JSON.stringify(post_result));
                    $("#frm_post_batches").submit();
                }
            }, 500);
        }
        if (counter < btch.length) {
            post_batch(btch);
        }
    });
}
