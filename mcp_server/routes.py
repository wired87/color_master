"""MCP server exposing the 3D time-series visualization workflow from main.py."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is on path for main import
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import numpy as np
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from main import build_3d_time_series_visualization, _demo_input_data

APP_NAME = "color-master-viz"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_PATH = "/mcp"


def _ensure_numpy(obj: Any) -> Any:
    """Convert JSON-serializable structures to numpy-friendly format for main.build_3d_time_series_visualization."""
    if isinstance(obj, list):
        return np.array(obj)
    if isinstance(obj, dict):
        return {k: _ensure_numpy(v) for k, v in obj.items()}
    return obj


def _prepare_data(data: dict[str, list[Any]]) -> dict[str, list[Any]]:
    """Convert incoming JSON data to format expected by build_3d_time_series_visualization."""
    return {key: [_ensure_numpy(item) for item in series] for key, series in data.items()}


app = FastMCP(
    name=APP_NAME,
    instructions="MCP tools for 3D time-series visualization. Build static plots, animations, and combined environment views from mixed-type time-series data.",
    host=os.getenv("MCP_HOST", DEFAULT_HOST),
    port=int(os.getenv("MCP_PORT", str(DEFAULT_PORT))),
    streamable_http_path=os.getenv("MCP_PATH", DEFAULT_PATH),
    json_response=True,
    stateless_http=True,
)


@app.custom_route("/health", methods=["GET"], include_in_schema=False)
async def _health(_: Request) -> Response:
    print("[routes] GET /health", file=sys.stderr)
    return JSONResponse({"status": "ok", "app": APP_NAME, "mcp_path": os.getenv("MCP_PATH", DEFAULT_PATH)})


@app.tool()
def build_3d_visualization(
    data: dict[str, list[Any]],
    amount_nodes: int = 28,
    dims: int = 360,
    output_dir: str = "output_dir",
) -> dict[str, Any]:
    """
    Run the full 3D time-series visualization pipeline.

    Accepts a dict of time-series data (JSON-serializable: lists of lists/numbers, scalars, nested dicts).
    Produces per-key static PNGs, per-key animated GIFs, and a combined environment GIF under output_dir.
    Transparency of each data point is scaled by min/max of that series.
    """
    try:
        print("[routes] build_3d_visualization start", file=sys.stderr)
        prepared = _prepare_data(data)
        build_3d_time_series_visualization(
            data=prepared,
            amount_nodes=amount_nodes,
            dims=dims,
            output_dir=output_dir,
        )
        out_root = Path(output_dir)
        static_dir = out_root / "per_key_static"
        anim_dir = out_root / "per_key_animation"
        combined_path = out_root / "combined" / "environment_3d.gif"
        keys = list(data.keys())
        return {
            "status": "ok",
            "output_dir": str(out_root),
            "per_key_static": [str(static_dir / f"{k}_3d.png") for k in keys],
            "per_key_animation": [str(anim_dir / f"{k}_3d.gif") for k in keys],
            "combined_animation": str(combined_path),
        }
    except Exception as exc:
        print(f"[routes] build_3d_visualization error: {exc!r}", file=sys.stderr)
        return {"status": "error", "message": str(exc)}


@app.tool()
def run_demo(
    timesteps: int = 50,
    amount_nodes: int = 36,
    dims: int = 360,
    output_dir: str = "output_dir",
) -> dict[str, Any]:
    """
    Run the hardcoded demo: mixed time-series data (list[array(3)], float, array[complex 5], dict with mixed fields).
    Returns paths of generated files.
    """
    try:
        print("[routes] run_demo start", file=sys.stderr)
        demo = _demo_input_data(timesteps=timesteps)
        build_3d_time_series_visualization(
            data=demo,
            amount_nodes=amount_nodes,
            dims=dims,
            output_dir=output_dir,
        )
        out_root = Path(output_dir)
        keys = list(demo.keys())
        return {
            "status": "ok",
            "output_dir": str(out_root),
            "per_key_static": [str(out_root / "per_key_static" / f"{k}_3d.png") for k in keys],
            "per_key_animation": [str(out_root / "per_key_animation" / f"{k}_3d.gif") for k in keys],
            "combined_animation": str(out_root / "combined" / "environment_3d.gif"),
        }
    except Exception as exc:
        print(f"[routes] run_demo error: {exc!r}", file=sys.stderr)
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", DEFAULT_HOST)
    port = int(os.getenv("MCP_PORT", str(DEFAULT_PORT)))
    path = os.getenv("MCP_PATH", DEFAULT_PATH)
    print(f"[routes] starting streamable-http host={host} port={port} path={path}", file=sys.stderr)
    app.run(transport="streamable-http")
