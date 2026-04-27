import re

with open("elektra_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add the generate_html_report function
html_report_func = """import os
import datetime
import html as html_lib

def generate_html_report(problem, history, total_generations, is_finished=False, synthesis=""):
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Elektra Log</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
'''
    if not is_finished:
        html += '<meta http-equiv="refresh" content="3">\\n'
        
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
        html += f'\\n    <div class="generation">\\n      <h2>Generación {gen} de {total_generations}</h2>\\n'
        for agent_id, resp in h["responses"].items():
            html += f'''
      <div class="agent-resp">
        <div class="agent-name">{html_lib.escape(agent_id.replace('agente_',''))}</div>
        <div style="white-space: pre-wrap;">{html_lib.escape(resp)}</div>
      </div>'''
        
        if h.get("evolution_log"):
            log_text = "\\n".join(h["evolution_log"])
            html += f'\\n      <div class="evo-log"><strong>Log de Evolución:</strong>\\n{html_lib.escape(log_text)}</div>'
            
        html += '\\n    </div>'
        
    if synthesis:
        html += f'''
    <div class="synthesis">
      <h2 style="color: #00e5c0; border-bottom: none; margin-top: 0;">SÍNTESIS FINAL</h2>
      <div style="white-space: pre-wrap;">{html_lib.escape(synthesis)}</div>
    </div>'''
        
    html += "\\n</body>\\n</html>"
    
    with open("elektra_log.html", "w", encoding="utf-8") as f:
        f.write(html)

"""

if "def generate_html_report" not in content:
    content = content.replace("app = FastAPI()", html_report_func + "\napp = FastAPI()")

# Find run_solve
run_solve_body = r"""
        current_agents = copy.deepcopy(elektra.agents)
        best_responses = {}
        evolution_history = []

        for gen in range(1, generations \+ 1):"""

if "evolution_history = []" not in content:
    content = re.sub(
        r"        current_agents = copy.deepcopy\(elektra.agents\)\n        best_responses = \{\}\n\n        for gen in range\(1, generations \+ 1\):",
        "        current_agents = copy.deepcopy(elektra.agents)\n        best_responses = {}\n        evolution_history = []\n\n        for gen in range(1, generations + 1):",
        content
    )


# Where evolution loop ends
evo_end_pattern = r"""                asyncio.run_coroutine_threadsafe\(
                    websocket.send_json\(\{
                        "type": "evolution_done",
                        "log": evo_log,
                        "agents": \[a.to_dict\(\) for a in current_agents\],
                    \}\),
                    loop
                \)"""

new_evo_end = """                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "evolution_done",
                        "log": evo_log,
                        "agents": [a.to_dict() for a in current_agents],
                    }),
                    loop
                )
            
            # GUARDAR HISTORIAL Y GENERAR HTML
            evolution_history.append({
                "generation": gen,
                "responses": responses,
                "evolution_log": evo_log if gen < generations else []
            })
            generate_html_report(problem, evolution_history, generations, is_finished=False)
            
            if gen == 1:
                import webbrowser
                webbrowser.open("file://" + os.path.abspath("elektra_log.html"))"""

if "evolution_history.append(" not in content:
    content = re.sub(evo_end_pattern, new_evo_end, content)

# End of synthesis
synthesis_end_pattern = r"""        elektra.agents = current_agents

        asyncio.run_coroutine_threadsafe\("""

new_synthesis_end = """        elektra.agents = current_agents

        # GENERAR HTML FINAL
        generate_html_report(problem, evolution_history, generations, is_finished=True, synthesis=synthesis)

        asyncio.run_coroutine_threadsafe("""

if "GENERAR HTML FINAL" not in content:
    content = re.sub(synthesis_end_pattern, new_synthesis_end, content)

with open("elektra_server.py", "w", encoding="utf-8") as f:
    f.write(content)
print("patched")
