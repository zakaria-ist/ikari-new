$(document).ready(function () {
    var start_date_click = '';
    var start_date_enter = '';
    $('#start_date').bind('keydown', function (event) {
        if (event.which == 13) {
            start_date_enter = $(this).val();
            console.log(start_date_enter);
            if (start_date_enter.length > 0) {
                console.log(start_date_enter);
                $('#start_date').val(start_date_enter);
                start_date_click = '';
            }
            $('#is_expire').focus();
            return false;
        }
    });
    $('#start_date').on('change', function () {
        if (start_date_enter != '') {
            $(this).val(start_date_enter);
        } else if (start_date_enter == '') {
            start_date_click = $(this).val();
            $(this).val(start_date_click);
        }
    });
    var expire_date_click = '';
    var expire_date_enter = '';
    $('#expire_date').bind('keydown', function (event) {
        if (event.which == 13) {
            expire_date_enter = $(this).val();
            if (expire_date_enter.length > 0) {
                $(this).val(expire_date_enter);
                expire_date_click = '';
            }
            $('#run_date').select();
            return false;
        }
    });
    $('#expire_date').on('change', function () {
        if (expire_date_enter != '') {
            $(this).val(expire_date_enter);
        } else if (expire_date_enter == '') {
            expire_date_click = $(this).val();
            $(this).val(expire_date_click);
        }
    });

    $('#is_expire').on('change', function (e) {
        if ($('#is_expire').is(":checked")) {
            $('#expire_date_div').show();
        } else {
            $('#expire_date_div').hide();
        }
    });

    $('#id_schedule_code').on('focus', function(e) {
        $('#btnSearchSchedule').trigger('click');
    });

    $('#btnScheduleSelect').on('click', function (e) {
        $(':submit').removeAttr('disabled');
        var sche_table = $('#schedule-code-table').DataTable();
        schedule_id = $('[name=schedule_chice]:checked').val();
        console.log(schedule_id);
        schedule_list.forEach(element => {
            if (element.id == schedule_id) {
                $('#id_schedule_code').val(element.code);
                $('#id_schedule_desc').val(element.desc);
                $('#schedule_id').val(element.id);
            }
        });
        sche_table.search('').draw();
    });

    if ($('#is_expire').is(":checked")) {
        $('#expire_date_div').show();
    } else {
        $('#expire_date_div').hide();
    }

    s_date = $('#start_date').val().split('-');
    if (s_date[0].length > 2) {
        s_date = $('#start_date').val().split('-').reverse().join('-');
        $('#start_date').datepicker("setDate", s_date);
    }
    e_date = $('#expire_date').val().split('-');
    if (e_date[0].length > 2) {
        e_date = $('#expire_date').val().split('-').reverse().join('-');
        $('#expire_date').datepicker("setDate", e_date);
    }
    r_date = $('#run_date').val().split('-');
    if (r_date[0].length > 2) {
        r_date = $('#run_date').val().split('-').reverse().join('-');
        $('#run_date').datepicker("setDate", r_date);
    }
    m_date = $('#maintained_date').val().split('-');
    if (m_date[0].length > 2) {
        m_date = $('#maintained_date').val().split('-').reverse().join('-');
        $('#maintained_date').datepicker("setDate", m_date);
    }

    $('#schedule-code-table').DataTable({
        "iDisplayLength": 5,
        "aLengthMenu": [[5, 10, 15, -1], [5, 10, 15, "All"]]
    });

});