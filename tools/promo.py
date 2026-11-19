"""Films and edits the Spearfishing promo video (ticket 31). Developer-only; everything it writes goes to work/promo/.

    python tools/spear_test.py promo                    film every shot in one RimWorld launch, then edit
    python tools/spear_test.py promo --shot gear        refilm one shot, then edit with the other shots' saved footage
    python tools/spear_test.py promo --edit-only        edit again from saved footage, without launching the game
    python tools/spear_test.py promo --music FILE       use another music file (--no-music drops it)

Filming runs the DevTests batch spearfishing-promo (or spearfishing-promo-<shot>) with --record. The batch writes shots.json
(each shot's start, end and marks on the game's clock) and sounds.jsonl (every one-shot sound played, because the capture has
no audio) beside build.mp4. Shots are filmed and edited at normal game speed: each one is a few short real-time moments around
its marks, joined by cuts, never sped up. Each shot is cut into work/promo/footage/<shot>/ with its marks and sounds, so one shot can be
refilmed alone. The edit builds a sound-effect track from the logged clips and a separate music track, and mixes them only
in the final file. Clips, music and the font come from the game's Assets.zip and stay in work/promo/assets/; never commit them.
"""
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HARNESS = Path(os.environ.get("RIMWORLD_DEV_TESTS_ROOT", str(ROOT.parent / "RimWorldDevTests")))
PROMO = ROOT / "work" / "promo"
FOOTAGE = PROMO / "footage"
ASSETS = PROMO / "assets"
BUILD = PROMO / "build"
GAME = Path(os.environ.get("RIMWORLD_DIR", "E:/Steam/steamapps/common/RimWorld"))
ASSETS_ZIP = GAME / "Assets.zip"
FONT = "Resources/Fonts/Arial_medium.ttf"
DEFAULT_MUSIC = "Resources/Sounds/Songs/Relax/These_Lands.mp3"

SHOTS = ["diver", "thinning", "freshwater", "snorkeler", "gear"]
W, H, FPS = 1920, 1080, 30
BACKGROUND = "0x1d1f22"

# Captions follow writing-copy.md: short and plain.
CAPTIONS = {
    "diver": "Divers wade out, spear fish and swim home.",
    "thinning": "Every catch thins the fish stock.",
    "freshwater": "Lakes and rivers hold fish too.",
    "snorkeler": "Colonists snorkel for recreation.",
    "gear": "Masks, snorkels, fins and spears help them dive.",
}
TITLE = ["Spearfishing", "An add-on for RimWorld: Waves"]
# The mod has no Workshop ID yet; replace this line when it is published (ticket 31 Comments).
WORKSHOP = "Workshop link: to be added on release"
CLOSING = ["Spearfishing", "Requires Waves", WORKSHOP]

# Each shot's moments as (mark, seconds before it, seconds after it), played at 1x and joined by cuts. A moment with a fourth
# item, an end mark, runs unbroken from before its mark to after the end mark (at most MAX_TAKE seconds). The long cut puts a
# caption card before each shot; the short clip lays the caption over the shot instead.
MOMENTS = {
    "long": {
        # One unbroken take from the beach to the first dive, so the diver is seen wading in and swimming out face down.
        "diver": [("wade", 1.0, 0.8, "submerged"), ("catch", 2.0, 1.5), ("ashore", 1.7, 0.5)],
        "thinning": [("stock-70", 0.3, 1.7), ("stock-45", 0.3, 1.7), ("stock-10", 0.3, 2.2)],
        "freshwater": [("lake-catch", 2.5, 1.0), ("river-catch", 2.5, 1.0)],
        "snorkeler": [("snorkel", 0.5, 5.5)],
        "gear": [("pose", 0.0, 2.5), ("go", 0.0, 3.0)],
    },
    "short": {
        "diver": [("catch", 1.8, 1.0)],
        "thinning": [("stock-45", 0.2, 0.8), ("stock-10", 0.2, 1.0)],
        # The river, where the shadow and fish show clearly; on the deep lake the depth fade makes them faint.
        "freshwater": [("river-catch", 1.6, 0.8)],
        "snorkeler": [("snorkel", 0.3, 1.9)],
        "gear": [("go", 0.5, 1.7)],
    },
}
# When a mark is missing from the footage, the first of these that is present stands in for it.
FALLBACK = {
    "catch": ["submerged", "wade"], "ashore": ["home"], "wade": [],
    "lake-catch": ["lake-submerged", "lake", "river-catch", "river"], "river-catch": ["river-submerged", "river"],
    "snorkel": ["freedive"],
}
# Long enough for the wade and the 6 to 10 second swim out before the first dive.
MAX_TAKE = 20.0
LONG_CARD, LONG_TITLE, LONG_CLOSE = 2.2, 3.0, 4.5
SHORT_TITLE, SHORT_CLOSE = 1.6, 2.4


def ffmpeg_paths():
    for candidate in [shutil.which("ffmpeg"), ROOT / "work/ffmpeg/ffmpeg.exe", HARNESS / "work/ffmpeg/ffmpeg.exe"]:
        if candidate and Path(candidate).is_file():
            exe = Path(candidate)
            probe = exe.with_name("ffprobe" + exe.suffix)
            if probe.is_file():
                return str(exe), str(probe)
    sys.exit("ffmpeg with ffprobe not found (PATH, work/ffmpeg or the shared harness's work/ffmpeg)")


FFMPEG, FFPROBE = ffmpeg_paths()


def run(args, cwd=PROMO):
    result = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("ffmpeg failed: " + " ".join(map(str, args))[:600] + "\n" + result.stderr[-3000:])


def duration(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def rel(path):
    return Path(os.path.relpath(path, PROMO)).as_posix()


# ---- Filming ------------------------------------------------------------------------------------------------------------

def film(shot, seed, timeout):
    batch = "spearfishing-promo" + ("-" + shot if shot else "")
    # The promo mod set adds Odyssey (lakes) and Living Waters to the default set, for the freshwater shot.
    command = [sys.executable, str(ROOT / "tools" / "spear_test.py"), "run", batch, "--seed", str(seed), "--mods", "promo", "--record",
               "--timeout", str(timeout)]
    print("Filming:", " ".join(command[1:]), flush=True)
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    run_dir = None
    for line in process.stdout:
        print(line, end="", flush=True)
        match = re.match(r"Run \S+: evidence (.+)$", line.strip())
        if match:
            run_dir = Path(match.group(1))
    code = process.wait()
    if run_dir is None:
        sys.exit("the launcher printed no run folder")
    needed = [run_dir / n for n in ("build.mp4", "recording.json", "shots.json", "sounds.jsonl")]
    missing = [p.name for p in needed if not p.is_file()]
    if missing:
        sys.exit(f"filming did not produce {', '.join(missing)} in {run_dir} (exit {code})")
    if code != 0:
        print(f"Warning: the run exited {code}; cutting whatever shots it filmed. See {run_dir / 'summary.txt'}.")
    cut(run_dir)


def cut(run_dir):
    """Cuts each filmed shot out of build.mp4 into footage/<shot>/, with its marks and sounds relative to the clip's start."""
    origin = json.loads((run_dir / "recording.json").read_text(encoding="utf-8"))["videoOriginMonotonicSeconds"]
    shots = json.loads((run_dir / "shots.json").read_text(encoding="utf-8"))["shots"]
    sounds = [json.loads(line) for line in (run_dir / "sounds.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    video = run_dir / "build.mp4"
    length = duration(video)
    for shot in shots:
        if not shot["ok"]:
            print(f"Shot {shot['name']} was not filmed; keeping its earlier footage if any.")
            continue
        start, end = shot["start"] - origin, min(shot["end"] - origin, length - 2.0)
        if end - start < 1.0:
            print(f"Shot {shot['name']} lies outside the recording ({start:.1f}-{end:.1f} s of {length:.1f} s); skipped.")
            continue
        out = FOOTAGE / shot["name"]
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        # The capture is scaled to 1080p here; the edit drops it to 30 fps.
        run(["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(video), "-an", "-vf", f"scale={W}:{H}:flags=lanczos,format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", str(out / "clip.mp4")])
        marks = {k: round(v - shot["start"], 3) for k, v in shot["marks"].items()}
        clip_sounds = [dict(s, t=round(s["t"] - shot["start"], 4)) for s in sounds if shot["start"] <= s["t"] <= shot["end"]]
        meta = {"name": shot["name"], "length": round(end - start, 3), "marks": marks, "source": str(run_dir)}
        (out / "shot.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        (out / "sounds.json").write_text(json.dumps(clip_sounds, indent=1), encoding="utf-8")
        print(f"Cut {shot['name']}: {meta['length']:.1f} s, {len(clip_sounds)} sounds, marks {', '.join(marks)}")


# ---- Assets -------------------------------------------------------------------------------------------------------------

def read_entry(archive, name):
    """Reads one Assets.zip entry. RimWorld 1.6+ stores many entries as zstd, which Python's zipfile reads only from 3.14,
    so those go through Windows' bsdtar (libarchive with zstd) instead."""
    try:
        return archive.read(name)
    except NotImplementedError:
        tar = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "tar.exe"
        return subprocess.run([str(tar), "-xOf", archive.filename, name], check=True, capture_output=True).stdout


def mod_sound_paths():
    """Each of the mod's SoundDefs as its grains: a clip grain is one file, a folder grain is every file in the folder.
    The game gives its loaded clips no names, so the log records the def and the edit plays these files in turn."""
    paths = {}
    for xml in sorted((ROOT / "Defs" / "SoundDefs").glob("*.xml")):
        for sound in ET.parse(xml).getroot().iter("SoundDef"):
            grains = [("clip", g.text) for g in sound.iter("clipPath")] + [("folder", g.text) for g in sound.iter("clipFolderPath")]
            paths[sound.findtext("defName")] = grains
    return paths


def extract_assets(music):
    """Takes the font, the mod's sound clips and the default music out of the game's Assets.zip, into work/promo/assets/.
    Returns each of the mod's SoundDefs with its clip files in a fixed order. Other mods' and vanilla sounds (alerts, animal
    calls) are left out of the promo."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    wanted = {FONT: ASSETS / Path(FONT).name}
    if music == "default":
        wanted[DEFAULT_MUSIC] = ASSETS / Path(DEFAULT_MUSIC).name
    variants = {}
    with zipfile.ZipFile(ASSETS_ZIP) as archive:
        names = sorted(n for n in archive.namelist() if n.startswith("Resources/Sounds/") and not n.endswith("/"))
        for def_name, grains in mod_sound_paths().items():
            files = []
            for kind, path in grains:
                prefix = "Resources/Sounds/" + path
                files += [n for n in names
                          if (Path(n).with_suffix("").as_posix() if kind == "clip" else Path(n).parent.as_posix()) == prefix]
            if not files:
                print(f"No game file for {def_name}, left silent")
                continue
            variants[def_name] = []
            for name in files:
                target = ASSETS / name.removeprefix("Resources/Sounds/").replace("/", "_")
                wanted[name] = target
                variants[def_name].append(target)
        for name, target in wanted.items():
            if not target.is_file():
                target.write_bytes(read_entry(archive, name))
    return variants


# ---- Edit ---------------------------------------------------------------------------------------------------------------

def text_file(name, text):
    path = BUILD / "text" / (name + ".txt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel(path)


def drawtext(name, text, size, y, alpha="1"):
    font = rel(ASSETS / Path(FONT).name)
    return (f"drawtext=fontfile={font}:textfile={text_file(name, text)}:fontsize={size}:fontcolor=white:alpha='{alpha}'"
            f":x=(w-text_w)/2:y={y}:shadowcolor=black@0.6:shadowx=2:shadowy=2")


def fades(length, fade=0.35):
    return f"fade=t=in:st=0:d={fade},fade=t=out:st={length - fade:.3f}:d={fade}"


def card(out, lines, length, name):
    """A plain card in RimWorld's font: the first line large, the rest smaller beneath it."""
    sizes = [96] + [44] * (len(lines) - 1)
    block = sum(sizes) + 30 * (len(lines) - 1)
    y = (H - block) // 2
    filters = []
    for i, (line, size) in enumerate(zip(lines, sizes)):
        filters.append(drawtext(f"{name}-{i}", line, size, y))
        y += size + 30
    run(["-f", "lavfi", "-i", f"color=c={BACKGROUND}:s={W}x{H}:r={FPS}:d={length}", "-vf", ",".join(filters + [fades(length)]),
         "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", rel(out)])


def caption_card(out, text, length, name):
    run(["-f", "lavfi", "-i", f"color=c={BACKGROUND}:s={W}x{H}:r={FPS}:d={length}",
         "-vf", ",".join([drawtext(name, text, 56, "(h-text_h)/2"), fades(length)]),
         "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", rel(out)])


def windows(shot, moments):
    """The shot's source windows as (start, length): each moment around its mark (or a fallback mark), clamped to the clip and
    kept from overlapping the one before. A shot with none of its marks gets one window from the middle of the clip."""
    meta = json.loads((FOOTAGE / shot / "shot.json").read_text(encoding="utf-8"))
    length, marks = meta["length"], meta["marks"]
    result, used = [], set()
    for mark, before, after, *until in moments:
        name = next((m for m in [mark] + FALLBACK.get(mark, []) if m in marks and m not in used), None)
        if name is None:
            print(f"{shot}: no {mark} mark; moment left out")
            continue
        used.add(name)
        span = min(before + after, length)
        if until and until[0] in marks and marks[until[0]] > marks[name]:
            span = min(marks[until[0]] - marks[name] + before + after, MAX_TAKE, length)
        elif until:
            print(f"{shot}: no {until[0]} mark after {name}; moment kept short")
        start = min(max(0.0, marks[name] - before), length - span)
        if result and start < result[-1][0] + result[-1][1]:
            start = result[-1][0] + result[-1][1]
        if start + 0.5 <= length:
            result.append((start, min(span, length - start)))
    if not result:
        span = min(sum(m[1] + m[2] for m in moments), length)
        result.append(((length - span) / 2, span))
    return result


def shot_segment(out, shot, parts, caption=None):
    """Joins the shot's windows at normal speed with plain cuts."""
    graph = [f"[0:v]trim=start={start:.3f}:duration={span:.3f},setpts=PTS-STARTPTS[p{i}]" for i, (start, span) in enumerate(parts)]
    length = sum(span for _, span in parts)
    filters = [f"concat=n={len(parts)}:v=1:a=0", f"fps={FPS}"]
    if caption:
        filters.append("drawbox=x=0:y=ih-150:w=iw:h=150:color=black@0.45:t=fill")
        filters.append(drawtext("short-" + shot, caption, 48, "h-75-text_h/2"))
    filters.append(fades(length, 0.25))
    graph.append("".join(f"[p{i}]" for i in range(len(parts))) + ",".join(filters) + "[v]")
    run(["-i", rel(FOOTAGE / shot / "clip.mp4"), "-an", "-filter_complex", ";".join(graph), "-map", "[v]", "-t", f"{length:.3f}",
         "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), rel(out)])
    return length


def sfx_events(shot, parts, at):
    """The shot's logged on-screen sounds inside its windows, at their real times in the edit. Sounds between windows are
    dropped."""
    sounds = json.loads((FOOTAGE / shot / "sounds.json").read_text(encoding="utf-8"))
    events, offset = [], at
    for start, span in parts:
        for s in sorted(sounds, key=lambda s: s["t"]):
            if s.get("onScreen", True) and start <= s["t"] < start + span:
                events.append({"t": offset + s["t"] - start, "def": s["def"], "volume": s["volume"], "pitch": s.get("pitch", 1.0)})
        offset += span
    return events


def sfx_track(out, events, total, variants):
    # Each def plays its clip files in turn, standing in for the game's random pick.
    turn = {}
    for e in events:
        files = variants.get(e["def"])
        if files:
            e["clip"] = files[turn.get(e["def"], 0) % len(files)]
            turn[e["def"]] = turn.get(e["def"], 0) + 1
    events = [e for e in events if e.get("clip")]
    clips = {e["clip"]: e["clip"] for e in events}
    if not events:
        run(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{total:.3f}", rel(out)])
        return 0
    # One input per distinct clip, split for each use, delayed to its time and mixed without normalising.
    used = sorted({e["clip"] for e in events})
    args, parts, labels = [], [], []
    for i, clip in enumerate(used):
        args += ["-i", rel(clips[clip])]
        uses = [e for e in events if e["clip"] == clip]
        split = "".join(f"[c{i}u{j}]" for j in range(len(uses)))
        parts.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit={len(uses)}{split}" if len(uses) > 1
                     else f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo[c{i}u0]")
        for j, e in enumerate(uses):
            ms = int(e["t"] * 1000)
            parts.append(f"[c{i}u{j}]asetrate={48000 * e['pitch']:.0f},aresample=48000,"
                         f"volume={min(max(e['volume'], 0.05), 1.5):.3f},adelay={ms}|{ms}[e{i}_{j}]")
            labels.append(f"[e{i}_{j}]")
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,alimiter=limit=0.9,apad[sfx]")
    script = BUILD / (out.stem + "-filter.txt")
    script.write_text(";\n".join(parts), encoding="utf-8")
    # The output's -t ends the endless apad; an atrim inside the graph once failed to stop it and the wav ran to 265 GB.
    run(args + ["-/filter_complex", rel(script), "-map", "[sfx]", "-ar", "48000", "-t", f"{total:.3f}", rel(out)])
    return len(events)


def music_track(out, music, total):
    run(["-i", str(Path(music).resolve()), "-vn",
         "-af", f"aformat=sample_rates=48000:channel_layouts=stereo,atrim=duration={total:.3f},apad,atrim=duration={total:.3f},"
                f"afade=t=in:d=1.0,afade=t=out:st={max(0.0, total - 3.0):.3f}:d=3.0",
         "-ar", "48000", "-t", f"{total:.3f}", rel(out)])


def assemble(cut_name, segments, events, total, clips, music):
    listing = BUILD / f"{cut_name}-segments.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in segments), encoding="utf-8")
    video = BUILD / f"{cut_name}-video.mp4"
    run(["-f", "concat", "-safe", "0", "-i", rel(listing), "-c", "copy", rel(video)])
    sfx = BUILD / f"{cut_name}-sfx.wav"
    count = sfx_track(sfx, events, total, clips)
    inputs = ["-i", rel(video), "-i", rel(sfx)]
    if music:
        track = BUILD / f"{cut_name}-music.wav"
        music_track(track, music, total)
        inputs += ["-i", rel(track)]
        mix = "[1:a]volume=1.0[s];[2:a]volume=0.32[m];[s][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"
    else:
        mix = "[1:a]alimiter=limit=0.95[a]"
    out = PROMO / f"promo-{cut_name}.mp4"
    run(inputs + ["-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                  "-movflags", "+faststart", "-t", f"{total:.3f}", rel(out)])
    print(f"{out}: {duration(out):.1f} s, {count} sound effects, music {'on' if music else 'off'}")
    return out


def edit(music):
    missing = [s for s in SHOTS if not (FOOTAGE / s / "clip.mp4").is_file()]
    if missing:
        sys.exit("no footage for " + ", ".join(missing) + "; film them with promo or promo --shot <name>")
    clips = extract_assets(music)
    if music == "default":
        music = ASSETS / Path(DEFAULT_MUSIC).name
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    outputs = []
    for cut_name in ("long", "short"):
        long_cut = cut_name == "long"
        segments, events, at = [], [], 0.0
        title = BUILD / f"{cut_name}-00-title.mp4"
        card(title, TITLE, LONG_TITLE if long_cut else SHORT_TITLE, f"{cut_name}-title")
        segments.append(title)
        at += LONG_TITLE if long_cut else SHORT_TITLE
        for i, shot in enumerate(SHOTS, 1):
            if long_cut:
                caption = BUILD / f"{cut_name}-{i:02}a-{shot}-caption.mp4"
                caption_card(caption, CAPTIONS[shot], LONG_CARD, f"caption-{shot}")
                segments.append(caption)
                at += LONG_CARD
            parts = windows(shot, MOMENTS[cut_name][shot])
            clip = BUILD / f"{cut_name}-{i:02}b-{shot}.mp4"
            length = shot_segment(clip, shot, parts, None if long_cut else CAPTIONS[shot])
            segments.append(clip)
            events += sfx_events(shot, parts, at)
            at += length
        closing = BUILD / f"{cut_name}-99-closing.mp4"
        card(closing, CLOSING, LONG_CLOSE if long_cut else SHORT_CLOSE, f"{cut_name}-closing")
        segments.append(closing)
        at += LONG_CLOSE if long_cut else SHORT_CLOSE
        outputs.append(assemble(cut_name, segments, events, at, clips, music))
    return outputs


def main(argv):
    parser = argparse.ArgumentParser(prog="spear_test.py promo", description=__doc__.split("\n\n")[0])
    parser.add_argument("--shot", choices=SHOTS + ["shoals"],
                        help="refilm only this shot (or 'shoals': every shot with a shoal, in one launch), then edit with "
                             "the others' saved footage")
    parser.add_argument("--edit-only", action="store_true", help="edit from saved footage without filming")
    parser.add_argument("--music", default="default", help="music file (default: the game's These Lands, from Assets.zip)")
    parser.add_argument("--no-music", action="store_true", help="leave the music out")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=3600, help="seconds for the filming run")
    args = parser.parse_args(argv)
    music = None if args.no_music else args.music
    if music not in (None, "default") and not Path(music).is_file():
        parser.error(f"music file not found: {music}")
    PROMO.mkdir(parents=True, exist_ok=True)
    if not args.edit_only:
        film(args.shot, args.seed, args.timeout)
    for out in edit(music):
        print("Wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
