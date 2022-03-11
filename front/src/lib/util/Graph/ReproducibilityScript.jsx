export const ReproducibilityDefaultScript = (
  Plotly,
  element,
  global_adc_mea_data,
  Obj,
) => {
  console.log('[ReproducibilityDefaultScript]obj', Obj);
  const reprod_data = global_adc_mea_data.reproducibility;
  const paper_width = parseFloat(Obj.screen_width); //1700
  const paper_height = parseFloat(Obj.screen_height); //1000
  const title = Obj.title; //"3σ_x"
  const upper_limit = parseFloat(Obj.upper_limit); //300
  const disp_name = Obj.disp_name; //"x"

  /* Make Data */
  const MakeReprodData = (
    reprod_data,
    paper_width,
    paper_height,
    title,
    upper_limit,
  ) => {
    let plotly_data = [];

    // Define Data
    let g_datatemplate = {
      x: [],
      y: [],
      type: 'bar',
      name: '',
      showlegend: false,
      marker: {
        color: 'rgb(70, 132, 180)',
      },
    };

    // Define Layout
    let plotly_layout = {
      title: '',
      showlegend: false,
      width: 700,
      height: 350,
      margin: {
        autoexpand: false,
        b: 50,
        l: 50,
        r: 50,
        t: 50,
      },
      xaxis: {
        autorange: true,
        title: '',
      },
      yaxis: {
        autorange: false,
        range: [0, 0],
        title: {
          text: '[um]',
          orientation: 'h',
        },
      },
      //annotations: []
    };

    /* Make Title */
    plotly_layout['title'] = title;

    /* Make Layout Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height = paper_height;

    /* Make Limit */
    if (upper_limit) {
      plotly_layout.yaxis.range[1] = upper_limit;
    } else {
      plotly_layout.yaxis.autorange = true;
    }

    /* Make Data */
    for (let x_name in reprod_data) {
      g_datatemplate.x.push(x_name);
      g_datatemplate.y.push(reprod_data[x_name]);
    }
    plotly_data.push(g_datatemplate);

    //console.log(plotly_data)
    //console.log(plotly_layout)
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };
  MakeReprodData(
    reprod_data[disp_name],
    paper_width,
    paper_height,
    title,
    upper_limit,
  );
};
