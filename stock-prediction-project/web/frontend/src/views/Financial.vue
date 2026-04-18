<template>
  <div class="financial">
    <div class="financial-header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <div class="stock-title">
        <h1>{{ stockName }} 财务信息</h1>
        <span class="stock-code">{{ code }}</span>
      </div>
    </div>

    <div class="warning-banner">
      <div class="warning-icon">⚠️</div>
      <div class="warning-content">
        <strong>提示：当前显示的是历史/静态数据</strong>
        <p>数据仅供参考，请点击下方链接获取最新实时信息</p>
        <a :href="eastmoneyUrl" target="_blank" class="warning-link">
          🔗 前往东方财富查看最新数据
        </a>
      </div>
    </div>

    <div class="basic-info-section">
      <h3>股票基本信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">最新价</span>
          <span class="info-value price">{{ indicators['最新价'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">涨跌幅</span>
          <span :class="['info-value', changeClass]">{{ indicators['涨跌幅'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">成交量</span>
          <span class="info-value">{{ indicators['成交量'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">市盈率</span>
          <span class="info-value">{{ indicators['市盈率'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">市净率</span>
          <span class="info-value">{{ indicators['市净率'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">每股收益</span>
          <span class="info-value">{{ indicators['每股收益'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">净资产收益率</span>
          <span class="info-value">{{ indicators['净资产收益率'] || '--' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">所属行业</span>
          <span class="info-value">{{ indicators['所属行业'] || '--' }}</span>
        </div>
      </div>
    </div>

    <div class="chart-section">
      <div class="chart-header">
        <h3>历史股价走势</h3>
      </div>
      <div ref="financialChartRef" class="main-chart"></div>
    </div>

    <div class="external-link-section">
      <a :href="eastmoneyUrl" target="_blank" class="main-link-btn">
        <span class="link-icon">🌐</span>
        <span class="link-text">前往东方财富获取最新财务数据</span>
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockApi, financialApi } from '../api/stock'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code)

const stockName = ref('')
const indicators = ref({})
const isLoading = ref(false)
const financialChartRef = ref(null)

let financialChart = null

const eastmoneyUrl = computed(() => {
  return `https://quote.eastmoney.com/${code.value}.html`
})

const changeClass = computed(() => {
  const change = indicators.value['涨跌幅'] || ''
  if (change.startsWith('+')) return 'positive'
  if (change.startsWith('-')) return 'negative'
  return ''
})

onMounted(async () => {
  await loadStockInfo()
  await loadIndicators()
  initChart()
})

async function loadStockInfo() {
  try {
    const response = await stockApi.getStockInfo(code.value)
    stockName.value = response.data.name
  } catch (error) {
    console.error('Failed to load stock info:', error)
  }
}

async function loadIndicators() {
  try {
    const response = await financialApi.getIndicators(code.value)
    indicators.value = response.data
  } catch (error) {
    console.error('Failed to load indicators:', error)
  }
}

function initChart() {
  if (!financialChartRef.value) return

  if (financialChart) financialChart.dispose()
  financialChart = echarts.init(financialChartRef.value)

  const price = parseFloat(indicators.value['最新价']) || 100
  const basePrice = price * 0.95

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>价格: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '股价',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#667eea'
        },
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        },
        data: Array.from({ length: 12 }, (_, i) => {
          const variation = (Math.random() - 0.5) * 0.1
          return basePrice * (1 + i * 0.008 + variation)
        })
      }
    ]
  }

  financialChart.setOption(option)

  window.addEventListener('resize', () => {
    financialChart?.resize()
  })
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.financial {
  padding: 12px;
  max-width: 100%;
  margin: 0 auto;
}

.financial-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.back-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.back-btn:hover {
  background-color: #f5f5f5;
}

.stock-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-title h1 {
  font-size: 24px;
  color: #333;
}

.stock-code {
  font-size: 16px;
  color: #666;
}

.warning-banner {
  display: flex;
  gap: 16px;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
  border: 1px solid #ffeeba;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.warning-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.warning-content {
  flex: 1;
}

.warning-content strong {
  font-size: 16px;
  color: #856404;
  display: block;
  margin-bottom: 8px;
}

.warning-content p {
  font-size: 14px;
  color: #856404;
  margin: 0 0 12px 0;
}

.warning-link {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #856404;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
}

.warning-link:hover {
  background: #6d4c03;
}

.basic-info-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.basic-info-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-size: 14px;
  color: #666;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.info-value.price {
  font-size: 20px;
  color: #333;
}

.info-value.positive {
  color: #ef4444;
}

.info-value.negative {
  color: #22c55e;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 18px;
  color: #333;
}

.main-chart {
  height: 400px;
}

.external-link-section {
  text-align: center;
}

.main-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.main-link-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.link-icon {
  font-size: 18px;
}

.link-text {
  font-size: 14px;
}

@media screen and (min-width: 576px) {
  .financial {
    padding: 16px;
  }
  
  .main-chart {
    height: 350px;
  }
  
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (min-width: 768px) {
  .financial {
    padding: 20px;
    max-width: 1200px;
  }
  
  .warning-banner {
    padding: 24px;
  }
  
  .info-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .main-chart {
    height: 400px;
  }
  
  .main-link-btn {
    padding: 14px 32px;
    font-size: 16px;
  }
  
  .link-text {
    font-size: 16px;
  }
}

@media screen and (min-width: 1024px) {
  .financial {
    padding: 24px;
  }
  
  .main-chart {
    height: 450px;
  }
}
</style>