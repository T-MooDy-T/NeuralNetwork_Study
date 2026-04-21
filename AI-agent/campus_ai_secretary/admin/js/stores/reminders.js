window.remindersStore = {
    reminders: Vue.reactive([]),
    pagination: Vue.reactive({ page: 1, page_size: 50, total: 0 }),
    loading: Vue.reactive({ value: false }),
    
    loadReminders: async () => {
        window.remindersStore.loading.value = true;
        try {
            const params = {
                page: window.remindersStore.pagination.page,
                page_size: window.remindersStore.pagination.page_size
            };
            const res = await api.getReminders(params);
            window.remindersStore.reminders = res.items;
            window.remindersStore.pagination.total = res.total;
        } catch (error) {
            ElementPlus.ElMessage.error('加载提醒日志失败');
        } finally {
            window.remindersStore.loading.value = false;
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