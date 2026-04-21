const { createApp, ref, reactive, computed, onMounted, watch } = Vue;
const { ElMessage, ElMessageBox } = ElementPlus;

const app = createApp({
    setup() {
        console.log('=== 校园AI秘书管理后台 v20260421 ===');

        const isLoggedIn = ref(!!localStorage.getItem('token'));
        const currentUser = ref({ username: '', role: '' });
        const loading = ref(false);
        const activeMenu = ref('dashboard');

        const loginForm = reactive({ username: 'admin', password: 'admin123' });
        const loginFormRef = ref(null);
        const loginRules = {
            username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
            password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
        };

        const pageTitle = computed(() => {
            const titles = {
                dashboard: '仪表盘',
                users: '用户管理',
                collected: '采集信息',
                schedules: '日程管理',
                knowledge: '知识库',
                reminders: '提醒日志',
                push: '消息推送',
                smartpush: '智能推送',
                profile: '学生画像',
                settings: '系统设置'
            };
            return titles[activeMenu.value] || '管理后台';
        });

        const handleLogin = async () => {
            if (!loginFormRef.value) return;
            
            await loginFormRef.value.validate(async (valid) => {
                if (!valid) return;
                
                loading.value = true;
                try {
                    const params = new URLSearchParams();
                    params.append('username', loginForm.username);
                    params.append('password', loginForm.password);
                    
                    const res = await api.login(params, {
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                    });
                    
                    localStorage.setItem('token', res.access_token);
                    isLoggedIn.value = true;
                    
                    const userRes = await api.getProfile();
                    currentUser.value = userRes;
                    
                    ElMessage.success('登录成功');
                    loadDashboard();
                } catch (error) {
                    ElMessage.error(error.response?.data?.detail || '登录失败');
                } finally {
                    loading.value = false;
                }
            });
        };

        const logout = () => {
            localStorage.removeItem('token');
            isLoggedIn.value = false;
            currentUser.value = { username: '', role: '' };
            ElMessage.info('已退出登录');
        };

        const handleCommand = (command) => {
            if (command === 'logout') logout();
        };

        const loadDashboard = async () => {
            try {
                window.dashboardStore.stats = await api.getDashboardStats();
                setTimeout(() => {
                    window.dashboardStore.loadUserChart();
                    window.dashboardStore.loadScheduleChart();
                }, 100);
            } catch (error) {
                ElMessage.error('加载统计数据失败');
            }
        };

        const loadUsers = () => {
            window.usersStore.loadUsers();
        };

        const loadSchedules = () => {
            window.schedulesStore.loadSchedules();
        };

        const loadKnowledge = () => {
            window.knowledgeStore.loadKnowledge();
        };

        const loadCollectedInfo = () => {
            window.collectedStore.loadCollectedInfo();
        };

        const loadReminders = () => {
            window.remindersStore.loadReminders();
        };

        const loadSystemInfo = () => {
            window.settingsStore.loadSystemInfo();
        };

        const loadStudents = () => {
            window.profileStore.loadStudents();
        };

        const onStudentSelect = (userId) => {
            if (userId) {
                window.profileStore.loadStudentProfile(userId);
            }
        };

        const loadAIAnalysis = async () => {
            const userId = window.profileStore.selectedStudentId.value;
            if (userId) {
                await window.profileStore.loadAIAnalysis(userId);
                ElementPlus.ElMessage.success('AI分析完成');
            } else {
                ElementPlus.ElMessage.warning('请先选择学生');
            }
        };

        watch(activeMenu, (newVal) => {
            if (newVal === 'dashboard') loadDashboard();
            else if (newVal === 'users') loadUsers();
            else if (newVal === 'schedules') loadSchedules();
            else if (newVal === 'knowledge') loadKnowledge();
            else if (newVal === 'collected') loadCollectedInfo();
            else if (newVal === 'reminders') loadReminders();
            else if (newVal === 'settings') loadSystemInfo();
            else if (newVal === 'profile') loadStudents();
        });

        onMounted(() => {
            if (isLoggedIn.value) {
                api.getProfile()
                    .then(res => currentUser.value = res)
                    .catch(() => logout());
                loadDashboard();
            }
        });

        const pushForm = Vue.reactive({
            userId: '',
            messageType: 'normal',
            template: 'none',
            content: '',
            sending: false,
            successCount: 0,
            failCount: 0,
            sendHistory: []
        });

        const onMessageTypeChange = () => {
            if (pushForm.messageType === 'test') {
                pushForm.content = '🔔 这是一条测试消息\n\n时间：' + new Date().toLocaleString('zh-CN') + '\n来源：管理后台\n\n此消息用于验证消息推送功能是否正常工作。';
            } else if (pushForm.messageType === 'notice') {
                pushForm.content = '📢 【系统公告】\n\n各位同学请注意，系统将于今晚22:00-00:00进行维护升级，期间将暂停服务。请提前保存好您的工作。\n\n感谢您的理解与支持！';
            }
        };

        const onTemplateChange = () => {
            const templates = {
                exam: '📝 【考试提醒】\n\n您有一场考试即将开始，请做好准备：\n• 考试科目：{科目}\n• 考试时间：{时间}\n• 考试地点：{地点}\n\n请携带学生证和相关考试用品。',
                schedule: '📅 【日程提醒】\n\n您有一个日程即将开始：\n• 日程名称：{名称}\n• 开始时间：{时间}\n• 地点：{地点}\n\n请准时参加！',
                system: '🔔 【系统通知】\n\n{内容}\n\n如有疑问，请联系管理员。'
            };
            if (templates[pushForm.template]) {
                pushForm.content = templates[pushForm.template];
            }
        };

        const sendManualMessage = async () => {
            if (!pushForm.userId) {
                ElementPlus.ElMessage.warning('请选择接收用户');
                return;
            }
            if (!pushForm.content.trim()) {
                ElementPlus.ElMessage.warning('请输入消息内容');
                return;
            }

            pushForm.sending = true;
            try {
                const response = await api.sendMessage({
                    user_id: pushForm.userId,
                    content: pushForm.content,
                    message_type: pushForm.messageType
                });

                if (response.success) {
                    ElementPlus.ElMessage.success('消息发送成功');
                    pushForm.successCount++;
                } else {
                    ElementPlus.ElMessage.error('消息发送失败：' + response.message);
                    pushForm.failCount++;
                }

                pushForm.sendHistory.unshift({
                    time: new Date().toLocaleString('zh-CN'),
                    user: pushForm.userId,
                    type: pushForm.messageType,
                    content: pushForm.content.slice(0, 50) + (pushForm.content.length > 50 ? '...' : ''),
                    status: response.success ? 'success' : 'failed'
                });

                if (pushForm.sendHistory.length > 20) {
                    pushForm.sendHistory.pop();
                }
            } catch (error) {
                ElementPlus.ElMessage.error('发送失败：' + error.message);
                pushForm.failCount++;
                pushForm.sendHistory.unshift({
                    time: new Date().toLocaleString('zh-CN'),
                    user: pushForm.userId,
                    type: pushForm.messageType,
                    content: pushForm.content.slice(0, 50) + (pushForm.content.length > 50 ? '...' : ''),
                    status: 'failed'
                });
            } finally {
                pushForm.sending = false;
            }
        };

        const sendTestMessage = async () => {
            pushForm.userId = 'test_user1';
            pushForm.messageType = 'test';
            pushForm.content = '🔔 测试提醒\n\n这是一条测试消息，用于验证消息推送功能是否正常工作。\n\n时间：' + new Date().toLocaleString('zh-CN') + '\n来源：管理后台';
            await sendManualMessage();
        };

        const previewMessage = () => {
            if (!pushForm.content.trim()) {
                ElementPlus.ElMessage.warning('请输入消息内容');
                return;
            }

            ElementPlus.ElMessageBox.alert(
                `<div style="padding: 10px;">
                    <p style="margin-bottom: 10px;"><strong>📤 消息预览</strong></p>
                    <p style="white-space: pre-wrap;">${pushForm.content}</p>
                    <p style="margin-top: 10px; font-size: 12px; color: #999;">
                        接收用户：${pushForm.userId || '未选择'} | 消息类型：${pushForm.messageType}
                    </p>
                </div>`,
                '消息预览',
                {
                    confirmButtonText: '知道了',
                    dangerouslyUseHTMLString: true
                }
            );
        };

        return {
            isLoggedIn,
            currentUser,
            loading,
            activeMenu,
            pageTitle,
            loginForm,
            loginFormRef,
            loginRules,
            handleLogin,
            handleCommand,
            pushForm,
            onMessageTypeChange,
            onTemplateChange,
            sendManualMessage,
            sendTestMessage,
            previewMessage,
            onStudentSelect,
            loadAIAnalysis,
            dashboardStore: window.dashboardStore,
            usersStore: window.usersStore,
            schedulesStore: window.schedulesStore,
            knowledgeStore: window.knowledgeStore,
            collectedStore: window.collectedStore,
            remindersStore: window.remindersStore,
            settingsStore: window.settingsStore,
            smartPushStore: window.smartPushStore,
            profileStore: window.profileStore
        };
    }
});

app.use(ElementPlus);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.mount('#app');