// 检测是否为 Capacitor 原生 App 环境（全局变量）
const isCapacitorNative = typeof window.Capacitor !== 'undefined' && window.Capacitor.isNativePlatform;

// 原生分享/保存功能开关（已回退到分享菜单方案）
const USE_NATIVE_SAVE_TO_GALLERY = false;

// App端：禁用双击放大
function applyViewportForApp() {
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
        viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
    }
}

// 按钮加载态辅助
function setButtonLoading(button, loadingText) {
    if (!button) return;
    button.dataset.originalText = button.dataset.originalText || (button.querySelector('.btn-text') ? button.querySelector('.btn-text').textContent : button.textContent);
    if (button.querySelector('.btn-text')) {
        button.querySelector('.btn-text').textContent = loadingText;
    } else {
        button.textContent = loadingText;
    }
    button.classList.add('btn-loading');
    button.disabled = true;
}

function clearButtonLoading(button) {
    if (!button) return;
    const originalText = button.dataset.originalText;
    if (originalText) {
        if (button.querySelector('.btn-text')) {
            button.querySelector('.btn-text').textContent = originalText;
        } else {
            button.textContent = originalText;
        }
        delete button.dataset.originalText;
    }
    button.classList.remove('btn-loading');
    button.disabled = false;
}

// App端：基础交互守护（禁用长按菜单/选中/手势缩放）
function applyNativeInteractionGuards() {
    document.body.classList.add('is-native');
    const preventDefault = (e) => e.preventDefault();
    document.addEventListener('contextmenu', preventDefault, { passive: false });
    document.addEventListener('selectstart', preventDefault, { passive: false });
    document.addEventListener('gesturestart', preventDefault, { passive: false });
    // 保持触摸滚动，但禁止回弹放大
    document.documentElement.style.overscrollBehaviorY = 'contain';
    document.body.style.overscrollBehaviorY = 'contain';
}

// 保持唤醒（下载/处理时防息屏）
let wakeLockSentinel = null;
let wakeLockRequestCount = 0;
async function requestWakeLock(reason = 'general') {
    wakeLockRequestCount += 1;
    if (!('wakeLock' in navigator)) return;
    if (wakeLockSentinel) return;
    try {
        wakeLockSentinel = await navigator.wakeLock.request('screen');
        wakeLockSentinel.addEventListener('release', () => {
            wakeLockSentinel = null;
        });
        console.log('🔒 WakeLock acquired:', reason);
    } catch (err) {
        console.warn('WakeLock request failed:', err);
        wakeLockSentinel = null;
    }
}

function releaseWakeLock(reason = 'general') {
    wakeLockRequestCount = Math.max(0, wakeLockRequestCount - 1);
    if (wakeLockSentinel && wakeLockRequestCount === 0) {
        wakeLockSentinel.release().catch(() => {});
        wakeLockSentinel = null;
        console.log('🔓 WakeLock released:', reason);
    }
}

// 响应式间距系统：根据屏幕尺寸动态调整间距
function getResponsiveSpacing() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const isLandscape = width > height;
    const diagonal = Math.sqrt(width * width + height * height);
    
    // 屏幕尺寸分类
    let screenSize;
    if (width < 375) {
        screenSize = 'small';      // 小屏手机（iPhone SE等）
    } else if (width < 768) {
        screenSize = 'medium';     // 标准手机
    } else if (width < 1024) {
        screenSize = 'large';      // 大屏手机/小平板
    } else {
        screenSize = 'xlarge';     // 平板/桌面
    }
    
    // 根据屏幕尺寸返回间距配置
    const spacingConfig = {
        small: {
            containerGap: 12,          // 紧凑间距
            sectionGap: 12,
            sectionMargin: 12,
            h1MarginBottom: 16,
            uploadAreaPadding: '18px 14px',
            uploadAreaMinHeight: 90,
            containerPaddingTop: 20,
            containerPaddingBottom: 20
        },
        medium: {
            containerGap: 16,          // 标准间距
            sectionGap: 16,
            sectionMargin: 16,
            h1MarginBottom: 20,
            uploadAreaPadding: '20px 16px',
            uploadAreaMinHeight: 100,
            containerPaddingTop: 24,
            containerPaddingBottom: 24
        },
        large: {
            containerGap: 24,          // 增加间距
            sectionGap: 24,
            sectionMargin: 24,
            h1MarginBottom: 28,
            uploadAreaPadding: '28px 20px',
            uploadAreaMinHeight: 120,
            containerPaddingTop: 32,
            containerPaddingBottom: 32
        },
        xlarge: {
            containerGap: 32,          // 更大间距
            sectionGap: 32,
            sectionMargin: 32,
            h1MarginBottom: 36,
            uploadAreaPadding: '32px 24px',
            uploadAreaMinHeight: 140,
            containerPaddingTop: 40,
            containerPaddingBottom: 40
        }
    };
    
    return {
        ...spacingConfig[screenSize],
        screenSize,
        width,
        height,
        isLandscape
    };
}

// API基础URL（根据环境自动选择）
// 开发环境：使用localhost或局域网IP
// 生产环境：使用Render后端URL（需要替换为实际URL）
const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    if (isCapacitorNative) {
        const backendUrl = 'https://beatsync.site';
        console.log('📱 Capacitor 原生环境检测');
        console.log('   访问地址:', window.location.href);
        console.log('   后端URL:', backendUrl);
        return backendUrl;
    }
    
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
    // 正式方案：使用域名 beatsync.site（通过Nginx反向代理，端口443，Let's Encrypt证书）
    const backendUrl = window.API_BASE_URL || 'https://beatsync.site';
    console.log('🟢 生产环境检测（腾讯云服务器 - HTTPS - 使用域名）');
    console.log('   访问地址:', window.location.href);
    console.log('   后端URL:', backendUrl);
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

// 下载状态标志（用于同时显示下载和处理状态）
let isDownloading = false;
let downloadingVersion = null;
let downloadingStatusMessage = null; // 当前显示的下载状态消息
let currentDownloadContext = null; // 保存当前下载的上下文，用于恢复

// 轮询状态管理
let isPolling = false;
let currentPollInterval = null; // 当前轮询定时器

// DOM元素
const danceFileInput = document.getElementById('dance-file');
const bgmFileInput = document.getElementById('bgm-file');
const processBtn = document.getElementById('process-btn');
const statusText = document.getElementById('status-text');
const downloadSection = document.getElementById('download-section');
const downloadModularBtn = document.getElementById('download-modular-btn');
const downloadV2Btn = document.getElementById('download-v2-btn');
const resetBtn = document.getElementById('reset-btn');
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
const statusSkeleton = document.getElementById('status-skeleton');

function showProgress(percent = 0, label = '') {
    if (!uploadProgressContainer || !uploadProgressFill || !uploadProgressText) return;
    uploadProgressContainer.style.display = 'flex';
    uploadProgressFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
    uploadProgressText.textContent = label || `${percent}%`;
}

function hideProgress() {
    if (!uploadProgressContainer || !uploadProgressFill || !uploadProgressText) return;
    uploadProgressContainer.style.display = 'none';
    uploadProgressFill.style.width = '0%';
    uploadProgressText.textContent = '0%';
}

// 监听页面可见性变化和app状态变化，防止下载中断
let downloadReader = null; // 保存当前的reader，用于检测是否中断

document.addEventListener('visibilitychange', () => {
    // 当页面重新可见时，如果正在下载，重新请求wakeLock
    if (!document.hidden && isDownloading) {
        console.log('📱 页面重新可见，正在下载中，重新请求wakeLock');
        requestWakeLock('download-resume');
    }
});

// 监听Capacitor App状态变化（如果可用）
if (typeof window.Capacitor !== 'undefined' && window.Capacitor.Plugins && window.Capacitor.Plugins.App) {
    window.Capacitor.Plugins.App.addListener('appStateChange', (state) => {
        console.log('📱 App状态变化:', state.isActive ? '激活' : '后台');
        // 当app从后台恢复时
        if (state.isActive && isDownloading && currentDownloadContext) {
            console.log('📱 App恢复，检查下载状态');
            // 重新请求wakeLock
            requestWakeLock('download-resume');
            // 检查reader是否还在工作（通过检查是否有pending的read）
            // 如果reader已断开，需要重新开始下载
            if (downloadReader) {
                // 尝试检测reader是否还可用
                // 如果不可用，提示用户下载已中断
                console.warn('⚠️ 检测到app恢复，但ReadableStream可能已断开');
                // 注意：iOS系统在后台会断开ReadableStream，无法恢复
                // 只能提示用户重新下载
            }
        }
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 仅在App端应用特殊样式（区分App端和网页端）
    if (isCapacitorNative) {
        // 禁用双击缩放（仅App端）
        applyViewportForApp();
        applyNativeInteractionGuards();

        // 计算安全区域值
        const safeAreaTop = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-top)') || '0', 10) || 0;
        const safeAreaBottom = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-bottom)') || '0', 10) || 0;
        
        // 设置body的padding（App端）- 减少顶部留白10px
        const bodyPaddingTop = Math.max(90, safeAreaTop ? safeAreaTop + 30 : 70);
        document.body.style.setProperty('padding-top', `${bodyPaddingTop}px`, 'important');
        document.body.style.setProperty('padding-bottom', `${Math.max(20, safeAreaBottom)}px`, 'important');
        
        // 响应式优化：根据屏幕尺寸动态调整间距
        const spacing = getResponsiveSpacing();
        const container = document.querySelector('.container');
        if (container) {
            // 优化顶部padding：根据屏幕尺寸和安全区域适配
            const paddingTop = Math.max(spacing.containerPaddingTop, safeAreaTop + 16);
            const paddingBottom = Math.max(spacing.containerPaddingBottom, safeAreaBottom + 16);
            
            // 关键修复：移除min-height，让内容自然排列，不强制占满屏幕
            container.style.setProperty('min-height', 'auto', 'important');
            container.style.setProperty('padding-top', `${paddingTop}px`, 'important');
            container.style.setProperty('padding-bottom', `${paddingBottom}px`, 'important');
            // 使用响应式间距系统
            container.style.setProperty('gap', `${spacing.containerGap}px`, 'important');
            
            // 优化上传区域间距
            const uploadSection = document.querySelector('.upload-section');
            if (uploadSection) {
                uploadSection.style.setProperty('gap', `${spacing.sectionGap}px`, 'important');
                uploadSection.style.setProperty('margin-bottom', `${spacing.sectionMargin}px`, 'important');
                // 关键修复：移除flex: 1，避免占据所有剩余空间
                uploadSection.style.setProperty('flex', 'none', 'important');
            }
            
            // 优化操作区域：根据屏幕尺寸调整间距
            const actionSection = document.querySelector('.action-section');
            if (actionSection) {
                actionSection.style.setProperty('margin-bottom', `${Math.max(12, spacing.sectionMargin - 4)}px`, 'important');
                actionSection.style.setProperty('margin-top', '0px', 'important');
            }
            
            // 优化状态区域
            const statusSection = document.querySelector('.status-section');
            if (statusSection) {
                statusSection.style.setProperty('margin-bottom', `${Math.max(12, spacing.sectionMargin - 4)}px`, 'important');
                statusSection.style.setProperty('min-height', 'auto', 'important');
            }
            
            // 优化标题：根据屏幕尺寸调整间距
            const h1 = document.querySelector('h1');
            if (h1) {
                h1.style.setProperty('margin-bottom', `${spacing.h1MarginBottom}px`, 'important');
                h1.style.setProperty('margin-top', '0px', 'important');
                h1.style.setProperty('padding-top', '0px', 'important');
            }
            
            // 优化上传卡片：根据屏幕尺寸调整内边距
            const uploadAreas = document.querySelectorAll('.upload-area');
            uploadAreas.forEach(area => {
                area.style.setProperty('padding', spacing.uploadAreaPadding, 'important');
                area.style.setProperty('min-height', `${spacing.uploadAreaMinHeight}px`, 'important');
            });
            
            console.log('[UI优化] App端响应式布局优化:', {
                screenSize: spacing.screenSize,
                screenWidth: spacing.width,
                screenHeight: spacing.height,
                isLandscape: spacing.isLandscape,
                safeAreaTop,
                safeAreaBottom,
                paddingTop,
                paddingBottom,
                bodyPaddingTop,
                containerGap: spacing.containerGap,
                sectionGap: spacing.sectionGap,
                minHeight: 'auto',
                uploadSectionFlex: 'none'
            });
        }
        
        // 隐藏App端滚动条
        document.documentElement.style.setProperty('overflow-y', 'hidden', 'important');
        document.body.style.setProperty('overflow-y', 'hidden', 'important');
        
        // 添加内联样式到head（更可靠）
        const styleElement = document.getElementById('app-specific-styles');
        if (styleElement) {
            styleElement.textContent = `
                /* App端专用样式 - 减少顶部留白10px */
                body {
                    padding-top: ${Math.max(90, safeAreaTop ? safeAreaTop + 30 : 70)}px !important;
                    padding-bottom: ${Math.max(20, safeAreaBottom)}px !important;
                    overflow-y: hidden !important;
                }
                
                html {
                    overflow-y: hidden !important;
                }
                
                /* 响应式优化：根据屏幕尺寸动态调整（通过JavaScript动态设置） */
                .container {
                    min-height: auto !important;
                }
                
                .upload-section {
                    flex: none !important;
                }
                
                .status-section {
                    min-height: auto !important;
                }
                
                h1 {
                    margin-top: 0px !important;
                    padding-top: 0px !important;
                }
                
                /* 隐藏滚动条 */
                ::-webkit-scrollbar {
                    display: none !important;
                }
                
                * {
                    -ms-overflow-style: none !important;
                    scrollbar-width: none !important;
                }
            `;
        }
    }
    
    // 手机网页端：应用响应式布局优化（非App端但移动设备）
    if (!isCapacitorNative) {
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        if (isMobile) {
            // 计算安全区域值（手机网页端）
            const safeAreaTop = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-top)') || '0', 10) || 0;
            const safeAreaBottom = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-bottom)') || '0', 10) || 0;
            
            // 设置body的padding-top，与App端保持一致（减少顶部留白10px）
            const bodyPaddingTop = Math.max(70, safeAreaTop ? safeAreaTop + 30 : 50);
            document.body.style.setProperty('padding-top', `${bodyPaddingTop}px`, 'important');
            document.body.style.setProperty('padding-bottom', `${Math.max(20, safeAreaBottom)}px`, 'important');
            
            // 响应式优化：根据屏幕尺寸动态调整间距
            const spacing = getResponsiveSpacing();
            
            // 应用响应式布局优化
            const container = document.querySelector('.container');
            if (container) {
                const paddingTop = Math.max(spacing.containerPaddingTop, safeAreaTop + 16);
                const paddingBottom = Math.max(spacing.containerPaddingBottom, safeAreaBottom + 16);
                container.style.setProperty('min-height', 'auto', 'important');
                container.style.setProperty('gap', `${spacing.containerGap}px`, 'important');
                container.style.setProperty('padding-top', `${paddingTop}px`, 'important');
                container.style.setProperty('padding-bottom', `${paddingBottom}px`, 'important');
            }
            
            const uploadSection = document.querySelector('.upload-section');
            if (uploadSection) {
                uploadSection.style.setProperty('flex', 'none', 'important');
                uploadSection.style.setProperty('gap', `${spacing.sectionGap}px`, 'important');
                uploadSection.style.setProperty('margin-bottom', `${spacing.sectionMargin}px`, 'important');
            }
            
            const actionSection = document.querySelector('.action-section');
            if (actionSection) {
                actionSection.style.setProperty('margin-bottom', `${Math.max(12, spacing.sectionMargin - 4)}px`, 'important');
                actionSection.style.setProperty('margin-top', '0px', 'important');
            }
            
            const statusSection = document.querySelector('.status-section');
            if (statusSection) {
                statusSection.style.setProperty('margin-bottom', `${Math.max(12, spacing.sectionMargin - 4)}px`, 'important');
                statusSection.style.setProperty('min-height', 'auto', 'important');
            }
            
            const h1 = document.querySelector('h1');
            if (h1) {
                h1.style.setProperty('margin-bottom', `${spacing.h1MarginBottom}px`, 'important');
                h1.style.setProperty('margin-top', '0px', 'important');
                h1.style.setProperty('padding-top', '0px', 'important');
            }
            
            const uploadAreas = document.querySelectorAll('.upload-area');
            uploadAreas.forEach(area => {
                area.style.setProperty('padding', spacing.uploadAreaPadding, 'important');
                area.style.setProperty('min-height', `${spacing.uploadAreaMinHeight}px`, 'important');
            });
            
            console.log('[UI优化] 手机网页端响应式布局优化:', {
                screenSize: spacing.screenSize,
                screenWidth: spacing.width,
                screenHeight: spacing.height,
                safeAreaTop,
                safeAreaBottom,
                bodyPaddingTop
            });
        }
    }
    
    // 响应式优化：监听窗口大小变化，动态调整间距
    let resizeTimer;
    function handleResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (isCapacitorNative) {
                // App端：重新应用响应式间距
                const safeAreaTop = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-top)') || '0', 10) || 0;
                const safeAreaBottom = parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-bottom)') || '0', 10) || 0;
                const spacing = getResponsiveSpacing();
                
                const container = document.querySelector('.container');
                if (container) {
                    const paddingTop = Math.max(spacing.containerPaddingTop, safeAreaTop + 16);
                    const paddingBottom = Math.max(spacing.containerPaddingBottom, safeAreaBottom + 16);
                    container.style.setProperty('gap', `${spacing.containerGap}px`, 'important');
                    container.style.setProperty('padding-top', `${paddingTop}px`, 'important');
                    container.style.setProperty('padding-bottom', `${paddingBottom}px`, 'important');
                }
                
                const uploadSection = document.querySelector('.upload-section');
                if (uploadSection) {
                    uploadSection.style.setProperty('gap', `${spacing.sectionGap}px`, 'important');
                    uploadSection.style.setProperty('margin-bottom', `${spacing.sectionMargin}px`, 'important');
                }
                
                const h1 = document.querySelector('h1');
                if (h1) {
                    h1.style.setProperty('margin-bottom', `${spacing.h1MarginBottom}px`, 'important');
                }
                
                const uploadAreas = document.querySelectorAll('.upload-area');
                uploadAreas.forEach(area => {
                    area.style.setProperty('padding', spacing.uploadAreaPadding, 'important');
                    area.style.setProperty('min-height', `${spacing.uploadAreaMinHeight}px`, 'important');
                });
            }
        }, 150); // 防抖：150ms
    }
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);
    
    // 设置重置按钮事件
    if (resetBtn) {
        resetBtn.addEventListener('click', handleReset);
    }
    
    // 重置所有状态（确保刷新后清空之前的记录）
    resetState();
    setupFileInputs();
    setupDragAndDrop();
    updateProcessButton();
    updateResetButtonVisibility();
    
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
    
    // 停止轮询（如果有）
    if (isPolling) {
        stopPolling();
    }
    
    // 重置下载状态（必须在更新状态显示之前清除，防止下载函数继续更新）
    isDownloading = false;
    downloadingVersion = null;
    downloadingStatusMessage = null;
    
    // 重置状态显示（必须在清除下载状态后立即更新，确保覆盖下载状态）
    updateStatus('等待上传文件...', '');
    if (statusSkeleton) statusSkeleton.style.display = 'none';
    hideProgress();
    
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
    
    // 隐藏重置按钮（无内容时）
    updateResetButtonVisibility();
    
    releaseWakeLock('processing');
    releaseWakeLock('download');
}

// 检查是否有内容需要重置
function hasContentToReset() {
    return state.danceFileId !== null || 
           state.bgmFileId !== null || 
           state.taskId !== null ||
           state.danceFile !== null ||
           state.bgmFile !== null ||
           downloadSection.style.display !== 'none' ||
           isPolling ||
           isDownloading;
}

// 更新重置按钮显示状态
function updateResetButtonVisibility() {
    if (resetBtn) {
        if (hasContentToReset()) {
            resetBtn.style.display = 'flex';
        } else {
            resetBtn.style.display = 'none';
        }
    }
}

// 清空/重置任务（带确认）
async function handleReset() {
    // 检查是否有内容需要重置
    if (!hasContentToReset()) {
        return;
    }
    
    // 移动端友好的确认对话框
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    let confirmed = false;
    
    if (isMobile) {
        // 移动端：使用原生confirm（更友好）
        confirmed = confirm('确定要清空当前任务吗？\n\n这将清除：\n• 已上传的文件\n• 处理进度\n• 下载结果');
    } else {
        // 桌面端：使用更详细的确认
        confirmed = confirm('确定要清空当前任务吗？\n\n这将清除：\n• 已上传的文件\n• 处理进度\n• 下载结果\n\n此操作不可撤销。');
    }
    
    if (!confirmed) {
        return;
    }
    
    // 执行重置
    console.log('🔄 用户触发清空任务');
    
    // 添加视觉反馈：按钮旋转动画
    if (resetBtn) {
        resetBtn.style.pointerEvents = 'none';
        resetBtn.classList.add('resetting');
        
        // 重置状态
        resetState();
        
        // 更新处理按钮状态
        updateProcessButton();
        
        // 显示成功反馈
        updateStatus('任务已清空', 'success');
        
        // 恢复按钮状态（延迟，让动画完成）
        setTimeout(() => {
            if (resetBtn) {
                resetBtn.classList.remove('resetting');
                resetBtn.style.pointerEvents = 'auto';
            }
            // 清除状态消息
            setTimeout(() => {
                updateStatus('等待上传文件...', '');
            }, 1500);
        }, 500);
    } else {
        // 如果没有按钮，直接重置
        resetState();
        updateProcessButton();
        updateStatus('任务已清空', 'success');
        setTimeout(() => {
            updateStatus('等待上传文件...', '');
        }, 1500);
    }
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
                console.warn('⚠️ SSL证书错误：请检查SSL证书配置');
                console.warn('   解决方法：请先手动访问健康检查地址确认证书状态');
                console.warn(`   健康检查地址：${API_BASE_URL}/api/health`);
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
            
            // HTTPS证书提示
            if (API_BASE_URL.startsWith('https://')) {
                errorMsg += `\n⚠️ HTTPS证书提示：\n`;
                errorMsg += `如果遇到SSL证书错误，某些浏览器（如夸克、微信）可能需要先手动访问健康检查地址并接受证书。\n`;
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
        
        // 更新重置按钮显示状态
        updateResetButtonVisibility();
        
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
    
    setButtonLoading(processBtn, '提交中...');
    if (statusSkeleton) statusSkeleton.style.display = 'flex';
    requestWakeLock('processing');
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
        
        // 更新重置按钮显示状态
        updateResetButtonVisibility();
        
    } catch (error) {
        const errorMsg = error.message || '处理失败';
        updateStatus(`提交失败: ${errorMsg}`, 'error');
        console.error('Process error:', error);
        processBtn.disabled = false;
        clearButtonLoading(processBtn);
        processBtn.textContent = '开始处理';
    } finally {
        // 等待轮询接管后由 stopPolling 释放；提交失败则立即释放
        if (!isPolling) {
            releaseWakeLock('processing');
        }
    }
}

// 停止轮询
function stopPolling() {
    if (currentPollInterval) {
        clearInterval(currentPollInterval);
        currentPollInterval = null;
    }
    isPolling = false;
    console.log('🛑 轮询已停止');
    releaseWakeLock('processing');
}


// 轮询任务状态
async function pollTaskStatus(taskId) {
    const maxAttempts = 240; // 最多轮询240次（20分钟，每5秒一次）
    let attempts = 0;
    let pollInterval = null;
    let lastStatusTime = Date.now(); // 记录上次状态更新时间
    const processingStartTime = Date.now(); // 记录处理开始时间
    
    // 停止之前的轮询（如果有）
    stopPolling();
    
    // 标记轮询开始
    isPolling = true;
    
    // 保存到全局变量，以便重置时可以停止
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
                    currentPollInterval = null;
                    currentPollInterval = null;
                    isPolling = false;
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
                currentPollInterval = null;
                isPolling = false; // 标记轮询结束
                updateResetButtonVisibility();
                const elapsed = Math.round((Date.now() - processingStartTime) / 1000); // 计算耗时（秒）
                console.log(`✅ 任务处理成功 (耗时${elapsed}秒)`);
                updateStatus(result.message || '处理完成！', 'success');
                downloadSection.style.display = 'block';
                updateResetButtonVisibility();
                processBtn.disabled = false;
                processBtn.textContent = '开始处理';
            } else if (result.status === 'failed') {
                // 处理失败
                clearInterval(pollInterval);
                currentPollInterval = null;
                isPolling = false; // 标记轮询结束
                updateResetButtonVisibility();
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
                    currentPollInterval = null;
                    isPolling = false; // 标记轮询结束
                    updateResetButtonVisibility();
                    const elapsedSeconds = attempts * 5;
                    const elapsedMinutes = Math.floor(elapsedSeconds / 60);
                    const remainingSeconds = elapsedSeconds % 60;
                    const elapsedMs = Date.now() - processingStartTime; // 计算实际耗时（毫秒）
                    const elapsedSec = Math.round(elapsedMs / 1000); // 转换为秒
                    
                    // 确定最终状态消息
                    let finalMessage = '处理完成！';
                    if (result.modular_status === 'success' && result.v2_status === 'success') {
                        finalMessage = '处理完成！两个版本都已成功生成。';
                    } else if (result.modular_status === 'success') {
                        finalMessage = '处理完成！Modular版本已成功生成。';
                    } else if (result.v2_status === 'success') {
                        finalMessage = '处理完成！V2版本已成功生成。';
                    }
                    
                    // 在控制台显示处理成功日志
                    console.log(`✅ 任务处理成功 (耗时${elapsedSec}秒)`);
                    
                    if (elapsedSeconds > 60) {
                        updateStatus(`${finalMessage} (耗时${elapsedMinutes}分${remainingSeconds}秒)`, 'success');
                    } else {
                        updateStatus(`${finalMessage} (耗时${elapsedSeconds}秒)`, 'success');
                    }
                    
                    downloadSection.style.display = 'block';
                    updateDownloadButton(result);
                    updateResetButtonVisibility();
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
                let processingStatusMsg;
                if (elapsedSeconds > 300) {
                    processingStatusMsg = `${statusMsg} (已等待${elapsedMinutes}分${remainingSeconds}秒)`;
                } else {
                    processingStatusMsg = `${statusMsg} (已等待${elapsedSeconds}秒)`;
                }
                
                // 如果正在下载，同时显示下载状态和处理状态
                if (isDownloading && downloadingStatusMessage) {
                    updateStatusWithMultiple(
                        [downloadingStatusMessage, processingStatusMsg],
                        ['processing', 'processing']
                    );
                } else {
                    updateStatus(processingStatusMsg, 'processing');
                }
                
                // 如果有部分完成，显示下载区域并更新按钮
                if (result.modular_output || result.v2_output) {
                    downloadSection.style.display = 'block';
                    updateDownloadButton(result);
                    updateResetButtonVisibility();
                    updateResetButtonVisibility();
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
            currentPollInterval = null;
            isPolling = false; // 标记轮询结束
            updateResetButtonVisibility();
            updateStatus('处理超时：处理时间超过20分钟。Render免费层资源有限，建议使用较小的测试视频或稍后重试。', 'error');
            processBtn.disabled = false;
            processBtn.textContent = '开始处理';
        }
    };
    
    // 立即执行一次
    await poll();
    
    // 每5秒轮询一次
    pollInterval = setInterval(poll, 5000);
    currentPollInterval = pollInterval; // 保存到全局变量
}

// 更新状态显示
function updateStatus(message, type = '') {
    statusText.textContent = `处理状态: ${message}`;
    statusText.className = 'status-text';
    if (statusSkeleton) statusSkeleton.style.display = 'none';
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

// 更新状态显示（支持多个状态同时显示）
function updateStatusWithMultiple(messages, types = []) {
    // messages: 状态消息数组
    // types: 对应的类型数组（可选）
    if (messages.length === 0) return;
    
    // 如果只有一个消息，使用原来的方式
    if (messages.length === 1) {
        updateStatus(messages[0], types[0] || '');
        return;
    }
    
    // 多个消息，用换行符连接
    const combinedMessage = messages.join('\n');
    statusText.textContent = `处理状态:\n${combinedMessage}`;
    statusText.className = 'status-text';
    if (statusSkeleton) statusSkeleton.style.display = 'none';
    
    // 设置样式（如果有多个类型，使用第一个类型）
    const primaryType = types[0] || '';
    if (primaryType === 'success') {
        statusText.style.color = '#4CAF50';
    } else if (primaryType === 'error') {
        statusText.style.color = '#f44336';
    } else if (primaryType === 'info') {
        statusText.style.color = '#2196F3';
    } else if (primaryType === 'processing') {
        statusText.style.color = '#FF9800';
    } else {
        statusText.style.color = '#333333';
    }
    if (primaryType) {
        statusText.classList.add(primaryType);
    }
    
    // 设置样式支持换行
    statusText.style.whiteSpace = 'pre-line';
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
                        await downloadFile(modularUrl, modularFilename, 'modular', downloadModularBtn);
                    } else {
                        console.warn('Modular版本状态已变更，无法下载');
                        updateStatus('Modular版本不可用', 'error');
                    }
                } else {
                    // 降级方案：使用当前result的值
                    if (result.modular_output) {
                        const modularUrl = `${API_BASE_URL}/api/download/${result.task_id}?version=modular`;
                        const modularFilename = `modular_${result.task_id}.mp4`;
                        await downloadFile(modularUrl, modularFilename, 'modular', downloadModularBtn);
                    }
                }
            } catch (error) {
                console.error('获取最新状态时出错:', error);
                // 降级方案：使用当前result的值
                if (result.modular_output) {
                    const modularUrl = `${API_BASE_URL}/api/download/${result.task_id}?version=modular`;
                    await downloadFile(modularUrl, 'beatsync_modular.mp4', 'modular', downloadModularBtn);
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
                                await downloadFile(v2Url, v2Filename, 'v2', downloadV2Btn);
                    } else {
                        console.warn('V2版本状态已变更，无法下载');
                        updateStatus('V2版本不可用', 'error');
                    }
                } else {
                    // 降级方案：使用当前result的值
                    if (result.v2_output) {
                        const v2Url = `${API_BASE_URL}/api/download/${result.task_id}?version=v2`;
                        const v2Filename = `v2_${result.task_id}.mp4`;
                                await downloadFile(v2Url, v2Filename, 'v2', downloadV2Btn);
                    }
                }
            } catch (error) {
                console.error('获取最新状态时出错:', error);
                // 降级方案：使用当前result的值
                if (result.v2_output) {
                    const v2Url = `${API_BASE_URL}/api/download/${result.task_id}?version=v2`;
                            await downloadFile(v2Url, 'beatsync_v2.mp4', 'v2', downloadV2Btn);
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
    
    // 更新重置按钮显示状态
    updateResetButtonVisibility();
}

// 下载单个文件（优化：立即响应，不等待）
async function downloadFile(url, filename, version = null, button = null) {
    requestWakeLock('download');
    try {
        // 设置下载标志（防止轮询覆盖状态）
        isDownloading = true;
        downloadingVersion = version;
        setButtonLoading(button, '下载中...');
        if (statusSkeleton) statusSkeleton.style.display = 'flex';
        showProgress(0, '准备下载...');
        
        // 检测是否为 Capacitor 原生 App 环境
        console.log('🔍 下载函数开始执行');
        const isNative = typeof window.Capacitor !== 'undefined' && window.Capacitor.isNativePlatform;
        if (isCapacitorNative || isNative) {
            return await downloadFileNativeApp(url, filename, version);
        }
        
        // 检测是否为移动设备和PWA环境（网页端/PWA端逻辑）
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        const isPWA = window.matchMedia('(display-mode: standalone)').matches || 
                     window.navigator.standalone || 
                     document.referrer.includes('android-app://');
        
        // 根据版本显示状态，并保存到全局变量
        // 注意：如果pollTaskStatus正在运行，它会统一显示状态，这里只更新变量
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            downloadingStatusMessage = `正在下载${versionName}结果...`;
        } else {
            downloadingStatusMessage = '正在下载...';
        }
        // 如果pollTaskStatus正在运行，它会统一显示状态
        // 否则直接更新状态（处理已完成的情况）
        if (!isPolling) {
            updateStatus(downloadingStatusMessage, 'processing');
        }
        showProgress(0, '准备下载...');
        
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
        
        // PWA环境：使用blob方式（确保在PWA中能正确下载）
        if (isPWA) {
            console.log('PWA环境，使用blob方式强制下载');
            return await downloadFileWithBlob(url, filename, version);
        }
        
        // 非PWA环境（包括移动浏览器和桌面浏览器）：使用直接下载方式（立即响应）
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            downloadingStatusMessage = `正在下载${versionName}结果...`;
        } else {
            downloadingStatusMessage = '正在开始下载...';
        }
        // 如果pollTaskStatus正在运行，它会统一显示状态
        // 否则直接更新状态（处理已完成的情况）
        if (!isPolling) {
            updateStatus(downloadingStatusMessage, 'processing');
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
        // 如果pollTaskStatus正在运行，不更新状态（让它统一显示）
        // 否则更新状态（处理已完成的情况）
        if (!isPolling) {
            if (version) {
                const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                updateStatus(`${versionName}下载已开始`, 'success');
            } else {
                updateStatus('下载已开始', 'success');
            }
        }
        showProgress(100, '下载已开始');
        return true;
    } catch (error) {
        console.error(`下载 ${filename} 失败:`, error);
        updateStatus(`下载失败: ${error.message}`, 'error');
        return false;
    } finally {
        // 重置下载标志（无论成功或失败）
        isDownloading = false;
        downloadingVersion = null;
        downloadingStatusMessage = null;
        clearButtonLoading(button);
        releaseWakeLock('download');
        updateResetButtonVisibility();
        setTimeout(() => hideProgress(), 600);
    }
}

// Capacitor 原生 App 下载并保存到相册
async function downloadFileNativeApp(url, filename, version = null) {
    try {
        const { Filesystem } = window.Capacitor.Plugins;
        const { Share } = window.Capacitor.Plugins;
        
        if (!Filesystem) {
            throw new Error('Capacitor Filesystem 插件未加载，请确保已安装 @capacitor/filesystem');
        }
        
        // Directory 枚举值（使用字符串常量）
        const DirectoryEnum = {
            Documents: 'DOCUMENTS',
            Cache: 'CACHE',
            Data: 'DATA',
            External: 'EXTERNAL',
            ExternalStorage: 'EXTERNAL_STORAGE'
        };
        
        // 根据版本显示状态
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            downloadingStatusMessage = `正在下载${versionName}结果...`;
                } else {
            downloadingStatusMessage = '正在下载...';
        }
        if (!isPolling) {
            updateStatus(downloadingStatusMessage, 'processing');
        }
        showProgress(0, '准备下载...');
        
        // 1. 下载视频文件
        console.log('📥 开始下载视频:', url);
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`下载失败: ${response.statusText}`);
        }
        
        // 获取文件大小用于显示进度
        const contentLength = response.headers.get('Content-Length');
        const total = contentLength ? parseInt(contentLength, 10) : 0;
        
        // 使用 ReadableStream 读取数据
        const reader = response.body.getReader();
        downloadReader = reader; // 保存reader引用，用于检测中断
        const chunks = [];
        let received = 0;
        
        // 保存下载上下文，用于恢复
        currentDownloadContext = {
            url: url,
            filename: filename,
            version: version,
            total: total,
            received: 0,
            retryCount: 0
        };
        
        while (true) {
            let readResult;
            try {
                readResult = await reader.read();
            } catch (readError) {
                // 如果读取失败（可能是app切到后台导致ReadableStream断开）
                console.error('❌ ReadableStream读取失败:', readError);
                // 检查是否是网络错误或流断开
                if (readError.name === 'NetworkError' || readError.message?.includes('network') || 
                    readError.message?.includes('aborted') || readError.message?.includes('canceled')) {
                    // 尝试重新开始下载
                    console.log('🔄 检测到下载中断，尝试重新开始下载...');
                    reader.cancel().catch(() => {});
                    downloadReader = null;
                    // 重新开始下载（递归调用，但限制重试次数）
                    if (!currentDownloadContext.retryCount) {
                        currentDownloadContext.retryCount = 0;
                    }
                    if (currentDownloadContext.retryCount < 2) {
                        currentDownloadContext.retryCount++;
                        updateStatus('下载中断，正在重新开始...', 'info');
                        // 等待1秒后重新开始
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        return await downloadFileNativeApp(url, filename, version);
                    } else {
                        throw new Error('下载中断，已重试多次仍失败，请重新下载');
                    }
                }
                throw readError;
            }
            
            const { done, value } = readResult;
            if (done) break;
            
            // 检查是否已重置（下载被取消）
            if (!isDownloading) {
                console.log('ℹ️ 下载已被重置，停止下载');
                reader.cancel();
                throw new Error('下载已取消');
            }
            
            chunks.push(value);
            received += value.length;
            
            // 更新已接收的字节数到上下文
            if (currentDownloadContext) {
                currentDownloadContext.received = received;
            }
            
            // 更新进度（更频繁地更新，每5%更新一次）
            if (total > 0) {
                const percent = Math.round((received / total) * 100);
                // 每5%更新一次，或者达到100%时更新
                if (percent % 5 === 0 || percent >= 100) {
                    // 再次检查是否已重置
                    if (!isDownloading) {
                        console.log('ℹ️ 下载已被重置，停止更新进度');
                        reader.cancel();
                        throw new Error('下载已取消');
                    }
                    showProgress(percent, `${percent}%`);
                    if (version) {
                        const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                        downloadingStatusMessage = `正在下载${versionName}结果... ${percent}%`;
                    } else {
                        downloadingStatusMessage = `正在下载... ${percent}%`;
                    }
                    // 立即更新状态显示（只有在未重置时）
                    if (!isPolling && isDownloading && downloadingStatusMessage) {
                        updateStatus(downloadingStatusMessage, 'processing');
                    }
                }
            }
        }
        
        // 合并所有 chunks
        const blob = new Blob(chunks, { type: 'video/mp4' });
        console.log('✅ 视频下载完成，大小:', formatFileSize(blob.size));
        
        // 清除下载上下文和reader引用（下载成功）
        currentDownloadContext = null;
        downloadReader = null;
        
        // 2. 保存到文件系统（Documents 目录，用户可访问）
        const tempFileName = `beatsync_${Date.now()}_${filename}`;
        const filePath = `beatsync/${tempFileName}`;
        
        // 将 blob 转换为 base64（使用安全的方法，避免调用栈溢出）
        const arrayBuffer = await blob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        // 分块处理，避免调用栈溢出
        const chunkSize = 8192; // 8KB chunks
        let base64Data = '';
        for (let i = 0; i < uint8Array.length; i += chunkSize) {
            const chunk = uint8Array.slice(i, i + chunkSize);
            base64Data += String.fromCharCode.apply(null, chunk);
        }
        base64Data = btoa(base64Data);
        
        console.log('💾 保存到文件系统:', filePath);
        await Filesystem.writeFile({
            path: filePath,
            data: base64Data,
            directory: DirectoryEnum.Documents,
            recursive: true
        });
        
        // 3. 获取文件 URI（用于备用方案）
        const fileUri = await Filesystem.getUri({
            path: filePath,
            directory: DirectoryEnum.Documents
        });
        
        console.log('📁 文件 URI:', fileUri.uri);
        
        // 4. 使用分享方案（Share / Web Share）
        try {
            const Capacitor = window.Capacitor;
            if (Capacitor && Capacitor.Plugins && Capacitor.Plugins.Share) {
                console.log('📤 使用 Capacitor Share 插件（打开分享菜单）');
                const shareResult = await Capacitor.Plugins.Share.share({
                    title: filename,
                    url: fileUri.uri,
                    dialogTitle: '请选择"保存到相册"'
                });
                console.log('✅ Share 插件调用成功:', shareResult);
                const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                updateStatus(version ? `${versionName}请从分享菜单选择"保存到相册"` : '请从分享菜单选择"保存到相册"', 'info');
                showProgress(100, '下载完成');
                return true;
            }
        } catch (shareError) {
            console.warn('⚠️ Share 插件调用失败:', shareError);
        }

        // 备用：Web Share API（同样是分享菜单）
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        if (isIOS && navigator.share && navigator.canShare) {
            const file = new File([blob], filename, { type: 'video/mp4' });
            if (navigator.canShare({ files: [file] })) {
                console.log('📤 使用 Web Share API（打开分享菜单）');
                await navigator.share({ files: [file], title: filename });
                const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                updateStatus(version ? `${versionName}请从分享菜单选择"保存到相册"` : '请从分享菜单选择"保存到相册"', 'info');
                showProgress(100, '下载完成');
                return true;
            }
        }

        // 最终兜底：提示已保存到文件
        const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
        updateStatus(version ? `${versionName}已保存到文件，可在文件应用中查看` : '视频已保存到文件，可在文件应用中查看', 'success');
        showProgress(100, '下载完成');
        return true;
        
    } catch (error) {
        // 清除下载上下文和reader引用
        currentDownloadContext = null;
        downloadReader = null;
        
        // 如果下载被重置（取消），不显示错误信息
        if (error.message === '下载已取消' || !isDownloading) {
            console.log('ℹ️ 下载已取消');
            return;
        }
        console.error('❌ 原生 App 下载失败:', error);
        // 只有在未重置时才更新错误状态
        if (isDownloading) {
            updateStatus(`下载失败: ${error.message}`, 'error');
        }
        throw error;
    } finally {
        // 只有在未重置时才执行清理
        if (isDownloading) {
            setTimeout(() => hideProgress(), 600);
        } else {
            hideProgress();
        }
        // 如果下载完成或失败，清除上下文
        if (!isDownloading) {
            currentDownloadContext = null;
            downloadReader = null;
        }
        releaseWakeLock('download');
        updateResetButtonVisibility();
    }
}

// 使用blob方式下载（辅助函数）
async function downloadFileWithBlob(url, filename, version = null) {
    try {
        // 根据版本显示状态，并保存到全局变量
        // 注意：如果pollTaskStatus正在运行，它会统一显示状态，这里只更新变量
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            downloadingStatusMessage = `正在下载${versionName}结果...`;
        } else {
            downloadingStatusMessage = '正在下载...';
        }
        // 如果pollTaskStatus正在运行，它会统一显示状态
        // 否则直接更新状态（处理已完成的情况）
        // 只有在未重置时才更新状态
        if (!isPolling && isDownloading && downloadingStatusMessage) {
            updateStatus(downloadingStatusMessage, 'processing');
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
        downloadReader = reader; // 保存reader引用
        const chunks = [];
        let received = 0;
        
        // 保存下载上下文
        currentDownloadContext = {
            url: url,
            filename: filename,
            version: version,
            total: total,
            received: 0,
            retryCount: 0
        };
        
        while (true) {
            let readResult;
            try {
                readResult = await reader.read();
            } catch (readError) {
                // 如果读取失败（可能是app切到后台导致ReadableStream断开）
                console.error('❌ ReadableStream读取失败:', readError);
                if (readError.name === 'NetworkError' || readError.message?.includes('network') || 
                    readError.message?.includes('aborted') || readError.message?.includes('canceled')) {
                    console.log('🔄 检测到下载中断，尝试重新开始下载...');
                    reader.cancel().catch(() => {});
                    downloadReader = null;
                    if (!currentDownloadContext.retryCount) {
                        currentDownloadContext.retryCount = 0;
                    }
                    if (currentDownloadContext.retryCount < 2) {
                        currentDownloadContext.retryCount++;
                        updateStatus('下载中断，正在重新开始...', 'info');
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        return await downloadFileWithBlob(url, filename, version);
                    } else {
                        throw new Error('下载中断，已重试多次仍失败，请重新下载');
                    }
                }
                throw readError;
            }
            
            const { done, value } = readResult;
            if (done) break;
            
            // 检查是否已重置（下载被取消）
            if (!isDownloading) {
                console.log('ℹ️ 下载已被重置，停止下载');
                reader.cancel();
                throw new Error('下载已取消');
            }
            
            chunks.push(value);
            received += value.length;
            
            // 更新已接收的字节数
            if (currentDownloadContext) {
                currentDownloadContext.received = received;
            }
            
            // 更新进度（更频繁地更新，每5%更新一次）
            if (total > 0) {
                const percent = Math.round((received / total) * 100);
                // 每5%更新一次，或者达到100%时更新
                if (percent % 5 === 0 || percent >= 100) {
                    // 再次检查是否已重置
                    if (!isDownloading) {
                        console.log('ℹ️ 下载已被重置，停止更新进度');
                        reader.cancel();
                        throw new Error('下载已取消');
                    }
                    showProgress(percent, `${percent}%`);
                    if (version) {
                        const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
                        downloadingStatusMessage = `正在下载${versionName}结果... ${percent}%`;
                    } else {
                        downloadingStatusMessage = `正在下载... ${percent}%`;
                    }
                    // 立即更新状态显示（只有在未重置时）
                    if (!isPolling && isDownloading && downloadingStatusMessage) {
                        updateStatus(downloadingStatusMessage, 'processing');
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
        
        // 清除下载上下文和reader引用
        currentDownloadContext = null;
        downloadReader = null;
        
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`${versionName}下载已开始`, 'success');
        } else {
            updateStatus('下载已开始', 'success');
        }
        showProgress(100, '下载完成');
        return true;
    } catch (error) {
        // 清除下载上下文和reader引用
        currentDownloadContext = null;
        downloadReader = null;
        
        console.error('Blob下载失败:', error);
        throw error;
    } finally {
        if (!isDownloading) {
            currentDownloadContext = null;
            downloadReader = null;
        }
        setTimeout(() => hideProgress(), 600);
    }
}

// 下载结果（自动下载所有可用版本）

// 绑定事件
processBtn.addEventListener('click', processVideo);
// 下载按钮的事件在updateDownloadButton中动态绑定

