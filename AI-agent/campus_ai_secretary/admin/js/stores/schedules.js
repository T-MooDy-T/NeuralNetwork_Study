window.schedulesStore = {
    schedules: Vue.reactive([]),
    filters: Vue.reactive({ status: '', priority: '' }),
    pagination: Vue.reactive({ page: 1, page_size: 20, total: 0 }),
    loading: Vue.reactive({ value: false }),
    
    loadSchedules: async () => {
        window.schedulesStore.loading.value = true;
        try {
            const params = {
                page: window.schedulesStore.pagination.page,
                page_size: window.schedulesStore.pagination.page_size
            };
            if (window.schedulesStore.filters.status) params.status = window.schedulesStore.filters.status;
            if (window.schedulesStore.filters.priority) params.priority = window.schedulesStore.filters.priority;
            
            const res = await api.getSchedules(params);
            window.schedulesStore.schedules = res.items;
            window.schedulesStore.pagination.total = res.total;
        } catch (error) {
            ElementPlus.ElMessage.error('加载日程列表失败');
        } finally {
            window.schedulesStore.loading.value = false;
        }
    },
    
    deleteSchedule: async (id) => {
        try {
            await ElementPlus.ElMessageBox.confirm('确定要删除这个日程吗？', '提示', {
                type: 'warning'
            });
            await api.deleteSchedule(id);
            ElementPlus.ElMessage.success('删除成功');
            window.schedulesStore.loadSchedules();
        } catch (error) {
            if (error !== 'cancel') {
                ElementPlus.ElMessage.error('删除失败');
            }
        }
    },
    
    formatDate: (dateStr) => {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleString('zh-CN', { 
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};