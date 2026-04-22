window.dashboardStore = {
    stats: Vue.reactive({
        users: {},
        schedules: {},
        reminders: {},
        knowledge: {},
        scheduleChart: [0, 0, 0, 0, 0, 0, 0],
        reminderChart: [0, 0, 0, 0, 0, 0, 0]
    }),
    
    loadStats: async () => {
        try {
            const res = await api.getDashboardStats();
            if (res) {
                window.dashboardStore.stats.users = res.users || {};
                window.dashboardStore.stats.schedules = res.schedules || {};
                window.dashboardStore.stats.reminders = res.reminders || {};
                window.dashboardStore.stats.knowledge = res.knowledge_base || {};
            }
            
            await window.dashboardStore.loadChartData();
        } catch (error) {
            console.error('加载统计数据失败', error);
        }
    },
    
    loadChartData: async () => {
        try {
            const scheduleRes = await api.getScheduleChart(7);
            const scheduleData = scheduleRes.data || [{ date: '04-15', total: 0, completed: 0 }, { date: '04-16', total: 0, completed: 0 }, { date: '04-17', total: 0, completed: 0 }, { date: '04-18', total: 0, completed: 0 }, { date: '04-19', total: 0, completed: 0 }, { date: '04-20', total: 0, completed: 0 }, { date: '04-21', total: 0, completed: 0 }];
            window.dashboardStore.stats.scheduleChart = scheduleData.map(d => d.total);
            
            const reminderRes = await api.getReminderChart(7);
            const reminderData = reminderRes.data || [{ date: '04-15', count: 0 }, { date: '04-16', count: 0 }, { date: '04-17', count: 0 }, { date: '04-18', count: 0 }, { date: '04-19', count: 0 }, { date: '04-20', count: 0 }, { date: '04-21', count: 0 }];
            window.dashboardStore.stats.reminderChart = reminderData.map(d => d.count);
        } catch (error) {
            console.error('加载图表数据失败', error);
        }
    },
    
    loadUserChart: async () => {
        try {
            const chartDom = document.getElementById('userChart');
            if (!chartDom) return;
            const res = await api.getUserChart(7);
            const chart = echarts.init(chartDom);
            const chartData = res.data || [{ date: '04-15', count: 0 }, { date: '04-16', count: 0 }, { date: '04-17', count: 0 }, { date: '04-18', count: 0 }, { date: '04-19', count: 0 }, { date: '04-20', count: 0 }, { date: '04-21', count: 0 }];
            chart.setOption({
                tooltip: { trigger: 'axis' },
                xAxis: {
                    type: 'category',
                    data: chartData.map(d => d.date.slice(5))
                },
                yAxis: { type: 'value' },
                series: [{
                    data: chartData.map(d => d.count),
                    type: 'line',
                    smooth: true,
                    areaStyle: { opacity: 0.3 },
                    itemStyle: { color: '#409EFF' }
                }]
            });
        } catch (error) {
            console.error('加载用户图表失败', error);
        }
    },
    
    loadScheduleChart: async () => {
        try {
            const chartDom = document.getElementById('scheduleChart');
            if (!chartDom) return;
            const res = await api.getScheduleChart(7);
            const chart = echarts.init(chartDom);
            const chartData = res.data || [{ date: '04-15', total: 0, completed: 0 }, { date: '04-16', total: 0, completed: 0 }, { date: '04-17', total: 0, completed: 0 }, { date: '04-18', total: 0, completed: 0 }, { date: '04-19', total: 0, completed: 0 }, { date: '04-20', total: 0, completed: 0 }, { date: '04-21', total: 0, completed: 0 }];
            chart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['总日程', '已完成'] },
                xAxis: {
                    type: 'category',
                    data: chartData.map(d => d.date.slice(5))
                },
                yAxis: { type: 'value' },
                series: [
                    {
                        name: '总日程',
                        data: chartData.map(d => d.total),
                        type: 'bar',
                        itemStyle: { color: '#409EFF' }
                    },
                    {
                        name: '已完成',
                        data: chartData.map(d => d.completed),
                        type: 'bar',
                        itemStyle: { color: '#67C23A' }
                    }
                ]
            });
        } catch (error) {
            console.error('加载日程图表失败', error);
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