# -*- coding: utf-8 -*-
"""音轨垫片 + 混音交付：把配音/原声音轨对齐到视频并封装最终成片。

用法:
  python mix_audio.py --video out/clip_v5.mp4 --audio vo_pad.wav --out final.mp4
  python mix_audio.py --video clip.mp4 --audio vo.wav --out final.mp4 --pad-before 3.0 --pad-after 2.4 --loudnorm
说明:
  - 视频 typically 来自 Remotion 渲染（无声），音频是独立音轨（原声截段/配音）。
  - pad-before/after 在音轨前后补静音，用于对齐片头钩子/片尾卡。
  - 视频流直接 copy 不重编码；音频 aac 192k；-shortest 防止音画超长。
"""
import argparse, glob, os, shutil, subprocess

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

def pad_audio(src, dst, before, after):
    """音轨前后补静音：silence -> audio -> silence，输出 wav。"""
    af = f"aevalsrc=0:d={before}[p0];[0:a]apad=pad_dur={after}[p1];[p0][0:a][p1]concat=n=3:v=0:a=1"
    cmd = [FF, "-y", "-i", src, "-filter_complex", af, "-ar", "48000", "-ac", "2", dst]
    subprocess.run(cmd, check=True, capture_output=True)

def mix(video, audio, out, loudnorm=False):
    filters = "loudnorm=I=-16:TP=-1.5:LRA=11" if loudnorm else None
    cmd = [FF, "-y", "-i", video, "-i", audio,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart"]
    if filters:
        cmd[cmd.index("-c:a"):cmd.index("-c:a")] = ["-af", filters]
    cmd.append(out)
    r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(1)
    print(f"OK -> {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pad-before", type=float, default=0.0)
    ap.add_argument("--pad-after", type=float, default=0.0)
    ap.add_argument("--loudnorm", action="store_true")
    ap.add_argument("--ffmpeg", help="手动指定 ffmpeg 路径")
    args = ap.parse_args()

    FF = args.ffmpeg or get_ffmpeg()

    aud = args.audio
    if args.pad_before > 0 or args.pad_after > 0:
        import os, tempfile
        tmp = os.path.join(tempfile.gettempdir(), "clip_pad.wav")
        pad_audio(args.audio, tmp, args.pad_before, args.pad_after)
        aud = tmp
    mix(args.video, aud, args.out, args.loudnorm)
