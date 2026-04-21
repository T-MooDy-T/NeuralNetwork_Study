window.profileStore = {
    students: Vue.ref([]),
    currentProfile: Vue.ref(null),
    aiAnalysis: Vue.ref(null),
    loading: Vue.ref(false),
    pagination: Vue.reactive({
        page: 1,
        page_size: 20,
        total: 0
    }),
    selectedStudentId: Vue.ref(null),
    
    async loadStudents() {
        this.loading.value = true;
        try {
            const res = await api.getStudentList({
                page: this.pagination.page,
                page_size: this.pagination.page_size
            });
            console.log('学生列表API返回:', res);
            if (res && res.items) {
                this.students.value = res.items;
                this.pagination.total = res.total;
                console.log('学生列表已更新:', this.students.value);
            }
        } catch (error) {
            console.error('加载学生列表失败:', error);
        } finally {
            this.loading.value = false;
        }
    },
    
    async loadStudentProfile(userId) {
        this.loading.value = true;
        try {
            const res = await api.getStudentProfile(userId);
            console.log('学生画像API返回:', res);
            this.currentProfile.value = res;
            this.selectedStudentId.value = userId;
            this.aiAnalysis.value = null;
        } catch (error) {
            console.error('加载学生画像失败:', error);
            this.currentProfile.value = null;
        } finally {
            this.loading.value = false;
        }
    },
    
    async loadAIAnalysis(userId) {
        this.loading.value = true;
        try {
            const res = await api.getStudentAIanalysis(userId);
            console.log('AI分析API返回:', res);
            this.aiAnalysis.value = res;
        } catch (error) {
            console.error('加载AI分析失败:', error);
            this.aiAnalysis.value = null;
        } finally {
            this.loading.value = false;
        }
    },
    
    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN');
        } catch {
            return dateStr;
        }
    },
    
    getPriorityLabel(priority) {
        const labels = {
            high: '🔴 高',
            medium: '🟡 中',
            low: '🟢 低'
        };
        return labels[priority] || priority;
    },
    
    getStatusLabel(status) {
        const labels = {
            pending: '待处理',
            completed: '已完成',
            cancelled: '已取消'
        };
        return labels[status] || status;
    }
};
