/**
 * Bear Cave BC_LORA_DEFINE File Browser Integration
 * Uses ComfyUI-FileBrowserAPI to add folder browsing to project_base_path
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading FileBrowserAPI integration...");
alert("🐻 Bear Cave: Extension Loading!");

app.registerExtension({
    name: "BearCave.BC_LORA_DEFINE.FileBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Processing BC_LORA_DEFINE node");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                console.log("🐻 Bear Cave: BC_LORA_DEFINE node created");
                console.log("🐻 Bear Cave: Available widgets:", this.widgets?.map(w => w.name));
                console.log("🐻 Bear Cave: app object keys:", Object.keys(app));
                console.log("🐻 Bear Cave: FileFolderAPI available:", !!app.FileFolderAPI);
                console.log("🐻 Bear Cave: window.FileFolderAPI available:", !!window.FileFolderAPI);
                console.log("🐻 Bear Cave: Looking for API in different locations...");
                
                // Wait for FileBrowserAPI to be available
                const waitForAPI = () => {
                    // Check multiple possible locations for the API
                    const api = app.FileFolderAPI || window.FileFolderAPI || window.app?.FileFolderAPI;
                    
                    if (api) {
                        console.log("🐻 Bear Cave: FileFolderAPI found!", api);
                        const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                        if (projectPathWidget) {
                            console.log("🐻 Bear Cave: Found project_base_path widget, adding browse button");
                            
                            // Add a browse button using FileBrowserAPI
                            this.addWidget("button", "📁 Set Project Path", null, () => {
                                console.log("🐻 Bear Cave: Browse button clicked");
                                api.open(projectPathWidget, 'folder');
                            });
                            
                            console.log("🐻 Bear Cave: Browse button added successfully");
                            console.log("🐻 Bear Cave: Total widgets now:", this.widgets.length);
                            console.log("🐻 Bear Cave: Widget names:", this.widgets.map(w => w.name));
                            
                            // Force UI refresh
                            this.setDirtyCanvas(true, true);
                            this.size = this.computeSize();
                        }
                    } else {
                        console.log("🐻 Bear Cave: Still waiting for FileFolderAPI... Checked app.FileFolderAPI:", !!app.FileFolderAPI, "window.FileFolderAPI:", !!window.FileFolderAPI);
                        setTimeout(waitForAPI, 1000);
                    }
                };
                
                setTimeout(waitForAPI, 100);
                
                return result;
            };
            
            // Also add to right-click menu
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(canvas, menuOptions) {
                getExtraMenuOptions?.apply(this, arguments);
                
                const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                if (projectPathWidget) {
                    menuOptions.unshift({
                        content: "🐻 Set Project Path",
                        callback: () => {
                            if (app.FileFolderAPI) {
                                console.log("🐻 Bear Cave: Opening folder browser via right-click menu");
                                app.FileFolderAPI.open(projectPathWidget, 'folder');
                            } else {
                                alert("FileBrowserAPI not found. Please make sure ComfyUI-FileBrowserAPI extension is installed.");
                            }
                        }
                    }, null);
                }
            };
        }
    }
});

console.log("🐻 Bear Cave: FileBrowserAPI integration loaded");