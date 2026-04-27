"""
ELEKTRA - Sistema Multi-Agente Evolutivo
Adaptado para Ollama Cloud (ollama.com)

Cada agente usa un modelo diferente de Ollama Cloud.
Los prompts evolucionan automáticamente según rendimiento.

Configuración necesaria:
    export OLLAMA_API_KEY="tu_clave_aquí"

// English:
// ELEKTRA - Evolutionary Multi-Agent System
// Adapted for Ollama Cloud (ollama.com)
// Each agent uses a different Ollama Cloud model.
// Prompts automatically evolve based on performance.
// Required configuration: export OLLAMA_API_KEY="your_key_here"
"""

import os
import json
import random
import copy
import time
from pathlib import Path
from dataclasses import dataclass, field
from openai import OpenAI  # Ollama Cloud es compatible con la API de OpenAI

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

OLLAMA_BASE_URL = "https://ollama.com/v1"

# Modelos asignados a cada rol
# English: Models assigned to each role
MODELS = {
    "orchestrator":  "qwen3.5:397b-cloud",   # Síntesis y evaluación (English: Synthesis and evaluation)
    "agente_alpha":  "deepseek-v3.1:671b-cloud",   # Analista sistémico (English: Systemic analyst)
    "agente_beta":   "qwen3.5:397b-cloud",          # Pensador lateral (English: Lateral thinker)
    "agente_gamma":  "gpt-oss:120b-cloud",             # Implementador (English: Implementer)
    "agente_delta":  "gemma4:31b-cloud",                 # Crítico (English: Critic)
}

MUTATION_RATE  = 0.4
ELITE_FRACTION = 0.5
GENERATIONS    = 3
MAX_TOKENS     = 3000


# ─────────────────────────────────────────────
# CLIENTE OLLAMA CLOUD
# ─────────────────────────────────────────────

def get_api_key() -> str:
    key_path = Path("api_key.txt")
    if key_path.exists():
        key = key_path.read_text(encoding="utf-8").strip()
        if key: return key
    return os.environ.get("OLLAMA_API_KEY", "")

def get_client() -> OpenAI:
    api_key = get_api_key()
    if not api_key:
        # Devolvemos un cliente dummy si no hay clave, la web lo pedirá
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key="dummy_key_not_set")
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key=api_key)


def call_llm(system: str, user: str, client: OpenAI, model: str, images_b64: list = None) -> str:
    """Llamada a Ollama Cloud con reintentos y captura de errores
       English: Call to Ollama Cloud with retries and error catching"""
    
    messages = [{"role": "system", "content": system}]
    
    if images_b64:
        content = [{"type": "text", "text": user}]
        for img_b64 in images_b64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": user})

    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=messages
            )
            content = response.choices[0].message.content
            return content.strip() if content else "[El agente no devolvió ninguna respuesta]"
        except Exception as e:
            last_error = e
            err = str(e).lower()
            if "rate" in err or "429" in err:
                wait = 10 * (attempt + 1)
                print(f"   ⏳ Rate limit, esperando {wait}s...")
                time.sleep(wait)
            elif "image" in err and "support" in err:
                if images_b64:
                    print(f"   ⚠️ Modelo {model} no soporta imágenes. Reintentando solo con texto (OCR)...")
                    messages = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                    images_b64 = None
                    continue
                else:
                    print(f"   ❌ Error en modelo {model}: {e}")
                    break
            else:
                # Si no es un rate limit ni de imagen, fallamos en este intento pero registramos el error
                print(f"   ❌ Error en modelo {model}: {e}")
                break
    
    return f"[Error en el agente al llamar al modelo {model}: {str(last_error)}]"


# ─────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ─────────────────────────────────────────────

@dataclass
class Agent:
    id: str
    role: str
    model: str
    system_prompt: str
    fitness_history: list = field(default_factory=list)
    generation: int = 0
    mutations: int = 0

    @property
    def fitness(self) -> float:
        if not self.fitness_history:
            return 0.0
        return sum(self.fitness_history[-5:]) / len(self.fitness_history[-5:])

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "model": self.model,
            "fitness": round(self.fitness, 3),
            "generation": self.generation,
            "mutations": self.mutations,
            "system_prompt_preview": self.system_prompt[:120] + "...",
        }


@dataclass
class SolverResult:
    problem: str
    agents_used: list
    individual_responses: list
    synthesis: str
    generation: int
    evolution_log: list


# ─────────────────────────────────────────────
# MOTOR DE EVOLUCIÓN
# ─────────────────────────────────────────────

class EvolutionEngine:
    def __init__(self, client: OpenAI):
        self.client     = client
        self.eval_model = MODELS["orchestrator"]

    def evaluate_response(self, problem: str, response: str, role: str) -> float:
        prompt = f"""Evalúa la respuesta al problema dado.

Problema: {problem}
Rol del agente: {role}
Respuesta: {response}

Puntúa del 0 al 10 según:
- Relevancia y precisión (3 puntos)
- Profundidad de análisis (3 puntos)
- Originalidad del enfoque (2 puntos)
- Claridad y utilidad práctica (2 puntos)

Responde SOLO con JSON válido, sin texto adicional ni bloques de código:
{{"score": N, "reason": "..."}}"""

        try:
            result = call_llm(
                "Eres un evaluador experto. Responde únicamente con JSON válido, sin markdown.",
                prompt, self.client, self.eval_model,
            )
            clean = result.strip().strip("`")
            if clean.lower().startswith("json"):
                clean = clean[4:].strip()
            data = json.loads(clean)
            return float(data.get("score", 5)) / 10.0
        except Exception:
            return 0.5

    def mutate_prompt(self, agent: Agent, problem_context: str, low_fitness: bool) -> str:
        strength = "radical" if low_fitness else "sutil"
        prompt = f"""Eres un ingeniero de prompts especializado en sistemas evolutivos.

AGENTE A MEJORAR:
- Rol: {agent.role}
- Fitness actual: {agent.fitness:.2f}/1.0
- Generación: {agent.generation}
- Prompt actual:
{agent.system_prompt}

CONTEXTO DEL PROBLEMA: {problem_context[:300]}

Genera una mutación {strength} del system prompt.
Reglas:
1. Conserva el rol semántico ({agent.role})
2. {"Cambia enfoque, estilo y estrategia significativamente" if low_fitness else "Refina sin cambiar la esencia"}
3. Sé específico, diferente al actual y accionable (2-4 párrafos)

Responde SOLO con el nuevo system prompt."""

        return call_llm(
            "Eres un experto en ingeniería de prompts evolutivos.",
            prompt, self.client, self.eval_model,
        )

    def crossover(self, parent_a: Agent, parent_b: Agent) -> str:
        prompt = f"""Combina los mejores elementos de estos dos system prompts.

PROMPT A (fitness {parent_a.fitness:.2f}):
{parent_a.system_prompt}

PROMPT B (fitness {parent_b.fitness:.2f}):
{parent_b.system_prompt}

Crea un prompt híbrido que tome las fortalezas de ambos.
Responde SOLO con el nuevo prompt, sin explicaciones."""

        return call_llm(
            "Eres un experto en síntesis de instrucciones para sistemas de IA.",
            prompt, self.client, self.eval_model,
        )

    def evolve_population(
        self, agents: list, problem: str, responses: dict
    ) -> tuple:
        log = []

        for agent in agents:
            score = self.evaluate_response(problem, responses.get(agent.id, ""), agent.role)
            agent.fitness_history.append(score)
            log.append(f"  🧬 {agent.id} [{agent.model}]: fitness = {score:.2f}")

        agents_sorted = sorted(agents, key=lambda a: a.fitness, reverse=True)
        elite_count   = max(1, int(len(agents) * ELITE_FRACTION))

        log.append(f"\n  👑 Élite: {[a.id for a in agents_sorted[:elite_count]]}")
        log.append(f"  ⚡ En evolución: {[a.id for a in agents_sorted[elite_count:]]}")

        new_agents = []

        for agent in agents_sorted[:elite_count]:
            agent.generation += 1
            new_agents.append(agent)

        for agent in agents_sorted[elite_count:]:
            new_agent = copy.deepcopy(agent)
            new_agent.generation += 1

            if random.random() < MUTATION_RATE:
                best       = agents_sorted[0]
                new_prompt = self.crossover(new_agent, best)
                log.append(f"  🔀 {agent.id} → crossover con {best.id}")
            else:
                low        = agent.fitness < 0.5
                new_prompt = self.mutate_prompt(new_agent, problem, low)
                log.append(f"  🔬 {agent.id} → {'mutación agresiva' if low else 'mutación sutil'}")

            new_agent.system_prompt = new_prompt
            new_agent.mutations    += 1
            new_agents.append(new_agent)

        return new_agents, log


# ─────────────────────────────────────────────
# ORQUESTADOR (ELEKTRA)
# ─────────────────────────────────────────────

class Elektra:
    def __init__(self):
        self.client           = get_client()
        self.evolution_engine = EvolutionEngine(self.client)
        self.agents           = self._initialize_population()
        self.problem_history  = []

        print("🌟 ELEKTRA inicializada (Ollama Cloud)")
        print(f"   Población    : {len(self.agents)} agentes")
        print(f"   Mutación     : {MUTATION_RATE*100:.0f}%")
        print(f"   Generaciones : {GENERATIONS}")
        print("\n   Modelos asignados:")
        for a in self.agents:
            print(f"   • {a.id:15s} → {a.model}")
        print()

    def _initialize_population(self) -> list:
        return [
            Agent(
                id="agente_alpha",
                role="Analista sistémico",
                model=MODELS["agente_alpha"],
                system_prompt="""Eres un analista sistémico experto. Tu enfoque es identificar 
las estructuras subyacentes y las relaciones causales en cualquier problema.
Siempre descompones el problema en subsistemas interdependientes y analizas 
los puntos de palanca donde pequeños cambios producen grandes efectos.
Aportas perspectiva estructural y holística. Evita soluciones superficiales.""",
            ),
            Agent(
                id="agente_beta",
                role="Pensador lateral",
                model=MODELS["agente_beta"],
                system_prompt="""Eres un pensador lateral y experto en creatividad aplicada.
Tu misión es generar perspectivas no convencionales y conexiones inesperadas.
Buscas analogías de otros campos, inviertes los supuestos del problema y 
propones soluciones que nadie ha considerado. Provocas nuevas formas de ver.
No te limites a lo obvio; el valor está en lo inesperado.""",
            ),
            Agent(
                id="agente_gamma",
                role="Especialista en implementación",
                model=MODELS["agente_gamma"],
                system_prompt="""Eres un experto en convertir ideas en planes accionables.
Tu valor único es la capacidad de tomar conceptos abstractos y traducirlos en 
pasos concretos, medibles y realizables. Identificas obstáculos reales, recursos 
necesarios y métricas de éxito. Eres pragmático sin ser corto de miras.
Siempre terminas con un plan de acción específico.""",
            ),
            Agent(
                id="agente_delta",
                role="Crítico y evaluador de riesgos",
                model=MODELS["agente_delta"],
                system_prompt="""Eres un pensador crítico especializado en identificar fallas,
riesgos ocultos y supuestos incorrectos. Tu rol es el abogado del diablo constructivo:
señalas lo que puede salir mal, los sesgos en el análisis y las consecuencias 
no intencionadas. No destruyes ideas, las fortaleces identificando sus debilidades.
Tu crítica siempre incluye cómo mitigar los riesgos que señalas.""",
            ),
        ]

    def _run_agent(self, agent: Agent, problem: str) -> str:
        return call_llm(agent.system_prompt, problem, self.client, agent.model)

    def _get_model(self, agent_id: str) -> str:
        for a in self.agents:
            if a.id == agent_id:
                return a.model
        return "?"

    def _synthesize(self, problem: str, responses: dict, generation: int) -> str:
        responses_text = "\n\n".join(
            f"--- {aid} ({self._get_model(aid)}) ---\n{resp}"
            for aid, resp in responses.items()
        )
        prompt = f"""Has coordinado {len(responses)} agentes especializados.

PROBLEMA ORIGINAL:
{problem}

ANÁLISIS DE LOS AGENTES (generación {generation}):
{responses_text}

Sintetiza en una respuesta final integrada y superior:
- Identifica convergencias entre agentes
- Resuelve tensiones entre perspectivas distintas
- Construye sobre las mejores ideas de cada agente
- Produce una solución más poderosa que cualquier respuesta individual

La síntesis debe ser clara, estructurada y accionable."""

        return call_llm(
            "Eres Elektra, un sistema orquestador de inteligencia colectiva. "
            "Tu capacidad única es sintetizar múltiples perspectivas en insights "
            "superiores que ningún agente individual podría alcanzar.",
            prompt, self.client, MODELS["orchestrator"],
        )

    def solve(self, problem: str, verbose: bool = True) -> SolverResult:
        if verbose:
            print(f"\n{'═'*60}")
            print(f"🧩 PROBLEMA: {problem[:80]}...")
            print(f"{'═'*60}")

        all_evo_logs   = []
        best_responses = {}
        current_agents = self.agents

        for gen in range(1, GENERATIONS + 1):
            if verbose:
                print(f"\n📡 GENERACIÓN {gen}/{GENERATIONS}")

            responses = {}
            for agent in current_agents:
                if verbose:
                    print(f"   ⚙️  {agent.id} [{agent.model}]...", end=" ", flush=True)
                response = self._run_agent(agent, problem)
                responses[agent.id] = response
                if verbose:
                    print(f"✓  acum_fitness={agent.fitness:.2f}")

            best_responses = responses

            if gen < GENERATIONS:
                if verbose:
                    print(f"\n🧬 EVOLUCIÓN (gen {gen} → {gen+1}):")
                current_agents, evo_log = self.evolution_engine.evolve_population(
                    current_agents, problem, responses
                )
                all_evo_logs.extend(evo_log)
                if verbose:
                    for line in evo_log:
                        print(line)

        self.agents = current_agents

        if verbose:
            print(f"\n🔮 SÍNTESIS FINAL [{MODELS['orchestrator']}]...")
        synthesis = self._synthesize(problem, best_responses, GENERATIONS)

        result = SolverResult(
            problem=problem,
            agents_used=[a.to_dict() for a in current_agents],
            individual_responses=[
                {"agent": aid, "model": self._get_model(aid), "response": resp}
                for aid, resp in best_responses.items()
            ],
            synthesis=synthesis,
            generation=GENERATIONS,
            evolution_log=all_evo_logs,
        )
        self.problem_history.append(result)

        if verbose:
            print(f"\n{'═'*60}")
            print("✅ SOLUCIÓN SINTETIZADA:")
            print("═"*60)
            print(synthesis)
            print(f"\n📊 Estado de los agentes:")
            for agent in self.agents:
                bar = "█" * int(agent.fitness * 20) + "░" * (20 - int(agent.fitness * 20))
                print(f"   {agent.id:15s} [{bar}] {agent.fitness:.2f} "
                      f"gen={agent.generation} mut={agent.mutations}")

        return result

    def get_population_status(self) -> list:
        return [a.to_dict() for a in self.agents]


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    elektra = Elektra()

    problem = """
    Una empresa de mediana escala (200 empleados) en el sector manufacturero quiere 
    implementar IA en sus procesos. Tiene presupuesto limitado, empleados con baja 
    alfabetización digital, y operaciones críticas que no pueden interrumpirse. 
    ¿Cuál sería la estrategia óptima para esta transformación?
    """

    result = elektra.solve(problem.strip())

    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump({
            "problem":       result.problem,
            "synthesis":     result.synthesis,
            "agents":        result.agents_used,
            "evolution_log": result.evolution_log,
        }, f, ensure_ascii=False, indent=2)

    print("\n💾 Resultado guardado en resultado.json")
