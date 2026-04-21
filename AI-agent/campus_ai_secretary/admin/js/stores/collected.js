window.collectedStore = {
    collectedInfo: Vue.reactive([]),
    filters: Vue.reactive({ source_type: '', priority: '', status: '' }),
    pagination: Vue.reactive({ page: 1, page_size: 20, total: 0 }),
    loading: Vue.reactive({ value: false }),
    
    loadCollectedInfo: async () => {
        window.collectedStore.loading.value = true;
        try {
            const params = {
                page: window.collectedStore.pagination.page,
                page_size: window.collectedStore.pagination.page_size,
                source_type: window.collectedStore.filters.source_type || undefined,
                priority: window.collectedStore.filters.priority || undefined,
                status: window.collectedStore.filters.status || undefined
            };
            const res = await api.getCollectedInfo(params);
            window.collectedStore.collectedInfo = res.items || [];
            window.collectedStore.pagination.total = res.total || 0;
        } catch (error) {
            console.error('加载采集信息失败:', error);
            ElementPlus.ElMessage.error('加载采集信息失败');
        } finally {
            window.collectedStore.loading.value = false;
        }
    },
    
    viewCollectedInfo: (item) => {
        const tags = item.tags && Array.isArray(item.tags) ? item.tags.join(', ') : '-';
        let content = `<div><p><strong>来源：</strong>${item.source || '-'}</p>`;
        content += `<p><strong>发送者：</strong>${item.sender || '-'}</p>`;
        content += `<p><strong>时间：</strong>${window.collectedStore.formatDate(item.timestamp)}</p>`;
        content += `<p><strong>优先级：</strong>${item.priority === 'high' ? '高' : item.priority === 'medium' ? '中' : '低'}</p>`;
        content += `<p><strong>标签：</strong>${tags}</p>`;
        content += `<p><strong>内容：</strong></p><p>${item.content || '-'}</p></div>`;
        ElementPlus.ElMessageBox.alert(content, '采集信息详情', {
            confirmButtonText: '关闭',
            dangerouslyUseHTMLString: true
        });
    },
    
    markCollectedAsRead: async (item) => {
        try {
            await api.updateCollectedStatus(item.id, 'read');
            item.status = 'read';
            ElementPlus.ElMessage.success('标记成功');
        } catch (error) {
            ElementPlus.ElMessage.error('标记失败');
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