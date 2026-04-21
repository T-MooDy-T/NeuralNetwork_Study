window.dashboardStore = {
    stats: {},
    
    loadUserChart: async () => {
        try {
            const chartDom = document.getElementById('userChart');
            if (!chartDom) return;
            const res = await api.getUserChart(7);
            const chart = echarts.init(chartDom);
            chart.setOption({
                tooltip: { trigger: 'axis' },
                xAxis: {
                    type: 'category',
                    data: res.data.map(d => d.date.slice(5))
                },
                yAxis: { type: 'value' },
                series: [{
                    data: res.data.map(d => d.count),
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
            chart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['总日程', '已完成'] },
                xAxis: {
                    type: 'category',
                    data: res.data.map(d => d.date.slice(5))
                },
                yAxis: { type: 'value' },
                series: [
                    {
                        name: '总日程',
                        data: res.data.map(d => d.total),
                        type: 'bar',
                        itemStyle: { color: '#409EFF' }
                    },
                    {
                        name: '已完成',
                        data: res.data.map(d => d.completed),
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