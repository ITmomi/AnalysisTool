export const VariationDefaultScript = (
  Plotly,
  element,
  global_adc_mea_data,
  obj,
) => {
  console.log('[VariationDefaultScript]obj', obj);
  const variation_data = global_adc_mea_data.variation;
  const variation_data_key = Object.keys(global_adc_mea_data.variation)[0];
  const paper_width = 1700;
  const paper_height = 1000;

  /* Make Data */
  const MakeVariationData = (
    variation_data,
    variation_data_key,
    paper_width,
    paper_height,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;

    // Define Layout
    let plotly_layout = {
      title: '',
      showlegend: false,
      width: 700,
      height: 350,
      margin: {
        autoexpand: true,
        b: 150,
        l: 50,
        r: 50,
        t: 50,
      },
      xaxis: {
        autorange: true,
        title: '',
        type: 'category',
      },
      yaxis: {
        autorange: true,
        title: '',
      },
      xaxis2: {
        autorange: true,
        title: '',
        type: 'category',
      },
      yaxis2: {
        autorange: true,
        title: {
          text: '(ppm)',
        },
      },
      grid: {
        columns: 2,
        rows: 1,
        pattern: 'independent', // independent, coupled
      },
      annotations: [],
    };

    /* Make Layout Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height = paper_height;

    /* Make Data */
    plotly_data_temp = MakeSubData(variation_data, 'rot', '');
    plotly_data.push(plotly_data_temp);
    plotly_layout['annotations'].push(MakeLayoutTitle('Plate Rot.', ''));

    plotly_data_temp = MakeSubData(variation_data, 'mag', '2');
    plotly_data.push(plotly_data_temp);
    plotly_layout['annotations'].push(MakeLayoutTitle('Plate Mag.', '2'));

    //console.log(plotly_data)
    //console.log(plotly_layout)
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };

  const MakeSubData = (variation_data, data_name, axis_index) => {
    let plotly_data_temp;

    // Define Data
    let g_datatemplate = {
      x: [],
      y: [],
      mode: 'markers',
      type: 'scatter',
      name: '',
      showlegend: false,
      marker: {
        color: 'rgb(70, 132, 180)',
      },
    };

    plotly_data_temp = Object.assign({}, g_datatemplate);
    for (let x_name in variation_data.plate_num) {
      plotly_data_temp.x.push(x_name);
      plotly_data_temp.y.push(variation_data.plate_num[x_name][data_name]);
      plotly_data_temp['xaxis'] = 'x' + axis_index;
      plotly_data_temp['yaxis'] = 'y' + axis_index;
    }
    return plotly_data_temp;
  };

  /* Make Each Annotation(Title) to Layout */
  const MakeLayoutTitle = (title, axis_index) => {
    let annotation_layout = {};
    annotation_layout['text'] = title;
    annotation_layout['x'] = 0.5;
    annotation_layout['y'] = 1.1;
    annotation_layout['xref'] = 'x' + axis_index + ' domain';
    annotation_layout['yref'] = 'y' + axis_index + ' domain';
    annotation_layout['showarrow'] = false;
    return annotation_layout;
  };
  MakeVariationData(
    variation_data,
    variation_data_key,
    paper_width,
    paper_height,
  );
};
