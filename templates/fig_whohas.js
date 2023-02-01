//const f3_vars = {{ d_whohas | safe }}

// Initialize the echarts instance based on the prepared dom
var f3_chart = echarts.init(document.getElementById('f3_chart'));  
window.addEventListener('resize', function() {
  f3_chart.resize();
});

const f3_labelSetting = {
    show: true,
    distance: 5,
    position: 'insideBottom',
    offset: [0, -270],
    fontSize: 14,
    color: '#000000',
    formatter: function (params) {
      return params.value.toFixed(2) + 'x' ;
    },
  };

// Specify the configuration items and data for the chart
var f3_option = {
// title: {
//     text: 'What fraction of enough do UK residents have?',
//     textAlign: 'center',
//     left: '50%'
// },
grid: {
    //top: 60,
    //height: 200,
    //width: 500,
    top: 0,
    bottom: 100,
    left: 70,
    right: 0
},
tooltip: {
    valueFormatter: function (value) {
        return value.toFixed(2) + 'x' ;
      }
},
//color: ['#0066CC', '#000000']
xAxis: {
    data: ['Bottom 10%', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', 'Top 10%'],
    splitLine: { show: false },
    axisTick: { show: false },
    axisLine: { show: false },
    axisLabel: {
        margin: 20,
        fontSize: 14,
        color: '#000000',
        align: 'center',
        overflow: 'break',
        interval: 0,
        width: 55
    },
    name: 'Non-retired UK residents by disposable income decile',
    nameLocation: 'center',
    nameTextStyle: {
      fontSize: 16,
      color: '#000000'
    },
    nameGap: 60
},
yAxis: {
    axisLine: { show: false },
    splitLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false }
},
series: [
    {
    name: 'Fraction of enough',
    type: 'bar',
    data: f3_vars.pc_enough_by_decile,
    label: f3_labelSetting,
    markLine: {
        symbol: 'none',
        label: {
          formatter: 'Enough',
          position: 'start',
          fontSize: 16
        },
        lineStyle: {
          color: 'green',
          type: 'dashed',
          width: 3
        },
        data: [
          {
            yAxis: 1
          }
        ]
      },
    z: 1        
    }
]
};

// Display the chart using the configuration items and data just specified.
f3_chart.setOption(f3_option);