window.settingsStore = {
    systemInfo: Vue.reactive({}),
    
    loadSystemInfo: async () => {
        try {
            window.settingsStore.systemInfo = await api.getSystemInfo();
        } catch (error) {
            console.error('加载系统信息失败', error);
        }
    }
};