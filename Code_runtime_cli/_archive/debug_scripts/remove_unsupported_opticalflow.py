node = op("/mosheng_project/01_camera_motion_mask/opticalflow_motion")
if node is not None:
    node.destroy()
    print("Removed unsupported opticalflow_motion node.")
else:
    print("No opticalflow_motion node found; already clean.")
