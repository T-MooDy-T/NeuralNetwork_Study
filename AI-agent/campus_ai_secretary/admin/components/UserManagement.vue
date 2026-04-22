<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索用户名或昵称" 
                    style="width: 300px;"
                    @input="searchUsers"
                ></el-input>
            </div>
            <el-button type="primary" @click="showAddUser = true">添加用户</el-button>
        </div>

        <el-table 
            :data="usersStore.users" 
            border 
            style="width: 100%;"
            :loading="usersStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="username" label="用户名"></el-table-column>
            <el-table-column prop="nickname" label="昵称"></el-table-column>
            <el-table-column prop="email" label="邮箱"></el-table-column>
            <el-table-column prop="role" label="角色">
                <template #default="scope">
                    <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
                        {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态">
                <template #default="scope">
                    <el-tag :type="scope.row.is_active ? 'success' : 'warning'">
                        {{ scope.row.is_active ? '活跃' : '禁用' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
            <el-table-column label="操作" width="200">
                <template #default="scope">
                    <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="deleteUser(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog title="添加用户" v-model="showAddUser">
            <el-form :model="userForm" :rules="userRules" ref="userFormRef">
                <el-form-item prop="username">
                    <el-input v-model="userForm.username" placeholder="用户名"></el-input>
                </el-form-item>
                <el-form-item prop="nickname">
                    <el-input v-model="userForm.nickname" placeholder="昵称"></el-input>
                </el-form-item>
                <el-form-item prop="email">
                    <el-input v-model="userForm.email" placeholder="邮箱"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="userForm.password" type="password" placeholder="密码"></el-input>
                </el-form-item>
                <el-form-item prop="role">
                    <el-select v-model="userForm.role" placeholder="角色">
                        <el-option label="普通用户" value="user"></el-option>
                        <el-option label="管理员" value="admin"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddUser = false">取消</el-button>
                <el-button type="primary" @click="submitUser">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'UserManagement',
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
            userRules: {
                username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
                nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
                password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
            }
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
            this.$message.info('编辑功能开发中');
        },
        async deleteUser(userId) {
            if (await this.$confirm('确定要删除该用户吗？')) {
                await usersStore.deleteUser(userId);
                this.$message.success('删除成功');
            }
        },
        async submitUser() {
            await usersStore.createUser(this.userForm);
            this.showAddUser = false;
            this.userForm = { username: '', nickname: '', email: '', password: '', role: 'user' };
            this.$message.success('添加成功');
            await this.loadUsers();
        }
    }
};
</script>
