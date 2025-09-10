/**
 * Add folder browser to BC_LORA_DEFINE right-click menu
 */

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "BearCave.FolderBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            // Add to right-click menu
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(canvas, menuOptions) {
                getExtraMenuOptions?.apply(this, arguments);
                
                const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                if (projectPathWidget) {
                    menuOptions.unshift({
                        content: "📁 Set Project Path",
                        callback: () => {
                            if (app.FileFolderAPI) {
                                console.log("🐻 Bear Cave: Opening folder browser from menu");
                                app.FileFolderAPI.open(projectPathWidget, 'folder');
                            } else {
                                alert("FileBrowserAPI not available. Please install ComfyUI-FileBrowserAPI.");
                            }
                        }
                    }, null);
                }
            };
            
            console.log("🐻 Bear Cave: Right-click menu folder browser added to BC_LORA_DEFINE");
        }
    }
});

console.log("🐻 Bear Cave: Folder browser menu extension loaded");