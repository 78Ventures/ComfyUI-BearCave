// bearcave_ui_groups.js
// Add section headers (UI subheaders) to TORTU nodes for better organization

app.registerExtension({
    name: "TORTU.UIGroups",
    
    async nodeCreated(node) {
        // BC_LORA_DEFINE node organization
        if (node.comfyClass === "BC_LORA_DEFINE") {
            // Wait for widgets to be created
            setTimeout(() => {
                this.organizeLoraDefineNode(node);
            }, 100);
        }
        
        // BC_EXIF_WRITER node organization  
        if (node.comfyClass === "BC_EXIF_WRITER") {
            setTimeout(() => {
                this.organizeExifWriterNode(node);
            }, 100);
        }
        
        // BC_DETECT_FACE_ORIENTATION node organization
        if (node.comfyClass === "BC_DETECT_FACE_ORIENTATION") {
            setTimeout(() => {
                this.organizeFaceDetectionNode(node);
            }, 100);
        }
        
        // BC_IMAGE_LORA_CONFORM node organization
        if (node.comfyClass === "BC_IMAGE_LORA_CONFORM") {
            setTimeout(() => {
                this.organizeLoraConformNode(node);
            }, 100);
        }
        
        // BC_LOAD_IMAGES node organization
        if (node.comfyClass === "BC_LOAD_IMAGES") {
            setTimeout(() => {
                this.organizeLoadImagesNode(node);
            }, 100);
        }
        
        // BC_SAVE_IMAGES node organization  
        if (node.comfyClass === "BC_SAVE_IMAGES") {
            setTimeout(() => {
                this.organizeSaveImagesNode(node);
            }, 100);
        }
    },
    
    organizeLoraDefineNode(node) {
        if (!node.widgets) return;
        
        // Find widgets by name
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        // Create section headers
        const projectHeader = node.addWidget("label", "── Project Setup ──");
        const subjectHeader = node.addWidget("label", "── Subject Metadata ──");
        
        // Define widget order with headers and alphabetical sorting within groups
        const projectWidgets = [
            "base_model", "create_folders", "custom_base_model_path", 
            "description", "overwrite_existing", "performance_mode", 
            "project_base_path", "project_name"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const subjectWidgets = [
            "additional_tags", "age", "background", "camera_angle", 
            "ethnicity", "gender", "lighting", "subject_name", "trigger_words"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Project Setup section (alphabetical)
            projectHeader,
            ...projectWidgets,
            
            // Subject Metadata section (alphabetical) 
            subjectHeader,
            ...subjectWidgets
        ];
        
        // Reorder widgets
        node.widgets = orderedWidgets;
        
        // Style the headers
        [projectHeader, subjectHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25]; // Height for header
                header.color = "#555";
            }
        });
    },
    
    organizeExifWriterNode(node) {
        if (!node.widgets) return;
        
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        // Create section headers
        const basicHeader = node.addWidget("label", "── Basic Information ──");
        const technicalHeader = node.addWidget("label", "── Technical Details ──");
        const metadataHeader = node.addWidget("label", "── Additional Metadata ──");
        
        // Alphabetically sort widgets within groups
        const basicWidgets = [
            "expression", "note", "output_dir", "pose", "subject"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const technicalWidgets = [
            "creation_date", "face_pose", "file_size", "filename", 
            "full_path", "height", "relative_path", "source_directory", "width"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const metadataWidgets = [
            "age", "background", "camera_angle", "dataset_name", "ethnicity", 
            "gender", "lighting", "quality_rating", "tags", "training_weight"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Basic Information (alphabetical)
            basicHeader,
            ...basicWidgets,
            
            // Technical Details (alphabetical)  
            technicalHeader,
            ...technicalWidgets,
            
            // Additional Metadata (alphabetical)
            metadataHeader,
            ...metadataWidgets
        ];
        
        node.widgets = orderedWidgets;
        
        [basicHeader, technicalHeader, metadataHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25];
                header.color = "#555";
            }
        });
    },
    
    organizeFaceDetectionNode(node) {
        if (!node.widgets) return;
        
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        const connectionHeader = node.addWidget("label", "── Connection Points ──");
        const detectionHeader = node.addWidget("label", "── Detection Settings ──");
        
        // Alphabetically sort widgets within groups
        const connectionWidgets = [
            "filename", "relative_path", "source_directory"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const detectionWidgets = [
            "detection_confidence", "model_selection"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Connection Points (alphabetical)
            connectionHeader,
            ...connectionWidgets,
            
            // Detection Settings (alphabetical)
            detectionHeader,
            ...detectionWidgets
        ];
        
        node.widgets = orderedWidgets;
        
        [connectionHeader, detectionHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25];
                header.color = "#555";
            }
        });
    },
    
    organizeLoraConformNode(node) {
        if (!node.widgets) return;
        
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        const connectionHeader = node.addWidget("label", "── Connection Points ──");
        const detectionHeader = node.addWidget("label", "── Face Detection Data ──");
        const processingHeader = node.addWidget("label", "── Processing Settings ──");
        
        // Alphabetically sort widgets within groups
        const connectionWidgets = [
            "creation_date", "file_size", "filename", "full_path", 
            "height", "relative_path", "source_directory", "width"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const detectionWidgets = [
            "detection_confidence", "face_detected", "face_pose"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const processingWidgets = [
            "processing_log"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Connection Points (alphabetical)
            connectionHeader,
            ...connectionWidgets,
            
            // Face Detection Data (alphabetical)
            detectionHeader,
            ...detectionWidgets,
            
            // Processing Settings (alphabetical)
            processingHeader,
            ...processingWidgets
        ];
        
        node.widgets = orderedWidgets;
        
        [connectionHeader, detectionHeader, processingHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25];
                header.color = "#555";
            }
        });
    },
    
    organizeLoadImagesNode(node) {
        if (!node.widgets) return;
        
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        const pathHeader = node.addWidget("label", "── Path Configuration ──");
        const filterHeader = node.addWidget("label", "── Filter & Sorting ──");
        const loadHeader = node.addWidget("label", "── Load Settings ──");
        
        // Alphabetically sort widgets within groups
        const pathWidgets = [
            "include_subfolders", "input_path"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const filterWidgets = [
            "filter_type", "sort_method"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const loadWidgets = [
            "load_limit", "start_index", "stop_index"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Path Configuration (alphabetical)
            pathHeader,
            ...pathWidgets,
            
            // Filter & Sorting (alphabetical)
            filterHeader,
            ...filterWidgets,
            
            // Load Settings (alphabetical)
            loadHeader,
            ...loadWidgets
        ];
        
        node.widgets = orderedWidgets;
        
        [pathHeader, filterHeader, loadHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25];
                header.color = "#555";
            }
        });
    },
    
    organizeSaveImagesNode(node) {
        if (!node.widgets) return;
        
        const widgetMap = {};
        node.widgets.forEach(widget => {
            widgetMap[widget.name] = widget;
        });
        
        const pathHeader = node.addWidget("label", "── Output Configuration ──");
        const formatHeader = node.addWidget("label", "── Format Settings ──");
        
        // Alphabetically sort widgets within groups
        const pathWidgets = [
            "file_prefix", "filename_text", "output_path", "sort_method"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const formatWidgets = [
            "file_format", "quality"
        ].map(name => widgetMap[name]).filter(widget => widget);
        
        const orderedWidgets = [
            // Output Configuration (alphabetical)
            pathHeader,
            ...pathWidgets,
            
            // Format Settings (alphabetical)
            formatHeader,
            ...formatWidgets
        ];
        
        node.widgets = orderedWidgets;
        
        [pathHeader, formatHeader].forEach(header => {
            if (header) {
                header.computeSize = () => [0, 25];
                header.color = "#555";
            }
        });
    }
});