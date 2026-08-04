"""Headless Blender renders of the 3DPLAM assembly.

Run:  blender --background --python tools/render_parts.py

STLs are millimetres. Blender's STL importer treats the raw numbers as
metres, so a 77 mm base arrives 77 m wide; every imported object is scaled
by 0.001 and the scale applied immediately, after which all coordinates in
this script are genuine metres (i.e. millimetres / 1000).

Only four renders are produced here — real photographs of the printed
device cover the hero shot, the per-part views, and the filter-support
comparison, so this script is limited to the views a camera cannot take:
an exploded stack and two cutaway sections.

Camera framing, the section cut plane, and the membrane's position are all
computed from the imported geometry's bounding boxes at render time — none
of it is a hardcoded coordinate — so the script keeps working if the CAD is
revised.

Requires Blender 5.2 LTS. Two API notes for anyone touching this file:
  - `bpy.ops.wm.stl_import` is the current (post-2.93) STL importer.
  - `mesh.use_auto_smooth` was removed in Blender 4.1; shading now goes
    through `bpy.ops.object.shade_auto_smooth()`, which adds a "Smooth by
    Angle" modifier.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "public", "renders")
RES = 2000
MM = 0.001
SAMPLES = 256

BASE_STL = os.path.join(ROOT, "hardware", "stl", "base.stl")
FUNNEL_STL = os.path.join(ROOT, "hardware", "stl", "funnel.stl")
FILTER_SUPPORT_STL = os.path.join(
    ROOT, "hardware", "stl", "filter-support-strand-mesh.stl")
ASSEMBLY_STL = os.path.join(ROOT, "hardware", "assembly", "assembly.stl")

# Matte grey-white plastic, used for every part except where the
# membrane-clamp figure needs the three elements colour-coded.
COLOR_PLASTIC = (0.82, 0.82, 0.80, 1.0)
COLOR_FUNNEL_ACCENT = (0.55, 0.68, 0.80, 1.0)   # cool blue-grey
COLOR_MEMBRANE = (0.86, 0.55, 0.16, 1.0)        # warm amber, reads as paper


def mm(x):
    """Convert a literal millimetre value (for things this script adds,
    like the membrane or a crop radius) into scene units."""
    return x * MM


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.resolution_x = RES
    scene.render.resolution_y = RES
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
        print(f"  cycles device: GPU ({[d.name for d in prefs.devices if d.use]})")
    except Exception as exc:
        scene.cycles.device = "CPU"
        print(f"  cycles device: CPU (GPU setup failed: {exc})")
    return scene


def matte_material(name, color, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def set_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


KEY_ENERGY = 260
KEY_DIST = 3.2  # metres — matches the "key" entry below


def lighting(center, fill_dir=None, fill_radius=None, fill_strength=3.0):
    """Three-point studio lighting aimed at `center` (a Vector), plus a
    soft white world for ambient fill. film_transparent hides the world
    from camera rays but it still contributes bounce light.

    A boolean cut leaves a flat face oriented straight at the camera; the
    generic three-point rig above (all placed metres away, effectively
    directional) barely grazes it, so a cut render reads as a dark band.
    Pass `fill_dir`/`fill_radius` — the camera's direction and the
    scene's own geometric radius — to add a light from near the viewer's
    position, close enough to actually illuminate that face.

    Its energy is *not* copied from the key light: at a much shorter
    distance, the same wattage massively overexposes the shot (this
    happened on the first attempt — irradiance falls off with the square
    of distance, so reusing a far light's power up close floods it).
    Instead it is derived from the key light's own irradiance at its
    distance, scaled to the new distance, times `fill_strength`."""
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    bpy.context.scene.world = world

    target = bpy.data.objects.new("light-target", None)
    target.location = center
    bpy.context.collection.objects.link(target)

    lights = [
        ("key", Vector((0.6, -0.8, 0.9)), KEY_DIST, KEY_ENERGY, 0.6),
        ("fill", Vector((-0.8, -0.4, 0.4)), 3.6, 90, 0.9),
        ("rim", Vector((0.0, 0.9, 0.6)), 3.4, 130, 0.7),
    ]
    if fill_dir is not None:
        dist = max(fill_radius * 2.5, 0.05)
        energy = KEY_ENERGY * (dist / KEY_DIST) ** 2 * fill_strength
        size = fill_radius * 0.6
        lights.append(("cut-fill", fill_dir, dist, energy, size))
        print(f"  cut-fill light: dist={dist:.4f} energy={energy:.3f} size={size:.4f}")

    for name, direction, dist, energy, size in lights:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = energy
        light.size = max(size, 0.01)
        obj = bpy.data.objects.new(name, light)
        obj.location = center + direction.normalized() * dist
        bpy.context.collection.objects.link(obj)
        track = obj.constraints.new("TRACK_TO")
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"
        track.target = target


def import_and_prepare(path):
    """Import an STL, fix its units, shade it, return the bare object
    (no material — callers assign one so multi-body scenes can colour
    parts differently)."""
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.abspath(path))
    obj = (set(bpy.data.objects) - before).pop()
    obj.scale = (MM, MM, MM)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    return obj


def world_bbox(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def combined_bbox(objs):
    mins, maxs = zip(*(world_bbox(o) for o in objs))
    lo = Vector((min(v.x for v in mins), min(v.y for v in mins), min(v.z for v in mins)))
    hi = Vector((max(v.x for v in maxs), max(v.y for v in maxs), max(v.z for v in maxs)))
    return lo, hi


def bbox_center(lo, hi):
    return (lo + hi) / 2


def bbox_radius(lo, hi):
    """Half the bounding box's diagonal: a true bounding-sphere radius.
    Unlike `max(dimensions)`, a sphere of this radius is guaranteed to
    contain the whole box from *any* viewing direction, which matters for
    the 3/4 and tilted views used throughout this script."""
    return (hi - lo).length / 2


def load_assembly_bodies():
    """Import the reference assembly and split it into its three loose
    bodies, returning (base, filter_support, funnel) — real objects at
    their true assembled positions, identified by stacking order (base is
    lowest, filter support nests just above it inside the base, funnel
    spans highest) and cross-checked by triangle count so a mislabel
    fails loudly instead of silently producing a wrong picture."""
    obj = import_and_prepare(ASSEMBLY_STL)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    pieces = list(bpy.data.objects)
    assert len(pieces) == 3, f"expected 3 loose bodies in assembly.stl, got {len(pieces)}"

    def centroid_z(o):
        lo, hi = world_bbox(o)
        return (lo.z + hi.z) / 2

    pieces.sort(key=centroid_z)
    base_obj, filter_obj, funnel_obj = pieces

    n_base = len(base_obj.data.polygons)
    n_filter = len(filter_obj.data.polygons)
    n_funnel = len(funnel_obj.data.polygons)
    assert n_base > 300000, f"expected base to be the ~361k-tri body, got {n_base}"
    assert 9500 < n_filter < 12000, f"expected filter support ~10656 tri, got {n_filter}"
    assert 7500 < n_funnel < 9800, f"expected funnel ~9216 tri, got {n_funnel}"

    base_obj.name, filter_obj.name, funnel_obj.name = "base", "filter-support", "funnel"
    return base_obj, filter_obj, funnel_obj


def add_membrane(filter_obj, thickness_mm=0.35, margin_mm=0.0):
    """A thin cylinder standing in for the 0.45 um membrane, which has no
    CAD file. Sized to the filter support's footprint and placed on its
    top face, matching where the assembly instructions say the membrane
    is placed."""
    lo, hi = world_bbox(filter_obj)
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    top_z = hi.z
    radius = max(hi.x - lo.x, hi.y - lo.y) / 2 + mm(margin_mm)
    thickness = mm(thickness_mm)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=thickness, location=(cx, cy, top_z + thickness / 2))
    membrane = bpy.context.active_object
    membrane.name = "membrane"
    bpy.ops.object.shade_smooth()
    return membrane


def cut_half(obj, center, axis=1, keep_positive=True):
    """Boolean-difference away the half of `obj` on the removed side of
    `center[axis]` along `axis` (0=X, 1=Y, 2=Z), leaving the other half
    with a flat cross-section at that plane."""
    size = max(obj.dimensions) * 6 + mm(5)
    bpy.ops.mesh.primitive_cube_add(size=size)
    cutter = bpy.context.active_object
    cutter.location = Vector(center)
    offset = size / 2
    cutter.location[axis] += -offset if keep_positive else offset
    mod = obj.modifiers.new("section", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="section")
    bpy.data.objects.remove(cutter, do_unlink=True)


SENSOR_WIDTH = 36.0  # mm, Blender's default camera sensor width


def frame_camera(center, radius, direction, lens=85, margin=1.15):
    """Place a tracked camera looking at `center` from `direction` (need
    not be normalized), at the closest distance that keeps a sphere of
    `radius` entirely inside the lens's field of view — computed from the
    lens's actual angle, not a guessed multiplier, so nothing at the
    frame edges gets clipped. TRACK_TO keeps `center` exactly in the
    middle of the frame regardless of `direction`, so a tilted or 3/4
    `direction` never throws the composition off-centre — only `radius`
    and `margin` control how much is visible. Returns the camera
    distance, for callers that want to place a light relative to it."""
    half_fov = math.atan((SENSOR_WIDTH / 2) / lens)
    dist = (radius * margin) / math.sin(half_fov)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = lens
    cam_data.sensor_width = SENSOR_WIDTH
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = Vector(center) + direction.normalized() * dist
    track = cam.constraints.new("TRACK_TO")
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    empty = bpy.data.objects.new("cam-target", None)
    empty.location = center
    bpy.context.collection.objects.link(empty)
    track.target = empty
    bpy.context.scene.camera = cam
    return dist


def render(scene, name):
    os.makedirs(OUT, exist_ok=True)
    scene.render.filepath = os.path.join(OUT, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {name}.png")


ISO = Vector((1.0, -1.0, 0.8))


def render_assembly_exploded():
    scene = reset()
    base_obj, filter_obj, funnel_obj = load_assembly_bodies()
    for obj in (base_obj, filter_obj, funnel_obj):
        set_material(obj, matte_material(f"plastic-{obj.name}", COLOR_PLASTIC))

    # Pull the middle and top parts apart along Z so the stacking order —
    # base, then filter support seated in it, then funnel on top — reads
    # clearly. Gaps are chosen empirically for legibility, not to scale.
    gap_base_to_filter = mm(26)
    gap_filter_to_funnel = mm(34)
    filter_obj.location.z += gap_base_to_filter
    funnel_obj.location.z += gap_base_to_filter + gap_filter_to_funnel
    bpy.context.view_layer.update()

    lo, hi = combined_bbox([base_obj, filter_obj, funnel_obj])
    center = bbox_center(lo, hi)
    radius = bbox_radius(lo, hi)
    print(f"  exploded bbox lo={lo} hi={hi} center={center} radius={radius}")
    lighting(center)
    # Generous margin: nothing in an exploded view may touch the frame
    # edge, and the stack is tall relative to its footprint.
    frame_camera(center, radius, ISO, margin=1.3)
    render(scene, "assembly-exploded")


def render_assembly_section():
    scene = reset()
    base_obj, filter_obj, funnel_obj = load_assembly_bodies()
    membrane = add_membrane(filter_obj)

    lo, hi = combined_bbox([base_obj, filter_obj, funnel_obj])
    center = bbox_center(lo, hi)
    radius = bbox_radius(lo, hi)

    for obj in (base_obj, filter_obj, funnel_obj):
        cut_half(obj, center, axis=1, keep_positive=True)
        set_material(obj, matte_material(f"plastic-{obj.name}", COLOR_PLASTIC))
    cut_half(membrane, center, axis=1, keep_positive=True)
    set_material(membrane, matte_material("membrane-mat", COLOR_MEMBRANE, roughness=0.6))

    # Camera sits on the removed (-Y) side, looking into the exposed cut
    # face, with a slight downward tilt for a natural elevated view. The
    # cut face is oriented straight at this camera, so it needs its own
    # light (see `lighting`) rather than relying on the generic rig.
    view_dir = Vector((0.0, -1.0, 0.12))
    frame_camera(center, radius, view_dir, margin=1.2)
    lighting(center, fill_dir=view_dir, fill_radius=radius)
    render(scene, "assembly-section")


def render_membrane_clamp():
    scene = reset()
    base_obj, filter_obj, funnel_obj = load_assembly_bodies()
    membrane = add_membrane(filter_obj)

    # Focus point computed *before* any boolean cut touches the membrane —
    # read this after cutting it and the query lands on the just-cut,
    # about-to-be-halved mesh mid-operation, which is not the point we
    # want the camera aimed at.
    mlo, mhi = world_bbox(membrane)
    focus = bbox_center(mlo, mhi)
    print(f"  membrane-clamp focus={focus}  (membrane bbox {mlo}..{mhi})")

    lo, hi = combined_bbox([base_obj, filter_obj, funnel_obj])
    center = bbox_center(lo, hi)
    focus.y = center.y

    for obj in (base_obj, filter_obj):
        cut_half(obj, center, axis=1, keep_positive=True)
        set_material(obj, matte_material(f"plastic-{obj.name}", COLOR_PLASTIC))
    cut_half(funnel_obj, center, axis=1, keep_positive=True)
    set_material(funnel_obj, matte_material("funnel-mat", COLOR_FUNNEL_ACCENT))
    cut_half(membrane, center, axis=1, keep_positive=True)
    set_material(membrane, matte_material("membrane-mat", COLOR_MEMBRANE, roughness=0.6))

    # Zoom on the interface: centred on the membrane, wide enough to show
    # the base's raised ridge and the funnel's mating slope closing over
    # it (roughly 30 mm of radial extent), without pulling back to the
    # whole assembly.
    zoom_radius = mm(28)
    view_dir = Vector((0.0, -1.0, 0.15))
    frame_camera(focus, zoom_radius, view_dir, lens=100, margin=1.15)
    lighting(focus, fill_dir=view_dir, fill_radius=zoom_radius)
    render(scene, "membrane-clamp")


def render_filter_support_section():
    scene = reset()
    obj = import_and_prepare(FILTER_SUPPORT_STL)
    set_material(obj, matte_material("plastic-filter-support", COLOR_PLASTIC))

    lo, hi = world_bbox(obj)
    center = bbox_center(lo, hi)
    cut_half(obj, center, axis=1, keep_positive=True)

    lo, hi = world_bbox(obj)
    center = bbox_center(lo, hi)
    radius = bbox_radius(lo, hi)

    # This render already works well; margin=1.0 with the new FOV-based
    # frame_camera reproduces its previous framing almost exactly
    # (verified against the prior render's camera distance), so it is
    # deliberately left otherwise untouched.
    lighting(center)
    frame_camera(center, radius, Vector((0.35, -1.0, 0.55)), lens=100, margin=1.0)
    render(scene, "filter-support-section")


JOBS = {
    "assembly-exploded": render_assembly_exploded,
    "assembly-section": render_assembly_section,
    "membrane-clamp": render_membrane_clamp,
    "filter-support-section": render_filter_support_section,
}


def main():
    # `blender --background --python tools/render_parts.py -- NAME [NAME ...]`
    # renders only the named job(s), for fast iteration; with no names
    # after `--` (or no `--` at all) it renders everything.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for name in (args or list(JOBS)):
        JOBS[name]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
