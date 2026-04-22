<template>
    <div class="login-container">
        <div class="login-box">
            <h2 class="login-title">🎓 校园 AI 秘书</h2>
            <h3 style="text-align: center; margin-bottom: 20px; color: #666;">管理后台</h3>
            
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
                <el-form-item prop="username">
                    <el-input 
                        v-model="loginForm.username" 
                        placeholder="用户名"
                        prefix-icon="User"
                        size="large"
                    ></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input 
                        v-model="loginForm.password" 
                        type="password"
                        placeholder="密码"
                        prefix-icon="Lock"
                        size="large"
                        @keyup.enter="handleLogin"
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button 
                        type="primary" 
                        @click="handleLogin" 
                        size="large"
                        :loading="loading"
                        style="width: 100%;"
                    >登录</el-button>
                </el-form-item>
            </el-form>
            
            <div style="text-align: center; color: #999; font-size: 12px; margin-top: 15px;">
                默认账号：admin / admin123
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Login',
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            loginRules: {
                username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
            loading: false
        };
    },
    methods: {
        async handleLogin() {
            if (!this.loginForm.username || !this.loginForm.password) {
                this.$message.error('请输入用户名和密码');
                return;
            }
            
            this.loading = true;
            try {
                const response = await axios.post('/api/v1/auth/login', {
                    username: this.loginForm.username,
                    password: this.loginForm.password
                });
                
                if (response.data.success) {
                    localStorage.setItem('token', response.data.access_token);
                    localStorage.setItem('user', JSON.stringify(response.data.user));
                    this.$emit('login-success');
                } else {
                    this.$message.error(response.data.message || '登录失败');
                }
            } catch (error) {
                console.error('登录失败:', error);
                this.$message.error('登录失败，请检查用户名和密码');
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
