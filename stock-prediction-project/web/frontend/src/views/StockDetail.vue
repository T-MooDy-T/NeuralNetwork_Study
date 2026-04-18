<template>
  <div class="stock-detail">
    <div class="detail-header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <div class="stock-info">
        <h1>{{ stockInfo.name }}</h1>
        <span class="stock-code">{{ stockInfo.code }}</span>
        <span class="market-badge">{{ stockInfo.market === 'sh' ? '沪市' : '深市' }}</span>
      </div>
    </div>
    
    <div class="realtime-section">
      <div class="realtime-price" :class="realtimeData.change >= 0 ? 'price-up' : 'price-down'">
        <span class="price">{{ realtimeData.price?.toFixed(2) || '--' }}</span>
        <span class="change">
          {{ realtimeData.change >= 0 ? '+' : '' }}{{ realtimeData.change?.toFixed(2) }}
          ({{ realtimeData.change_percent >= 0 ? '+' : '' }}{{ realtimeData.change_percent?.toFixed(2) }}%)
        </span>
      </div>
      <div class="realtime-time">{{ realtimeData.time }}</div>
    </div>
    
    <div class="chart-section">
      <div class="chart-header">
        <h3>股价走势图</h3>
        <div class="time-range">
          <button 
            v-for="range in timeRanges" 
            :key="range.value"
            :class="{ active: selectedRange === range.value }"
            @click="changeTimeRange(range.value)"
          >
            {{ range.label }}
          </button>
        </div>
      </div>
      <div ref="chartRef" class="chart-container"></div>
    </div>
    
    <div class="stats-section">
      <div class="stat-card">
        <span class="stat-label">开盘价</span>
        <span class="stat-value">{{ todayData.open?.toFixed(2) || '--' }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">最高价</span>
        <span class="stat-value">{{ todayData.high?.toFixed(2) || '--' }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">最低价</span>
        <span class="stat-value">{{ todayData.low?.toFixed(2) || '--' }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">成交量</span>
        <span class="stat-value">{{ formatVolume(todayData.volume) || '--' }}</span>
      </div>
    </div>
    
    <div class="action-buttons">
      <button @click="goToPrediction">查看预测</button>
      <button @click="goToFinancial">财务分析</button>
      <button @click="refreshData">刷新数据</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockApi } from '../api/stock'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code)

const stockInfo = ref({ code: '', name: '', market: 'sh' })
const realtimeData = ref({ price: null, change: null, change_percent: null, time: '' })
const historicalData = ref([])
const selectedRange = ref('1y')
const chartRef = ref(null)

const timeRanges = [
  { label: '1日', value: '1d' },
  { label: '1周', value: '1w' },
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '1年', value: '1y' },
  { label: '全部', value: 'all' }
]

const todayData = computed(() => {
  if (historicalData.value.length > 0) {
    return historicalData.value[historicalData.value.length - 1]
  }
  return {}
})

let chartInstance = null

onMounted(async () => {
  await loadStockInfo()
  await loadRealtimeData()
  await loadHistoricalData()
  initChart()
})

watch(selectedRange, async () => {
  await loadHistoricalData()
  updateChart()
})

async function loadStockInfo() {
  try {
    const response = await stockApi.getStockInfo(code.value)
    stockInfo.value = response.data
  } catch (error) {
    console.error('Failed to load stock info:', error)
  }
}

async function loadRealtimeData() {
  try {
    const response = await stockApi.getRealtimePrice(code.value)
    realtimeData.value = response.data
  } catch (error) {
    console.error('Failed to load realtime data:', error)
  }
}

async function loadHistoricalData() {
  try {
    const response = await stockApi.getStockHistory(code.value)
    historicalData.value = response.data
    updateChart()
  } catch (error) {
    console.error('Failed to load historical data:', error)
  }
}

function initChart() {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
    
    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  }
}

function updateChart() {
  if (!chartInstance || historicalData.value.length === 0) return
  
  const dates = historicalData.value.map(item => item.date)
  const prices = historicalData.value.map(item => item.close)
  const volumes = historicalData.value.map(item => item.volume)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        top: '5%',
        height: '55%'
      },
      {
        left: '10%',
        right: '10%',
        top: '72%',
        height: '20%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#ddd' } },
        splitLine: { show: false }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        axisLine: { lineStyle: { color: '#ddd' } },
        splitLine: { show: false }
      }
    ],
    yAxis: [
      {
        type: 'value',
        scale: true,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f0f0f0' } }
      },
      {
        type: 'value',
        gridIndex: 1,
        scale: true,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f0f0f0' } }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100,
        bottom: '2%'
      }
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        smooth: true,
        data: prices,
        lineStyle: { color: '#667eea', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: { color: '#764ba2' }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

function changeTimeRange(range) {
  selectedRange.value = range
}

function formatVolume(volume) {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + ' 亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + ' 万'
  }
  return volume.toString()
}

function goBack() {
  router.push('/')
}

function goToPrediction() {
  router.push(`/prediction/${code.value}`)
}

function goToFinancial() {
  router.push(`/financial/${code.value}`)
}

async function refreshData() {
  await loadRealtimeData()
  await loadHistoricalData()
}
</script>

<style scoped>
.stock-detail {
  padding: 12px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.back-btn {
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.back-btn:hover {
  background-color: #f5f5f5;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.stock-info h1 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.stock-code {
  font-size: 14px;
  color: #666;
}

.market-badge {
  font-size: 11px;
  color: white;
  background-color: #667eea;
  padding: 3px 8px;
  border-radius: 10px;
}

.realtime-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.realtime-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.price {
  font-size: 32px;
  font-weight: 700;
}

.change {
  font-size: 16px;
}

.price-up .price,
.price-up .change {
  color: #ef4444;
}

.price-down .price,
.price-down .change {
  color: #22c55e;
}

.realtime-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.time-range {
  display: flex;
  gap: 6px;
}

.time-range button {
  padding: 4px 10px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.time-range button:hover {
  border-color: #667eea;
  color: #667eea;
}

.time-range button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.chart-container {
  height: 280px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

@media screen and (min-width: 576px) {
  .stock-detail {
    padding: 16px;
  }
  
  .price {
    font-size: 40px;
  }
  
  .chart-container {
    height: 320px;
  }
  
  .stats-section {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media screen and (min-width: 768px) {
  .stock-detail {
    padding: 20px;
  }
  
  .stock-info h1 {
    font-size: 24px;
  }
  
  .realtime-section {
    padding: 24px;
  }
  
  .price {
    font-size: 48px;
  }
  
  .change {
    font-size: 18px;
  }
  
  .chart-section {
    padding: 24px;
  }
  
  .chart-header h3 {
    font-size: 18px;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .time-range button {
    padding: 6px 14px;
    font-size: 13px;
  }
}

@media screen and (min-width: 1024px) {
  .stock-detail {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .chart-container {
    height: 450px;
  }
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons button {
  flex: 1;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.action-buttons button:hover {
  opacity: 0.9;
}
</style>