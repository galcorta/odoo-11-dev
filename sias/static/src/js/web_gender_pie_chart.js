/*global Highcharts*/
odoo.define("sias.chart_page", function(require) {
    "use strict";

    var core = require("web.core");
    var Widget = require("web.Widget");
    var ajax = require('web.ajax');
    var WebClient = require('web.web_client');
    var Session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;

    var ChartPage = Widget.extend({
        template: "GenderPieChart",
        init: function(parent, options){
            this._super.apply(this, arguments);
            this.community_id=options.params.community_id;
        },
        start: function() {
            var self = this;
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_gender_data',
                args: [[]],
                kwargs: {community_id: self.community_id
                },
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('container', {
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Porcentaje de mujeres y varones'
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                                style: {
                                    color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Brands',
                        colorByPoint: true,
                        data: result
                    }]
                });
            });

        },
    });

    core.action_registry.add("action_sias_chart_page", ChartPage);
    return {
        ChartPage: ChartPage,
    };

});
