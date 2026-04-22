window.usersStore = {
    users: Vue.reactive([]),
    filters: Vue.reactive({ keyword: '' }),
    pagination: Vue.reactive({ page: 1, page_size: 20, total: 0 }),
    loading: Vue.reactive({ value: false }),
    
    loadUsers: async () => {
        window.usersStore.loading.value = true;
        try {
            const params = {
                page: window.usersStore.pagination.page,
                page_size: window.usersStore.pagination.page_size
            };
            if (window.usersStore.filters.keyword) params.keyword = window.usersStore.filters.keyword;
            
            const res = await api.getUsers(params);
            window.usersStore.users = res.items;
            window.usersStore.pagination.total = res.total;
        } catch (error) {
            ElementPlus.ElMessage.error('加载用户列表失败');
        } finally {
            window.usersStore.loading.value = false;
        }
    },
    
    createUser: async (userForm) => {
        try {
            const data = {
                username: userForm.username,
                nickname: userForm.nickname || userForm.username,
                email: userForm.email,
                password: userForm.password,
                role: userForm.role || 'user'
            };
            await api.createUser(data);
            ElementPlus.ElMessage.success('创建成功');
            await window.usersStore.loadUsers();
        } catch (error) {
            console.error('创建用户失败:', error);
            throw error;
        }
    },
    
    toggleUserStatus: async (user) => {
        try {
            await api.updateUserStatus(user.id, !user.is_active);
            ElementPlus.ElMessage.success('操作成功');
            window.usersStore.loadUsers();
        } catch (error) {
            ElementPlus.ElMessage.error('操作失败');
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