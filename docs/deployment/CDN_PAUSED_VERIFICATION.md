# CDN 暂停后验证指南

## 概述

本文档提供 CDN 暂停后的验证步骤，确保服务正常运行。

## 快速验证清单

### ✅ 1. 检查响应头（确认CDN已关闭）

在服务器上执行：

```bash
# 如果遇到SSL证书验证错误，使用 -k 参数跳过验证
curl -I -k https://beatsync.site/
# 或者
curl -I https://beatsync.site/ --insecure
```

**预期结果（停用后）**：
- ❌ 不应该有 `X-Cache-Lookup` 响应头
- ❌ 不应该有 `X-NWS-LOG-UUID` 响应头
- ✅ 应该看到 `Server: nginx/1.18.0 (Ubuntu)`（源站响应）

**停用前示例**：
```
HTTP/2 200
Server: nginx/1.18.0 (Ubuntu)
X-Cache-Lookup: Cache Hit
X-NWS-LOG-UUID: 13069004270188260204
...
```

**停用后示例**：
```
HTTP/2 200
Server: nginx/1.18.0 (Ubuntu)
...
```

**⚠️ CDN 仍在运行的标志**：
```
HTTP/2 418 (或其他非200状态码)
Server: Lego Server
X-NWS-LOG-UUID: ...
X-Cache-Lookup: Return Directly
```
如果看到这些响应头，说明 CDN 仍在运行，需要等待更长时间或检查 CDN 控制台状态。

### ✅ 2. 验证网站功能

访问 https://beatsync.site/ 并测试：

- [ ] 网站首页正常加载
- [ ] 文件上传功能正常
- [ ] 视频处理功能正常
- [ ] 视频下载功能正常
- [ ] 响应速度可接受

### ✅ 3. 验证App端访问

在iOS App中测试：

- [ ] App可以正常连接后端API
- [ ] 上传文件功能正常
- [ ] 视频处理功能正常
- [ ] 视频下载功能正常
- [ ] 下载速度是否符合预期（相对于CDN启用时）

### ✅ 4. 检查DNS解析（可选）

```bash
nslookup beatsync.site
# 或
dig beatsync.site
```

**说明**：
- DNS可能仍然指向CDN的CNAME记录，这是**正常的**
- CDN停用后会自动将请求转发到源站服务器
- 如果看到CDN相关的DNS记录，不需要手动修改

### ✅ 5. 监控服务器负载（建议）

关闭CDN后，所有流量直接访问源站，建议监控：

- 服务器带宽使用情况
- CPU和内存使用率
- 如果有监控工具，观察是否有异常流量

## 常见问题

### Q: DNS仍然指向CDN，是否需要修改？

**A**: 不需要。停用CDN后，CDN节点会自动将请求转发到源站。DNS继续使用CDN的CNAME记录是正常且推荐的配置，这样重新启用CDN时无需修改DNS。

### Q: 停用后访问变慢怎么办？

**A**: 
1. 这是正常的，因为不再有CDN加速
2. 如果速度明显异常，检查：
   - 服务器带宽是否充足
   - Nginx配置是否正常
   - 服务器负载是否过高

### Q: 如何重新启用CDN？

**A**: 
1. 登录腾讯云CDN控制台
2. 在域名管理页面找到 `beatsync.site`
3. 点击"启用"按钮
4. 等待5-10分钟生效

### Q: 停用后还需要注意什么？

**A**:
1. 监控服务器带宽使用（可能增加）
2. 监控服务器负载（所有请求直接访问源站）
3. 如果发现异常流量，及时排查

## 验证命令汇总

```bash
# 1. 检查响应头（确认CDN已关闭）
curl -I https://beatsync.site/

# 2. 检查DNS解析（可选）
nslookup beatsync.site
dig beatsync.site

# 3. 测试API端点
curl https://beatsync.site/api/health

# 4. 检查服务器资源（如果在服务器上）
htop  # 或 top
df -h  # 检查磁盘
```

## 下一步

验证完成后，可以：
1. 更新文档状态（已停用CDN）
2. 监控一段时间服务器性能
3. 如果下载速度仍然不理想，考虑其他优化方案

---

**最后更新**：2025-12-20






