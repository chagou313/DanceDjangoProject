(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const contentField = document.getElementById('id_content');
        
        if (!contentField) return;
        
        // 创建包裹容器，将内容框和工具栏组合在一起
        const wrapper = document.createElement('div');
        wrapper.className = 'content-wrapper';
        wrapper.style.position = 'relative';
        
        // 将 wrapper 插入到内容框的父容器中
        const parent = contentField.parentNode;
        parent.insertBefore(wrapper, contentField.nextSibling);
        
        // 将内容框移入 wrapper
        wrapper.appendChild(contentField);
        
        // 创建工具栏
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar';
        toolbar.innerHTML = `
            <span class="toolbar-label">格式工具：</span>
            <button type="button" class="toolbar-btn" data-action="indent">
                缩进 <kbd>Alt+I</kbd>
            </button>
            <button type="button" class="toolbar-btn" data-action="outdent">
                取消缩进 <kbd>Alt+O</kbd>
            </button>
            <button type="button" class="toolbar-btn" data-action="paragraph">
                新段落 <kbd>Enter</kbd>
            </button>
            <span class="toolbar-divider">|</span>
            <button type="button" class="toolbar-btn" data-action="bold">
                加粗 <kbd>Ctrl+B</kbd>
            </button>
            <button type="button" class="toolbar-btn" data-action="italic">
                斜体 <kbd>Ctrl+I</kbd>
            </button>
        `;
        
        // 将工具栏添加到 wrapper 中，紧跟内容框
        wrapper.appendChild(toolbar);
        
        // 添加工具栏样式
        const style = document.createElement('style');
        style.textContent = `
            /* 创建包裹容器 */
            .content-wrapper {
                position: relative;
            }
            
            .rich-text-toolbar {
                display: flex !important;
                align-items: center !important;
                gap: 0.4rem !important;
                padding: 0.4rem 0.6rem !important;
                background: rgba(216, 191, 100, 0.06) !important;
                border: 1px solid rgba(216, 191, 100, 0.25) !important;
                border-top: none !important;
                border-radius: 0 0 0.3rem 0.3rem !important;
                margin: 0 !important;
                margin-top: -1px !important;
                flex-wrap: wrap !important;
                font-size: 0.8rem !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }
            
            .toolbar-label {
                color: rgba(232, 213, 155, 0.7) !important;
                font-size: 0.75rem !important;
                margin-right: 0.3rem !important;
                font-weight: 500 !important;
            }
            
            .toolbar-btn {
                padding: 0.2rem 0.5rem !important;
                background: transparent !important;
                border: 1px solid rgba(216, 191, 100, 0.2) !important;
                border-radius: 0.2rem !important;
                color: #C8B87A !important;
                cursor: pointer !important;
                font-size: 0.75rem !important;
                transition: all 0.2s !important;
                white-space: nowrap !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 0.25rem !important;
                height: auto !important;
                line-height: 1.4 !important;
                min-height: unset !important;
            }
            
            .toolbar-btn:hover {
                background: rgba(216, 191, 100, 0.12) !important;
                border-color: rgba(216, 191, 100, 0.4) !important;
                color: #E8D59B !important;
            }
            
            .toolbar-btn kbd {
                display: inline-block !important;
                padding: 0.05rem 0.3rem !important;
                background: rgba(216, 191, 100, 0.15) !important;
                border: 1px solid rgba(216, 191, 100, 0.3) !important;
                border-radius: 0.15rem !important;
                font-size: 0.65rem !important;
                font-family: 'Consolas', 'Monaco', monospace !important;
                color: rgba(232, 213, 155, 0.8) !important;
                line-height: 1.3 !important;
                margin: 0 !important;
            }
            
            .toolbar-divider {
                color: rgba(216, 191, 100, 0.3) !important;
                margin: 0 0.15rem !important;
                font-size: 0.85rem !important;
            }
            
            #id_content {
                border-radius: 0.3rem 0.3rem 0 0 !important;
                margin-bottom: 0 !important;
                min-height: 400px !important;
                font-family: 'Noto Serif SC', serif !important;
                line-height: 1.8 !important;
            }
            
            /* 隐藏 Django admin 默认的 help text 造成的间距 */
            .field-content .help {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
        
        // 工具栏按钮事件
        toolbar.addEventListener('click', function(e) {
            const btn = e.target.closest('.toolbar-btn');
            if (!btn) return;
            
            const action = btn.dataset.action;
            contentField.focus();
            
            switch(action) {
                case 'indent':
                    insertHTML('<p style="text-indent: 2em;">');
                    break;
                case 'outdent':
                    insertHTML('<p>');
                    break;
                case 'paragraph':
                    insertHTML('</p><p>');
                    break;
                case 'bold':
                    // 直接插入 <strong> 标签包裹选中的文本
                    wrapSelection('<strong>', '</strong>');
                    break;
                case 'italic':
                    // 直接插入 <em> 标签包裹选中的文本
                    wrapSelection('<em>', '</em>');
                    break;
            }
        });
        
        // 快捷键支持
        contentField.addEventListener('keydown', function(e) {
            // Alt+I - 缩进
            if (e.altKey && e.key === 'i') {
                e.preventDefault();
                insertHTML('<p style="text-indent: 2em;">');
            }
            // Alt+O - 取消缩进
            if (e.altKey && e.key === 'o') {
                e.preventDefault();
                insertHTML('<p>');
            }
            // Ctrl+B - 加粗（浏览器默认支持）
            // Ctrl+I - 斜体（浏览器默认支持）
        });
        
        // 插入HTML的辅助函数
        function insertHTML(html) {
            const start = contentField.selectionStart;
            const end = contentField.selectionEnd;
            const text = contentField.value;
            
            contentField.value = text.substring(0, start) + html + text.substring(end);
            
            // 移动光标到插入位置之后
            const newCursorPos = start + html.length;
            contentField.setSelectionRange(newCursorPos, newCursorPos);
            
            // 触发change事件
            contentField.dispatchEvent(new Event('input', { bubbles: true }));
            contentField.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 包裹选中文本的辅助函数
        function wrapSelection(openTag, closeTag) {
            const start = contentField.selectionStart;
            const end = contentField.selectionEnd;
            const text = contentField.value;
            
            // 获取选中的文本
            const selectedText = text.substring(start, end);
            
            // 如果没有选中文本，插入空标签并将光标放在中间
            if (!selectedText) {
                const placeholder = '文本';
                const fullHTML = openTag + placeholder + closeTag;
                contentField.value = text.substring(0, start) + fullHTML + text.substring(end);
                
                // 将光标定位在 placeholder 中间
                const newCursorPos = start + openTag.length + placeholder.length;
                contentField.setSelectionRange(newCursorPos, newCursorPos);
            } else {
                // 如果已选中文本，直接包裹
                const wrappedText = openTag + selectedText + closeTag;
                contentField.value = text.substring(0, start) + wrappedText + text.substring(end);
                
                // 选中包裹后的文本
                const newStart = start;
                const newEnd = start + wrappedText.length;
                contentField.setSelectionRange(newStart, newEnd);
            }
            
            // 触发change事件
            contentField.dispatchEvent(new Event('input', { bubbles: true }));
            contentField.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
})();
