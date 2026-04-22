<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索推送内容" 
                    style="width: 300px;"
                    @input="searchPush"
                ></el-input>
            </div>
            <el-button type="primary" @click="showSendPush = true">发送推送</el-button>
        </div>

        <el-table 
            :data="pushStore.pushList" 
            border 
            style="width: 100%;"
            :loading="pushStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="title" label="标题"></el-table-column>
            <el-table-column prop="content" label="内容"></el-table-column>
            <el-table-column prop="push_type" label="推送类型" width="120">
                <template #default="scope">
                    <el-tag type="info">{{ scope.row.push_type }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
                <template #default="scope">
                    <el-tag :type="scope.row.status === 'sent' ? 'success' : 'warning'">
                        {{ scope.row.status === 'sent' ? '已发送' : '待发送' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        </el-table>

        <el-dialog title="发送推送" v-model="showSendPush">
            <el-form :model="pushForm" :rules="pushRules" ref="pushFormRef">
                <el-form-item prop="title">
                    <el-input v-model="pushForm.title" placeholder="标题"></el-input>
                </el-form-item>
                <el-form-item prop="content">
                    <el-textarea v-model="pushForm.content" placeholder="内容" :rows="5"></el-textarea>
                </el-form-item>
                <el-form-item prop="push_type">
                    <el-select v-model="pushForm.push_type" placeholder="推送类型">
                        <el-option label="系统通知" value="system"></el-option>
                        <el-option label="日程提醒" value="schedule"></el-option>
                        <el-option label="消息通知" value="message"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showSendPush = false">取消</el-button>
                <el-button type="primary" @click="sendPush">发送</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'PushMessage',
    data() {
        return {
            searchQuery: '',
            showSendPush: false,
            pushForm: {
                title: '',
                content: '',
                push_type: 'system'
            },
            pushRules: {
                title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
                content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
            }
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
            this.$message.success('发送成功');
            await this.loadPush();
        }
    }
};
</script>
