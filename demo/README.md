# Galaxy Model Demo

This directory hosts a static React demo visualizing the DeepConf "Galaxy Model" as a multi-dimensional (3D) force-directed graph.

## Running the Demo
1. Start the backend server:
   ```bash
   python -m app.main
   ```
2. Serve this directory:
   ```bash
   python -m http.server 5173 --directory demo
   ```
3. Open your browser to [http://localhost:5173/index.html](http://localhost:5173/index.html) and click **Run Analysis**.

Windows users can run `start_galaxy_demo.bat` to launch both the backend and this demo automatically.

## Features
- 3D force-directed visualization of reasoning traces
- Slider to filter nodes by confidence (η)
- Inspector panel showing the full text for selected nodes
