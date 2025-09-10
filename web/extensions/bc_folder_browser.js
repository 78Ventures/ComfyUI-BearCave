/**
 * Bear Cave Folder Browser Extension - Entry Point
 * This file is loaded by ComfyUI's extension system
 */

import { app } from "../../../scripts/app.js";

// Enhanced folder browser implementation
class BCFolderBrowser {
    constructor() {
        this.init();
    }

    init() {
        console.log("🐻 Bear Cave: Initializing Folder Browser Extension");
        this.setupNodeExtension();
    }

    createFolderDialog(callback) {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        // Create dialog
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: #2a2a2a;
            border: 2px solid #555;
            border-radius: 8px;
            padding: 24px;
            min-width: 450px;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        `;

        const html = `
            <div style="margin-bottom: 20px;">
                <h3 style="margin: 0 0 8px 0; color: #fff; font-size: 18px;">
                    🐻 Select Images Folder
                </h3>
                <p style="margin: 0; color: #ccc; font-size: 14px;">
                    Choose the folder containing your training images
                </p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <input type="text" 
                       id="bc-path-input" 
                       placeholder="Enter folder path or click Browse..."
                       style="
                           width: 100%;
                           padding: 12px;
                           background: #1a1a1a;
                           border: 2px solid #555;
                           border-radius: 6px;
                           color: #fff;
                           font-size: 14px;
                           font-family: 'SF Mono', Monaco, monospace;
                           box-sizing: border-box;
                       ">
            </div>
            
            <div style="margin-bottom: 20px;">
                <button id="bc-browse-btn" style="
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    width: 100%;
                    transition: all 0.2s;
                " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(76,175,80,0.3)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    📁 Browse for Folder
                </button>
            </div>
            
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button id="bc-cancel-btn" style="
                    background: #666;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">Cancel</button>
                <button id="bc-ok-btn" style="
                    background: linear-gradient(135deg, #2196F3, #1976D2);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                ">Select Folder</button>
            </div>
        `;

        dialog.innerHTML = html;
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        const pathInput = dialog.querySelector('#bc-path-input');
        const browseBtn = dialog.querySelector('#bc-browse-btn');
        const okBtn = dialog.querySelector('#bc-ok-btn');
        const cancelBtn = dialog.querySelector('#bc-cancel-btn');

        // Focus input
        pathInput.focus();

        // Browse button handler
        browseBtn.onclick = async () => {
            if ('showDirectoryPicker' in window) {
                try {
                    const dirHandle = await window.showDirectoryPicker();
                    // Get the path name (this is limited in browsers for security)
                    pathInput.value = dirHandle.name;
                    console.log('🐻 Selected directory handle:', dirHandle);
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        this.showNotification('Folder selection cancelled or failed', 'warning');
                    }
                }
            } else {
                // Fallback for older browsers
                this.showNotification('Please enter the path manually. Modern browsers support folder browsing.', 'info');
                pathInput.focus();
            }
        };

        // OK button handler
        okBtn.onclick = () => {
            const path = pathInput.value.trim();
            if (path) {
                callback(path);
                document.body.removeChild(overlay);
            } else {
                this.showNotification('Please enter a folder path', 'warning');
                pathInput.focus();
            }
        };

        // Cancel button handler
        cancelBtn.onclick = () => {
            document.body.removeChild(overlay);
        };

        // Enter key handler
        pathInput.onkeypress = (e) => {
            if (e.key === 'Enter') {
                okBtn.click();
            }
        };

        // Escape key handler
        document.onkeydown = (e) => {
            if (e.key === 'Escape' && document.body.contains(overlay)) {
                cancelBtn.click();
            }
        };
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const bgColor = type === 'warning' ? '#f44336' : 
                       type === 'success' ? '#4CAF50' : 
                       '#2196F3';
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Add CSS animation
        if (!document.querySelector('#bc-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'bc-notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }

    setupNodeExtension() {
        app.registerExtension({
            name: "BearCave.FolderBrowser",
            
            async beforeRegisterNodeDef(nodeType, nodeData) {
                if (nodeData.name === "BC_LOAD_IMAGES") {
                    console.log("🐻 Bear Cave: Enhancing BC_LOAD_IMAGES with folder browser");
                    
                    const originalNodeCreated = nodeType.prototype.onNodeCreated;
                    
                    nodeType.prototype.onNodeCreated = function() {
                        if (originalNodeCreated) {
                            originalNodeCreated.apply(this, arguments);
                        }
                        
                        // Find the input_path widget
                        const pathWidget = this.widgets?.find(w => w.name === "input_path");
                        if (pathWidget) {
                            // Add double-click handler to open folder browser
                            const originalMouseDown = pathWidget.mouse ? pathWidget.mouse : null;
                            
                            pathWidget.mouse = (event, pos, node) => {
                                if (originalMouseDown) {
                                    originalMouseDown.call(this, event, pos, node);
                                }
                                
                                // Handle double-click to open folder browser
                                if (event.type === "dblclick" || 
                                   (event.type === "pointerdown" && event.detail === 2)) {
                                    
                                    const browser = new BCFolderBrowser();
                                    browser.createFolderDialog((selectedPath) => {
                                        pathWidget.value = selectedPath;
                                        // Trigger change event
                                        if (pathWidget.callback) {
                                            pathWidget.callback(selectedPath);
                                        }
                                        // Mark node as modified
                                        node.setDirtyCanvas(true);
                                    });
                                }
                            };
                            
                            // Add visual indicator
                            pathWidget.options = pathWidget.options || {};
                            pathWidget.options.placeholder = "Double-click to browse for folder...";
                            
                            console.log("🐻 Bear Cave: Added folder browser to input_path widget");
                        }
                    };
                }
            }
        });
    }
}

// Initialize the extension
const bcFolderBrowser = new BCFolderBrowser();

console.log("🐻 Bear Cave Folder Browser extension loaded and ready!");