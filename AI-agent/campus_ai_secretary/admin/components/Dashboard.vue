<template>
    <div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">总用户数</div>
                <div class="stat-value">{{ dashboardStore.stats.users?.total || 0 }}</div>
                <div style="color: #67C23A; font-size: 12px;">活跃：{{ dashboardStore.stats.users?.active || 0 }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">总日程数</div>
                <div class="stat-value">{{ dashboardStore.stats.schedules?.total || 0 }}</div>
                <div style="color: #666; font-size: 12px;">今日：{{ dashboardStore.stats.schedules?.today || 0 }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">提醒总数</div>
                <div class="stat-value">{{ dashboardStore.stats.reminders?.total || 0 }}</div>
                <div style="color: #666; font-size: 12px;">今日：{{ dashboardStore.stats.reminders?.today || 0 }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">知识库条目</div>
                <div class="stat-value">{{ dashboardStore.stats.knowledge?.total || 0 }}</div>
                <div style="color: #666; font-size: 12px;">今日新增：{{ dashboardStore.stats.knowledge?.today || 0 }}</div>
            </div>
        </div>

        <div style="display: flex; gap: 20px; margin-top: 20px;">
            <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                <h4 style="margin-bottom: 15px;">日程统计</h4>
                <div id="scheduleChart" style="height: 250px;"></div>
            </div>
            <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                <h4 style="margin-bottom: 15px;">提醒统计</h4>
                <div id="reminderChart" style="height: 250px;"></div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Dashboard',
    data() {
        return {
            scheduleChart: null,
            reminderChart: null
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
            this.scheduleChart = echarts.init(document.getElementById('scheduleChart'));
            this.reminderChart = echarts.init(document.getElementById('reminderChart'));
            this.updateCharts();
        },
        updateCharts() {
            const scheduleData = dashboardStore.stats.scheduleChart || [0, 0, 0, 0, 0, 0, 0];
            const reminderData = dashboardStore.stats.reminderChart || [0, 0, 0, 0, 0, 0, 0];
            const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

            this.scheduleChart.setOption({
                xAxis: { type: 'category', data: days },
                yAxis: { type: 'value' },
                series: [{ data: scheduleData, type: 'bar', color: '#409EFF' }]
            });

            this.reminderChart.setOption({
                xAxis: { type: 'category', data: days },
                yAxis: { type: 'value' },
                series: [{ data: reminderData, type: 'bar', color: '#67C23A' }]
            });
        }
    }
};
</script>
