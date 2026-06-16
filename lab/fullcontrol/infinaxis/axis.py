from typing import Optional
from pydantic import BaseModel
from fullcontrol import Point

class Axis(BaseModel):
    name: Optional[str] = None # Used for the output gcode. And sets type if type not given
    type: Optional[str] = None # 'A', 'B', 'C', 'X', 'Y', 'Z'
    active: float = 0 # current position (for rotational axes, the angle of rotation in degrees. for linear axes, the position in mm.)
    orientation: float = 1 # 1 or -1, 1 means the axis follows mathematical convention (either positive/counterclockwise rotation or fits the right hand rule for linear axes)
    offset: Optional[Point] = None # the offset in mm in x,y,z from the previous axis in the chain.

    def __init__(self, **data):
        super().__init__(**data)

        if self.name is not None and self.name.upper() in ["X", "Y", "Z"]:
            raise ValueError('Axis.name cannot be "X", "Y", or "Z"; use Axis.type for linear kinematics with a different name')

        if self.type is None:
            if self.name is not None and self.name in ["A", "B", "C"]:
                self.type = self.name
            else:
                raise ValueError("Cannot set axis type based on name")
            
        if self.offset is None:
            self.offset = Point(x=0, y=0, z=0)
