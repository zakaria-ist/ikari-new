function checkEndDate(i) {
    next = i+1;
    if (moment(end_date, "DD-MM-YYYY", true).isValid()) {
        endDate = new Date(moment(end_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
        endDate.setDate(endDate.getDate()+1);
        if(next < 12) {
            $('#id_form-' + next + '-start_date').val(moment(endDate.toISOString().substring(0, 10), "YYYY-MM-DD").format("DD-MM-YYYY"));
        }
        if (end_date != '') {
            $('#id_form-' + i + '-end_date').val(moment(end_date, "DD-MM-YYYY").format("DD-MM-YYYY"));
        }
    }
}

function checkStartDate(i) {
    previous = i-1;
    if (moment(start_date, "DD-MM-YYYY", true).isValid()) {
        startDate = new Date(moment(start_date, "DD-MM-YYYY").format("YYYY-MM-DD"));
        startDate.setDate(startDate.getDate()-1);
        if(previous >= 0) {
            $('#id_form-' + previous + '-end_date').val(moment(startDate.toISOString().substring(0, 10), "YYYY-MM-DD").format("DD-MM-YYYY"));
        }
        if(start_date != '') {
            $('#id_form-' + i + '-start_date').val(moment(start_date, "DD-MM-YYYY").format("DD-MM-YYYY"));
        }
    }
}

function getFiscalPeriod() {
    error = 0
    $('#fiscal_error').text('')
    for(i=0; i<12; i++) {
        period = i+1
        var start = $('#id_form-'+i+'-start_date').val();
        var end = $('#id_form-'+i+'-end_date').val();
        var startDate = new Date(moment(start, "DD-MM-YYYY").format("YYYY-MM-DD"));
        var endDate = new Date(moment(end, "DD-MM-YYYY").format("YYYY-MM-DD"));
        if(startDate > endDate) {
            error += 1;
            $('#fiscal_error').append('Start Date ( '+start+' ) is greater than End Date ( '+end+' ) in Period '+period+'.<br>');
        }
    }
    if(error > 0) {
        return false;
    } else {
        return true;
    }
}

$(function () {
    $('.button-checkbox').each(function () {

        // Settings
        var $widget = $(this),
            $button = $widget.find('button'),
            $checkbox = $widget.find('input:checkbox'),
            color = $button.data('color'),
            settings = {
                on: {
                    icon: 'fa fa-lock'
                },
                off: {
                    icon: 'fa fa-unlock-alt'
                }
            };

        // Event Handlers
        $button.on('click', function () {
            
            if($checkbox[0].id == 'all-checkbox'){
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();

                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_']").prop('checked', false).trigger('change');
                }
                //$("button[name*='btn-check']").trigger('click');
                //
                //$('input:checkbox').not(this).prop('checked', this.checked);
                
            }
            else if($checkbox[0].id == 'all-ap-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_ap']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_ap']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id == 'all-ar-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_ar']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_ar']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id == 'all-gl-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_gl']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_gl']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id == 'all-bank-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_bank']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_bank']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id == 'all-sp-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_sp']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_sp']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id == 'all-ic-checkbox') {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                a = $checkbox.is(':checked');
                if(a) {
                    $("input[name*='is_ic']").prop('checked', true).trigger('change');
                } else {
                    $("input[name*='is_ic']").prop('checked', false).trigger('change');
                }
            }
            else if($checkbox[0].id.substring(0,4) == 'form') {
                id = $checkbox[0].id;
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
                if(id == 'form-1') {
                    a = $checkbox.is(':checked');
                    if(a) {
                        $("input[name*='"+id+"-is']").prop('checked', true).trigger('change');
                    } else {
                        $("input[name*='"+id+"-is']").prop('checked', false).trigger('change');
                    }
                } else {
                    a = $checkbox.is(':checked');
                    if(a) {
                        $("input[name*='"+id+"']").prop('checked', true).trigger('change');
                    } else {
                        $("input[name*='"+id+"']").prop('checked', false).trigger('change');
                    }
                }
                
            }
            else {
                $checkbox.prop('checked', !$checkbox.is(':checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
            }
        });
        $checkbox.on('change', function () {
            updateDisplay();
            // if( $("input[name*='is_ap']:checked").length == $("input[name*='is_ap']").length) {
            //     $('#all-ap-checkbox').prop('checked', true).trigger('change');
            // }
        });

        // Actions
        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');

            // Set the button's state
            $button.data('state', (isChecked) ? "on" : "off");

            // Set the button's icon
            $button.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$button.data('state')].icon);

            // Update the button's color
            if (isChecked) {
                $button
                    .removeClass('btn-default')
                    .addClass('btn-' + color + ' active');
            }
            else {
                $button
                    .removeClass('btn-' + color + ' active')
                    .addClass('btn-default');
            }
        }

        // Initialization
        function init() {

            updateDisplay();

            // Inject the icon if applicable
            if ($button.find('.state-icon').length == 0) {
                $button.prepend('<i class="state-icon ' + settings[$button.data('state')].icon + '"></i> ');
            }
        }
        init();
    });
});