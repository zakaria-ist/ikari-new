$('.suppler-checkbox').click(function () {
    supplier_selected = $('input[name="supplier_selected"]').val();
    if (this.checked) {
        supplier_selected += this.value + ';';
        $('input[name="supplier_selected"]').val(supplier_selected);
    }
    else {
        var supplier_remove = this.value + ';'
        var suppler_removed = supplier_selected.replace(supplier_remove, '');
        $('input[name="supplier_selected"]').val(suppler_removed);
    }
});


function fnFormatDetails(oTable, nTr) {
    var sOut = '';
    var aData = oTable.fnGetData(nTr);
    var jqInputs = $('input', nTr);
    $.ajax({
        method: "POST",
        url: '/orders/load_sales_items_by_supplier/' + jqInputs[1].value + '/' + jqInputs[0].value + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            if (json.length > 0) {
                var sOut = '<table class="display table table-bordered table-striped table-condensed" ' +
                    'style="margin-bottom: 0px! important;">';
                sOut += '<tr><th>Product</th><th>Quantity</th><th>Purchase Price</th><th>Exchange Rate</th><th>Amount</th></tr>'
                for (j = 0; j < json.length; j++) {
                    sOut += '<tr>';
                    sOut += '<td>' + json[j].name + '</td>';
                    sOut += '<td>' + json[j].quantity + '</td>';
                    sOut += '<td>' + json[j].purchase_price + '</td>';
                    sOut += '<td>' + json[j].exchange_rate + '</td>';
                    sOut += '<td>' + parseFloat(json[j].amount).toFixed(2) + '</td>';
                    sOut += '</tr>';
                }
                sOut += '</table>';
                oTable.fnOpen(nTr, sOut, 'details');
            }

        }
    });

    return sOut;
}

$(document).ready(function () {
    /*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement('th');
    var nCloneTd = document.createElement('td');
    nCloneTd.innerHTML = '<img src="/static/img/details_open.png">';
    nCloneTd.className = "center";

    $('#purchase-order-table-info thead tr').each(function () {
        this.insertBefore(nCloneTh, this.childNodes[0]);
    });

    $('#purchase-order-table-info tbody tr').each(function () {
        this.insertBefore(nCloneTd.cloneNode(true), this.childNodes[0]);
    });

    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    var oTable = $('#purchase-order-table-info').dataTable({
        "aoColumnDefs": [
            {"bSortable": false, "aTargets": [0]}
        ],
        "aaSorting": [[0, 'asc']]
    });

    /* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    $(document).on('click', '#purchase-order-table-info tbody td img', function () {
        var nTr = $(this).parents('tr')[0];
        if (oTable.fnIsOpen(nTr)) {
            /* This row is already open - close it */
            this.src = "/static/img/details_open.png";
            oTable.fnClose(nTr);
        }
        else {
            /* Open this row */
            this.src = "/static/img/details_close.png";
            oTable.fnOpen(nTr, fnFormatDetails(oTable, nTr), 'details');
        }
    });
});