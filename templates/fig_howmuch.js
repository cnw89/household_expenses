const f1_vars = {{ d_howmuch | safe }}

// Initialize the echarts instance based on the prepared dom
var f1_chart = echarts.init(document.getElementById('f1_chart'));  
window.addEventListener('resize', function() {
    f1_chart.resize();
  });

const f1_pathSymbols = {
    gbp_black : 'image://{{ url_for('static', filename='img/gbp1.svg') }}',
    gbp_blue : 'image://{{ url_for('static', filename='img/gbp2.svg') }}'
}

const f1_labelSetting = {
    show: true,
    position: 'right',
    offset: [5, 0],
    fontSize: 16,
    formatter: function (params) {
      return '£' + Math.ceil(params.value).toLocaleString() ;
    },
  };

// Specify the configuration items and data for the chart
var f1_option = {
// title: {
//     text: 'How much is enough',
//     textAlign: 'center',
//     left: '50%',
//     subtitle: 'By household composition'
// },
grid: {
    //top: 100,
    //height: 200,
    left: 220,
    right: 50,
    bottom: 0
},
tooltip: {
    valueFormatter: function (value) {
        return '£' + Math.ceil(value).toLocaleString() ;
      }
},
color: ['#0066CC', '#000000'],
legend: {
    data: ['Required Income', 'Including Expected Tax'],
    //top: 50,
    textStyle: {
      fontSize: 16
    }
},
xAxis: {
    splitLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false },
    axisLine: { show: false }
},
yAxis: {
    data: ['1 adult', '1 adult and 1 child', '2 adults', '2 adults and 1 child', '2 adults and 2 children', '2 adults and 3 children'],
    inverse: true,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
        margin: 30,
        fontSize: 16,
        overflow: 'break',
        align: 'right'
    },
    
},
series: [
    {
    name: 'Required Income',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['40%', '60%'],
    symbol: f1_pathSymbols.gbp_blue,
    data: f1_vars.base,
    stack: 'y',
    z: 2        
    },
    {
    name: 'Including Expected Tax',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['40%', '60%'],
    symbol: f1_pathSymbols.gbp_black,
    data: f1_vars.with_tax1,
    stack: 'y',
    label: f1_labelSetting,
    z: 1
    }
]
};

// Display the chart using the configuration items and data just specified.
f1_chart.setOption(f1_option);