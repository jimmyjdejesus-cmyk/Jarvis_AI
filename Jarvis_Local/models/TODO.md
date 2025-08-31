### Task Breakdown & To-Do List

This plan is broken down into phases. Focus on completing each phase before moving to the next to ensure you're always building on a stable foundation.

-----

### Phase 1: Foundational Setup (The Core Local Agent)

**Goal:** Get a single, GPU-accelerated AI agent running locally with a basic UI.
**Estimated Time:** 1.5 - 2.5 hours (excluding download time).

  * [x] **1.1: Download the Meta-Agent Model.**

      * **Action:** Download a GGUF quantized version of `microsoft/Phi-3-mini-instruct`. The `Q4_K_M` version is recommended.
      * **Action:** Place the downloaded file inside the `./Jarvis_Local/models/` directory.

  * [x] **1.2: Set Up the Project Structure.**

      * **Action:** Create the `Jarvis_Local` directory and the five initial files: `main.py`, `agent.py`, `orchestrator.py`, `config.py`, and `evaluation.py`.

  * [x] **1.3: Install and Validate AMD-Optimized Library.**

      * **Risk:** This is the most complex step. Ensure your AMD drivers are up to date.
      * **Action:** Open your terminal and run the specific commands to install `llama-cpp-python` with ROCm support for your AMD GPU.
        ```bash
        # For Windows (PowerShell)
        $env:CMAKE_ARGS = "-DLLAMA_HIPBLAS=on"
        pip install llama-cpp-python
        ```

  * [x] **1.4: Implement the Code.**

      * **Action:** Copy the code we've developed into `main.py` (the Tkinter UI), `config.py` (pointing to your model file and setting `N_GPU_LAYERS = -1`), `agent.py` (the direct loader), and `orchestrator.py` (the simple orchestrator).

  * [x] **1.5: Run and Verify.**

      * **Action:** Run the application with `python main.py`.
      * **Action:** Verify that the UI launches, the model loads without errors, and your system monitor shows VRAM usage, confirming it's running on the GPU.

-----

### Phase 2: Foundational Tooling (Stability & Measurement)

**Goal:** Add essential developer tools for logging, dependency management, and quality control.
**Estimated Time:** \~7 - 12 hours.

  * [x] **2.1: Implement Structured Logging.**

      * **Action:** Use Python's built-in `logging` module to add simple, file-based logging to `orchestrator.py` and `agent.py`. This is a simplified version of your legacy logger.

  * [x] **2.2: Create Dependency File.**

      * **Action:** In your project's virtual environment, run `pip freeze > requirements.txt` to create a list of all necessary libraries.

  * [x] **2.3: Build the Evaluation Harness.**

      * **Action:** In `evaluation.py`, create a list of 5-10 standard test prompts that cover different reasoning and coding tasks.
      * **Action:** Write a runner function that executes these prompts and checks the model's output against expected criteria. This will be your primary tool for measuring if future optimizations are working.

-----

### Phase 3: Optimization & Expansion (The Roadmap)

**Goal:** Evolve the single agent into the sophisticated, multi-agent system you envision. These are future tasks to be tackled after the foundation is solid.

  * [x] **3.1: Evolve to a Multi-Agent Orchestrator.**

      * **Action:** Design a `SpecialistAgent` base class.
      * **Action:** Add a second, local specialist model, using CPU offloading (`n_gpu_layers`) if VRAM becomes a concern.
      * **Action:** Enhance `orchestrator.py` with routing logic to delegate tasks to the correct agent, inspired by your legacy router.

  * [ ] **3.2: Implement DeepConf Optimization.**

      * **Action:** Modify your `agent.py` generation calls to request `logprobs`.
      * **Action:** Implement the confidence calculation and early-stopping logic from the research paper.
      * **Action:** Use your evaluation harness to measure the performance gains.

  * [ ] **3.3: Integrate the Cloud Bridge (MCP).**

      * **Action:** Re-implement the client for your Model Control Plane.
      * **Action:** Teach the orchestrator to call powerful cloud-based models for tasks that are too difficult for the local agents.

  * [ ] **3.4: Re-introduce the Memory Bus.**

      * **Action:** Implement a centralized logging and messaging system for inter-agent communication, based on your original `MessageBus` concept.
