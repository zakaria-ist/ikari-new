var EditableTable = function () {

    return {

        //main function to initiate the module
        init: function () {
            function restoreRow(oTable, nRow) {
                var aData = oTable.fnGetData(nRow);
                var jqTds = $('>td', nRow);

                for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                    oTable.fnUpdate(aData[i], nRow, i, false);
                }

                oTable.fnDraw();
            }

            function editRow(oTable, nRow) {
                var aData = oTable.fnGetData(nRow);
                var jqTds = $('>td', nRow);

                for (i = 0; i < jqTds.length; i++) {
                    var spanData = jqTds[i].getElementsByTagName("span").item(0);
                    if (spanData != null) {
                        var inputData = spanData.getElementsByTagName("input").item(0);
                        var transData = $.trim(aData[i].split('<span')[0])
                        if (inputData != null) {
                            inputData.setAttribute("value", transData);
                        }
                        else {
                            selectData = spanData.getElementsByTagName("option");
                            for (x = 0; x < selectData.length; x++) {
                                var optionData = selectData.item(x);
                                if ($.trim(optionData.innerText) == transData) {
                                    optionData.setAttribute("selected", "selected");
                                    selectData.item(0).setAttribute("selected", "");
                                }
                            }
                        }
                        jqTds[i].innerHTML = spanData.innerHTML;
                    }
                }
                debugger;
                // jqTds[0].innerHTML = jqTds[0].getElementsByTagName("span").item(0).innerHTML
                jqTds[9].innerHTML = jqTds[9].getElementsByTagName("input").item(0).outerHTML;
                jqTds[9].innerHTML = jqTds[9].innerHTML + '<a class="edit fa fa-save btn btn-success btn-xs" href="">Save</a>' +
                    '<a class="cancel fa fa-times btn btn-default btn-xs" href="">Cancel</a>';
            }

            function saveRow(oTable, nRow) {

                var jqInputs = $('input', nRow);
                var jqSelects = $('select', nRow);

                $.ajax({
                    method: "POST",
                    url: '/transactions/payment/edit/' + jqInputs[4].value + '/',
                    dataType: 'JSON',
                    data: {
                        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                        'transaction_date': jqInputs[0].value,
                        'number': jqInputs[1].value,
                        'amount': jqInputs[2].value,
                        'currency': jqSelects[0].value,
                        'debit_account': jqSelects[1].value,
                        'credit_account': jqSelects[2].value,
                    },
                    responseTime: 200,
                    complete: function (jqXHR) {
                        if (jqXHR.readyState === 4) {
                            window.location.reload(true);
                        }
                    }
                });

                var btnEditDelete = '<a class="edit fa fa-edit btn btn-primary btn-xs" href="javascript:;"></a>'
                btnEditDelete = btnEditDelete + '<a style="min-width: 20px!important;" class="delete fa fa-bitbucket btn btn-danger btn-xs" href="javascript:;"></a>'

                oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);//transaction_date
                oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);//number
                //oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);//remark
                oTable.fnUpdate(jqInputs[2].value, nRow, 3, false);//payment amount               
                oTable.fnUpdate(jqInputs[3].value * jqInputs[2].value, nRow, 5, false);//amount

                oTable.fnUpdate(jqSelects[0].selectedOptions[0].innerText, nRow, 2, false);//currency
                oTable.fnUpdate(jqSelects[1].selectedOptions[0].innerText, nRow, 7, false);//debit_account
                oTable.fnUpdate(jqSelects[2].selectedOptions[0].innerText, nRow, 8, false);//credit_account
                oTable.fnUpdate(btnEditDelete, nRow, 9, false);
                //oTable.fnUpdate('<a class="delete" href="">Delete</a>', nRow, 8, false);
                oTable.fnDraw();
                window.location.reload(true);
            }

            function cancelEditRow(oTable, nRow) {
                var jqInputs = $('input', nRow);
                oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
                oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
                oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
                oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
                oTable.fnUpdate(jqInputs[4].value, nRow, 4, false);
                oTable.fnUpdate(jqInputs[5].value, nRow, 5, false);
                oTable.fnUpdate(jqInputs[6].value, nRow, 6, false);
                oTable.fnUpdate(jqInputs[7].value, nRow, 7, false);
                oTable.fnUpdate(jqInputs[8].value, nRow, 8, false);
                oTable.fnUpdate('<a class="edit" href="">Edit</a>', nRow, 9, false);
                oTable.fnDraw();
            }

            var oTable = $('#editable-sample').dataTable({
                "aLengthMenu": [
                    [5, 15, 20, -1],
                    [5, 15, 20, "All"] // change per page values here
                ],
                // set the initial value
                "iDisplayLength": 5,
                "sDom": "<'row'<'col-lg-6'l><'col-lg-6'f>r>t<'row'<'col-lg-6'i><'col-lg-6'p>>",
                "sPaginationType": "bootstrap",
                "oLanguage": {
                    "sLengthMenu": "_MENU_ records per page",
                    "oPaginate": {
                        "sPrevious": "Prev",
                        "sNext": "Next"
                    }
                },
                "aoColumnDefs": [{
                    'bSortable': false,
                    'aTargets': [0]
                }
                ]
            });

            jQuery('#editable-sample_wrapper .dataTables_filter input').addClass("form-control medium"); // modify table search input
            jQuery('#editable-sample_wrapper .dataTables_length select').addClass("form-control xsmall"); // modify table per page dropdown

            var nEditing = null;

            $('#editable-sample_new').click(function (e) {
                e.preventDefault();
                var aiNew = oTable.fnAddData(['', '', '', '',
                    '<a class="edit" href="">Edit</a>', '<a class="cancel" data-mode="new" href="">Cancel</a>'
                ]);
                var nRow = oTable.fnGetNodes(aiNew[0]);
                editRow(oTable, nRow);
                nEditing = nRow;
            });

            $('#editable-sample a.delete').live('click', function (e) {
                e.preventDefault();

                $('#delete-transaction-dialog').modal('show');
                var frDelete = $('#delete-transaction-form')[0];
                var nRow = $(this).parents('tr')[0];
                var jqInputs = $('input', nRow);
                var hd_order_type = $('#hd_order_type')[0].value;
                frDelete.setAttribute('action', '/transactions/payment/delete/' + jqInputs[4].value + '/' + hd_order_type + '/');

            });

            $('#editable-sample a.cancel').live('click', function (e) {
                e.preventDefault();
                if ($(this).attr("data-mode") == "new") {
                    var nRow = $(this).parents('tr')[0];
                    oTable.fnDeleteRow(nRow);
                } else {
                    restoreRow(oTable, nEditing);
                    nEditing = null;
                }
            });

            $('#editable-sample a.edit').live('click', function (e) {
                e.preventDefault();

                /* Get the row as a parent of the link that was clicked on */
                var nRow = $(this).parents('tr')[0];

                if (nEditing !== null && nEditing != nRow) {
                    /* Currently editing - but not this row - restore the old before continuing to edit mode */
                    restoreRow(oTable, nEditing);
                    editRow(oTable, nRow);
                    nEditing = nRow;
                } else if (nEditing == nRow && this.innerHTML == "Save") {
                    /* Editing this row and want to save it */
                    saveRow(oTable, nEditing);
                    nEditing = null;
                } else {
                    /* No edit in progress - let's start one */
                    editRow(oTable, nRow);
                    nEditing = nRow;
                }
            });
        }

    };

}();