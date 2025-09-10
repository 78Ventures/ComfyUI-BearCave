/**
 * Bear Cave Folder Browser Extension for ComfyUI
 * Adds folder browsing capability to BC_LOAD_IMAGES node
 */

import { app } from "../../scripts/app.js";

// Function to create folder browser dialog
function createFolderBrowserDialog(callback) {
    const dialog = document.createElement('div');
    dialog.className = 'bc-folder-browser-dialog';
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #2b2b2b;
        border: 2px solid #555;
        border-radius: 8px;
        padding: 20px;
        z-index: 10000;
        min-width: 400px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    `;

    const title = document.createElement('h3');
    title.textContent = '🐻 Select Folder';
    title.style.cssText = `
        color: #fff;
        margin: 0 0 15px 0;
        font-size: 16px;
    `;

    const pathInput = document.createElement('input');
    pathInput.type = 'text';
    pathInput.placeholder = 'Enter folder path or browse...';
    pathInput.style.cssText = `
        width: 100%;
        padding: 8px;
        margin-bottom: 15px;
        background: #1a1a1a;
        border: 1px solid #555;
        border-radius: 4px;
        color: #fff;
        font-family: monospace;
    `;

    const browseButton = document.createElement('button');
    browseButton.textContent = '📁 Browse Folder';
    browseButton.style.cssText = `
        background: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin-right: 10px;
    `;

    const okButton = document.createElement('button');
    okButton.textContent = 'OK';
    okButton.style.cssText = `
        background: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin-right: 10px;
    `;

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.cssText = `
        background: #f44336;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
    `;

    const buttonContainer = document.createElement('div');
    buttonContainer.appendChild(browseButton);
    buttonContainer.appendChild(okButton);
    buttonContainer.appendChild(cancelButton);

    dialog.appendChild(title);
    dialog.appendChild(pathInput);
    dialog.appendChild(buttonContainer);
    document.body.appendChild(dialog);

    // Handle browse button click (use directory picker API if available)
    browseButton.onclick = async () => {
        if ('showDirectoryPicker' in window) {
            try {
                const dirHandle = await window.showDirectoryPicker();
                pathInput.value = dirHandle.name; // Note: This gives folder name, not full path
                console.log('Selected directory:', dirHandle);
            } catch (err) {
                if (err.name !== 'AbortError') {
                    alert('Folder selection was cancelled or failed.');
                }
            }
        } else {
            // Fallback for browsers that don't support File System Access API
            alert('Folder browsing requires a modern browser. Please enter the path manually.');
        }
    };

    // Handle OK button
    okButton.onclick = () => {
        const path = pathInput.value.trim();
        if (path) {
            callback(path);
            document.body.removeChild(dialog);
        } else {
            alert('Please enter a folder path.');
        }
    };

    // Handle Cancel button
    cancelButton.onclick = () => {
        document.body.removeChild(dialog);
    };

    // Handle Enter key
    pathInput.onkeypress = (e) => {
        if (e.key === 'Enter') {
            okButton.click();
        }
    };

    // Focus on input
    pathInput.focus();
}

// Register the extension when the app starts
app.registerExtension({
    name: "BearCave.FolderBrowser",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only apply to BC_LOAD_IMAGES nodes
        if (nodeData.name === "BC_LOAD_IMAGES") {
            console.log("🐻 Bear Cave: Adding folder browser to BC_LOAD_IMAGES");
            
            // Store the original node creation function
            const originalNodeCreated = nodeType.prototype.onNodeCreated;
            
            // Override the node creation to add folder browser functionality
            nodeType.prototype.onNodeCreated = function() {
                if (originalNodeCreated) {
                    originalNodeCreated.apply(this, arguments);
                }
                
                // Find the input_path widget
                const pathWidget = this.widgets?.find(w => w.name === "input_path");
                if (pathWidget) {
                    console.log("🐻 Bear Cave: Found input_path widget, adding folder browser");
                    
                    // Store original callback
                    const originalCallback = pathWidget.callback;
                    
                    // Create a button element for folder browsing
                    const browseBtn = document.createElement('button');
                    browseBtn.textContent = '📁';
                    browseBtn.title = 'Browse for folder';
                    browseBtn.style.cssText = `
                        position: absolute;
                        right: 2px;
                        top: 2px;
                        bottom: 2px;
                        width: 30px;
                        background: #4CAF50;
                        border: none;
                        border-radius: 3px;
                        color: white;
                        cursor: pointer;
                        font-size: 14px;
                    `;
                    
                    // Add click handler to open folder browser
                    browseBtn.onclick = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        createFolderBrowserDialog((selectedPath) => {
                            pathWidget.value = selectedPath;
                            if (originalCallback) {
                                originalCallback(selectedPath);
                            }
                            // Trigger node update
                            if (this.onResize) {
                                this.onResize();
                            }
                        });
                    };
                    
                    // Add the button to the widget's DOM element when it's created
                    const originalComputeSize = pathWidget.computeSize;
                    pathWidget.computeSize = function(width) {
                        const result = originalComputeSize ? originalComputeSize.call(this, width) : [width, 20];
                        
                        // Add browse button to widget's element if it exists
                        setTimeout(() => {
                            const widgetElement = document.querySelector(`[data-widget="${this.name}"]`);
                            if (widgetElement && !widgetElement.querySelector('.bc-browse-btn')) {
                                browseBtn.className = 'bc-browse-btn';
                                widgetElement.style.position = 'relative';
                                widgetElement.appendChild(browseBtn);
                            }
                        }, 100);
                        
                        return result;
                    };
                }
            };
        }
    }
});

console.log("🐻 Bear Cave Folder Browser extension loaded");