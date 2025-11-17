# BeatSync 项目当前进展总结

## 一、核心处理程序

### 1. **beatsync_fine_cut_modular.py** - Modular版本处理程序
- **功能**：使用多策略融合对齐算法进行视频音频同步
- **对齐算法**：多策略融合算法（MFCC、Chroma、Spectral Contrast、Spectral Rolloff）
- **处理方式**：检测并裁剪前面的无声段落
- **音频配置**：✅ **已修改为双声道** (`-ac 2`)
- **输出**：只输出最终视频，已删除中间文件 `_module1_aligned.mp4`

### 2. **beatsync_badcase_fix_trim_v2.py** - V2版本处理程序
- **功能**：使用简化滑动窗口对齐算法进行视频音频同步
- **对齐算法**：简化滑动窗口算法（基于节拍检测）
- **处理方式**：裁剪未重叠部分
- **音频配置**：双声道 (`-ac 2`)
- **特点**：处理速度较快，适合特定badcase类型

### 3. **beatsync_parallel_processor.py** - 并行处理器 ⭐ **当前推荐使用**
- **功能**：同时使用modular版本和V2版本处理样本，生成两个输出视频供用户选择
- **输出文件**：
  - `{sample_name}_modular.mp4` - modular版本输出
  - `{sample_name}_v2.mp4` - V2版本输出
- **优势**：绕过badcase分类的复杂性，让用户直接选择最佳结果
- **状态**：✅ 已完全实现

## 二、主控程序（历史版本）

### 4. **beatsync_main_controller_corrected_v3.py** - 主控程序V3
- **功能**：根据badcase类型自动选择处理版本
- **分类逻辑**：
  - `T2 > T1` → `SHORTERBEGIN` → 调用V2版本
  - `bgm=0s` → `BGM_ZERO` → 调用modular版本
  - 其他 → `NORMAL` → 调用modular版本
- **对齐算法**：V2简化滑动窗口算法（仅用于badcase类型检测）
- **状态**：已实现，但存在分类准确性问题

### 5. **beatsync_main_controller_v2_algorithm.py** - 程序A
- **功能**：使用V2对齐算法进行badcase检测
- **对齐算法**：V2简化滑动窗口算法
- **状态**：测试用程序

### 6. **beatsync_main_controller_multistrategy_algorithm.py** - 程序B
- **功能**：使用多策略融合对齐算法进行badcase检测
- **对齐算法**：多策略融合算法
- **状态**：测试用程序，已修复二维搜索问题

## 三、辅助程序

### 7. **beatsync_badcase_fix.py** - Badcase修复程序（填充版本）
- **功能**：使用填充黑色帧的方式处理badcase
- **状态**：历史版本，已不再使用

### 8. **batch_parallel_processor.py** - 批量并行处理脚本
- **功能**：批量处理所有测试样本，使用并行处理器
- **状态**：✅ 已实现

## 四、当前技术状态

### 对齐算法对比
1. **V2简化滑动窗口算法**（`beatsync_badcase_fix_trim_v2.py`）
   - 优点：处理速度快
   - 缺点：对齐精度相对较低，可能找到局部最优解
   - 适用场景：第二类badcase（T2 > T1）

2. **多策略融合算法**（`beatsync_fine_cut_modular.py`）
   - 优点：对齐精度高，综合多种特征
   - 缺点：处理时间较长
   - 适用场景：第一类badcase、正常case、bgm=0s情况

### Badcase分类
- **T1_GT_T2**：第一类badcase（dance视频开始时间 > bgm视频开始时间）
- **T2_GT_T1**：第二类badcase（bgm视频开始时间 > dance视频开始时间，即SHORTERBEGIN）
- **BGM_ZERO**：bgm从0秒开始的情况
- **NORMAL**：正常情况

### 音频处理统一
- ✅ **已完成**：将modular版本的音频从单声道改为双声道
- **修改位置**：`beatsync_fine_cut_modular.py` 中的 `extract_audio_optimized` 函数
- **修改内容**：`-ac 1` → `-ac 2`
- **目的**：统一两个版本的音频输出，解决V2版本音量更大更亮的问题

## 五、测试样本

### 测试文件夹
- `input_allcases_lowp/` - 所有测试样本（低分辨率版本）
- `input_false/` - 特定badcase样本
- `newcases/` - 新增测试样本

### 已知问题样本
- `killitgirl_full` - 在某些情况下对齐点错误
- `nobody` - 对齐点错误（与`nobody_shorterbegin`使用相同bgm但结果不同）
- `sweetjuice_full` - 曾被误分类为SHORTERBEGIN
- `likethat_full` - 曾被误分类为SHORTERBEGIN

## 六、接下来的TODO

### 高优先级
1. ✅ **验证双声道修改效果**
   - 使用 `beatsync_parallel_processor.py` 处理测试样本
   - 对比modular版本和V2版本的音频输出
   - 确认两个版本的音量、音质是否一致

2. **批量处理所有测试样本**
   - 使用修改后的并行处理器处理所有测试样本
   - 生成对比报告，记录每个样本的两个版本输出
   - 等待用户人工检验并选择最佳版本

### 中优先级
3. **优化并行处理性能**
   - 考虑使用 `beatsync_parallel_processor_optimized.py`（如果存在）
   - 优化内存使用，避免处理大文件时内存溢出

4. **完善错误处理**
   - 添加更详细的错误日志
   - 处理文件不存在、格式不支持等异常情况

### 低优先级
5. **主控程序优化**（如果继续使用）
   - 改进badcase分类算法，提高分类准确率
   - 考虑使用更复杂的特征来判断badcase类型

6. **文档完善**
   - 更新使用说明
   - 记录已知问题和解决方案

## 七、推荐工作流程

### 当前推荐流程
1. 使用 `beatsync_parallel_processor.py` 处理单个样本
2. 或使用 `batch_parallel_processor.py` 批量处理所有样本
3. 人工检验两个版本的输出视频
4. 选择最佳版本作为最终结果

### 优势
- 绕过复杂的badcase分类问题
- 用户可以直接对比选择最佳结果
- 两个版本使用统一的音频配置（双声道）

---

**最后更新**：2024年（当前会话）
**当前状态**：✅ 并行处理方案已实现，音频配置已统一为双声道，等待验证效果


## 八、fallingout 对照结论（用户复检）

- 本次对照（22k / 容器小写 / 粗到细快速版）三种路径的程序输出对齐点一致，但经用户人工核验均为错误对齐，判定该方向优化“无效”，予以放弃。
- 结论与建议：
  - 放弃针对 fallingout 的上述三项对照优化思路；
  - 暂不继续在 V2 裁剪流（`beatsync_badcase_fix_trim_v2*.py`）上做该类微调；
  - 对 fallingout 等类似样本，优先使用并行处理方案（`beatsync_parallel_processor.py`）并倾向选择 modular 结果，或单独迭代 modular 算法的多特征权重/搜索策略。
  - 如需继续深入，应转向特征层策略（如节拍/Chroma权重、窗口与步长自适应、候选峰簇一致性校验）而非采样率/容器名等外层因素。



