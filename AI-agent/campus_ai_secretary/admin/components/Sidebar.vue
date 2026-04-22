<template>
    <div class="sidebar">
        <div class="sidebar-logo">🎓 校园 AI 秘书</div>
        <el-menu 
            :default-active="activeMenu"
            background-color="#001529"
            text-color="rgba(255,255,255,0.65)"
            active-text-color="#fff"
            class="sidebar-menu"
        >
            <el-menu-item index="dashboard" @click="handleMenuClick('dashboard')">
                <el-icon><component :is="'DataAnalysis'" /></el-icon>
                <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="users" @click="handleMenuClick('users')">
                <el-icon><component :is="'User'" /></el-icon>
                <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="schedules" @click="handleMenuClick('schedules')">
                <el-icon><component :is="'Calendar'" /></el-icon>
                <span>日程管理</span>
            </el-menu-item>
            <el-menu-item index="knowledge" @click="handleMenuClick('knowledge')">
                <el-icon><component :is="'Document'" /></el-icon>
                <span>知识库</span>
            </el-menu-item>
            <el-menu-item index="collected" @click="handleMenuClick('collected')">
                <el-icon><component :is="'Message'" /></el-icon>
                <span>采集信息</span>
            </el-menu-item>
            <el-menu-item index="reminders" @click="handleMenuClick('reminders')">
                <el-icon><component :is="'Bell'" /></el-icon>
                <span>提醒日志</span>
            </el-menu-item>
            <el-menu-item index="push" @click="handleMenuClick('push')">
                <span>📤</span>
                <span>消息推送</span>
            </el-menu-item>
            <el-menu-item index="smartpush" @click="handleMenuClick('smartpush')">
                <el-icon><component :is="'Cpu'" /></el-icon>
                <span>智能推送</span>
            </el-menu-item>
            <el-menu-item index="profile" @click="handleMenuClick('profile')">
                <el-icon><component :is="'UserFilled'" /></el-icon>
                <span>学生画像</span>
            </el-menu-item>
            <el-menu-item index="settings" @click="handleMenuClick('settings')">
                <el-icon><component :is="'Setting'" /></el-icon>
                <span>系统设置</span>
            </el-menu-item>
        </el-menu>
    </div>
</template>

<script>
export default {
    name: 'Sidebar',
    props: {
        activeMenu: {
            type: String,
            default: 'dashboard'
        }
    },
    methods: {
        handleMenuClick(menu) {
            this.$emit('menu-change', menu);
        }
    }
};
</script>
