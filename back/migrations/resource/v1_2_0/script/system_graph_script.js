function renderGraph(Plotly, element, params) {
    let tmpGraphProp = {};

    const createPropData = (obj, type, params) => {
        let tmpRange = {},
            tmpDensityRange = {},
            tmpData = [];

        if (params.range.x.length > 0) {
            tmpRange['xaxis'] = {
                range: params.range.x,
            };
        }

        if (params.range.y.length > 0) {
            tmpRange['yaxis'] = {
                range: params.range.y,
            };
        }

        switch (type.toLowerCase()) {
            case 'bar':
            default:
                Object.keys(params.y).reduce((acc, v) => {
                    acc.push({
                        x: params.x[v],
                        y: params.y[v],
                        type: 'bar',
                        name: v,
                    });
		                return acc;
                }, tmpData);
                if (Object.keys(obj).length === 0) {
                    obj = {
                        data: tmpData,
                        layout: {
                            title: params.title,
                            font: {
                                family: "Saira, 'Nunito Sans'",
                            },
                            ...tmpRange,
                        },
                    };
                } else {
                    obj = {
                        ...obj,
                        data: obj.data.concat(tmpData),
                    };
                }
                break;

            case 'line':
                Object.keys(params.y).reduce((acc, v) => {
                    acc.push({
                        x: params.x[v],
                        y: params.y[v],
                        type: 'scatter',
                        name: v,
                    });
                    return acc;
                }, tmpData);
                if (Object.keys(obj).length === 0) {
                    obj = {
                        data: tmpData,
                        layout: {
                            title: params.title,
                            font: {
                                family: "Saira, 'Nunito Sans'",
                            },
                            ...tmpRange,
                        },
                    };
                } else {
                    obj = {
                        ...obj,
                        data: obj.data.concat(tmpData),
                    };
                }
                break;

            case 'box plot':
                Object.keys(params.y).reduce((acc, v) => {
                    acc.push({
                        y: params.y[v],
                        type: 'box',
                        name: v,
                    });
		                return acc;
                }, tmpData);
                if (Object.keys(obj).length === 0) {
                    obj = {
                        data: tmpData,
                        layout: {
                            title: params.title,
                            font: {
                                family: "Saira, 'Nunito Sans'",
                            },
                            ...tmpRange,
                        },
                    };
                } else {
                    obj = {
                        ...obj,
                        data: obj.data.concat(tmpData),
                    };
                }
                break;

            case 'density plot':
                Object.keys(params.y).reduce((acc, v) => {
                    acc.push(
                        {
                            x: params.x[v],
                            y: params.y[v],
                            mode: 'markers',
                            name: v,
                            marker: {
                                color: 'rgb(245,245,245)',
                                size: 1.5,
                                opacity: 0.7,
                            },
                            type: 'scatter',
                        },
                        {
                            x: params.x[v],
                            y: params.y[v],
                            name: v,
                            ncontours: 20,
                            colorscale: 'Blues',
                            reversescale: true,
                            showscale: false,
                            type: 'histogram2dcontour',
                        },
                    );
		                return acc;
                }, tmpData);
				
                if (params.range.x.length > 0) {
                    tmpDensityRange['xaxis'] = {
                        showgrid: false,
                        zeroline: false,
                        range: params.range.x,
                    };
                }

                if (params.range.y.length > 0) {
                    tmpDensityRange['yaxis'] = {
                        showgrid: false,
                        zeroline: false,
                        range: params.range.y,
                    };
                }

                if (Object.keys(obj).length === 0) {
                    obj = {
                        data: tmpData,
                        layout: {
                            title: params.title,
                            font: {
                                family: "Saira, 'Nunito Sans'",
                            },
                            showlegend: false,
                            hovermode: 'closest',
                            bargap: 0,
                            ...tmpDensityRange,
                        },
                    };
                } else {
                    obj = {
                        ...obj,
                        data: obj.data.concat(tmpData),
                    };
                }
                break;

            case 'bubble chart':
                Object.keys(params.y).reduce((acc, v) => {
                    acc.push({
                        x: params.x[v],
                        y: params.y[v],
                        mode: 'markers',
                        name: v,
                        marker: {
                            color: 'rgb(93, 164, 214)',
                            size: params.z,
                        },
                    });
		                return acc;
                }, tmpData);
                if (Object.keys(obj).length === 0) {
                    obj = {
                        data: tmpData,
                        layout: {
                            title: params.title,
                            font: {
                                family: "Saira, 'Nunito Sans'",
                            },
                            ...tmpRange,
                        },
                    };
                } else {
                    obj = {
                        ...obj,
                        data: obj.data.concat(tmpData),
                    };
                }
                break;
        }
        return obj;
    };

    params.type.forEach((v) => {
        tmpGraphProp = createPropData(tmpGraphProp, v, params);
    });

    Plotly.newPlot(element, tmpGraphProp.data, tmpGraphProp.layout);

    if (params.func) {
        element.on('plotly_relayout', params.func);
    }
}
