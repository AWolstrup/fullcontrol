# Changes implemented to first pr submission

- Renamed `infaxis` to `infinaxis` across package files, demos, tutorials, Colab notebooks, and the Colab generator.
- `lab.fullcontrol.infinaxis` now follows the root package flow: `__init__.py` imports from `common.py`.
- `common.py` imports the base `fullcontrol` namespace for normal user access, then overrides the infinaxis-specific public names: `Point`, `Printer`, `GcodeControls`, `Axis`, `gcode`, and `transform`.
- Demos/tutorials now use only `import lab.fullcontrol.infinaxis as fci`; no `fullcontrol` monkey-patching or extra `import fullcontrol as fc`.
- Helper-only plot functions moved out of public `common.py` into private `_plot.py`.
- Internal package imports now point at `lab.fullcontrol.infinaxis...`.
- `Point.axes` remains optional, and inverse kinematics only reads it when it is present, so `fci.Point(x=10)` works naturally.
- Added `fci.configure_point(head_chain, bed_chain)` to return a configured `Point` class.
  - It keeps `axes={...}` as the internal storage model, but allows dot-style axis input/access like `Point(x=10, b=20, c=30)` or `Point(X=10, B=20, C=30)`.
  - Axis matching is case-insensitive for user input, while stored axis keys preserve the configured `Axis.name` for gcode output.
  - Gcode state now recognizes configured `Point` subclasses.
- Updated the two infinaxis demos, tutorial notebooks, and Colab copies to use `Point = fci.configure_point(head_chain, bed_chain)` with dot-style axis values instead of `axes={...}`.
- Added `fci.xyz_geom` and `fci.xyz_add_axes(...)`, matching the existing multiaxis pattern for using normal xyz geometry functions and converting their Points to infinaxis Points.
- Clarified optional helper gcode outputs: `distance_axis` can emit accumulated-distance `U`, while `model_XYZ_gcode` can emit model-space `U/V/W` for motion-planning support.
- Updated the root 5-axis demo to show gcode output with `verbose=False` and `verbose=True`.
- `Axis(name="X")`, `Axis(name="Y")`, and `Axis(name="Z")` now raise an exception; linear helper axes should use another name with `type="X"`, `type="Y"`, or `type="Z"`.
- Added a root custom-axis-names demo showing `CI` / `CII` with shared `type="C"` kinematics.
- Added a root controls demo showing `Axis.name/type/active/orientation/offset` plus `GcodeControls.verbose`, `distance_axis`, `model_XYZ_gcode`, `inverse_time_feedrate`, and `xyz_orientation`; uncertain descriptions are marked with `CHECK_THIS_DESCRIPTION`.
- Added cautious fixed-axis notes to `lab.fullcontrol.fouraxis`, `lab.fullcontrol.fiveaxis`, `lab.fullcontrol.fiveaxisC0B1`, and the four/five-axis tutorial and Colab notebooks.


Due to rename from infaxis to infinaxis, git tracking is not that valuable (lots of untracked/deleted files rather than comparisions of modification). A python script was written to do a comparison and results of that script are copied below.

### python script:

``` python
from __future__ import annotations

import difflib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "infinaxis_rename_comparison.md"

PAIRS = [
    ("lab/fullcontrol/infaxis/__init__.py", "lab/fullcontrol/infinaxis/__init__.py"),
    ("lab/fullcontrol/infaxis/axis.py", "lab/fullcontrol/infinaxis/axis.py"),
    ("lab/fullcontrol/infaxis/common.py", "lab/fullcontrol/infinaxis/common.py"),
    ("lab/fullcontrol/infaxis/controls.py", "lab/fullcontrol/infinaxis/controls.py"),
    ("lab/fullcontrol/infaxis/point.py", "lab/fullcontrol/infinaxis/point.py"),
    ("lab/fullcontrol/infaxis/printer.py", "lab/fullcontrol/infinaxis/printer.py"),
    ("lab/fullcontrol/infaxis/state.py", "lab/fullcontrol/infinaxis/state.py"),
    ("lab/fullcontrol/infaxis/steps2gcode.py", "lab/fullcontrol/infinaxis/steps2gcode.py"),
    ("tutorials/lab_infaxis_4_demo.ipynb", "tutorials/lab_infinaxis_4_demo.ipynb"),
    ("tutorials/lab_infaxis_5_demo.ipynb", "tutorials/lab_infinaxis_5_demo.ipynb"),
    ("tutorials/colab/lab_infaxis_4_demo_colab.ipynb", "tutorials/colab/lab_infinaxis_4_demo_colab.ipynb"),
    ("tutorials/colab/lab_infaxis_5_demo_colab.ipynb", "tutorials/colab/lab_infinaxis_5_demo_colab.ipynb"),
]

NEW_ONLY = [
    "lab/fullcontrol/infinaxis/_plot.py",
    "lab/fullcontrol/infinaxis/xyz_add_axes.py",
]


def git_show(path: str) -> str:
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT, text=True)


def normalize_text(text: str) -> str:
    return (
        text.replace("infaxis", "infinaxis")
        .replace("Infaxis", "Infinaxis")
        .replace("INFAXIS", "INFINAXIS")
        .replace("fc_infinaxis", "lab.fullcontrol.infinaxis")
    )


def normalize_notebook(text: str) -> str:
    notebook = json.loads(text)
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
    return json.dumps(notebook, indent=1, sort_keys=True) + "\n"


def normalized(path: str, text: str) -> list[str]:
    text = normalize_text(text)
    if path.endswith(".ipynb"):
        text = normalize_notebook(text)
    return text.splitlines(keepends=True)


def main() -> None:
    sections: list[str] = [
        "# Infinaxis Rename Comparison\n\n",
        "This file compares old tracked `infaxis` files from `HEAD` with the current working-tree `infinaxis` files.\n\n",
        "Normalization applied before diffing:\n\n",
        "- `infaxis`/`Infaxis`/`INFAXIS` text is treated as `infinaxis`/`Infinaxis`/`INFINAXIS`.\n",
        "- notebook outputs and execution counts are cleared.\n",
        "- notebook JSON is formatted consistently.\n\n",
        "Use this as a temporary commit-description aid; it can be deleted after the rename/edit commit is prepared.\n\n",
    ]

    changed = 0
    unchanged = 0
    missing = 0

    for old_path, new_path in PAIRS:
        sections.append(f"## `{old_path}` -> `{new_path}`\n\n")
        new_file = ROOT / new_path
        if not new_file.exists():
            sections.append(f"Missing new file: `{new_path}`\n\n")
            missing += 1
            continue

        old_lines = normalized(old_path, git_show(old_path))
        new_lines = normalized(new_path, new_file.read_text())
        diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=old_path.replace("infaxis", "infinaxis"),
                tofile=new_path,
            )
        )
        if diff:
            changed += 1
            sections.append("```diff\n")
            sections.extend(diff)
            sections.append("```\n\n")
        else:
            unchanged += 1
            sections.append("No content changes after rename normalization.\n\n")

    if NEW_ONLY:
        sections.append("## New files without old `infaxis` equivalent\n\n")
        for path in NEW_ONLY:
            exists = (ROOT / path).exists()
            status = "present" if exists else "missing"
            sections.append(f"- `{path}`: {status}\n")
        sections.append("\n")

    summary = (
        "## Summary\n\n"
        f"- compared pairs: {len(PAIRS)}\n"
        f"- changed after normalization: {changed}\n"
        f"- unchanged after normalization: {unchanged}\n"
        f"- missing new files: {missing}\n\n"
    )
    sections.insert(1, summary)
    OUTPUT.write_text("".join(sections))
    print(OUTPUT)


if __name__ == "__main__":
    main()
```

### python script output:


_____
_____
_____

### NOTE THIS WAS RUN BEFORE RENAMING SOME OF THE TUTORIALS AND CREATING THE README AT lab/fullcontrol/infinaxis/README.md

# Infinaxis Rename Comparison

## Summary

- compared pairs: 12
- changed after normalization: 12
- unchanged after normalization: 0
- missing new files: 0

This file compares old tracked `infaxis` files from `HEAD` with the current working-tree `infinaxis` files.

Normalization applied before diffing:

- `infaxis`/`Infaxis`/`INFAXIS` text is treated as `infinaxis`/`Infinaxis`/`INFINAXIS`.
- notebook outputs and execution counts are cleared.
- notebook JSON is formatted consistently.

Use this as a temporary commit-description aid; it can be deleted after the rename/edit commit is prepared.

## `lab/fullcontrol/infaxis/__init__.py` -> `lab/fullcontrol/infinaxis/__init__.py`

```diff
--- lab/fullcontrol/infinaxis/__init__.py
+++ lab/fullcontrol/infinaxis/__init__.py
@@ -1,7 +1 @@
-from .point import Point
-from .controls import GcodeControls
-from .printer import Printer
-from .state import State
-from .steps2gcode import gcode
-from .common import transform
-from .axis import Axis+from lab.fullcontrol.infinaxis.common import *
```

## `lab/fullcontrol/infaxis/axis.py` -> `lab/fullcontrol/infinaxis/axis.py`

```diff
--- lab/fullcontrol/infinaxis/axis.py
+++ lab/fullcontrol/infinaxis/axis.py
@@ -12,6 +12,9 @@
     def __init__(self, **data):
         super().__init__(**data)
 
+        if self.name is not None and self.name.upper() in ["X", "Y", "Z"]:
+            raise ValueError('Axis.name cannot be "X", "Y", or "Z"; use Axis.type for linear kinematics with a different name')
+
         if self.type is None:
             if self.name is not None and self.name in ["A", "B", "C"]:
                 self.type = self.name
```

## `lab/fullcontrol/infaxis/common.py` -> `lab/fullcontrol/infinaxis/common.py`

```diff
--- lab/fullcontrol/infinaxis/common.py
+++ lab/fullcontrol/infinaxis/common.py
@@ -1,307 +1,14 @@
 from typing import Union
 
-import numpy as np
-import plotly.graph_objects as go
-from fullcontrol.visualize.tube_mesh import CylindersMesh, FlowTubeMesh, MeshExporter
-from fullcontrol.visualize.controls import PlotControls
-from fullcontrol.visualize.plot_data import PlotData
-from fullcontrol.visualize.state import State
-from fullcontrol.visualize.plotly import generate_mesh
-# # see comment in __init__.py about why this module exists
-
-# # import functions and classes that will be accessible to the user
-from fullcontrol.common import check
-from fullcontrol.geometry import move, move_polar, travel_to  # don't import all geometry functions since they are not designed for multiaxis Points
-from fullcontrol.combinations.gcode_and_visualize.classes import *
+from fullcontrol import *
 import fullcontrol.geometry as xyz_geom
-
-def generate_single_path_vase_lod_surface_arrays(
-    path,
-    center_xy=None,
-    points_per_turn: int = 128,
-    turn_stride: int = 2,
-    color_mode: str = "none",
-):
-    points = np.asarray([path.xvals, path.yvals, path.zvals], dtype=np.float32).T
-
-    if len(points) < 4:
-        return None, None, None, None
-
-    good = np.ones(len(points), dtype=bool)
-    dups = np.all(np.diff(points, axis=0) == 0, axis=1)
-    good[1:] = ~dups
-    points = points[good]
-
-    if len(points) < 4:
-        return None, None, None, None
-
-    source_color_scalar = None
-
-    if color_mode == "path":
-        if getattr(path, "colors", None) is not None and len(path.colors) > 0:
-            colors_arr = np.asarray(path.colors, dtype=np.float32)
-
-            if len(colors_arr) == len(good):
-                colors_arr = colors_arr[good]
-
-            if len(colors_arr) == len(points):
-                source_color_scalar = (
-                    0.299 * colors_arr[:, 0]
-                    + 0.587 * colors_arr[:, 1]
-                    + 0.114 * colors_arr[:, 2]
-                ).astype(np.float32)
-
-    if center_xy is None:
-        cx = np.float32(0.5 * (np.min(points[:, 0]) + np.max(points[:, 0])))
-        cy = np.float32(0.5 * (np.min(points[:, 1]) + np.max(points[:, 1])))
-    else:
-        cx, cy = center_xy
-
-    theta = np.unwrap(np.arctan2(points[:, 1] - cy, points[:, 0] - cx)).astype(np.float32)
-
-    if theta[-1] < theta[0]:
-        theta = -theta
-
-    turn_coord = ((theta - theta[0]) / np.float32(2.0 * np.pi)).astype(np.float32)
-
-    monotonic_good = np.concatenate([[True], np.diff(turn_coord) > 1e-10])
-    turn_coord = turn_coord[monotonic_good]
-    points = points[monotonic_good]
-
-    if source_color_scalar is not None:
-        source_color_scalar = source_color_scalar[monotonic_good]
-
-    if len(points) < 4:
-        return None, None, None, None
-
-    first_complete_turn = int(np.ceil(turn_coord[0]))
-    last_complete_turn = int(np.floor(turn_coord[-1])) - 1
-
-    if last_complete_turn <= first_complete_turn:
-        return None, None, None, None
-
-    all_turns = np.arange(first_complete_turn, last_complete_turn + 1, dtype=np.float32)
-
-    selected_turns = all_turns[::max(1, int(turn_stride))]
-
-    if selected_turns[-1] != all_turns[-1]:
-        selected_turns = np.append(selected_turns, all_turns[-1]).astype(np.float32)
-
-    if len(selected_turns) < 2:
-        return None, None, None, None
-
-    phases = np.linspace(
-        0.0,
-        1.0,
-        points_per_turn + 1,
-        endpoint=True,
-        dtype=np.float32,
-    )
-
-    targets = selected_turns[:, None] + phases[None, :]
-    targets_flat = targets.ravel()
-
-    x_grid = np.interp(targets_flat, turn_coord, points[:, 0]).reshape(targets.shape).astype(np.float32)
-    y_grid = np.interp(targets_flat, turn_coord, points[:, 1]).reshape(targets.shape).astype(np.float32)
-    z_grid = np.interp(targets_flat, turn_coord, points[:, 2]).reshape(targets.shape).astype(np.float32)
-
-    if color_mode == "path" and source_color_scalar is not None:
-        color_grid = np.interp(
-            targets_flat,
-            turn_coord,
-            source_color_scalar,
-        ).reshape(targets.shape).astype(np.float32)
-
-    elif color_mode == "height":
-        color_grid = z_grid
-
-    elif color_mode == "turn":
-        color_grid = targets.astype(np.float32)
-
-    else:
-        color_grid = np.zeros_like(z_grid, dtype=np.float32)
-
-    return x_grid, y_grid, z_grid, color_grid
-
-def generate_single_path_vase_lod_surface_trace(
-    path,
-    center_xy=None,
-    points_per_turn: int = 128,
-    turn_stride: int = 2,
-    color_mode: str = "none",
-    colorscale="Viridis",
-    showscale: bool = False,
-    opacity: float = 1.0,
-):
-    """
-    Drop-in Plotly Surface trace for fast vase preview.
-
-    Returns:
-        go.Surface or None
-    """
-
-    x, y, z, surfacecolor = generate_single_path_vase_lod_surface_arrays(
-        path,
-        center_xy=center_xy,
-        points_per_turn=points_per_turn,
-        turn_stride=turn_stride,
-        color_mode=color_mode,
-    )
-
-    if x is None:
-        return None
-
-    return go.Surface(
-        x=x,
-        y=y,
-        z=z,
-        surfacecolor=surfacecolor,
-        colorscale=colorscale,
-        showscale=showscale,
-        opacity=opacity,
-        hoverinfo="skip",
-        contours=dict(
-            x=dict(show=False),
-            y=dict(show=False),
-            z=dict(show=False),
-        ),
-        # lighting=dict(
-        #     ambient=0.65,
-        #     diffuse=0.7,
-        #     specular=0.05,
-        #     roughness=1.0,
-        # ),
-        showlegend=False,
-    )
-
-
-
-def fig_plot(data: PlotData, controls: PlotControls):
-    '''
-    Plot data for x y z lines with RGB colors and annotations.
-    The style of the plot is governed by the controls.
-
-    Args:
-        data (PlotData): The data to be plotted.
-        controls (PlotControls): The controls for customizing the plot.
-
-    Returns:
-        None
-    '''
-    
-    fig = go.Figure()
-
-    if controls.tube_type is not None:
-        Mesh = {'flow': FlowTubeMesh, 'cylinders': CylindersMesh}[controls.tube_type]
-    else:  # Fall back to FlowTubeMesh if no tube_type is explicitly specified
-        Mesh = FlowTubeMesh
-
-    # generate line plots
-    max_width = 0
-
-    for path in data.paths:
-        colors_now = [f'rgb({color[0]*255:.2f}, {color[1]*255:.2f}, {color[2]*255:.2f})' for color in path.colors]
-
-        linewidth_now = controls.line_width * 2 if path.extruder.on == True else controls.line_width * 0.5
-
-        ## Generate mesh now imported from main fullcontrol visualization module, the only reason it was here was for the global local_max variable, I've just changed the plot function to derive a similar variable from the path width instead.
-        if path.widths:
-                max_width = max(max_width, max(path.widths))
-
-        if path.extruder.on and controls.style == "vase_surface":
-            surface_trace = generate_single_path_vase_lod_surface_trace(
-                path,
-                points_per_turn=96,
-                turn_stride=3,
-                color_mode="height",
-                colorscale="viridis",
-                showscale=False,
-                opacity=1.0,
-            )
-
-            if surface_trace is not None:
-                fig.add_trace(surface_trace)
-
-
-        elif path.extruder.on and controls.style == 'tube':
-            sides, rounding_strength, flat_sides = controls.tube_sides, 0.4, False
-            mesh = generate_mesh(path, linewidth_now, Mesh, sides, rounding_strength, flat_sides, colors_now)
-            fig.add_trace(mesh.to_Mesh3d(colors=colors_now))
-
-        elif not controls.hide_travel or path.extruder.on:
-            fig.add_trace(go.Scatter3d(
-                mode='lines',
-                x=path.xvals,
-                y=path.yvals,
-                z=path.zvals,
-                showlegend=False,
-                line=dict(width=linewidth_now, color=colors_now),
-            ))
-
-
-    # find a bounding box, to create a plot with equally proportioned X Y Z scales (so a cuboid looks like a cuboid, not a cube)
-    bounding_box_size = max(data.bounding_box.maxx-data.bounding_box.minx, data.bounding_box.maxy -
-                            data.bounding_box.miny, data.bounding_box.maxz-min(0, data.bounding_box.minz))
-    bounding_box_size += 0.002
-    bounding_box_size += max_width
-
-    # generate annotations
-    annotations_pts = []
-    annotations = []
-    if controls.hide_annotations == False and not controls.neat_for_publishing:
-    # if controls.hide_annotations == False:  # and not controls.neat_for_publishing:
-        for annotation in data.annotations:
-            x, y, z = (annotation[axis] for axis in 'xyz')
-            annotations_pts.append([x, y, z])
-            annotations.append(dict(
-                showarrow=False,
-                x=x, y=y, z=z,
-                text=annotation['label'],
-                yshift=10))
-        xs, ys, zs = zip(*annotations_pts) if annotations_pts else [[]]*3
-        fig.add_trace(go.Scatter3d(mode='markers', x=xs, y=ys, z=zs, showlegend=False, marker=dict(size=2, color='red')))
-
-        # make sure the bounding box is big enough for the annotations
-        # the 0.001 is to make sure the annotations don't lie on the boundary
-        midx, midy, midz = (getattr(data.bounding_box, f'mid{axis}') for axis in 'xyz')
-        range
-        offset = 0.001
-        offset_both_sides = 2 * offset
-        for (x, y, z) in annotations_pts:
-            if x < midx - bounding_box_size / 2 + offset:
-                bounding_box_size = 2 * (midx - x) + offset_both_sides
-            if x > midx + bounding_box_size / 2 - offset:
-                bounding_box_size = 2 * (x - midx) + offset_both_sides
-            if y < midy - bounding_box_size / 2 + offset:
-                bounding_box_size = 2 * (midy - y) + offset_both_sides
-            if y > midy + bounding_box_size / 2 - offset:
-                bounding_box_size = 2 * (y - midy) + offset_both_sides
-            if z < midz - bounding_box_size / 2 + offset:
-                bounding_box_size = 2 * (midz - z) + offset_both_sides
-            if z > midz + bounding_box_size / 2 - offset:
-                bounding_box_size = 2 * (z - midz) + offset_both_sides
-
-    relative_centre_z = 0.5*data.bounding_box.rangez/bounding_box_size
-    camera_centre_z = -0.5 + relative_centre_z
-    camera = dict(eye=dict(x=-0.5/controls.zoom, y=-1/controls.zoom, z=-0.5+0.5/controls.zoom),
-                  center=dict(x=0, y=0, z=camera_centre_z))
-    fig.update_layout(template='plotly_dark', paper_bgcolor="black", scene_aspectmode='cube',
-                      scene=dict(annotations=annotations,
-                                 xaxis=dict(backgroundcolor="black", nticks=10,
-                                            range=[data.bounding_box.midx-bounding_box_size/2, data.bounding_box.midx+bounding_box_size/2],),
-                                 yaxis=dict(backgroundcolor="black", nticks=10,
-                                            range=[data.bounding_box.midy-bounding_box_size/2, data.bounding_box.midy+bounding_box_size/2],),
-                                 zaxis=dict(backgroundcolor="black", nticks=10, range=[min(0, data.bounding_box.minz), bounding_box_size],),
-                      ), scene_camera=camera, width=800, height=500, margin=dict(l=10, r=10, b=10, t=10, pad=4))
-    if controls.hide_axes or controls.neat_for_publishing:
-        for axis in ['xaxis', 'yaxis', 'zaxis']:
-            fig.update_layout(
-                scene={axis: dict(showgrid=False, zeroline=False, visible=False)})
-    if controls.neat_for_publishing:
-        fig.update_layout(width=500, height=500)
-
-    # cicd_testing is a flag set by the CICD testing script (as a temporary environmental variable) to save the plot as a .png file
-    return fig
+# base fc namespace for user access; infinaxis replacements override matching names
+from lab.fullcontrol.infinaxis.axis import Axis
+from lab.fullcontrol.infinaxis.controls import GcodeControls
+from lab.fullcontrol.infinaxis.point import Point, configure_point
+from lab.fullcontrol.infinaxis.printer import Printer
+from lab.fullcontrol.infinaxis.steps2gcode import gcode
+from lab.fullcontrol.infinaxis.xyz_add_axes import xyz_add_axes
 
 
 def transform(steps: list, result_type: str, controls: Union[GcodeControls, PlotControls] = None, show_tips: bool = True):
@@ -311,7 +18,6 @@
     '''
 
     if result_type == 'gcode':
-        from lab.fullcontrol.infinaxis.steps2gcode import gcode
         if controls is None: controls = GcodeControls()
         return gcode(steps, controls)
 
@@ -321,16 +27,18 @@
         return visualize(steps, controls, show_tips)
     
     elif result_type == 'fig':
-        from fullcontrol.visualize.steps2visualization import visualize
+        from fullcontrol.visualize.plot_data import PlotData
+        from fullcontrol.visualize.state import State as VisualizeState
+        from lab.fullcontrol.infinaxis._plot import fig_plot
 
         if controls is None: controls = PlotControls()
         plot_controls = controls
         plot_controls.initialize()
 
-        state = State(steps, plot_controls)
+        state = VisualizeState(steps, plot_controls)
         plot_data = PlotData(steps, state)
         for step in steps:
             step.visualize(state, plot_data, plot_controls)
         plot_data.cleanup()
 
-        return fig_plot(plot_data, plot_controls)+        return fig_plot(plot_data, plot_controls)
```

## `lab/fullcontrol/infaxis/controls.py` -> `lab/fullcontrol/infinaxis/controls.py`

```diff
--- lab/fullcontrol/infinaxis/controls.py
+++ lab/fullcontrol/infinaxis/controls.py
@@ -11,6 +11,7 @@
     bed_chain: list = [] # Ordered list of axes in the bed chain, used for the IK loop (back to front!)
     xyz_orientation: Optional[list] = [1,1,1] # orientation of XYZ axes, 1 means the axis follows the right hand rule.
     inverse_time_feedrate: Optional[bool] = False  # if true, F command will be output as inverse time feedrate (e.g. F0.5 for 2 seconds per move) instead of speed (e.g. F300 for 300 mm/s). This is useful for some multiaxis machines that use inverse time feedrate to control speed. Note that when this is true, the print_speed and travel_speed attributes will be interpreted as seconds per move instead of mm/s. Also note that acceleration and deceleration will not be handled correctly when using inverse time feedrate, so it is recommended to use constant speed moves (G1 F...) when this is true.
+    # the following two parameters (model_XYZ_gcode and distance_axis) may be useful for give more information for motion planning
     distance_axis: Optional[bool] = False
     model_XYZ_gcode: Optional[bool] = False  # if true, the gcode output will have a UVW axis which shows the the XYZ movement in the model (Alternative to distance_axis). Intended to be used with the system axis (XYZAC for instance) all be treated as rotational in firmware and the UVW being linear aixs for motion planning.
     verbose: Optional[bool] = False```

## `lab/fullcontrol/infaxis/point.py` -> `lab/fullcontrol/infinaxis/point.py`

```diff
--- lab/fullcontrol/infinaxis/point.py
+++ lab/fullcontrol/infinaxis/point.py
@@ -3,7 +3,56 @@
 from copy import deepcopy
 import numpy as np
 
-from infinaxis.axis import Axis
+from lab.fullcontrol.infinaxis.axis import Axis
+
+
+def _model_field_names(model_class):
+    return set(model_class.model_fields if hasattr(model_class, "model_fields") else model_class.__fields__)
+
+
+def _axis_names(head_chain=None, bed_chain=None):
+    axes = list(head_chain or []) + list(bed_chain or [])
+    return {axis.name for axis in axes if axis.name is not None}
+
+
+def configure_point(head_chain=None, bed_chain=None):
+    """Return a Point class whose extra constructor fields map to configured axes."""
+    axis_name_lookup = {name.lower(): name for name in _axis_names(head_chain, bed_chain)}
+
+    class ConfiguredPoint(Point):
+        # Keep axes as the storage model. This class is only a user-facing
+        # convenience so designs can write Point(x=..., b=...) and point.b.
+        def __init__(self, **data):
+            fields = _model_field_names(type(self))
+            field_lookup = {name.lower(): name for name in fields}
+            axes = dict(data.pop("axes", None) or {})
+            for name in list(data):
+                if name not in fields and name.lower() in field_lookup:
+                    data[field_lookup[name.lower()]] = data.pop(name)
+                elif name.lower() in axis_name_lookup and name not in fields:
+                    axes[axis_name_lookup[name.lower()]] = data.pop(name)
+            if axes:
+                data["axes"] = axes
+            super().__init__(**data)
+
+        def __getattr__(self, name):
+            axes = getattr(self, "axes", None)
+            axis_name = axis_name_lookup.get(name.lower())
+            if axes is not None and axis_name in axes:
+                return axes[axis_name]
+            raise AttributeError(name)
+
+        def __setattr__(self, name, value):
+            axis_name = axis_name_lookup.get(name.lower())
+            if axis_name is not None and name not in _model_field_names(type(self)):
+                axes = dict(getattr(self, "axes", None) or {})
+                axes[axis_name] = value
+                super().__setattr__("axes", axes)
+            else:
+                super().__setattr__(name, value)
+
+    return ConfiguredPoint
+
 
 class Point(BasePoint):
     axes: Optional[dict] = None # dictionary for assigning chages to the printer Axis based on the info in the point
@@ -89,9 +138,10 @@
         model_point = deepcopy(state.point)
         model_point.update_from(self)
         # Update Axis from point
-        for axis in state.printer.head_chain + state.printer.bed_chain:
-            if axis.name in self.axes and self.axes[axis.name] != None:
-                axis.active = self.axes[axis.name]
+        if self.axes is not None:
+            for axis in state.printer.head_chain + state.printer.bed_chain:
+                if axis.name in self.axes and self.axes[axis.name] != None:
+                    axis.active = self.axes[axis.name]
 
         # inverse kinematics:
         system_point = model2system(model_point, state)
@@ -125,6 +175,7 @@
 
             
             state.distance_accumulated += (dist**2-dist_system**2)**0.5 if dist - dist_system > 0 else 0
+            # the following two checks for model_XYZ_gcode and distance_axis are only passed if the user flags them in GcodeControls and may be useful for give more information for motion planning
             if state.printer.model_XYZ_gcode:
                 infinaxis_str = infinaxis_str + f"U{round(self.x, 6):.6} V{round(self.y, 6):.6} W{round(self.z, 6):.6} "
             elif state.printer.distance_axis:
@@ -167,4 +218,4 @@
         if change_check:
             state.point.update_color(state, plot_data, plot_controls)
             plot_data.paths[-1].add_point(state)
-            state.point_count_now += 1+            state.point_count_now += 1
```

## `lab/fullcontrol/infaxis/printer.py` -> `lab/fullcontrol/infinaxis/printer.py`

```diff
--- lab/fullcontrol/infinaxis/printer.py
+++ lab/fullcontrol/infinaxis/printer.py
@@ -11,6 +11,7 @@
     bed_chain: list = None
     xyz_orientation: list = None
     inverse_time_feedrate: bool = None  # if true, F command will be output as inverse time feedrate (e.g. F2 for 30 seconds per move (1/2 minutes per move)) instead of speed (e.g. F300 for 300 mm/s). This is useful for some multiaxis machines that use inverse time feedrate to control speed.
+    # the following two parameters (model_XYZ_gcode and distance_axis) may be useful for give more information for motion planning
     distance_axis: bool = None
     model_XYZ_gcode: bool = None
     verbose: bool = None
```

## `lab/fullcontrol/infaxis/state.py` -> `lab/fullcontrol/infinaxis/state.py`

```diff
--- lab/fullcontrol/infinaxis/state.py
+++ lab/fullcontrol/infinaxis/state.py
@@ -3,11 +3,10 @@
 from importlib import import_module
 
 from fullcontrol.gcode.extrusion_classes import ExtrusionGeometry, Extruder
-from fullcontrol.gcode.controls import GcodeControls
 
-from infinaxis.point import Point
-from infinaxis.printer import Printer
-from infinaxis.controls import GcodeControls
+from lab.fullcontrol.infinaxis.point import Point
+from lab.fullcontrol.infinaxis.printer import Printer
+from lab.fullcontrol.infinaxis.controls import GcodeControls
 
 
 class State(BaseModel):
@@ -36,14 +35,14 @@
             'return first Point in list. if the parameter fully_defined is true, return first Point with x,y,z'
             if type(steps).__name__ == 'list':
                 for i in range(len(steps)):
-                    if type(steps[i]).__name__ == 'Point':
+                    if isinstance(steps[i], Point):
                         if fully_defined:
                             if steps[i].x != None and steps[i].y != None and steps[i].z != None:
                                 return steps[i]
                         else:
                             return steps[i]
             if fully_defined:
-                raise Exception(f'No point found in steps with all five axis defined')
+                raise Exception(f'No point found in steps with fully defined x, y, and z')
             if not fully_defined:
                 raise Exception(f'No point found in steps')
 
@@ -98,4 +97,4 @@
         primer_steps.append(Extruder(on=False))
         primer_steps.append(first_infinaxis_point(steps))  # move fast to start position
         primer_steps.append(Extruder(on=True))
-        self.steps = initialization_data['starting_procedure_steps'] + primer_steps + steps + initialization_data['ending_procedure_steps']+        self.steps = initialization_data['starting_procedure_steps'] + primer_steps + steps + initialization_data['ending_procedure_steps']
```

## `lab/fullcontrol/infaxis/steps2gcode.py` -> `lab/fullcontrol/infinaxis/steps2gcode.py`

```diff
--- lab/fullcontrol/infinaxis/steps2gcode.py
+++ lab/fullcontrol/infinaxis/steps2gcode.py
@@ -2,8 +2,8 @@
 import os
 from datetime import datetime
 
-from infinaxis.state import State
-from infinaxis.controls import GcodeControls
+from lab.fullcontrol.infinaxis.state import State
+from lab.fullcontrol.infinaxis.controls import GcodeControls
 
 
 def gcode(steps: list, gcode_controls: GcodeControls = GcodeControls()):
@@ -22,4 +22,4 @@
         filename = gcode_controls.save_as + datetime.now().strftime("__%d-%m-%Y__%H-%M-%S.gcode")
         open(filename, 'w').write(gc)
     else:
-        return gc+        return gc
```

## `tutorials/lab_infaxis_4_demo.ipynb` -> `tutorials/lab_infinaxis_4_demo.ipynb`

```diff
--- tutorials/lab_infinaxis_4_demo.ipynb
+++ tutorials/lab_infinaxis_4_demo.ipynb
@@ -8,13 +8,7 @@
    "outputs": [],
    "source": [
     "import lab.fullcontrol.infinaxis as fci\n",
-    "import fullcontrol as fc\n",
-    "from math import sin, cos, tau\n",
-    "\n",
-    "fc.Point = fci.Point\n",
-    "fc.GcodeControls = fci.GcodeControls\n",
-    "fc.transform = fci.transform\n",
-    "fc.Axis = fci.Axis"
+    "from math import sin, cos, tau\n"
    ]
   },
   {
@@ -28,9 +22,13 @@
     "EH = 0.3\n",
     "\n",
     "print_settings = {'extrusion_width': EW,'extrusion_height': EH}\n",
-    "gcode_controls = fc.GcodeControls(\n",
-    "    head_chain = [],\n",
-    "    bed_chain = [fc.Axis(name='C')],\n",
+    "head_chain = []\n",
+    "bed_chain = [fci.Axis(name='C')]\n",
+    "Point = fci.configure_point(head_chain, bed_chain)\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
     "    initialization_data=print_settings \n",
     "    )"
    ]
@@ -50,20 +48,20 @@
     "\n",
     "\n",
     "steps = []\n",
-    "steps.append(fc.Printer(print_speed=2160))\n",
+    "steps.append(fci.Printer(print_speed=2160))\n",
     "for i in range(layers):\n",
     "    for j in range(density):\n",
     "        angle = 360*(i+j/density)\n",
-    "        steps.append(fc.Point(x=r*sin(angle/360*tau), y=r*cos(angle/360*tau), z=((i+j/density)*h)+z_start, axes={'C':angle}))\n",
+    "        steps.append(Point(x=r*sin(angle/360*tau), y=r*cos(angle/360*tau), z=((i+j/density)*h)+z_start, c=angle))\n",
     "\n",
     "for step in steps:\n",
-    "    if type(step).__name__ == 'Point':\n",
+    "    if isinstance(step, fci.Point):\n",
     "        # color is a gradient from C=0 deg (blue) to C=360 (red)\n",
-    "        step.color = [((step.axes['C']%360)/360), 0, 1-((step.axes['C']%360)/360)]\n",
+    "        step.color = [((step.c%360)/360), 0, 1-((step.c%360)/360)]\n",
     "\n",
-    "fig = fc.transform(steps, 'fig', fc.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
+    "fig = fci.transform(steps, 'fig', fci.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
     "fig.show()\n",
-    "gcode = fc.transform(steps,'gcode',gcode_controls)\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
     "print('first ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[:10]))\n",
     "print('')\n",
     "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
```

## `tutorials/lab_infaxis_5_demo.ipynb` -> `tutorials/lab_infinaxis_5_demo.ipynb`

```diff
--- tutorials/lab_infinaxis_5_demo.ipynb
+++ tutorials/lab_infinaxis_5_demo.ipynb
@@ -8,13 +8,7 @@
    "outputs": [],
    "source": [
     "import lab.fullcontrol.infinaxis as fci\n",
-    "import fullcontrol as fc\n",
-    "from math import sin, cos, tau\n",
-    "\n",
-    "fc.Point = fci.Point\n",
-    "fc.GcodeControls = fci.GcodeControls\n",
-    "fc.transform = fci.transform\n",
-    "fc.Axis = fci.Axis"
+    "from math import sin, cos, tau\n"
    ]
   },
   {
@@ -28,11 +22,13 @@
     "EH = 0.3\n",
     "\n",
     "print_settings = {'extrusion_width': EW,'extrusion_height': EH}\n",
-    "gcode_controls = fc.GcodeControls(\n",
-    "    head_chain = [fc.Axis(name='B')],\n",
-    "    bed_chain = [fc.Axis(name='C')],\n",
-    "    distance_axis = True,\n",
-    "    verbose = True,\n",
+    "head_chain = [fci.Axis(name='B')]\n",
+    "bed_chain = [fci.Axis(name='C')]\n",
+    "Point = fci.configure_point(head_chain, bed_chain)\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
     "    initialization_data=print_settings \n",
     "    )"
    ]
@@ -53,17 +49,17 @@
     "        r_next = (p_next.x**2 + p_next.y**2)**0.5\n",
     "        dr = r_next - r\n",
     "        dz = p_next.z-p.z\n",
-    "        ptilt = p.axes['B']\n",
-    "        dtilt = p_next.axes['B']-ptilt\n",
+    "        ptilt = p.b\n",
+    "        dtilt = p_next.b-ptilt\n",
     "            \n",
-    "        dc = p_next.axes['C']-p.axes['C']\n",
+    "        dc = p_next.c-p.c\n",
     "        for j in range(density):\n",
-    "            angle = p.axes['C'] + dc * j / density\n",
+    "            angle = p.c + dc * j / density\n",
     "            tilt = ptilt + dtilt * j / density\n",
     "            r_final = r + dr * j / density\n",
     "            z_final = p.z + dz * j / density\n",
     "   \n",
-    "            steps.append(fc.Point(x=r_final*sin(angle/360*tau), y=r_final*cos(angle/360*tau), z=z_final, axes={'B':tilt,'C':angle}))\n",
+    "            steps.append(Point(x=r_final*sin(angle/360*tau), y=r_final*cos(angle/360*tau), z=z_final, b=tilt, c=angle))\n",
     "    \n",
     "    return steps\n",
     "\n",
@@ -87,45 +83,85 @@
     "    angle = i * 360\n",
     "    z = z_start + h * i\n",
     "\n",
-    "    trace.append(fc.Point(x=r, y=0, z=z, axes={'B':tilt,'C':angle}))\n",
+    "    trace.append(Point(x=r, y=0, z=z, b=tilt, c=angle))\n",
     "\n",
-    "angle_offset = fc.last_point(trace).axes['C']\n",
-    "z_offset = fc.last_point(trace).z\n",
+    "angle_offset = fci.last_point(trace).c\n",
+    "z_offset = fci.last_point(trace).z\n",
     "\n",
     "for i in range(1,arc_layers):\n",
     "    tilt = tilt_start + (tilt_end - tilt_start) * i / (arc_layers - 1)\n",
     "    r = r_start+r_tilt*(1-cos(tilt*tau/360))\n",
     "    z = z_offset+r_tilt*(sin(tilt*tau/360))\n",
     "    angle = i * 360 + angle_offset\n",
-    "    trace.append(fc.Point(x=r, y=0, z=z, axes={'B':-tilt,'C':angle}))\n",
+    "    trace.append(Point(x=r, y=0, z=z, b=-tilt, c=angle))\n",
     "\n",
-    "angle_offset = fc.last_point(trace).axes['C']\n",
-    "z_offset = fc.last_point(trace).z\n",
-    "r_offset = fc.last_point(trace).x\n",
+    "angle_offset = fci.last_point(trace).c\n",
+    "z_offset = fci.last_point(trace).z\n",
+    "r_offset = fci.last_point(trace).x\n",
     "\n",
     "for i in range(1,layers_tilted):\n",
     "    tilt = tilt_end\n",
     "    r = r_offset + d_tilted * i / (layers_tilted - 1) * (sin(tilt*tau/360))\n",
     "    z = z_offset + d_tilted * i / (layers_tilted - 1) * cos(tilt*tau/360)\n",
     "    angle = i * 360 + angle_offset\n",
-    "    trace.append(fc.Point(x=0, y=r, z=z, axes={'B':-tilt,'C':angle}))\n",
+    "    trace.append(Point(x=0, y=r, z=z, b=-tilt, c=angle))\n",
     "\n",
     "steps = vase_from_trace(trace, density)\n",
-    "steps.append(fc.last_point(trace))\n",
+    "steps.append(fci.last_point(trace))\n",
     "\n",
     "for step in steps:\n",
-    "    if type(step).__name__ == 'Point':\n",
+    "    if isinstance(step, fci.Point):\n",
     "        # color is a gradient from A=0 (blue) to A=90 (red)\n",
-    "        step.color = [((abs(step.axes['B']))/90), 0, 1-((abs(step.axes['B']))/90)]\n",
+    "        step.color = [((abs(step.b))/90), 0, 1-((abs(step.b))/90)]\n",
     "\n",
-    "fig = fc.transform(steps, 'fig', fc.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
+    "fig = fci.transform(steps, 'fig', fci.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
     "fig.show()\n",
     "\n",
-    "gcode = fc.transform(steps,'gcode',gcode_controls)\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
     "print('first ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[:10]))\n",
     "print('')\n",
     "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
    ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": null,
+   "id": "9462651e",
+   "metadata": {},
+   "outputs": [],
+   "source": [
+    "# with and without 'verbose'\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
+    "    verbose = False,\n",
+    "    initialization_data=print_settings \n",
+    "    )\n",
+    "\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
+    "print('___\\nwith GcodeControls(verbose=False):')\n",
+    "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
+    "    verbose = True,\n",
+    "    initialization_data=print_settings \n",
+    "    )\n",
+    "\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
+    "print('\\n___\\nwith GcodeControls(verbose=True):')\n",
+    "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": null,
+   "id": "aaf9ec1a",
+   "metadata": {},
+   "outputs": [],
+   "source": []
   }
  ],
  "metadata": {
```

## `tutorials/colab/lab_infaxis_4_demo_colab.ipynb` -> `tutorials/colab/lab_infinaxis_4_demo_colab.ipynb`

```diff
--- tutorials/colab/lab_infinaxis_4_demo_colab.ipynb
+++ tutorials/colab/lab_infinaxis_4_demo_colab.ipynb
@@ -8,13 +8,7 @@
    "outputs": [],
    "source": [
     "if 'google.colab' in str(get_ipython()):\n  !pip install git+https://github.com/FullControlXYZ/fullcontrol --quiet\nimport lab.fullcontrol.infinaxis as fci\n",
-    "import fullcontrol as fc\n",
-    "from math import sin, cos, tau\n",
-    "\n",
-    "fc.Point = fci.Point\n",
-    "fc.GcodeControls = fci.GcodeControls\n",
-    "fc.transform = fci.transform\n",
-    "fc.Axis = fci.Axis"
+    "from math import sin, cos, tau\n"
    ]
   },
   {
@@ -28,9 +22,13 @@
     "EH = 0.3\n",
     "\n",
     "print_settings = {'extrusion_width': EW,'extrusion_height': EH}\n",
-    "gcode_controls = fc.GcodeControls(\n",
-    "    head_chain = [],\n",
-    "    bed_chain = [fc.Axis(name='C')],\n",
+    "head_chain = []\n",
+    "bed_chain = [fci.Axis(name='C')]\n",
+    "Point = fci.configure_point(head_chain, bed_chain)\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
     "    initialization_data=print_settings \n",
     "    )"
    ]
@@ -50,20 +48,20 @@
     "\n",
     "\n",
     "steps = []\n",
-    "steps.append(fc.Printer(print_speed=2160))\n",
+    "steps.append(fci.Printer(print_speed=2160))\n",
     "for i in range(layers):\n",
     "    for j in range(density):\n",
     "        angle = 360*(i+j/density)\n",
-    "        steps.append(fc.Point(x=r*sin(angle/360*tau), y=r*cos(angle/360*tau), z=((i+j/density)*h)+z_start, axes={'C':angle}))\n",
+    "        steps.append(Point(x=r*sin(angle/360*tau), y=r*cos(angle/360*tau), z=((i+j/density)*h)+z_start, c=angle))\n",
     "\n",
     "for step in steps:\n",
-    "    if type(step).__name__ == 'Point':\n",
+    "    if isinstance(step, fci.Point):\n",
     "        # color is a gradient from C=0 deg (blue) to C=360 (red)\n",
-    "        step.color = [((step.axes['C']%360)/360), 0, 1-((step.axes['C']%360)/360)]\n",
+    "        step.color = [((step.c%360)/360), 0, 1-((step.c%360)/360)]\n",
     "\n",
-    "fig = fc.transform(steps, 'fig', fc.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
+    "fig = fci.transform(steps, 'fig', fci.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
     "fig.show()\n",
-    "gcode = fc.transform(steps,'gcode',gcode_controls)\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
     "print('first ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[:10]))\n",
     "print('')\n",
     "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
```

## `tutorials/colab/lab_infaxis_5_demo_colab.ipynb` -> `tutorials/colab/lab_infinaxis_5_demo_colab.ipynb`

```diff
--- tutorials/colab/lab_infinaxis_5_demo_colab.ipynb
+++ tutorials/colab/lab_infinaxis_5_demo_colab.ipynb
@@ -8,13 +8,7 @@
    "outputs": [],
    "source": [
     "if 'google.colab' in str(get_ipython()):\n  !pip install git+https://github.com/FullControlXYZ/fullcontrol --quiet\nimport lab.fullcontrol.infinaxis as fci\n",
-    "import fullcontrol as fc\n",
-    "from math import sin, cos, tau\n",
-    "\n",
-    "fc.Point = fci.Point\n",
-    "fc.GcodeControls = fci.GcodeControls\n",
-    "fc.transform = fci.transform\n",
-    "fc.Axis = fci.Axis"
+    "from math import sin, cos, tau\n"
    ]
   },
   {
@@ -28,11 +22,13 @@
     "EH = 0.3\n",
     "\n",
     "print_settings = {'extrusion_width': EW,'extrusion_height': EH}\n",
-    "gcode_controls = fc.GcodeControls(\n",
-    "    head_chain = [fc.Axis(name='B')],\n",
-    "    bed_chain = [fc.Axis(name='C')],\n",
-    "    distance_axis = True,\n",
-    "    verbose = True,\n",
+    "head_chain = [fci.Axis(name='B')]\n",
+    "bed_chain = [fci.Axis(name='C')]\n",
+    "Point = fci.configure_point(head_chain, bed_chain)\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
     "    initialization_data=print_settings \n",
     "    )"
    ]
@@ -53,17 +49,17 @@
     "        r_next = (p_next.x**2 + p_next.y**2)**0.5\n",
     "        dr = r_next - r\n",
     "        dz = p_next.z-p.z\n",
-    "        ptilt = p.axes['B']\n",
-    "        dtilt = p_next.axes['B']-ptilt\n",
+    "        ptilt = p.b\n",
+    "        dtilt = p_next.b-ptilt\n",
     "            \n",
-    "        dc = p_next.axes['C']-p.axes['C']\n",
+    "        dc = p_next.c-p.c\n",
     "        for j in range(density):\n",
-    "            angle = p.axes['C'] + dc * j / density\n",
+    "            angle = p.c + dc * j / density\n",
     "            tilt = ptilt + dtilt * j / density\n",
     "            r_final = r + dr * j / density\n",
     "            z_final = p.z + dz * j / density\n",
     "   \n",
-    "            steps.append(fc.Point(x=r_final*sin(angle/360*tau), y=r_final*cos(angle/360*tau), z=z_final, axes={'B':tilt,'C':angle}))\n",
+    "            steps.append(Point(x=r_final*sin(angle/360*tau), y=r_final*cos(angle/360*tau), z=z_final, b=tilt, c=angle))\n",
     "    \n",
     "    return steps\n",
     "\n",
@@ -87,45 +83,85 @@
     "    angle = i * 360\n",
     "    z = z_start + h * i\n",
     "\n",
-    "    trace.append(fc.Point(x=r, y=0, z=z, axes={'B':tilt,'C':angle}))\n",
+    "    trace.append(Point(x=r, y=0, z=z, b=tilt, c=angle))\n",
     "\n",
-    "angle_offset = fc.last_point(trace).axes['C']\n",
-    "z_offset = fc.last_point(trace).z\n",
+    "angle_offset = fci.last_point(trace).c\n",
+    "z_offset = fci.last_point(trace).z\n",
     "\n",
     "for i in range(1,arc_layers):\n",
     "    tilt = tilt_start + (tilt_end - tilt_start) * i / (arc_layers - 1)\n",
     "    r = r_start+r_tilt*(1-cos(tilt*tau/360))\n",
     "    z = z_offset+r_tilt*(sin(tilt*tau/360))\n",
     "    angle = i * 360 + angle_offset\n",
-    "    trace.append(fc.Point(x=r, y=0, z=z, axes={'B':-tilt,'C':angle}))\n",
+    "    trace.append(Point(x=r, y=0, z=z, b=-tilt, c=angle))\n",
     "\n",
-    "angle_offset = fc.last_point(trace).axes['C']\n",
-    "z_offset = fc.last_point(trace).z\n",
-    "r_offset = fc.last_point(trace).x\n",
+    "angle_offset = fci.last_point(trace).c\n",
+    "z_offset = fci.last_point(trace).z\n",
+    "r_offset = fci.last_point(trace).x\n",
     "\n",
     "for i in range(1,layers_tilted):\n",
     "    tilt = tilt_end\n",
     "    r = r_offset + d_tilted * i / (layers_tilted - 1) * (sin(tilt*tau/360))\n",
     "    z = z_offset + d_tilted * i / (layers_tilted - 1) * cos(tilt*tau/360)\n",
     "    angle = i * 360 + angle_offset\n",
-    "    trace.append(fc.Point(x=0, y=r, z=z, axes={'B':-tilt,'C':angle}))\n",
+    "    trace.append(Point(x=0, y=r, z=z, b=-tilt, c=angle))\n",
     "\n",
     "steps = vase_from_trace(trace, density)\n",
-    "steps.append(fc.last_point(trace))\n",
+    "steps.append(fci.last_point(trace))\n",
     "\n",
     "for step in steps:\n",
-    "    if type(step).__name__ == 'Point':\n",
+    "    if isinstance(step, fci.Point):\n",
     "        # color is a gradient from A=0 (blue) to A=90 (red)\n",
-    "        step.color = [((abs(step.axes['B']))/90), 0, 1-((abs(step.axes['B']))/90)]\n",
+    "        step.color = [((abs(step.b))/90), 0, 1-((abs(step.b))/90)]\n",
     "\n",
-    "fig = fc.transform(steps, 'fig', fc.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
+    "fig = fci.transform(steps, 'fig', fci.PlotControls(color_type='manual',style='tube', zoom=0.75), show_tips=False)\n",
     "fig.show()\n",
     "\n",
-    "gcode = fc.transform(steps,'gcode',gcode_controls)\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
     "print('first ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[:10]))\n",
     "print('')\n",
     "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
    ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": null,
+   "id": "9462651e",
+   "metadata": {},
+   "outputs": [],
+   "source": [
+    "# with and without 'verbose'\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
+    "    verbose = False,\n",
+    "    initialization_data=print_settings \n",
+    "    )\n",
+    "\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
+    "print('___\\nwith GcodeControls(verbose=False):')\n",
+    "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))\n",
+    "\n",
+    "gcode_controls = fci.GcodeControls(\n",
+    "    head_chain = head_chain,\n",
+    "    bed_chain = bed_chain,\n",
+    "    verbose = True,\n",
+    "    initialization_data=print_settings \n",
+    "    )\n",
+    "\n",
+    "gcode = fci.transform(steps,'gcode',gcode_controls)\n",
+    "print('\\n___\\nwith GcodeControls(verbose=True):')\n",
+    "print('final ten gcode lines:\\n' + '\\n'.join(gcode.split('\\n')[-10:]))"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": null,
+   "id": "aaf9ec1a",
+   "metadata": {},
+   "outputs": [],
+   "source": []
   }
  ],
  "metadata": {
```

## New files without old `infaxis` equivalent

- `lab/fullcontrol/infinaxis/_plot.py`: present
- `lab/fullcontrol/infinaxis/xyz_add_axes.py`: present

