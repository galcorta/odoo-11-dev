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
            this.chart_lang = {
                                printChart: 'Imprimir Gráfico',
                                downloadPNG: 'Descargar imagen PNG',
                                downloadJPEG: 'Descargar imagen JPEG',
                                downloadPDF: 'Descargar archivo PDF',
                                downloadSVG: 'Descargar imagen SVG',
                                contextButtonTitle: 'Opciones',
                                noData: 'No hay datos para mostrar'
                            }
        },
        start: function() {
            var self = this;
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'gender', community_id: self.community_id},
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'population', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('population', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'sump', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('sump', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'source_distance', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('source_distance', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_qualification', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('water_qualification', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_treatment', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('water_treatment', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'common_diseases', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('common_diseases', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'water_supply', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('water_supply', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'occupation', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('occupation', {
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
            });

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'sias.survey.input',
                method: 'get_charts_data',
                args: [[]],
                kwargs: {chart: 'education', community_id: self.community_id},
            }).then(function (result) {
                self.GenderPieChart = Highcharts.chart('education', {
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
            });
        },
    });

    core.action_registry.add("action_sias_chart_page", ChartPage);
    return {
        ChartPage: ChartPage,
    };

});
