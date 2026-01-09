# 修复 Swift Package Manager 依赖问题

## 问题

Xcode 报错：
- "Missing package product 'Capacitor'"
- "Missing package product 'Cordova'"
- "Missing package product 'IONFilesystemLib'"
- "There is no XCFramework found"

## 修复步骤

### 步骤 1：在 Xcode 中重置包缓存

1. 在 Xcode 中，菜单：`File` → `Packages` → `Reset Package Caches`
2. 等待重置完成

### 步骤 2：重新解析依赖

1. 在 Xcode 中，菜单：`File` → `Packages` → `Resolve Package Versions`
2. 等待解析完成（可能需要几分钟）

### 步骤 3：检查 node_modules

确认 Capacitor 插件已安装：

```bash
# 在项目根目录
ls -la node_modules/@capacitor/camera
ls -la node_modules/@capacitor/filesystem
ls -la node_modules/@capacitor/share
```

如果不存在，安装依赖：

```bash
npm install
```

### 步骤 4：重新同步 Capacitor

```bash
# 重新同步到 iOS
npx cap sync ios
```

### 步骤 5：清理并重新构建

在 Xcode 中：
1. `Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 关闭 Xcode
3. 重新打开：`npx cap open ios`
4. 重新构建

---

## 一键修复命令

```bash
# 1. 检查并安装 npm 依赖
npm install

# 2. 重新同步 Capacitor
npx cap sync ios

# 3. 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 4. 打开 Xcode
npx cap open ios
```

然后在 Xcode 中：
1. `File` → `Packages` → `Reset Package Caches`
2. `File` → `Packages` → `Resolve Package Versions`
3. 等待完成后，`Product` → `Clean Build Folder`
4. 重新构建

---

**请先执行一键修复命令，然后在 Xcode 中重置包缓存和重新解析依赖！** 🔧

# 修复 Swift Package Manager 依赖问题

## 问题

Xcode 报错：
- "Missing package product 'Capacitor'"
- "Missing package product 'Cordova'"
- "Missing package product 'IONFilesystemLib'"
- "There is no XCFramework found"

## 修复步骤

### 步骤 1：在 Xcode 中重置包缓存

1. 在 Xcode 中，菜单：`File` → `Packages` → `Reset Package Caches`
2. 等待重置完成

### 步骤 2：重新解析依赖

1. 在 Xcode 中，菜单：`File` → `Packages` → `Resolve Package Versions`
2. 等待解析完成（可能需要几分钟）

### 步骤 3：检查 node_modules

确认 Capacitor 插件已安装：

```bash
# 在项目根目录
ls -la node_modules/@capacitor/camera
ls -la node_modules/@capacitor/filesystem
ls -la node_modules/@capacitor/share
```

如果不存在，安装依赖：

```bash
npm install
```

### 步骤 4：重新同步 Capacitor

```bash
# 重新同步到 iOS
npx cap sync ios
```

### 步骤 5：清理并重新构建

在 Xcode 中：
1. `Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 关闭 Xcode
3. 重新打开：`npx cap open ios`
4. 重新构建

---

## 一键修复命令

```bash
# 1. 检查并安装 npm 依赖
npm install

# 2. 重新同步 Capacitor
npx cap sync ios

# 3. 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 4. 打开 Xcode
npx cap open ios
```

然后在 Xcode 中：
1. `File` → `Packages` → `Reset Package Caches`
2. `File` → `Packages` → `Resolve Package Versions`
3. 等待完成后，`Product` → `Clean Build Folder`
4. 重新构建

---

**请先执行一键修复命令，然后在 Xcode 中重置包缓存和重新解析依赖！** 🔧

# 修复 Swift Package Manager 依赖问题

## 问题

Xcode 报错：
- "Missing package product 'Capacitor'"
- "Missing package product 'Cordova'"
- "Missing package product 'IONFilesystemLib'"
- "There is no XCFramework found"

## 修复步骤

### 步骤 1：在 Xcode 中重置包缓存

1. 在 Xcode 中，菜单：`File` → `Packages` → `Reset Package Caches`
2. 等待重置完成

### 步骤 2：重新解析依赖

1. 在 Xcode 中，菜单：`File` → `Packages` → `Resolve Package Versions`
2. 等待解析完成（可能需要几分钟）

### 步骤 3：检查 node_modules

确认 Capacitor 插件已安装：

```bash
# 在项目根目录
ls -la node_modules/@capacitor/camera
ls -la node_modules/@capacitor/filesystem
ls -la node_modules/@capacitor/share
```

如果不存在，安装依赖：

```bash
npm install
```

### 步骤 4：重新同步 Capacitor

```bash
# 重新同步到 iOS
npx cap sync ios
```

### 步骤 5：清理并重新构建

在 Xcode 中：
1. `Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 关闭 Xcode
3. 重新打开：`npx cap open ios`
4. 重新构建

---

## 一键修复命令

```bash
# 1. 检查并安装 npm 依赖
npm install

# 2. 重新同步 Capacitor
npx cap sync ios

# 3. 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 4. 打开 Xcode
npx cap open ios
```

然后在 Xcode 中：
1. `File` → `Packages` → `Reset Package Caches`
2. `File` → `Packages` → `Resolve Package Versions`
3. 等待完成后，`Product` → `Clean Build Folder`
4. 重新构建

---

**请先执行一键修复命令，然后在 Xcode 中重置包缓存和重新解析依赖！** 🔧












