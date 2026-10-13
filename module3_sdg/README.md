# Module 3 — Synthetic Data Generation (project)

**Project goal:** generate a randomized, labelled pallet-jack detection dataset (KITTI format) that a detector
can be trained on.

| Lesson | Video | Diagram | Script |
|---|---|---|---|
| [Generate a dataset with Replicator](lesson1_generate_dataset.md) | [▶ 3](../videos/3.1_synthetic_data.mp4) | [pipeline](../diagrams/m3-sdg-pipeline.png) | `m3_palletjack_sdg.py` |

## Project milestones

- [ ] `m3_palletjack_sdg.py --headless --test` passes (5 different frames, palletjack-only labels)
- [ ] 20 frames generated with a window; you inspected images and labels
- [ ] Optional larger datasets, after the image/label checks: `--num_frames 2000 --distractors warehouse` and `--num_frames 1000 --distractors None`
- [ ] (outside Isaac Sim) detector trained with the course repo's notebook

**Before scaling up:** overlay KITTI boxes on a few RGB images and explain any empty labels, poor
visibility, or unexpected class assignments. Keep a bright and a dark example in your notes.

**Stretch project:** add a second object class and compare two small datasets with one randomization
setting changed. Do not treat the five-frame smoke test as evidence of real-world detector accuracy.

You can now create inputs for perception experiments. [Module 4](../module4_sil/README.md) returns to
robot control and shows how to exchange commands and sensor data with external software.
