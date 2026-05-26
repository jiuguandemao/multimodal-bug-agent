from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageChops, ImageStat


def extract_keyframes(video_path: Optional[Path], output_dir: Path, every_n_frames: int = 12, max_frames: int = 8) -> List[Path]:
    if not video_path or not video_path.exists():
        return []
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        import imageio.v2 as imageio
    except Exception:
        return []

    reader = imageio.get_reader(str(video_path))
    saved: List[Path] = []
    previous = None
    for idx, frame in enumerate(reader):
        if idx % every_n_frames != 0:
            continue
        image = Image.fromarray(frame).convert("RGB")
        if previous is not None and _mean_diff(previous, image) < 4:
            continue
        frame_path = output_dir / f"keyframe_{idx:04d}.png"
        image.save(frame_path)
        saved.append(frame_path)
        previous = image
        if len(saved) >= max_frames:
            break
    reader.close()
    return saved


def _mean_diff(a: Image.Image, b: Image.Image) -> float:
    b = b.resize(a.size)
    diff = ImageChops.difference(a, b)
    return ImageStat.Stat(diff.convert("L")).mean[0]

