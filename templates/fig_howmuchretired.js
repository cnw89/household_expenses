//const f1_vars = {{ d_howmuch | safe }}

// Initialize the echarts instance based on the prepared dom
var f1b_chart = echarts.init(document.getElementById('f1b_chart'));  
window.addEventListener('resize', function() {
    f1b_chart.resize();
  });

// const f1_pathSymbols = {
//     gbp_black : 'image://{{ url_for('static', filename='img/gbp1.svg') }}',
//     gbp_blue : 'image://{{ url_for('static', filename='img/gbp2.svg') }}'
// }

// const f1_labelSetting = {
//     show: true,
//     position: 'right',
//     offset: [5, 0],
//     fontSize: 16,
//     formatter: function (params) {
//       return '£' + Math.ceil(params.value).toLocaleString() ;
//     },
//   };

// Specify the configuration items and data for the chart
var f1b_option = {
// title: {
//     text: 'How much is enough',
//     textAlign: 'center',
//     left: '50%',
//     subtitle: 'By household composition'
// },
grid: {
    //top: 100,
    //height: 200,
    top: 50,
    left: 130,
    right: 70,
    bottom: 0
},
tooltip: {
    valueFormatter: function (value) {
        return '£' + Math.ceil(value).toLocaleString() ;
      }
},
color: ['#0066CC', '#000000'],
legend: {
    data: ['Covered by State Pension', 'Including Private Pension'],
    //top: 50,
    textStyle: {
      fontSize: 16
    }
},
xAxis: {
    splitLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false },
    axisLine: { show: false },
    max: f1_vars.with_tax1.slice(-1)
},
yAxis: {
    data: ['1 adult\n(retired)', '2 adults\n(retired)'],
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
    name: 'Covered by State Pension',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['40%', '60%'],
    symbol: f1_pathSymbols.gbp_blue,
    data: f1_vars.state_pension,
    stack: 'y',
    z: 2        
    },
    {
    name: 'Including Private Pension',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['40%', '60%'],
    symbol: f1_pathSymbols.gbp_black,
    data: f1_vars.base_retired,
    stack: 'y',
    label: f1_labelSetting,
    z: 1
    }
]
};

// Display the chart using the configuration items and data just specified.
f1b_chart.setOption(f1b_option);