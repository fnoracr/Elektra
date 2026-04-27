# Elektra
Sistema Multi-Agente Evolutivo /  Evolutionary Multi-Agent System

En Español (below in English)
## ⚡ ¿Qué es Elektra?

ELEKTRA es un sistema de **Inteligencia Artificial Colectiva** que coordina múltiples agentes LLM. Estos agentes **evolucionan automáticamente** sus instrucciones (prompts) para resolver problemas complejos (especialmente matemáticos y lógicos) de forma iterativa, superando las capacidades de cualquier modelo individual.

```text
Problema → [Agentes Gen.1] → Evaluación → Evolución → [Agentes Gen.2] → ... → Síntesis Final
```

### 🧠 Los 4 Agentes Especializados

| Agente | Rol                  | Especialidad                                                      |
|--------|----------------------|-------------------------------------------------------------------|
| `alpha` | Analista Sistémico  | Descomposición y evaluación del panorama general                  |
| `beta`  | Pensador Lateral    | Búsqueda de soluciones creativas y perspectivas no convencionales |
| `gamma` | Implementador       | Desarrollo del paso a paso matemático/lógico accionable           |
| `delta` | Crítico y Evaluador | Abogado del diablo, búsqueda de fallos y casos límite             |

### 🧬 Mecanismo Evolutivo

El sistema utiliza un **Algoritmo Genético Semántico** para mejorar las instrucciones de los agentes en cada ronda. A diferencia de los algoritmos genéticos clásicos que alteran bits al azar, Elektra utiliza un LLM como "Motor Evolutivo" para realizar modificaciones semánticas e inteligentes en los *System Prompts* (el "genoma" del agente).

El proceso en cada generación es el siguiente:
1. **Evaluación (Fitness):** Todos los agentes responden al problema (incluyendo OCR si hay imágenes). Un modelo Juez-Orquestador evalúa la respuesta en parámetros de precisión, profundidad, originalidad y claridad, asignándole una puntuación de 0 a 1.
2. **Selección Natural (Élite):** El 50% de los agentes con mejor puntuación conforman la "élite". Sobreviven y pasan a la siguiente generación intactos.
3. **Evolución del resto:** El 50% de los agentes de menor rendimiento evolucionan de dos formas:
   * **Mutación:** El Motor Evolutivo reescribe sus instrucciones. Si el rendimiento fue muy bajo, aplica una mutación *radical* cambiando la estrategia. Si fue decente, aplica una mutación *sutil* para pulir errores.
   * **Crossover (Cruce):** El Motor Evolutivo cruza las instrucciones del agente de bajo rendimiento con las del agente líder (el de mayor *fitness* de la generación). Se leen ambos System Prompts y se genera un **híbrido semántico** que hereda y fusiona las mejores características, tácticas y perspectivas de ambos "padres".

---

## ✨ Características Principales

* **Interfaz Web Completa:** Incluye chat, selector de modelos por agente y visualizador de estado en tiempo real.
* **Soporte OCR Local Acelerado:** Extrae fórmulas matemáticas complejas de imágenes y PDFs usando tu GPU (PyTorch/CUDA).
* **Ollama Cloud Integration:** No necesitas descargar modelos LLM pesados en tu PC, Elektra se conecta a la nube de Ollama de forma transparente.
* **Trazabilidad Total:** Genera un archivo log HTML en vivo para seguir paso a paso la evolución del "pensamiento" de la IA.

---

## 🚀 Requisitos e Instalación

### Requisitos Previos
* **OS:** Windows 10/11
* **Python:** 3.10+
* **Cuenta Ollama Cloud:** Para procesar los LLMs (Plan Free). Descarga la app de Ollama para Windows.
* **GPU (Recomendado):** Tarjeta NVIDIA compatible con CUDA 11.8+ para acelerar el OCR.

### Instalación

Clona el repositorio o descarga los archivos y ejecuta en la carpeta del proyecto:

```bash
pip install -r requirements_web.txt
```
*(Nota: El archivo de requisitos descargará PyTorch con soporte CUDA para el OCR).*

### Uso

Para iniciar la interfaz gráfica de forma sencilla, haz doble clic en:
**`Iniciar_Elektra.bat`**

Esto abrirá la consola del servidor de Python y lanzará automáticamente tu navegador web en `http://localhost:8000`.

---

## 🏗️ Arquitectura del Sistema

```text
┌─────────────────────────────────────────────────┐
│                   ELEKTRA                       │
│              (Orquestadora)                     │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Agente  │  │  Agente  │  │    Motor de  │   │
│  │  Alpha   │  │   Beta   │  │  Evolución   │   │
│  │  Gamma   │  │  Delta   │  │  (Mutación + │   │
│  └──────────┘  └──────────┘  │  Crossover)  │   │
│       │             │        └──────────────┘   │
│       └──────┬──────┘               │           │
│              ▼                      │           │
│         Síntesis Final ◄────────────┘           │
└─────────────────────────────────────────────────┘
```

### 📂 Estructura de Archivos
* **`elektra_ollama.py`**: El "cerebro" del sistema. Contiene el Motor Evolutivo, la definición de los agentes y la conexión con la API de Ollama Cloud.
* **`elektra_server.py`**: El servidor web (FastAPI). Sirve la interfaz web, maneja las conexiones en tiempo real (WebSockets) y genera el archivo de reporte `elektra_log.html`. **Es vital para la interfaz gráfica.**
* **`elektra_web.html`**: El "rostro" del proyecto. Contiene la interfaz gráfica interactiva, el chat y el panel de control de agentes.
* **`elektra_ocr.py`**: Módulo local que utiliza Nougat (PyTorch) para extraer fórmulas matemáticas complejas desde PDFs e imágenes.
* **`elektra_cli.py`**: Una interfaz alternativa y minimalista de línea de comandos (Terminal) para usuarios avanzados o despliegues sin interfaz gráfica.

---

## 📜 Licencia y Autoría
Eres libre de distribuir este proyecto como quieras, sin embargo te pido que mantengas mi nombre y reconozcas que la idea original es de Fernando José Nora Costa-Ribeiro (fnoracr@gmail.com).

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

In Inglish:

⚡ What is Elektra?
ELEKTRA is a Collective Artificial Intelligence system that coordinates multiple LLM agents. These agents automatically evolve their instructions (prompts) to solve complex problems (especially mathematical and logical ones) iteratively, surpassing the capabilities of any individual model.

Problem → [Gen.1 Agents] → Evaluation → Evolution → [Gen.2 Agents] → ... → Final Synthesis

🧠 The 4 Specialized Agents
Agent  Role                Specialty
alpha  Systemic Analyst    Decomposition and evaluation of the big picture
beta   Lateral Thinker     Search for creative solutions and unconventional perspectives
gamma  Implementer         Development of actionable mathematical/logical step-by-step
delta  Critic & Evaluator  Devil’s advocate, searching for flaws and edge cases

🧬 Evolutionary Mechanism
The system utilizes a Semantic Genetic Algorithm to improve agent instructions in each round. Unlike classic genetic algorithms that alter bits randomly, Elektra uses an LLM as an "Evolutionary Engine" to perform semantic and intelligent modifications to the System Prompts (the agent's "genome").

The process in each generation is as follows:

Evaluation (Fitness): All agents respond to the problem (including OCR if images are present). An Orchestrator-Judge model evaluates the response based on parameters of accuracy, depth, originality, and clarity, assigning it a score from 0 to 1.

Natural Selection (Elite): The top 50% of agents with the highest scores make up the "elite." They survive and move to the next generation intact.

Evolution of the Rest: The 50% lower-performing agents evolve in two ways:

Mutation: The Evolutionary Engine rewrites their instructions. If performance was very low, it applies a radical mutation by changing the strategy. If it was decent, it applies a subtle mutation to polish errors.

Crossover: The Evolutionary Engine crosses the instructions of the low-performing agent with those of the leading agent (the one with the highest fitness of the generation). Both System Prompts are read, and a semantic hybrid is generated that inherits and merges the best features, tactics, and perspectives of both "parents."

✨ Main Features
Full Web Interface: Includes chat, model selector per agent, and real-time status visualizer.

Accelerated Local OCR Support: Extracts complex mathematical formulas from images and PDFs using your GPU (PyTorch/CUDA).

Ollama Cloud Integration: No need to download heavy LLM models to your PC; Elektra connects seamlessly to the Ollama cloud.

Total Traceability: Generates a live HTML log file to follow the evolution of the AI's "thinking" step by step.

🚀 Requirements and Installation
Prerequisites
OS: Windows 10/11

Python: 3.10+

Ollama Cloud Account: To process the LLMs (Free Plan). Download the Ollama app for Windows.

GPU (Recommended): NVIDIA card compatible with CUDA 11.8+ to accelerate OCR.

Installation
Clone the repository or download the files and run the following in the project folder:

Bash
pip install -r requirements_web.txt
(Note: The requirements file will download PyTorch with CUDA support for OCR).

Usage
To easily launch the graphical interface, double-click:
Iniciar_Elektra.bat

This will open the Python server console and automatically launch your web browser at http://localhost:8000.

🏗️ System Architecture
Plaintext
┌─────────────────────────────────────────────────┐
│                    ELEKTRA                      │
│                 (Orchestrator)                  │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Agent   │  │  Agent   │  │ Evolution    │   │
│  │  Alpha   │  │  Beta    │  │   Engine     │   │
│  │  Gamma   │  │  Delta   │  │ (Mutation +  │   │
│  └──────────┘  └──────────┘  │  Crossover)  │   │
│        │              │      └──────────────┘   │
│        └──────┬───────┘              │          │
│               ▼                      │          │
│        Final Synthesis ◄─────────────┘          │
└─────────────────────────────────────────────────┘
📂 File Structure
elektra_ollama.py: The "brain" of the system. Contains the Evolutionary Engine, the definition of the agents, and the connection to the Ollama Cloud API.

elektra_server.py: The web server (FastAPI). Serves the web interface, handles real-time connections (WebSockets), and generates the elektra_log.html report file. It is vital for the graphical interface.

elektra_web.html: The "face" of the project. Contains the interactive graphical interface, chat, and agent control panel.

elektra_ocr.py: Local module using Nougat (PyTorch) to extract complex mathematical formulas from PDFs and images.

elektra_cli.py: An alternative and minimalist Command Line Interface (Terminal) for advanced users or deployments without a graphical interface.

📜 License and Authorship
You are free to distribute this project as you wish; however, I ask that you keep my name and acknowledge that the original idea belongs to Fernando José Nora Costa-Ribeiro (fnoracr@gmail.com).

