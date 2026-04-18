<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">📈</span>
          <span class="logo-text">股价预测系统</span>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item">首页</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="app-footer">
      <p>© 2024 股价预测系统 - 仅供学习研究使用</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style>
:root {
  --header-height: 60px;
  --footer-height: 60px;
  --mobile-padding: 12px;
  --tablet-padding: 16px;
  --desktop-padding: 24px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 14px;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #f5f7fa;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--mobile-padding);
  height: var(--header-height);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 20px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
}

.nav-menu {
  display: flex;
  gap: 16px;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.app-main {
  flex: 1;
  padding: var(--mobile-padding);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  text-align: center;
  padding: 12px var(--mobile-padding);
  background-color: #fff;
  border-top: 1px solid #e8e8e8;
  color: #666;
  font-size: 12px;
  height: var(--footer-height);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media screen and (min-width: 576px) {
  html {
    font-size: 15px;
  }
  
  .header-content {
    padding: 0 var(--tablet-padding);
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .nav-item {
    padding: 8px 14px;
    font-size: 15px;
  }
  
  .app-main {
    padding: var(--tablet-padding);
  }
  
  .app-footer {
    font-size: 13px;
    padding: 14px var(--tablet-padding);
  }
}

@media screen and (min-width: 768px) {
  html {
    font-size: 16px;
  }
  
  :root {
    --header-height: 70px;
  }
  
  .header-content {
    padding: 0 var(--desktop-padding);
  }
  
  .logo {
    gap: 12px;
  }
  
  .logo-icon {
    font-size: 28px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .nav-menu {
    gap: 24px;
  }
  
  .nav-item {
    padding: 8px 16px;
    font-size: 16px;
  }
  
  .app-main {
    padding: var(--desktop-padding);
  }
  
  .app-footer {
    font-size: 14px;
    padding: 16px var(--desktop-padding);
  }
}

@media screen and (min-width: 1024px) {
  .header-content {
    padding: 0 40px;
  }
  
  .app-main {
    padding: 32px 40px;
  }
}

@media screen and (min-width: 1200px) {
  .header-content {
    padding: 0 60px;
  }
  
  .app-main {
    padding: 40px 60px;
  }
}
</style>