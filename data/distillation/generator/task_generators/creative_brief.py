"""
creative_brief.py — CREATIVE_BRIEF Task Generator
===================================================
Video/script/UGC creative brief senaryoları. (Toplam dağılımın %10'u)
Ek alan: video_script timeline.
"""

import random
from ..scenarios import build_scenario


_VIDEO_LENGTHS = [6, 10, 15, 20, 30, 45, 60]

_CREATIVE_TYPES = [
    "ugc_testimonial", "product_demo", "before_after", "unboxing",
    "founder_story", "tutorial_how_to", "lifestyle_montage",
    "problem_agitate_solve", "social_proof_compilation",
    "behind_the_scenes", "day_in_life", "trend_remix",
    "asmr_product", "comparison_test", "reaction_video",
    "expert_endorsement", "customer_interview",
]

_HOOK_STYLES = [
    "face_to_camera_question", "bold_text_overlay", "shock_stat",
    "product_in_action", "relatable_problem", "trend_audio",
    "before_after_split", "asmr_close_up", "controversy_statement",
    "celebrity_cameo", "visual_disruption", "whisper_hook",
]

_EDIT_STYLES = [
    "fast_cut_dynamic", "smooth_minimal", "raw_authentic",
    "cinematic_polished", "meme_inspired", "tutorial_clean",
    "stop_motion", "split_screen", "zoom_transitions",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """CREATIVE_BRIEF örneği üret — video script timeline içerir."""
    base = build_scenario(
        platform=platform,
        task_type="CREATIVE_BRIEF",
        example_id=example_id,
        **kwargs,
    )

    video_length = random.choice(_VIDEO_LENGTHS)
    creative_type = random.choice(_CREATIVE_TYPES)
    hook_style = random.choice(_HOOK_STYLES)
    edit_style = random.choice(_EDIT_STYLES)
    num_scenes = max(3, video_length // 5)

    # Generate scene breakdown request
    scene_desc = []
    for i in range(num_scenes):
        sec_start = int(i * video_length / num_scenes)
        sec_end = int((i + 1) * video_length / num_scenes)
        scene_desc.append(f"  - Sahne {i+1}: {sec_start}-{sec_end}s")

    scenes_text = "\n".join(scene_desc)
    creative_section = (
        f"\n\n### Creative Brief Detaylari\n"
        f"- Video suresi: {video_length}s\n"
        f"- Creative tipi: {creative_type}\n"
        f"- Hook stili: {hook_style}\n"
        f"- Edit stili: {edit_style}\n"
        f"- Sahne sayisi: {num_scenes}\n"
        + scenes_text + "\n"
        f"- JSON yanitinda \"video_script\" arrayi ekle: her sahne icin sec, visual, voice, on_screen_text, edit_notes alanlari.\n"
        f"- Ilk 2 saniye hook -- thumbstop optimize edilmeli.\n"
        f"- Son sahne CTA + branding.\n"
    )

    base["user"] = base["user"] + creative_section
    if "creative_brief" not in base["tags"]:
        base["tags"].append("video_script")

    return base
