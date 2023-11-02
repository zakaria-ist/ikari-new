$(window).load(function() {
	$('#container').prepend(
        '<div id="confirmDialogClose" class="modal form-dialog" tabindex="-1" role="dialog" style="padding-top:15%">'+
          '<div class="modal-dialog modal-sm" role="document">'+
            '<div class="modal-content">'+
             '<div id="content-dialog" class="panel panel-warning">'+
                '<div id="header-message" class="panel-heading">Closing </div>'+
                '<div class="panel-body">'+
                    '<div class="col-lg-12 question" style="margin-left: -15px; margin-right:-15px"><p id="body-message">Close the Current Year Period ?</p></div>'+
                    '<button data-action="cancel" class="btn btn-default pull-right btnConfirmClose" style="margin-left:5px">CLOSE</button>'+
                    '<button data-action="ok" class="btn btn-primary pull-right btnConfirmClose" style="margin-right:0px">OK</button>'+
                '</div>'+
             '</div>'+
            '</div>'+
          '</div>'+
        '</div>'
    );
});
$(document).ready(function() {
    var fiscal_year;
    var fiscal_period;

	$('a[data-target=closing]').click(function(event) {
		$('div#content-dialog').attr('class', 'panel panel panel-warning');
		$('div#header-message').text('Closing');
		$('p#body-message').html('Close the Current Year Period ?');

		url = $(this).data('url');
		reloadURL = $(this).data('url-target');

		$('#confirmDialogClose').modal('show');

		$('.btnConfirmClose').on('click', function() {
            var act = $(this).data('action');
            if(act == 'ok') {
            	$('.btnConfirmClose').attr('disabled', 'true');
                doTheClosing(url, reloadURL);
            } else {
                $('#confirmDialogClose').modal('hide');
            }
        });
	});
});

function doTheClosing(url, reloadURL) {

	$('p#body-message').html('Loading <i class="fa fa-spinner fa-spin"></i>');
	$.ajax({
		url: url,
		type: 'GET',
		dataType: 'json',
		cache: false
	})
	.done(function(e) {
		$('p#body-message').html(e.messages);
		if(e.status == 200) {
			$('div#content-dialog').attr('class', 'panel panel panel-success');
			$('div#header-message').text('Success');
			window.location.href = reloadURL;
		} else {
			$('div#content-dialog').attr('class', 'panel panel panel-danger');
			$('div#header-message').text('Warning::ERROR');
		}

	})
	.fail(function(e) {
		$('p#body-message').html('ERROR::CODE#128');
		$('div#content-dialog').attr('class', 'panel panel panel-danger');
		$('div#header-message').text('Warning::ERROR');
	})
	.always(function() {
		$('.btnConfirmClose').removeAttr('disabled');
		// $('#confirmDialogClose').modal('hide');
	});

	
}

function inventoryClosing() {
    $.ajax({
        method: "GET",
        url: '/accounting/load_fiscal_period/',
        dataType: 'JSON',
        success: function (json) {
            $('#ic_period').val('Period ' + json.period + ' (' + json.start_date + ' to ' + json.end_date +')');
            $("#ICClosing").modal("show");
            fiscal_year = json.year;
            fiscal_period = json.period;
        }
    });
}

function sales_purchasesClosing() {
    $.ajax({
        method: "GET",
        url: '/accounting/load_fiscal_period/',
        dataType: 'JSON',
        success: function (json) {
            $('#sp_period').val('Period ' + json.period + ' (' + json.start_date + ' to ' + json.end_date +')');
            $("#SPClosing").modal("show");
            fiscal_year = json.year;
            fiscal_period = json.period;
        }
    });
}

$('#btnICClosing').on('click', function() {
    $.ajax({
        method: "POST",
        url: '/accounting/inventory_closing/',
        dataType: 'JSON',
        data: {
            'year' : fiscal_year,
            'period': fiscal_period,
        }
    })
    .always(function() {
        window.location.reload();
    });
})

$('#btnSPClosing').on('click', function() {
    $.ajax({
        method: "POST",
        url: '/accounting/sp_closing/',
        dataType: 'JSON',
        data: {
            'year' : fiscal_year,
            'period': fiscal_period,
        }
    })
    .always(function() {
        window.location.reload();
    });
})

function inventoryClosing_new() {
    var dummy_pid = 'dummy_pid';
    $('#close_type_str').text('Inventory');
    $("#btnSubmitClosing").attr("onclick", "submitInventoryClosing('"+dummy_pid+"')");
    $("#ConfirmClosing").modal("show");
}

function submitInventoryClosing(pid){
    $("#loading").show();
    inputData = $('#year_period').val();
    yp = inputData.split("-");
    var pyear = yp[1];
    var pmonth = yp[0];
    $.ajax({
        method: "POST",
        url: '/accounting/inventory_closing/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val(),
            'fiscal_period_id': pid,
            'years_period': pyear,
            'month_period': pmonth,
        }
    })
    .always(function(e) {
        window.location.reload();
    });
}

function sales_purchasesClosing_new() {
    var pid = $('#period_list').val();
    if (pid!='None'){
        $('#close_type_str').text('Sales & Purchase');
        $("#btnSubmitClosing").attr("onclick", "submitSPClosing("+pid+")");
        $("#ConfirmClosing").modal("show");
    } else {
        submitSPClosing(pid);
    }
}

function submitSPClosing(fiscal_period_id){
    $('#loading').show();
    // var pyear = $('#period_list').select2().find(":selected").data('pyear');
    // var pmonth = $('#period_list').select2().find(":selected").data('pmonth');
    inputData = $('#year_period').val();
    yp = inputData.split("-");
    var pyear = yp[1];
    var pmonth = yp[0];
    $.ajax({
        method: "POST",
        url: '/accounting/sp_closing/',
        dataType: 'JSON',
        data: {
            'fiscal_period_id': fiscal_period_id,
            'year': pyear,
            'month': pmonth
        }
    })
    .always(function() {
        window.location.reload();
    });
}

function end_year_closing() {
    $('#ConfirmationText').text('You are about to do Year End Closing. Continue ?');
    $("#btnSubmitClosing").attr("onclick", "end_year_closing_submit()");
    $("#ConfirmClosing").modal("show");
}

function end_year_closing_submit(){
    $('#loading').show();
    var pyear = $('#period_yr').select2().find(":selected").val();
    $.ajax({
        method: "POST",
        url: '/accounting/closing/',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'year': pyear
        }
    })
    .always(function() {
        window.location.reload();
    });
}
