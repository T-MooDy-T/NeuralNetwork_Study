const API_BASE = window.location.origin;

const axiosInstance = axios.create({
    baseURL: API_BASE,
    timeout: 30000
});

const aiAxiosInstance = axios.create({
    baseURL: API_BASE,
    timeout: 60000
});

aiAxiosInstance.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

aiAxiosInstance.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

axiosInstance.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);

window.api = {
    login: (data, config) => axiosInstance.post('/api/v1/auth/login', data, config),
    getProfile: () => axiosInstance.get('/api/v1/auth/me'),
    
    getDashboardStats: () => axiosInstance.get('/api/admin/dashboard/stats'),
    getUserChart: (days = 7) => axiosInstance.get(`/api/admin/dashboard/chart/users?days=${days}`),
    getScheduleChart: (days = 7) => axiosInstance.get(`/api/admin/dashboard/chart/schedules?days=${days}`),
    
    getUsers: (params) => axiosInstance.get('/api/admin/users', { params }),
    updateUserStatus: (id, status) => axiosInstance.put(`/api/admin/users/${id}/toggle`),
    
    getSchedules: (params) => axiosInstance.get('/api/admin/schedules', { params }),
    deleteSchedule: (id) => axiosInstance.delete(`/api/admin/schedules/${id}`),
    
    getKnowledge: (params) => axiosInstance.get('/api/admin/knowledge', { params }),
    addKnowledge: (data) => axiosInstance.post('/api/admin/knowledge', data, {
        headers: { 'Content-Type': 'application/json' }
    }),
    deleteKnowledge: (id) => axiosInstance.delete(`/api/admin/knowledge/${id}`),
    
    getCollectedInfo: (params) => axiosInstance.get('/api/admin/collected-info', { params }),
    updateCollectedStatus: (id, status) => axiosInstance.put(`/api/admin/collected-info/${id}/status`, { status }),
    
    getReminders: (params) => axiosInstance.get('/api/admin/reminders', { params }),
    
    getSystemInfo: () => axiosInstance.get('/api/admin/system/info'),
    
    sendMessage: (data) => axiosInstance.post('/api/admin/send-message', data),
    sendTestReminder: (userId) => axiosInstance.post(`/api/admin/send-reminder-test?user_id=${userId}`),
    
    logPush: (data) => axiosInstance.post('/api/admin/push-log', data),
    getPushHistory: () => axiosInstance.get('/api/admin/push-history'),
    
    generatePushContent: (data) => aiAxiosInstance.post('/api/v1/smart-push/generate-content', data),
    analyzePriority: (content, context) => aiAxiosInstance.post('/api/v1/smart-push/analyze-priority', { content, context }),
    getPersonalizedRecommend: (params) => aiAxiosInstance.get('/api/v1/smart-push/personalized-recommend', { params }),
    
    getStudentList: (params) => axiosInstance.get('/api/v1/student/profile/list', { params }),
    getStudentProfile: (userId) => axiosInstance.get(`/api/v1/student/profile/${userId}`),
    getStudentAIanalysis: (userId) => aiAxiosInstance.get(`/api/v1/student/profile/${userId}/ai-analysis`)
};