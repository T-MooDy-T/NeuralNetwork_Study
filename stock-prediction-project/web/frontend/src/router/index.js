import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import StockDetail from '../views/StockDetail.vue'
import Prediction from '../views/Prediction.vue'
import Financial from '../views/Financial.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/stock/:code',
    name: 'StockDetail',
    component: StockDetail
  },
  {
    path: '/prediction/:code',
    name: 'Prediction',
    component: Prediction
  },
  {
    path: '/financial/:code',
    name: 'Financial',
    component: Financial
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router