//const f5_vars = {{ f5 | safe }}

// Initialize the echarts instance based on the prepared dom
var f5_chart = echarts.init(document.getElementById('f5_chart'));  
const start_year = 2020;
const end_year = 2050;
var growth_pc = 2;

var x_data = [];
for (var i = start_year; i < end_year+1; i++) {
    x_data.push(i);
}

const y_fun = (start_val, growth_pc) => {
    let y = start_val;
    let y_data = [];
    for (var i = start_year; i < end_year+1; i++){
        y_data.push(y);
        y = y * (1 + growth_pc/100);
    }
    return y_data
}

const updateGrowth = (growth_pc) => {
    f5_option = {
        title: {
          text: 'Will growth give everyone enough?',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          //formatter: '{b}<br> {c}x',
          valueFormatter: (value) => value.toFixed(2) + 'x'
        },
        grid: {
          top: 30,
          height: 200,
          left: 50,
          right: 150
      },
        xAxis: {
          boundaryGap: false,
          data: x_data,
          axisLabel: {
            textStyle:{
              fontSize: 14,
              color: '#000000'
            }
          }
        },
        yAxis: {
          type: 'value',
          splitLine: { show: false },
          axisTick: { show: false },
          axisLine: { show: false },
          axisLabel: {show : false}
        },
        series: [
          {
            name: 'Top 10%',
            data: y_fun(7, growth_pc),
            type: 'line',
            endLabel: {
              show: true,
              formatter: '{a}',
              fontSize: 16
            }
          },
          {
            name: 'Typical household',
            data: y_fun(1.1, growth_pc),
            type: 'line',
            endLabel: {
              show: true,
              formatter: '{a}',
              fontSize: 16
            }
          },
          {
            name: 'Bottom 10%',
            data: y_fun(0.3, growth_pc),
            type: 'line',
            endLabel: {
              show: true,
              formatter: '{a}',
              fontSize: 16
            }
          },
          {
            name: 'Enough',
            data: y_fun(1, 0),
            type: 'line', 
            symbol: 'none',
            lineStyle: {
              type: 'dashed'
            },
            endLabel: {
              show: true,
              formatter: '{a}',
              fontSize: 16,
              offset: [-280, 0]
            }
          }
        ]
      };
    
    // Display the chart using the configuration items and data just specified.
    f5_chart.setOption(f5_option);
}

updateGrowth(growth_pc);