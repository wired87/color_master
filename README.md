# Color Master

3D time-series visualization engine with MCP server support. Generates static plots, per-key animations, and combined environment views from mixed-type time-series data.

## Quick Start

### Run the demo locally

```bash
pip install -r requirements.txt
python main.py
```

Output files are written to `output_dir/` (per-key static PNGs, per-key GIFs, combined environment GIF).

### Run the MCP server

```bash
pip install -r requirements.txt
python mcp_server/routes.py
```

**Environment variables:**
- `MCP_HOST` – host (default: `0.0.0.0`)
- `MCP_PORT` – port (default: `8000`)
- `MCP_PATH` – MCP endpoint path (default: `/mcp`)

**MCP endpoint:** `http://localhost:8000/mcp`

**Tools:**
- `build_3d_visualization(data, amount_nodes, dims, output_dir)` – run the full pipeline on JSON-serializable time-series data
- `run_demo(timesteps, amount_nodes, dims, output_dir)` – run the hardcoded demo and return generated file paths

## Docker

### Build

```bash
docker build -t color-master-mcp .
```

### Run

```bash
docker run -p 8000:8000 color-master-mcp
```

MCP endpoint: `http://localhost:8000/mcp`

## Requirements

- Python 3.10+
- `mcp[cli]`, `matplotlib`, `numpy`

See `requirements.txt`.
