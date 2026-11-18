// 字幕表：from/to 为成片帧号，text 中 [括号] 内容渲染为红色关键词。
// 字幕稿来自 ASR 转写（whisper/讯飞等）+ 人工压缩，每条 ≤ 22 字。
// ⚠️ ASR 相对秒数坑见 references/methodology.md 坑 1：转写偏移要用能量模式匹配校正后换算帧号。
export type Sub = { from: number; to: number; text: string };

export const SUBS: Sub[] = [
  { from: 90, to: 180, text: "[客户]凭什么审核我们的工厂？" },
  { from: 180, to: 270, text: "答案是一部国际标准：[SA8000]" },
  { from: 270, to: 360, text: "它管的是童工、工时、[安全和薪酬]" },
  // ... 按转写稿逐条补齐
];
