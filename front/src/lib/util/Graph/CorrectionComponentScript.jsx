export const CorrectionComponentDefaultScript = (
  Plotly,
  element,
  global_correction_data,
  obj,
) => {
  console.log('[CorrectionComponentDefaultScript]obj', obj);

  const lot_name = obj.lot_name; //Object.keys(global_correction_data.data.map)[0];
  const paper_width = 1700;
  const disp_start = obj.display_map.min; //1;
  const disp_end = obj.display_map.max; //30;
  const plate_width = obj.plate_size.size_x; //2500;
  const plate_height = obj.plate_size.size_y; //2500;
  const row = obj.column_num; //5;
  const upper_division = obj.div.div_upper; //1;
  const lower_division = obj.div.div_lower; //1;
  const stage_correction_tooltip = obj.stage_correction_tooltip; //['[DR]', 'bdc x', '', '[MY]', 'bdc y'];
  const adc_correction_tooltip = obj.adc_correction_tooltip; //['[ADC Measurement + Offset]', 'dr', 'my'];
  const shot_offset_info = obj.offset.info;
  const disp_option_correction = {
    shot: obj.disp_option_correction,
  }; /*{
    shot: {
      1: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
      2: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
      3: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
      4: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
      5: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
      6: {
        CP: {
          cp1: true,
          cp12d: true,
          cp1d: true,
          cp21d: true,
          cp2: true,
          cp23d: true,
          cp3d: true,
          cp32d: true,
          cp3: true,
        },
        VS: {
          vs1l: true,
          vs2l: true,
          vs3l: true,
          vs4l: true,
          vsc: true,
          vs4r: true,
          vs3r: true,
          vs2r: true,
          vs1r: true,
        },
      },
    },
  };*/

  //useEffect(()=>{
  //    if(plolyRef.current !== null){
  //        MakeMapData(global_correction_data, lot_name, paper_width, disp_start, disp_end,
  //            plate_width, plate_height, row, upper_division, lower_division,
  //            disp_option_correction, shot_offset_info, stage_correction_tooltip, adc_correction_tooltip)
  //    }
  //},[plolyRef])

  /* Make Data */
  const MakeMapData = (
    correction_data,
    lot_name,
    paper_width,
    disp_start,
    disp_end,
    plate_width,
    plate_height,
    disp_columns,
    upper_division,
    lower_division,
    disp_option_correction,
    shot_offset_info,
    stage_correction_tooltip,
    adc_correction_tooltip,
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
        l: 70,
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

    let map_data_inner = correction_data.data.map[lot_name];
    let plate_data = map_data_inner.plate;
    let correction_image_inner = correction_data.data.correction_image;
    let stage_correction_inner = correction_data.data.stage_correction;
    let adc_correction_inner = correction_data.data.adc_correction;
    let grid_columns, grid_rows;
    let plate_box_data;
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

    /* Make Layout Grid Col, Row */
    let plate_total = disp_end - disp_start + 1;
    if (plate_total <= disp_columns) {
      grid_columns = plate_total;
      grid_rows = 1;
    } else {
      grid_columns = disp_columns;
      grid_rows =
        parseInt(plate_total / disp_columns) +
        (plate_total % disp_columns == 0 ? 0 : 1);
    }
    grid_rows *= 2;
    plotly_layout.grid.columns = grid_columns;
    plotly_layout.grid.rows = grid_rows;

    /* Make Layout Paper Size */
    plotly_layout.width = paper_width;
    plotly_layout.height =
      (paper_width / grid_columns) * grid_rows * (1 + grid_columns * 0.015);

    let g_pointer_correction_values = MakePointCorrectionValues();

    /* Make Lot Data */
    for (let plate_num in plate_data) {
      /* Make Plate Data */
      if (
        parseInt(plate_num) >= disp_start &&
        parseInt(plate_num) <= disp_end
      ) {
        /*****************************************************************************************************/
        let glass_num = plate_data[plate_num]['glass_num'];

        /*****************************************************************************************************/
        plotly_data_temp = MakePlateCorrectionData(
          correction_image_inner[glass_num],
          stage_correction_inner[glass_num],
          plate_index,
          upper_division,
          g_pointer_correction_values,
          disp_option_correction,
          shot_offset_info,
          stage_correction_tooltip,
        );
        for (let x of plotly_data_temp) plotly_data.push(x);

        /* Add Plate Box Data */
        plate_box_data = Object.assign({}, plate_box_data);
        plate_box_data['xaxis'] =
          'x' + (plate_index + grid_columns == 1 ? '' : plate_index);
        plate_box_data['yaxis'] =
          'y' + (plate_index + grid_columns == 1 ? '' : plate_index);
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

        if (plate_index % grid_columns == 1) {
          plotly_layout['annotations'].push(
            MakeLayoutLowTitle(
              plotly_layout,
              plate_index,
              'Stage Correction',
              grid_columns,
            ),
          );
        }

        /*****************************************************************************************************/
        plotly_data_temp = MakePlateCorrectionData(
          correction_image_inner[glass_num],
          adc_correction_inner[glass_num],
          plate_index + grid_columns,
          lower_division,
          g_pointer_correction_values,
          disp_option_correction,
          shot_offset_info,
          adc_correction_tooltip,
        );
        for (let x of plotly_data_temp) plotly_data.push(x);

        /* Add Plate Box Data */
        plate_box_data = Object.assign({}, plate_box_data);
        plate_box_data['xaxis'] =
          'x' +
          (plate_index + grid_columns == 1 ? '' : plate_index + grid_columns);
        plate_box_data['yaxis'] =
          'y' +
          (plate_index + grid_columns == 1 ? '' : plate_index + grid_columns);
        plotly_data.push(plate_box_data);

        /* Add Layout Plate Ratio */
        plotly_layout = MakeLayoutPlateRatio(
          plotly_layout,
          g_layout_xaxis,
          g_layout_yaxis,
          plate_index + grid_columns,
          fix_plate_size_disp,
        );

        /* Add Each Plate Annotation(Title) to Layout */
        plotly_layout['annotations'].push(
          MakeLayoutPlateTitle(
            plate_data[plate_num]['glass_num'],
            plate_num,
            plate_index + grid_columns,
            g_layout_xaxis.range[0],
            g_layout_yaxis.range[1],
          ),
        );

        if (plate_index % grid_columns == 1) {
          plotly_layout['annotations'].push(
            MakeLayoutLowTitle(
              plotly_layout,
              plate_index + grid_columns,
              'ADC Correction',
              grid_columns,
            ),
          );
        }

        /*****************************************************************************************************/
        if (plate_index % grid_columns == 0) {
          plate_index = plate_index + grid_columns;
        }
        plate_index++;
      }
    }

    //Plotly.newPlot(plolyRef.current, plotly_data, plotly_layout);
    Plotly.newPlot(element, plotly_data, plotly_layout);
  };

  /* Plate Data */
  const MakePlateCorrectionData = (
    base_correction_data,
    measurement_correction_data,
    plate_index,
    division,
    g_pointer_correction_values,
    disp_option_correction,
    shot_offset_info,
    tool_tip,
  ) => {
    let plotly_data = [];
    let shot_disp_index = 0;
    for (let shot in measurement_correction_data.shot) {
      MakeShotCorrectionData(
        plotly_data,
        base_correction_data.shot[shot],
        measurement_correction_data.shot[shot],
        shot,
        division,
        g_pointer_correction_values,
        disp_option_correction.shot[shot],
        shot_offset_info,
        tool_tip,
      );
      // eslint-disable-next-line no-unused-vars
      shot_disp_index++;
    }
    /* Make matching xaxis, yaxis of plotly data*/
    for (let data of plotly_data) {
      data['xaxis'] = 'x' + (plate_index == 1 ? '' : plate_index);
      data['yaxis'] = 'y' + (plate_index == 1 ? '' : plate_index);
    }
    return plotly_data;
  };

  /* Shot Data */
  const MakeShotCorrectionData = (
    plotly_data,
    base_shot_data,
    measurement_shot_data,
    shot_no,
    division,
    g_pointer_correction_values,
    disp_option_shot,
    shot_offset_info,
    tool_tip,
  ) => {
    let base_data_return;
    let plotly_data_temp, base_x_point_values, base_y_point_values;
    for (let ele in measurement_shot_data) {
      if (ele == 'base') {
        base_data_return = MakeBaseCorrectionData(
          base_shot_data[ele],
          shot_no,
          g_pointer_correction_values,
          disp_option_shot,
          shot_offset_info,
          tool_tip,
        );
        plotly_data_temp = base_data_return.plotly_data;
        base_x_point_values = base_data_return.x_point_values;
        base_y_point_values = base_data_return.y_point_values;
        for (let x of plotly_data_temp) plotly_data.push(x);
      } else {
        plotly_data_temp = MakeMeasurementCorrectionData(
          measurement_shot_data[ele],
          shot_no,
          base_x_point_values,
          base_y_point_values,
          50,
          division,
          g_pointer_correction_values,
          disp_option_shot,
          tool_tip,
        );
        for (let x of plotly_data_temp) plotly_data.push(x);
      }
    }
  };

  /* Base Data */
  const MakeBaseCorrectionData = (
    value_data,
    shot_no,
    g_pointer_correction_values,
    disp_option_shot,
    shot_offset_info,
    tool_tip,
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
    let x_point_values = GetPointCorrectionValues(
      g_pointer_correction_values,
      value_data,
      'x',
    );
    let y_point_values = GetPointCorrectionValues(
      g_pointer_correction_values,
      value_data,
      'y',
    );
    for (let i = 0; i < x_point_values.length; i++) {
      x_point_values[i] =
        x_point_values[i] + parseFloat(shot_offset_info[shot_no].x);
    }
    for (let i = 0; i < y_point_values.length; i++) {
      y_point_values[i] =
        y_point_values[i] + parseFloat(shot_offset_info[shot_no].y);
    }
    plotly_data = MakeGridCorrectionData(
      plotly_data,
      shot_no,
      x_point_values,
      y_point_values,
      x_point_values,
      y_point_values,
      g_base_datatemplate,
      disp_option_shot,
      tool_tip,
    );
    return { plotly_data, x_point_values, y_point_values };
  };

  /* Measurement Data */
  const MakeMeasurementCorrectionData = (
    value_data,
    shot_no,
    base_x_point_values,
    base_y_point_values,
    interval_val,
    division_val,
    g_pointer_correction_values,
    disp_option_shot,
    tool_tip,
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
    let x_point_values_measure = GetPointCorrectionValues(
      g_pointer_correction_values,
      value_data,
      'x',
    );
    let y_point_values_measure = GetPointCorrectionValues(
      g_pointer_correction_values,
      value_data,
      'y',
    );

    x_point_values = x_point_values_measure.map(function (obj, index) {
      return base_x_point_values[index] + obj * (interval_val / division_val);
    });
    y_point_values = y_point_values_measure.map(function (obj, index) {
      return base_y_point_values[index] + obj * (interval_val / division_val);
    });

    plotly_data = MakeGridCorrectionData(
      plotly_data,
      shot_no,
      x_point_values,
      y_point_values,
      x_point_values_measure,
      y_point_values_measure,
      g_measurement_datatemplate,
      disp_option_shot,
      tool_tip,
    );
    return plotly_data;
  };

  /* Make X,Y Point List [...]   Order by global_point_order */
  const MakePointCorrectionValues = () => {
    const cp_name_list = [
      'cp3',
      'cp32d',
      'cp3d',
      'cp23d',
      'cp2',
      'cp21d',
      'cp1d',
      'cp12d',
      'cp1',
    ];
    const vs_name_list = [
      'vs1l',
      'vs2l',
      'vs3l',
      'vs4l',
      'vsc',
      'vs4r',
      'vs3r',
      'vs2r',
      'vs1r',
    ];
    let g_point_order = [];
    for (let vs_name of vs_name_list) {
      for (let cp_name of cp_name_list) {
        g_point_order.push(cp_name + '_' + vs_name);
      }
    }
    return g_point_order;
  };

  /* Make X,Y Point List [...]   Order by global_point_order */
  const GetPointCorrectionValues = (g_point_order, value_data, axis_name) => {
    let point_values = g_point_order.reduce((acc, cur) => {
      acc.push(value_data[cur][axis_name]);
      return acc;
    }, []);
    return point_values;
  };

  /* Make Grid Data */
  const MakeGridCorrectionData = (
    plotly_data,
    shot_no,
    x_point_values,
    y_point_values,
    x_hover_values,
    y_hover_values,
    data_template,
    disp_option_shot,
    tool_tip,
  ) => {
    const x_point_max = 9,
      y_point_max = 9;
    let outputdata = { x: [], y: [], text: '' };
    let text_tool_tip = '';

    const cp_name_list = [
      'cp3',
      'cp32d',
      'cp3d',
      'cp23d',
      'cp2',
      'cp21d',
      'cp1d',
      'cp12d',
      'cp1',
    ];
    const vs_name_list = [
      'vs1l',
      'vs2l',
      'vs3l',
      'vs4l',
      'vsc',
      'vs4r',
      'vs3r',
      'vs2r',
      'vs1r',
    ];

    for (let tip of tool_tip) {
      text_tool_tip = text_tool_tip + tip + '<br>';
    }

    for (let col = 0; col < x_point_max; col++) {
      if (!disp_option_shot.VS[vs_name_list[col]]) continue;
      outputdata = { x: [], y: [], text: [] };
      let filtered = GetColumnsCorrectionFilter(
        col,
        x_point_max,
        y_point_max,
        x_point_values.length,
        disp_option_shot,
      );
      for (let idx of filtered) {
        outputdata.x.push(x_point_values[idx]);
        outputdata.y.push(y_point_values[idx]);
      }
      outputdata.text = text_tool_tip;
      plotly_data.push(Object.assign(outputdata, data_template));
    }

    for (let row = 0; row < y_point_max; row++) {
      if (!disp_option_shot.CP[cp_name_list[row]]) continue;
      outputdata = { x: [], y: [], text: [] };
      let filtered = GetRowsCorrectionFilter(
        row,
        x_point_max,
        y_point_max,
        x_point_values.length,
        disp_option_shot,
      );
      for (let idx of filtered) {
        outputdata.x.push(x_point_values[idx]);
        outputdata.y.push(y_point_values[idx]);
      }
      outputdata.text = text_tool_tip;
      plotly_data.push(Object.assign(outputdata, data_template));
    }
    return plotly_data;
  };

  /* Get Columns */
  const GetColumnsCorrectionFilter = (
    col,
    x_point_max,
    y_point_max,
    x_point_values_length,
    disp_option_shot,
  ) => {
    const cp_name_list = [
      'cp3',
      'cp32d',
      'cp3d',
      'cp23d',
      'cp2',
      'cp21d',
      'cp1d',
      'cp12d',
      'cp1',
    ];
    const arr = Array.from(
      { length: x_point_values_length },
      (_, index) => index,
    );
    let cp_index;

    const filtered = arr.filter((value, index) => {
      if (index >= y_point_max * col && index < y_point_max * (col + 1)) {
        cp_index = index % x_point_max;
        if (disp_option_shot.CP[cp_name_list[cp_index]]) return true;
        else return false;
      }
      return false;
    });
    return filtered;
  };

  /* Get Rows */
  const GetRowsCorrectionFilter = (
    row,
    x_point_max,
    y_point_max,
    x_point_values_length,
    disp_option_shot,
  ) => {
    const vs_name_list = [
      'vs1l',
      'vs2l',
      'vs3l',
      'vs4l',
      'vsc',
      'vs4r',
      'vs3r',
      'vs2r',
      'vs1r',
    ];
    const arr = Array.from(
      { length: x_point_values_length },
      (_, index) => index,
    );
    let vs_index;
    const filtered = arr.filter((value, index) => {
      for (
        let tmpidx = row;
        tmpidx < x_point_values_length;
        tmpidx = tmpidx + y_point_max
      ) {
        if (index == tmpidx) {
          vs_index = parseInt(index / y_point_max);
          if (disp_option_shot.VS[vs_name_list[vs_index]]) return true;
          else return false;
        }
      }
      return false;
    });
    return filtered;
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

  /* Make Each Plate Annotation(Title) to Layout */
  const MakeLayoutLowTitle = (
    plotly_layout,
    plate_index,
    text,
    grid_columns,
  ) => {
    let plate_annotation_layout = {};
    plate_annotation_layout['text'] = text;
    plate_annotation_layout['textangle'] = 270;
    plate_annotation_layout['bordercolor'] = 'rgb(0,0,0)';
    plate_annotation_layout['font'] = { size: 25 };

    plate_annotation_layout['align'] = 'center';

    plate_annotation_layout['height'] = 40;
    plate_annotation_layout['x'] = -(60 / plotly_layout.width);
    plate_annotation_layout['xanchor'] = 'left';
    plate_annotation_layout['xref'] = 'paper';

    plate_annotation_layout['width'] =
      (plotly_layout.width * 0.88) / grid_columns;
    plate_annotation_layout['y'] = 0;
    plate_annotation_layout['yanchor'] = 'bottom';
    plate_annotation_layout['yref'] = 'y' + plate_index + ' domain';

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
    if (plate_index == 1) {
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
  MakeMapData(
    global_correction_data,
    lot_name,
    paper_width,
    disp_start,
    disp_end,
    plate_width,
    plate_height,
    row,
    upper_division,
    lower_division,
    disp_option_correction,
    shot_offset_info,
    stage_correction_tooltip,
    adc_correction_tooltip,
  );
};
