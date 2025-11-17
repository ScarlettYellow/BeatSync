// API基础URL（根据环境自动选择）
// 开发环境：使用localhost
// 生产环境：使用Render后端URL（需要替换为实际URL）
const API_BASE_URL = (() => {
    // 如果是本地开发环境
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    // 生产环境：从环境变量或配置中获取
    // TODO: 替换为实际的Render后端URL，例如：'https://beatsync-backend.onrender.com'
    return window.API_BASE_URL || 'https://beatsync-backend.onrender.com';
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

// 处理视频
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
        processBtn.textContent = '处理中...';
        updateStatus('正在处理，请稍候...', 'processing');
        downloadSection.style.display = 'none';
        
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '处理失败');
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            state.taskId = result.task_id;
            state.modularOutput = result.modular_output || null;
            state.v2Output = result.v2_output || null;
            updateStatus('处理完成！', 'success');
            downloadSection.style.display = 'block';
        } else {
            updateStatus('处理失败', 'error');
        }
        
    } catch (error) {
        updateStatus('处理失败', 'error');
        console.error('Process error:', error);
    } finally {
        processBtn.disabled = false;
        processBtn.textContent = '开始处理';
    }
}

// 更新状态显示
function updateStatus(message, type = '') {
    statusText.textContent = `处理状态: ${message}`;
    statusText.className = 'status-text';
    if (type) {
        statusText.classList.add(type);
    }
}

// 下载单个文件
async function downloadFile(url, filename) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`下载失败: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        return true;
    } catch (error) {
        console.error(`下载 ${filename} 失败:`, error);
        return false;
    }
}

// 下载结果（自动下载所有可用版本）
async function downloadResult() {
    if (!state.taskId) {
        alert('没有可下载的结果');
        return;
    }
    
    const downloads = [];
    
    // 下载modular版本
    if (state.modularOutput) {
        downloads.push(
            downloadFile(
                `${API_BASE_URL}/api/download/${state.taskId}?version=modular`,
                `beatsync_${state.taskId}_modular.mp4`
            )
        );
    }
    
    // 下载v2版本
    if (state.v2Output) {
        // 延迟一下，避免浏览器阻止多个下载
        setTimeout(() => {
            downloadFile(
                `${API_BASE_URL}/api/download/${state.taskId}?version=v2`,
                `beatsync_${state.taskId}_v2.mp4`
            );
        }, 500);
    }
    
    // 等待所有下载完成
    const results = await Promise.all(downloads);
    const successCount = results.filter(r => r).length;
    const totalCount = downloads.length + (state.v2Output ? 1 : 0);
    
    if (successCount < totalCount) {
        alert(`下载完成：${successCount}/${totalCount} 个文件成功`);
    }
}

// 绑定事件
processBtn.addEventListener('click', processVideo);
downloadBtn.addEventListener('click', downloadResult);

