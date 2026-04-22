<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索日程名称" 
                    style="width: 300px;"
                    @input="searchSchedules"
                ></el-input>
            </div>
            <el-button type="primary" @click="showAddSchedule = true">添加日程</el-button>
        </div>

        <el-table 
            :data="schedulesStore.schedules" 
            border 
            style="width: 100%;"
            :loading="schedulesStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="event_name" label="日程名称"></el-table-column>
            <el-table-column prop="location" label="地点"></el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="180"></el-table-column>
            <el-table-column prop="priority" label="优先级">
                <template #default="scope">
                    <el-tag :type="{high: 'danger', medium: 'warning', low: 'success'}[scope.row.priority]">
                        {{ {high: '高', medium: '中', low: '低'}[scope.row.priority] }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
                <template #default="scope">
                    <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                        {{ scope.row.status === 'completed' ? '已完成' : '进行中' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="description" label="描述"></el-table-column>
            <el-table-column label="操作" width="200">
                <template #default="scope">
                    <el-button size="small" @click="editSchedule(scope.row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="deleteSchedule(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog title="添加日程" v-model="showAddSchedule">
            <el-form :model="scheduleForm" :rules="scheduleRules" ref="scheduleFormRef">
                <el-form-item prop="event_name">
                    <el-input v-model="scheduleForm.event_name" placeholder="日程名称"></el-input>
                </el-form-item>
                <el-form-item prop="location">
                    <el-input v-model="scheduleForm.location" placeholder="地点"></el-input>
                </el-form-item>
                <el-form-item prop="start_time">
                    <el-date-picker v-model="scheduleForm.start_time" type="datetime" placeholder="开始时间"></el-date-picker>
                </el-form-item>
                <el-form-item prop="priority">
                    <el-select v-model="scheduleForm.priority" placeholder="优先级">
                        <el-option label="高" value="high"></el-option>
                        <el-option label="中" value="medium"></el-option>
                        <el-option label="低" value="low"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item prop="description">
                    <el-textarea v-model="scheduleForm.description" placeholder="描述"></el-textarea>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddSchedule = false">取消</el-button>
                <el-button type="primary" @click="submitSchedule">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'ScheduleManagement',
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
            scheduleRules: {
                event_name: [{ required: true, message: '请输入日程名称', trigger: 'blur' }],
                start_time: [{ required: true, message: '请选择开始时间', trigger: 'blur' }]
            }
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
            this.$message.info('编辑功能开发中');
        },
        async deleteSchedule(scheduleId) {
            if (await this.$confirm('确定要删除该日程吗？')) {
                await schedulesStore.deleteSchedule(scheduleId);
                this.$message.success('删除成功');
            }
        },
        async submitSchedule() {
            await schedulesStore.createSchedule(this.scheduleForm);
            this.showAddSchedule = false;
            this.scheduleForm = { event_name: '', location: '', start_time: '', priority: 'medium', description: '' };
            this.$message.success('添加成功');
            await this.loadSchedules();
        }
    }
};
</script>
