//const f5_vars = {{ d_whohas | safe }}

// Initialize the echarts instance based on the prepared dom
var f5_chart = echarts.init(document.getElementById('f5_chart'));  
window.addEventListener('resize', function() {
  f5_chart.resize();
});

const f5_labelSetting = {
    show: true,
    distance: 5,
    position: 'insideBottom',
    offset: [0, -240],
    fontSize: 14,
    color: '#000000',
    formatter: function (params) {
      return params.value.toFixed(2) + 'x' ;
    },
  };

var decile_data = f3_vars.pc_enough_by_decile.slice();
var year = 2023;
var growth_rate = 1.02;

const update_data = () => {
  for (var i=0; i<10; i++ ){
    decile_data[i] = decile_data[i] * growth_rate;
  }
  year += 1;
  if (year > 2050){
    decile_data = f3_vars.pc_enough_by_decile.slice();
    year = 2023;
  }
  return decile_data
}

// Specify the configuration items and data for the chart
var f5_option = {
title: {
    text: year,
    textAlign: 'center',
    left: '50%',
    // subtext: '\n\n\n\n' + year,
    // subtextStyle: {
    //   fontSize: 16,
    //   color: '#DC3545'
    // }
},
grid: {
  top: 60,
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
    axisTick: { show: false },
    max: 7
},
series: [
    {
    name: 'Fraction of enough',
    type: 'bar',
    data: decile_data,
    label: f5_labelSetting,
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

function beginTransition(){
  thisInterval = setInterval(() => {
    f5_chart.setOption({
      title: {
        text: year
      },
      series: {
        data: update_data()
      }
    });
  }, 500);
  return thisInterval
}
var myInterval;

function update_growth(value_str){
  //clearInterval(myInterval);
  growth_rate = 1 + parseFloat(value_str)/100;
  year = 2051;
  //myInterval = beginTransition();
}

const update_growth_label = (value_str) => {
  document.getElementById("growthPCRangeLabel").innerHTML = "Growth percent: " + value_str + "%";
};

f5_chart.setOption(f5_option);
myInterval = beginTransition();

document.getElementById("growthPCRange").setAttribute("onchange", "update_growth(this.value)");
document.getElementById("growthPCRange").setAttribute("oninput", "update_growth_label(this.value)");