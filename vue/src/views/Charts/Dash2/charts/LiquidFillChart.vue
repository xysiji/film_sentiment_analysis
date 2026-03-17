<template>
  <v-chart
    style="width:100%;"
    :options="chartOption"
    autoresize
  />
</template>

<script>
import 'echarts-liquidfill';

export default {
  name: 'LiquidFillChart',
  data() {
    return {
      chartOption: {},
    };
  },
  methods: {
    buildChartOption() {
      const option = {
        // backgroundColor: '#1c2f5c',
        series: [
          {
            type: 'liquidFill',
            data: [0.89],
            direction: 'right',
            radius: '60%',
            color: ['#0fe0d9'],
            center: ['50%', '50%'],
            outline: {
              borderDistance: 0,
              itemStyle: {
                borderWidth: 2,
              },
            },
            backgroundStyle: {
              color: 'rgba(6, 25, 70, 0.8)',
            },
          },
        ],
      };

      return option;
    },
  },
  created() {
    this.chartOption = this.buildChartOption();
  },
};
</script>
