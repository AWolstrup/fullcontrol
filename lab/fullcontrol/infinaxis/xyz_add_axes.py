from typing import Union

from fullcontrol import Point as XYZPoint

from lab.fullcontrol.infinaxis.point import Point


def xyz_add_axes(xyz_geometry: Union[XYZPoint, list], point_class=Point) -> Union[Point, list]:
    'convert xyz geometry points to infinaxis Points'
    if isinstance(xyz_geometry, XYZPoint):
        pt = point_class()
        pt.update_from(xyz_geometry)
        return pt

    geometry_new = []
    for step in xyz_geometry:
        if isinstance(step, XYZPoint):
            pt = point_class()
            pt.update_from(step)
            geometry_new.append(pt)
        else:
            geometry_new.append(step)
    return geometry_new
