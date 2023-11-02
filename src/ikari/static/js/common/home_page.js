$(document).ready(function () {
    var current_date = new Date();

    $.ajax({
        method: "POST",
        url: '/reports/get_current_month_amount/2/' + (current_date.getMonth() + 1) + '/' + current_date.getFullYear() + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            $display = $('.count');
            $display.text(json.month_amount.toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,"));
            //countUp(json);
        }
    });
    $.ajax({
        method: "POST",
        url: '/reports/get_current_month_amount/1/' + (current_date.getMonth() + 1) + '/' + current_date.getFullYear() + '/',
        dataType: 'JSON',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        responseTime: 200,
        success: function (json) {
            $display = $('.count2');
            $display.text(json.month_amount.toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,"));
        }
    });

    var arrSalesAmount = [];
    var arrPurchaseAmount = [];
    $("#barchart_sales").sparkline(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {
        type: 'bar',
        height: '250',
        barWidth: 8,
        barSpacing: 5,
        barColor: '#c6cad6'
    });
    $("#barchart_purchase").sparkline(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {
        type: 'bar',
        height: '250',
        barWidth: 8,
        barSpacing: 5,
        barColor: '#c6cad6'
    });

    function calculateAmountOfBarChart() {
        for (x = 1; x <= 12; x++) {
            $.ajax({
                method: "POST",
                url: '/reports/get_current_month_amount/1/' + x + '/' + current_date.getFullYear() + '/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                responseTime: 200,
                success: function (json) {
                    arrSalesAmount[parseInt(json.month)-1] = json.month_amount;
                    if (json.month == '12') {
                        $display = $('.chart-tittle .value')[1];
                        $display.innerText = (parseFloat(arrSalesAmount[0]) + parseFloat(arrSalesAmount[1]) +
                        parseFloat(arrSalesAmount[2]) + parseFloat(arrSalesAmount[3]) +
                        parseFloat(arrSalesAmount[4]) + parseFloat(arrSalesAmount[5]) +
                        parseFloat(arrSalesAmount[6]) + parseFloat(arrSalesAmount[7]) +
                        parseFloat(arrSalesAmount[8]) + parseFloat(arrSalesAmount[9]) +
                        parseFloat(arrSalesAmount[10]) + parseFloat(arrSalesAmount[11])).toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
                        $("#barchart_sales").sparkline([arrSalesAmount[0], arrSalesAmount[1], arrSalesAmount[2],
                            arrSalesAmount[3], arrSalesAmount[4], arrSalesAmount[5], arrSalesAmount[6],
                            arrSalesAmount[7], arrSalesAmount[8], arrSalesAmount[9], arrSalesAmount[10],
                            arrSalesAmount[11]], {
                            type: 'bar',
                            height: '250',
                            barWidth: 25,
                            barSpacing: 15,
                            barColor: '#c6cad6',
                            disableHighlight: true
                        });
                    }
                }
            });
            $.ajax({
                method: "POST",
                url: '/reports/get_current_month_amount/2/' + x + '/' + current_date.getFullYear() + '/',
                dataType: 'JSON',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                responseTime: 200,
                success: function (json) {
                    arrPurchaseAmount[parseInt(json.month)-1] = json.month_amount;
                    if (json.month == '12') {
                        $display = $('.chart-tittle .value')[0];
                        $display.innerText = (parseFloat(arrPurchaseAmount[0]) + parseFloat(arrPurchaseAmount[1]) +
                        parseFloat(arrPurchaseAmount[2]) + parseFloat(arrPurchaseAmount[3]) +
                        parseFloat(arrPurchaseAmount[4]) + parseFloat(arrPurchaseAmount[5]) +
                        parseFloat(arrPurchaseAmount[6]) + parseFloat(arrPurchaseAmount[7]) +
                        parseFloat(arrPurchaseAmount[8]) + parseFloat(arrPurchaseAmount[9]) +
                        parseFloat(arrPurchaseAmount[10]) + parseFloat(arrPurchaseAmount[11])).toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
                        $("#barchart_purchase").sparkline([arrPurchaseAmount[0], arrPurchaseAmount[1], arrPurchaseAmount[2],
                            arrPurchaseAmount[3], arrPurchaseAmount[4], arrPurchaseAmount[5], arrPurchaseAmount[6],
                            arrPurchaseAmount[7], arrPurchaseAmount[8], arrPurchaseAmount[9], arrPurchaseAmount[10],
                            arrPurchaseAmount[11]], {
                            type: 'bar',
                            height: '250',
                            barWidth: 25,
                            barSpacing: 10,
                            barColor: '#c6cad6',
                            disableHighlight: true
                        });
                    }
                }
            });
        }
    }

    calculateAmountOfBarChart();

});