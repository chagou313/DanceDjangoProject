(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        // 获取封面图输入框
        const coverImageField = document.getElementById('id_cover_image');
        
        if (!coverImageField) {
            console.log('未找到封面图输入框');
            return;
        }
        
        console.log('已启用封面图粘贴上传功能');
        
        // 在封面图字段旁边添加提示
        const hintDiv = document.createElement('div');
        hintDiv.style.cssText = 'color: #D8BF64; font-size: 0.85rem; margin-top: 0.5rem; padding: 0.5rem; background: rgba(216, 191, 100, 0.1); border-radius: 0.3rem; border: 1px solid rgba(216, 191, 100, 0.2);';
        hintDiv.innerHTML = '<i class="fas fa-paste"></i> 💡 提示：点击此区域后，可以直接粘贴截图（Ctrl+V）作为封面图';
        coverImageField.parentNode.insertBefore(hintDiv, coverImageField.nextSibling);
        
        // 让封面图字段的父容器可点击
        const parentDiv = coverImageField.closest('div') || coverImageField.parentNode;
        parentDiv.style.cursor = 'pointer';
        parentDiv.title = '点击后按 Ctrl+V 粘贴封面图';
        
        // 监听粘贴事件（在整个 document 上监听，但只处理封面图字段获得焦点时）
        document.addEventListener('paste', function(e) {
            // 检查是否应该处理这个粘贴事件
            // 如果当前焦点在封面图字段或其附近，或者没有在其他输入框中
            const activeElement = document.activeElement;
            const isNearCoverImage = coverImageField.contains(activeElement) || 
                                    parentDiv.contains(activeElement) ||
                                    (activeElement === document.body);
            
            if (!isNearCoverImage) {
                // 如果焦点在其他输入框，不处理
                if (activeElement && (activeElement.tagName === 'INPUT' || 
                                     activeElement.tagName === 'TEXTAREA' ||
                                     activeElement.isContentEditable)) {
                    return;
                }
            }
            
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            
            if (!items) return;
            
            for (let i = 0; i < items.length; i++) {
                // 检查是否为图片
                if (items[i].type.indexOf('image') !== -1) {
                    e.preventDefault();
                    const blob = items[i].getAsFile();
                    console.log('检测到粘贴的封面图:', blob);
                    uploadCoverImage(blob);
                    break;
                }
            }
        });
        
        // 上传封面图函数
        function uploadCoverImage(blob) {
            const formData = new FormData();
            formData.append('file', blob, 'cover-image.png');
            
            // 显示上传提示
            showNotification('正在上传封面图...', 'info');
            
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
                    // 创建一个新的 File 对象并设置到封面图字段
                    fetch(data.url)
                        .then(res => res.blob())
                        .then(imageBlob => {
                            const file = new File([imageBlob], 'cover-image.png', { type: blob.type });
                            
                            // 创建 DataTransfer 对象来设置文件
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(file);
                            
                            // 设置文件到输入框
                            coverImageField.files = dataTransfer.files;
                            
                            // 触发 change 事件
                            coverImageField.dispatchEvent(new Event('change', { bubbles: true }));
                            
                            showNotification('封面图上传成功！', 'success');
                        })
                        .catch(error => {
                            console.error('下载图片错误:', error);
                            showNotification('封面图上传失败：' + error.message, 'error');
                        });
                } else {
                    showNotification('封面图上传失败：' + (data.error || '未知错误'), 'error');
                }
            })
            .catch(error => {
                console.error('上传错误:', error);
                showNotification('封面图上传出错：' + error.message, 'error');
            });
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
