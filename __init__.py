###################################
# __init__.py
###################################
# TORTU root package entry point for ComfyUI.
#
# This file re-exports NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
# from our subpackage so ComfyUI can register the nodes.
###################################

import os

from .nodes import (
    NODE_CLASS_MAPPINGS as _BC_NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as _BC_NODE_DISPLAY_NAME_MAPPINGS,
)

NODE_CLASS_MAPPINGS = dict(_BC_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS = dict(_BC_NODE_DISPLAY_NAME_MAPPINGS)

# Tell ComfyUI where to find our web extensions
WEB_DIRECTORY = "./web"

print(f"✅ TORTU: registered {len(NODE_CLASS_MAPPINGS)} nodes.")
print(f"✅ TORTU: web directory set to {WEB_DIRECTORY}")