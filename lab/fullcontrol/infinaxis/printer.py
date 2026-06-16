from typing import Optional
from fullcontrol import Printer as BasePrinter
from fullcontrol import Point


class Printer(BasePrinter):
    'generic gcode Printer with 5-axis aspects added/modified'
    bed_center: Point = None
    post_ik_offset: Point = None
    head_chain: list = None
    bed_chain: list = None
    xyz_orientation: list = None
    inverse_time_feedrate: bool = None  # if true, F command will be output as inverse time feedrate (e.g. F2 for 30 seconds per move (1/2 minutes per move)) instead of speed (e.g. F300 for 300 mm/s). This is useful for some multiaxis machines that use inverse time feedrate to control speed.
    # the following two parameters (model_XYZ_gcode and distance_axis) may be useful for give more information for motion planning
    distance_axis: bool = None
    model_XYZ_gcode: bool = None
    verbose: bool = None

    def f_gcode(self, state):
        if self.speed_changed == True:
            return f'F{self.print_speed if state.extruder.on else self.travel_speed:.1f}'.rstrip('0').rstrip('.') + ' '
        else:
            return ''

    def gcode(self, state):
        'process this instance in a list of steps supplied by the designer to generate and return a line of gcode'
        # update all attributes of the tracking instance with the new instance (self)
        state.printer.update_from(self)
        if self.print_speed != None \
                or self.travel_speed != None:
            state.printer.speed_changed = True
        if self.new_command != None:
            state.printer.command_list = {**state.printer.command_list, **self.new_command}