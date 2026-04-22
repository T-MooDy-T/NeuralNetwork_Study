<template>
    <div class="header">
        <h3>{{ title }}</h3>
        <div>
            <el-dropdown @command="handleCommand">
                <span style="cursor: pointer;">
                    <el-icon><component :is="'UserFilled'" /></el-icon>
                    {{ currentUser.username }}
                    <el-icon><component :is="'ArrowDown'" /></el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Header',
    props: {
        title: {
            type: String,
            default: ''
        },
        currentUser: {
            type: Object,
            default: () => ({ username: 'admin' })
        }
    },
    methods: {
        handleCommand(command) {
            if (command === 'logout') {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                this.$emit('logout');
            }
        }
    }
};
</script>
