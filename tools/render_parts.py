"""Headless Blender renders of the 3DPLAM assembly.

Run:  blender --background --python tools/render_parts.py

STLs are millimetres. Blender's STL importer treats the raw numbers as
metres, so a 77 mm base arrives 77 m wide; every imported object is scaled
by 0.001 and the scale applied immediately, after which all coordinates in
this script are genuine metres (i.e. millimetres / 1000).

Only three renders are produced here, real photographs of the printed
device cover the hero shot, the per-part views, and the filter-support
comparison, so this script is limited to the views a camera cannot take:
an exploded stack and two cutaways (the sealing interface, and the
filter-support strand mesh).

Camera framing, the section cut plane, and the membrane's position are all
computed from the imported geometry's bounding boxes at render time (none
of it is a hardcoded coordinate), so the script keeps working if the CAD is
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
# Web-ready glTF of the same geometry, for the site's click-to-open 3D
# viewer. Exported from the identical scene each render is made from, so a
# part is the same colour and the same shape in both.
MODELS_OUT = os.path.join(ROOT, "site", "public", "models")
RES = 2000
MM = 0.001
SAMPLES = 256

BASE_STL = os.path.join(ROOT, "hardware", "stl", "base.stl")
FUNNEL_STL = os.path.join(ROOT, "hardware", "stl", "funnel.stl")
FILTER_SUPPORT_STL = os.path.join(
    ROOT, "hardware", "stl", "filter-support-strand-mesh.stl")
ASSEMBLY_STL = os.path.join(ROOT, "hardware", "assembly", "assembly.stl")

# One colour per part, applied in EVERY render, a reader who learns
# "yellow is the funnel" in the exploded view carries that into the
# section views without re-reading a caption. Do not give a part a
# different colour in one figure for local contrast; that is exactly the
# inconsistency this palette replaced (the base used to be slate-teal in
# the membrane-clamp figure and grey everywhere else).
#
# Values are scene-linear Principled BSDF base colours, and the scene
# renders with the Standard view transform, so displayed sRGB is roughly
# linear^(1/2.2), 0.42 linear reads as mid-to-dark grey on screen, 0.62
# as light grey. The site places these renders on a near-white card
# (--bg-2, #f6f7f9), so nothing may sit too close to white or the part
# loses its silhouette; 0.82 was tried originally and read as a pale
# blur, which is why the light-grey part stops at 0.62.
COLOR_BASE = (0.42, 0.42, 0.39, 1.0)            # the base (dark grey)
COLOR_FILTER_SUPPORT = (0.62, 0.62, 0.60, 1.0)  # the filter support (light grey)
COLOR_FUNNEL = (0.56, 0.43, 0.16, 1.0)          # the funnel (yellow ochre)
# The membrane has no CAD file and is not a printed part; it keeps the
# thesis figure's red (desaturated to terracotta) so it reads as the
# consumable passing through the joint, distinct from all three prints.
COLOR_MEMBRANE = (0.60, 0.18, 0.13, 1.0)        # the membrane (muted terracotta)

# Part name (as set by load_assembly_bodies) -> colour, so a multi-body
# scene can be coloured by lookup rather than by remembering which
# variable goes with which body.
PART_COLORS = {
    "base": COLOR_BASE,
    "filter-support": COLOR_FILTER_SUPPORT,
    "funnel": COLOR_FUNNEL,
}


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
    # Blender 5.2 defaults to the AgX view transform, which rolls off
    # highlights and desaturates strongly, it turned the intended muted
    # teal/ochre/terracotta of the membrane-clamp figure into washed-out
    # pastels, and likely made the original near-white plastic look even
    # paler than its base colour alone would. Standard renders the
    # material's base colour with predictable, non-filmic contrast, which
    # these technical/diagrammatic renders want more than photographic
    # highlight rolloff.
    scene.view_settings.view_transform = "Standard"
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


KEY_ENERGY = 30
KEY_DIST = 3.2  # metres, matches the "key" entry below


def lighting(center, fill_dir=None, fill_radius=None, fill_strength=3.0):
    """Three-point studio lighting aimed at `center` (a Vector), plus a
    soft white world for ambient fill. film_transparent hides the world
    from camera rays but it still contributes bounce light.

    A boolean cut leaves a flat face oriented straight at the camera; the
    generic three-point rig above (all placed metres away, effectively
    directional) barely grazes it, so a cut render reads as a dark band.
    Pass `fill_dir`/`fill_radius` (the camera's direction and the
    scene's own geometric radius) to add a light from near the viewer's
    position, close enough to actually illuminate that face.

    Its energy is *not* copied from the key light: at a much shorter
    distance, the same wattage massively overexposes the shot (this
    happened on the first attempt, irradiance falls off with the square
    of distance, so reusing a far light's power up close floods it).
    Instead it is derived from the key light's own irradiance at its
    distance, scaled to the new distance, times `fill_strength`.

    The world's ambient strength and the fill/rim energies are kept low
    relative to the key (roughly 4:1 key-to-fill) so that form is carried
    by shading gradients rather than washed flat, with the original
    near-white plastic and a strong flat ambient, mid-tones and shadow
    fell in too narrow a range to read as depth."""
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.05
    bpy.context.scene.world = world

    target = bpy.data.objects.new("light-target", None)
    target.location = center
    bpy.context.collection.objects.link(target)

    lights = [
        ("key", Vector((0.6, -0.8, 0.9)), KEY_DIST, KEY_ENERGY, 0.6),
        ("fill", Vector((-0.8, -0.4, 0.4)), 3.6, 8, 0.9),
        ("rim", Vector((0.0, 0.9, 0.6)), 3.4, 10, 0.7),
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
    (no material, callers assign one so multi-body scenes can colour
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


def radial_extent(obj, axis_xy, z_lo, z_hi):
    """Maximum XY distance from `axis_xy` among `obj`'s vertices whose
    world Z falls in [z_lo, z_hi], the true local radius at a given
    height band. The overall bounding box is no substitute here: the
    base's widest point is its bottom brim/legs, not its top connection,
    so `bbox_radius` would place the membrane-clamp crop in empty air."""
    mw = obj.matrix_world
    best = 0.0
    for v in obj.data.vertices:
        w = mw @ v.co
        if z_lo <= w.z <= z_hi:
            r = math.hypot(w.x - axis_xy.x, w.y - axis_xy.y)
            if r > best:
                best = r
    return best


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
    bodies, returning (base, filter_support, funnel): real objects at
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

    # Cross-check by size, not triangle count: the count depends on the
    # export resolution chosen in Onshape, the envelope does not.
    def dims_mm(o):
        lo, hi = world_bbox(o)
        d = (hi - lo) / MM
        return sorted((round(d.x, 1), round(d.y, 1), round(d.z, 1)))

    for o, name, expected in ((base_obj, "base", (38.7, 77.0, 77.0)),
                              (filter_obj, "filter support", (2.9, 37.3, 37.3)),
                              (funnel_obj, "funnel", (55.5, 71.8, 71.8))):
        got = dims_mm(o)
        assert all(abs(g - e) < 1.0 for g, e in zip(got, expected)), \
            f"expected {name} of about {expected} mm, got {got} mm"

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
    `radius` entirely inside the lens's field of view, computed from the
    lens's actual angle, not a guessed multiplier, so nothing at the
    frame edges gets clipped. TRACK_TO keeps `center` exactly in the
    middle of the frame regardless of `direction`, so a tilted or 3/4
    `direction` never throws the composition off-centre, only `radius`
    and `margin` control how much is visible. Returns the camera
    distance, for callers that want to place a light relative to it."""
    half_fov = math.atan((SENSOR_WIDTH / 2) / lens)
    dist = (radius * margin) / math.sin(half_fov)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = lens
    cam_data.sensor_width = SENSOR_WIDTH
    # Blender's default near-clip (0.1 m) silently clips the entire
    # subject out of a tight close-up: the membrane-clamp crop sits the
    # camera ~70 mm from its focus, inside that default, which produced a
    # fully transparent render with no error. 1 mm is safe at every scale
    # this script uses.
    cam_data.clip_start = mm(1)
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


def add_shadow_catcher(lo, hi, margin_factor=8.0):
    """A large plane at the lowest point of the scene (`lo.z`), marked as
    a Cycles shadow catcher so it renders *only* the soft contact shadow
    the geometry casts on it; the plane itself stays invisible. Combined
    with `film_transparent`, the shadowed pixels get partial alpha rather
    than none, so the shadow survives into the PNG and composites onto
    whatever background the page puts under it. Without this, a
    transparent-background render leaves objects looking like they float
    with no grounding."""
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    size = max(hi.x - lo.x, hi.y - lo.y) * margin_factor
    bpy.ops.mesh.primitive_plane_add(size=size, location=(cx, cy, lo.z))
    plane = bpy.context.active_object
    plane.name = "shadow-catcher"
    set_material(plane, matte_material("shadow-catcher-mat", (1, 1, 1, 1), roughness=0.9))
    plane.is_shadow_catcher = True
    return plane


def render(scene, name):
    os.makedirs(OUT, exist_ok=True)
    scene.render.filepath = os.path.join(OUT, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {name}.png")


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def decimate_for_web(obj, max_tris):
    """Reduce `obj` to roughly `max_tris` triangles for browser delivery.

    Two passes, cheapest first. Planar dissolve merges faces that are
    coplanar within a small angle, on meshes tessellated out of CAD it
    removes a large share of the triangles while changing the silhouette
    by nothing at all, because the removed edges were interior to flat
    regions. Only if that alone misses the budget does collapse
    decimation run, which does move vertices and so is kept as the
    fallback rather than the first move.

    Call this AFTER rendering: the render must use the full-resolution
    mesh, and both modifiers are applied destructively.
    """
    before = tri_count(obj)
    if before <= max_tris:
        print(f"    {obj.name}: {before:,} tris, under budget, untouched")
        return

    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(3.0)
    bpy.ops.object.modifier_apply(modifier="planar")
    after_planar = tri_count(obj)

    if after_planar > max_tris:
        mod = obj.modifiers.new("collapse", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = max_tris / after_planar
        bpy.ops.object.modifier_apply(modifier="collapse")
    after = tri_count(obj)
    print(f"    {obj.name}: {before:,} -> {after_planar:,} (planar) -> "
          f"{after:,} tris (budget {max_tris:,})")


def export_glb(name, objs, max_tris=60000):
    """Write `objs` to site/public/models/<name>.glb.

    Only the named objects are exported (no camera, no lights, no shadow
    catcher) because the viewer supplies its own. Materials come along,
    which is what keeps the 3D colours identical to the render's without
    a second palette defined in JavaScript.
    """
    os.makedirs(MODELS_OUT, exist_ok=True)
    for obj in objs:
        decimate_for_web(obj, max_tris)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    path = os.path.join(MODELS_OUT, f"{name}.glb")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        # glTF is Y-up; Blender is Z-up. Without this the model arrives in
        # three.js lying on its side.
        export_yup=True,
    )
    print(f"  exported {name}.glb ({os.path.getsize(path) / 1e6:.2f} MB)")


ISO = Vector((1.0, -1.0, 0.8))


def render_assembly_exploded():
    scene = reset()
    base_obj, filter_obj, funnel_obj = load_assembly_bodies()
    for obj in (base_obj, filter_obj, funnel_obj):
        set_material(obj, matte_material(f"plastic-{obj.name}", PART_COLORS[obj.name]))

    # Pull the middle and top parts apart along Z so the stacking order
    # (base, then filter support seated in it, then funnel on top) reads
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
    add_shadow_catcher(lo, hi)
    lighting(center)
    # Generous margin: nothing in an exploded view may touch the frame
    # edge, and the stack is tall relative to its footprint.
    frame_camera(center, radius, ISO, margin=1.3)
    render(scene, "assembly-exploded")
    export_glb("assembly-exploded", [base_obj, filter_obj, funnel_obj])


def render_membrane_clamp():
    scene = reset()
    base_obj, filter_obj, funnel_obj = load_assembly_bodies()
    membrane = add_membrane(filter_obj)

    # The device is axisymmetric and the cut below exposes a diametral
    # cross-section, so the sealing ring appears at the outer edges of
    # the cut face (X = axis ± seal_radius), not at the centre, the
    # previous version focused on the membrane's own bbox centre, which
    # is the central axis, and so framed the flat middle of the assembly
    # rather than the joint. Base is used (not the combined bbox) because
    # its footprint alone is already centred on the true device axis
    # (verified against the combined bbox, the two agree to sub-mm), and
    # it is available before any boolean cut touches the other bodies.
    base_lo, base_hi = world_bbox(base_obj)
    funnel_lo, funnel_hi = world_bbox(funnel_obj)
    axis = Vector(((base_lo.x + base_hi.x) / 2, (base_lo.y + base_hi.y) / 2, 0.0))

    # Base and funnel overlap in Z only across the band where they mate;
    # that band is where the clamping ridge sits.
    overlap_lo_z = max(base_lo.z, funnel_lo.z)
    overlap_hi_z = min(base_hi.z, funnel_hi.z)

    # The base's *local* radius at the mating band, not its overall bbox
    # radius, the widest point of the whole part is its bottom brim/legs,
    # well below this band, so using the bbox radius here would put the
    # crop centre in empty air.
    seal_radius = radial_extent(base_obj, axis, overlap_lo_z, overlap_hi_z)

    # Frame the *span* of the interface, from the membrane's own outer
    # edge (its inner boundary, where it starts crossing the ridge) out
    # past the ridge into the funnel wall (its outer boundary, for
    # context), centred on the midpoint of that span, not offset from
    # just one edge of it. An earlier version anchored the crop to the
    # ridge alone, which put the membrane's edge right at the frame's
    # left border with the funnel's open wall filling the rest.
    mem_lo, mem_hi = world_bbox(membrane)
    membrane_radius = (mem_hi.x - mem_lo.x) / 2
    inner_x = axis.x + membrane_radius
    outer_x = axis.x + seal_radius + mm(6)
    focus = Vector(((inner_x + outer_x) / 2, axis.y, (overlap_lo_z + overlap_hi_z) / 2))
    zoom_radius = mm(14)
    print(f"  membrane-clamp focus={focus}  seal_radius={seal_radius*1000:.1f}mm "
          f"zoom_radius={zoom_radius*1000:.1f}mm")

    for obj in (base_obj, filter_obj):
        cut_half(obj, axis, axis=1, keep_positive=True)
    set_material(base_obj, matte_material("base-mat", COLOR_BASE))
    set_material(filter_obj, matte_material("filter-mat", COLOR_FILTER_SUPPORT))
    cut_half(funnel_obj, axis, axis=1, keep_positive=True)
    set_material(funnel_obj, matte_material("funnel-mat", COLOR_FUNNEL))
    cut_half(membrane, axis, axis=1, keep_positive=True)
    set_material(membrane, matte_material("membrane-mat", COLOR_MEMBRANE, roughness=0.55))

    # Tight crop on the interface itself: the raised sealing edge, the
    # membrane crossing it, and the funnel's slope pressing down, all
    # large in frame.
    view_dir = Vector((0.0, -1.0, 0.15))
    frame_camera(focus, zoom_radius, view_dir, lens=100, margin=1.15)
    lighting(focus, fill_dir=view_dir, fill_radius=zoom_radius)
    render(scene, "membrane-clamp")
    # The render is a tight crop on the seal; the model is the whole cut
    # assembly, so a reader can scroll-zoom into that same joint and then
    # orbit around it, which is the point of making it interactive.
    export_glb("membrane-clamp", [base_obj, filter_obj, funnel_obj, membrane])


def render_filter_support_section():
    scene = reset()
    obj = import_and_prepare(FILTER_SUPPORT_STL)
    set_material(obj, matte_material("plastic-filter-support", COLOR_FILTER_SUPPORT))

    lo, hi = world_bbox(obj)
    center = bbox_center(lo, hi)
    cut_half(obj, center, axis=1, keep_positive=True)

    lo, hi = world_bbox(obj)
    center = bbox_center(lo, hi)
    radius = bbox_radius(lo, hi)

    # This render's framing already works well; margin=1.0 with the
    # FOV-based frame_camera reproduces its previous composition almost
    # exactly (verified against the prior render's camera distance), so
    # camera and crop are deliberately left untouched, only the material
    # and lighting below changed.
    add_shadow_catcher(lo, hi)
    lighting(center)
    frame_camera(center, radius, Vector((0.35, -1.0, 0.55)), lens=100, margin=1.0)
    render(scene, "filter-support-section")
    export_glb("filter-support-section", [obj])


JOBS = {
    "assembly-exploded": render_assembly_exploded,
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
