######################################
# __init__.py for bc_lora module
######################################
# ComfyUI-BearCave LoRa-specific nodes
######################################

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import LoRa-specific nodes
try:
    from .bc_lora_conform import NODE_CLASS_MAPPINGS as CONFORM_NODES, NODE_DISPLAY_NAME_MAPPINGS as CONFORM_DISPLAY
    NODE_CLASS_MAPPINGS.update(CONFORM_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(CONFORM_DISPLAY)
    print("🐻 Bear Cave LoRa: Conform node loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave LoRa: Failed to load conform node: {e}")

# Import LoRa-specific nodes
try:
    from .bc_lora_define import NODE_CLASS_MAPPINGS as DEFINE_NODES, NODE_DISPLAY_NAME_MAPPINGS as DEFINE_DISPLAY
    NODE_CLASS_MAPPINGS.update(DEFINE_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(DEFINE_DISPLAY)
    print("🐻 Bear Cave LoRa: Define node loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave LoRa: Failed to load define node: {e}")

try:
    from .bc_lora_metadata import NODE_CLASS_MAPPINGS as LORA_META_NODES, NODE_DISPLAY_NAME_MAPPINGS as LORA_META_DISPLAY
    NODE_CLASS_MAPPINGS.update(LORA_META_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(LORA_META_DISPLAY)
    print("🐻 Bear Cave LoRa: LoRa metadata node loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave LoRa: Failed to load LoRa metadata node: {e}")

try:
    from .bc_lora_train import NODE_CLASS_MAPPINGS as TRAIN_NODES, NODE_DISPLAY_NAME_MAPPINGS as TRAIN_DISPLAY
    NODE_CLASS_MAPPINGS.update(TRAIN_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(TRAIN_DISPLAY)
    print("🐻 Bear Cave LoRa: Train node loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave LoRa: Failed to load train node: {e}")

total_lora_nodes = len(NODE_CLASS_MAPPINGS)
print(f"🐻 Bear Cave LoRa: Total LoRa nodes loaded: {total_lora_nodes}")

if total_lora_nodes == 0:
    print("🐻 Bear Cave LoRa: No LoRa nodes loaded! Check the errors above.")
