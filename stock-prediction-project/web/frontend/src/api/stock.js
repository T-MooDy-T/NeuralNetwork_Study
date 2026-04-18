import axios from 'axios'

const baseURL = '/api'

export const stockApi = {
  getStockList() {
    return axios.get(`${baseURL}/stocks`)
  },
  
  getStockInfo(code) {
    return axios.get(`${baseURL}/stocks/${code}`)
  },
  
  getStockHistory(code, startDate, endDate) {
    let url = `${baseURL}/stocks/${code}/history`
    const params = []
    if (startDate) params.push(`start_date=${startDate}`)
    if (endDate) params.push(`end_date=${endDate}`)
    if (params.length > 0) url += `?${params.join('&')}`
    return axios.get(url)
  },
  
  getRealtimePrice(code) {
    return axios.get(`${baseURL}/stocks/${code}/realtime`)
  },
  
  updateStockData(code) {
    return axios.post(`${baseURL}/stocks/${code}/update`)
  },
  
  addStock(code) {
    return axios.post(`${baseURL}/stocks/add?code=${code}`)
  }
}

export const predictionApi = {
  createPrediction(code, days) {
    return axios.post(`${baseURL}/predictions`, { code, days })
  },
  
  getPredictions(code) {
    return axios.get(`${baseURL}/predictions/${code}`)
  }
}

export const financialApi = {
  getFinancialData(code) {
    return axios.get(`${baseURL}/financial/${code}`)
  },
  
  getIndicators(code) {
    return axios.get(`${baseURL}/financial/${code}/indicators`)
  },
  
  updateFinancialData(code) {
    return axios.post(`${baseURL}/financial/${code}/update`)
  }
}

export const newsApi = {
  getStockNews(code, limit) {
    let url = `${baseURL}/news/${code}`
    if (limit) url += `?limit=${limit}`
    return axios.get(url)
  },
  
  getGeneralNews(limit) {
    let url = `${baseURL}/news/general`
    if (limit) url += `?limit=${limit}`
    return axios.get(url)
  },
  
  updateStockNews(code) {
    return axios.post(`${baseURL}/news/${code}/update`)
  }
}