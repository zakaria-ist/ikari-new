function update_tab_travel(ord_code){
    try{
        switch(ord_code) {
            case 'SR7101':

                $('#loading').show();
                setTimeout(() => {
                    // $("select").select2('close');
                    $("#date_fromSA").datepicker('hide');
                    $("#date_toSA").datepicker('hide');
                    $('#report_list').focus();
                    $('#report_list').select2('open');
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSA').focus();
                });

                $('#date_fromSA').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSA').focus();
                    }
                });

                $('#date_toSA').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#fromSACustomerPo').select2('open');
                    }
                });

                $('#fromSACustomerPo').on('select2:select', function (e)
                {
                    $('#toSACustomerPo').select2('open');
                });

                $('#fromSACustomerPo').on('select2:close', function (e)
                {
                    $('#toSACustomerPo').focus();
                });

                $('#toSACustomerPo').on('select2:select', function (e)
                {
                    $('#fromSAPartNo').select2('open');
                });

                $('#toSACustomerPo').on('select2:close', function (e)
                {
                    $('#fromSAPartNo').focus();
                });

                $('#fromSAPartNo').on('select2:select', function (e)
                {
                    $('#toSAPartNo').select2('open');
                });

                $('#fromSAPartNo').on('select2:close', function (e)
                {
                    $('#toSAPartNo').focus();
                });

                $('#toSAPartNo').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7103':
                $('#loading').show();
                setTimeout(() => {
                    // $("select").select2('close');
                    $('#date_fromSA').focus();
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSA').focus();
                });

                $('#date_fromSA').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSA').focus();
                    }
                });

                $('#date_toSA').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#fromSACustomer').select2('open');
                    }
                });

                $('#fromSACustomer').on('select2:select', function (e)
                {
                    $('#toSACustomer').select2('open');
                });

                $('#fromSACustomer').on('select2:close', function (e)
                {
                    $('#toSACustomer').focus();
                });

                $('#toSACustomer').on('select2:select', function (e)
                {
                    $('#fromSACustomerPo').select2('open');
                });

                $('#toSACustomer').on('select2:close', function (e)
                {
                    $('#fromSACustomerPo').focus();
                });

                $('#fromSACustomerPo').on('select2:select', function (e)
                {
                    $('#toSACustomerPo').select2('open');
                });

                $('#fromSACustomerPo').on('select2:close', function (e)
                {
                    $('#toSACustomerPo').focus();
                });

                $('#toSACustomerPo').on('select2:select', function (e)
                {
                    $('#fromSAPartNo').select2('open');
                });

                $('#toSACustomerPo').on('select2:close', function (e)
                {
                    $('#fromSAPartNo').focus();
                });

                $('#fromSAPartNo').on('select2:select', function (e)
                {
                    $('#toSAPartNo').select2('open');
                });

                $('#fromSAPartNo').on('select2:close', function (e)
                {
                    $('#toSAPartNo').focus();
                });

                $('#toSAPartNo').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7201':
                $('#loading').show();
                setTimeout(() => {
                    // $("select").select2('close');
                    $("#date_fromSR7201").datepicker('hide');
                    $("#date_toSR7201").datepicker('hide');
                    $('#report_list').focus();
                    $('#report_list').select2('open');
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7201').focus();
                });

                $('#date_fromSR7201').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7201').focus();
                    }
                });

                $('#date_toSR7201').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7201Document').select2('open');
                    }
                });

                $('#lbSR7201Document').on('select2:select', function (e)
                {
                    $('#lbSR7201ToDocument').select2('open');
                });

                $('#lbSR7201Document').on('select2:close', function (e)
                {
                    $('#lbSR7201ToDocument').focus();
                });

                $('#lbSR7201ToDocument').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7202':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7202').focus();
                });

                $('#date_fromSR7202').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7202').focus();
                    }
                });

                $('#date_toSR7202').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7202Supplier').select2('open');
                    }
                });

                $('#lbSR7202Supplier').on('select2:select', function (e)
                {
                    $('#lbSR7202ToSupplier').select2('open');
                });

                $('#lbSR7202Supplier').on('select2:close', function (e)
                {
                    $('#lbSR7202ToSupplier').focus();
                });

                $('#lbSR7202ToSupplier').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7203':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7203').focus();
                });

                $('#date_fromSR7203').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7203').focus();
                    }
                });

                $('#date_toSR7203').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7203Supplier').select2('open');
                    }
                });

                $('#lbSR7203Supplier').on('select2:select', function (e)
                {
                    $('#lbSR7203ToSupplier').select2('open');
                });

                $('#lbSR7203Supplier').on('select2:close', function (e)
                {
                    $('#lbSR7203ToSupplier').focus();
                });

                $('#lbSR7203ToSupplier').on('select2:select', function (e)
                {
                    $('#lbSR7203Cutomer').select2('open');
                });

                $('#lbSR7203ToSupplier').on('select2:close', function (e)
                {
                    $('#lbSR7203Cutomer').focus();
                });

                $('#lbSR7203Cutomer').on('select2:select', function (e)
                {
                    $('#lbSR7203ToCutomer').select2('open');
                });

                $('#lbSR7203Cutomer').on('select2:close', function (e)
                {
                    $('#lbSR7203ToCutomer').focus();
                });

                $('#lbSR7203ToCutomer').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7204':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7204').focus();
                });

                $('#date_fromSR7204').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7204').focus();
                    }
                });

                $('#date_toSR7204').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7204Supplier').select2('open');
                    }
                });

                $('#lbSR7204Supplier').on('select2:select', function (e)
                {
                    $('#lbSR7204ToSupplier').select2('open');
                });

                $('#lbSR7204Supplier').on('select2:close', function (e)
                {
                    $('#lbSR7204ToSupplier').focus();
                });

                $('#lbSR7204ToSupplier').on('select2:select', function (e)
                {
                    $('#lbSR7204PartNo').select2('open');
                });

                $('#lbSR7204ToSupplier').on('select2:close', function (e)
                {
                    $('#lbSR7204PartNo').focus();
                });

                $('#lbSR7204PartNo').on('select2:select', function (e)
                {
                    $('#lbSR7204ToPartNo').select2('open');
                });

                $('#lbSR7204PartNo').on('select2:close', function (e)
                {
                    $('#lbSR7204ToPartNo').focus();
                });

                $('#lbSR7204ToPartNo').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7404':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7404').focus();
                });

                $('#date_fromSR7404').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7404').focus();
                    }
                });

                $('#date_toSR7404').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7404Customer').select2('open');
                    }
                });

                $('#lbSR7404Customer').on('select2:close', function (e)
                {
                    $('#lbSR7404ToCustomer').focus();
                    // $('#lbSR7404ToCustomer').select2('open');
                });

                $('#lbSR7404Customer').on('select2:select', function (e)
                {
                    // $('#lbSR7404ToCustomer').focus();
                    $('#lbSR7404ToCustomer').select2('open');
                });

                $('#lbSR7404ToCustomer').on('select2:close', function (e)
                {
                    $('#lbSR7404PartNo').focus();
                    // $('#lbSR7404PartNo').select2('open');
                });

                $('#lbSR7404ToCustomer').on('select2:select', function (e)
                {
                    // $('#lbSR7404PartNo').focus();
                    $('#lbSR7404PartNo').select2('open');
                });

                $('#lbSR7404PartNo').on('select2:close', function (e)
                {
                    $('#lbSR7404ToPartNo').focus();
                    // $('#lbSR7404ToPartNo').select2('open');
                });

                $('#lbSR7404PartNo').on('select2:select', function (e)
                {
                    // $('#lbSR7404ToPartNo').focus();
                    $('#lbSR7404ToPartNo').select2('open');
                });

                $('#lbSR7404ToPartNo').on('select2:close', function (e)
                {
                    $('#lbSR7404PartGrp').focus();
                    // $('#lbSR7404PartGrp').select2('open');
                });

                $('#lbSR7404ToPartNo').on('select2:select', function (e)
                {
                    // $('#lbSR7404PartGrp').focus();
                    $('#lbSR7404PartGrp').select2('open');
                });

                $('#lbSR7404PartGrp').on('select2:close', function (e)
                {
                    $('#lbSR7404ToPartGrp').focus();
                    // $('#lbSR7404ToPartGrp').select2('open');
                });

                $('#lbSR7404PartGrp').on('select2:select', function (e)
                {
                    // $('#lbSR7404ToPartGrp').focus();
                    $('#lbSR7404ToPartGrp').select2('open');
                });

                $('#lbSR7404ToPartGrp').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });

                $('#lbSR7404ToPartGrp').on('select2:select', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7401':

                $('#loading').show();
                setTimeout(() => {
                    // $("select").select2('close');
                    $("#date_fromSR7401").datepicker('hide');
                    $("#date_toSR7401").datepicker('hide');
                    $('#report_list').focus();
                    $('#report_list').select2('open');
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7401').focus();
                });

                $('#date_fromSR7401').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7401').focus();
                    }
                });

                $('#date_toSR7401').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#txtDocNoFromSR7401').select2('open');
                    }
                });

                $('#txtDocNoFromSR7401').on('select2:select', function (e)
                {
                    $('#txtDocNoToSR7401').select2('open');
                });

                $('#txtDocNoFromSR7401').on('select2:close', function (e)
                {
                    $('#txtDocNoToSR7401').focus();
                });

                $('#txtDocNoToSR7401').on('select2:select', function (e)
                {
                    $('#txtCustPONoFromSR7401').select2('open');
                });

                $('#txtDocNoToSR7401').on('select2:close', function (e)
                {
                    $('#txtCustPONoFromSR7401').focus();
                });

                $('#txtCustPONoFromSR7401').on('select2:select', function (e)
                {
                    $('#txtCustPONoToSR7401').select2('open');
                });

                $('#txtCustPONoFromSR7401').on('select2:close', function (e)
                {
                    $('#txtCustPONoToSR7401').focus();
                });

                $('#txtCustPONoToSR7401').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7402':
            case 'SR8800':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7402').focus();
                });

                $('#date_fromSR7402').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7402').focus();
                    }
                });

                $('#date_toSR7402').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#lbSR7402Customer').select2('open');
                    }
                });

                $('#lbSR7402Customer').on('select2:select', function (e)
                {
                    $('#lbSR7402ToCustomer').select2('open');
                });

                $('#lbSR7402Customer').on('select2:close', function (e)
                {
                    $('#lbSR7402ToCustomer').focus();
                });

                $('#lbSR7402ToCustomer').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7502':
            case 'SR7503':
                $('#loading').show();

                setTimeout(() => {
                    // $("select").select2('close');
                    $("#date_fromSR7503").datepicker('hide');
                    $("#date_toSR7503").datepicker('hide');
                    $('#report_list').focus();
                    $('#report_list').select2('open');
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7503').focus();
                });

                $('#date_fromSR7503').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7503').focus();
                    }
                });

                $('#date_toSR7503').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $('#date_toSR7503').datepicker('hide');
                        $('#loading').show();
                        setTimeout(() => {
                            $('#loading').hide();
                            //$('#txtCustPONoFromSR7503').select2('open');
                        }, 900);
                    }
                });

                $('#txtCustPONoFromSR7503').on('select2:select', function (e)
                {
                    $('#txtCustPONoToSR7503').select2('open');
                });

                $('#txtCustPONoFromSR7503').on('select2:close', function (e)
                {
                    $('#txtCustPONoToSR7503').focus();
                });

                $('#txtCustPONoToSR7503').on('select2:select', function (e)
                {
                    $('#txtPartGrpSR7503').select2('open');
                });

                $('#txtCustPONoToSR7503').on('select2:close', function (e)
                {
                    $('#txtPartGrpSR7503').focus();
                });

                $('#txtPartGrpSR7503').on('select2:select', function (e)
                {
                    $('#txtPartGrpToSR7503').select2('open');
                });

                $('#txtPartGrpSR7503').on('select2:close', function (e)
                {
                    $('#txtPartGrpToSR7503').focus();
                });

                $('#txtPartGrpToSR7503').on('select2:select', function (e)
                {
                    $('#txtPartNoSR7503').select2('open');
                });

                $('#txtPartGrpToSR7503').on('select2:close', function (e)
                {
                    $('#txtPartNoSR7503').focus();
                });

                $('#txtPartNoSR7503').on('select2:select', function (e)
                {
                    $('#txtPartNoToSR7503').select2('open');
                });

                $('#txtPartNoSR7503').on('select2:close', function (e)
                {
                    $('#txtPartNoToSR7503').focus();
                });

                $('#txtPartNoToSR7503').on('select2:select', function (e)
                {
                    $('#is_confirm').select2('open');
                });

                $('#txtPartNoToSR7503').on('select2:close', function (e)
                {
                    $('#is_confirm').focus();
                });

                $('#is_confirm').on('select2:select', function (e)
                {
                    $('#btnReview').focus();
                });

                $('#is_confirm').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7501':
            case 'SR7504':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR7504').focus();
                });

                $('#date_fromSR7504').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR7504').focus();
                    }
                });

                $('#date_toSR7504').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $('#date_toSR7504').datepicker('hide');
                        $('#loading').show();
                        setTimeout(() => {
                            $('#loading').hide();
                            //$('#txtSuppplierNoSR7504').select2('open');
                        }, 900);
                    }
                });

                // $('#date_fromSR7504').on('changeDate', function (ev) {
                //     $('#date_toSR7504').focus();
                // });
                //
                // $('#date_toSR7504').on('changeDate', function (ev) {
                //     $('#txtSuppplierNoSR7504').select2('open');
                // });

                $('#txtSuppplierNoSR7504').on('select2:select', function (e)
                {
                    $('#txtToSuppplierNoSR7504').select2('open');
                });

                $('#txtSuppplierNoSR7504').on('select2:close', function (e)
                {
                    $('#txtToSuppplierNoSR7504').focus();
                });

                $('#txtToSuppplierNoSR7504').on('select2:select', function (e)
                {
                    if (ord_code == 'SR7504') {
                        $('#is_confirm_2').select2('open');
                    }
                });

                $('#txtToSuppplierNoSR7504').on('select2:close', function (e)
                {
                    if (ord_code == 'SR7504') {
                        $('#is_confirm_2').focus();
                    }
                });

                $('#is_confirm_2').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7601':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#year_monthSR7601').focus();
                });

                $('#year_monthSR7601').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        //$('#txtSuppplierCodeSR7601').select2('open');
                    }
                });

                $('#txtSuppplierCodeSR7601').on('select2:select', function (e)
                {
                    $('#totxtSuppplierCodeSR7601').select2('open');
                });

                $('#txtSuppplierCodeSR7601').on('select2:close', function (e)
                {
                    $('#totxtSuppplierCodeSR7601').focus();
                });

                $('#totxtSuppplierCodeSR7601').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7602':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#year_monthSR7602').focus();
                });

                $('#year_monthSR7602').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        //$('#txtSuppplierCodeSR7602').select2('open');
                    }
                });

                $('#txtSuppplierCodeSR7602').on('select2:select', function (e)
                {
                    $('#totxtSuppplierCodeSR7602').select2('open');
                });

                $('#txtSuppplierCodeSR7602').on('select2:close', function (e)
                {
                    $('#totxtSuppplierCodeSR7602').focus();
                });

                $('#totxtSuppplierCodeSR7602').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7302':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#year_monthSR7302').focus();
                });

                $('#year_monthSR7302').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        //$('#txtDocumentNoSR7302').select2('open');
                    }
                });

                $('#txtDocumentNoSR7302').on('select2:select', function (e)
                {
                    $('#txtDocumentNoToSR7302').select2('open');
                });

                $('#txtDocumentNoSR7302').on('select2:close', function (e)
                {
                    $('#txtDocumentNoToSR7302').focus();
                });

                $('#txtDocumentNoToSR7302').on('select2:select', function (e)
                {
                    $('#txtPartNoSR7302').select2('open');
                });

                $('#txtDocumentNoToSR7302').on('select2:close', function (e)
                {
                    $('#txtPartNoSR7302').focus();
                });

                $('#txtPartNoSR7302').on('select2:select', function (e)
                {
                    $('#txtPartNoToSR7302').select2('open');
                });

                $('#txtPartNoSR7302').on('select2:close', function (e)
                {
                    $('#txtPartNoToSR7302').focus();
                });

                $('#txtPartNoToSR7302').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7301':
                $('#report_list').on('select2:select', function (e)
                {
                    $('#year_monthSR7301').focus();
                });

                $('#year_monthSR7301').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        //$('#txtCustomerPoSR7301').select2('open');
                    }
                });

                $('#txtCustomerPoSR7301').on('select2:select', function (e)
                {
                    $('#txtCustomerPoToSR7301').select2('open');
                });

                $('#txtCustomerPoSR7301').on('select2:close', function (e)
                {
                    $('#txtCustomerPoToSR7301').focus();
                });

                $('#txtCustomerPoToSR7301').on('select2:select', function (e)
                {
                    $('#txtPartNoSR7301').select2('open');
                });

                $('#txtCustomerPoToSR7301').on('select2:close', function (e)
                {
                    $('#txtPartNoSR7301').focus();
                });

                $('#txtPartNoSR7301').on('select2:select', function (e)
                {
                    $('#txtPartNoToSR7301').select2('open');
                });

                $('#txtPartNoSR7301').on('select2:close', function (e)
                {
                    $('#txtPartNoToSR7301').focus();
                });

                $('#txtPartNoToSR7301').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'SR7300':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#year_monthSR7300').focus();
                });

                $('#year_monthSR7300').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        //$('#txt7300SuppplierNo').select2('open');
                    }
                });

                $('#txt7300SuppplierNo').on('select2:select', function (e)
                {
                    $('#txt7300ToSuppplierNo').select2('open');
                });

                $('#txt7300SuppplierNo').on('select2:close', function (e)
                {
                    $('#txt7300ToSuppplierNo').focus();
                });

                $('#txt7300ToSuppplierNo').on('select2:select', function (e)
                {
                    $('#txtDocumentNoSR7300').select2('open');
                });

                $('#txt7300ToSuppplierNo').on('select2:close', function (e)
                {
                    $('#txtDocumentNoSR7300').focus();
                });

                $('#txtDocumentNoSR7300').on('select2:select', function (e)
                {
                    $('#txtDocumentNoSR7300_to').select2('open');
                });

                $('#txtDocumentNoSR7300').on('select2:close', function (e)
                {
                    $('#txtDocumentNoSR7300_to').focus();
                });

                $('#txtDocumentNoSR7300_to').on('select2:select', function (e)
                {
                    $('#btnReview').focus();
                });

                $('#txtDocumentNoSR7300_to').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
            case 'GL2200':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#divCurrentMonthCL2200').focus();
                });

                $('#divCurrentMonthCL2200').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#btnReview').focus();
                    }
                });

                break;
            case 'CL2400':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#txtSuppplierCodeCL2400').focus();
                });

                $('#txtSuppplierCodeCL2400').on('focusout', function (e)
                {
                    $('#btnReview').focus();
                });

                $('#txtSuppplierCodeCL2400').on('keydown', function (e)
                {
                    if (e.keyCode == 9) {
                        setTimeout(() => {
                            $('#btnReview').focus();
                        }, 100);
                    }
                });

                break;
            case 'SR8600':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#inputFromSR8600').focus();
                });

                $('#inputToSR8600').on('focusout', function (e)
                {
                    $('#btnReview').focus();
                });

                $('#inputFromSR8600').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#inputToSR8600').focus();
                    }
                });

                $('#inputToSR8600').on('changeDate', function (ev) {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#btnReview').focus();
                    }
                });

                // $('#inputFromSR8600')
                //     .on('hide', function () {
                //         $('#inputToSR8600').focus();
                //     });
                //
                // $('#inputToSR8600')
                //     .on('hide', function () {
                //         $('#btnReview').focus();
                //     });
                break;
            case 'SR8601':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#divCurrentMonthCL2200').focus();
                });

                $('#divCurrentMonthCL2200').on('changeDate', function (ev)
                {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#btnReview').focus();
                    }
                });
                break;

            case 'SR8602':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#divCurrentMonthCL2200').focus();
                });

                $('#divCurrentMonthCL2200').on('changeDate', function (ev)
                {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#btnReview').focus();
                    }
                });
                break;

            case 'SR8700_1':
            case 'SR8700':
            case 'SR8701':
                $('#report_list').on('select2:close', function (e)
                {
                    $('#divCurrentMonthCL2200').focus();
                });

                $('#divCurrentMonthCL2200').on('changeDate', function (ev)
                {
                    valid_date = moment($(this).val(), "MM-YYYY", true).isValid();
                    if (valid_date) {
                        $(this).datepicker('hide');
                        $('#btnReview').focus();
                    }
                });
                break;
            case 'SR8500':

                $('#loading').show();
                setTimeout(() => {
                    // $("select").select2('close');
                    $("#date_fromSR8500").datepicker('hide');
                    $("#date_toSR8500").datepicker('hide');
                    $('#report_list').focus();
                    $('#report_list').select2('open');
                    $('#loading').hide();
                }, 1000);

                $('#report_list').on('select2:close', function (e)
                {
                    $('#date_fromSR8500').focus();
                });

                $('#date_fromSR8500').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        $('#date_toSR8500').focus();
                    }
                });

                $('#date_toSR8500').on('changeDate', function (ev) {
                    var date_from_valid = moment($(this).val(), "DD-MM-YYYY", true).isValid();
                    if (date_from_valid){
                        $(this).datepicker('hide');
                        //$('#sr8500Location').select2('open');
                    }
                });

                $('#sr8500Location').on('select2:select', function (e)
                {
                    $('#sr8500PartNo').select2('open');
                });

                $('#sr8500Location').on('select2:close', function (e)
                {
                    $('#sr8500PartNo').focus();
                });

                $('#sr8500PartNo').on('select2:select', function (e)
                {
                    $('#sr8500ToPartNo').select2('open');
                });

                $('#sr8500PartNo').on('select2:close', function (e)
                {
                    $('#sr8500ToPartNo').focus();
                });

                $('#sr8500ToPartNo').on('select2:close', function (e)
                {
                    $('#btnReview').focus();
                });
                break;
        }
    } catch(e) {
        console.log(e);
    }
}