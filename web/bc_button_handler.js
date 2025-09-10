/**
 * Add folder browser functionality to BC_LORA_DEFINE using ComfyUI-FileBrowserAPI
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading folder browser with FileBrowserAPI...");

app.registerExtension({
    name: "BearCave.FolderBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Setting up folder browser for BC_LORA_DEFINE");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                console.log("🐻 Bear Cave: BC_LORA_DEFINE node created, widgets:", this.widgets?.map(w => w.name));
                
                // Add folder browser functionality
                setTimeout(() => {
                    console.log("🐻 Bear Cave: Timeout executing, widgets:", this.widgets?.map(w => w.name));
                    const projectPathWidget = this.widgets?.find(w => w.name === "project_base_path");
                    if (projectPathWidget) {
                        console.log("🐻 Bear Cave: Found project_base_path widget, adding button...");
                        
                        try {
                            // Add browse button next to the path widget
                            const button = this.addWidget("button", "📁 Browse Folder", null, () => {
                                console.log("🐻 Bear Cave: Browse button clicked!");
                                
                                if (app.FileFolderAPI) {
                                    console.log("🐻 Bear Cave: Using FileFolderAPI");
                                    app.FileFolderAPI.open(projectPathWidget, 'folder');
                                } else {
                                    console.warn("🐻 Bear Cave: FileFolderAPI not available, falling back to manual input");
                                    showManualInput(projectPathWidget);
                                }
                            });
                            
                            console.log("🐻 Bear Cave: Browse button added successfully:", button);
                            
                            // Force a redraw
                            this.setDirtyCanvas(true, true);
                            
                        } catch (error) {
                            console.error("🐻 Bear Cave: Error adding button:", error);
                        }
                        
                    } else {
                        console.error("🐻 Bear Cave: project_base_path widget not found!");
                        console.error("🐻 Bear Cave: Available widgets:", this.widgets?.map(w => w.name));
                    }
                }, 200);
                
                return result;
            };
            
            // Also add double-click functionality as backup
            const onDblClick = nodeType.prototype.onDblClick;
            nodeType.prototype.onDblClick = function() {
                onDblClick?.apply(this, arguments);
                console.log("🐻 Bear Cave: Node double-clicked");
                
                const projectPathWidget = this.widgets?.find(w => w.name === "project_base_path");
                if (app.FileFolderAPI && projectPathWidget) {
                    console.log("🐻 Bear Cave: Opening folder browser via double-click");
                    app.FileFolderAPI.open(projectPathWidget, 'folder');
                } else if (projectPathWidget) {
                    console.warn("🐻 Bear Cave: FileFolderAPI not available, using manual input");
                    showManualInput(projectPathWidget);
                }
            };
            
            // Add right-click menu option
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(_, menuOptions) {
                getExtraMenuOptions?.apply(this, arguments);
                
                const projectPathWidget = this.widgets?.find(w => w.name === "project_base_path");
                if (projectPathWidget) {
                    menuOptions.unshift({
                        content: "📁 Browse Project Folder",
                        callback: () => {
                            console.log("🐻 Bear Cave: Menu browse option selected");
                            if (app.FileFolderAPI) {
                                app.FileFolderAPI.open(projectPathWidget, 'folder');
                            } else {
                                showManualInput(projectPathWidget);
                            }
                        }
                    }, null);
                }
            };
        }
    }
});

function showManualInput(widget) {
    const currentValue = widget.value || '';
    
    const helpText = `📁 FOLDER BROWSER (Manual Input)

FileBrowserAPI not available. Enter the full path where your LoRa projects will be stored:

Examples:
• macOS: /Users/YourName/Documents/LoRa-Projects
• Windows: C:\\Users\\YourName\\Documents\\LoRa-Projects
• Linux: /home/yourname/lora-projects

The node will create a subfolder here for your specific project.

Current value: ${currentValue}`;
    
    const newPath = prompt(helpText, currentValue);
    if (newPath !== null && newPath.trim() !== '') {
        widget.value = newPath.trim();
        console.log("🐻 Bear Cave: Manual path entered:", widget.value);
    }
}

console.log("🐻 Bear Cave: Double-click folder browser extension loaded");