// API基础URL（根据环境自动选择）
// 开发环境：使用localhost或局域网IP
// 生产环境：使用Render后端URL（需要替换为实际URL）
const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    
    // 如果是本地开发环境（localhost或127.0.0.1）
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        const backendUrl = 'http://localhost:8000';
        console.log('🔵 本地开发环境检测（电脑）');
        console.log('   访问地址:', window.location.href);
        console.log('   后端URL:', backendUrl);
        return backendUrl;
    }
    
    // 如果是局域网IP（手机访问）
    // 匹配 192.168.x.x, 10.x.x.x, 172.16-31.x.x 等私有IP
    const privateIpPattern = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)/;
    if (privateIpPattern.test(hostname)) {
        const backendUrl = `http://${hostname}:8000`;
        console.log('📱 本地开发环境检测（手机/局域网）');
        console.log('   访问地址:', window.location.href);
        console.log('   后端URL:', backendUrl);
        return backendUrl;
    }
    
    // 生产环境：使用腾讯云服务器（HTTPS）
    // 临时方案：使用IP地址（域名备案审核中，备案通过后改回域名）
    // 正式方案：使用域名 beatsync.site（通过Nginx反向代理，端口443，Let's Encrypt证书）
    const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
    console.log('🟢 生产环境检测（腾讯云服务器 - HTTPS - 临时使用IP地址）');
    console.log('   访问地址:', window.location.href);
    console.log('   后端URL:', backendUrl);
    console.log('   ⚠️ 临时方案：域名备案审核中，备案通过后改回域名');
    return backendUrl;
})();

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// 状态管理
let state = {
    danceFileId: null,
    bgmFileId: null,
    taskId: null,
    danceFile: null,
    bgmFile: null,
    modularOutput: null,  // modular版本输出文件路径
    v2Output: null        // v2版本输出文件路径
};

// 下载状态标志（用于防止轮询覆盖下载状态）
let isDownloading = false;
let downloadingVersion = null;

// DOM元素
const danceFileInput = document.getElementById('dance-file');
const bgmFileInput = document.getElementById('bgm-file');
const processBtn = document.getElementById('process-btn');
const statusText = document.getElementById('status-text');
const downloadSection = document.getElementById('download-section');
const downloadModularBtn = document.getElementById('download-modular-btn');
const downloadV2Btn = document.getElementById('download-v2-btn');
// 在线预览功能已移除
// const previewModularBtn = document.getElementById('preview-modular-btn');
// const previewV2Btn = document.getElementById('preview-v2-btn');
const modularPreview = document.getElementById('modular-preview');
const v2Preview = document.getElementById('v2-preview');
const modularResult = document.getElementById('modular-result');
const v2Result = document.getElementById('v2-result');
const uploadProgressContainer = document.getElementById('upload-progress-container');
const uploadProgressFill = document.getElementById('upload-progress-fill');
const uploadProgressText = document.getElementById('upload-progress-text');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 重置所有状态（确保刷新后清空之前的记录）
    resetState();
    setupFileInputs();
    setupDragAndDrop();
    updateProcessButton();
    
    // 手机端优化：隐藏拖拽提示
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile) {
        document.querySelectorAll('.upload-hint').forEach(hint => {
            hint.style.display = 'none';
        });
    }
});

// 重置状态
function resetState() {
    state = {
        danceFileId: null,
        bgmFileId: null,
        taskId: null,
        danceFile: null,
        bgmFile: null,
        modularOutput: null,
        v2Output: null
    };
    
    // 清空文件输入
    danceFileInput.value = '';
    bgmFileInput.value = '';
    
    // 隐藏文件信息
    document.getElementById('dance-info').style.display = 'none';
    document.getElementById('bgm-info').style.display = 'none';
    
    // 重置状态显示
    updateStatus('等待上传文件...', '');
    
    // 隐藏下载按钮
    downloadSection.style.display = 'none';
    
    // 重置下载按钮状态
    downloadModularBtn.disabled = true;
    downloadModularBtn.querySelector('.btn-status').textContent = '⏳';
    downloadModularBtn.querySelector('.btn-text').textContent = '下载Modular版本结果';
    downloadModularBtn.onclick = null;
    downloadV2Btn.disabled = true;
    downloadV2Btn.querySelector('.btn-status').textContent = '⏳';
    downloadV2Btn.querySelector('.btn-text').textContent = '下载V2版本结果';
    downloadV2Btn.onclick = null;
    
    // 重置处理按钮
    processBtn.disabled = true;
    processBtn.textContent = '开始处理';
}

// 设置文件输入
function setupFileInputs() {
    danceFileInput.addEventListener('change', (e) => handleFileSelect(e, 'dance'));
    bgmFileInput.addEventListener('change', (e) => handleFileSelect(e, 'bgm'));
}

// 处理文件选择
async function handleFileSelect(event, fileType) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件格式
    const allowedExtensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV'];
    const fileExt = '.' + file.name.split('.').pop();
    if (!allowedExtensions.includes(fileExt)) {
        alert(`不支持的文件格式，支持格式: ${allowedExtensions.join(', ')}`);
        event.target.value = '';
        return;
    }
    
    // 上传文件
    await uploadFile(file, fileType);
}

// 检查后端服务是否可用（支持渐进式超时和重试，增强浏览器兼容性）
async function checkBackendHealth(retryCount = 0) {
    const healthUrl = `${API_BASE_URL}/api/health`;
    const controller = new AbortController();
    
    // 检测浏览器类型
    const userAgent = navigator.userAgent.toLowerCase();
    const isQuark = userAgent.includes('quark');
    const isWeChat = userAgent.includes('micromessenger');
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    // 渐进式超时策略：首次尝试较短超时，重试时增加超时时间
    // 对于某些浏览器（如夸克、微信），使用更长的超时时间
    let timeoutStrategies;
    if (isQuark || isWeChat) {
        // 夸克和微信浏览器可能需要更长的超时时间
        timeoutStrategies = [
            30000,  // 第一次：30秒
            50000,  // 第二次：50秒
            60000   // 第三次：60秒（最大超时）
        ];
    } else {
        timeoutStrategies = [
            20000,  // 第一次：20秒（快速检测正常情况）
            35000,  // 第二次：35秒（给慢速网络更多时间）
            45000   // 第三次：45秒（最大超时，适应极端情况）
        ];
    }
    
    const timeoutMs = timeoutStrategies[Math.min(retryCount, timeoutStrategies.length - 1)];
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    
    try {
        const startTime = Date.now();
        
        // 构建fetch选项，针对不同浏览器优化
        const fetchOptions = {
            method: 'GET',
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            // 确保跨域请求正常
            mode: 'cors',
            credentials: 'omit'
        };
        
        // 某些浏览器可能需要额外的配置
        if (isQuark || isWeChat) {
            // 对于夸克和微信，尝试更宽松的配置
            fetchOptions.cache = 'no-store';
        }
        
        const response = await fetch(healthUrl, fetchOptions);
        clearTimeout(timeoutId);
        const elapsed = Date.now() - startTime;
        
        if (response.ok) {
            console.log(`✅ 后端健康检查成功 (耗时${elapsed}ms${retryCount > 0 ? `, 重试${retryCount}次` : ''})`);
            return true;
        } else {
            console.warn(`⚠️ 后端健康检查返回非200状态: ${response.status}`);
            return false;
        }
    } catch (fetchError) {
        clearTimeout(timeoutId);
        
        // 记录详细的错误信息（用于调试）
        const errorDetails = {
            name: fetchError.name,
            message: fetchError.message,
            stack: fetchError.stack,
            userAgent: navigator.userAgent,
            url: healthUrl,
            retryCount: retryCount
        };
        console.warn('⚠️ 后端健康检查失败详情:', errorDetails);
        
        // AbortError是预期的超时错误
        if (fetchError.name === 'AbortError') {
            const timeoutSeconds = Math.floor(timeoutMs / 1000);
            console.log(`⏱️ 后端健康检查超时（${timeoutSeconds}秒内无响应）${retryCount > 0 ? `, 第${retryCount + 1}次尝试` : ''}`);
            
            // 如果还有重试机会，自动重试
            if (retryCount < timeoutStrategies.length - 1) {
                console.log(`🔄 自动重试健康检查（${retryCount + 1}/${timeoutStrategies.length - 1}）...`);
                // 等待1秒后重试
                await new Promise(resolve => setTimeout(resolve, 1000));
                return await checkBackendHealth(retryCount + 1);
            }
            
            return false;
        }
        
        // 其他错误（如网络错误、CORS错误、证书错误等）
        if (fetchError.message && !fetchError.message.includes('aborted')) {
            console.warn('⚠️ 后端健康检查失败:', fetchError.message);
            
            // 检测证书错误（某些浏览器对自签名证书更严格）
            if (fetchError.message.includes('certificate') || 
                fetchError.message.includes('SSL') || 
                fetchError.message.includes('TLS') ||
                fetchError.message.includes('ERR_CERT') ||
                fetchError.message.includes('ERR_CERT_COMMON_NAME_INVALID')) {
                console.warn('⚠️ SSL证书错误：证书是为域名签发的，使用IP地址访问时需要接受证书警告');
                console.warn('   解决方法：请先手动访问 https://124.221.58.149/api/health 并接受证书警告');
                console.warn('   步骤：1. 点击"高级" 2. 点击"继续访问" 3. 刷新页面重试');
            }
            
            // 如果是CORS错误，提供更详细的提示
            if (fetchError.message.includes('CORS') || fetchError.message.includes('cors')) {
                console.warn('⚠️ 可能是CORS问题，请检查后端CORS配置');
            }
            
            // 如果是网络错误，尝试重试一次
            if (retryCount === 0 && (
                fetchError.message.includes('Failed to fetch') ||
                fetchError.message.includes('NetworkError') ||
                fetchError.message.includes('network') ||
                fetchError.message.includes('ERR_')
            )) {
                console.log('🔄 网络错误，自动重试一次...');
                await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒后重试
                return await checkBackendHealth(retryCount + 1);
            }
        }
        
        return false;
    }
}

// 上传文件（支持重试）
async function uploadFile(file, fileType, retryCount = 0) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    
    try {
        // 先检查后端服务是否可用
        updateStatus(`正在检查后端服务...`, 'processing');
        const backendAvailable = await checkBackendHealth();
        
        if (!backendAvailable) {
            // 检测浏览器和设备类型
            const userAgent = navigator.userAgent.toLowerCase();
            const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            const isQuark = userAgent.includes('quark');
            const isWeChat = userAgent.includes('micromessenger');
            const isSafari = /safari/i.test(navigator.userAgent) && !/chrome|crios|fxios/i.test(navigator.userAgent);
            
            let errorMsg = `后端服务不可用（已尝试多次连接）。\n\n`;
            errorMsg += `可能原因：\n`;
            errorMsg += `1. 网络连接问题（请检查网络，手机网络可能比WiFi慢）\n`;
            
            // 针对不同浏览器提供不同的提示
            if (isQuark) {
                errorMsg += `2. 夸克浏览器可能需要更长的连接时间（建议使用WiFi网络）\n`;
                errorMsg += `3. 如果使用HTTPS，可能需要手动接受证书（访问 ${API_BASE_URL}/api/health）\n`;
            } else if (isWeChat) {
                errorMsg += `2. 微信内置浏览器可能有网络限制（建议使用系统浏览器）\n`;
                errorMsg += `3. 如果使用HTTPS，可能需要手动接受证书（访问 ${API_BASE_URL}/api/health）\n`;
            } else if (isMobile) {
                errorMsg += `2. 手机网络延迟较高（建议使用WiFi网络）\n`;
                errorMsg += `3. 后端服务未运行（请检查服务器状态）\n`;
            } else {
                errorMsg += `2. 防火墙配置问题（请检查服务器防火墙）\n`;
                errorMsg += `3. 后端服务未运行（请检查服务器状态）\n`;
            }
            
            errorMsg += `\n手动检查：访问 ${API_BASE_URL}/api/health 查看服务状态\n`;
            
            // 针对HTTPS自签名证书的特殊提示
            if (API_BASE_URL.startsWith('https://') && API_BASE_URL.includes('124.221.58.149')) {
                errorMsg += `\n⚠️ SSL证书错误（临时方案）：\n`;
                errorMsg += `当前使用IP地址访问，但SSL证书是为域名签发的，浏览器会拒绝连接。\n`;
                errorMsg += `解决方法：\n`;
                errorMsg += `1. 点击下方链接打开健康检查页面：\n`;
                errorMsg += `   ${API_BASE_URL}/api/health\n`;
                errorMsg += `2. 在打开的页面中，点击"高级"或"Advanced"\n`;
                errorMsg += `3. 点击"继续访问"或"Proceed to 124.221.58.149 (unsafe)"\n`;
                errorMsg += `4. 返回本页面，点击"重试"按钮\n`;
                errorMsg += `\n注意：这是临时方案，域名备案通过后将自动恢复。\n`;
            } else if (API_BASE_URL.startsWith('https://')) {
                errorMsg += `\n⚠️ HTTPS证书提示：\n`;
                errorMsg += `如果使用自签名证书，某些浏览器（如夸克、微信）可能需要先手动访问健康检查地址并接受证书。\n`;
                errorMsg += `请先访问：${API_BASE_URL}/api/health\n`;
            }
            
            errorMsg += `\n如果健康检查正常，可能是网络延迟问题，请点击"重试"按钮。`;
            
            // 显示错误并添加重试按钮
            updateStatus(errorMsg, 'error');
            
            // 创建重试按钮
            const retryBtn = document.createElement('button');
            retryBtn.textContent = '重试';
            retryBtn.className = 'retry-btn';
            retryBtn.style.cssText = 'margin-top: 15px; padding: 10px 20px; background-color: #007AFF; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; min-height: 44px;';
            
            retryBtn.onclick = async () => {
                retryBtn.disabled = true;
                retryBtn.textContent = '重试中...';
                updateStatus('正在检查后端服务（已自动重试多次）...', 'processing');
                
                // 重新检查（会使用渐进式超时和自动重试）
                const available = await checkBackendHealth(0);
                if (available) {
                    retryBtn.remove();
                    // 继续上传流程：重新调用uploadFile
                    try {
                        await uploadFile(file, fileType, retryCount + 1);
                    } catch (error) {
                        // 如果重试后仍然失败，显示错误
                        updateStatus(`上传失败: ${error.message}`, 'error');
                    }
                } else {
                    retryBtn.disabled = false;
                    retryBtn.textContent = '重试';
                    updateStatus(errorMsg, 'error');
                }
            };
            
            // 将重试按钮添加到状态区域
            const statusSection = document.querySelector('.status-section');
            // 移除旧的重试按钮（如果存在）
            const oldRetryBtn = statusSection.querySelector('.retry-btn');
            if (oldRetryBtn) {
                oldRetryBtn.remove();
            }
            statusSection.appendChild(retryBtn);
            
            throw new Error(errorMsg);
        }
        
        // 检查文件大小（限制500MB）
        const fileSizeMB = file.size / (1024 * 1024);
        const maxSizeMB = 500; // 500MB限制
        if (fileSizeMB > maxSizeMB) {
            const errorMsg = `文件大小超过限制（最大${maxSizeMB}MB），当前文件：${formatFileSize(file.size)}。请压缩或裁剪文件后重试。`;
            updateStatus(errorMsg, 'error');
            throw new Error(errorMsg);
        }
        
        updateStatus(`正在上传${fileType === 'dance' ? '原始视频' : '音源视频'}...`, 'processing');
        
        // 显示上传进度条
        uploadProgressContainer.style.display = 'block';
        uploadProgressFill.style.width = '0%';
        uploadProgressText.textContent = '0%';
        
        console.log('开始上传文件:', {
            fileName: file.name,
            fileSize: file.size,
            fileSizeMB: fileSizeMB.toFixed(2),
            fileType: fileType,
            apiUrl: `${API_BASE_URL}/api/upload`
        });
        
        // 使用XMLHttpRequest替代fetch，以支持上传进度
        const timeoutMs = fileSizeMB >= 10 ? 600000 : 120000; // 大文件10分钟，小文件2分钟
        
        let response;
        const startTime = Date.now();
        try {
            console.log('📤 发送上传请求...');
            response = await new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                let timeoutId;
                
                // 设置超时
                timeoutId = setTimeout(() => {
                    xhr.abort();
                    reject(new Error('AbortError'));
                }, timeoutMs);
                
                // 上传进度事件
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        uploadProgressFill.style.width = percent + '%';
                        uploadProgressText.textContent = `${percent}% (${formatFileSize(e.loaded)} / ${formatFileSize(e.total)})`;
                    }
                });
                
                // 请求完成
                xhr.addEventListener('load', () => {
                    clearTimeout(timeoutId);
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const result = JSON.parse(xhr.responseText);
                            resolve({
                                ok: true,
                                status: xhr.status,
                                statusText: xhr.statusText,
                                json: async () => result,
                                text: async () => xhr.responseText,
                                headers: {
                                    get: (name) => xhr.getResponseHeader(name),
                                    entries: () => {
                                        const headers = {};
                                        xhr.getAllResponseHeaders().split('\r\n').forEach(line => {
                                            const [key, value] = line.split(': ');
                                            if (key && value) headers[key] = value;
                                        });
                                        return Object.entries(headers);
                                    }
                                }
                            });
                        } catch (e) {
                            resolve({
                                ok: true,
                                status: xhr.status,
                                statusText: xhr.statusText,
                                json: async () => ({ message: xhr.responseText }),
                                text: async () => xhr.responseText,
                                headers: { get: () => null, entries: () => [] }
                            });
                        }
                    } else {
                        reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                    }
                });
                
                // 请求错误
                xhr.addEventListener('error', () => {
                    clearTimeout(timeoutId);
                    reject(new Error('Network error'));
                });
                
                // 请求中止
                xhr.addEventListener('abort', () => {
                    clearTimeout(timeoutId);
                    reject(new Error('AbortError'));
                });
                
                // 发送请求
                xhr.open('POST', `${API_BASE_URL}/api/upload`);
                xhr.send(formData);
            });
            
            const elapsed = Date.now() - startTime;
            console.log(`📥 收到响应 (耗时${elapsed}ms):`, response.status, response.statusText);
        } catch (fetchError) {
            clearTimeout(timeoutId);
            const elapsed = Date.now() - startTime;
            console.error(`❌ Fetch错误 (耗时${elapsed}ms):`, fetchError);
            if (fetchError.name === 'AbortError') {
                const timeoutMinutes = Math.floor(timeoutMs / 60000);
                const errorMsg = `上传超时：请求超过${timeoutMinutes}分钟未响应。可能原因：\n` +
                    `1. 后端服务未启动（请检查 http://localhost:8000 是否可访问）\n` +
                    `2. 文件过大，上传时间过长\n` +
                    `3. 网络连接问题\n\n` +
                    `请检查后端服务状态或尝试使用较小的文件。`;
                throw new Error(errorMsg);
            } else if (fetchError.message.includes('Failed to fetch')) {
                const errorMsg = `无法连接到后端服务。请确认：\n` +
                    `1. 后端服务已启动（访问 http://localhost:8000/api/health 检查）\n` +
                    `2. 后端服务正在运行（检查终端是否有错误信息）\n` +
                    `3. 防火墙未阻止连接\n\n` +
                    `启动后端服务：cd web_service/backend && ./start_server.sh`;
                throw new Error(errorMsg);
            } else {
                throw new Error(`上传失败: ${fetchError.message}`);
            }
        }
        
        // 隐藏进度条
        uploadProgressContainer.style.display = 'none';
        
        console.log('📋 响应详情:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok
        });
        
        if (!response.ok) {
            let errorDetail = '上传失败';
            try {
                const error = await response.json();
                errorDetail = error.detail || error.message || '上传失败';
                console.error('上传错误详情:', error);
            } catch (e) {
                // 如果响应不是JSON，尝试读取文本
                try {
                    const errorText = await response.text();
                    console.error('上传错误响应:', errorText);
                    errorDetail = errorText || `HTTP ${response.status}: ${response.statusText}`;
                } catch (textError) {
                    errorDetail = `HTTP ${response.status}: ${response.statusText}`;
                }
            }
            throw new Error(errorDetail);
        }
        
        let result;
        try {
            // 直接使用json()方法，因为XMLHttpRequest的Promise已经解析了JSON
            result = await response.json();
            console.log('✅ 上传成功，解析后的响应:', result);
        } catch (parseError) {
            console.error('❌ JSON解析失败:', parseError);
            // 如果json()失败，尝试使用text()然后手动解析
            try {
                const responseText = await response.text();
                console.log('📄 响应文本:', responseText);
                result = JSON.parse(responseText);
                console.log('✅ 上传成功（手动解析），解析后的响应:', result);
            } catch (textParseError) {
                console.error('❌ 文本解析也失败:', textParseError);
                throw new Error('服务器响应格式错误');
            }
        }
        
        // 保存文件ID
        if (fileType === 'dance') {
            state.danceFileId = result.file_id;
            state.danceFile = file;
            showFileInfo('dance', file.name, formatFileSize(result.size));
        } else {
            state.bgmFileId = result.file_id;
            state.bgmFile = file;
            showFileInfo('bgm', file.name, formatFileSize(result.size));
        }
        
        // 确保进度条显示100%，然后延迟隐藏
        uploadProgressFill.style.width = '100%';
        uploadProgressText.textContent = '100% (上传完成)';
        setTimeout(() => {
            uploadProgressContainer.style.display = 'none';
        }, 1000);
        
        updateStatus('文件上传成功', 'success');
        updateProcessButton();
        
    } catch (error) {
        console.error('上传异常:', error);
        console.error('错误堆栈:', error.stack);
        const errorMessage = error.message || '上传失败，请检查网络连接或后端服务';
        updateStatus(`上传失败: ${errorMessage}`, 'error');
        
        // 如果是网络错误，提供更详细的提示
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            updateStatus('上传失败: 无法连接到后端服务，请确认后端服务已启动', 'error');
        }
    }
}

// 显示文件信息
function showFileInfo(fileType, filename, size) {
    const infoDiv = document.getElementById(`${fileType}-info`);
    const filenameSpan = document.getElementById(`${fileType}-filename`);
    const sizeSpan = document.getElementById(`${fileType}-size`);
    
    filenameSpan.textContent = `文件名: ${filename}`;
    sizeSpan.textContent = `大小: ${size}`;
    infoDiv.style.display = 'block';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// 设置拖拽上传
function setupDragAndDrop() {
    const danceUpload = document.getElementById('dance-upload');
    const bgmUpload = document.getElementById('bgm-upload');
    
    [danceUpload, bgmUpload].forEach((area, index) => {
        const fileType = index === 0 ? 'dance' : 'bgm';
        const fileInput = index === 0 ? danceFileInput : bgmFileInput;
        
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', async (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (!file) return;
            
            // 验证文件格式
            const allowedExtensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV'];
            const fileExt = '.' + file.name.split('.').pop();
            if (!allowedExtensions.includes(fileExt)) {
                alert(`不支持的文件格式，支持格式: ${allowedExtensions.join(', ')}`);
                return;
            }
            
            // 设置文件到input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // 触发change事件
            fileInput.dispatchEvent(new Event('change'));
        });
    });
}

// 更新处理按钮状态
function updateProcessButton() {
    if (state.danceFileId && state.bgmFileId) {
        processBtn.disabled = false;
    } else {
        processBtn.disabled = true;
    }
}

// 处理视频（异步处理）
async function processVideo() {
    if (!state.danceFileId || !state.bgmFileId) {
        alert('请先上传两个视频文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('dance_file_id', state.danceFileId);
    formData.append('bgm_file_id', state.bgmFileId);
    
    try {
        processBtn.disabled = true;
        processBtn.textContent = '提交中...';
        updateStatus('正在提交任务...', 'processing');
        downloadSection.style.display = 'none';
        
        // 提交任务
        console.log('📤 开始提交任务...');
        console.log('提交数据:', {
            dance_file_id: state.danceFileId,
            bgm_file_id: state.bgmFileId,
            apiUrl: `${API_BASE_URL}/api/process`
        });
        
        // 创建带超时的fetch请求（30秒超时）
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
        
        let response;
        const startTime = Date.now();
        try {
            response = await fetch(`${API_BASE_URL}/api/process`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            const elapsed = Date.now() - startTime;
            console.log(`📥 收到响应 (耗时${elapsed}ms):`, {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok
            });
        } catch (fetchError) {
            clearTimeout(timeoutId);
            const elapsed = Date.now() - startTime;
            console.error(`❌ Fetch错误 (耗时${elapsed}ms):`, fetchError);
            if (fetchError.name === 'AbortError') {
                throw new Error(
                    `提交任务超时：请求超过30秒未响应。可能原因：\n` +
                    `1. 后端服务处理缓慢或卡住\n` +
                    `2. 后端服务未正确启动\n` +
                    `3. 网络连接问题\n\n` +
                    `请检查后端服务状态或查看后端日志。`
                );
            } else if (fetchError.message.includes('Failed to fetch')) {
                throw new Error(
                    `无法连接到后端服务。请确认：\n` +
                    `1. 后端服务已启动（访问 ${API_BASE_URL}/api/health 检查）\n` +
                    `2. 后端服务正在运行（检查终端是否有错误信息）\n` +
                    `3. 防火墙未阻止连接\n\n` +
                    `启动后端服务：cd web_service/backend && ./start_server.sh`
                );
            } else {
                throw new Error(`提交任务失败: ${fetchError.message}`);
            }
        }
        
        if (!response.ok) {
            let errorDetail = '提交失败';
            try {
                const error = await response.json();
                errorDetail = error.detail || error.message || error.error || '提交失败';
                console.error('❌ 响应错误:', error);
            } catch (e) {
                const errorText = await response.text();
                console.error('❌ 响应文本:', errorText);
                errorDetail = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorDetail);
        }
        
        const result = await response.json();
        console.log('📋 响应内容:', result);
        
        const taskId = result.task_id;
        
        // 验证task_id是否存在
        if (!taskId) {
            console.error('❌ 响应中没有task_id:', result);
            throw new Error('任务提交失败：未收到任务ID');
        }
        
        console.log('✅ 任务提交成功，任务ID:', taskId);
        console.log('任务状态:', result);
        
        // 更新按钮状态
        processBtn.textContent = '处理中...';
        updateStatus('任务已提交，正在处理...', 'processing');
        
        // 开始轮询状态
        pollTaskStatus(taskId);
        
    } catch (error) {
        const errorMsg = error.message || '处理失败';
        updateStatus(`提交失败: ${errorMsg}`, 'error');
        console.error('Process error:', error);
        processBtn.disabled = false;
        processBtn.textContent = '开始处理';
    }
}

// 轮询任务状态
async function pollTaskStatus(taskId) {
    const maxAttempts = 240; // 最多轮询240次（20分钟，每5秒一次）
    let attempts = 0;
    let pollInterval = null;
    let lastStatusTime = Date.now(); // 记录上次状态更新时间
    
    const poll = async () => {
        attempts++;
        
        // 如果正在下载，不更新状态（保持下载状态显示）
        if (isDownloading) {
            return; // 跳过本次轮询的状态更新
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/status/${taskId}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    let errorDetail = '任务不存在';
                    try {
                        const error = await response.json();
                        errorDetail = error.detail || error.message || '任务不存在';
                    } catch (e) {
                        // 忽略JSON解析错误
                    }
                    console.error('❌ 任务不存在:', errorDetail);
                    console.error('任务ID:', taskId);
                    updateStatus(`任务不存在: ${errorDetail}`, 'error');
                    clearInterval(pollInterval);
                    processBtn.disabled = false;
                    processBtn.textContent = '开始处理';
                    return;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // 更新状态
            state.taskId = result.task_id;
            state.modularOutput = result.modular_output || null;
            state.v2Output = result.v2_output || null;
            
            // 调试日志：检查两个版本的状态
            console.log('任务状态更新:', {
                task_id: result.task_id,
                modular_status: result.modular_status,
                modular_output: result.modular_output,
                v2_status: result.v2_status,
                v2_output: result.v2_output
            });
            
            // 更新下载按钮状态
            updateDownloadButton(result);
            
            if (result.status === 'success') {
                // 处理成功
                clearInterval(pollInterval);
                updateStatus(result.message || '处理完成！', 'success');
                downloadSection.style.display = 'block';
                processBtn.disabled = false;
                processBtn.textContent = '开始处理';
            } else if (result.status === 'failed') {
                // 处理失败
                clearInterval(pollInterval);
                const errorMsg = result.error || result.message || '处理失败';
                // 显示详细错误信息（如果可用）
                let displayMsg = `处理失败: ${errorMsg}`;
                if (result.modular_status === 'failed' && result.v2_status === 'failed') {
                    displayMsg += ' (两个版本都处理失败)';
                } else if (result.modular_status === 'failed') {
                    displayMsg += ' (Modular版本失败)';
                } else if (result.v2_status === 'failed') {
                    displayMsg += ' (V2版本失败)';
                }
                updateStatus(displayMsg, 'error');
                console.error('Process failed:', result);
                // 在控制台显示完整错误信息，方便调试
                if (result.error) {
                    console.error('Error details:', result.error);
                }
                processBtn.disabled = false;
                processBtn.textContent = '开始处理';
            } else if (result.status === 'processing' || result.status === 'pending') {
                // 检查是否所有版本都已完成（无论成功或失败）
                const modularDone = result.modular_status === 'success' || result.modular_status === 'failed';
                const v2Done = result.v2_status === 'success' || result.v2_status === 'failed';
                const allDone = modularDone && v2Done;
                
                // 如果所有版本都已完成，停止轮询并更新状态
                if (allDone) {
                    clearInterval(pollInterval);
                    const elapsedSeconds = attempts * 5;
                    const elapsedMinutes = Math.floor(elapsedSeconds / 60);
                    const remainingSeconds = elapsedSeconds % 60;
                    
                    // 确定最终状态消息
                    let finalMessage = '处理完成！';
                    if (result.modular_status === 'success' && result.v2_status === 'success') {
                        finalMessage = '处理完成！两个版本都已成功生成。';
                    } else if (result.modular_status === 'success') {
                        finalMessage = '处理完成！Modular版本已成功生成。';
                    } else if (result.v2_status === 'success') {
                        finalMessage = '处理完成！V2版本已成功生成。';
                    }
                    
                    if (elapsedSeconds > 60) {
                        updateStatus(`${finalMessage} (耗时${elapsedMinutes}分${remainingSeconds}秒)`, 'success');
                    } else {
                        updateStatus(`${finalMessage} (耗时${elapsedSeconds}秒)`, 'success');
                    }
                    
                    downloadSection.style.display = 'block';
                    updateDownloadButton(result);
                    processBtn.disabled = false;
                    processBtn.textContent = '开始处理';
                    return; // 停止轮询
                }
                
                // 继续处理中，显示等待时间
                const elapsedSeconds = attempts * 5;
                const elapsedMinutes = Math.floor(elapsedSeconds / 60);
                const remainingSeconds = elapsedSeconds % 60;
                
                // 显示详细状态消息
                const statusMsg = result.message || '正在处理，请稍候...';
                if (elapsedSeconds > 300) {
                    updateStatus(`${statusMsg} (已等待${elapsedMinutes}分${remainingSeconds}秒)`, 'processing');
                } else {
                    updateStatus(`${statusMsg} (已等待${elapsedSeconds}秒)`, 'processing');
                }
                
                // 如果有部分完成，显示下载区域并更新按钮
                if (result.modular_output || result.v2_output) {
                    downloadSection.style.display = 'block';
                    updateDownloadButton(result);
                }
                
                // 仍在处理中，保持按钮状态
                processBtn.disabled = true;
                processBtn.textContent = '处理中...';
            }
        } catch (error) {
            console.error('Poll error:', error);
            // 继续轮询，不中断
        }
        
        // 超时检查
        if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
            updateStatus('处理超时：处理时间超过20分钟。Render免费层资源有限，建议使用较小的测试视频或稍后重试。', 'error');
            processBtn.disabled = false;
            processBtn.textContent = '开始处理';
        }
    };
    
    // 立即执行一次
    await poll();
    
    // 每5秒轮询一次
    pollInterval = setInterval(poll, 5000);
}

// 更新状态显示
function updateStatus(message, type = '') {
    statusText.textContent = `处理状态: ${message}`;
    statusText.className = 'status-text';
    // 根据类型设置样式
    if (type === 'success') {
        statusText.style.color = '#4CAF50';
    } else if (type === 'error') {
        statusText.style.color = '#f44336';
    } else if (type === 'info') {
        statusText.style.color = '#2196F3';
    } else if (type === 'processing') {
        statusText.style.color = '#FF9800';
    } else {
        statusText.style.color = '#333333';
    }
    if (type) {
        statusText.classList.add(type);
    }
}

// 更新下载按钮状态（两个独立按钮）
function updateDownloadButton(result) {
    const modularStatus = result.modular_status || 'processing';
    const v2Status = result.v2_status || 'processing';
    
    // 更新modular按钮（在线预览功能已移除）
    if (modularStatus === 'success' && result.modular_output) {
        modularResult.style.display = 'block';
        downloadModularBtn.disabled = false;
        downloadModularBtn.querySelector('.btn-status').textContent = '✅';
        downloadModularBtn.querySelector('.btn-text').textContent = '下载视频';
        
        downloadModularBtn.onclick = async () => {
            // 重新获取最新状态（避免使用闭包中的旧值）
            try {
                const statusResponse = await fetch(`${API_BASE_URL}/api/status/${result.task_id}`);
                if (statusResponse.ok) {
                    const latestResult = await statusResponse.json();
                    if (latestResult.modular_status === 'success' && latestResult.modular_output) {
                        console.log('下载modular版本:', latestResult.modular_output);
                        const modularUrl = `${API_BASE_URL}/api/download/${latestResult.task_id}?version=modular`;
                        const modularFilename = `modular_${latestResult.task_id}.mp4`;
                        await downloadFile(modularUrl, modularFilename, 'modular');
                    } else {
                        console.warn('Modular版本状态已变更，无法下载');
                        updateStatus('Modular版本不可用', 'error');
                    }
                } else {
                    // 降级方案：使用当前result的值
                    if (result.modular_output) {
                        const modularUrl = `${API_BASE_URL}/api/download/${result.task_id}?version=modular`;
                        const modularFilename = `modular_${result.task_id}.mp4`;
                        await downloadFile(modularUrl, modularFilename, 'modular');
                    }
                }
            } catch (error) {
                console.error('获取最新状态时出错:', error);
                // 降级方案：使用当前result的值
                if (result.modular_output) {
                    const modularUrl = `${API_BASE_URL}/api/download/${result.task_id}?version=modular`;
                    await downloadFile(modularUrl, 'beatsync_modular.mp4', 'modular');
                }
            }
        };
    } else if (modularStatus === 'failed') {
        downloadModularBtn.disabled = true;
        downloadModularBtn.querySelector('.btn-status').textContent = '❌';
        downloadModularBtn.querySelector('.btn-text').textContent = 'Modular版本处理失败';
        downloadModularBtn.onclick = null;
    } else {
        downloadModularBtn.disabled = true;
        downloadModularBtn.querySelector('.btn-status').textContent = '⏳';
        downloadModularBtn.querySelector('.btn-text').textContent = 'Modular版本处理中...';
        downloadModularBtn.onclick = null;
    }
    
    // 更新v2按钮（在线预览功能已移除）
    if (v2Status === 'success' && result.v2_output) {
        v2Result.style.display = 'block';
        downloadV2Btn.disabled = false;
        downloadV2Btn.querySelector('.btn-status').textContent = '✅';
        downloadV2Btn.querySelector('.btn-text').textContent = '下载视频';
        
        downloadV2Btn.onclick = async () => {
            // 重新获取最新状态（避免使用闭包中的旧值）
            try {
                const statusResponse = await fetch(`${API_BASE_URL}/api/status/${result.task_id}`);
                if (statusResponse.ok) {
                    const latestResult = await statusResponse.json();
                    if (latestResult.v2_status === 'success' && latestResult.v2_output) {
                        console.log('下载V2版本:', latestResult.v2_output);
                        const v2Url = `${API_BASE_URL}/api/download/${latestResult.task_id}?version=v2`;
                        const v2Filename = `v2_${latestResult.task_id}.mp4`;
                        await downloadFile(v2Url, v2Filename, 'v2');
                    } else {
                        console.warn('V2版本状态已变更，无法下载');
                        updateStatus('V2版本不可用', 'error');
                    }
                } else {
                    // 降级方案：使用当前result的值
                    if (result.v2_output) {
                        const v2Url = `${API_BASE_URL}/api/download/${result.task_id}?version=v2`;
                        const v2Filename = `v2_${result.task_id}.mp4`;
                        await downloadFile(v2Url, v2Filename, 'v2');
                    }
                }
            } catch (error) {
                console.error('获取最新状态时出错:', error);
                // 降级方案：使用当前result的值
                if (result.v2_output) {
                    const v2Url = `${API_BASE_URL}/api/download/${result.task_id}?version=v2`;
                    await downloadFile(v2Url, 'beatsync_v2.mp4', 'v2');
                }
            }
        };
    } else if (v2Status === 'failed') {
        downloadV2Btn.disabled = true;
        downloadV2Btn.querySelector('.btn-status').textContent = '❌';
        downloadV2Btn.querySelector('.btn-text').textContent = 'V2版本处理失败';
        downloadV2Btn.onclick = null;
    } else {
        downloadV2Btn.disabled = true;
        downloadV2Btn.querySelector('.btn-status').textContent = '⏳';
        downloadV2Btn.querySelector('.btn-text').textContent = 'V2版本处理中...';
        downloadV2Btn.onclick = null;
    }
}

// 下载单个文件（优化：立即响应，不等待）
async function downloadFile(url, filename, version = null) {
    try {
        // 设置下载标志（防止轮询覆盖状态）
        isDownloading = true;
        downloadingVersion = version;
        
        // 检测是否为移动设备和PWA环境
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        const isPWA = window.matchMedia('(display-mode: standalone)').matches || 
                     window.navigator.standalone || 
                     document.referrer.includes('android-app://');
        
        // 根据版本显示状态
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`正在下载${versionName}结果...`, 'processing');
        } else {
            updateStatus('正在下载...', 'processing');
        }
        
        // iOS PWA环境：直接打开新窗口到下载URL（让用户手动下载）
        if (isIOS && isPWA) {
            console.log('iOS PWA环境，打开新窗口到下载URL');
            
            // 直接打开新窗口到下载URL
            // 这样用户可以在新窗口中长按视频保存
            const downloadWindow = window.open(url, '_blank');
            
            if (downloadWindow) {
                // 新窗口已打开
                if (version) {
                    const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                    updateStatus(`${versionName}下载页面已打开。请在新页面中长按视频，选择"存储视频"保存到相册`, 'info');
                } else {
                    updateStatus('已打开下载页面。请在新页面中长按视频，选择"存储视频"保存到相册', 'info');
                }
                
                // 3秒后尝试关闭提示
                setTimeout(() => {
                    if (version) {
                        const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                        updateStatus(`${versionName}下载页面已打开`, 'success');
                    } else {
                        updateStatus('下载页面已打开', 'success');
                    }
                }, 3000);
            } else {
                // 弹窗被阻止，尝试其他方法
                console.warn('新窗口被阻止，尝试使用blob方式');
                const result = await downloadFileWithBlob(url, filename, version);
                return result;
            }
            
            return true;
        }
        
        // Android PWA或其他移动设备：使用blob方式
        if (isPWA || isMobile) {
            console.log('PWA/移动设备环境，使用blob方式强制下载');
            return await downloadFileWithBlob(url, filename, version);
        }
        
        // 桌面浏览器环境，使用直接下载方式（更快）
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`正在下载${versionName}结果...`, 'processing');
        } else {
            updateStatus('正在开始下载...', 'processing');
        }
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        
        // 延迟清理，确保下载开始
        setTimeout(() => {
            document.body.removeChild(a);
        }, 100);
        
        console.log('开始下载:', filename, '(立即响应)');
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`${versionName}下载已开始`, 'success');
        } else {
            updateStatus('下载已开始', 'success');
        }
        return true;
    } catch (error) {
        console.error(`下载 ${filename} 失败:`, error);
        updateStatus(`下载失败: ${error.message}`, 'error');
        return false;
    } finally {
        // 重置下载标志（无论成功或失败）
        isDownloading = false;
        downloadingVersion = null;
    }
}

// 使用blob方式下载（辅助函数）
async function downloadFileWithBlob(url, filename, version = null) {
    try {
        // 根据版本显示状态
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`正在下载${versionName}结果...`, 'processing');
        } else {
            updateStatus('正在下载...', 'processing');
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`下载失败: ${response.statusText}`);
        }
        
        // 获取文件大小（用于显示进度）
        const contentLength = response.headers.get('Content-Length');
        const total = contentLength ? parseInt(contentLength, 10) : 0;
        
        // 使用ReadableStream读取数据（支持大文件）
        const reader = response.body.getReader();
        const chunks = [];
        let received = 0;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            chunks.push(value);
            received += value.length;
            
            // 更新进度（可选，对于大文件）
            if (total > 0) {
                const percent = Math.round((received / total) * 100);
                if (percent % 10 === 0) { // 每10%更新一次
                    if (version) {
                        const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                        updateStatus(`正在下载${versionName}结果... ${percent}%`, 'processing');
                    } else {
                        updateStatus(`正在下载... ${percent}%`, 'processing');
                    }
                }
            }
        }
        
        // 合并所有chunks
        const blob = new Blob(chunks, { type: 'application/octet-stream' }); // 使用通用类型，避免预览
        
        // 尝试使用Web Share API（iOS Safari支持，但文件大小有限制）
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        if (isIOS && navigator.share && blob.size < 10 * 1024 * 1024) { // 小于10MB
            try {
                const file = new File([blob], filename, { type: 'video/mp4' });
                await navigator.share({
                    files: [file],
                    title: filename
                });
                if (version) {
                    const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                    updateStatus(`${versionName}已通过分享保存`, 'success');
                } else {
                    updateStatus('已通过分享保存视频', 'success');
                }
                return true;
            } catch (shareError) {
                console.warn('Web Share API失败，使用blob下载:', shareError);
                // 继续使用blob下载方式
            }
        }
        
        // 使用blob URL下载
        const downloadUrl = window.URL.createObjectURL(blob);
        
        // 创建下载链接
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        
        // 延迟清理，确保下载开始
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        }, 100);
        
        console.log('下载完成:', filename);
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`${versionName}下载已开始`, 'success');
        } else {
            updateStatus('下载已开始', 'success');
        }
        return true;
    } catch (error) {
        console.error('Blob下载失败:', error);
        throw error;
    }
}

// 下载结果（自动下载所有可用版本）

// 绑定事件
processBtn.addEventListener('click', processVideo);
// 下载按钮的事件在updateDownloadButton中动态绑定

