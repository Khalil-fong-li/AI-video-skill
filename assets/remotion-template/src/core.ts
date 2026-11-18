// 全部常量与切点集中在这里。切点必须来自帧级扫描（analyze_source.py --jumps / portrait_scan.py），
// 不允许凭秒级估算填数字。
export const W = 1280;
export const H = 720;
export const FPS = 30;

export type Seg = {
  file: string;       // public/ 下的素材路径，如 "hq1.mp4"
  from: number;       // 在主体时间轴中的起始帧
  dur: number;        // 帧数
  startFrom?: number; // 从素材文件的第几帧开始播（借入段用）
  fadeIn?: number;    // 接缝淡入帧数（建议 3）
};

// 主体段数组：按时间轴顺序排列。相邻段硬切对齐（from + dur == 下一段 from），
// 不要让 Sequence 重叠——重叠会在交接帧提前截断画面（见 references/methodology.md 坑 4）。
export const SEGMENTS: Seg[] = [
  { file: "hq1.mp4", from: 0, dur: 1200 },
  // 借入段示例：素材 B 从 8000 帧借 351 帧顶替缺口
  { file: "hq2.mp4", from: 1200, dur: 351, startFrom: 8000, fadeIn: 3 },
  { file: "hq2.mp4", from: 1551, dur: 400, startFrom: 298, fadeIn: 3 },
  { file: "hq3.mp4", from: 1951, dur: 600 },
];

// 片头钩子：一句话 + 红色副题，抓前 3 秒
export const HOOK = { dur: 90, title: "从客户验厂到日常经营", sub: "90 秒看懂 SA8000" };

// 片尾卡
export const END = { dur: 75, title: "关注我，看懂更多体系认证", sub: "" };
