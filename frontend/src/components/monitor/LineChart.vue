<!-- 折线图轻封装（echarts）：props 变化自动重绘，窗口缩放自适应 -->
<template>
  <div ref="chartRef" class="line-chart"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { lineSeriesSchema } from '@/types'

const props = defineProps<{
  /** 纵轴单位标签，如 "次"、"token" */
  unit?: string
  /** x 轴标签（各时间桶，已排序去重） */
  xData: string[]
  /** 每条曲线一个元素 */
  series: lineSeriesSchema[]
  /** 渲染器：canvas（默认）或 svg（矢量，在 transform/动画容器里不模糊） */
  renderer?: 'canvas' | 'svg'
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

// 曲线配色取自 Arco Design 调色板（与全站令牌一致）
const PALETTE = ['#165DFF', '#00B42A', '#FF7D00', '#F53F3F', '#14C9C9', '#722ED1', '#F77234', '#F759AB']

function render() {
  if (!chart) return
  chart.setOption(
    {
      grid: { left: 64, right: 20, top: 44, bottom: 40 },
      tooltip: { trigger: 'axis' },
      legend: { top: 4, type: 'scroll' },
      color: PALETTE,
      xAxis: { type: 'category', boundaryGap: false, data: props.xData },
      yAxis: { type: 'value', name: props.unit },
      series: props.series.map((s) => ({
        name: s.name,
        type: 'line' as const,
        data: s.data,
        // 点多时显示圆点会很挤，只在稀疏时间轴上显示
        showSymbol: props.xData.length <= 48,
      })),
    },
    { notMerge: true },
  )
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  chart = echarts.init(chartRef.value!, undefined, { renderer: props.renderer ?? 'canvas' })
  render()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

watch(() => [props.xData, props.series], render, { deep: true })
</script>

<style scoped>
.line-chart {
  width: 100%;
  height: 100%;
  min-height: 260px;
}
</style>
