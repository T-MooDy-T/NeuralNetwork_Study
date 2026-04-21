window.pushStore = {
    pushForm: Vue.ref({ user_id: '', message: '' }),
    pushLoading: Vue.ref(false),
    testLoading: Vue.ref(false),
    
    sendPushMessage: async () => {
        if (!window.pushStore.pushForm.value.user_id || !window.pushStore.pushForm.value.message) {
            alert('请填写用户ID和消息内容');
            return;
        }
        
        window.pushStore.pushLoading.value = true;
        try {
            await api.sendMessage(window.pushStore.pushForm.value);
            alert('消息发送成功');
            window.pushStore.pushForm.value.user_id = '';
            window.pushStore.pushForm.value.message = '';
        } catch (error) {
            console.error('发送消息失败:', error);
            alert('发送失败: ' + (error.response?.data?.detail || '未知错误'));
        } finally {
            window.pushStore.pushLoading.value = false;
        }
    },
    
    sendTestReminder: async () => {
        if (!window.pushStore.pushForm.value.user_id) {
            alert('请填写用户ID');
            return;
        }
        
        window.pushStore.testLoading.value = true;
        try {
            await api.sendTestReminder(window.pushStore.pushForm.value.user_id);
            alert('测试提醒已发送');
        } catch (error) {
            console.error('发送测试提醒失败:', error);
            alert('发送失败: ' + (error.response?.data?.detail || '未知错误'));
        } finally {
            window.pushStore.testLoading.value = false;
        }
    }
};

async function sendMessageToQQ() {
    const userId = document.getElementById('pushUserId').value;
    const message = document.getElementById('pushMessage').value;
    const sendBtn = document.getElementById('sendBtn');
    
    if (!userId || !message) {
        alert('请填写用户ID和消息内容');
        return;
    }
    
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span>📤</span> 发送中...';
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/admin/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ user_id: userId, message: message })
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(data.message + (data.note ? '\n\n提示: ' + data.note : ''));
            document.getElementById('pushUserId').value = '';
            document.getElementById('pushMessage').value = '';
        } else {
            const data = await response.json();
            alert('发送失败: ' + (data.detail || '未知错误'));
        }
    } catch (error) {
        alert('发送失败: ' + error.message);
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span>📤</span> 发送消息';
    }
}

async function sendTestReminderToQQ() {
    const userId = document.getElementById('pushUserId').value;
    const testBtn = document.getElementById('testBtn');
    
    if (!userId) {
        alert('请填写用户ID');
        return;
    }
    
    testBtn.disabled = true;
    testBtn.innerHTML = '<span>🔔</span> 发送中...';
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/admin/send-reminder-test?user_id=${userId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            alert('测试提醒已发送');
        } else {
            const data = await response.json();
            alert('发送失败: ' + (data.detail || '未知错误'));
        }
    } catch (error) {
        alert('发送失败: ' + error.message);
    } finally {
        testBtn.disabled = false;
        testBtn.innerHTML = '<span>🔔</span> 发送测试提醒';
    }
}