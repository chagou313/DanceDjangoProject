(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        // 获取内容输入框
        const contentField = document.getElementById('id_content');
        
        if (!contentField) {
            console.log('未找到内容输入框');
            return;
        }
        
        console.log('已启用新闻图片粘贴上传功能');
        
        // 监听粘贴事件
        contentField.addEventListener('paste', function(e) {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            
            if (!items) return;
            
            for (let i = 0; i < items.length; i++) {
                // 检查是否为图片
                if (items[i].type.indexOf('image') !== -1) {
                    e.preventDefault();
                    const blob = items[i].getAsFile();
                    console.log('检测到粘贴的图片:', blob);
                    uploadPastedImage(blob);
                    break; // 只处理第一张图片
                }
            }
        });
        
        // 上传图片函数
        function uploadPastedImage(blob) {
            const formData = new FormData();
            formData.append('file', blob, 'pasted-image.png');
            
            // 显示上传提示
            showNotification('正在上传图片...', 'info');
            
            // 发送请求到后端
            fetch('/admin/news/news/upload_image/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络响应失败');
                }
                return response.json();
            })
            .then(data => {
                console.log('上传响应:', data);
                if (data.success && data.url) {
                    insertImageToContent(data.url);
                    showNotification('图片上传成功！', 'success');
                } else {
                    showNotification('图片上传失败：' + (data.error || '未知错误'), 'error');
                }
            })
            .catch(error => {
                console.error('上传错误:', error);
                showNotification('图片上传出错：' + error.message, 'error');
            });
        }
        
        // 在光标位置插入图片标签
        function insertImageToContent(url) {
            const imgTag = `\n<img src="${url}" alt="粘贴的图片" style="max-width: 100%; height: auto; display: block; margin: 10px 0;">\n`;
            
            const start = contentField.selectionStart;
            const end = contentField.selectionEnd;
            const text = contentField.value;
            
            // 在光标位置插入图片标签
            contentField.value = text.substring(0, start) + imgTag + text.substring(end);
            
            // 更新光标位置
            const newCursorPos = start + imgTag.length;
            contentField.setSelectionRange(newCursorPos, newCursorPos);
            
            // 触发 change 和 input 事件，让 Django 感知内容变化
            contentField.dispatchEvent(new Event('change', { bubbles: true }));
            contentField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        // 显示通知消息
        function showNotification(message, type) {
            // 移除旧的通知
            const oldNotification = document.querySelector('.paste-notification');
            if (oldNotification) {
                oldNotification.remove();
            }
            
            // 创建新通知
            const notification = document.createElement('div');
            notification.className = 'paste-notification';
            notification.textContent = message;
            
            // 设置样式
            Object.assign(notification.style, {
                position: 'fixed',
                top: '20px',
                right: '20px',
                padding: '15px 25px',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '14px',
                fontWeight: '500',
                zIndex: '9999',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                transition: 'all 0.3s ease',
                opacity: '0',
                transform: 'translateY(-20px)'
            });
            
            // 根据类型设置颜色
            if (type === 'success') {
                notification.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            } else if (type === 'error') {
                notification.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
            } else {
                notification.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
            }
            
            document.body.appendChild(notification);
            
            // 淡入动画
            setTimeout(() => {
                notification.style.opacity = '1';
                notification.style.transform = 'translateY(0)';
            }, 10);
            
            // 3秒后自动消失
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-20px)';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        // 获取 CSRF Token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    });
})();
