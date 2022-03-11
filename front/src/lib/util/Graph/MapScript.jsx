export const MapDefaultScript = (Plotly, element, global_adc_mea_data, obj) => {
  console.log('[MapDefaultScript]obj', obj);

  const lot_name = obj.lot_name; //Object.keys(global_adc_mea_data.data)[0];
  const paper_width = 1700;
  const disp_start = parseInt(obj.display_map.min); //1
  const disp_end = parseInt(obj.display_map.max); //30
  const plate_width = parseFloat(obj.plate_size.size_x); //2500
  const plate_height = parseFloat(obj.plate_size.size_y); //2500
  const row = parseInt(obj.column_num); //4
  const upper_division = parseFloat(obj.div.div_upper); //0.001
  const show_extra_info = obj.show_extra_info;
  /* Each shot disp option */
  /* [firstshot, secondshot, ... ] each shot value : 0:P1&P2&P3, 1:P1&P2, 2:P2&P3, 3:P2only, 4:Non */
  const disp_option = obj.disp_option; //[0, 0, 0, 0, 0, 0];
  const shot_offset_info = obj.offset.info;

  /* Lot Data */
  const MakeMapData = (
    adc_mea_data,
    lot_name,
    paper_width,
    disp_start,
    disp_end,
    plate_width,
    plate_height,
    disp_columns,
    upper_division,
    show_extra_info,
    disp_option,
    shot_offset_info,
  ) => {
    let plotly_data = [];
    let plotly_data_temp;
    let plate_index = 1;

    let g_layout_xaxis = {
      title: '',
      autorange: false,
      range: [],
      dtick: 50,
      showticklabels: false,
      zeroline: false,
    };

    let g_layout_yaxis = {
      title: '',
      autorange: false,
      range: [],
      dtick: 50,
      showticklabels: false,
      zeroline: false,
    };

    let plotly_layout = {
      title: '',
      showlegend: false,
      width: 0,
      height: 0,
      margin: {
        autoexpand: false,
        b: 50,
        l: 50,
        r: 50,
        t: 50,
      },
      grid: {
        columns: 0,
        rows: 0,
        pattern: 'independent',
        xgap: 0.04,
        ygap: 0.15,
      },
      hoverlabel: {
        bgcolor: '#fff',
      },
      annotations: [],
    };

    let plate_box_data;
    let lot_data_inner = adc_mea_data.data[lot_name];
    let grid_columns, grid_rows;
    let plate_data = lot_data_inner.plate;
    let fix_plate_size_disp = false,
      show_tick = false;

    /* Make Plate Size and Range Set : Reverse */
    g_layout_xaxis.range.push(parseInt(plate_width / 2) + 10);
    g_layout_xaxis.range.push(0 - parseInt(plate_width / 2) - 10);
    g_layout_xaxis.showticklabels = show_tick;
    g_layout_yaxis.range.push(parseInt(plate_height / 2) + 10);
    g_layout_yaxis.range.push(0 - parseInt(plate_height / 2) - 10);
    g_layout_yaxis.showticklabels = show_tick;

    /* Make Plate Box Data */
    plate_box_data = MakePlateBoxData(plate_width, plate_height);

    let plate_first_num = 0;
    /* Make Layout Grid Col, Row */
    let plate_total = 0;
    for (let plate_num in plate_data) {
      if (
        parseInt(plate_num) >= disp_start &&
        parseInt(plate_num) <= disp_end
      ) {
        plate_total++;
        if (plate_first_num === 0) {
          plate_first_num = parseInt(plate_num);
        }
      }
    }
    const div = document.getElementById(element);
    if (plate_total === 0) {
      div.setAttribute('style', 'display:none;');
      return;
    } else {
      div.setAttribute('style', 'display:contents;');
    }

    if (plate_total <= disp_columns) {
      grid_columns = plate_total;
      grid_rows = 1;
    } else {
      grid_columns = disp_columns;
      grid_rows =
        parseInt(plate_total / disp_columns) +
        (plate_total % disp_columns === 0 ? 0 : 1);
    }
    plotly_layout.grid.columns = grid_columns;
    plotly_layout.grid.rows = grid_rows;

    /* Make Layout Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height =
      (paper_width / grid_columns) * grid_rows * (1 + grid_columns * 0.02);

    /* Make Lot Data */
    for (let plate_num in plate_data) {
      /* Make Plate Data */
      if (
        parseInt(plate_num) >= disp_start &&
        parseInt(plate_num) <= disp_end
      ) {
        plotly_data_temp = MakePlateData(
          plate_data[plate_num],
          plate_index,
          upper_division,
          disp_option,
          shot_offset_info,
        );
        for (let x of plotly_data_temp) plotly_data.push(x);

        /* Add Plate Box Data */
        plate_box_data = Object.assign({}, plate_box_data);
        plate_box_data['xaxis'] = 'x' + (plate_index === 1 ? '' : plate_index);
        plate_box_data['yaxis'] = 'y' + (plate_index === 1 ? '' : plate_index);
        plotly_data.push(plate_box_data);

        /* Add Layout Plate Ratio */
        plotly_layout = MakeLayoutPlateRatio(
          plotly_layout,
          g_layout_xaxis,
          g_layout_yaxis,
          plate_index,
          fix_plate_size_disp,
        );

        /* Add Each Plate Annotation(Title) to Layout */
        plotly_layout['annotations'].push(
          MakeLayoutPlateTitle(
            plate_data[plate_num]['glass_num'],
            plate_num,
            plate_index,
            g_layout_xaxis.range[0],
            g_layout_yaxis.range[1],
          ),
        );

        plate_index++;
      }
    }

    if (show_extra_info) {
      plotly_data = MakeThreeSigmaData(
        plotly_data,
        plate_data[plate_first_num],
        lot_data_inner.extra_info['3sigma_max'],
        shot_offset_info,
      );
    }

    // Plotly.newPlot(plolyRef.current, plotly_data, plotly_layout);
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };

  /* Plate Data */
  const MakePlateData = (
    plate_data,
    plate_index,
    upper_division,
    disp_option,
    shot_offset_info,
  ) => {
    let plotly_data = [];
    let shot_disp_index = 0;
    for (let shot in plate_data.shot) {
      MakeShotData(
        plotly_data,
        plate_data.shot[shot],
        shot,
        upper_division,
        disp_option[shot_disp_index],
        shot_offset_info,
      );
      shot_disp_index++;
    }
    /* Make matching xaxis, yaxis of plotly data*/
    for (let data of plotly_data) {
      data['xaxis'] = 'x' + (plate_index === 1 ? '' : plate_index);
      data['yaxis'] = 'y' + (plate_index === 1 ? '' : plate_index);
    }
    return plotly_data;
  };

  /* Shot Data */
  const MakeShotData = (
    plotly_data,
    shot_data,
    shot_no,
    upper_division,
    disp_option_shot,
    shot_offset_info,
  ) => {
    let base_data_return;
    let plotly_data_temp, base_x_point_values, base_y_point_values;
    for (let ele in shot_data) {
      if (ele === 'base') {
        base_data_return = MakeBaseData(
          shot_data[ele],
          shot_no,
          disp_option_shot,
          shot_offset_info,
        );
        plotly_data_temp = base_data_return.plotly_data;
        base_x_point_values = base_data_return.x_point_values;
        base_y_point_values = base_data_return.y_point_values;
        for (let x of plotly_data_temp) plotly_data.push(x);
      } else {
        plotly_data_temp = MakeMeasurementData(
          shot_data[ele],
          shot_no,
          base_x_point_values,
          base_y_point_values,
          50,
          upper_division,
          disp_option_shot,
        );
        for (let x of plotly_data_temp) plotly_data.push(x);
      }
    }
  };

  /* Base Data */
  const MakeBaseData = (
    value_data,
    shot_no,
    disp_option_shot,
    shot_offset_info,
  ) => {
    const g_base_datatemplate = {
      type: 'scatter',
      mode: 'lines',
      name: '',
      line: {
        dash: 'dashdot',
        color: 'rgb(0,0,0)',
        width: 2,
      },
      hoverinfo: 'text',
    };
    let plotly_data = [];
    let x_point_values = GetPointValues(value_data, 'x');
    let y_point_values = GetPointValues(value_data, 'y');
    for (let i = 0; i < x_point_values.length; i++) {
      x_point_values[i] =
        x_point_values[i] + parseFloat(shot_offset_info[shot_no].x);
    }
    for (let i = 0; i < y_point_values.length; i++) {
      y_point_values[i] =
        y_point_values[i] + parseFloat(shot_offset_info[shot_no].y);
    }
    plotly_data = MakeGridData(
      plotly_data,
      shot_no,
      x_point_values,
      y_point_values,
      x_point_values,
      y_point_values,
      g_base_datatemplate,
      disp_option_shot,
      true,
    );
    return { plotly_data, x_point_values, y_point_values };
  };

  /* Measurement Data */
  const MakeMeasurementData = (
    value_data,
    shot_no,
    base_x_point_values,
    base_y_point_values,
    interval_val,
    division_val,
    disp_option_shot,
  ) => {
    const g_measurement_datatemplate = {
      type: 'scatter',
      mode: 'lines',
      name: '',
      line: {
        color: 'rgb(255,0,0)',
        width: 2,
      },
      hoverinfo: 'text',
    };
    let plotly_data = [];
    let x_point_values, y_point_values;
    let x_point_values_measure = GetPointValues(value_data, 'x');
    let y_point_values_measure = GetPointValues(value_data, 'y');

    x_point_values = x_point_values_measure.map(function (obj, index) {
      return base_x_point_values[index] + obj * (interval_val / division_val);
    });
    y_point_values = y_point_values_measure.map(function (obj, index) {
      return base_y_point_values[index] + obj * (interval_val / division_val);
    });

    //   console.log("x_point_values_measure",x_point_values_measure);
    //   console.log("x_point_values",x_point_values);
    //   console.log("base_x_point_values",base_x_point_values);
    //   console.log("division_val",division_val);

    plotly_data = MakeGridData(
      plotly_data,
      shot_no,
      x_point_values,
      y_point_values,
      x_point_values_measure,
      y_point_values_measure,
      g_measurement_datatemplate,
      disp_option_shot,
      true,
    );
    return plotly_data;
  };

  /* Make X,Y Point List [...]   Order by global_point_order */
  const GetPointValues = (value_data, axis_name) => {
    const g_point_order = ['P3L', 'P2L', 'P1L', 'P3R', 'P2R', 'P1R'];
    let point_values = g_point_order.reduce((acc, cur) => {
      acc.push(value_data[cur][axis_name]);
      return acc;
    }, []);
    return point_values;
  };

  /* Make Grid Data */
  const MakeGridData = (
    plotly_data,
    shot_no,
    x_point_values,
    y_point_values,
    x_hover_values,
    y_hover_values,
    data_template,
    disp_option_shot,
    show_tool_tip,
  ) => {
    let hovertext;
    const x_point_max = 2,
      y_point_max = 3;
    let outputdata;

    /* Non Case : Speed Up */
    if (disp_option_shot === 4) {
      return plotly_data;
    }

    for (let col = 0; col < x_point_max; col++) {
      if (show_tool_tip) {
        outputdata = { x: [], y: [], text: [] };
      } else {
        outputdata = { x: [], y: [], text: '' };
      }
      let filtered = GetColumnsFilter(
        col,
        x_point_max,
        y_point_max,
        x_point_values.length,
      );
      for (let idx of filtered) {
        if (!GetDispIdxCol(idx, disp_option_shot)) {
          continue;
        }
        outputdata.x.push(x_point_values[idx]);
        outputdata.y.push(y_point_values[idx]);
        if (show_tool_tip) {
          hovertext =
            'ShotNo:' +
            shot_no +
            '<br>(' +
            x_hover_values[idx] +
            ', ' +
            y_hover_values[idx] +
            ')';
          outputdata.text.push(hovertext);
        }
      }
      plotly_data.push(Object.assign(outputdata, data_template));
    }

    for (let row = 0; row < y_point_max; row++) {
      if (show_tool_tip) {
        outputdata = { x: [], y: [], text: [] };
      } else {
        outputdata = { x: [], y: [], text: '' };
      }
      let filtered = GetRowsFilter(
        row,
        x_point_max,
        y_point_max,
        x_point_values.length,
      );
      for (let idx of filtered) {
        if (!GetDispIdxRow(idx, disp_option_shot)) {
          continue;
        }
        outputdata.x.push(x_point_values[idx]);
        outputdata.y.push(y_point_values[idx]);
        if (show_tool_tip) {
          hovertext =
            'ShotNo:' +
            shot_no +
            '<br>(' +
            x_hover_values[idx] +
            ', ' +
            y_hover_values[idx] +
            ')';
          outputdata.text.push(hovertext);
        }
      }
      plotly_data.push(Object.assign(outputdata, data_template));
    }
    return plotly_data;
  };

  /* Get Columns : [0,1,2], [3,4,5] */
  const GetColumnsFilter = (
    col,
    x_point_max,
    y_point_max,
    x_point_values_length,
  ) => {
    const arr = Array.from(
      { length: x_point_values_length },
      (_, index) => index,
    );
    const filtered = arr.filter((value, index) => {
      if (index >= y_point_max * col && index < y_point_max * (col + 1)) {
        return true;
      }
      return false;
    });
    return filtered;
  };

  /* Get Rows : [0,3], [1,4], [2,5] */
  const GetRowsFilter = (
    row,
    x_point_max,
    y_point_max,
    x_point_values_length,
  ) => {
    const arr = Array.from(
      { length: x_point_values_length },
      (_, index) => index,
    );
    const filtered = arr.filter((value, index) => {
      for (
        let tmpidx = row;
        tmpidx < x_point_values_length;
        tmpidx = tmpidx + y_point_max
      ) {
        if (index === tmpidx) {
          return true;
        }
      }
      return false;
    });
    return filtered;
  };

  /* Get Disp Flag for DispOption
    Grid idx is below :
    2|  |5
    1|  |4
    0|  |3
    */
  const GetDispIdxCol = (idx, disp_option_shot) => {
    if (disp_option_shot === 0) {
      return true;
    } else if (disp_option_shot === 1) {
      if (idx === 0 || idx === 3) {
        return false;
      }
      return true;
    } else if (disp_option_shot === 2) {
      if (idx === 2 || idx === 5) {
        return false;
      }
      return true;
    } else if (disp_option_shot === 3) {
      if (idx === 1 || idx === 4) {
        return true;
      }
      return false;
    } else {
      return false;
    }
  };

  const GetDispIdxRow = (idx, disp_option_shot) => {
    if (disp_option_shot === 0) {
      return true;
    } else if (disp_option_shot === 1) {
      if (idx === 0 || idx === 3) {
        return false;
      }
      return true;
    } else if (disp_option_shot === 2) {
      if (idx === 2 || idx === 5) {
        return false;
      }
      return true;
    } else if (disp_option_shot === 3) {
      if (idx === 1 || idx === 4) {
        return true;
      }
      return false;
    } else {
      return false;
    }
  };

  /* Make Each Plate Annotation(Title) to Layout */
  const MakeLayoutPlateTitle = (
    glass_num,
    plate_num,
    plate_index,
    x_position_val,
    y_position_val,
  ) => {
    let plate_annotation_layout = {};
    plate_annotation_layout['text'] =
      'Glass:' + glass_num + '<br>Plate:' + plate_num;
    plate_annotation_layout['align'] = 'left';
    plate_annotation_layout['x'] = x_position_val;
    plate_annotation_layout['y'] = y_position_val;
    plate_annotation_layout['xanchor'] = 'left';
    plate_annotation_layout['yanchor'] = 'bottom';
    plate_annotation_layout['xref'] = 'x' + plate_index;
    plate_annotation_layout['yref'] = 'y' + plate_index;
    plate_annotation_layout['showarrow'] = false;
    return plate_annotation_layout;
  };

  /* Make Plate Ratio to Layout */
  const MakeLayoutPlateRatio = (
    layout,
    g_layout_xaxis,
    g_layout_yaxis,
    plate_index,
    matches_enable,
  ) => {
    if (plate_index === 1) {
      plate_index = '';
    }
    layout['xaxis' + plate_index] = Object.assign({}, g_layout_xaxis);
    layout['xaxis' + plate_index]['scaleanchor'] = 'y' + plate_index;
    if (matches_enable) {
      layout['xaxis' + plate_index]['matches'] = 'y' + plate_index;
    }
    layout['yaxis' + plate_index] = Object.assign({}, g_layout_yaxis);
    return layout;
  };

  /* Make Plate Box Data */
  const MakePlateBoxData = (plate_width, plate_height) => {
    let plate_box_data = {
      x: [],
      y: [],
      name: '',
      text: '',
      mode: 'lines',
      line: {
        color: '#000',
      },
      hoverinfo: 'text',
    };
    plate_box_data.x.push(0 - parseInt(plate_width / 2));
    plate_box_data.x.push(0 - parseInt(plate_width / 2));
    plate_box_data.x.push(parseInt(plate_width / 2));
    plate_box_data.x.push(parseInt(plate_width / 2));
    plate_box_data.x.push(0 - parseInt(plate_width / 2));
    plate_box_data.y.push(0 - parseInt(plate_height / 2));
    plate_box_data.y.push(parseInt(plate_height / 2));
    plate_box_data.y.push(parseInt(plate_height / 2));
    plate_box_data.y.push(0 - parseInt(plate_height / 2));
    plate_box_data.y.push(0 - parseInt(plate_height / 2));
    return plate_box_data;
  };

  /* Make Three Sigma Data */
  const MakeThreeSigmaData = (
    plotly_data,
    first_plate_data,
    three_sigma_data,
    shot_offset_info,
  ) => {
    let three_sigma_data_template = {
      x: [],
      y: [],
      name: '',
      mode: 'markers',
      type: 'scatter',
      hoverinfo: 'none',
      marker: {
        color: '#00f',
        size: 8,
        symbol: 'square',
        opacity: 0.7,
      },
    };
    let three_sigma_data_template2 = {
      x: [],
      y: [],
      name: '',
      mode: 'markers',
      type: 'scatter',
      hoverinfo: 'none',
      marker: {
        color: '#0f0',
        size: 7,
        symbol: 'circle',
        opacity: 0.7,
      },
    };

    for (let data of three_sigma_data.x) {
      let tmp_x =
        first_plate_data.shot[data.shot].base[data.pos].x +
        shot_offset_info[data.shot].x;
      let tmp_y =
        first_plate_data.shot[data.shot].base[data.pos].y +
        shot_offset_info[data.shot].y;
      three_sigma_data_template.x.push(tmp_x);
      three_sigma_data_template.y.push(tmp_y);
    }
    plotly_data.push(three_sigma_data_template);

    for (let data of three_sigma_data.y) {
      let tmp_x =
        first_plate_data.shot[data.shot].base[data.pos].x +
        shot_offset_info[data.shot].x;
      let tmp_y =
        first_plate_data.shot[data.shot].base[data.pos].y +
        shot_offset_info[data.shot].y;
      three_sigma_data_template2.x.push(tmp_x);
      three_sigma_data_template2.y.push(tmp_y);
    }
    plotly_data.push(three_sigma_data_template2);
    return plotly_data;
  };
  MakeMapData(
    global_adc_mea_data,
    lot_name,
    paper_width,
    disp_start,
    disp_end,
    plate_width,
    plate_height,
    row,
    upper_division,
    show_extra_info,
    disp_option,
    shot_offset_info,
  );
};
