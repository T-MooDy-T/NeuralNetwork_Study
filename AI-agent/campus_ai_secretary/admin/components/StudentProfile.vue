<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="width: 300px;">
                <el-select 
                    v-model="profileStore.selectedStudentId.value" 
                    placeholder="请选择学生"
                    style="width: 100%;"
                    @change="onStudentSelect"
                >
                    <el-option 
                        v-for="student in profileStore.students.value" 
                        :key="student.id" 
                        :label="student.nickname" 
                        :value="student.id"
                    ></el-option>
                </el-select>
            </div>
            <div>
                <el-button type="primary" @click="generateAIAnalysis" :disabled="!profileStore.selectedStudentId.value">
                    🤖 AI分析
                </el-button>
                <el-button @click="refreshList" style="margin-left: 10px;">🔄 刷新列表</el-button>
            </div>
        </div>

        <div v-if="!profileStore.currentProfile.value" style="text-align: center; padding: 40px; color: #999;">
            <el-icon size="48" style="margin-bottom: 10px;">UserFilled</el-icon>
            <p>请选择学生查看画像</p>
        </div>

        <div v-else>
            <div class="stats-grid" style="margin-bottom: 20px;">
                <div class="stat-card">
                    <div class="stat-label">总日程数</div>
                    <div class="stat-value">{{ profileStore.currentProfile.value?.learning_stats?.total_schedules || 0 }}</div>
                    <div style="color: #67C23A; font-size: 12px;">已完成：{{ profileStore.currentProfile.value?.learning_stats?.completed_schedules || 0 }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">待处理</div>
                    <div class="stat-value">{{ profileStore.currentProfile.value?.learning_stats?.pending_schedules || 0 }}</div>
                    <div style="color: #E6A23C; font-size: 12px;">平均优先级：{{ profileStore.currentProfile.value?.learning_stats?.average_priority }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">最活跃时段</div>
                    <div class="stat-value">{{ profileStore.currentProfile.value?.activity_patterns?.most_active_hour }}</div>
                    <div style="color: #666; font-size: 12px;">{{ profileStore.currentProfile.value?.activity_patterns?.most_active_day }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">注册时间</div>
                    <div class="stat-value">{{ profileStore.formatDate(profileStore.currentProfile.value?.basic_info?.created_at) }}</div>
                </div>
            </div>

            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <h4>个人信息</h4>
                    <div style="margin-top: 15px;">
                        <p><strong>用户名：</strong>{{ profileStore.currentProfile.value?.basic_info?.username }}</p>
                        <p><strong>昵称：</strong>{{ profileStore.currentProfile.value?.basic_info?.nickname }}</p>
                        <p><strong>邮箱：</strong>{{ profileStore.currentProfile.value?.basic_info?.email }}</p>
                        <p><strong>状态：</strong><el-tag :type="profileStore.currentProfile.value?.basic_info?.is_active ? 'success' : 'warning'">{{ profileStore.currentProfile.value?.basic_info?.is_active ? '活跃' : '禁用' }}</el-tag></p>
                    </div>
                </div>
                <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <h4>兴趣爱好</h4>
                    <div style="margin-top: 15px;">
                        <el-tag v-for="interest in profileStore.currentProfile.value?.preferences?.interests" :key="interest" type="info" style="margin-right: 10px; margin-bottom: 10px;">
                            {{ interest }}
                        </el-tag>
                    </div>
                    <h4 style="margin-top: 20px;">偏好课程</h4>
                    <div style="margin-top: 15px;">
                        <el-tag v-for="course in profileStore.currentProfile.value?.preferences?.favorite_courses" :key="course" type="success" style="margin-right: 10px; margin-bottom: 10px;">
                            {{ course }}
                        </el-tag>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <h4>活动时间分布</h4>
                    <div id="timeChart" style="height: 200px; margin-top: 15px;"></div>
                </div>
                <div style="flex: 1; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <h4>活动类型分布</h4>
                    <div id="typeChart" style="height: 200px; margin-top: 15px;"></div>
                </div>
            </div>

            <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h4>最近活动</h4>
                <el-table :data="profileStore.currentProfile.value?.recent_activities" border style="width: 100%; margin-top: 15px;">
                    <el-table-column prop="event_name" label="活动名称"></el-table-column>
                    <el-table-column prop="location" label="地点"></el-table-column>
                    <el-table-column prop="start_time" label="时间"></el-table-column>
                    <el-table-column prop="status" label="状态">
                        <template #default="scope">
                            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">{{ scope.row.status === 'completed' ? '已完成' : '进行中' }}</el-tag>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <div v-if="profileStore.aiAnalysis.value" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                <h4>🤖 AI分析报告</h4>
                <div style="margin-top: 15px; padding: 15px; background: #f9fafb; border-radius: 8px; white-space: pre-wrap;">
                    {{ profileStore.aiAnalysis.value?.analysis }}
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'StudentProfile',
    data() {
        return {
            timeChart: null,
            typeChart: null
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
                this.$message.warning('请先选择学生');
                return;
            }
            await profileStore.loadAIAnalysis(profileStore.selectedStudentId.value);
            this.$message.success('AI分析完成，报告已保存到知识库');
        },
        refreshList() {
            this.loadStudents();
        },
        initCharts() {
            const activityData = profileStore.currentProfile.value?.activity_patterns;
            const typeData = profileStore.currentProfile.value?.activity_type_distribution;

            if (this.timeChart) {
                this.timeChart.dispose();
            }
            if (this.typeChart) {
                this.typeChart.dispose();
            }

            this.timeChart = echarts.init(document.getElementById('timeChart'));
            this.typeChart = echarts.init(document.getElementById('typeChart'));

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

            const typeLabels = typeData?.map(item => item.type) || [];
            const typeValues = typeData?.map(item => item.count) || [];

            this.typeChart.setOption({
                series: [{
                    type: 'pie',
                    data: typeData?.map(item => ({ value: item.count, name: item.type })) || []
                }]
            });
        }
    }
};
</script>
