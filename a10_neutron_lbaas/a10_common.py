# Copyright 2015 A10 Networks

auto_dictionary = {
    "2.1": ("source_nat_auto", lambda x: int(x)),
    "3.0": ("auto", lambda x: x)
}


def _set_auto_parameter(vport, device_info):
    # import pdb
    # pdb.set_trace()
    api_ver = device_info.get("api_version", None)
    auto_tuple = auto_dictionary.get(api_ver, None)

    vport_key = None
    vport_transform = lambda x: x

    if auto_tuple:
        vport_key = auto_tuple[0]
        vport_transform = auto_tuple[1]

    if vport_key is not None:
        cfg_value = device_info.get("autosnat", False)
        vport[vport_key] = vport_transform(cfg_value)
