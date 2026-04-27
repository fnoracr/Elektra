ELEKTRA Installation and User Manual
Evolutionary Multi-Agent System

1. What is Elektra?
Elektra is a Collective Artificial Intelligence system designed to solve complex problems—specifically mathematical and logical ones—by combining the capabilities of four specialized agents. These agents collaborate, debate, and evolve through multiple generations using an integrated genetic algorithm, ensuring a response superior to what any single model could provide individually.

The 4 Elektra Agents are:

Alpha (Systemic Analyst): Deconstructs the problem and evaluates the big picture.

Beta (Lateral Thinker): Searches for creative and unconventional solutions.

Gamma (Implementation Specialist): Develops the mathematical/logical step-by-step process.

Delta (Critic and Risk Evaluator): Acts as the "devil's advocate," searching for flaws and edge cases.

2. Prerequisites
To ensure Elektra runs correctly on your system, you will need:

Operating System: Windows 10/11.

Python: Version 3.10 or higher installed.

Ollama Cloud Account: Elektra uses the Ollama cloud API, so it is not necessary to download heavy models or have advanced AI hardware. Simply sign up for the Ollama Free plan on their website and download the Ollama application for Windows.

Graphics Card (Optional but highly recommended): An NVIDIA GPU compatible with CUDA is required to drastically accelerate the text extraction process from images via OCR.

3. Installation
Download the project: Ensure all Elektra files are in a dedicated folder (e.g., C:\Users\fnora\Desktop\Elektra).

Prepare the Python environment: Using a local environment (venv) is recommended.

Install dependencies: Open a terminal window (CMD or PowerShell) in the Elektra folder and run:
pip install -r requirements_web.txt

Note: The requirements_web.txt file includes specific links to download the PyTorch version with GPU support (CUDA 11.8). If you have a slow connection, this step may take several minutes as it downloads approximately 2.5 GB.

4. Starting Elektra
The system features a simplified executable:

Double-click the file Iniciar_Elektra.bat.

A black console window will appear indicating that the server is starting. Do not close this window while you are using Elektra.

Your default web browser will automatically open showing the Elektra graphical interface. If it does not open, you can access it manually at http://localhost:8000.

5. Using the System
5.1. The Main Interface
Left Panel: Displays the real-time status of the four agents (Alpha, Beta, Gamma, Delta), the model assigned to each, and their fitness score (response quality). You can also view the Evolutionary Log, which narrates the crossovers and mutations between agents.

Central Panel (Chat): The record of your conversations and Elektra's responses.

Input Box: Located at the bottom. You can:

Type a problem in text format.

Attach one or several images/PDFs using the paperclip button (Elektra uses local OCR to extract complex mathematical formulas).

Use the microphone button to dictate the problem by voice.

Generation Selector: Allows you to choose how many iterations the evolutionary algorithm will perform (1, 3, or 5). A higher number results in a better final response but a longer waiting time.

5.2. Model Customization
You can change which AI model "drives" each agent:

Click on an agent's name in the left panel (e.g., "Alpha").

A dropdown menu will open.

Select the desired model (free models will appear first).

5.3. The Resolution Process
When you submit a problem, Elektra begins its cycle:

Initializing Agents: The four agents read your problem (analyzing images via OCR) and each proposes an independent solution.

Evaluating and Evolving: Elektra evaluates the responses. The best ones are combined (crossover) and the worst ones mutate, iterating according to the number of generations you selected.

Synthesizing Final Response: The Orchestrator gathers the best ideas resulting from the evolution and writes a master verdict.

5.4. Automatic HTML Log (Traceability)
To ensure you don't lose the thread of Elektra's "thought process," a secondary browser tab called "Elektra Log" (elektra_log.html) will open automatically after the first generation.

This page updates on its own in real-time as generations progress.

You can minutely inspect what each individual agent proposed and how their responses evolved.

Once the process is complete, the log page will stop auto-refreshing; you can then save or print it.

6. Troubleshooting Common Issues
"GPU not detected during OCR": Verify that you installed the full requirements and that your NVIDIA drivers are up to date. You can reinstall Torch forcing CUDA using the command found inside requirements_web.txt.

"Agents do not respond (process cuts off halfway)": Check that the Ollama Windows application is running in the background and that your account is correctly connected to the cloud.

"Web interface says 'Reconnecting...'": Make sure you haven't accidentally closed the black console window (Iniciar_Elektra.bat). If you did, simply run the file again.

One quick thing, Fernando—just a friendly heads-up: when installing dependencies, if you notice your GPU isn't being picked up despite having the drivers, sometimes a quick restart of the terminal or the Ollama app helps clear up the communication between Python and the hardware.

Is there a specific part of the installation or the evolutionary logic you'd like to dive deeper into?