window.settingsStore = {
    settings: Vue.reactive({
        ai_enabled: true,
        push_interval: 5,
        reminder_advance: 30
    }),
    systemInfo: Vue.reactive({}),
    
    loadSettings: async () => {
        try {
            window.settingsStore.systemInfo = await api.getSystemInfo();
        } catch (error) {
            console.error('加载系统信息失败', error);
        }
    },
    
    saveSettings: async () => {
        try {
            await api.saveSettings(window.settingsStore.settings);
        } catch (error) {
            console.error('保存设置失败', error);
        }
    }
};