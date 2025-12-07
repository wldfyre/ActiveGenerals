# Open Source Architecture Visualization Tools & Generated Diagrams

## 🎨 Open Source Tools for Creating Clean Architecture Views

### **1. Python-based Visualization Libraries**
- **Matplotlib** - Foundation for creating custom diagrams and charts
- **NetworkX** - Graph theory library for relationship diagrams
- **Graphviz** - Declarative graph drawing (via `pygraphviz` or `pydot`)
- **Plotly** - Interactive web-based visualizations
- **Bokeh** - Interactive web plots for modern web browsers
- **Seaborn** - Statistical data visualization (built on matplotlib)

### **2. Text-based Diagram Tools**
- **Mermaid** - Text-to-diagram conversion (used in your docs)
- **PlantUML** - UML diagram generation from text
- **D2** - Modern diagram scripting language by Terrastruct
- **Nomnoml** - UML diagrams from text
- **WebSequenceDiagrams** - Sequence diagram generation

### **3. Desktop Applications**
- **Draw.io/Diagrams.net** - Web-based diagramming (open source)
- **Excalidraw** - Collaborative whiteboarding
- **Inkscape** - Vector graphics editor
- **GIMP** - Raster graphics editor

### **4. Specialized Architecture Tools**
- **Structurizr** - Software architecture modeling
- **Archi** - ArchiMate modeling toolkit
- **Gaphor** - UML/SysML modeling application
- **Modelio** - UML modeling tool

### **5. Web-based Tools**
- **Miro** - Collaborative whiteboard (has free tier)
- **Lucidchart** - Diagramming (has free tier)
- **Figma** - Design and prototyping (has free tier)

## 📊 Generated Diagrams for Evony Active Generals Tracker

### **Architecture Diagrams** (`create_architecture_diagrams.py`)

#### **1. Layered Architecture Diagram**
- **File**: `docs/architecture_diagram.png` / `.pdf`
- **Shows**: Hierarchical component relationships
- **Layers**: Entry → UI → Controller → Platform/OCR/Navigation → Data/Export
- **Connections**: Data flow and dependencies between layers
- **External Dependencies**: PyQt5, OpenCV, ADB, OpenPyXL, etc.

#### **2. Component Relationship Graph**
- **File**: `docs/architecture_network.png` / `.pdf`
- **Shows**: Network graph of component interactions
- **Nodes**: All major classes and modules
- **Edges**: Dependencies and data flow relationships
- **Layout**: Force-directed graph layout for optimal visualization

#### **3. Data Flow Diagram**
- **File**: `docs/data_flow_diagram.png` / `.pdf`
- **Shows**: Step-by-step data collection process
- **Flow**: User Input → Navigation → OCR → Model Creation → Export
- **Decision Points**: Error handling and validation steps

### **Process Flow Diagrams** (`create_process_flows.py`)

#### **4. Application Startup Flow**
- **File**: `docs/startup_process_flow.png` / `.pdf`
- **Shows**: Complete application initialization sequence
- **Steps**: Config loading → Logging setup → Qt app creation → UI initialization
- **Decisions**: Config file existence, High DPI scaling needs

#### **5. Data Collection Process Flow**
- **File**: `docs/collection_process_flow.png` / `.pdf`
- **Shows**: Detailed general data extraction workflow
- **Steps**: Navigation → Screenshot → OCR extraction → Data validation → Confidence scoring
- **Loop**: Process each general with subscreen navigation
- **Decisions**: Connection status, navigation success, confidence thresholds

#### **6. Error Handling & Recovery Flow**
- **File**: `docs/error_handling_flow.png` / `.pdf`
- **Shows**: Comprehensive error handling strategies
- **Error Types**: Platform, Navigation, OCR, Screenshot, Export errors
- **Recovery**: Retry logic, graceful degradation, user notifications
- **Decisions**: Retry count limits, continuation possibilities

#### **7. Excel Export Process Flow**
- **File**: `docs/export_process_flow.png` / `.pdf`
- **Shows**: Spreadsheet generation workflow
- **Steps**: Template loading → Data sorting → Cell writing → Image insertion → Formatting
- **Loop**: Process each general's data and images
- **Decisions**: Path validation, template existence, completion status

## 🛠️ How to Use These Tools

### **Python Script Usage**
```bash
# Generate all architecture diagrams
python create_architecture_diagrams.py

# Generate all process flow diagrams
python create_process_flows.py

# View results
# Open PNG files in docs/ folder
```

### **Customization**
- **Colors**: Modify color schemes in the script
- **Layout**: Adjust positioning and sizing
- **Content**: Update process steps and component names
- **Resolution**: Change DPI for higher quality output

### **Integration with Documentation**
- **Markdown**: Embed PNG images in README.md or docs
- **PDF**: Use for presentations or formal documentation
- **Web**: Convert to SVG for web documentation

## 📈 Benefits of These Visualizations

### **For Developers**
- **Clear Architecture**: Understand component relationships at a glance
- **Process Clarity**: Follow data flow through the entire system
- **Error Scenarios**: Visualize failure modes and recovery paths
- **Onboarding**: Help new developers understand the codebase

### **For Stakeholders**
- **High-Level Overview**: Understand system complexity without code details
- **Process Transparency**: See how user actions translate to system operations
- **Decision Points**: Understand where the system makes critical choices

### **For Maintenance**
- **Dependency Mapping**: Identify coupling between components
- **Bottleneck Identification**: Spot potential performance issues
- **Testing Focus**: Highlight critical paths that need thorough testing

## 🔧 Advanced Usage

### **Automated Generation**
```python
# Integrate with CI/CD pipeline
# Generate diagrams on code changes
# Include in documentation builds
```

### **Interactive Versions**
```python
# Use Plotly for web-based interactive diagrams
# Add hover information and clickable elements
# Embed in web documentation
```

### **Version Control Integration**
```python
# Track architecture changes over time
# Compare diagrams between versions
# Document architectural decisions
```

These tools and generated diagrams provide comprehensive, professional-quality visualizations that make the Evony Active Generals Tracker's architecture clear and maintainable.