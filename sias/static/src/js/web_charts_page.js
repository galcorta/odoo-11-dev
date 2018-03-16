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

    var ChartsPage = Widget.extend({
        template: "ChartsPage",
        init: function(parent, options){
            this._super.apply(this, arguments);
            this.community_id=options.params.community_id;
            this.survey_id=options.params.survey_id;
            this.chart_lang = {
                                printChart: 'Imprimir Gráfico',
                                downloadPNG: 'Descargar imagen PNG',
                                downloadJPEG: 'Descargar imagen JPEG',
                                downloadPDF: 'Descargar archivo PDF',
                                downloadSVG: 'Descargar imagen SVG',
                                contextButtonTitle: 'Opciones',
                                noData: 'No hay datos para mostrar'
                            }
            this.chartList = []

            /**
             * Create a global getSVG method that takes an array of charts as an argument. The SVG is returned as an argument in the callback.
             */
            Highcharts.getSVG = function (charts, options, callback) {
                var svgArr = [],
                    top = 0,
                    width = 0,
                    addSVG = function (svgres) {
                        // Grab width/height from exported chart
                        var svgWidth = +svgres.match(
                                /^<svg[^>]*width\s*=\s*\"?(\d+)\"?[^>]*>/
                            )[1],
                            svgHeight = +svgres.match(
                                /^<svg[^>]*height\s*=\s*\"?(\d+)\"?[^>]*>/
                            )[1],
                            // Offset the position of this chart in the final SVG
                            svg = svgres.replace('<svg', '<g transform="translate(0,' + top + ')" ');
                        svg = svg.replace('</svg>', '</g>');
                        top += svgHeight;
                        width = Math.max(width, svgWidth);
                        svgArr.push(svg);
                    },
                    exportChart = function (i) {
                        if (i === charts.length) {
                            return callback('<svg height="' + top + '" width="' + width +
                              '" version="1.1" xmlns="http://www.w3.org/2000/svg">' + svgArr.join('') + '</svg>');
                        }
                        charts[i].getSVGForLocalExport(options, {}, function () {
                            console.log("Failed to get SVG");
                        }, function (svg) {
                            addSVG(svg);
                            return exportChart(i + 1); // Export next only when this SVG is received
                        });
                    };
                exportChart(0);
            };

            /**
             * Create a global exportCharts method that takes an array of charts as an argument,
             * and exporting options as the second argument
             */
            Highcharts.exportCharts = function (charts, options) {
                options = Highcharts.merge(Highcharts.getOptions().exporting, options);

                    // Get SVG asynchronously and then download the resulting SVG
                Highcharts.getSVG(charts, options, function (svg) {
                    Highcharts.downloadSVGLocal(svg, options, function () {
                        console.log("Failed to export on client side");
                    });
                });
            };

            // Set global default options for all charts
            Highcharts.setOptions({
                exporting: {
                    fallbackToExportServer: false // Ensure the export happens on the client side or not at all
                }
            });
        },
        start: function() {
            var self = this;
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'gender', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('gender', {
                    lang: self.chart_lang,
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.GenderPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'population', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.PopulationPieChart = Highcharts.chart('population', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Menores de 20 años'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.PopulationPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'sump', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.SumpPieChart = Highcharts.chart('sump', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Poseedores de letrina'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.SumpPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'source_distance', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.SourceDistancePieChart = Highcharts.chart('source_distance', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Distancia a la fuente mas cercana'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.SourceDistancePieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_qualification', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.WaterQualificationPieChart = Highcharts.chart('water_qualification', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Cómo califican la calidad del Agua'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.WaterQualificationPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_treatment', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.WaterTreatmentPieChart = Highcharts.chart('water_treatment', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Tratamiento del Agua para beber'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.WaterTreatmentPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'common_diseases', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.CommonDiseasesPieChart = Highcharts.chart('common_diseases', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Enfermedades más comunes en los últimos 6 meses'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.CommonDiseasesPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_supply', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.WaterSupplyPieChart = Highcharts.chart('water_supply', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Fuente de abastecimiento de Agua'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.WaterSupplyPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'occupation', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.OccupationPieChart = Highcharts.chart('occupation', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Ocupación'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.OccupationPieChart)
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'education', community_id: self.community_id, survey_id: self.survey_id},
            }).then(function (result) {
                self.EducationPieChart = Highcharts.chart('education', {
                    lang: self.chart_lang,
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Grado de instrucción'
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
                        name: 'Puntos',
                        colorByPoint: true,
                        data: result
                    }]
                });
                self.chartList.push(self.EducationPieChart)
            });


            self.$el.find('#export-png').click(function () {
                Highcharts.exportCharts(self.chartList);
            });

            self.$el.find('#export-pdf').click(function () {
                Highcharts.exportCharts(self.chartList, {
                    type: 'application/pdf'
                });
            });


        },
    });

    core.action_registry.add("action_sias_charts_page", ChartsPage);

    return {
        ChartsPage: ChartsPage,
    };

});
