from typing import Optional
from pydantic import BaseModel
from fullcontrol import Point
from fullcontrol.combinations.gcode_and_visualize.classes import GcodeControls as BaseGcodeControls


class GcodeControls(BaseGcodeControls):
    'control to adjust the style and initialization of the gcode'
    bed_center: Optional[Point] = Point(x=0, y=0, z=0)
    head_chain: list = [] # Ordered list of axes in the head chain, used for the IK loop (back to front!)
    bed_chain: list = [] # Ordered list of axes in the bed chain, used for the IK loop (back to front!)
    xyz_orientation: Optional[list] = [1,1,1] # orientation of XYZ axes, 1 means the axis follows the right hand rule.
    inverse_time_feedrate: Optional[bool] = False  # if true, F command will be output as inverse time feedrate (e.g. F0.5 for 2 seconds per move) instead of speed (e.g. F300 for 300 mm/s). This is useful for some multiaxis machines that use inverse time feedrate to control speed. Note that when this is true, the print_speed and travel_speed attributes will be interpreted as seconds per move instead of mm/s. Also note that acceleration and deceleration will not be handled correctly when using inverse time feedrate, so it is recommended to use constant speed moves (G1 F...) when this is true.
    # the following three parameters (model_XYZ_gcode and distance_axis (_full)) may be useful for give more information for motion planning
    distance_axis: Optional[bool] = False
    distance_axis_full: Optional[bool] = False
    distance_axis_name: Optional[str] = "m" #assigned drive name in firmware
    model_XYZ_gcode: Optional[bool] = False  # if true, the gcode output will have a PQR axis which shows the the XYZ movement in the model (Alternative to distance_axis). Intended to be used with the system axis (XYZAC for instance) all be treated as rotational in firmware and the UVW being linear aixs for motion planning.
    model_XYZ_gcode_name: Optional[list[str]] = ["p","q","r"] #assigned drive names in firmware
    verbose: Optional[bool] = False
    f_round: Optional[bool] = True