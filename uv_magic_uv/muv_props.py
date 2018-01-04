# <pep8-80 compliant>

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "4.5"
__date__ = "19 Nov 2017"

import bpy
from bpy.props import (
    FloatProperty,
    EnumProperty,
    BoolProperty,
    FloatVectorProperty,
    StringProperty,
)
from mathutils import Vector


DEBUG = False


def get_loaded_texture_name(_, __):
    items = [(key, key, "") for key in bpy.data.images.keys()]
    items.append(("None", "None", ""))
    return items


# Properties used in this add-on.
class MUV_Properties():
    cpuv = None
    cpuv_obj = None
    cpuv_selseq = None
    transuv = None
    uvbb = None
    texlock = None
    texproj = None
    texwrap = None
    wsuv = None
    mvuv = None
    ovlpuv = None
    flpuv = None

    def __init__(self):
        self.cpuv = MUV_CPUVProps()
        self.cpuv_obj = MUV_CPUVProps()
        self.cpuv_selseq = MUV_CPUVSelSeqProps()
        self.transuv = MUV_TransUVProps()
        self.uvbb = MUV_UVBBProps()
        self.texlock = MUV_TexLockProps()
        self.texproj = MUV_TexProjProps()
        self.texwrap = MUV_TexWrapProps()
        self.wsuv = MUV_WSUVProps()
        self.mvuv = MUV_MVUVProps()
        self.ovlpuv = MUV_OVLPUVProps()
        self.flpuv = MUV_FLPUVProps()


class MUV_CPUVProps():
    src_uvs = []
    src_pin_uvs = []
    src_seams = []


class MUV_CPUVSelSeqProps():
    src_uvs = []
    src_pin_uvs = []
    src_seams = []


class MUV_TransUVProps():
    topology_copied = []


class MUV_TexProjProps():
    running = False


class MUV_UVBBProps():
    uv_info_ini = []
    ctrl_points_ini = []
    ctrl_points = []
    running = False


class MUV_TexLockProps():
    verts_orig = None
    intr_verts_orig = None
    intr_running = False


class MUV_TexWrapProps():
    src_face_index = -1


class MUV_WSUVProps():
    ref_sv = None
    ref_suv = None


class MUV_MVUVProps():
    running = False


class MUV_OVLPUVProps():
    running = False
    overlapped_uvs = []


class MUV_FLPUVProps():
    running = False
    flipped_uvs = []


def init_props(scene):
    scene.muv_props = MUV_Properties()

    # Align UV
    scene.muv_auv_transmission = BoolProperty(
        name="Transmission",
        description="Align linked UVs",
        default=False
    )
    scene.muv_auv_select = BoolProperty(
        name="Select",
        description="Select UVs which are aligned",
        default=False
    )
    scene.muv_auv_vertical = BoolProperty(
        name="Vert-Infl (Vertical)",
        description="Align vertical direction influenced "
                    "by mesh vertex proportion",
        default=False
    )
    scene.muv_auv_horizontal = BoolProperty(
        name="Vert-Infl (Horizontal)",
        description="Align horizontal direction influenced "
                    "by mesh vertex proportion",
        default=False
    )
    scene.muv_auv_location = EnumProperty(
        name="Location",
        description="Align location",
        items=[
            ('LEFT_TOP', "Left/Top", "Align to Left or Top"),
            ('MIDDLE', "Middle", "Align to middle"),
            ('RIGHT_BOTTOM', "Right/Bottom", "Align to Right or Bottom")
        ],
        default='MIDDLE'
    )

    # Smooth UV
    scene.muv_smuv_transmission = BoolProperty(
        name="Transmission",
        description="Smooth linked UVs",
        default=False
    )
    scene.muv_smuv_mesh_infl = FloatProperty(
        name="Mesh Influence",
        description="Influence rate of mesh vertex",
        min=0.0,
        max=1.0,
        default=0.0
    )
    scene.muv_smuv_select = BoolProperty(
        name="Select",
        description="Select UVs which are smoothed",
        default=False
    )

    # UV Bounding Box
    scene.muv_uvbb_uniform_scaling = BoolProperty(
        name="Uniform Scaling",
        description="Enable Uniform Scaling",
        default=False
    )

    # Pack UV
    scene.muv_packuv_allowable_center_deviation = FloatVectorProperty(
        name="Allowable Center Deviation",
        description="Allowable center deviation to judge same UV island",
        min=0.000001,
        max=0.1,
        default=(0.001, 0.001),
        size=2
    )
    scene.muv_packuv_allowable_size_deviation = FloatVectorProperty(
        name="Allowable Size Deviation",
        description="Allowable sizse deviation to judge same UV island",
        min=0.000001,
        max=0.1,
        default=(0.001, 0.001),
        size=2
    )

    # Move UV
    scene.muv_mvuv_enabled = BoolProperty(
        name="Move UV Enabled",
        description="Move UV is enabled",
        default=False
    )

    # UVW
    scene.muv_uvw_enabled = BoolProperty(
        name="UVW Enabled",
        description="UVW is enabled",
        default=False
    )

    # Texture Projection
    scene.muv_texproj_enabled = BoolProperty(
        name="Texture Projection Enabled",
        description="Texture Projection is enabled",
        default=False
    )
    scene.muv_texproj_tex_magnitude = FloatProperty(
        name="Magnitude",
        description="Texture Magnitude",
        default=0.5,
        min=0.0,
        max=100.0
    )
    scene.muv_texproj_tex_image = EnumProperty(
        name="Image",
        description="Texture Image",
        items=get_loaded_texture_name
    )
    scene.muv_texproj_tex_transparency = FloatProperty(
        name="Transparency",
        description="Texture Transparency",
        default=0.2,
        min=0.0,
        max=1.0
    )
    scene.muv_texproj_adjust_window = BoolProperty(
        name="Adjust Window",
        description="Size of renderered texture is fitted to window",
        default=True
    )
    scene.muv_texproj_apply_tex_aspect = BoolProperty(
        name="Texture Aspect Ratio",
        description="Apply Texture Aspect ratio to displayed texture",
        default=True
    )

    # Texture Lock
    scene.muv_texlock_enabled = BoolProperty(
        name="Texture Lock Enabled",
        description="Texture Lock is enabled",
        default=False
    )
    scene.muv_texlock_connect = BoolProperty(
        name="Connect UV",
        default=True
    )

    # World Scale UV
    scene.muv_wsuv_enabled = BoolProperty(
        name="World Scale UV Enabled",
        description="World Scale UV is enabled",
        default=False
    )
    scene.muv_wsuv_proportional_scaling = BoolProperty(
        name="Proportional Scaling",
        default=True
    )
    scene.muv_wsuv_scaling_factor = FloatProperty(
        name="Scaling Factor",
        default=1.0,
        max=1000.0,
        min=0.00001
    )
    scene.muv_wsuv_origin = EnumProperty(
        name="Origin",
        description="Aspect Origin",
        items=[
            ('CENTER', 'Center', 'Center'),
            ('LEFT_TOP', 'Left Top', 'Left Bottom'),
            ('LEFT_CENTER', 'Left Center', 'Left Center'),
            ('LEFT_BOTTOM', 'Left Bottom', 'Left Bottom'),
            ('CENTER_TOP', 'Center Top', 'Center Top'),
            ('CENTER_BOTTOM', 'Center Bottom', 'Center Bottom'),
            ('RIGHT_TOP', 'Right Top', 'Right Top'),
            ('RIGHT_CENTER', 'Right Center', 'Right Center'),
            ('RIGHT_BOTTOM', 'Right Bottom', 'Right Bottom')

        ],
        default="CENTER"
    )

    # Unwrap Constraint
    scene.muv_unwrapconst_enabled = BoolProperty(
        name="Unwrap Constraint Enabled",
        description="Unwrap Constraint is enabled",
        default=False
    )
    scene.muv_unwrapconst_u_const = BoolProperty(
        name="U-Constraint",
        description="Keep UV U-axis coordinate",
        default=False
    )
    scene.muv_unwrapconst_v_const = BoolProperty(
        name="V-Constraint",
        description="Keep UV V-axis coordinate",
        default=False
    )

    # Preserve UV Aspect
    scene.muv_preserve_uv_enabled = BoolProperty(
        name="Preserve UV Aspect Enabled",
        description="Preserve UV Aspect is enabled",
        default=False
    )
    scene.muv_preserve_uv_tex_image = EnumProperty(
        name="Image",
        description="Texture Image",
        items=get_loaded_texture_name
    )
    scene.muv_preserve_uv_origin = EnumProperty(
        name="Origin",
        description="Aspect Origin",
        items=[
            ('CENTER', 'Center', 'Center'),
            ('LEFT_TOP', 'Left Top', 'Left Bottom'),
            ('LEFT_CENTER', 'Left Center', 'Left Center'),
            ('LEFT_BOTTOM', 'Left Bottom', 'Left Bottom'),
            ('CENTER_TOP', 'Center Top', 'Center Top'),
            ('CENTER_BOTTOM', 'Center Bottom', 'Center Bottom'),
            ('RIGHT_TOP', 'Right Top', 'Right Top'),
            ('RIGHT_CENTER', 'Right Center', 'Right Center'),
            ('RIGHT_BOTTOM', 'Right Bottom', 'Right Bottom')

        ],
        default="CENTER"
    )

    # Flip/Rotate UV
    scene.muv_fliprot_enabled = BoolProperty(
        name="Flip/Rotate UV Enabled",
        description="Flip/Rotate UV is enabled",
        default=False
    )
    scene.muv_fliprot_seams = BoolProperty(
        name="Seams",
        description="Seams",
        default=True
    )

    # Mirror UV
    scene.muv_mirroruv_enabled = BoolProperty(
        name="Mirror UV Enabled",
        description="Mirror UV is enabled",
        default=False
    )
    scene.muv_mirroruv_axis = EnumProperty(
        items=[
            ('X', "X", "Mirror Along X axis"),
            ('Y', "Y", "Mirror Along Y axis"),
            ('Z', "Z", "Mirror Along Z axis")
        ],
        name="Axis",
        description="Mirror Axis",
        default='X'
    )

    # Copy/Paste UV
    scene.muv_cpuv_enabled = BoolProperty(
        name="Copy/Paste UV Enabled",
        description="Copy/Paste UV is enabled",
        default=False
    )
    scene.muv_cpuv_copy_seams = BoolProperty(
        name="Copy Seams",
        description="Copy Seams",
        default=True
    )
    scene.muv_cpuv_mode = EnumProperty(
        items=[
            ('DEFAULT', "Default", "Default Mode"),
            ('SEL_SEQ', "Selection Sequence", "Selection Sequence Mode")
        ],
        name="Copy/Paste UV Mode",
        description="Copy/Paste UV Mode",
        default='DEFAULT'
    )
    scene.muv_cpuv_strategy = EnumProperty(
        name="Strategy",
        description="Paste Strategy",
        items=[
            ('N_N', 'N:N', 'Number of faces must be equal to source'),
            ('N_M', 'N:M', 'Number of faces must not be equal to source')
        ],
        default='N_M'
    )

    # Transfer UV
    scene.muv_transuv_enabled = BoolProperty(
        name="Transfer UV Enabled",
        description="Transfer UV is enabled",
        default=False
    )
    scene.muv_transuv_invert_normals = BoolProperty(
        name="Invert Normals",
        description="Invert Normals",
        default=False
    )
    scene.muv_transuv_copy_seams = BoolProperty(
        name="Copy Seams",
        description="Copy Seams",
        default=True
    )

    def auvc_get_cursor_loc(self):
        from . import muv_common
        area, _, space = muv_common.get_space('IMAGE_EDITOR', 'WINDOW',
                                              'IMAGE_EDITOR')
        bd_size = muv_common.get_uvimg_editor_board_size(area)
        loc = space.cursor_location
        if bd_size[0] < 0.000001:
            cx = 0.0
        else:
            cx = loc[0] / bd_size[0]
        if bd_size[1] < 0.000001:
            cy = 0.0
        else:
            cy = loc[1] / bd_size[1]
        self['muv_auvc_cursor_loc'] = Vector((cx, cy))
        return self.get('muv_auvc_cursor_loc', (0.0, 0.0))

    def auvc_set_cursor_loc(self, value):
        from . import muv_common
        self['muv_auvc_cursor_loc'] = value
        area, _, space = muv_common.get_space('IMAGE_EDITOR', 'WINDOW',
                                              'IMAGE_EDITOR')
        bd_size = muv_common.get_uvimg_editor_board_size(area)
        cx = bd_size[0] * value[0]
        cy = bd_size[1] * value[1]
        space.cursor_location = Vector((cx, cy))

    scene.muv_auvc_cursor_loc = FloatVectorProperty(
        name="UV Cursor Location",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(0.000, 0.000),
        get=auvc_get_cursor_loc,
        set=auvc_set_cursor_loc
    )
    scene.muv_auvc_align_menu = EnumProperty(
        name="Align Method",
        description="Align Method",
        default='TEXTURE',
        items=[
            ('TEXTURE', "Texture", "Align to texture"),
            ('UV_ISLAND', "UV Island", "Align to UV island")
        ]
    )


def clear_props(scene):
    del scene.muv_props

    del scene.muv_auv_transmission
    del scene.muv_auv_select
    del scene.muv_auv_vertical
    del scene.muv_auv_horizontal

    del scene.muv_uvbb_uniform_scaling

    del scene.muv_texproj_tex_magnitude
    del scene.muv_texproj_tex_image
    del scene.muv_texproj_tex_transparency
    del scene.muv_texproj_adjust_window
    del scene.muv_texproj_apply_tex_aspect

    del scene.muv_auvc_cursor_loc
    del scene.muv_auvc_align_menu
