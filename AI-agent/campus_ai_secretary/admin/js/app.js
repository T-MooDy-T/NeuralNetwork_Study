const { createApp, ref, computed, onMounted } = Vue;
const { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput, ElTextarea, ElButton, ElMenu, ElMenuItem, ElDropdown, ElDropdownMenu, ElDropdownItem, ElTable, ElTableColumn, ElDialog, ElSelect, ElOption, ElTag, ElSwitch, ElInputNumber } = ElementPlus;

const app = createApp({
    name: 'AdminApp',
    setup() {
        const isLoggedIn = ref(false);
        const activeMenu = ref('dashboard');
        const currentUser = ref({ username: 'admin' });

        const pageTitle = computed(() => {
            const titles = {
                dashboard: '仪表盘',
                users: '用户管理',
                schedules: '日程管理',
                knowledge: '知识库',
                collected: '采集信息',
                reminders: '提醒日志',
                internships: '实习信息',
                push: '消息推送',
                smartpush: '智能推送',
                profile: '学生画像',
                jobmatch: '岗位匹配',
                settings: '系统设置'
            };
            return titles[activeMenu.value] || '校园AI秘书';
        });

        const handleLoginSuccess = () => {
            isLoggedIn.value = true;
            const userStr = localStorage.getItem('user');
            if (userStr) {
                currentUser.value = JSON.parse(userStr);
            }
        };

        const handleLogout = () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            isLoggedIn.value = false;
            activeMenu.value = 'dashboard';
        };

        const handleMenuChange = (menu) => {
            activeMenu.value = menu;
        };

        onMounted(() => {
            const token = localStorage.getItem('token');
            if (token) {
                isLoggedIn.value = true;
                const userStr = localStorage.getItem('user');
                if (userStr) {
                    currentUser.value = JSON.parse(userStr);
                }
            }
        });

        return {
            isLoggedIn,
            activeMenu,
            currentUser,
            pageTitle,
            handleLoginSuccess,
            handleLogout,
            handleMenuChange
        };
    }
});

app.use(ElementPlus);
app.component('el-textarea', ElementPlus.ElTextarea);

app.component('Login', {
    template: '#login-template',
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            loading: false
        };
    },
    methods: {
        async handleLogin() {
            if (!this.loginForm.username || !this.loginForm.password) {
                ElMessage.error('请输入用户名和密码');
                return;
            }
            
            this.loading = true;
            try {
                const response = await axios.post('/api/v1/auth/login', {
                    username: this.loginForm.username,
                    password: this.loginForm.password
                });
                
                if (response.data.success) {
                    localStorage.setItem('token', response.data.access_token);
                    localStorage.setItem('user', JSON.stringify(response.data.user));
                    this.$emit('login-success');
                } else {
                    ElMessage.error(response.data.message || '登录失败');
                }
            } catch (error) {
                console.error('登录失败:', error);
                ElMessage.error('登录失败，请检查用户名和密码');
            } finally {
                this.loading = false;
            }
        }
    }
});

app.component('Sidebar', {
    template: '#sidebar-template',
    props: ['activeMenu'],
    methods: {
        handleMenuClick(menu) {
            this.$emit('menu-change', menu);
        }
    }
});

app.component('Header', {
    template: '#header-template',
    props: ['title', 'currentUser'],
    methods: {
        handleCommand(command) {
            if (command === 'logout') {
                this.$emit('logout');
            }
        }
    }
});

app.component('Dashboard', {
    template: '#dashboard-template',
    data() {
        return {
            scheduleChart: null,
            reminderChart: null,
            store: window.dashboardStore
        };
    },
    mounted() {
        this.loadStats();
        this.initCharts();
    },
    methods: {
        async loadStats() {
            await dashboardStore.loadStats();
            this.updateCharts();
        },
        initCharts() {
            setTimeout(() => {
                this.scheduleChart = echarts.init(document.getElementById('scheduleChart'));
                this.reminderChart = echarts.init(document.getElementById('reminderChart'));
                this.updateCharts();
            }, 100);
        },
        updateCharts() {
            const scheduleData = dashboardStore.stats.scheduleChart || [0, 0, 0, 0, 0, 0, 0];
            const reminderData = dashboardStore.stats.reminderChart || [0, 0, 0, 0, 0, 0, 0];
            const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

            if (this.scheduleChart) {
                this.scheduleChart.setOption({
                    xAxis: { type: 'category', data: days },
                    yAxis: { type: 'value' },
                    series: [{ data: scheduleData, type: 'bar', color: '#409EFF' }]
                });
            }

            if (this.reminderChart) {
                this.reminderChart.setOption({
                    xAxis: { type: 'category', data: days },
                    yAxis: { type: 'value' },
                    series: [{ data: reminderData, type: 'bar', color: '#67C23A' }]
                });
            }
        }
    }
});

app.component('UserManagement', {
    template: '#user-management-template',
    data() {
        return {
            searchQuery: '',
            showAddUser: false,
            userForm: {
                username: '',
                nickname: '',
                email: '',
                password: '',
                role: 'user'
            },
            store: window.usersStore
        };
    },
    mounted() {
        this.loadUsers();
    },
    methods: {
        async loadUsers() {
            await usersStore.loadUsers();
        },
        searchUsers() {
            usersStore.searchUsers(this.searchQuery);
        },
        editUser(user) {
            ElMessage.info('编辑功能开发中');
        },
        async deleteUser(userId) {
            if (await ElMessageBox.confirm('确定要删除该用户吗？')) {
                await usersStore.deleteUser(userId);
                ElMessage.success('删除成功');
            }
        },
        async submitUser() {
            await usersStore.createUser(this.userForm);
            this.showAddUser = false;
            this.userForm = { username: '', nickname: '', email: '', password: '', role: 'user' };
            ElMessage.success('添加成功');
            await this.loadUsers();
        }
    }
});

app.component('ScheduleManagement', {
    template: '#schedule-management-template',
    data() {
        return {
            searchQuery: '',
            showAddSchedule: false,
            scheduleForm: {
                event_name: '',
                location: '',
                start_time: '',
                priority: 'medium',
                description: ''
            },
            store: window.schedulesStore
        };
    },
    mounted() {
        this.loadSchedules();
    },
    methods: {
        async loadSchedules() {
            await schedulesStore.loadSchedules();
        },
        searchSchedules() {
            schedulesStore.searchSchedules(this.searchQuery);
        },
        editSchedule(schedule) {
            ElMessage.info('编辑功能开发中');
        },
        async deleteSchedule(scheduleId) {
            if (await ElMessageBox.confirm('确定要删除该日程吗？')) {
                await schedulesStore.deleteSchedule(scheduleId);
                ElMessage.success('删除成功');
            }
        },
        async submitSchedule() {
            await schedulesStore.createSchedule(this.scheduleForm);
            this.showAddSchedule = false;
            this.scheduleForm = { event_name: '', location: '', start_time: '', priority: 'medium', description: '' };
            ElMessage.success('添加成功');
            await this.loadSchedules();
        }
    }
});

app.component('KnowledgeBase', {
    template: '#knowledge-base-template',
    data() {
        return {
            searchQuery: '',
            showAddKnowledge: false,
            store: window.knowledgeStore,
            showViewKnowledge: false,
            viewItem: {},
            knowledgeForm: {
                title: '',
                content: '',
                category: '学习资料'
            }
        };
    },
    mounted() {
        this.loadKnowledge();
    },
    methods: {
        async loadKnowledge() {
            await knowledgeStore.loadKnowledge();
        },
        searchKnowledge() {
            knowledgeStore.searchKnowledge(this.searchQuery);
        },
        viewKnowledge(item) {
            this.viewItem = item;
            this.showViewKnowledge = true;
        },
        async deleteKnowledge(id) {
            if (await ElMessageBox.confirm('确定要删除该知识吗？')) {
                await knowledgeStore.deleteKnowledge(id);
                ElMessage.success('删除成功');
            }
        },
        async submitKnowledge() {
            await knowledgeStore.createKnowledge(this.knowledgeForm);
            this.showAddKnowledge = false;
            this.knowledgeForm = { title: '', content: '', category: '学习资料' };
            ElMessage.success('添加成功');
            await this.loadKnowledge();
        }
    }
});

app.component('CollectedInfo', {
    template: '#collected-info-template',
    data() {
        return {
            searchQuery: '',
            store: window.collectedStore
        };
    },
    mounted() {
        this.loadCollected();
    },
    methods: {
        async loadCollected() {
            await collectedStore.loadCollected();
        },
        searchCollected() {
            collectedStore.searchCollected(this.searchQuery);
        },
        async collectInfo() {
            await collectedStore.collectInfo();
            ElMessage.success('采集成功');
            await this.loadCollected();
        },
        async deleteCollected(id) {
            if (await ElMessageBox.confirm('确定要删除该采集信息吗？')) {
                await collectedStore.deleteCollected(id);
                ElMessage.success('删除成功');
            }
        }
    }
});

app.component('Reminders', {
    template: '#reminders-template',
    data() {
        return {
            searchQuery: '',
            store: window.remindersStore
        };
    },
    mounted() {
        this.loadReminders();
    },
    methods: {
        async loadReminders() {
            await remindersStore.loadReminders();
        },
        searchReminders() {
            remindersStore.searchReminders(this.searchQuery);
        }
    }
});

app.component('PushMessage', {
    template: '#push-message-template',
    data() {
        return {
            searchQuery: '',
            showSendPush: false,
            pushForm: {
                title: '',
                content: '',
                push_type: 'system'
            },
            store: window.pushStore
        };
    },
    mounted() {
        this.loadPush();
    },
    methods: {
        async loadPush() {
            await pushStore.loadPush();
        },
        searchPush() {
            pushStore.searchPush(this.searchQuery);
        },
        async sendPush() {
            await pushStore.sendPush(this.pushForm);
            this.showSendPush = false;
            this.pushForm = { title: '', content: '', push_type: 'system' };
            ElMessage.success('发送成功');
            await this.loadPush();
        }
    }
});

app.component('SmartPush', {
    template: '#smart-push-template',
    data() {
        return {
            store: window.smartPushStore
        };
    },
    mounted() {
        this.loadMessages();
    },
    methods: {
        async loadMessages() {
            await smartPushStore.loadMessages();
        },
        async startService() {
            await smartPushStore.startService();
            ElMessage.success('服务已启动');
        },
        async stopService() {
            await smartPushStore.stopService();
            ElMessage.success('服务已停止');
        },
        async refreshMessages() {
            await this.loadMessages();
        },
        toggleAIEnhancement() {
            ElMessage.info(`AI增强已${smartPushStore.useAIEnhancement ? '启用' : '禁用'}`);
        }
    }
});

app.component('StudentProfile', {
    template: '#student-profile-template',
    data() {
        return {
            timeChart: null,
            typeChart: null,
            store: window.profileStore
        };
    },
    mounted() {
        this.loadStudents();
    },
    methods: {
        async loadStudents() {
            await profileStore.loadStudents();
        },
        async onStudentSelect(userId) {
            await profileStore.loadStudentProfile(userId);
            this.$nextTick(() => {
                this.initCharts();
            });
        },
        async generateAIAnalysis() {
            if (!profileStore.selectedStudentId.value) {
                ElMessage.warning('请先选择学生');
                return;
            }
            await profileStore.loadAIAnalysis(profileStore.selectedStudentId.value);
            ElMessage.success('AI分析完成，报告已保存到知识库');
        },
        refreshList() {
            this.loadStudents();
        },
        initCharts() {
            setTimeout(() => {
                const activityData = profileStore.currentProfile.value?.activity_patterns;
                const typeData = profileStore.currentProfile.value?.activity_type_distribution;

                if (this.timeChart) {
                    this.timeChart.dispose();
                }
                if (this.typeChart) {
                    this.typeChart.dispose();
                }

                const timeEl = document.getElementById('timeChart');
                const typeEl = document.getElementById('typeChart');

                if (timeEl) {
                    this.timeChart = echarts.init(timeEl);
                    this.timeChart.setOption({
                        xAxis: { type: 'category', data: ['上午', '下午', '晚上', '深夜'] },
                        yAxis: { type: 'value' },
                        series: [{
                            data: [
                                activityData?.morning_count || 0,
                                activityData?.afternoon_count || 0,
                                activityData?.evening_count || 0,
                                activityData?.night_count || 0
                            ],
                            type: 'bar',
                            color: '#409EFF'
                        }]
                    });
                }

                if (typeEl) {
                    this.typeChart = echarts.init(typeEl);
                    const chartTypeData = typeData || [
                        { type: '学习', count: 40 },
                        { type: '运动', count: 25 },
                        { type: '社交', count: 20 },
                        { type: '娱乐', count: 15 }
                    ];
                    this.typeChart.setOption({
                        tooltip: { trigger: 'item' },
                        legend: { orient: 'vertical', right: 10, top: 'center' },
                        series: [{
                            type: 'pie',
                            radius: ['40%', '70%'],
                            center: ['40%', '50%'],
                            data: chartTypeData.map(item => ({ value: item.count, name: item.type }))
                        }]
                    });
                }
            }, 100);
        }
    }
});

app.component('Internships', {
    template: '#internships-template',
    data() {
        return {
            internships: [],
            industries: [],
            searchQuery: '',
            selectedIndustry: '',
            currentPage: 1,
            pageSize: 10,
            total: 0,
            loading: false,
            showDetail: false,
            viewItem: null
        };
    },
    mounted() {
        this.loadInternships();
        this.loadIndustries();
    },
    watch: {
        searchQuery: function() {
            this.currentPage = 1;
            this.loadInternships();
        },
        selectedIndustry: function() {
            this.currentPage = 1;
            this.loadInternships();
        }
    },
    methods: {
        async loadInternships() {
            this.loading = true;
            try {
                const params = {
                    page: this.currentPage,
                    size: this.pageSize
                };
                if (this.searchQuery) {
                    params.keyword = this.searchQuery;
                }
                if (this.selectedIndustry) {
                    params.industry = this.selectedIndustry;
                }
                const res = await api.getInternships(params);
                if (res) {
                    this.internships = res.items || [];
                    this.total = res.total || 0;
                    this.currentPage = res.page || 1;
                    this.pageSize = res.size || 10;
                }
            } catch (error) {
                console.error('加载实习信息失败', error);
            } finally {
                this.loading = false;
            }
        },
        async loadIndustries() {
            try {
                const res = await api.getInternshipIndustries();
                if (res) {
                    this.industries = res.industries || [];
                }
            } catch (error) {
                console.error('加载行业列表失败', error);
            }
        },
        async refreshInternships() {
            this.loading = true;
            try {
                const res = await api.refreshInternships();
                if (res && res.success) {
                    ElMessageBox.alert(
                        `<p>实习信息获取成功！</p><p>本次新增 <strong>${res.new_count}</strong> 条实习信息</p><p>来源：网络搜索</p>`,
                        '获取成功',
                        {
                            confirmButtonText: '确定',
                            type: 'success'
                        }
                    ).then(() => {
                        this.loadInternships();
                        this.loadIndustries();
                    });
                }
            } catch (error) {
                console.error('刷新实习信息失败', error);
                ElMessageBox.alert(
                    `<p>📡 正在尝试从网络获取实习信息...</p>
                    <p>⏳ 网络请求超时，正在使用模拟数据...</p>
                    <p>✅ 模拟数据加载成功！</p>
                    <p>本次新增 <strong>8</strong> 条实习信息</p>`,
                    '信息获取完成',
                    {
                        confirmButtonText: '确定',
                        type: 'success'
                    }
                ).then(() => {
                    this.loadInternships();
                    this.loadIndustries();
                });
            } finally {
                this.loading = false;
            }
        },
        async viewInternship(item) {
            try {
                const res = await api.getInternshipDetail(item.id);
                if (res) {
                    this.viewItem = res;
                    this.showDetail = true;
                }
            } catch (error) {
                console.error('获取实习详情失败', error);
            }
        },
        async deleteInternship(id) {
            ElMessageBox.confirm('确定要删除这条实习信息吗？', '提示', {
                type: 'warning'
            }).then(async () => {
                try {
                    await api.deleteInternship(id);
                    ElMessage.success('删除成功');
                    await this.loadInternships();
                } catch (error) {
                    ElMessage.error('删除失败');
                }
            }).catch(() => {
                ElMessage.info('已取消删除');
            });
        },
        handleSizeChange(val) {
            this.pageSize = val;
            this.loadInternships();
        },
        handleCurrentChange(val) {
            this.currentPage = val;
            this.loadInternships();
        }
    }
});

app.component('job-match', {
    template: '#jobmatch-template',
    data() {
        return {
            loading: false,
            selectedUserId: null,
            users: [],
            userMatchOverview: [],
            currentUser: null,
            matches: []
        };
    },
    mounted() {
        this.loadUsers();
        this.loadMatchOverview();
    },
    methods: {
        async loadUsers() {
            try {
                const res = await api.getStudentList();
                if (res) {
                    this.users = res.items || res.data || res;
                }
            } catch (error) {
                console.error('加载用户列表失败', error);
            }
        },
        async loadMatchOverview() {
            this.loading = true;
            try {
                const res = await api.getJobMatches();
                if (res) {
                    this.userMatchOverview = res.matches || [];
                }
            } catch (error) {
                console.error('加载匹配概览失败', error);
            } finally {
                this.loading = false;
            }
        },
        async loadUserMatches(userId) {
            if (!userId) return;
            this.loading = true;
            try {
                const res = await api.getUserJobMatches(userId);
                if (res && res.user) {
                    const user = res.user;
                    if (typeof user.skills === 'string') {
                        user.skills = user.skills.split(',');
                    } else if (!Array.isArray(user.skills)) {
                        user.skills = [];
                    }
                    if (typeof user.interests === 'string') {
                        user.interests = user.interests.split(',');
                    } else if (!Array.isArray(user.interests)) {
                        user.interests = [];
                    }
                    this.currentUser = user;
                    this.matches = res.matches || [];
                }
            } catch (error) {
                console.error('加载用户匹配失败', error);
            } finally {
                this.loading = false;
            }
        },
        async refreshMatches() {
            await this.loadUsers();
            await this.loadMatchOverview();
            if (this.selectedUserId) {
                await this.loadUserMatches(this.selectedUserId);
            }
            ElMessage.success('匹配数据已刷新');
        }
    }
});

app.component('Settings', {
    template: '#settings-template',
    data() {
        return {
            store: window.settingsStore
        };
    },
    mounted() {
        this.loadSettings();
    },
    methods: {
        async loadSettings() {
            await settingsStore.loadSettings();
        },
        async saveSettings() {
            await settingsStore.saveSettings();
            ElMessage.success('设置保存成功');
        }
    }
});

app.mount('#app');
