const f4_vars = {{ d_dowe | safe }};
window.addEventListener('resize', function() {
  f4_chart.resize();
});

// Initialize the echarts instance based on the prepared dom
var f4_chart = echarts.init(document.getElementById('f4_chart'));  

const f4_labelSetting = {
    show: true,
    position: 'center',
    fontSize: 16,
    color: '#000000',
    textShadowColor: '#FFFFFF',
    textShadowBlur: 10,
    overflow: 'break',
    width: 150
  };
  
  const max_radius = 50;
    
  const set_radius = (val) => {
    let r = (val**0.5/f4_vars.uk_gdhi**0.5) * max_radius;
    return  r.toString() + '%'
  };
  
  f4_option = {
    // title: {
    //   text: 'Do we have enough?',
    //   left: 'center'
    // },
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br> £{c} billion',
    },
    series: [
      {
        name: 'Total UK Household Disposable Income',
        type: 'pie',
        radius: set_radius(f4_vars.uk_gdhi),
        center: ['20%', '50%'],
        data: [
          { value: Math.round(f4_vars.uk_gdhi/1e9), name: 'Total UK Household Disposable Income' }
        ],
        label: f4_labelSetting,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      },
      {
        name: 'Enough for Everyone',
        type: 'pie',
        radius: set_radius(f4_vars.enough_for_everyone),
        center: ['50%', '50%'],
        data: [
          { value: Math.round(f4_vars.enough_for_everyone/1e9), name: 'Enough for Everyone' }
        ],
        label: f4_labelSetting,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      },
      {
        name: 'Shortfall of those Without Enough',
        type: 'pie',
        radius: set_radius(f4_vars.deficit_without_enough),
        center: ['80%', '50%'],
        data: [
          { value: Math.round(f4_vars.deficit_without_enough/1e9), name: 'Shortfall of those Without Enough' }
        ],
        label: f4_labelSetting,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

// Display the chart using the configuration items and data just specified.
f4_chart.setOption(f4_option);