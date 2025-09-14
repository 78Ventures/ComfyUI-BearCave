######################################
# __init__.py for bc_fileman module
######################################
# ComfyUI-TORTU File Management nodes
######################################

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import file management nodes from bc_fileman.py
try:
    from .bc_fileman import NODE_CLASS_MAPPINGS as FILEMAN_NODES, NODE_DISPLAY_NAME_MAPPINGS as FILEMAN_DISPLAY
    NODE_CLASS_MAPPINGS.update(FILEMAN_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(FILEMAN_DISPLAY)
    print("🐢 TORTU FileMan: BC file management nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU FileMan: Failed to load BC file management nodes: {e}")

# Import IF Load Images node from IF_Load_Images_Node.py
try:
    from .IF_Load_Images_Node import NODE_CLASS_MAPPINGS as IF_NODES, NODE_DISPLAY_NAME_MAPPINGS as IF_DISPLAY
    NODE_CLASS_MAPPINGS.update(IF_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(IF_DISPLAY)
    print("🐢 TORTU FileMan: IF Load Images node loaded successfully")
except Exception as e:
    print(f"🐢 TORTU FileMan: Failed to load IF Load Images node: {e}")

total_fileman_nodes = len(NODE_CLASS_MAPPINGS)
print(f"🐢 TORTU FileMan: Total file management nodes loaded: {total_fileman_nodes}")

if total_fileman_nodes == 0:
    print("🐢 TORTU FileMan: No file management nodes loaded! Check the errors above.")
