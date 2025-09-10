/**
 * Bear Cave BC_LORA_DEFINE File Browser Integration
 * Uses ComfyUI-FileBrowserAPI to add folder browsing to project_base_path
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading FileBrowserAPI integration...");

app.registerExtension({
    name: "BearCave.BC_LORA_DEFINE.FileBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Adding FileBrowserAPI to BC_LORA_DEFINE");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Find the project_base_path widget
                const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                if (projectPathWidget) {
                    console.log("🐻 Bear Cave: Found project_base_path widget, adding browse button");
                    
                    // Add a browse button using FileBrowserAPI
                    this.addWidget("button", "📁 Browse Project Folder", null, () => {
                        if (app.FileFolderAPI) {
                            console.log("🐻 Bear Cave: Opening folder browser via FileBrowserAPI");
                            app.FileFolderAPI.open(projectPathWidget, 'folder');
                        } else {
                            console.error("🐻 Bear Cave: FileBrowserAPI not available");
                            alert("FileBrowserAPI not found. Please install ComfyUI-FileBrowserAPI extension.");
                        }
                    });
                } else {
                    console.error("🐻 Bear Cave: project_base_path widget not found");
                }
                
                return result;
            };
            
            // Also add to right-click menu
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(canvas, menuOptions) {
                getExtraMenuOptions?.apply(this, arguments);
                
                const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                if (projectPathWidget) {
                    menuOptions.unshift({
                        content: "🐻 Browse Project Folder",
                        callback: () => {
                            if (app.FileFolderAPI) {
                                console.log("🐻 Bear Cave: Opening folder browser via right-click menu");
                                app.FileFolderAPI.open(projectPathWidget, 'folder');
                            } else {
                                alert("FileBrowserAPI not found. Please install ComfyUI-FileBrowserAPI extension.");
                            }
                        }
                    }, null);
                }
            };
        }
    }
});

console.log("🐻 Bear Cave: FileBrowserAPI integration loaded");