const f6_vars = {{ d_willgrowth | tojson }}

// Initialize the echarts instance based on the prepared dom
var f6_chart = echarts.init(document.getElementById('f6_chart'));  
window.addEventListener('resize', function() {
  f6_chart.resize();
});

const f6_labelSetting = {
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
var f6_option = {
// title: {
//     text: 'What fraction of enough do UK citizens have?',
//     textAlign: 'center',
//     left: '50%'
// },
grid: {
    //top: 60,
    //height: 200,
    //width: 500,
    top: 0,
    bottom: 100,
    left: 80,
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
    name: 'Non-retired UK citizens by disposable income decile',
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
    data: f6_vars.pc_enough_post_tax_by_decile,
    label: f6_labelSetting,
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
    stack: 'y',
    z: 2        
    },
    {
    name: 'Excess',
    type: 'bar',
    data: f6_vars.taxed,
    color: 'red',    
    markLine: {        
        symbol: 'none',
        label: {
          {% if d_willgrowth.tax_thresh_ratio is eq(1) %}show: false, {% endif %}
            formatter: 'Excess',
            position: 'start',
            fontSize: 16
        },
        lineStyle: {
            color: 'red',
            type: 'dashed',
            width: 3
        },
        data: [
            {
            yAxis: f6_vars.tax_thresh_ratio
            }
        ]
        },
    stack: 'y',
    z: 1        
    },
    {
    name: 'Shortfall',
    type: 'bar',
    color: 'green',
    data: f6_vars.credited,      
    stack: 'y',
    z: 1        
    }
]
};

// Display the chart using the configuration items and data just specified.
f6_chart.setOption(f6_option);