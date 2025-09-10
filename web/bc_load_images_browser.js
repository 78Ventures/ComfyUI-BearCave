/**
 * Bear Cave BC_LOAD_IMAGES Folder Browser
 * Adds folder selection dialog to BC_LOAD_IMAGES nodes
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
        <h3 style="margin-top: 0; color: #fff;">🐻 Select Images Folder</h3>
        <p style="color: #ccc; margin: 10px 0;">Choose the folder containing your training images:</p>
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
    name: "BearCave.BC_LOAD_IMAGES.FolderBrowser",
    
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "BC_LOAD_IMAGES") {
            console.log("🐻 Bear Cave: Adding folder browser to BC_LOAD_IMAGES");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Find the input_path widget
                for (const widget of this.widgets || []) {
                    if (widget.name === "input_path") {
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
                        
                        console.log("🐻 Bear Cave: Folder browser attached to input_path widget");
                        break;
                    }
                }
                
                return result;
            };
        }
    }
});

console.log("🐻 Bear Cave BC_LOAD_IMAGES Folder Browser extension loaded");