/**
 * Handle button clicks for BC_LORA_DEFINE browse button
 */

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "BearCave.ButtonHandler",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Find the browse button and add click handler
                setTimeout(() => {
                    const browseButton = this.widgets.find(w => w.name === "browse_button");
                    const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                    
                    if (browseButton && projectPathWidget) {
                        browseButton.callback = () => {
                            if (app.FileFolderAPI) {
                                app.FileFolderAPI.open(projectPathWidget, 'folder');
                            } else {
                                alert("FileBrowserAPI not available. Please install ComfyUI-FileBrowserAPI.");
                            }
                        };
                        console.log("🐻 Bear Cave: Button handler attached");
                    }
                }, 100);
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave: Button handler loaded");