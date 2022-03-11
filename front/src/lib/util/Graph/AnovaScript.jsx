export const AnovaDefaultScript = (
  Plotly,
  element,
  global_adc_mea_data,
  obj,
) => {
  console.log('[AnovaDefaultScript]obj', obj);

  const anova_data = global_adc_mea_data.anova;
  const paper_width = parseFloat(obj.screen_width); //1700
  const paper_height = parseFloat(obj.screen_height); //1000
  const disp_val = obj.disp_name; //"X"

  /* Make Data */
  const MakeAnovaData = (anova_data, paper_width, paper_height, disp_val) => {
    let plotly_data = [];
    let plotly_data_temp;

    // Define Layout
    let plotly_layout = {
      width: 0,
      height: 0,
      legend: {
        orientation: 'h',
        x: 0.5,
        y: 1.1,
        xanchor: 'center',
        //traceorder:"reversed"
      },
      barmode: 'stack',
      xaxis: {
        title: 'Variance[nm2]',
      },
    };

    /* Make Layout Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height = paper_height;

    /* Make Data */
    plotly_data_temp = MakeAnovaXYData(anova_data[disp_val]);
    for (let x of plotly_data_temp) plotly_data.push(x);

    //console.log("plotly_data")
    //console.log(plotly_data)
    //console.log("plotly_layout")
    //console.log(plotly_layout)
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };

  /* Make anova X or Y */
  const MakeAnovaXYData = (anova_data_xy) => {
    let plotly_data = [];
    let plotly_data_temp;
    let sub_name1,
      sub_name1_array = [],
      sub_name2_array = [];

    for (sub_name1 in anova_data_xy) {
      if (sub_name1 != 'sum') {
        sub_name1_array.push(sub_name1);
      }
    }
    for (let sub_name2 in anova_data_xy[sub_name1]) {
      if (sub_name2 != 'sum') {
        sub_name2_array.push(sub_name2);
      }
    }

    for (let i = 0; i < sub_name2_array.length; i++) {
      plotly_data_temp = MakeAnovaXYDataSub(
        anova_data_xy,
        sub_name2_array[i],
        sub_name1_array.reverse(),
      );
      plotly_data.push(plotly_data_temp);
    }
    return plotly_data;
  };

  /* Make anova data */
  const MakeAnovaXYDataSub = (anova_data_xy, sub_name2, sub_name1_array) => {
    // Define Data
    let g_datatemplate = {
      x: [],
      y: [],
      type: 'bar',
      name: '',
      orientation: 'h',
    };
    let tempdata = Object.assign({}, g_datatemplate);

    tempdata.name = sub_name2;
    for (let i = 0; i < sub_name1_array.length; i++) {
      let sub_name1 = sub_name1_array[i];
      tempdata.x.push(anova_data_xy[sub_name1][sub_name2]);
      tempdata.y.push(sub_name1);
    }
    return tempdata;
  };
  const div = document.getElementById(element);
  if (anova_data ?? false) {
    div.setAttribute('style', 'display:contents;');
  } else {
    div.setAttribute('style', 'display:none;');
    return;
  }
  MakeAnovaData(anova_data, paper_width, paper_height, disp_val);
};
