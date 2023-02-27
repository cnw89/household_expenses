const f3_vars = {{ d_whohas | safe }};

// Initialize the echarts instance based on the prepared dom
var f3a_chart = echarts.init(document.getElementById('f3a_chart'));  
window.addEventListener('resize', function() {
    f3a_chart.resize();
  });

const f3a_pathSymbols = {
    person_red : 'image://{{ url_for('static', filename='img/person-red.svg') }}',
    person_green : 'image://{{ url_for('static', filename='img/person-green.svg') }}'
};

var f3a_option = {
legend: {
    data: ['UK citizens without enough', 'UK citizens with enough'],
    //top: 50,
    textStyle: {
      fontSize: 16
    },
    selectedMode: false
},
grid: {
    top: 50,//"50%",
    //height: 200,
    left: 150,
    right: 0,
    bottom: 0
},

xAxis: {
    splitLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false },
    axisLine: { show: false }
},
yAxis: {
    data: ["All citizens", "Non-retired", "Retired"],
    inverse: true,
    splitLine: { show: false },
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
        margin: 30,
        fontSize: 16,
        overflow: 'break',
        align: 'right'
    }    
},
series: [
    {
    name: 'UK citizens without enough',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['20%', '54%'],
    label: {
        show: true,
        formatter: function (params) {
          return params.value.toFixed(0) + ' %';
        },
        position: 'top',
        distance: 0,
        align: 'left',
        offset: [0, 10],        
        color: 'red',
        fontSize: 14
      },
    symbol: f3a_pathSymbols.person_red,
    data: [f3_vars.pc_individuals_without_enough_all, f3_vars.pc_individuals_without_enough_nonretired, f3_vars.pc_individuals_without_enough_retired],    
    barCategoryGap: "0%",
    z: 2     
    },
    {
    name: 'UK citizens with enough',
    type: 'pictorialBar',
    itemStyle: {
        opacity: 0.5
    },
    symbolRepeat: 'fixed',
    symbolSize: ['20%', '54%'],
    symbol: f3a_pathSymbols.person_green,
    data: [100, 100, 100],    
    barCategoryGap: "20%",
    z: 1  
    }
]
};


// Display the chart using the configuration items and data just specified.
f3a_chart.setOption(f3a_option);