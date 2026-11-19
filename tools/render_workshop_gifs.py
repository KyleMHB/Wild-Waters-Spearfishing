"""Cut the Workshop description GIFs from filmed promo footage.

Usage:
  python tools/render_workshop_gifs.py           # every GIF into docs/images/workshop/

Footage comes from `python tools/spear_test.py promo` (work/promo/footage/<shot>/clip.mp4, 1920x1080, camera on the diver),
filmed on generated natural coasts, never the square test ponds. Each GIF is a short window around one of the shot's marks,
cropped round the diver at normal game speed.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOTAGE = ROOT / "work" / "promo" / "footage"
OUT = ROOT / "docs" / "images" / "workshop"
HARNESS = Path(os.environ.get("RIMWORLD_DEV_TESTS_ROOT", str(ROOT.parent / "RimWorldDevTests")))

# name: (shot, mark, seconds before, seconds after, crop width, crop height, crop centre x, crop centre y)
GIFS = {
    "spearfishing-dive": ("diver", "swim-facedown", 0.5, 5.0, 640, 360, 940, 570),
    "spearfishing-shoal": ("freshwater", "river-catch", 3.6, 1.4, 960, 540, 960, 540),
    "spearfishing-kelp": ("kelp", "kelp", 0.0, 5.0, 1280, 720, 1100, 400),
}
WIDTH, FPS = 560, 12


def ffmpeg():
    for candidate in [shutil.which("ffmpeg"), ROOT / "work/ffmpeg/ffmpeg.exe", HARNESS / "work/ffmpeg/ffmpeg.exe"]:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    sys.exit("ffmpeg not found (PATH, work/ffmpeg or the shared harness's work/ffmpeg)")


def render(name, shot, mark, before, after, w, h, cx, cy):
    clip = FOOTAGE / shot / "clip.mp4"
    if not clip.is_file():
        print(f"{name}: no footage for shot {shot}; skipped")
        return
    marks = json.loads((FOOTAGE / shot / "shot.json").read_text(encoding="utf-8"))["marks"]
    start = max(0.0, marks[mark] - before)
    crop = f"crop={w}:{h}:{cx - w // 2}:{cy - h // 2},fps={FPS},scale={WIDTH}:-1:flags=lanczos"
    graph = f"[0:v]{crop},split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle"
    out = OUT / (name + ".gif")
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{before + after:.2f}", "-i", str(clip),
                    "-filter_complex", graph, "-loop", "0", str(out)], check=True)
    print(f"Wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for gif, args in GIFS.items():
        if len(sys.argv) == 1 or gif in sys.argv[1:]:
            render(gif, *args)
