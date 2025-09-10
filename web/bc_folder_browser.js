/**
 * Simple folder browser for BC_LORA_DEFINE project_base_path
 * Adds double-click handler to open folder picker
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading folder browser extension v3...");

app.registerExtension({
    name: "BearCave.FolderBrowser",
    
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Processing BC_LORA_DEFINE node");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                console.log("🐻 Bear Cave: BC_LORA_DEFINE node created, widgets:", this.widgets?.map(w => w.name));
                
                // Add double-click handler to project_base_path widget
                for (const widget of this.widgets || []) {
                    if (widget.name === "project_base_path") {
                        console.log("🐻 Bear Cave: Found project_base_path widget, adding handler");
                        
                        const originalCallback = widget.callback;
                        let lastClickTime = 0;
                        
                        widget.callback = function(...args) {
                            const now = Date.now();
                            if (now - lastClickTime < 300) {
                                // Double click detected
                                console.log("🐻 Bear Cave: Double-click detected, opening folder browser");
                                
                                if ('showDirectoryPicker' in window) {
                                    window.showDirectoryPicker().then(dirHandle => {
                                        const path = prompt('Enter full folder path (browser only shows folder name):', dirHandle.name);
                                        if (path) {
                                            widget.value = path;
                                            if (originalCallback) originalCallback.apply(this, args);
                                        }
                                    }).catch(err => {
                                        if (err.name !== 'AbortError') {
                                            console.log('Folder picker cancelled or failed');
                                        }
                                    });
                                } else {
                                    const path = prompt('Enter folder path:', widget.value || '');
                                    if (path !== null) {
                                        widget.value = path;
                                        if (originalCallback) originalCallback.apply(this, args);
                                    }
                                }
                            }
                            lastClickTime = now;
                            
                            if (originalCallback) {
                                return originalCallback.apply(this, args);
                            }
                        };
                        
                        console.log("🐻 Bear Cave: Double-click handler added to project_base_path");
                        break;
                    }
                }
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave: Folder browser extension loaded v3");