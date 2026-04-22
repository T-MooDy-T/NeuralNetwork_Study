<template>
    <div>
        <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
            <h4>系统设置</h4>
            
            <el-form :model="settingsStore.settings" style="margin-top: 20px;">
                <el-form-item label="AI增强开关">
                    <el-switch 
                        v-model="settingsStore.settings.ai_enabled" 
                        active-text="开启" 
                        inactive-text="关闭"
                    ></el-switch>
                </el-form-item>
                
                <el-form-item label="推送间隔（分钟）">
                    <el-input-number v-model="settingsStore.settings.push_interval" :min="1" :max="60"></el-input-number>
                </el-form-item>
                
                <el-form-item label="提醒提前时间（分钟）">
                    <el-input-number v-model="settingsStore.settings.reminder_advance" :min="1" :max="120"></el-input-number>
                </el-form-item>
                
                <el-form-item>
                    <el-button type="primary" @click="saveSettings">保存设置</el-button>
                </el-form-item>
            </el-form>
        </div>

        <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); margin-top: 20px;">
            <h4>系统信息</h4>
            <div style="margin-top: 15px;">
                <p><strong>版本：</strong>v1.0.0</p>
                <p><strong>运行状态：</strong><el-tag type="success">正常</el-tag></p>
                <p><strong>数据库：</strong>SQLite</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Settings',
    mounted() {
        this.loadSettings();
    },
    methods: {
        async loadSettings() {
            await settingsStore.loadSettings();
        },
        async saveSettings() {
            await settingsStore.saveSettings();
            this.$message.success('设置保存成功');
        }
    }
};
</script>
