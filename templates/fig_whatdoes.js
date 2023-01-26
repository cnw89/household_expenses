const f2_vars = {{ f1 | safe }}
var f2_chart = echarts.init(document.getElementById('f2_chart')); 


var nWorkers = 1;
const STANDARD_HOURS = 37.5;
var hours = STANDARD_HOURS;
const MIN_WAGE = 10.4;
var wage = MIN_WAGE;
const WEEKS_IN_YEAR = 52;

function generate_wage_data() {

    if (nWorkers == 1) {
        var total_required = f2_vars.with_tax1;
    }
    else {
        var total_required = f2_vars.with_tax2;
    }

    let required_wage = [];
    for (var i = 0; i < total_required.length; i++) {
        required_wage.push(total_required[i] / (WEEKS_IN_YEAR * hours));
    }
    return required_wage;
}

function generate_hours_data() {

    if (nWorkers == 1) {
        var total_required = f2_vars.with_tax1;
    }
    else {
        var total_required = f2_vars.with_tax2;
    }

    let required_hours = [];
    for (var i = 0; i < total_required.length; i++) {
        required_hours.push(total_required[i] / (WEEKS_IN_YEAR * wage));
    }
    return required_hours;
}

const f2_symbols = {
    gbp_black : 'image://{{ url_for('static', filename='img/gbp1.svg') }}',
    gbp_blue : 'image://{{ url_for('static', filename='img/gbp2.svg') }}',
    clock : 'image://{{ url_for('static', filename='img/clock.svg') }}'
};

const f2wage_labelSetting = {
    show: true,
    position: 'right',
    offset: [5, 0],
    fontSize: 16,
    formatter: function (params) {
      return '£' + params.value.toFixed(2) + '/hour' ;
    },
  };

  const f2hours_labelSetting = {
    show: true,
    position: 'right',
    offset: [5, 0],
    fontSize: 16,
    formatter: function (params) {
      return params.value.toFixed(1) + ' hours' ;
    },
  };
  

// Specify the configuration items and data for the chart
function make_wage_option(){
    var option = {
        tooltip: {
            valueFormatter: function (value) {
                return '£' + value.toFixed(2) + '/hour';
              }
        },
        series: [
            {
            name: 'Required Wage',
            type: 'pictorialBar',
            symbolRepeat: true,
            symbolClip: true,
            symbolSize: ['40%', '60%'],
            symbol: f2_symbols.gbp_black,
            data: generate_wage_data(),
            label: f2wage_labelSetting,
            z: 2        
            }
        ]
        };
    return option
}
        
function make_hours_option(){
    // Specify the configuration items and data for the chart
    var option = {
        title: {
            text: 'What it takes to earn enough',
            textAlign: 'center',
            left: '50%'
        },
        grid: {
            top: 50,
            height: 200,
            left: 220,
            right: 130
        },
        tooltip: {
            valueFormatter: function (value) {
                return value.toFixed(1) + ' hours';
                }
        },
        color: ['#0066CC', '#000000'],
        
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
        name: 'Required Hours',
        type: 'pictorialBar',
        symbolRepeat: true,
        symbolClip: true,
        symbolSize: ['60%', '60%'],
        symbol: f2_symbols.clock,
        data: generate_hours_data(),
        label: f2hours_labelSetting,
        z: 2        
        }
    ]
    };
    return option
}

const wageHoursSwitchLabelValues = ["Fixed wage", "Fixed hours"];
const nWorkersLabelValues = ["One worker per household", "Two workers per household (where present), earning equally"];
const hoursOrWageRangeLabelValues = ["Wage (per hour): £", "Hours worked per week: "];

function update_hoursOrWageRangeLabel(){
    let range = document.getElementById("hoursOrWageRange");
    let range_label = document.getElementById("hoursOrWageRangeLabel");

    if (document.getElementById("wageHoursSwitch").checked) {        
        
        range_label.innerHTML = hoursOrWageRangeLabelValues[1] + range.value;
    } else {
        
        range_label.innerHTML = hoursOrWageRangeLabelValues[0] + range.value + "0";
    }
}

function switch_hoursOrWageRange(iswage, do_update_range) {
    var range = document.getElementById("hoursOrWageRange");
    var range_label = document.getElementById("hoursOrWageRangeLabel");

    if (iswage) {
        
        if (do_update_range){
            range.setAttribute("min", "4.0");
            range.setAttribute("max", "80.0");
            range.setAttribute("value", STANDARD_HOURS.toString());
            range.value = STANDARD_HOURS.toString();
        }        

        range_label.innerHTML = hoursOrWageRangeLabelValues[1] + range.value;

    } else {
        if (do_update_range){
            range.setAttribute("min", "3.0");
            range.setAttribute("max", "30.0");
            range.setAttribute("value", MIN_WAGE.toString());
            range.value = MIN_WAGE.toString();
        }

        range_label.innerHTML = hoursOrWageRangeLabelValues[0] + range.value + "0";        
    }
}

function update_f2(do_update_range) {
    
    switch_hoursOrWageRange(document.getElementById("wageHoursSwitch").checked, do_update_range);

    if (document.getElementById("nWorkersSwitch").checked){
        nWorkers = 2;
        document.getElementById("nWorkersSwitchLabel").innerHTML = nWorkersLabelValues[1];
    } else {
        nWorkers = 1;
        document.getElementById("nWorkersSwitchLabel").innerHTML = nWorkersLabelValues[0];
    }

    if (document.getElementById("wageHoursSwitch").checked){
        
        hours = parseFloat(document.getElementById("hoursOrWageRange").value);
        wage = MIN_WAGE;

        f2_chart.setOption(make_wage_option());
        document.getElementById("wageHoursSwitchLabel").innerHTML = wageHoursSwitchLabelValues[1];
    }else {
        
        wage = parseFloat(document.getElementById("hoursOrWageRange").value);
        hours = STANDARD_HOURS;

        f2_chart.setOption(make_hours_option());
        document.getElementById("wageHoursSwitchLabel").innerHTML = wageHoursSwitchLabelValues[0];        
    }


}

document.getElementById("wageHoursSwitch").setAttribute("onchange", "update_f2(true)");
document.getElementById("nWorkersSwitch").setAttribute("onchange", "update_f2(false)");
document.getElementById("hoursOrWageRange").setAttribute("onchange", "update_f2(false)");
document.getElementById("hoursOrWageRange").setAttribute("oninput", "update_hoursOrWageRangeLabel()");

update_f2(true);