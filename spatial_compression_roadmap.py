from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "rrkal_displaytools.spatial_compression_roadmap.v1"


def roadmap_packet(source: str = "spatial_compression_roadmap") -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source": source,
        "status": "research_contract_only",
        "displaytools_role": "renderer_contracts_visual_review_and_lod_selection_only",
        "primary_problem": "Move beyond planar 1D Fourier assumptions for global bathymetry and ocean terrain fields.",
        "avoid_as_primary_codec": [
            "lossy_planar_1d_fourier_for_global_bathymetry",
            "projection_unaware_global_grid_fft",
            "runtime_training_inside_displaytools",
        ],
        "strategy_options": [
            {
                "id": "two_dimensional_dwt",
                "label": "2D DWT tile/residual codec",
                "status": "candidate_for_tile_local_edge_preservation",
                "owner": "rrkal-visual-compressor",
                "best_fit": "tile-local bathymetry residuals, cliff/trench edges and texture pyramids",
                "risk": "needs padding and seam policy to avoid tile boundary artifacts",
                "displaytools_contract": "consume decoded height/normal tiles plus compression metadata only",
            },
            {
                "id": "spherical_harmonics",
                "label": "Sparse spherical harmonics global LOD",
                "status": "preferred_global_lod_probe_after_render_plan_decoupling",
                "owner": "shared_contract_between_visual_compressor_and_displaytools_renderer",
                "best_fit": "global low-frequency sphere fields without polar tearing",
                "risk": "high-frequency trenches require residual or tile overlay channel",
                "displaytools_contract": "sample coefficients through renderer LOD contract, not data discovery",
            },
            {
                "id": "neural_field",
                "label": "Latent neural field compression",
                "status": "research_only_not_mvp",
                "owner": "future_research_branch",
                "best_fit": "continuous-resolution terrain reconstruction after baseline contracts are stable",
                "risk": "training, validation, reproducibility and GPU budget are not displaytools MVP work",
                "displaytools_contract": "accept prevalidated lightweight decoder artifacts only after parity evidence",
            },
        ],
        "recommended_sequence": [
            "finish_render_plan_compose_decoupling",
            "record_renderer_lod_sampling_contract",
            "prototype_spherical_harmonics_low_frequency_lod_contract",
            "prototype_2d_dwt_tile_residual_contract_in_visual_compressor",
            "consider_neural_field_only_after_reproducible_baselines",
        ],
        "required_evidence_before_runtime_adoption": [
            "visual_parity_artifacts",
            "stage_timing_jsonl",
            "memory_transfer_counts",
            "polar_region_artifact_review",
            "trench_edge_artifact_review",
        ],
        "explicit_non_goals": [
            "no_dataset_discovery",
            "no_dataset_download",
            "no_cache_governance",
            "no_training_loop",
            "no_runtime_codec_switch_before_parity",
        ],
        "boundary": "displaytools records renderer-facing contracts and visual evidence requirements; RRKAL owns data/cache governance and rrkal-visual-compressor owns codec experiments.",
        "portable": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the RRKAL_displaytools spatial compression roadmap contract.")
    parser.add_argument("--source", default="spatial_compression_roadmap")
    args = parser.parse_args()
    print(json.dumps(roadmap_packet(args.source), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
