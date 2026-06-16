from typing import Union

from fullcontrol import *
import fullcontrol.geometry as xyz_geom
# base fc namespace for user access; infinaxis replacements override matching names
from lab.fullcontrol.infinaxis.axis import Axis
from lab.fullcontrol.infinaxis.controls import GcodeControls
from lab.fullcontrol.infinaxis.point import Point, configure_point
from lab.fullcontrol.infinaxis.printer import Printer
from lab.fullcontrol.infinaxis.steps2gcode import gcode
from lab.fullcontrol.infinaxis.xyz_add_axes import xyz_add_axes


def transform(steps: list, result_type: str, controls: Union[GcodeControls, PlotControls] = None, show_tips: bool = True):
    '''transform a fullcontrol design (a list of function class instances) into result_type
    "gcode" or "plot". Optionally, GcodeControls or PlotControls can be passed to control 
    how the gcode or plot are generated.
    '''

    if result_type == 'gcode':
        if controls is None: controls = GcodeControls()
        return gcode(steps, controls)

    elif result_type == 'plot':
        from fullcontrol.visualize.steps2visualization import visualize
        if controls is None: controls = PlotControls()
        return visualize(steps, controls, show_tips)
    
    elif result_type == 'fig':
        from fullcontrol.visualize.plot_data import PlotData
        from fullcontrol.visualize.state import State as VisualizeState
        from lab.fullcontrol.infinaxis._plot import fig_plot

        if controls is None: controls = PlotControls()
        plot_controls = controls
        plot_controls.initialize()

        state = VisualizeState(steps, plot_controls)
        plot_data = PlotData(steps, state)
        for step in steps:
            step.visualize(state, plot_data, plot_controls)
        plot_data.cleanup()

        return fig_plot(plot_data, plot_controls)
