window.smartPushStore = {
    pushHistory: Vue.reactive([]),
    pendingMessages: Vue.reactive([]),
    delayQueue: Vue.reactive([]),
    pushedMessageIds: Vue.reactive(new Set()),
    isRunning: Vue.ref(false),
    lastCheckTime: Vue.ref(null),
    timeoutId: null,
    dailyUpdateId: null,
    useAIEnhancement: Vue.ref(true),
    messages: Vue.reactive([]),
    serviceStatus: Vue.ref('stopped'),
    loading: Vue.reactive({ value: false }),
    
    loadMessages: async () => {
        window.smartPushStore.loading.value = true;
        try {
            await window.smartPushStore.getPushHistory();
            window.smartPushStore.messages = [...window.smartPushStore.pushHistory];
            window.smartPushStore.serviceStatus.value = window.smartPushStore.isRunning.value ? 'running' : 'stopped';
        } catch (error) {
            console.error('加载消息失败:', error);
        } finally {
            window.smartPushStore.loading.value = false;
        }
    },
    
    startService: async () => {
        await window.smartPushStore.startSmartPush();
        window.smartPushStore.serviceStatus.value = 'running';
    },
    
    stopService: async () => {
        await window.smartPushStore.stopSmartPush();
        window.smartPushStore.serviceStatus.value = 'stopped';
    },
    
    priorityMap: {
        high: 3,
        medium: 2,
        low: 1,
        normal: 1
    },
    
    async startSmartPush() {
        if (this.isRunning.value) return;
        this.isRunning.value = true;
        
        this.pushedMessageIds.clear();
        this.delayQueue.splice(0, this.delayQueue.length);
        
        ElementPlus.ElMessage.info('智能推送服务已启动');
        await this.checkAndPush();
        this.scheduleNextCheck();
        this.scheduleDailyUpdate();
    },
    
    async stopSmartPush() {
        this.isRunning.value = false;
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
        if (this.dailyUpdateId) {
            clearTimeout(this.dailyUpdateId);
            this.dailyUpdateId = null;
        }
        ElementPlus.ElMessage.info('智能推送服务已停止');
    },
    
    scheduleNextCheck() {
        if (!this.isRunning.value) return;
        this.timeoutId = setTimeout(async () => {
            await this.checkAndPush();
            this.scheduleNextCheck();
        }, 30000);
    },
    
    scheduleDailyUpdate() {
        if (!this.isRunning.value) return;
        const now = new Date();
        const nextMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
        const delay = nextMidnight - now;
        
        this.dailyUpdateId = setTimeout(() => {
            this.executeDailyUpdate();
            this.scheduleDailyUpdate();
        }, delay);
    },
    
    async executeDailyUpdate() {
        if (!this.isRunning.value) return;
        console.log('[智能推送] 执行每日更新');
        
        const longTermTasks = this.pendingMessages.filter(msg => {
            const msgTime = new Date(msg.time);
            const diff = msgTime - new Date();
            return diff > 86400000 && !this.pushedMessageIds.has(msg.id);
        });
        
        for (const task of longTermTasks) {
            const daysLeft = Math.ceil((new Date(task.time) - new Date()) / 86400000);
            const updatedMsg = {
                ...task,
                content: `${task.content.replace(/剩余.*天/, '')}（剩余${daysLeft}天）`
            };
            
            this.pushedMessageIds.add(task.id);
            await this.pushMessage(updatedMsg);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    },
    
    async checkAndPush() {
        if (!this.isRunning.value) return;
        try {
            this.lastCheckTime.value = new Date().toLocaleString('zh-CN');
            await this.collectAllData();
            await this.processDelayQueue();
            await this.analyzeAndPrioritize();
            await this.executePush();
        } catch (error) {
            console.error('智能推送检查失败:', error);
        }
    },
    
    async processDelayQueue() {
        const now = new Date();
        
        const readyToPush = this.delayQueue.filter(item => {
            const msgTime = new Date(item.time);
            const diff = msgTime - now;
            return diff <= 7200000;
        });
        
        readyToPush.forEach(item => {
            const index = this.delayQueue.findIndex(d => d.id === item.id);
            if (index > -1) {
                this.delayQueue.splice(index, 1);
            }
            if (!this.pushedMessageIds.has(item.id)) {
                this.pendingMessages.push(item);
            }
        });
    },
    
    async collectAllData() {
        this.pendingMessages.splice(0, this.pendingMessages.length);
        
        try {
            const [schedulesRes, knowledgeRes, collectedRes, remindersRes] = await Promise.all([
                api.getSchedules({ page: 1, page_size: 50 }),
                api.getKnowledge({ page: 1, page_size: 50 }),
                api.getCollectedInfo({ page: 1, page_size: 50 }),
                api.getReminders({ page: 1, page_size: 50 })
            ]);
            
            const rawMessages = [];
            
            schedulesRes.items?.forEach(schedule => {
                if (schedule.status === 'pending') {
                    rawMessages.push({
                        id: `schedule_${schedule.id}`,
                        type: 'schedule',
                        title: '日程提醒',
                        content: `${schedule.event_name} 将在 ${this.formatTime(schedule.start_time)} 开始`,
                        priority: schedule.priority || 'medium',
                        time: schedule.start_time,
                        userId: schedule.user_id,
                        username: schedule.username,
                        originalContent: `${schedule.event_name} 将在 ${this.formatTime(schedule.start_time)} 开始`,
                        originalData: schedule
                    });
                }
            });
            
            knowledgeRes.items?.forEach(item => {
                if (item.is_active && item.view_count < 5) {
                    rawMessages.push({
                        id: `knowledge_${item.id}`,
                        type: 'knowledge',
                        title: '知识库推荐',
                        content: `推荐阅读：${item.title}`,
                        priority: 'medium',
                        time: item.created_at,
                        userId: null,
                        username: null,
                        originalData: item
                    });
                }
            });
            
            collectedRes.items?.forEach(item => {
                if (item.status === 'unread') {
                    rawMessages.push({
                        id: `collected_${item.id}`,
                        type: 'collected',
                        title: '新采集信息',
                        content: `来自${this.getSourceTypeName(item.source_type)}的消息：${item.content?.slice(0, 50)}...`,
                        priority: item.priority || 'normal',
                        time: item.timestamp,
                        userId: null,
                        username: null,
                        originalData: item
                    });
                }
            });
            
            remindersRes.items?.forEach(item => {
                if (item.status !== 'sent') {
                    rawMessages.push({
                        id: `reminder_${item.id}`,
                        type: 'reminder',
                        title: '提醒通知',
                        content: `${item.event_name} 的提醒`,
                        priority: 'high',
                        time: item.remind_time,
                        userId: null,
                        username: item.username,
                        originalData: item
                    });
                }
            });
            
            if (this.useAIEnhancement.value) {
                await this.enhanceWithAI(rawMessages);
            } else {
                this.pendingMessages.push(...rawMessages);
            }
        } catch (error) {
            console.error('收集数据失败:', error);
        }
    },
    
    async enhanceWithAI(rawMessages) {
        console.log('[智能推送] 开始AI内容增强...');
        console.log(`[智能推送] 需要增强消息数: ${rawMessages.length}`);
        
        const enhancedMessages = [];
        const successCount = { schedule: 0, knowledge: 0, collected: 0, reminder: 0 };
        const failCount = { schedule: 0, knowledge: 0, collected: 0, reminder: 0 };
        
        for (const msg of rawMessages) {
            try {
                const response = await api.generatePushContent({
                    type: msg.type,
                    item: msg.originalData
                }, {
                    timeout: 30000
                });
                
                if (response.success) {
                    enhancedMessages.push({
                        ...msg,
                        content: response.generated_content,
                        title: response.original_title || msg.title,
                        priority: response.priority || msg.priority,
                        enhanced: true
                    });
                    successCount[msg.type] = (successCount[msg.type] || 0) + 1;
                } else {
                    enhancedMessages.push(msg);
                    failCount[msg.type] = (failCount[msg.type] || 0) + 1;
                }
                
                await new Promise(resolve => setTimeout(resolve, 500));
            } catch (error) {
                console.warn(`[智能推送] AI增强失败 (${msg.type}):`, error.message);
                failCount[msg.type] = (failCount[msg.type] || 0) + 1;
                enhancedMessages.push(msg);
            }
        }
        
        this.pendingMessages.push(...enhancedMessages);
        
        const totalSuccess = Object.values(successCount).reduce((a, b) => a + b, 0);
        const totalFail = Object.values(failCount).reduce((a, b) => a + b, 0);
        console.log(`[智能推送] AI内容增强完成 - 成功: ${totalSuccess}, 失败: ${totalFail}`);
        
        if (totalFail > 0) {
            ElementPlus.ElMessage.warning(`AI内容增强部分失败，${totalFail}条消息使用原始内容`);
        }
    },
    
    analyzeAndPrioritize() {
        this.pendingMessages.sort((a, b) => {
            const priorityDiff = this.priorityMap[b.priority] - this.priorityMap[a.priority];
            if (priorityDiff !== 0) return priorityDiff;
            return new Date(a.time) - new Date(b.time);
        });
    },
    
    async executePush() {
        if (!this.isRunning.value) return;
        
        const now = new Date();
        console.log('[智能推送] 当前时间:', now.toLocaleString('zh-CN'));
        console.log('[智能推送] 待推送消息总数:', this.pendingMessages.length);
        console.log('[智能推送] 延迟队列消息数:', this.delayQueue.length);
        console.log('[智能推送] 已推送消息数:', this.pushedMessageIds.size);
        
        const immediateMessages = [];
        const delayMessages = [];
        
        this.pendingMessages.forEach(msg => {
            if (!this.isRunning.value) return;
            if (this.pushedMessageIds.has(msg.id)) return;
            
            const msgTime = new Date(msg.time);
            const diff = msgTime - now;
            
            console.log('[智能推送] 消息:', msg.title, '- 时间:', msg.time, '- 差值:', Math.round(diff / 60000), '分钟');
            
            if (diff <= 7200000 && diff > -86400000) {
                immediateMessages.push(msg);
            } else if (diff > 7200000 && diff <= 86400000) {
                const exists = this.delayQueue.some(d => d.id === msg.id);
                if (!exists) {
                    delayMessages.push(msg);
                }
            }
        });
        
        delayMessages.forEach(msg => {
            const exists = this.delayQueue.some(d => d.id === msg.id);
            if (!exists) {
                this.delayQueue.push(msg);
                console.log('[智能推送] 加入延迟队列:', msg.title);
            }
        });
        
        console.log('[智能推送] 立即推送消息数:', immediateMessages.length);
        console.log('[智能推送] 延迟队列消息数:', this.delayQueue.length);
        
        for (const msg of immediateMessages.slice(0, 5)) {
            if (!this.isRunning.value) {
                console.log('[智能推送] 服务已停止，中断推送');
                break;
            }
            
            if (this.pushedMessageIds.has(msg.id)) {
                console.log('[智能推送] 已推送过，跳过:', msg.title);
                continue;
            }
            
            console.log('[智能推送] 正在推送:', msg.title);
            this.pushedMessageIds.add(msg.id);
            const index = this.pendingMessages.findIndex(m => m.id === msg.id);
            if (index > -1) {
                this.pendingMessages.splice(index, 1);
            }
            await this.pushMessage(msg);
            await new Promise(resolve => setTimeout(resolve, 1500));
        }
        
        await this.processDelayQueue();
    },
    
    async processDelayQueue() {
        if (!this.isRunning.value) return;
        
        const now = new Date();
        const readyMessages = [];
        
        for (let i = this.delayQueue.length - 1; i >= 0; i--) {
            const msg = this.delayQueue[i];
            const msgTime = new Date(msg.time);
            const diff = msgTime - now;
            
            if (diff <= 7200000) {
                readyMessages.push(msg);
                this.delayQueue.splice(i, 1);
            }
        }
        
        console.log('[智能推送] 延迟队列就绪消息数:', readyMessages.length);
        
        for (const msg of readyMessages) {
            if (!this.isRunning.value) break;
            
            if (this.pushedMessageIds.has(msg.id)) {
                console.log('[智能推送] 延迟队列消息已推送过，跳过:', msg.title);
                continue;
            }
            
            console.log('[智能推送] 延迟队列推送:', msg.title);
            this.pushedMessageIds.add(msg.id);
            const index = this.pendingMessages.findIndex(m => m.id === msg.id);
            if (index > -1) {
                this.pendingMessages.splice(index, 1);
            }
            await this.pushMessage(msg);
            await new Promise(resolve => setTimeout(resolve, 1500));
        }
    },
    
    async pushMessage(msg) {
        const pushRecord = {
            id: msg.id,
            type: msg.type,
            title: msg.title,
            content: msg.content,
            priority: msg.priority,
            username: msg.username || '系统推送',
            pushTime: new Date().toLocaleString('zh-CN'),
            status: 'success'
        };
        
        this.pushHistory.unshift(pushRecord);
        if (this.pushHistory.length > 50) {
            this.pushHistory.pop();
        }
        
        console.log('[智能推送] 显示弹窗:', msg.title);
        
        try {
            await ElementPlus.ElMessageBox.alert(
                `<div style="padding: 10px;">
                    <p><strong>📤 ${msg.title}</strong></p>
                    <p style="margin-top: 10px;">${msg.content}</p>
                    <p style="margin-top: 10px; font-size: 12px; color: #999;">
                        优先级：${this.getPriorityLabel(msg.priority)} | 用户：${msg.username || '全体'}
                    </p>
                </div>`,
                '智能消息推送',
                {
                    confirmButtonText: '知道了',
                    dangerouslyUseHTMLString: true,
                    customClass: 'smart-push-modal'
                }
            );
        } catch (error) {
            console.log('[智能推送] 弹窗关闭');
        }
        
        await this.logPush(pushRecord);
    },
    
    async logPush(record) {
        try {
            await api.logPush(record);
        } catch (error) {
            console.error('记录推送日志失败:', error);
        }
    },
    
    getSourceTypeName(type) {
        const types = {
            qq_group: 'QQ群',
            wechat_chat: '微信群',
            wechat_official: '公众号'
        };
        return types[type] || type;
    },
    
    getPriorityLabel(priority) {
        const labels = {
            high: '🔴 高',
            medium: '🟡 中',
            low: '🟢 低',
            normal: '🟢 低'
        };
        return labels[priority] || priority;
    },
    
    formatTime(timeStr) {
        if (!timeStr) return '-';
        const date = new Date(timeStr);
        return date.toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    async getPushHistory() {
        try {
            const res = await api.getPushHistory();
            if (res.items) {
                this.pushHistory = [...res.items, ...this.pushHistory].slice(0, 50);
            }
        } catch (error) {
            console.error('获取推送历史失败:', error);
        }
    }
};