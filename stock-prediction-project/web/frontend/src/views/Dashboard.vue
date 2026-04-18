<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>股票概览</h1>
      <div class="header-actions">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜索股票代码或名称..."
            @keyup.enter="searchStock"
          />
          <button @click="searchStock">搜索</button>
        </div>
        <button @click="showAddModal = true" class="add-btn">+ 添加股票</button>
      </div>
    </div>
    
    <div class="stock-list">
      <div 
        v-for="stock in stockList" 
        :key="stock.code" 
        class="stock-card"
        @click="goToStock(stock.code)"
      >
        <div class="stock-header">
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-name">{{ stock.name }}</span>
        </div>
        <div class="stock-price" :class="getPriceClass(stock)">
          <span class="price-value">{{ stock.price?.toFixed(2) || '--' }}</span>
          <span class="price-change" v-if="stock.change">
            {{ stock.change > 0 ? '+' : '' }}{{ stock.change?.toFixed(2) }}
            ({{ stock.change_percent > 0 ? '+' : '' }}{{ stock.change_percent?.toFixed(2) }}%)
          </span>
        </div>
        <div class="stock-meta">
          <span class="meta-item">{{ stock.industry || '未知行业' }}</span>
          <span class="meta-item">{{ stock.market === 'sh' ? '沪市' : '深市' }}</span>
        </div>
        <div class="stock-actions">
          <button @click.stop="viewDetail(stock.code)">详情</button>
          <button @click.stop="viewPrediction(stock.code)">预测</button>
          <button @click.stop="viewFinancial(stock.code)">财务</button>
        </div>
      </div>
    </div>
    
    <div v-if="stockList.length === 0" class="empty-state">
      <div class="empty-icon">📊</div>
      <p>暂无股票数据</p>
      <button @click="showAddModal = true">添加股票</button>
    </div>
    
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>添加股票</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>股票代码</label>
            <input 
              v-model="newStockCode" 
              type="text" 
              placeholder="请输入6位股票代码，如 600519"
              @keyup.enter="handleAddStock"
            />
            <p class="hint">沪市股票以6开头，深市股票以0或3开头</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModal" class="btn-cancel">取消</button>
          <button @click="handleAddStock" :disabled="!newStockCode || isAdding" class="btn-confirm">
            {{ isAdding ? '添加中...' : '确认添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stockApi } from '../api/stock'

const router = useRouter()

const stockList = ref([])
const searchKeyword = ref('')
const showAddModal = ref(false)
const newStockCode = ref('')
const isAdding = ref(false)

onMounted(() => {
  loadStockList()
})

async function loadStockList() {
  try {
    const response = await stockApi.getStockList()
    const stocks = response.data
    
    for (const stock of stocks) {
      try {
        const realtime = await stockApi.getRealtimePrice(stock.code)
        stock.price = realtime.data.price
        stock.change = realtime.data.change
        stock.change_percent = realtime.data.change_percent
      } catch {
        stock.price = null
        stock.change = null
        stock.change_percent = null
      }
    }
    
    stockList.value = stocks
  } catch (error) {
    console.error('Failed to load stock list:', error)
  }
}

function searchStock() {
  if (!searchKeyword.value) {
    loadStockList()
    return
  }
  
  stockList.value = stockList.value.filter(stock => 
    stock.code.includes(searchKeyword.value) || 
    stock.name.includes(searchKeyword.value)
  )
}

function getPriceClass(stock) {
  if (!stock.change) return ''
  return stock.change >= 0 ? 'price-up' : 'price-down'
}

function goToStock(code) {
  router.push(`/stock/${code}`)
}

function viewDetail(code) {
  router.push(`/stock/${code}`)
}

function viewPrediction(code) {
  router.push(`/prediction/${code}`)
}

function viewFinancial(code) {
  router.push(`/financial/${code}`)
}

function closeModal() {
  showAddModal.value = false
  newStockCode.value = ''
}

async function handleAddStock() {
  if (!newStockCode.value || newStockCode.value.length !== 6) {
    alert('请输入有效的6位股票代码')
    return
  }
  
  isAdding.value = true
  
  try {
    await stockApi.addStock(newStockCode.value)
    alert(`股票 ${newStockCode.value} 添加成功！`)
    closeModal()
    await loadStockList()
  } catch (error) {
    console.error('Failed to add stock:', error)
    alert('添加失败，请检查股票代码是否正确')
  } finally {
    isAdding.value = false
  }
}
</script>

<style scoped>
.dashboard {
  padding: 12px;
}

.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.dashboard-header h1 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: stretch;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-box input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.search-box button {
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.search-box button:hover {
  opacity: 0.9;
}

.add-btn {
  padding: 10px 16px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.3s;
  font-size: 14px;
}

.add-btn:hover {
  opacity: 0.9;
}

.stock-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.stock-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stock-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stock-code {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.stock-name {
  font-size: 14px;
  color: #666;
}

.stock-price {
  margin-bottom: 12px;
}

.price-value {
  font-size: 24px;
  font-weight: 700;
}

@media screen and (min-width: 576px) {
  .dashboard {
    padding: 16px;
  }
  
  .stock-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .dashboard-header h1 {
    font-size: 22px;
  }
}

@media screen and (min-width: 768px) {
  .dashboard {
    padding: 20px;
  }
  
  .dashboard-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  .header-actions {
    flex-direction: row;
    align-items: center;
    gap: 16px;
  }
  
  .search-box input {
    width: 200px;
    border-radius: 20px;
  }
  
  .search-box button {
    border-radius: 20px;
  }
  
  .add-btn {
    border-radius: 20px;
  }
  
  .stock-list {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
  }
  
  .stock-card {
    padding: 20px;
  }
  
  .dashboard-header h1 {
    font-size: 24px;
  }
  
  .stock-code {
    font-size: 18px;
  }
  
  .price-value {
    font-size: 28px;
  }
}

@media screen and (min-width: 1024px) {
  .stock-list {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
  }
}

.price-up .price-value,
.price-up .price-change {
  color: #ef4444;
}

.price-down .price-value,
.price-down .price-change {
  color: #22c55e;
}

.price-change {
  display: block;
  font-size: 14px;
  margin-top: 4px;
}

.stock-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-item {
  font-size: 12px;
  color: #999;
  background-color: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.stock-actions {
  display: flex;
  gap: 8px;
}

.stock-actions button {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.stock-actions button:hover {
  background-color: #f5f7fa;
  border-color: #667eea;
  color: #667eea;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  color: #999;
  margin-bottom: 16px;
}

.empty-state button {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.close-btn {
  font-size: 24px;
  color: #999;
  background: none;
  border: none;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group .hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 10px 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel:hover {
  background-color: #f5f5f5;
}

.btn-confirm {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-confirm:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>