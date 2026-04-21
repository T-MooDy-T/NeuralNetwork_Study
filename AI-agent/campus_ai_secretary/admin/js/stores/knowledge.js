window.knowledgeStore = {
    knowledge: Vue.reactive([]),
    filters: Vue.reactive({ is_active: null }),
    pagination: Vue.reactive({ page: 1, page_size: 20, total: 0 }),
    loading: Vue.reactive({ value: false }),
    showAddDialog: Vue.ref(false),
    form: Vue.reactive({ title: '', content: '', source_type: '教务通知', category: '' }),
    
    loadKnowledge: async () => {
        window.knowledgeStore.loading.value = true;
        try {
            const params = {
                page: window.knowledgeStore.pagination.page,
                page_size: window.knowledgeStore.pagination.page_size
            };
            if (window.knowledgeStore.filters.is_active !== null) params.is_active = window.knowledgeStore.filters.is_active;
            
            const res = await api.getKnowledge(params);
            window.knowledgeStore.knowledge = res.items;
            window.knowledgeStore.pagination.total = res.total;
        } catch (error) {
            ElementPlus.ElMessage.error('加载知识库失败');
        } finally {
            window.knowledgeStore.loading.value = false;
        }
    },
    
    viewKnowledge: (item) => {
        ElementPlus.ElMessageBox.alert(item.content, item.title || '知识库文档', {
            confirmButtonText: '关闭'
        });
    },
    
    addKnowledge: async () => {
        if (!window.knowledgeStore.form.content) {
            ElementPlus.ElMessage.warning('请输入内容');
            return;
        }
        
        try {
            const data = {
                title: window.knowledgeStore.form.title,
                content: window.knowledgeStore.form.content,
                source_type: window.knowledgeStore.form.source_type,
                category: window.knowledgeStore.form.category
            };
            await api.addKnowledge(data);
            ElementPlus.ElMessage.success('添加成功');
            window.knowledgeStore.showAddDialog.value = false;
            window.knowledgeStore.loadKnowledge();
            Object.assign(window.knowledgeStore.form, { title: '', content: '', source_type: '教务通知', category: '' });
        } catch (error) {
            console.error('添加知识库失败:', error);
            ElementPlus.ElMessage.error(error.response?.data?.detail || '添加失败');
        }
    },
    
    deleteKnowledge: async (id) => {
        try {
            await ElementPlus.ElMessageBox.confirm('确定要删除这个文档吗？', '提示', {
                type: 'warning'
            });
            await api.deleteKnowledge(id);
            ElementPlus.ElMessage.success('删除成功');
            window.knowledgeStore.loadKnowledge();
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