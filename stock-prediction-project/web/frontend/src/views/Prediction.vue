<template>
  <div class="prediction">
    <div class="prediction-header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <div class="stock-title">
        <h1>{{ stockName }} 股价预测</h1>
        <span class="stock-code">{{ code }}</span>
      </div>
    </div>
    
    <div class="prediction-input">
      <label>预测天数：</label>
      <select v-model="predictionDays">
        <option :value="3">3天</option>
        <option :value="7">7天</option>
        <option :value="14">14天</option>
        <option :value="30">30天</option>
      </select>
      <button @click="generatePrediction" :disabled="isLoading">
        {{ isLoading ? '预测中...' : '生成预测' }}
      </button>
    </div>
    
    <div v-if="predictions.length > 0" class="prediction-result">
      <div class="result-header">
        <h3>预测结果</h3>
        <span class="model-info">使用 LSTM 模型</span>
      </div>
      
      <div class="chart-section">
        <div ref="predictionChartRef" class="chart-container"></div>
      </div>
      
      <div class="prediction-table">
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>预测价格</th>
              <th>涨跌预测</th>
              <th>置信区间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(pred, index) in predictions" :key="index">
              <td>{{ pred.date }}</td>
              <td :class="getPriceClass(pred)">{{ pred.predicted_price.toFixed(2) }}</td>
              <td :class="getPriceClass(pred)">
                {{ getChangeText(pred, index) }}
              </td>
              <td>
                <span v-if="pred.lower_bound && pred.upper_bound">
                  {{ pred.lower_bound.toFixed(2) }} - {{ pred.upper_bound.toFixed(2) }}
                </span>
                <span v-else>--</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="prediction-summary">
        <div class="summary-card">
          <span class="summary-label">平均涨幅</span>
          <span class="summary-value" :class="averageChange >= 0 ? 'positive' : 'negative'">
            {{ averageChange >= 0 ? '+' : '' }}{{ averageChange.toFixed(2) }}%
          </span>
        </div>
        <div class="summary-card">
          <span class="summary-label">最高预测</span>
          <span class="summary-value">{{ maxPrediction.toFixed(2) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">最低预测</span>
          <span class="summary-value">{{ minPrediction.toFixed(2) }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="!isLoading && predictions.length === 0" class="empty-state">
      <div class="empty-icon">🔮</div>
      <p>点击上方按钮生成股价预测</p>
      <p class="hint">预测基于历史数据和机器学习模型，仅供参考</p>
    </div>
    
    <div class="risk-warning">
      ⚠️ 风险提示：本预测仅供学习研究使用，不构成投资建议。股市有风险，投资需谨慎。
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockApi, predictionApi } from '../api/stock'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code)

const stockName = ref('')
const predictionDays = ref(7)
const predictions = ref([])
const isLoading = ref(false)
const historicalData = ref([])
const predictionChartRef = ref(null)

let chartInstance = null

onMounted(async () => {
  await loadStockInfo()
  await loadHistoricalData()
})

async function loadStockInfo() {
  try {
    const response = await stockApi.getStockInfo(code.value)
    stockName.value = response.data.name
  } catch (error) {
    console.error('Failed to load stock info:', error)
  }
}

async function loadHistoricalData() {
  try {
    const response = await stockApi.getStockHistory(code.value)
    historicalData.value = response.data.slice(-60)
  } catch (error) {
    console.error('Failed to load historical data:', error)
  }
}

async function generatePrediction() {
  isLoading.value = true
  
  try {
    const response = await predictionApi.createPrediction(code.value, predictionDays.value)
    predictions.value = response.data
    initChart()
  } catch (error) {
    console.error('Failed to generate prediction:', error)
    const errorMessage = error.response?.data?.detail || '预测失败'
    alert(`预测失败: ${errorMessage}`)
  } finally {
    isLoading.value = false
  }
}

function initChart() {
  if (!predictionChartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(predictionChartRef.value)
  updateChart()
  
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

function updateChart() {
  if (!chartInstance || historicalData.value.length === 0) return
  
  const historyDates = historicalData.value.map(item => item.date)
  const historyPrices = historicalData.value.map(item => item.close)
  
  const predDates = predictions.value.map(item => item.date)
  const predPrices = predictions.value.map(item => item.predicted_price)
  
  const allDates = [...historyDates, ...predDates]
  const allPrices = [...historyPrices, ...predPrices]
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const data = params[0]
        return `${data.name}<br/>价格: ${data.value.toFixed(2)}`
      }
    },
    legend: {
      data: ['历史价格', '预测价格'],
      bottom: '5%'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: allDates,
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: {
        rotate: 45,
        fontSize: 11
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f0f0f0' } }
    },
    series: [
      {
        name: '历史价格',
        type: 'line',
        smooth: true,
        data: historyPrices,
        lineStyle: { color: '#667eea', width: 2 },
        itemStyle: { color: '#667eea' }
      },
      {
        name: '预测价格',
        type: 'line',
        smooth: true,
        data: [...Array(historyPrices.length - 1).fill(null), historyPrices[historyPrices.length - 1], ...predPrices],
        lineStyle: { 
          color: '#f59e0b', 
          width: 2,
          type: 'dashed'
        },
        itemStyle: { color: '#f59e0b' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
          ])
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

function getPriceClass(pred, index = 0) {
  if (index === 0) {
    const lastPrice = historicalData.value[historicalData.value.length - 1]?.close || pred.predicted_price
    return pred.predicted_price >= lastPrice ? 'price-up' : 'price-down'
  }
  const prevPred = predictions.value[index - 1]
  return pred.predicted_price >= prevPred.predicted_price ? 'price-up' : 'price-down'
}

function getChangeText(pred, index) {
  if (index === 0) {
    const lastPrice = historicalData.value[historicalData.value.length - 1]?.close || pred.predicted_price
    const change = ((pred.predicted_price - lastPrice) / lastPrice * 100)
    return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
  }
  const prevPred = predictions.value[index - 1]
  const change = ((pred.predicted_price - prevPred.predicted_price) / prevPred.predicted_price * 100)
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const averageChange = computed(() => {
  if (predictions.value.length === 0) return 0
  const lastPrice = historicalData.value[historicalData.value.length - 1]?.close || predictions.value[0].predicted_price
  const avgPrediction = predictions.value.reduce((sum, p) => sum + p.predicted_price, 0) / predictions.value.length
  return ((avgPrediction - lastPrice) / lastPrice * 100)
})

const maxPrediction = computed(() => {
  if (predictions.value.length === 0) return 0
  return Math.max(...predictions.value.map(p => p.predicted_price))
})

const minPrediction = computed(() => {
  if (predictions.value.length === 0) return 0
  return Math.min(...predictions.value.map(p => p.predicted_price))
})

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.prediction {
  padding: 20px;
}

.prediction-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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

.prediction-input {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.prediction-input label {
  font-size: 14px;
  color: #333;
}

.prediction-input select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.prediction-input button {
  padding: 8px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.prediction-input button:hover:not(:disabled) {
  opacity: 0.9;
}

.prediction-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prediction-result {
  margin-bottom: 24px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h3 {
  font-size: 18px;
  color: #333;
}

.model-info {
  font-size: 12px;
  color: #999;
  background-color: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-container {
  height: 350px;
}

.prediction-table {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
}

.prediction-table table {
  width: 100%;
  border-collapse: collapse;
}

.prediction-table th,
.prediction-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.prediction-table th {
  background-color: #fafafa;
  font-weight: 600;
  color: #666;
}

.prediction-table tr:last-child td {
  border-bottom: none;
}

.price-up {
  color: #ef4444;
}

.price-down {
  color: #22c55e;
}

.prediction-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.summary-label {
  display: block;
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.summary-value.positive {
  color: #ef4444;
}

.summary-value.negative {
  color: #22c55e;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  color: #666;
  margin-bottom: 8px;
}

.empty-state .hint {
  font-size: 14px;
  color: #999;
}

.risk-warning {
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  padding: 16px;
  color: #92400e;
  font-size: 14px;
  text-align: center;
}
</style>