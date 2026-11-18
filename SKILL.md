---
name: video-clip-cut
description: 讲座/录屏/课程长视频精剪切片技能。当用户要求从长视频剪出 1–3 分钟切片、精剪成片、加片头钩子/片尾卡/字幕/进度条、提升画质、修复人像缺失或画面瑕疵、混音交付时使用。基于 Remotion 帧级剪辑 + ffmpeg 分析验证的五步工作流。触发词：剪切片、切片、精剪、剪辑视频、剪个一两分钟、剪得吸引人、video clip、cut。
agent_created: true
---

# 讲座/录屏视频精剪切片

本技能把长讲座/录屏视频剪成 1–3 分钟的高吸引力切片，核心原则：**切点帧级确认、画面修复用连续真实画面、交付前机器验证**。

## 何时使用

- "从这段讲座里剪个一两分钟的切片"
- "剪得有吸引力一点"、"加片头片尾"、"加字幕"
- "画质调高一点"、"按照这个画质剪"
- "中间人像没了/画面违和，能不能修复"
- 需要混音、对齐音轨、覆盖交付成片

## 五步工作流

完整方法论（含真实踩过的 10 条坑）在 `references/methodology.md`，动手前必读。

### 第 1 步：素材体检与内容规划
1. `python scripts/analyze_source.py --src <素材>` 获取时长/分辨率/帧率。
2. ASR 转写全片（注意相对秒数 offset 校正，见方法论坑 1）。
3. 按转写稿规划叙事：片头钩子（痛点一句话）→ 主体选段 → 片尾卡。

### 第 2 步：切点帧级确认 + 素材预处理
1. 所有切点用帧级扫描确认，**禁止秒级估算**：
   - 镜头跳变：`analyze_source.py --jumps FROM TO`
   - 停顿：`analyze_source.py --silence`
   - 人像在位边界：`portrait_scan.py --from X --to Y --step 0.25`，边界处再逐帧扫描。
2. 源画质差且有高清源时：裁切 → lanczos 下采样 → unsharp 0.3 → crf10–12 中间素材
   （宽高必须偶数；不拿高清源重处理时才考虑放大低清源）。

### 第 3 步：Remotion 精剪工程
1. 复制 `assets/remotion-template/` 为工作工程，`npm i`，素材放 `public/`。
2. 在 `src/core.ts` 填 SEGMENTS（切点帧号来自第 2 步）；相邻段硬切对齐、不重叠、接缝 fadeIn 3 帧。
3. 缺口/瑕疵段修复优先级：**整段借入连续真实画面 > 画中画补丁 > 静帧定格**（详见方法论）。
4. 视觉规范：Noto Sans SC 700/800/900 黑体（禁宋体）、字幕 30px 关键词红、页边注释只放空白区不挡讲解区、底部进度条。

### 第 4 步：渲染与混音
1. 渲染（Windows 无 Chrome 用 Edge）：
   ```
   npx remotion render Clip out/clip_vX.mp4 --browser-executable="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --gl=angle --concurrency=6 --crf=12 --codec=h264
   ```
   长渲染放后台；完成后先解码校验（`ffmpeg -v error -i out/xxx.mp4 -f null -` 输出为空才算无损）。
2. 混音交付：`python scripts/mix_audio.py --video out/clip_vX.mp4 --audio vo.wav --out 成片.mp4 --pad-before 3.0 --pad-after 2.4`
   （视频 copy、aac 192k、-shortest、+faststart；loudnorm 可选。）

### 第 5 步：验证与交付
1. 用户要求"确认没问题"才结束，验证三件套：
   - 全片解码零错误；
   - 修复段 `portrait_scan.py` 每 0.5 秒抽帧确认人像/画面全程在位；
   - 片头、接缝、片尾三处抽查音画对齐。
2. 覆盖桌面固定文件名交付（如 `主题-90秒.mp4`），**不产生备份副本**。

## 资源清单

| 资源 | 用途 |
|---|---|
| `scripts/analyze_source.py` | 流信息、帧差跳变扫描、静音检测 |
| `scripts/portrait_scan.py` | 人像在位扫描（缺口/补丁/借入段验证） |
| `scripts/mix_audio.py` | 音轨垫片 + 混音封装交付 |
| `assets/remotion-template/` | Remotion 4.0.538 工程模板（Hook/EndCard/Subs/Progress/借入段） |
| `references/methodology.md` | 五步工作流详解 + 10 条坑清单（动手前必读） |

## 交付底线

- 切点帧级确认过；修复段机器验证过；解码零错误；音画对齐抽查过。
- 用户偏好：不产生备份副本、输出 720p（用户明确要求更高时可调）、成片覆盖桌面同名文件。
