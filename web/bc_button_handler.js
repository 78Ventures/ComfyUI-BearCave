/**
 * Add double-click folder browser to BC_LORA_DEFINE project_base_path field
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading double-click folder browser...");

app.registerExtension({
    name: "BearCave.DoubleClickBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Setting up double-click for BC_LORA_DEFINE");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                console.log("🐻 Bear Cave: BC_LORA_DEFINE node created");
                
                // Add double-click handler to project_base_path widget
                setTimeout(() => {
                    const projectPathWidget = this.widgets.find(w => w.name === "project_base_path");
                    if (projectPathWidget) {
                        console.log("🐻 Bear Cave: Found project_base_path widget, adding double-click handler");
                        
                        // Store original callback
                        const originalCallback = projectPathWidget.callback;
                        
                        // Track clicks for double-click detection
                        let lastClickTime = 0;
                        
                        projectPathWidget.callback = function(value, widget, node, pos, event) {
                            const now = Date.now();
                            if (now - lastClickTime < 300) {
                                // Double-click detected
                                console.log("🐻 Bear Cave: Double-click detected on project_base_path!");
                                if (app.FileFolderAPI) {
                                    console.log("🐻 Bear Cave: Opening FileFolderAPI...");
                                    app.FileFolderAPI.open(projectPathWidget, 'folder');
                                } else {
                                    console.error("🐻 Bear Cave: FileFolderAPI not available");
                                    const path = prompt('Enter project folder path:', projectPathWidget.value || '');
                                    if (path !== null) {
                                        projectPathWidget.value = path;
                                    }
                                }
                            }
                            lastClickTime = now;
                            
                            // Call original callback
                            if (originalCallback) {
                                return originalCallback.call(this, value, widget, node, pos, event);
                            }
                        };
                        
                        console.log("🐻 Bear Cave: Double-click handler attached to project_base_path");
                    } else {
                        console.error("🐻 Bear Cave: project_base_path widget not found");
                    }
                }, 100);
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave: Double-click folder browser extension loaded");