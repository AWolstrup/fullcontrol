import numpy as np
import plotly.graph_objects as go

from fullcontrol.visualize.plotly import generate_mesh
from fullcontrol.visualize.tube_mesh import CylindersMesh, FlowTubeMesh


def generate_single_path_vase_lod_surface_arrays(
    path,
    center_xy=None,
    points_per_turn: int = 128,
    turn_stride: int = 2,
    color_mode: str = "none",
):
    points = np.asarray([path.xvals, path.yvals, path.zvals], dtype=np.float32).T

    if len(points) < 4:
        return None, None, None, None

    good = np.ones(len(points), dtype=bool)
    dups = np.all(np.diff(points, axis=0) == 0, axis=1)
    good[1:] = ~dups
    points = points[good]

    if len(points) < 4:
        return None, None, None, None

    source_color_scalar = None

    if color_mode == "path":
        if getattr(path, "colors", None) is not None and len(path.colors) > 0:
            colors_arr = np.asarray(path.colors, dtype=np.float32)

            if len(colors_arr) == len(good):
                colors_arr = colors_arr[good]

            if len(colors_arr) == len(points):
                source_color_scalar = (
                    0.299 * colors_arr[:, 0]
                    + 0.587 * colors_arr[:, 1]
                    + 0.114 * colors_arr[:, 2]
                ).astype(np.float32)

    if center_xy is None:
        cx = np.float32(0.5 * (np.min(points[:, 0]) + np.max(points[:, 0])))
        cy = np.float32(0.5 * (np.min(points[:, 1]) + np.max(points[:, 1])))
    else:
        cx, cy = center_xy

    theta = np.unwrap(np.arctan2(points[:, 1] - cy, points[:, 0] - cx)).astype(np.float32)

    if theta[-1] < theta[0]:
        theta = -theta

    turn_coord = ((theta - theta[0]) / np.float32(2.0 * np.pi)).astype(np.float32)

    monotonic_good = np.concatenate([[True], np.diff(turn_coord) > 1e-10])
    turn_coord = turn_coord[monotonic_good]
    points = points[monotonic_good]

    if source_color_scalar is not None:
        source_color_scalar = source_color_scalar[monotonic_good]

    if len(points) < 4:
        return None, None, None, None

    first_complete_turn = int(np.ceil(turn_coord[0]))
    last_complete_turn = int(np.floor(turn_coord[-1])) - 1

    if last_complete_turn <= first_complete_turn:
        return None, None, None, None

    all_turns = np.arange(first_complete_turn, last_complete_turn + 1, dtype=np.float32)

    selected_turns = all_turns[::max(1, int(turn_stride))]

    if selected_turns[-1] != all_turns[-1]:
        selected_turns = np.append(selected_turns, all_turns[-1]).astype(np.float32)

    if len(selected_turns) < 2:
        return None, None, None, None

    phases = np.linspace(
        0.0,
        1.0,
        points_per_turn + 1,
        endpoint=True,
        dtype=np.float32,
    )

    targets = selected_turns[:, None] + phases[None, :]
    targets_flat = targets.ravel()

    x_grid = np.interp(targets_flat, turn_coord, points[:, 0]).reshape(targets.shape).astype(np.float32)
    y_grid = np.interp(targets_flat, turn_coord, points[:, 1]).reshape(targets.shape).astype(np.float32)
    z_grid = np.interp(targets_flat, turn_coord, points[:, 2]).reshape(targets.shape).astype(np.float32)

    if color_mode == "path" and source_color_scalar is not None:
        color_grid = np.interp(
            targets_flat,
            turn_coord,
            source_color_scalar,
        ).reshape(targets.shape).astype(np.float32)

    elif color_mode == "height":
        color_grid = z_grid

    elif color_mode == "turn":
        color_grid = targets.astype(np.float32)

    else:
        color_grid = np.zeros_like(z_grid, dtype=np.float32)

    return x_grid, y_grid, z_grid, color_grid


def generate_single_path_vase_lod_surface_trace(
    path,
    center_xy=None,
    points_per_turn: int = 128,
    turn_stride: int = 2,
    color_mode: str = "none",
    colorscale="Viridis",
    showscale: bool = False,
    opacity: float = 1.0,
):
    x, y, z, surfacecolor = generate_single_path_vase_lod_surface_arrays(
        path,
        center_xy=center_xy,
        points_per_turn=points_per_turn,
        turn_stride=turn_stride,
        color_mode=color_mode,
    )

    if x is None:
        return None

    return go.Surface(
        x=x,
        y=y,
        z=z,
        surfacecolor=surfacecolor,
        colorscale=colorscale,
        showscale=showscale,
        opacity=opacity,
        hoverinfo="skip",
        contours=dict(
            x=dict(show=False),
            y=dict(show=False),
            z=dict(show=False),
        ),
        showlegend=False,
    )


def fig_plot(data, controls):
    fig = go.Figure()

    if controls.tube_type is not None:
        Mesh = {"flow": FlowTubeMesh, "cylinders": CylindersMesh}[controls.tube_type]
    else:
        Mesh = FlowTubeMesh

    max_width = 0

    for path in data.paths:
        colors_now = [f"rgb({color[0]*255:.2f}, {color[1]*255:.2f}, {color[2]*255:.2f})" for color in path.colors]
        linewidth_now = controls.line_width * 2 if path.extruder.on == True else controls.line_width * 0.5

        if path.widths:
            max_width = max(max_width, max(path.widths))

        if path.extruder.on and controls.style == "vase_surface":
            surface_trace = generate_single_path_vase_lod_surface_trace(
                path,
                points_per_turn=96,
                turn_stride=3,
                color_mode="height",
                colorscale="viridis",
                showscale=False,
                opacity=1.0,
            )

            if surface_trace is not None:
                fig.add_trace(surface_trace)

        elif path.extruder.on and controls.style == "tube":
            sides, rounding_strength, flat_sides = controls.tube_sides, 0.4, False
            mesh = generate_mesh(path, linewidth_now, Mesh, sides, rounding_strength, flat_sides, colors_now)
            fig.add_trace(mesh.to_Mesh3d(colors=colors_now))

        elif not controls.hide_travel or path.extruder.on:
            fig.add_trace(go.Scatter3d(
                mode="lines",
                x=path.xvals,
                y=path.yvals,
                z=path.zvals,
                showlegend=False,
                line=dict(width=linewidth_now, color=colors_now),
            ))

    bounding_box_size = max(
        data.bounding_box.maxx - data.bounding_box.minx,
        data.bounding_box.maxy - data.bounding_box.miny,
        data.bounding_box.maxz - min(0, data.bounding_box.minz),
    )
    bounding_box_size += 0.002
    bounding_box_size += max_width

    annotations_pts = []
    annotations = []
    if controls.hide_annotations == False and not controls.neat_for_publishing:
        for annotation in data.annotations:
            x, y, z = (annotation[axis] for axis in "xyz")
            annotations_pts.append([x, y, z])
            annotations.append(dict(
                showarrow=False,
                x=x,
                y=y,
                z=z,
                text=annotation["label"],
                yshift=10,
            ))
        xs, ys, zs = zip(*annotations_pts) if annotations_pts else [[]] * 3
        fig.add_trace(go.Scatter3d(mode="markers", x=xs, y=ys, z=zs, showlegend=False, marker=dict(size=2, color="red")))

        midx, midy, midz = (getattr(data.bounding_box, f"mid{axis}") for axis in "xyz")
        offset = 0.001
        offset_both_sides = 2 * offset
        for (x, y, z) in annotations_pts:
            if x < midx - bounding_box_size / 2 + offset:
                bounding_box_size = 2 * (midx - x) + offset_both_sides
            if x > midx + bounding_box_size / 2 - offset:
                bounding_box_size = 2 * (x - midx) + offset_both_sides
            if y < midy - bounding_box_size / 2 + offset:
                bounding_box_size = 2 * (midy - y) + offset_both_sides
            if y > midy + bounding_box_size / 2 - offset:
                bounding_box_size = 2 * (y - midy) + offset_both_sides
            if z < midz - bounding_box_size / 2 + offset:
                bounding_box_size = 2 * (midz - z) + offset_both_sides
            if z > midz + bounding_box_size / 2 - offset:
                bounding_box_size = 2 * (z - midz) + offset_both_sides

    relative_centre_z = 0.5 * data.bounding_box.rangez / bounding_box_size
    camera_centre_z = -0.5 + relative_centre_z
    camera = dict(
        eye=dict(x=-0.5 / controls.zoom, y=-1 / controls.zoom, z=-0.5 + 0.5 / controls.zoom),
        center=dict(x=0, y=0, z=camera_centre_z),
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="black",
        scene_aspectmode="cube",
        scene=dict(
            annotations=annotations,
            xaxis=dict(
                backgroundcolor="black",
                nticks=10,
                range=[data.bounding_box.midx - bounding_box_size / 2, data.bounding_box.midx + bounding_box_size / 2],
            ),
            yaxis=dict(
                backgroundcolor="black",
                nticks=10,
                range=[data.bounding_box.midy - bounding_box_size / 2, data.bounding_box.midy + bounding_box_size / 2],
            ),
            zaxis=dict(backgroundcolor="black", nticks=10, range=[min(0, data.bounding_box.minz), bounding_box_size]),
        ),
        scene_camera=camera,
        width=800,
        height=500,
        margin=dict(l=10, r=10, b=10, t=10, pad=4),
    )
    if controls.hide_axes or controls.neat_for_publishing:
        for axis in ["xaxis", "yaxis", "zaxis"]:
            fig.update_layout(scene={axis: dict(showgrid=False, zeroline=False, visible=False)})
    if controls.neat_for_publishing:
        fig.update_layout(width=500, height=500)

    return fig
