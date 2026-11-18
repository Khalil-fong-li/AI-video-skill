# -*- coding: utf-8 -*-
"""素材体检：流信息、镜头跳变帧差扫描、静音/停顿检测。

用法:
  python analyze_source.py --src video.mp4
  python analyze_source.py --src video.mp4 --jumps 100 200      # 只扫 100-200s 的跳变
  python analyze_source.py --src video.mp4 --silence            # 静音/停顿检测
输出 JSON 报告到 stdout。
"""
import argparse, glob, json, os, re, shutil, subprocess, sys

def get_ffmpeg():
    """依次尝试：imageio_ffmpeg 包 → 常见 Python 站点包路径 → PATH。"""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    for pat in [
        os.path.expanduser(r"~/AppData/Local/Programs/Python/Python*/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-*.exe"),
        "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg",
    ]:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise SystemExit("找不到 ffmpeg：请 pip install imageio-ffmpeg，或用 --ffmpeg 指定路径")

FF = get_ffmpeg()

def probe(src):
    """用 ffmpeg -i 输出解析流信息（imageio_ffmpeg 不带 ffprobe）。"""
    r = subprocess.run([FF, "-i", src], capture_output=True, text=True, errors="ignore")
    out = r.stderr
    info = {}
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out)
    if m:
        info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    streams = []
    for sm in re.finditer(r"Stream #\d+:(\d+)[^\n]*", out):
        line = sm.group(0)
        if "Video:" in line:
            tail = line.split("Video:", 1)[1]  # 只在 Video: 之后的参数区找分辨率，避免被 [0x1] 干扰
            res = re.search(r"(\d{2,5})x(\d{2,5})", tail)
            fps = re.search(r"([\d.]+) fps", tail)
            streams.append({"type": "video", "index": int(sm.group(1)),
                            "width": int(res.group(1)) if res else None,
                            "height": int(res.group(2)) if res else None,
                            "fps": float(fps.group(1)) if fps else None})
        elif "Audio:" in line:
            streams.append({"type": "audio", "index": int(sm.group(1))})
    info["streams"] = streams
    return info

def scan_jumps(src, start, end, thresh=40.0):
    """逐帧差扫描定位镜头跳变/画面切换（切点定位精度=1帧）。

    解码 160x90 缩略帧流，计算相邻帧平均绝对差；diff > thresh 视为跳变。
    返回跳变时刻列表（秒）。用于确认切点是否干净、找分屏/镜头切换。
    """
    W, H = 160, 90
    cmd = [FF, "-v", "error", "-ss", str(start), "-to", str(end), "-i", src,
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-"]
    r = subprocess.run(cmd, capture_output=True)
    raw = r.stdout
    n = len(raw) // (W * H * 3)
    if n < 2:
        return []
    frames = [raw[i*W*H*3:(i+1)*W*H*3] for i in range(n)]
    import numpy as np
    jumps = []
    prev = np.frombuffer(frames[0], dtype=np.uint8).astype(int)
    for i in range(1, n):
        cur = np.frombuffer(frames[i], dtype=np.uint8).astype(int)
        diff = float(np.abs(cur - prev).mean())
        if diff > thresh:
            jumps.append(round(start + i, 3))  # 跳变发生在第 i 帧处
        prev = cur
    return jumps

def detect_silence(src, start=None, noise="-34dB", d="0.8"):
    """silencedetect 找停顿/说话空档。返回 [(开始秒, 结束秒, 时长)]。"""
    cmd = [FF, "-i", src, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"]
    if start is not None:
        cmd = [FF, "-ss", str(start), "-i", src, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    out = r.stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", out)]
    res = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        res.append({"start": s, "end": e, "dur": round(e - s, 2) if e else None})
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--jumps", nargs=2, type=float, metavar=("FROM", "TO"), help="帧差扫描区间(秒)")
    ap.add_argument("--jump-thresh", type=float, default=40.0)
    ap.add_argument("--silence", action="store_true", help="检测静音/停顿")
    ap.add_argument("--noise", default="-34dB")
    ap.add_argument("--ffmpeg", help="手动指定 ffmpeg 路径")
    args = ap.parse_args()

    FF = args.ffmpeg or get_ffmpeg()

    report = {"src": args.src, "info": probe(args.src)}
    if args.jumps:
        report["jumps"] = scan_jumps(args.src, args.jumps[0], args.jumps[1], args.jump_thresh)
    if args.silence:
        report["silences"] = detect_silence(args.src, noise=args.noise)
    print(json.dumps(report, ensure_ascii=False, indent=2))
