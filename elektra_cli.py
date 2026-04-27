"""
ELEKTRA CLI - Interfaz interactiva para el sistema multi-agente evolutivo
"""

import sys
import json
from elektra_ollama import Elektra

def banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    ███████╗██╗     ███████╗██╗  ██╗████████╗██████╗ █████╗ ║
║    ██╔════╝██║     ██╔════╝██║ ██╔╝╚══██╔══╝██╔══██╗██╔══██╗║
║    █████╗  ██║     █████╗  █████╔╝    ██║   ██████╔╝███████║║
║    ██╔══╝  ██║     ██╔══╝  ██╔═██╗    ██║   ██╔══██╗██╔══██║║
║    ███████╗███████╗███████╗██║  ██╗   ██║   ██║  ██║██║  ██║║
║    ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝║
║                                                          ║
║     Sistema Multi-Agente Evolutivo  •  v1.0              ║
║     Inspirado en "Cama y Fonda" de F.J. Nora Costa       ║
╚══════════════════════════════════════════════════════════╝
""")

def menu():
    print("\n┌─────────────────────────────────────┐")
    print("│  ¿Qué quieres hacer?                │")
    print("│                                     │")
    print("│  [1] Resolver un problema            │")
    print("│  [2] Ver estado de los agentes       │")
    print("│  [3] Ver historial de problemas      │")
    print("│  [4] Ver modelos disponibles         │")
    print("│  [5] Salir                           │")
    print("└─────────────────────────────────────┘")
    return input("→ ").strip()

def show_agents(elektra):
    print("\n📊 ESTADO ACTUAL DE LOS AGENTES")
    print("─" * 50)
    for agent in elektra.get_population_status():
        bar_len = int(agent['fitness'] * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"\n  {agent['id']}")
        print(f"  Rol:       {agent['role']}")
        print(f"  Fitness:   [{bar}] {agent['fitness']:.2f}")
        print(f"  Generación: {agent['generation']}  |  Mutaciones: {agent['mutations']}")
        print(f"  Prompt:    {agent['system_prompt_preview']}")

def show_history(elektra):
    if not elektra.problem_history:
        print("\n  (No hay problemas resueltos aún)")
        return
    print(f"\n📚 HISTORIAL ({len(elektra.problem_history)} problemas)")
    for i, result in enumerate(elektra.problem_history, 1):
        print(f"\n  [{i}] {result.problem[:80]}...")
        print(f"       Generaciones: {result.generation} | Agentes: {len(result.agents_used)}")

def main():
    banner()
    print("Inicializando sistema...")
    elektra = Elektra()

    while True:
        choice = menu()

        if choice == "1":
            print("\n📝 Describe el problema a resolver")
            print("   (puedes escribir varias líneas, termina con una línea vacía)\n")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            problem = " ".join(lines).strip()

            if not problem:
                print("  ⚠️  Problema vacío, cancelando.")
                continue

            print("\n📎 ¿Deseas adjuntar una imagen o PDF con enunciados matemáticos?")
            print("   (Introduce la ruta del archivo o presiona Enter para saltar): ", end="")
            file_path = input().strip()
            
            if file_path:
                try:
                    import os
                    from elektra_ocr import run_local_ocr
                    
                    if not os.path.exists(file_path):
                        print(f"  ❌ No se encontró el archivo: {file_path}")
                    else:
                        ext = file_path.lower().split('.')[-1]
                        file_text = ""
                        
                        if ext in ['png', 'jpg', 'jpeg', 'webp', 'pdf']:
                            file_text = run_local_ocr(file_path)
                        else:
                            try:
                                with open(file_path, "rb") as f:
                                    file_text = f.read().decode("utf-8")
                            except:
                                print("  ⚠️ Formato no soportado para Lectura plana.")
                        
                        if file_text:
                            problem += f"\n\n[ARCHIVO ADJUNTO: {os.path.basename(file_path)}]\n{file_text}"
                            print("  ✅ Archivo procesado y adjuntado al contexto.")
                except Exception as e:
                    print(f"  ❌ Error al procesar el archivo: {e}")

            print(f"\n  ¿Cuántas generaciones? (1-5, Enter para usar {3}): ", end="")
            gens_input = input().strip()
            try:
                import elektra_ollama as e_module
                e_module.GENERATIONS = int(gens_input) if gens_input else 3
                e_module.GENERATIONS = max(1, min(5, e_module.GENERATIONS))
            except Exception:
                pass

            result = elektra.solve(problem)

            print("\n💾 ¿Guardar resultado? (s/n): ", end="")
            if input().strip().lower() == "s":
                fname = f"resultado_{len(elektra.problem_history)}.json"
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump({
                        "problem": result.problem,
                        "synthesis": result.synthesis,
                        "agents": result.agents_used,
                        "evolution_log": result.evolution_log,
                        "individual_responses": result.individual_responses
                    }, f, ensure_ascii=False, indent=2)
                print(f"  ✅ Guardado en {fname}")

        elif choice == "2":
            show_agents(elektra)

        elif choice == "3":
            show_history(elektra)

        elif choice == "4":
            print("\n  Buscando modelos en Ollama Cloud...")
            try:
                models = elektra.client.models.list()
                print(f"  ✅ {len(models.data)} modelos encontrados:")
                for m in models.data:
                    print(f"      - {m.id}")
            except Exception as e:
                print(f"  ❌ Error al obtener modelos: {e}")

        elif choice == "5":
            print("\n  Hasta pronto. «Hola. Me llamo Elektra. ¿Podemos charlar?»\n")
            sys.exit(0)

        else:
            print("  Opción no válida.")

if __name__ == "__main__":
    main()
