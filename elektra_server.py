"""
ELEKTRA - Servidor Web
FastAPI + WebSockets para la interfaz de navegador

Instalar:
    pip install fastapi uvicorn python-multipart openai

Ejecutar:
    python elektra_server.py
    Luego abrir: http://localhost:8000

// English:
// ELEKTRA - Web Server
// FastAPI + WebSockets for the browser interface
// Install: pip install fastapi uvicorn python-multipart openai
// Run: python elektra_server.py
// Then open: http://localhost:8000
"""

import os
import json
import base64
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importar Elektra (asegúrate de que elektra_ollama.py está en la misma carpeta)
# English: Import Elektra (make sure elektra_ollama.py is in the same folder)
from elektra_ollama import Elektra, MODELS, call_llm, get_client

import time
import datetime
import html as html_lib

log_updated_at = time.time()

def generate_html_report(problem, history, total_generations, is_finished=False, synthesis=""):
    global log_updated_at
    log_updated_at = time.time()
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Elektra Log</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
'''
    if not is_finished:
        html += '''
<script>
  let initTime = null;
  setInterval(() => {
    fetch('http://localhost:8000/log_status')
      .then(r => r.json())
      .then(data => {
        if (initTime === null) {
          initTime = data.updated_at;
        } else if (data.updated_at !== initTime) {
          location.reload();
        }
      }).catch(e => {});
  }, 2000);
</script>
'''
        
    html += '''<style>
    body { background: #080c0f; color: #c8dce8; font-family: 'JetBrains Mono', monospace; padding: 20px; line-height: 1.6; }
    h1 { font-family: 'Syne', sans-serif; color: #00e5c0; text-shadow: 0 0 20px rgba(0,229,192,0.5); }
    h2 { color: #0077ff; border-bottom: 1px solid #1e2d3a; padding-bottom: 5px; margin-top: 30px; }
    .problem { background: #111820; border: 1px solid #1e2d3a; padding: 15px; border-radius: 8px; white-space: pre-wrap; margin-bottom: 20px; }
    .generation { margin-bottom: 40px; padding: 20px; border: 1px solid #1e2d3a; border-radius: 12px; background: #0d1419; }
    .agent-resp { background: #111820; border-left: 4px solid #00e5c0; padding: 15px; margin: 10px 0; border-radius: 4px; }
    .agent-name { font-weight: bold; color: #00e5c0; font-size: 14px; text-transform: uppercase; margin-bottom: 10px; }
    .evo-log { background: #0a0e12; color: #4a6070; padding: 15px; font-size: 12px; border-radius: 6px; white-space: pre-wrap; margin-top: 15px; border: 1px dashed #1e2d3a; }
    .synthesis { background: linear-gradient(135deg, #041a14, #062420); border: 1px solid rgba(0,229,192,0.25); box-shadow: 0 0 20px rgba(0,229,192,0.1); padding: 20px; border-radius: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>ELEKTRA — Reporte de Resolución</h1>
    <div style="font-size: 12px; color: #4a6070; margin-bottom: 20px;">''' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</div>
    
    <h2>Problema Original</h2>
    <div class="problem">''' + html_lib.escape(problem) + '''</div>
'''
    
    for h in history:
        gen = h["generation"]
        html += f'\n    <div class="generation">\n      <h2>Generación {gen} de {total_generations}</h2>\n'
        for agent_id, resp in h["responses"].items():
            html += f'''
      <div class="agent-resp">
        <div class="agent-name">{html_lib.escape(agent_id.replace('agente_',''))}</div>
        <div style="white-space: pre-wrap;">{html_lib.escape(resp)}</div>
      </div>'''
        
        if h.get("evolution_log"):
            log_text = "\n".join(h["evolution_log"])
            html += f'\n      <div class="evo-log"><strong>Log de Evolución:</strong>\n{html_lib.escape(log_text)}</div>'
            
        html += '\n    </div>'
        
    if synthesis:
        html += f'''
    <div class="synthesis">
      <h2 style="color: #00e5c0; border-bottom: none; margin-top: 0;">SÍNTESIS FINAL</h2>
      <div style="white-space: pre-wrap;">{html_lib.escape(synthesis)}</div>
    </div>'''
        
    html += '''
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']], processEscapes: true },
  svg: { fontCache: 'global' }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</body>
</html>'''    
    try:
        with open("elektra_log.html", "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print("Error escribiendo log html:", e)

app = FastAPI(title="Elektra Web")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    import os
    if os.path.exists("Elektra.JPG"):
        return FileResponse("Elektra.JPG")
    elif os.path.exists("Nora.JPG"):
        return FileResponse("Nora.JPG")
    return JSONResponse(status_code=404, content={"message": "Not Found"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Estado global
# ─────────────────────────────────────────────

elektra_instance: Optional[Elektra] = None
active_connections: list[WebSocket] = []


def get_elektra() -> Elektra:
    global elektra_instance
    if elektra_instance is None:
        elektra_instance = Elektra()
    return elektra_instance


# ─────────────────────────────────────────────
# WebSocket — canal principal de comunicación
# ─────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "solve":
                await handle_solve(websocket, data)

            elif msg_type == "set_model":
                agent_id = data.get("agent_id")
                model = data.get("model")
                if agent_id and model:
                    elektra = get_elektra()
                    for a in elektra.agents:
                        if a.id == agent_id:
                            a.model = model
                            break
                    await websocket.send_json({"type": "status", "agents": elektra.get_population_status(), "problems_solved": len(elektra.problem_history)})

            elif msg_type == "status":
                elektra = get_elektra()
                await websocket.send_json({
                    "type": "status",
                    "agents": elektra.get_population_status(),
                    "problems_solved": len(elektra.problem_history),
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def handle_solve(websocket: WebSocket, data: dict):
    """Ejecuta Elektra y va enviando actualizaciones en tiempo real"""
    problem     = data.get("problem", "")
    generations = int(data.get("generations", 3))
    files_data  = data.get("files", [])   # [{name, type, base64}]

    if not problem.strip():
        await websocket.send_json({"type": "error", "message": "El problema está vacío."})
        return

    images_b64 = []
    # Añadir contexto de ficheros al problema
    if files_data:
        file_context = "\n\n[ARCHIVOS ADJUNTOS]\n"
        for f in files_data:
            if f.get("base64") and f["type"].startswith("image/"):
                images_b64.append(f["base64"])
            
            file_context += f"\n— Texto extraído por OCR de {f['name']} ({f['type']})"
            if f.get("text"):
                file_context += f":\n{f['text'][:3000]}"
            else:
                file_context += f":\n[No se pudo extraer texto. El agente debe basarse en la imagen enviada si tiene capacidades de visión.]"
        problem = problem + file_context

    await websocket.send_json({"type": "start", "generations": generations})

    elektra = get_elektra()

    # Parchear GENERATIONS temporalmente
    import elektra_ollama as em
    em.GENERATIONS = generations

    # Ejecutar en un hilo para no bloquear el event loop
    loop = asyncio.get_event_loop()

    def run_solve():
        results_log = []

        class StreamingElektra(Elektra):
            """Subclase que emite eventos durante la ejecución"""
            pass

        # Usamos la instancia existente pero capturamos el progreso
        # enviando mensajes síncronos desde el hilo
        import copy, random
        from elektra_ollama import call_llm, EvolutionEngine, MODELS

        current_agents = copy.deepcopy(elektra.agents)
        best_responses = {}
        evolution_history = []

        for gen in range(1, generations + 1):
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({"type": "generation_start", "gen": gen, "total": generations}),
                loop
            )

            responses = {}
            for agent in current_agents:
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "agent_thinking",
                        "agent_id": agent.id,
                        "role": agent.role,
                        "model": agent.model,
                    }),
                    loop
                )
                response = call_llm(agent.system_prompt, problem, elektra.client, agent.model, images_b64=images_b64)
                responses[agent.id] = response
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "agent_done",
                        "agent_id": agent.id,
                        "response": response,
                        "fitness": round(agent.fitness, 2),
                    }),
                    loop
                )

                # Generar HTML cada vez que un agente termina
                temp_history = list(evolution_history)
                temp_history.append({
                    "generation": gen,
                    "responses": responses.copy(),
                    "evolution_log": []
                })
                generate_html_report(problem, temp_history, generations, is_finished=False)
                
                if gen == 1 and len(responses) == 1:
                    import webbrowser
                    webbrowser.open("http://localhost:8000/log")

            best_responses = responses

            if gen < generations:
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({"type": "evolving"}),
                    loop
                )
                engine = EvolutionEngine(elektra.client)
                current_agents, evo_log = engine.evolve_population(
                    current_agents, problem, responses
                )
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "evolution_done",
                        "log": evo_log,
                        "agents": [a.to_dict() for a in current_agents],
                    }),
                    loop
                )
            else:
                evo_log = []
            
            # GUARDAR HISTORIAL Y GENERAR HTML
            evolution_history.append({
                "generation": gen,
                "responses": responses,
                "evolution_log": evo_log
            })
            generate_html_report(problem, evolution_history, generations, is_finished=False)

        # Síntesis final
        asyncio.run_coroutine_threadsafe(
            websocket.send_json({"type": "synthesizing"}),
            loop
        )

        responses_text = "\n\n".join(
            f"--- {aid} ---\n{resp}" for aid, resp in best_responses.items()
        )
        synthesis_prompt = f"""Has coordinado {len(best_responses)} agentes especializados.

PROBLEMA ORIGINAL:
{problem}

ANÁLISIS DE LOS AGENTES:
{responses_text}

Sintetiza en una respuesta final integrada, clara y accionable."""

        synthesis = call_llm(
            "Eres Elektra, un sistema orquestador de inteligencia colectiva.",
            synthesis_prompt,
            elektra.client,
            MODELS["orchestrator"],
            images_b64=images_b64
        )

        # Actualizar instancia global con los agentes evolucionados
        elektra.agents = current_agents

        # GENERAR HTML FINAL
        generate_html_report(problem, evolution_history, generations, is_finished=True, synthesis=synthesis)

        asyncio.run_coroutine_threadsafe(
            websocket.send_json({
                "type": "synthesis",
                "text": synthesis,
                "agents": [a.to_dict() for a in current_agents],
            }),
            loop
        )

    await loop.run_in_executor(None, run_solve)


# ─────────────────────────────────────────────
# API REST — subida de ficheros con extracción de texto
# ─────────────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Recibe un fichero y extrae su texto si es posible"""
    content = await file.read()
    mime    = file.content_type or ""
    name    = file.filename or "archivo"
    text    = None

    try:
        if mime.startswith("text/") or name.endswith((".txt", ".md", ".csv", ".py", ".js", ".json")):
            text = content.decode("utf-8", errors="replace")[:5000]
        elif mime.startswith("image/") or mime == "application/pdf" or name.endswith(".pdf"):
            import tempfile
            import os
            from elektra_ocr import run_local_ocr
            import asyncio
            
            # Guardar el contenido temporalmente
            ext = "." + name.split(".")[-1] if "." in name else (".pdf" if mime == "application/pdf" else ".jpg")
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
                
            try:
                # Ejecutar OCR local en un hilo para no bloquear el servidor
                text = await asyncio.to_thread(run_local_ocr, tmp_path)
            except Exception as ve:
                text = f"[Error en OCR local: {ve}]"
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    except Exception as e:
        text = f"[Error al procesar: {e}]"

    b64 = base64.b64encode(content).decode()

    return JSONResponse({
        "name": name,
        "type": mime,
        "size": len(content),
        "base64": b64,
        "text": text,
    })


# ─────────────────────────────────────────────
# API REST — Configuración y Modelos
# ─────────────────────────────────────────────

class KeyUpdate(BaseModel):
    key: str

@app.get("/api/key")
async def get_key_status():
    from elektra_ollama import get_api_key
    key = get_api_key()
    has_key = bool(key and key != "dummy_key_not_set")
    return {"has_key": has_key, "preview": f"...{key[-4:]}" if has_key and len(key) > 4 else ""}

@app.post("/api/key")
async def update_key(data: KeyUpdate):
    global elektra_instance
    with open("api_key.txt", "w", encoding="utf-8") as f:
        f.write(data.key.strip())
    # Forzar reinicio de cliente
    elektra_instance = Elektra()
    return {"status": "ok"}

@app.get("/api/models")
async def get_models():
    elektra = get_elektra()
    try:
        response = elektra.client.models.list()
        all_models = sorted([m.id for m in response.data], key=lambda x: x.lower())
        
        # Heurística simple: qwen y deepseek son free, el resto de pago (o los marcamos así por defecto para cumplir el requisito)
        free_keywords = ["free", "qwen", "deepseek"]
        
        models_data = []
        for m in all_models:
            is_free = any(k in m.lower() for k in free_keywords)
            models_data.append({
                "id": m,
                "is_free": is_free,
                "tier_label": "Free" if is_free else "Pago"
            })
            
        # Ordenar: primero los gratuitos, luego los de pago, ambos alfabéticos internamente
        models_data.sort(key=lambda x: (not x["is_free"], x["id"].lower()))
        return models_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/agents")
async def get_agents():
    elektra = get_elektra()
    return elektra.get_population_status()

@app.get("/log_status")
async def get_log_status():
    global log_updated_at
    return {"updated_at": log_updated_at}

@app.get("/log", response_class=HTMLResponse)
async def serve_log():
    try:
        if os.path.exists("elektra_log.html"):
            with open("elektra_log.html", "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
    except:
        pass
    return HTMLResponse("<h1>Log no disponible aún. Espera un momento...</h1>")


# ─────────────────────────────────────────────
# Servir la interfaz web
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path(__file__).parent / "elektra_web.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>elektra_web.html no encontrado</h1>")


# ─────────────────────────────────────────────
# Arranque
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("🌟 Iniciando ELEKTRA Web Server...")
    print("   Abre tu navegador en: http://localhost:8000\n")
    uvicorn.run("elektra_server:app", host="0.0.0.0", port=8000, reload=False)
