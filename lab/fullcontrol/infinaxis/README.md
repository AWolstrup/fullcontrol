# Infinaxis Scope

`infinaxis` is currently set up for systems with normal XYZ linear axes, plus rotational axes after those linear axes at the end of the kinematic chain.

The inverse kinematics are calculated on that basis. This is useful because it explicitly works through nozzle offset from the rotation axes and part movement caused by rotation. The part-movement case is especially awkward: the effective offset depends on the exact current position within the part (distance from rotation axis), so it changes continuously as the toolpath moves.

Tutorial notebooks demonstrate how infinaxis works, and can be found [here](https://github.com/FullControlXYZ/fullcontrol/tree/master/tutorials/README.md)