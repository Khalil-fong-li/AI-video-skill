// 切片主模板：片头钩子 -> 主体素材段（可含借入段） -> 片尾卡，叠加字幕/侧栏/进度条。
// 常量集中在 core.ts；切点全部用帧号（由 analyze_source.py / 帧级扫描得出，不要用秒级估算）。
import React from "react";
import { AbsoluteFill, Sequence, Video, useCurrentFrame, interpolate, Easing } from "remotion";
import { W, H, FPS, SEGMENTS, HOOK, END } from "./core";
import { SUBS } from "./subs";

// ---------- 单个素材段（支持 startFrom 借入 / 首尾淡入） ----------
export const VideoPage: React.FC<{ file: string; startFrom?: number; fadeIn?: number }> = ({
  file, startFrom = 0, fadeIn = 0,
}) => {
  const frame = useCurrentFrame();
  const opacity = fadeIn > 0
    ? interpolate(frame, [0, fadeIn], [0, 1], { extrapolateRight: "clamp" })
    : 1;
  return (
    <AbsoluteFill style={{ opacity }}>
      <Video src={staticFileSafe(file)} startFrom={startFrom} />
    </AbsoluteFill>
  );
};
const staticFileSafe = (f: string) => `${window.remotion_staticBase}/${f}`;

// ---------- 片头钩子 ----------
export const Hook: React.FC<{ title: string; sub?: string }> = ({ title, sub }) => {
  const f = useCurrentFrame();
  const y = interpolate(f, [0, 12], [40, 0], { easing: Easing.out(Easing.cubic), extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#0f1117", justifyContent: "center", alignItems: "center" }}>
      <div style={{ transform: `translateY(${y}px)`, textAlign: "center" }}>
        <div style={{ fontSize: 64, fontWeight: 900, color: "#fff", fontFamily: FONT }}>{title}</div>
        {sub && <div style={{ fontSize: 28, fontWeight: 700, color: "#e5484d", marginTop: 16, fontFamily: FONT }}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

// ---------- 片尾卡 ----------
export const EndCard: React.FC<{ title: string; sub?: string }> = ({ title, sub }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10], [0, 1], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#0f1117", justifyContent: "center", alignItems: "center", opacity: o }}>
      <div style={{ fontSize: 56, fontWeight: 900, color: "#fff", fontFamily: FONT }}>{title}</div>
      {sub && <div style={{ fontSize: 24, fontWeight: 700, color: "#9aa0ac", marginTop: 18, fontFamily: FONT }}>{sub}</div>}
    </AbsoluteFill>
  );
};

// ---------- 字幕（黑体，关键词红） ----------
export const Subs: React.FC = () => {
  const f = useCurrentFrame();
  const cur = SUBS.find((s) => f >= s.from && f < s.to);
  if (!cur) return null;
  // 关键词用 [红字] 标记，渲染时拆分
  const parts = cur.text.split(/(\[[^\]]+\])/g).filter(Boolean);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 46 }}>
      <div style={{
        background: "rgba(10,12,16,0.55)", borderRadius: 8, padding: "8px 18px",
        fontSize: 30, fontWeight: 800, color: "#fff", fontFamily: FONT,
      }}>
        {parts.map((p, i) =>
          p.startsWith("[") ? (
            <span key={i} style={{ color: "#ff5a52" }}>{p.slice(1, -1)}</span>
          ) : (
            <span key={i}>{p}</span>
          ),
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------- 底部进度条 ----------
export const Progress: React.FC<{ total: number }> = ({ total }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div style={{ width: `${(f / total) * 100}%`, height: 6, background: "#e5484d" }} />
    </AbsoluteFill>
  );
};

const FONT = '"Noto Sans SC", "Microsoft YaHei", sans-serif';

// ---------- 主合成：SEGMENTS 描述主体结构，见 core.ts ----------
export const Clip: React.FC = () => {
  const total = HOOK.dur + SEGMENTS.reduce((a, s) => Math.max(a, s.from + s.dur), 0) + END.dur;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Sequence from={0} durationInFrames={HOOK.dur}>
        <Hook title={HOOK.title} sub={HOOK.sub} />
      </Sequence>
      {SEGMENTS.map((s, i) => (
        <Sequence key={i} from={HOOK.dur + s.from} durationInFrames={s.dur}>
          <VideoPage file={s.file} startFrom={s.startFrom} fadeIn={s.fadeIn ?? 3} />
        </Sequence>
      ))}
      <Sequence from={total - END.dur} durationInFrames={END.dur}>
        <EndCard title={END.title} sub={END.sub} />
      </Sequence>
      <Subs />
      <Progress total={total} />
    </AbsoluteFill>
  );
};

export { W, H, FPS };
