export const BaraDefaultScript = (
  Plotly,
  element,
  global_adc_mea_data,
  obj,
) => {
  console.log('[BaraDefaultScript]obj', obj);

  const all_lot_data = global_adc_mea_data.data;
  const paper_width = 1700;

  const select_shot = Array.isArray(obj.select_shot)
    ? obj.select_shot
    : [obj.select_shot]; //["1","2","3","4","5","6"]
  const shot_col_count = Array.isArray(obj.select_shot) ? 3 : 1;
  const shot_row_count = Array.isArray(obj.select_shot)
    ? parseInt(Math.ceil(obj.select_shot.length / 3))
    : 1;

  // const select_shot = ["5"]
  // const shot_col_count = 1
  // const shot_row_count = 1

  const title = 'Unit X:[um],Y:[um]';

  // Make Lot Color Table
  const color_table = [
    'rgb(255, 0, 0)',
    'rgb(0, 255, 0)',
    'rgb(0, 0, 255)',
    'rgb(127, 127, 0)',
    'rgb(0, 127, 127)',
    'rgb(127, 0, 127)',
    'rgb(127, 127, 127)',
  ];

  const x_range_min = parseFloat(obj.x_range_min); //0
  const x_range_max = parseFloat(obj.x_range_max); //0
  const y_range_min = parseFloat(obj.y_range_min); //0
  const y_range_max = parseFloat(obj.y_range_max); //0

  let first_legend_display = true;

  /* All Lot Data */
  const MakeLotData = (
    all_lot_data,
    paper_width,
    title,
    select_shot,
    color_table,
    x_range_min,
    x_range_max,
    y_range_min,
    y_range_max,
    shot_col_count,
    shot_row_count,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;
    let plate_data;

    // Define Layout
    let plotly_layout = {
      title: {
        text: '',
        x: 0.02,
        font: {
          size: 11,
        },
      },
      //showlegend:false,
      legend: {
        x: 0.5,
        xanchor: 'center',
        xref: 'paper',
        y: 1.035,
        yanchor: 'top',
        yref: 'paper',
        orientation: 'h',
        bgcolor: '#efefef',
      },
      width: 0,
      height: 0,
      margin: {
        autoexpand: false,
        b: 50,
        l: 70,
        r: 50,
        t: 70,
      },
      hoverlabel: {
        bgcolor: '#fff',
      },
      annotations: [],
    };
    let axis_index, graph_index_start;
    // const px_name_all = ["P1","P2","P3"]

    /* Make Lot Title */
    plotly_layout['title'].text = title;
    if (select_shot.length == 1) {
      shot_col_count = 1;
      shot_row_count = 1;
      plotly_layout.legend.y = 1.025;
    }

    graph_index_start = select_shot.length + 1;

    /* Set Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height =
      (paper_width / (shot_col_count * 2)) * (3 * shot_row_count);

    /* Get Each Inner Graph Area */
    let x_domain_list = GetXDomainList(shot_col_count);
    let y_domain_list = GetYDomainList(shot_row_count);

    /* Make All Shot Out Box */
    plotly_data_temp = MakeAllShotBox(
      plotly_layout,
      select_shot,
      x_domain_list,
      y_domain_list,
      shot_col_count,
      shot_row_count,
    );
    for (let x of plotly_data_temp) plotly_data.push(x);

    /* Make All Lot Graph Data */
    let lot_index = 0;
    for (let lot_name in all_lot_data) {
      axis_index = graph_index_start;
      plate_data = all_lot_data[lot_name].plate;
      plotly_data_temp = MakeAllShotData(
        lot_name,
        select_shot,
        plate_data,
        plotly_layout,
        axis_index,
        color_table[lot_index],
        x_domain_list,
        y_domain_list,
        shot_col_count,
        shot_row_count,
        x_range_min,
        x_range_max,
        y_range_min,
        y_range_max,
      );
      for (let x of plotly_data_temp) plotly_data.push(x);
      lot_index++;
    }

    //console.log(plotly_data)
    //console.log(plotly_layout)
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };

  /* Get Each Graph Area*/
  const GetXDomainList = (shot_col_count) => {
    let domain_list = [];
    let start_domain = 0;
    let shot_gap = 0.05,
      graph_gap = 0.005,
      outbox_gap = 0.005;
    let graph_acc_width =
      1 -
      ((shot_col_count - 1) * shot_gap +
        shot_col_count * graph_gap +
        outbox_gap * 2);
    let graph_width = graph_acc_width / (shot_col_count * 2);

    start_domain = outbox_gap;
    domain_list.push([start_domain, start_domain + graph_width]);
    for (let i = 0; i < shot_col_count; i++) {
      start_domain = start_domain + graph_width + graph_gap;
      domain_list.push([start_domain, start_domain + graph_width]);
      /* Do not make last shot gap */
      if (i !== shot_col_count - 1) {
        start_domain = start_domain + graph_width + shot_gap;
        domain_list.push([start_domain, start_domain + graph_width]);
      }
    }
    return domain_list;
  };

  const GetYDomainList = (shot_row_count) => {
    let domain_list = [];
    let start_domain = 0;
    let shot_gap = 0.05,
      graph_gap = 0.01,
      outbox_gap = 0.005;
    let graph_acc_width =
      1 -
      ((shot_row_count - 1) * shot_gap +
        shot_row_count * 2 * graph_gap +
        outbox_gap * 2);
    let graph_width = graph_acc_width / (shot_row_count * 3);

    start_domain = outbox_gap;
    domain_list.push([start_domain, start_domain + graph_width]);
    for (let i = 0; i < shot_row_count; i++) {
      start_domain = start_domain + graph_width + graph_gap;
      domain_list.push([start_domain, start_domain + graph_width]);
      start_domain = start_domain + graph_width + graph_gap;
      domain_list.push([start_domain, start_domain + graph_width]);

      /* Do not make last shot gap */
      if (i !== shot_row_count - 1) {
        start_domain = start_domain + graph_width + shot_gap;
        domain_list.push([start_domain, start_domain + graph_width]);
      }
    }

    let domain_list_tmp = domain_list.reverse();
    /*
  * Example : 3x2
  * [
    [        0.8450000000000001,        0.9950000000000001    ],
    [        0.685,        0.8350000000000001    ],
    [        0.525,        0.675    ],
    [        0.325,        0.475    ],
    [        0.165,        0.315    ],
    [        0.005,        0.155    ]
    ]
  * */
    return domain_list_tmp;
  };

  /* Make All shot data */
  const MakeAllShotData = (
    lot_name,
    select_shot,
    plate_data,
    plotly_layout,
    axis_index,
    color_val,
    x_domain_list,
    y_domain_list,
    shot_col_count,
    shot_row_count,
    x_range_min,
    x_range_max,
    y_range_min,
    y_range_max,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;
    let shot_index = 0;

    /* Make Each Shot data */
    for (let shot_row = 0; shot_row < shot_row_count; shot_row++) {
      if (shot_row % 2 == 0) {
        for (let shot_col = 0; shot_col < shot_col_count; shot_col++) {
          if (shot_index < select_shot.length) {
            plotly_data_temp = MakeShotData(
              lot_name,
              select_shot[shot_index],
              plate_data,
              plotly_layout,
              axis_index,
              color_val,
              x_domain_list,
              y_domain_list,
              shot_col,
              shot_row,
              x_range_min,
              x_range_max,
              y_range_min,
              y_range_max,
            );
            for (let x of plotly_data_temp) plotly_data.push(x);
            shot_index++;
            axis_index += 6;
          }
        }
      } else {
        for (let shot_col = shot_col_count - 1; shot_col >= 0; shot_col--) {
          if (shot_index < select_shot.length) {
            plotly_data_temp = MakeShotData(
              lot_name,
              select_shot[shot_index],
              plate_data,
              plotly_layout,
              axis_index,
              color_val,
              x_domain_list,
              y_domain_list,
              shot_col,
              shot_row,
              x_range_min,
              x_range_max,
              y_range_min,
              y_range_max,
            );
            for (let x of plotly_data_temp) plotly_data.push(x);
            shot_index++;
            axis_index += 6;
          }
        }
      }
    }
    return plotly_data;
  };

  /* Make each shot data */
  const MakeShotData = (
    lot_name,
    shot_name,
    plate_data,
    plotly_layout,
    axis_index,
    color_val,
    x_domain_list,
    y_domain_list,
    shot_col,
    shot_row,
    x_range_min,
    x_range_max,
    y_range_min,
    y_range_max,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;
    const px_name_all = ['P1', 'P2', 'P3'];
    let px_row_index = 0;

    for (let px_name of px_name_all) {
      plotly_data_temp = MakePxDataSub(
        lot_name,
        shot_name,
        px_name + 'L',
        plate_data,
        axis_index,
        color_val,
      );
      plotly_data.push(plotly_data_temp);
      MakeLayoutGraph(
        plotly_layout,
        axis_index,
        x_domain_list,
        y_domain_list,
        shot_col,
        shot_row,
        0,
        px_row_index,
        x_range_min,
        x_range_max,
        y_range_min,
        y_range_max,
      );
      MakeLayoutAnnotP123(
        plotly_layout,
        px_name,
        axis_index,
        x_domain_list,
        plotly_layout.width,
      );
      axis_index++;

      plotly_data_temp = MakePxDataSub(
        lot_name,
        shot_name,
        px_name + 'R',
        plate_data,
        axis_index,
        color_val,
      );
      plotly_data.push(plotly_data_temp);
      MakeLayoutGraph(
        plotly_layout,
        axis_index,
        x_domain_list,
        y_domain_list,
        shot_col,
        shot_row,
        1,
        px_row_index,
        x_range_min,
        x_range_max,
        y_range_min,
        y_range_max,
      );
      axis_index++;

      px_row_index++;
    }
    return plotly_data;
  };

  /* Make each graph P1L, P1R, P2L ... data */
  const MakePxDataSub = (
    lot_name,
    shot_name,
    pxx_data,
    plate_data,
    axis_index,
    color_val,
  ) => {
    let plotly_data = [];
    let outputdata = { x: [], y: [] };
    let g_base_datatemplate = {
      type: 'scatter',
      mode: 'markers',
      name: '',
      marker: {
        color: '',
      },
      showlegend: false,
    };

    if (first_legend_display) {
      g_base_datatemplate.showlegend = true;
      g_base_datatemplate.name = lot_name;
      first_legend_display = false;
    }
    g_base_datatemplate.marker.color = color_val;
    for (let plate_num in plate_data) {
      let tmp_x = plate_data[plate_num].shot[shot_name].measurement[pxx_data].x;
      let tmp_y = plate_data[plate_num].shot[shot_name].measurement[pxx_data].y;
      outputdata.x.push(tmp_x);
      outputdata.y.push(tmp_y);
    }
    outputdata['xaxis'] = 'x' + (axis_index == 1 ? '' : axis_index);
    outputdata['yaxis'] = 'y' + (axis_index == 1 ? '' : axis_index);
    plotly_data.push(Object.assign(outputdata, g_base_datatemplate));
    return plotly_data[0];
  };

  /* Make each graph layout data */
  const MakeLayoutGraph = (
    plotly_layout,
    axis_index,
    x_domain_list,
    y_domain_list,
    shot_col,
    shot_row,
    px_col_index,
    px_row_index,
    x_range_min,
    x_range_max,
    y_range_min,
    y_range_max,
  ) => {
    let g_layout_xaxis = {
      title: '',
      autorange: true,
      range: [],
      //dtick:50,
      //scaleratio : 0,
      showticklabels: true,
      tickfont: {
        size: 8,
      },
      ticklabelposition: 'inside',
      domain: [],
      mirror: true,
      showline: true,
      linewidth: 2,
    };

    let g_layout_yaxis = {
      title: '',
      autorange: true,
      range: [],
      //dtick:50,
      //scaleratio : 0,
      showticklabels: true,
      tickfont: {
        size: 8,
      },
      ticklabelposition: 'inside',
      domain: [],
      mirror: true,
      showline: true,
      linewidth: 1,
    };

    if (axis_index == 1) {
      axis_index = '';
    }
    plotly_layout['xaxis' + axis_index] = Object.assign({}, g_layout_xaxis);
    plotly_layout['xaxis' + axis_index]['anchor'] = 'y' + axis_index;
    //plotly_layout["xaxis"+axis_index]["scaleanchor"] = 'y'+axis_index_temp
    if (x_range_min != 0 || x_range_max != 0) {
      plotly_layout['xaxis' + axis_index]['autorange'] = false;
      plotly_layout['xaxis' + axis_index]['range'].push(x_range_min);
      plotly_layout['xaxis' + axis_index]['range'].push(x_range_max);
    }

    plotly_layout['yaxis' + axis_index] = Object.assign({}, g_layout_yaxis);
    plotly_layout['yaxis' + axis_index]['anchor'] = 'x' + axis_index;
    if (y_range_min != 0 || y_range_max != 0) {
      plotly_layout['yaxis' + axis_index]['autorange'] = false;
      plotly_layout['yaxis' + axis_index]['range'].push(y_range_min);
      plotly_layout['yaxis' + axis_index]['range'].push(y_range_max);
    }
    /* Make each graph domain(position) */
    plotly_layout['xaxis' + axis_index].domain.push(
      x_domain_list[shot_col * 2 + px_col_index][0],
    );
    plotly_layout['xaxis' + axis_index].domain.push(
      x_domain_list[shot_col * 2 + px_col_index][1],
    );
    plotly_layout['yaxis' + axis_index].domain.push(
      y_domain_list[shot_row * 3 + px_row_index][0],
    );
    plotly_layout['yaxis' + axis_index].domain.push(
      y_domain_list[shot_row * 3 + px_row_index][1],
    );
  };

  /* Make All P123 Annotation */
  const MakeLayoutAnnotP123 = (
    plotly_layout,
    px_name,
    axis_index,
    x_domain_list,
    paper_width,
  ) => {
    let graph_width_pixel =
      (x_domain_list[0][1] - x_domain_list[0][0]) * paper_width;
    let x_pos_ratio = -((50 - 10) / graph_width_pixel);
    let annot_template = {
      text: '',
      name: '',
      yref: '',
      xref: '',
      //xanchor:'left',
      yanchor: 'bottom',
      y: 0.5,
      x: 0,
      showarrow: false,
      font: { size: 16 },
    };
    let annot = Object.assign({}, annot_template);
    annot.text = px_name;
    annot.yref = 'y' + (axis_index == 1 ? '' : axis_index) + ' domain';
    annot.xref = 'x' + (axis_index == 1 ? '' : axis_index) + ' domain';
    annot.x = x_pos_ratio;
    plotly_layout.annotations.push(annot);
  };

  /* Make All Out Shot Box */
  const MakeAllShotBox = (
    plotly_layout,
    select_shot,
    x_domain_list,
    y_domain_list,
    shot_col_count,
    shot_row_count,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;

    /* Make Each Shot Out Box */
    plotly_data_temp = MakeShotBox(
      plotly_layout,
      select_shot.length,
      x_domain_list,
      y_domain_list,
      shot_col_count,
      shot_row_count,
    );
    for (let x of plotly_data_temp) plotly_data.push(x);

    /* Make All Shot Title */
    MakeLayoutAnnotShot(plotly_layout, select_shot);
    return plotly_data;
  };

  /* Make Each Out Shot Box */
  const MakeShotBox = (
    plotly_layout,
    box_total_count,
    x_domain_list,
    y_domain_list,
    shot_col_count,
    shot_row_count,
  ) => {
    let plotly_data = [];
    let shot_index, box_axis_index;

    /* Make Box Empty Data */
    for (
      box_axis_index = 1;
      box_axis_index <= box_total_count;
      box_axis_index++
    ) {
      plotly_data.push(MakeShotBoxSub(box_axis_index));
    }

    /* Make Box Domain(Position) */
    shot_index = 0;
    box_axis_index = 1;
    for (let shot_row = 0; shot_row < shot_row_count; shot_row++) {
      if (shot_row % 2 == 0) {
        for (let shot_col = 0; shot_col < shot_col_count; shot_col++) {
          if (shot_index < box_total_count) {
            MakeLayoutBox(
              plotly_layout,
              box_axis_index,
              x_domain_list,
              y_domain_list,
              shot_col,
              shot_row,
            );
            shot_index++;
            box_axis_index++;
          }
        }
      } else {
        for (let shot_col = shot_col_count - 1; shot_col >= 0; shot_col--) {
          if (shot_index < box_total_count) {
            MakeLayoutBox(
              plotly_layout,
              box_axis_index,
              x_domain_list,
              y_domain_list,
              shot_col,
              shot_row,
            );
            shot_index++;
            box_axis_index++;
          }
        }
      }
    }
    return plotly_data;
  };

  const MakeShotBoxSub = (box_axis_index) => {
    let g_base_datatemplate = {
      x: [],
      y: [],
      type: 'scatter',
      mode: 'markers',
      name: '',
    };
    g_base_datatemplate['xaxis'] =
      'x' + (box_axis_index == 1 ? '' : box_axis_index);
    g_base_datatemplate['yaxis'] =
      'y' + (box_axis_index == 1 ? '' : box_axis_index);
    return g_base_datatemplate;
  };

  /* Make Box Domain(Position) */
  const MakeLayoutBox = (
    plotly_layout,
    box_axis_index,
    x_domain_list,
    y_domain_list,
    shot_col,
    shot_row,
  ) => {
    let outbox_gap = 0.005;

    let g_layout_xaxis = {
      title: '',
      autorange: true,
      showticklabels: false,
      domain: [],
      mirror: true,
      showline: true,
      linewidth: 2,
      anchor: '',
      showgrid: false,
      zeroline: false,
    };

    let g_layout_yaxis = {
      title: '',
      autorange: true,
      showticklabels: false,
      domain: [],
      mirror: true,
      showline: true,
      linewidth: 2,
      anchor: '',
      showgrid: false,
      zeroline: false,
    };
    if (box_axis_index == 1) {
      box_axis_index = '';
    }
    plotly_layout['xaxis' + box_axis_index] = Object.assign({}, g_layout_xaxis);
    plotly_layout['xaxis' + box_axis_index]['anchor'] = 'y' + box_axis_index;
    //plotly_layout["xaxis"+box_axis_index]["scaleanchor"] = 'y'+axis_index_temp
    plotly_layout['yaxis' + box_axis_index] = Object.assign({}, g_layout_yaxis);
    plotly_layout['yaxis' + box_axis_index]['anchor'] = 'x' + box_axis_index;

    /* Position */
    plotly_layout['xaxis' + box_axis_index].domain.push(
      x_domain_list[shot_col * 2][0] - outbox_gap,
    );
    plotly_layout['xaxis' + box_axis_index].domain.push(
      x_domain_list[shot_col * 2 + 1][1] + outbox_gap,
    );
    plotly_layout['yaxis' + box_axis_index].domain.push(
      y_domain_list[shot_row * 3 + 2][0] - outbox_gap,
    );
    plotly_layout['yaxis' + box_axis_index].domain.push(
      y_domain_list[shot_row * 3][1] + outbox_gap,
    );
  };

  /* Make All Shot Title */
  const MakeLayoutAnnotShot = (plotly_layout, select_shot) => {
    //let shot_gap = 0.05, graph_gap = 0.01, outbox_gap = 0.005
    let y_pos_ratio = 1;
    for (let i = 0; i < select_shot.length; i++) {
      MakeLayoutAnnotShotSub(plotly_layout, select_shot[i], i + 1, y_pos_ratio);
    }
  };
  const MakeLayoutAnnotShotSub = (
    plotly_layout,
    shot_name,
    axis_index,
    y_pos_ratio,
  ) => {
    let annot_template = {
      text: '',
      name: '',
      yref: '',
      xref: '',
      //xanchor:'left',
      yanchor: 'bottom',
      y: 0,
      x: 0.5,
      showarrow: false,
      font: { size: 16 },
    };
    let annot = Object.assign({}, annot_template);
    annot.text = 'Shot ' + shot_name;
    annot.yref = 'y' + (axis_index == 1 ? '' : axis_index) + ' domain';
    annot.xref = 'x' + (axis_index == 1 ? '' : axis_index) + ' domain';
    annot.y = y_pos_ratio;
    plotly_layout.annotations.push(annot);
  };
  MakeLotData(
    all_lot_data,
    paper_width,
    title,
    select_shot,
    color_table,
    x_range_min,
    x_range_max,
    y_range_min,
    y_range_max,
    shot_col_count,
    shot_row_count,
  );
};
