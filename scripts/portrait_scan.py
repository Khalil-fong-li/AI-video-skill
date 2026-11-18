# -*- coding: utf-8 -*-
"""人像在位扫描：肤色质心/占比检测，验证人像缺口、补丁、借入段是否全程在位。

用法:
  python portrait_scan.py --src video.mp4 --from 42 --to 58 --step 0.5
  python portrait_scan.py --src video.mp4 --full            # 全片粗扫（每2秒）
  python portrait_scan.py --src video.mp4 --from 44 --to 56 --win 115,52,52,41 --res 320x180
窗口坐标为缩放后帧内像素（--res 对应的分辨率），不指定则按 720p 人像区比例换算。
输出: 人像缺失区间列表（低于阈值即视为缺失）。
"""
import argparse, glob, json, os, re, shutil, subprocess

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

def skin_fraction(raw, W, H, win):
    import numpy as np
    a = np.frombuffer(raw, dtype=np.uint8)
    if a.size < W * H * 3:
        return -1.0
    img = a[:W*H*3].reshape(H, W, 3).astype(int)
    R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    skin = (R > 110) & (G > 55) & (B > 35) & (R - G > 15) & (R - B > 22) & (R < 250)
    x, y, w, h = win
    return float(skin[y:y+h, x:x+w].mean())

def scan(src, t0, t1, step, res="320x180", win=None):
    W, H = (int(v) for v in res.split("x"))
    if win is None:
        # 320x180 下人像区默认窗口（720p 全屏讲课时主讲人位置，可 --win 覆盖）
        win = (115, 52, 52, 41)
    missing, ok_vals = [], []
    t = t0
    while t <= t1 + 1e-6:
        r = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", src,
                            "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", res, "-"], capture_output=True)
        frac = skin_fraction(r.stdout, W, H, win)
        if frac < 0:
            missing.append({"t": round(t, 2), "frac": None, "note": "no-frame"})
        else:
            ok_vals.append(frac)
            if frac < 0.02:
                missing.append({"t": round(t, 2), "frac": round(frac, 4)})
        t += step
    return {"missing": missing, "min_frac": round(min(ok_vals), 4) if ok_vals else None,
            "checked": len(ok_vals) + len(missing)}

def group_intervals(missing):
    """把离散缺失点合并成区间，便于阅读。"""
    if not missing:
        return []
    ts = [m["t"] for m in missing if m["frac"] is not None or m.get("note") == "no-frame"]
    out, start, prev = [], ts[0], ts[0]
    for t in ts[1:]:
        if t - prev > 0.75:
            out.append([start, prev]); start = t
        prev = t
    out.append([start, prev])
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, required=True)
    ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--res", default="320x180")
    ap.add_argument("--win", help="x,y,w,h in downscaled frame")
    ap.add_argument("--ffmpeg", help="手动指定 ffmpeg 路径")
    ap.add_argument("--full", action="store_true", help="全片粗扫（step=2s，到视频末尾）")
    args = ap.parse_args()

    FF = args.ffmpeg or get_ffmpeg()

    if args.full:
        r = subprocess.run([FF, "-i", args.src], capture_output=True, text=True, errors="ignore")
        info = r.stderr
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", info)
        args.t1 = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)) if m else args.t1
        args.step = 2.0
    win = tuple(int(v) for v in args.win.split(",")) if args.win else None
    result = scan(args.src, args.t0, args.t1, args.step, args.res, win)
    result["missing_intervals"] = group_intervals(result["missing"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
