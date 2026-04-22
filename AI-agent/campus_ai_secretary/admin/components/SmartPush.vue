<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <span style="margin-right: 20px;">服务状态：</span>
                <el-tag :type="smartPushStore.serviceStatus === 'running' ? 'success' : 'warning'">
                    {{ smartPushStore.serviceStatus === 'running' ? '运行中' : '已停止' }}
                </el-tag>
                <span style="margin-left: 20px; margin-right: 10px;">AI增强：</span>
                <el-switch 
                    v-model="smartPushStore.useAIEnhancement" 
                    active-text="已启用" 
                    inactive-text="已禁用"
                    @change="toggleAIEnhancement"
                ></el-switch>
            </div>
            <div>
                <el-button 
                    type="primary" 
                    @click="startService" 
                    v-if="smartPushStore.serviceStatus !== 'running'"
                >▶️ 启动服务</el-button>
                <el-button 
                    type="danger" 
                    @click="stopService" 
                    v-else
                >⏹️ 停止服务</el-button>
                <el-button @click="refreshMessages" style="margin-left: 10px;">🔄 刷新</el-button>
            </div>
        </div>

        <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
            <h4 style="margin-bottom: 15px;">推送消息列表</h4>
            <el-table 
                :data="smartPushStore.messages" 
                border 
                style="width: 100%;"
                :loading="smartPushStore.loading"
            >
                <el-table-column prop="id" label="ID" width="80"></el-table-column>
                <el-table-column prop="type" label="类型" width="100">
                    <template #default="scope">
                        <el-tag :type="{schedule: 'warning', knowledge: 'info', collected: 'primary', reminder: 'danger'}[scope.row.type]">
                            {{ {schedule: '日程', knowledge: '知识库', collected: '采集', reminder: '提醒'}[scope.row.type] }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="title" label="标题"></el-table-column>
                <el-table-column prop="content" label="内容"></el-table-column>
                <el-table-column prop="ai_enhanced" label="AI增强" width="100">
                    <template #default="scope">
                        <span v-if="scope.row.ai_enhanced">🤖</span>
                    </template>
                </el-table-column>
                <el-table-column prop="priority" label="优先级" width="100">
                    <template #default="scope">
                        <el-tag :type="{high: 'danger', medium: 'warning', low: 'success'}[scope.row.priority]">
                            {{ {high: '高', medium: '中', low: '低'}[scope.row.priority] }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SmartPush',
    mounted() {
        this.loadMessages();
    },
    methods: {
        async loadMessages() {
            await smartPushStore.loadMessages();
        },
        async startService() {
            await smartPushStore.startService();
            this.$message.success('服务已启动');
        },
        async stopService() {
            await smartPushStore.stopService();
            this.$message.success('服务已停止');
        },
        async refreshMessages() {
            await this.loadMessages();
        },
        async toggleAIEnhancement() {
            this.$message.info(`AI增强已${smartPushStore.useAIEnhancement ? '启用' : '禁用'}`);
        }
    }
};
</script>
