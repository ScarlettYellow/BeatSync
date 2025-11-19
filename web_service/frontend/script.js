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
    
    // 生产环境：从环境变量或配置中获取
    // 注意：部署时需要替换为实际的Render后端URL
    // 例如：'https://beatsync-backend-xxx.onrender.com'
    const backendUrl = window.API_BASE_URL || 'https://beatsync-backend-asha.onrender.com';
    console.log('🟢 生产环境检测');
    console.log('   访问地址:', window.location.href);
    console.log('   后端URL:', backendUrl);
    return backendUrl;
})();

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

// DOM元素
const danceFileInput = document.getElementById('dance-file');
const bgmFileInput = document.getElementById('bgm-file');
const processBtn = document.getElementById('process-btn');
const statusText = document.getElementById('status-text');
const downloadSection = document.getElementById('download-section');
const downloadBtn = document.getElementById('download-btn');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 重置所有状态（确保刷新后清空之前的记录）
    resetState();
    setupFileInputs();
    setupDragAndDrop();
    updateProcessButton();
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
    downloadBtn.disabled = true;
    downloadBtn.textContent = '下载结果';
    downloadBtn.onclick = null;
    
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

// 上传文件
async function uploadFile(file, fileType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    
    try {
        updateStatus(`正在上传${fileType === 'dance' ? '原始视频' : '音源视频'}...`, 'processing');
        
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上传失败');
        }
        
        const result = await response.json();
        
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
        
        updateStatus('文件上传成功', 'success');
        updateProcessButton();
        
    } catch (error) {
        updateStatus(`上传失败: ${error.message}`, 'error');
        console.error('Upload error:', error);
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
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            let errorDetail = '提交失败';
            try {
                const error = await response.json();
                errorDetail = error.detail || error.message || error.error || '提交失败';
            } catch (e) {
                errorDetail = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorDetail);
        }
        
        const result = await response.json();
        const taskId = result.task_id;
        
        // 验证task_id是否存在
        if (!taskId) {
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
                // 继续处理中
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

// 更新下载按钮状态（单个按钮，下载两个版本的结果）
function updateDownloadButton(result) {
    const modularStatus = result.modular_status || 'processing';
    const v2Status = result.v2_status || 'processing';
    const modularSuccess = modularStatus === 'success' && result.modular_output;
    const v2Success = v2Status === 'success' && result.v2_output;
    
    // 如果至少有一个版本成功，启用下载按钮
    if (modularSuccess || v2Success) {
        downloadBtn.disabled = false;
        downloadBtn.textContent = '下载结果';
        downloadBtn.onclick = async () => {
            console.log('开始下载，modular成功:', modularSuccess, 'v2成功:', v2Success);
            
            // 下载所有可用的版本结果
            // 先下载modular版本（如果成功）
            if (modularSuccess && result.modular_output) {
                console.log('下载modular版本:', result.modular_output);
                const modularUrl = `${API_BASE_URL}/api/download/${result.task_id}?version=modular`;
                await downloadFile(modularUrl, 'beatsync_modular.mp4');
            }
            
            // 延迟500ms后下载V2版本（如果成功），避免浏览器阻止多个下载
            if (v2Success && result.v2_output) {
                console.log('延迟下载V2版本:', result.v2_output);
                setTimeout(async () => {
                    const v2Url = `${API_BASE_URL}/api/download/${result.task_id}?version=v2`;
                    await downloadFile(v2Url, 'beatsync_v2.mp4');
                }, 500);
            }
        };
    } else if (modularStatus === 'failed' && v2Status === 'failed') {
        // 两个版本都失败
        downloadBtn.disabled = true;
        downloadBtn.textContent = '处理失败';
        downloadBtn.onclick = null;
    } else {
        // 处理中
        downloadBtn.disabled = true;
        downloadBtn.textContent = '处理中...';
        downloadBtn.onclick = null;
    }
}

// 下载单个文件（优先保存到相册）
async function downloadFile(url, filename) {
    try {
        // 检测是否为移动设备
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        
        // 对于移动设备，优先使用Web Share API（可以直接保存到相册）
        // 这是最接近"默认保存到相册"的方式，用户只需在分享菜单中选择"存储视频"
        if (isMobile && navigator.share) {
            try {
                console.log('使用Web Share API（可保存到相册）...');
                updateStatus('正在准备视频，请稍候...', 'processing');
                
                // 先获取文件
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`下载失败: ${response.statusText}`);
                }
                
                const blob = await response.blob();
                const file = new File([blob], filename, { type: 'video/mp4' });
                
                // 使用Web Share API分享文件
                // 在iOS上，"存储视频"通常是分享菜单中的第一个选项
                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    updateStatus('请选择"存储视频"保存到相册', 'info');
                    await navigator.share({
                        files: [file],
                        title: '保存视频到相册',
                        text: '请选择"存储视频"选项保存到相册'
                    });
                    console.log('✅ 已通过Web Share API分享');
                    updateStatus('视频已保存到相册', 'success');
                    return true;
                } else {
                    // 如果不支持分享文件，回退到直接下载
                    console.log('Web Share API不支持文件分享，使用直接下载...');
                }
            } catch (shareError) {
                // 如果用户取消分享，不报错
                if (shareError.name === 'AbortError') {
                    console.log('用户取消了分享');
                    updateStatus('下载已取消', '');
                    return false;
                }
                console.log('Web Share API失败，使用直接下载:', shareError);
            }
        }
        
        // 直接下载方式（适用于桌面浏览器和移动浏览器）
        // 注意：由于浏览器安全限制，无法直接保存到相册，需要用户手动操作
        updateStatus('正在下载...', 'processing');
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
        
        console.log('开始下载:', filename);
        
        // 如果是移动设备，提示用户如何保存到相册
        if (isMobile) {
            setTimeout(() => {
                if (isIOS) {
                    updateStatus('下载完成。请在"文件"应用中长按视频，选择"存储视频"保存到相册', 'info');
                } else {
                    updateStatus('下载完成。请在文件管理器中找到视频，移动到相册文件夹', 'info');
                }
            }, 1000);
        } else {
            updateStatus('下载完成', 'success');
        }
        
        return true;
    } catch (error) {
        console.error(`下载 ${filename} 失败:`, error);
        // 如果直接下载失败，尝试使用fetch+blob方式（备用方案）
        try {
            console.log('直接下载失败，尝试使用blob方式...');
            updateStatus('正在下载...', 'processing');
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`下载失败: ${response.statusText}`);
            }
            
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
            updateStatus('下载完成', 'success');
            return true;
        } catch (blobError) {
            console.error('Blob download error:', blobError);
            updateStatus(`下载失败: ${blobError.message}`, 'error');
            return false;
        }
    }
}

// 下载结果（自动下载所有可用版本）

// 绑定事件
processBtn.addEventListener('click', processVideo);
// 下载按钮的事件在updateDownloadButton中动态绑定

