import Foundation
import Capacitor
import Photos

@objc(SaveToGalleryPlugin)
public class SaveToGalleryPlugin: CAPPlugin {
    
    public override func getId() -> String {
        return "SaveToGallery"
    }
    
    @objc func saveVideo(_ call: CAPPluginCall) {
        guard let filePath = call.getString("filePath") else {
            call.reject("filePath 参数缺失")
            return
        }
        
        // 将 filePath 转换为 URL
        let fileURL: URL
        if filePath.hasPrefix("file://") {
            guard let url = URL(string: filePath) else {
                call.reject("无效的文件路径")
                return
            }
            fileURL = url
        } else if filePath.hasPrefix("/") {
            fileURL = URL(fileURLWithPath: filePath)
        } else {
            let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            fileURL = documents.appendingPathComponent(filePath)
        }
        
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            call.reject("文件不存在: \(fileURL.path)")
            return
        }
        
        let status = PHPhotoLibrary.authorizationStatus(for: .addOnly)
        switch status {
        case .authorized, .limited:
            save(url: fileURL, call: call)
        case .notDetermined:
            PHPhotoLibrary.requestAuthorization(for: .addOnly) { newStatus in
                DispatchQueue.main.async {
                    if newStatus == .authorized || newStatus == .limited {
                        self.save(url: fileURL, call: call)
                    } else {
                        call.reject("用户拒绝了相册写入权限")
                    }
                }
            }
        default:
            call.reject("相册写入权限被拒绝，请在系统设置中允许访问相册")
        }
    }
    
    private func save(url: URL, call: CAPPluginCall) {
        PHPhotoLibrary.shared().performChanges({
            PHAssetChangeRequest.creationRequestForAssetFromVideo(atFileURL: url)
        }) { success, error in
            DispatchQueue.main.async {
                if success {
                    call.resolve([
                        "success": true,
                        "message": "视频已保存到相册"
                    ])
                } else {
                    call.reject("保存失败: \(error?.localizedDescription ?? "未知错误")")
                }
            }
        }
    }
}

