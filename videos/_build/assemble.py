"""Assemble narrated lesson videos from slide frames + ElevenLabs narration.

    python3 learning_resource/videos/_build/assemble.py [lesson_id ...]

For every slide: narration mp3 (videos/_work/<lid>/sNN_audio/*.mp3), padded with a short lead-in and tail.
Steps slides switch frames when the narration reaches each bullet (timed by text length).
Every slide gets a slow push-in zoom; slides are joined with 0.5 s crossfades.
Output: videos/<lid>.mp4 (H.264 + AAC, small burned-in captions) and videos/subtitles/<lid>.srt
"""

import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VID = os.path.join(ROOT, "videos")
WORK = os.path.join(VID, "_work")
FPS = 30
LEAD, TAIL, XF = 0.5, 0.9, 0.5  # seconds of silence before/after speech, crossfade length


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = []
    for p in parts:  # keep cues readable: split long sentences at commas
        while len(p) > 110 and "," in p[40:]:
            cut = p.index(",", 40) + 1
            out.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            out.append(p)
    return out


def slide_clip(lid, si, slide, tmp):
    mp3s = sorted(glob.glob(os.path.join(WORK, lid, f"s{si:02d}_audio", "*.mp3")))
    if not mp3s:
        raise SystemExit(f"missing narration for {lid} slide {si}")
    speech = duration(mp3s[-1])
    total = LEAD + speech + TAIL
    # frame switch times, proportional to text length of each segment
    segs = slide["segments"]
    lens = [max(1, len(s)) for s in segs]
    starts, acc = [], 0
    for n in lens:
        starts.append(LEAD + speech * acc / sum(lens))
        acc += n
    starts[0] = 0.0
    frames = slide["frames"]
    concat = os.path.join(tmp, f"s{si:02d}.txt")
    with open(concat, "w") as f:
        for k, fr in enumerate(frames):
            end = starts[k + 1] if k + 1 < len(frames) else total
            f.write(f"file '{os.path.join(WORK, lid, fr)}'\nduration {end - starts[k]:.3f}\n")
        f.write(f"file '{os.path.join(WORK, lid, frames[-1])}'\n")
    out = os.path.join(tmp, f"s{si:02d}.mp4")
    newest_input = max(os.path.getmtime(mp3s[-1]), os.path.getmtime(os.path.join(WORK, lid, frames[0])))
    cached = os.path.exists(out) and os.path.getmtime(out) > newest_input
    nframes = int(total * FPS)
    vf = (f"fps={FPS},zoompan=z='1+0.035*on/{nframes}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":s=1920x1080:fps={FPS},format=yuv420p")
    if not cached:
      run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
         "-i", mp3s[-1], "-filter_complex",
         f"[0:v]{vf}[v];[1:a]adelay={int(LEAD * 1000)}:all=1,apad=whole_dur={total:.3f},aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", out])
    # subtitle cues inside this clip, timed by text length
    cues, sents = [], sentences(slide["text"])
    lens = [len(s) for s in sents]
    acc = 0
    for s, n in zip(sents, lens):
        a = LEAD + speech * acc / sum(lens)
        acc += n
        b = LEAD + speech * acc / sum(lens)
        cues.append((a, b, s))
    return out, total, cues


def build(lid):
    with open(os.path.join(WORK, lid, "plan.json")) as f:
        plan = json.load(f)
    tmp = os.path.join(WORK, lid, "_clips")
    os.makedirs(tmp, exist_ok=True)
    clips, durs, all_cues = [], [], []
    t0 = 0.0
    for si, slide in enumerate(plan["slides"]):
        clip, d, cues = slide_clip(lid, si, slide, tmp)
        clips.append(clip)
        durs.append(d)
        all_cues += [(t0 + a, t0 + b, s) for a, b, s in cues]
        t0 += d - XF
    # crossfade chain
    inputs, fc = [], []
    for c in clips:
        inputs += ["-i", c]
    vprev, aprev, offset = "0:v", "0:a", 0.0
    for i in range(1, len(clips)):
        offset += durs[i - 1] - XF
        fc.append(f"[{vprev}][{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[v{i}]")
        fc.append(f"[{aprev}][{i}:a]acrossfade=d={XF}[a{i}]")
        vprev, aprev = f"v{i}", f"a{i}"
    os.makedirs(os.path.join(VID, "subtitles"), exist_ok=True)
    srt = os.path.join(VID, "subtitles", f"{lid}.srt")
    with open(srt, "w") as f:
        for i, (a, b, s) in enumerate(all_cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{s}\n\n")
    out = os.path.join(VID, f"{lid}.mp4")
    # Small burned-in captions (~30 px on 1080p) on a translucent box just above the slide footer.
    # No soft subtitle track: players render those at their own (often huge) size.
    style = ("FontName=DejaVu Sans,FontSize=7,PrimaryColour=&H00FFFFFF,BackColour=&H33202431,"
             "BorderStyle=4,Outline=0,Shadow=0,MarginV=30,MarginL=24,MarginR=24")
    fc.append(f"[{vprev}]subtitles=filename={srt}:force_style='{style}'[vout]")
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", f"[{aprev}]" if len(clips) > 1 else "0:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
           "-metadata", f"title={plan['title']}", "-movflags", "+faststart", out]
    run(cmd)
    print(f"{lid}: {duration(out):.1f} s -> {out}")


if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(d for d in os.listdir(WORK) if os.path.isdir(os.path.join(WORK, d)))
    for lid in ids:
        build(lid)
