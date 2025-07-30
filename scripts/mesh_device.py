# Adapted fixture from conftest.py in home
import ttnn 
import os 

def get_dispatch_core_type():
    # TODO: 11059 move dispatch_core_type to device_params when all tests are updated to not use WH_ARCH_YAML env flag
    dispatch_core_type = ttnn.device.DispatchCoreType.WORKER
    if ("WH_ARCH_YAML" in os.environ) and os.environ["WH_ARCH_YAML"] == "wormhole_b0_80_arch_eth_dispatch.yaml":
        dispatch_core_type = ttnn.device.DispatchCoreType.ETH
    return dispatch_core_type

def get_updated_device_params(device_params):
    dispatch_core_type = get_dispatch_core_type()
    new_device_params = device_params.copy()
    dispatch_core_axis = new_device_params.pop(
        "dispatch_core_axis",
        ttnn.DispatchCoreAxis.COL if os.environ["ARCH_NAME"] == "blackhole" else ttnn.DispatchCoreAxis.ROW,
    )
    dispatch_core_config = ttnn.DispatchCoreConfig(dispatch_core_type, dispatch_core_axis)
    new_device_params["dispatch_core_config"] = dispatch_core_config
    return new_device_params

def create_mesh_device(param, device_params):
    device_ids = ttnn.get_device_ids()

    if isinstance(param, tuple):
        grid_dims = param
        assert len(grid_dims) == 2
        num_devices_requested = grid_dims[0] * grid_dims[1]
        assert num_devices_requested <= len(device_ids)
        mesh_shape = ttnn.MeshShape(*grid_dims)
    else:
        num_devices_requested = min(param, len(device_ids))
        mesh_shape = ttnn.MeshShape(1, num_devices_requested)


    pci_ids = [ttnn.GetPCIeDeviceID(i) for i in device_ids[:num_devices_requested]]
    updated_device_params = get_updated_device_params(device_params)

    mesh_device = ttnn.open_mesh_device(mesh_shape=mesh_shape, **updated_device_params)

    return mesh_device, pci_ids