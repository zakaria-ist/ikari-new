
$("#id_batch_number_from").on('change', function() {
    triggerEntryNumber();
});

$("#id_batch_number_to").on('change', function() {
    triggerEntryNumber();
});

function triggerEntryNumber() {
    let from_batch = $("#id_batch_number_from").val();
    let to_batch = $("#id_batch_number_to").val();
    let batch_type = $('#batch_type_modal').val();

    if (from_batch == to_batch) {
        $.ajax({
            type: "GET",
            url: "/accounting/get_batch_entries/" + batch_type + "/" + to_batch + "/",
            success: function (data) {
                if (data.data.length) {
                    $('#entry_range_div').css('display', 'block');
                    if ($('#id_entry_number_from').data('select2')) {
                        $('#id_entry_number_from').select2('destroy');
                    }
                    $('#id_entry_number_from').empty();
                    var options = '<option value="">Select Entry</option>';
                    $.each(data.data, function(indx, item) {
                        options += "<option value="+item[0]+">"+item[1]+"</option>";
                    });
                    $('#id_entry_number_from').append(options);
                    $('#id_entry_number_from').select2({
                        placeholder: "Select Entry",
                        allowClear: true
                    });

                    if ($('#id_entry_number_to').data('select2')) {
                        $('#id_entry_number_to').select2('destroy');
                    }
                    $('#id_entry_number_to').empty();
                    options = '<option value="">Select Entry</option>';
                    $.each(data.data, function(indx, item) {
                        options += "<option value="+item[0]+">"+item[1]+"</option>";
                    });
                    $('#id_entry_number_to').append(options);
                    $('#id_entry_number_to').select2({
                        placeholder: "Select Entry",
                        allowClear: true
                    });
                } else {
                    $('#entry_range_div').css('display', 'none');
                }
            }
        });
    } else {
        $('#entry_range_div').css('display', 'none');
    }
}

function printFromBatchInfo(batch_type, batch_id, batch_no) {
    if (batch_type == 5) {
        var size = batch_no.length
        var s = batch_no+"";
        while (s.length < size) s = "0" + s;

        var o_from = new Option(s, batch_id);
        $(o_from).html(s);
        $("#id_batch_number_from").append(o_from);

        var o_to = new Option(s, batch_id);
        $(o_to).html(s);
        $("#id_batch_number_to").append(o_to);

        showModalPrintBatch(batch_type);
    } else {
        loadIframe(batch_type, batch_id, 0, 0);
    }
}

function download(dataurl) {
    var link = document.createElement('a');
    link.href = dataurl;
    link.download = '';
    $('#loading').show();
    $(link).load(dataurl, function( response, status, xhr ) {
      var filename = "";
      var disposition = xhr.getResponseHeader('Content-Disposition');
      if (disposition && disposition.indexOf('filename') !== -1) {
          var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          var matches = filenameRegex.exec(disposition);
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
          }
      }

      // The actual download
      var blob = new Blob([response], { type: 'application/pdf' });
      var link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      $('#loading').hide();
      // $("#PrintOutModalLoading").modal("hide");
    });

    //link.dispatchEvent(new MouseEvent('click'));
}

function loadIframe(batch_type= 0, batchFrom=0, batchTo=0, currency=0, entryFrom=0, entryTo=0) {
    var url = '/reports/print_BatchNumber/' + batch_type + '/' + batchFrom + '/' + batchTo + '/' + currency + '/' + entryFrom + '/' + entryTo + '/';
    download(url)
    return false;
}

function showModalPrintBatch(batch_type, batch_id=null){
    $("#loadpage").css("display","none");
    var title = batch_type == 1 ? 'A/R Invoice Batch List' : '';
    title = batch_type == 2 ? 'A/P Invoice Batch List' : title;
    title = batch_type == 3 ? 'A/R Receipt Batch List' : title;
    title = batch_type == 4 ? 'A/P Payment Batch List' : title;
    title = batch_type == 5 ? 'G/L Batch List' : title;

    $('#title_name').text(title);
    $('#batch_type_modal').val(batch_type);
    if (batch_id) {
        $("#id_batch_number_from").val(batch_id).trigger('change');
        $("#id_batch_number_to").val(batch_id).trigger('change');
    } else {
        $("#id_batch_number_from").trigger('change');
        $("#id_batch_number_to").trigger('change');
    }
    if (batch_type != 5) {
        $('#id_currency_report').attr('disabled', true);
        $('#div_currency').hide();
    } else {
        $('#id_currency_report').attr('disabled', false);
        $('#div_currency').show();
    }
    $("#PrintOutModal").modal("show");
}

$(document).ready(function () {
    $('#print_batch_number').on('click', function () {
        var batchFrom = $('#id_batch_number_from').val();
        var batchTo = $('#id_batch_number_to').val();
        var currency = $('#id_currency_report').val();
        var entryFrom = 0;
        var entryTo = 0;
        if(batchFrom == 0 ||  batchFrom == null) {
            alert('Please select batch number');
            return false;
        }
        if (parseInt(batchTo) < parseInt(batchFrom) && parseInt(batchTo) > 0) {
            alert('Please select batch number [To] greater than [From]');
            return false;
        }
        if ( batchTo == null || parseInt(batchTo) == 0) {
            batchTo = -1;
        }

        if (parseInt(batchTo) == parseInt(batchFrom)) {
            batchTo = 0;
            entryFrom = ($('#id_entry_number_from').val() != '') ? $('#id_entry_number_from').val() : 0;
            entryTo = ($('#id_entry_number_to').val() != '') ? $('#id_entry_number_to').val() : 0;
        }
        // $("#loadpage").css("display","block");
        $("#PrintOutModal").modal("hide");
        loadIframe($('#batch_type_modal').val(), batchFrom, batchTo, currency, entryFrom, entryTo);
        $("#comfirmDeleteJournalModal").modal("hide");
    });
})
