<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索提醒内容" 
                    style="width: 300px;"
                    @input="searchReminders"
                ></el-input>
            </div>
        </div>

        <el-table 
            :data="remindersStore.reminders" 
            border 
            style="width: 100%;"
            :loading="remindersStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="user_id" label="用户ID" width="100"></el-table-column>
            <el-table-column prop="content" label="提醒内容"></el-table-column>
            <el-table-column prop="trigger_time" label="触发时间" width="180"></el-table-column>
            <el-table-column prop="status" label="状态">
                <template #default="scope">
                    <el-tag :type="scope.row.status === 'sent' ? 'success' : 'warning'">
                        {{ scope.row.status === 'sent' ? '已发送' : '待发送' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        </el-table>
    </div>
</template>

<script>
export default {
    name: 'Reminders',
    data() {
        return {
            searchQuery: ''
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
};
</script>
