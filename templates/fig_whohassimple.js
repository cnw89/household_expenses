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


const format_subtext = () =>{
  let subtext_str = parseInt(100 - f3_vars.pc_individuals_without_enough) + "% of non-retired UK residents have more than enough,\n" 
  + parseInt(f3_vars.pc_individuals_without_enough) + "% of non-retired UK residents do not have enough";
  return subtext_str
};

var f3a_option = {
// title: {
//     text: format_subtext(),
//     textAlign: 'center',
//     left: '50%'
//     // subtext: format_subtext(),
//     // subtextStyle: {
//     //   fontSize: 16
//     //}
// },
legend: {
    data: ['UK non-retired residents without enough', 'UK non-retired residents with enough'],
    //top: 50,
    textStyle: {
      fontSize: 16
    }
},
grid: {
    top: 0,//"50%",
    //height: 200,
    left: 0,
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
    data: [1],
    splitLine: { show: false },
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {show: false },
    
},
series: [
    {
    name: 'UK non-retired residents without enough',
    type: 'pictorialBar',
    symbolRepeat: true,
    symbolClip: true,
    symbolSize: ['15%', '35%'],
    symbol: f3a_pathSymbols.person_red,
    data: [f3_vars.pc_individuals_without_enough],    
    z: 2     
    },
    {
    name: 'UK non-retired residents with enough',
    type: 'pictorialBar',
    symbolRepeat: 'fixed',
    symbolSize: ['15%', '35%'],
    symbol: f3a_pathSymbols.person_green,
    data: [100],    
    z: 1  
    }
]
};


// Display the chart using the configuration items and data just specified.
f3a_chart.setOption(f3a_option);