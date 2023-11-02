
// Highlight enpty field on clicking save button
let check_if_empty = function(button_id) {
  $(button_id).on('click', function() {
    $('.panel input, .panel select, .panel .select2-selection').each(function(index) {
      if($(this).is("[required='required']") && !$(this).val()) {
        $(this).attr('style', 'border: 1px solid darkred')
      } else {
        $(this).attr('style', 'border: atuo')
      }
    });
  })
}

// Centering element
$('.center').children().removeClass('text-right').addClass('text-center');

// th tag not tabbable
$.each($('th'), function() {
  $(this).removeAttr('tabindex');
})

// Center all modal
$('.modal-dialog').attr('style', 'margin: auto');

function validateDate(selectDate, nextDate) {
  $(selectDate).on('keyup', function(event) {
    if (event.which != 13) {
      adjust_input_date(this);
      date = $(this).val();
      } else {
       if (date && moment(date, "DD-MM-YYYY", true).isValid()) {
         $(this).val(date);
         if(nextDate) {
           $(nextDate).datepicker('setDate', date);
           $(nextDate).select();
         }
       } else {
           $(this).datepicker('setDate', new Date());
           if(nextDate) {
             $(nextDate).datepicker('setDate', date);
             $(nextDate).select();
           }
       }
       if(nextDate) {
         $(nextDate).select();
       }
     }
  });

  // blur
  $(selectDate).on('blur', function() {
    let date = $(this);
    setTimeout(function() {
      if (date.val() && moment(date.val(), "DD-MM-YYYY", true).isValid()) {
        if(nextDate) {
          $(nextDate).datepicker('setDate', date.val());
          $(nextDate).select();
        }
        return;
      } else {
        $(this).datepicker('setDate', new Date());
        if(nextDate) {
          $(nextDate).datepicker('setDate', date.val());
          $(nextDate).select();
        }
      }
    }, 1)
  });
}


$('#batch_view_date').bind('keydown', function (event) {
  if (event.which == 13) {
      date_key_down(this);
      return false;
  }
});
$('#doc_date_view').bind('keydown', function (event) {
  if (event.which == 13) {
      date_key_down(this);
      return false;
  }
});
$('#post_date_view').bind('keydown', function (event) {
  if (event.which == 13) {
      post_date_enter = $(this).val();
      if (post_date_enter.length > 0){
          $(this).datepicker('setDate', post_date_enter);
          post_date_click = '';
      }
      $('#id_supplier').focus();
      return false;
  }
});
$('#batch_view_date').on('change', function() {
  var dt = $(this).val();
  if (dt && moment(dt, "DD-MM-YYYY", true).isValid()) {
      var goodday = takeday($("#batch_view_date").val());
      $("#id_batch_date").val(goodday);
      if (!journal_id || journal_id == '0') {
          $("#doc_date_view").datepicker('setDate', $("#batch_view_date").val()).trigger('change');
      }
  }else{
      var date_view = dateView($("#id_batch_date").val());
      $("#batch_view_date").datepicker('setDate', date_view);
  }

});
$('#doc_date_view').on('change', function() {
   var dt = $(this).val();
   if (dt && moment(dt, "DD-MM-YYYY", true).isValid()){
       if($("#doc_date_view").val() != $('#post_date_view').val()) {
           var goodday = takeday($("#doc_date_view").val());
           $("#id_document_date").val(goodday);
           $("#id_posting_date").val(goodday);
           $("#post_date_view").datepicker('setDate', $("#doc_date_view").val());
           //$('#post_date_view').trigger('change');
           //$('#post_date_view').select();
           try{
            update_exch_rate();
           } catch (e) {

           }
       }
   }else{
       var date_view = dateView($("#id_document_date").val());
       $("#doc_date_view").datepicker('setDate', date_view);
       $("#post_date_view").datepicker('setDate', $("#doc_date_view").val());
   }
   setTimeout(() => {
     checkPostingDate($("#doc_date_view").val());
   }, 100);
});
// $('#post_date_view').on('click', function() {
//   post_date = $('#post_date_view').val();
//   $("#post_date_view").datepicker('setDate', post_date);
// });
$('#post_date_view').on('change', function() {
  var dt = $(this).val();
  if (dt && moment(dt, "DD-MM-YYYY", true).isValid()) {
      if (post_date_enter != '') {
          if (jrn_status = '2') {
              // checkPostingDate(post_date_enter);
          }
          post_date_enter = '';
      }else if(post_date_enter == '') {
          post_date_click = $('#post_date_view').val();
          if (jrn_status != '2') {
              // checkPostingDate(post_date_click);
          }
      }
  } else {
      var date_view = dateView($("#id_posting_date").val());
      $("#post_date_view").datepicker('setDate', date_view);
  }
});

function checkPostingDate(post_date) {
  $.ajax({
      type: "GET",
      url: "/accounting/check_fiscal_calendar/" + post_date + "/",
      success: function (data) {
          fiscal_start_date = data.fiscal_start_date;
          fiscal_end_date = data.fiscal_end_date;
          fiscal_year = data.fiscal_year;
          fiscal_month = data.fiscal_month;
          current_month = data.current_month;
          current_year = data.current_year;
          if (fiscal_start_date == '' && fiscal_end_date == '') {
              pop_ok_dialog("Invalid Document Date",
                  "Document Date (" + post_date + ") must be in between valid fiscal period.",
                  function () { $("#doc_date_view").datepicker('setDate', moment().format("DD-MM-YYYY")); });
          } else {
              var goodday = takeday(post_date);
              $("#id_document_date").val(goodday);
          }
          $('#perd_year').val(data.fiscal_year);
          $('#perd_month').val(data.fiscal_month);
          $('#year_period').val(data.fiscal_month + "-" + data.fiscal_year);

          batch_date = ($('#batch_view_date').val()).split('-');
          doc_date = ($("#doc_date_view").val()).split('-');
          if (batch_date[1] != doc_date[1] || batch_date[2] != doc_date[2]) {
            $("#doc_date_view").datepicker('setDate', $('#batch_view_date').val());
            // pop_ok_dialog("Invalid Document Date",
            //       "Document Date does not match with batch date.",
            //       function () { $("#doc_date_view").datepicker('setDate', $('#batch_view_date').val()) });
          }
      }
  });
}
