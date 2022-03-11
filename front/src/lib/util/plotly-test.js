import Plotly from 'plotly.js';
import { postRequestExport } from '../api/axios/requests';

export const getGraphImage = (SummaryYAxis, DetailYAxis) => {
  const tab = ['summary', 'detail'];
  const graphBuff = [];
  tab.map((obj) => {
    const list = obj === 'summary' ? SummaryYAxis : DetailYAxis;
    list.map((item) => {
      const graph = document.getElementById(`${obj}_graph_${item}`);
      if (graph) {
        var data = graph.querySelector('div.js-plotly-plot');
        const text = graph.querySelector('text.gtitle').innerHTML;
        Plotly.toImage(data, {
          format: 'png',
          filename: `graph_${item}`,
        }).then((url) => {
          graphBuff.push({ url: url, filename: `${obj}.${text}.png` });
        });
      }
    });
  });
  return graphBuff;
};

export const getGraphImage2 = async () => {
  const imgArr = [];
  const components = document.querySelectorAll('div[class^="js-plotly-plot"]');

  for (let i = 0; i < components.length; i++) {
    const divId = components[i]?.id ?? '';
    const mainHeader = divId.split('_')[0];
    const subDiv = divId.split('_')[1];
    await Plotly.toImage(components[i], {
      format: 'png',
      filename: `graph_${i}`,
    }).then((url) => {
      imgArr.push({
        url: url,
        filename:
          mainHeader !== undefined
            ? `${mainHeader}.${subDiv}.png`
            : `graph_${i}.png`,
      });
    });
  }
  return imgArr;
};
export const jsonToCSV = (json_data) => {
  const json_array = json_data;
  let csv_string = '';
  const titles = Object.keys(json_array[0]);
  titles.forEach((title, index) => {
    csv_string += index !== titles.length - 1 ? `${title},` : `${title}\r\n`;
  });
  json_array.forEach((content, index) => {
    let row = '';

    for (let title in content) {
      row += row === '' ? `${content[title]}` : `,${content[title]}`;
    }
    csv_string += index !== json_array.length - 1 ? `${row}\r\n` : `${row}`;
  });
  return csv_string;
};

export const download = async (formData) => {
  try {
    await postRequestExport(formData);
  } catch (e) {
    console.log(e);
  }
};
