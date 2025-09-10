/**
 * Bear Cave BC_LORA_DEFINE Folder Browser
 * Adds folder selection dialog to BC_LORA_DEFINE project_base_path field
 * Version: 2024-09-10-v2
 */

import { app } from "../../scripts/app.js";

// Simple folder selection dialog
function openFolderDialog(callback) {
    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    // Create dialog
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        background: #333;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #555;
        color: white;
        font-family: Arial, sans-serif;
        min-width: 400px;
    `;

    dialog.innerHTML = `
        <h3 style="margin-top: 0; color: #fff;">🐻 Select Project Base Folder</h3>
        <p style="color: #ccc; margin: 10px 0;">Choose the folder where your LoRa project will be created:</p>
        <input type="text" id="folder-path" placeholder="Enter folder path..." style="
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            background: #222;
            border: 1px solid #555;
            color: white;
            border-radius: 4px;
            box-sizing: border-box;
        ">
        <div style="margin-top: 15px;">
            <button id="browse-btn" style="
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                margin-right: 10px;
                border-radius: 4px;
                cursor: pointer;
            ">📁 Browse</button>
            <button id="ok-btn" style="
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                margin-right: 10px;
                border-radius: 4px;
                cursor: pointer;
            ">OK</button>
            <button id="cancel-btn" style="
                background: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
            ">Cancel</button>
        </div>
    `;

    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);

    const pathInput = document.getElementById('folder-path');
    const browseBtn = document.getElementById('browse-btn');
    const okBtn = document.getElementById('ok-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    pathInput.focus();

    // Browse button handler
    browseBtn.onclick = async () => {
        if ('showDirectoryPicker' in window) {
            try {
                const dirHandle = await window.showDirectoryPicker();
                // Note: Due to browser security, we can only get the folder name, not full path
                pathInput.value = dirHandle.name;
                console.log('Selected directory:', dirHandle);
            } catch (err) {
                if (err.name !== 'AbortError') {
                    alert('Folder selection cancelled.');
                }
            }
        } else {
            alert('Folder browsing requires a modern browser. Please enter the path manually.');
        }
    };

    // OK handler
    okBtn.onclick = () => {
        const path = pathInput.value.trim();
        if (path) {
            callback(path);
            document.body.removeChild(backdrop);
        } else {
            alert('Please enter a folder path.');
        }
    };

    // Cancel handler
    cancelBtn.onclick = () => {
        document.body.removeChild(backdrop);
    };

    // Enter key handler
    pathInput.onkeypress = (e) => {
        if (e.key === 'Enter') {
            okBtn.click();
        }
    };

    // Escape key handler
    backdrop.onkeydown = (e) => {
        if (e.key === 'Escape') {
            cancelBtn.click();
        }
    };
}

// Register extension with ComfyUI
app.registerExtension({
    name: "BearCave.BC_LORA_DEFINE.FolderBrowser",
    
    beforeRegisterNodeDef(nodeType, nodeData) {
        console.log("🐻 Bear Cave: Checking node type:", nodeData.name);
        
        // Explicitly block folder browser from BC_LOAD_IMAGES  
        if (nodeData.name === "BC_LOAD_IMAGES") {
            console.log("🐻 Bear Cave: BLOCKING folder browser from BC_LOAD_IMAGES node");
            return; // Do nothing for BC_LOAD_IMAGES
        }
        
        if (nodeData.name === "BC_LORA_DEFINE") {
            console.log("🐻 Bear Cave: CORRECTLY Adding folder browser to BC_LORA_DEFINE node");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Find the project_base_path widget
                console.log("🐻 Bear Cave: Available widgets:", (this.widgets || []).map(w => w.name));
                for (const widget of this.widgets || []) {
                    console.log("🐻 Bear Cave: Checking widget:", widget.name);
                    if (widget.name === "project_base_path") {
                        // Store original mouse handler
                        const originalMouse = widget.mouse;
                        
                        // Override mouse handler to detect double-clicks
                        widget.mouse = function(event, pos, node) {
                            if (originalMouse) {
                                originalMouse.call(this, event, pos, node);
                            }
                            
                            // Handle double-click
                            if (event.type === "dblclick" || (event.type === "pointerdown" && event.detail === 2)) {
                                console.log("🐻 Bear Cave: Opening folder browser");
                                openFolderDialog((selectedPath) => {
                                    widget.value = selectedPath;
                                    if (widget.callback) {
                                        widget.callback(selectedPath, widget, node, pos, event);
                                    }
                                    node.setDirtyCanvas(true, false);
                                });
                            }
                        };
                        
                        console.log("🐻 Bear Cave: ✅ Folder browser successfully attached to project_base_path widget on BC_LORA_DEFINE node");
                        break;
                    }
                }
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave: BC_LORA_DEFINE Folder Browser extension loaded v2024-09-10-v2 - targets project_base_path field ONLY");