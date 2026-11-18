# AI-video-skill

讲座 / 录屏 / 课程长视频精剪切片技能。从长视频中剪出 1–3 分钟的高吸引力切片，覆盖切点帧级确认、画面修复、Remotion 精剪、混音交付与机器验证的完整工作流。

> 这是一个 WorkBuddy / Agent Skill 包，核心入口是 `SKILL.md`，动手前必读 `references/methodology.md`（含 10 条真实踩坑记录）。

## 目录结构

```
video-clip-cut/
├── SKILL.md                       # 技能入口：五步工作流
├── references/methodology.md      # 方法论详解 + 10 条坑清单
├── scripts/
│   ├── analyze_source.py          # 流信息 / 帧差跳变 / 静音检测
│   ├── portrait_scan.py           # 人像在位扫描（修复段验证）
│   └── mix_audio.py               # 音轨垫片 + 混音封装
├── assets/remotion-template/      # Remotion 4.0.538 工程模板
└── install.sh / install.bat       # 安装脚本
```

## 五步工作流（摘要）

1. **素材体检与内容规划**：`analyze_source.py` 取流信息，ASR 转写全片，按"钩子→主体→片尾卡"规划叙事。
2. **切点帧级确认**：所有切点用帧差/静音/人像扫描逐帧确认，禁止秒级估算；低清源按规范预处理。
3. **Remotion 精剪工程**：复制模板，`npm i`，在 `src/core.ts` 填 SEGMENTS（帧号来自第 2 步）。
4. **渲染与混音**：Edge/Chrome 渲染（crf12/h264），解码校验后用 `mix_audio.py` 混音。
5. **验证与交付**：解码零错误 + 人像全程在位 + 三处音画对齐抽查；不产生备份副本。

## 安装

Windows：双击 `install.bat`；macOS / Linux：`bash install.sh`（把本目录安装到 `~/.workbuddy/skills/`）。

## 许可

自用与学习交流，随意。
