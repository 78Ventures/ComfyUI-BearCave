/**
 * Simple folder browser for BC_LORA_DEFINE project_base_path
 * Adds a browse button next to the text field
 */

import { app } from "../../scripts/app.js";

console.log("🐻 Bear Cave: Loading folder browser extension...");

app.registerExtension({
    name: "BearCave.FolderBrowser",
    
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: Adding folder browser to BC_LORA_DEFINE");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Find the project_base_path widget and add a button next to it
                setTimeout(() => {
                    for (const widget of this.widgets || []) {
                        if (widget.name === "project_base_path") {
                            console.log("🐻 Bear Cave: Found project_base_path widget");
                            
                            // Create browse button
                            const browseBtn = document.createElement('button');
                            browseBtn.textContent = '📁';
                            browseBtn.style.cssText = `
                                position: absolute;
                                right: 5px;
                                top: 50%;
                                transform: translateY(-50%);
                                width: 25px;
                                height: 20px;
                                border: 1px solid #555;
                                background: #333;
                                color: white;
                                cursor: pointer;
                                font-size: 12px;
                                z-index: 1000;
                            `;
                            
                            browseBtn.onclick = async (e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                
                                // Use the File System Access API if available
                                if ('showDirectoryPicker' in window) {
                                    try {
                                        const dirHandle = await window.showDirectoryPicker();
                                        // Get the folder name (browsers can't give full paths for security)
                                        widget.value = dirHandle.name;
                                        this.setDirtyCanvas(true, false);
                                    } catch (err) {
                                        if (err.name !== 'AbortError') {
                                            // Fallback to text input
                                            const path = prompt('Enter folder path:', widget.value || '');
                                            if (path !== null) {
                                                widget.value = path;
                                                this.setDirtyCanvas(true, false);
                                            }
                                        }
                                    }
                                } else {
                                    // Fallback for browsers that don't support the API
                                    const path = prompt('Enter folder path:', widget.value || '');
                                    if (path !== null) {
                                        widget.value = path;
                                        this.setDirtyCanvas(true, false);
                                    }
                                }
                            };
                            
                            // Add button to the widget's DOM element
                            if (widget.element) {
                                widget.element.style.position = 'relative';
                                widget.element.appendChild(browseBtn);
                            }
                            
                            console.log("🐻 Bear Cave: Folder browser button added");
                            break;
                        }
                    }
                }, 100);
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave: Folder browser extension loaded");