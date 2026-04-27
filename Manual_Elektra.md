# Manual de Instalación y Uso de ELEKTRA
**Sistema Multi-Agente Evolutivo**

## 1. ¿Qué es Elektra?
Elektra es un sistema de Inteligencia Artificial Colectiva diseñado para resolver problemas complejos (especialmente matemáticos y lógicos) combinando las capacidades de 4 agentes especializados. Estos agentes colaboran, debaten y evolucionan a través de varias generaciones mediante un algoritmo genético integrado, garantizando una respuesta superior a la que cualquier modelo podría dar individualmente.

Los 4 agentes de Elektra son:
* **Alpha (Analista Sistémico):** Descompone el problema y evalúa el panorama general.
* **Beta (Pensador Lateral):** Busca soluciones creativas y fuera de lo común.
* **Gamma (Especialista en Implementación):** Desarrolla el paso a paso matemático/lógico.
* **Delta (Crítico y Evaluador de Riesgos):** Actúa como "abogado del diablo", buscando fallos y casos límite.

## 2. Requisitos Previos
Para que Elektra funcione correctamente en tu sistema, necesitas:
* **Sistema Operativo:** Windows 10/11.
* **Python:** Versión 3.10 o superior instalada en el sistema.
* **Cuenta de Ollama Cloud:** Elektra utiliza la API en la nube de Ollama, por lo que **no es necesario** descargar modelos pesados ni tener hardware avanzado para IA. Solo necesitas registrarte en el plan Free de Ollama en su página web y descargar la aplicación de Ollama para Windows.
* **Tarjeta Gráfica (Opcional pero muy recomendado):** Se requiere GPU NVIDIA compatible con CUDA para acelerar drásticamente el proceso de extracción de texto de imágenes mediante OCR.

## 3. Instalación

1. **Descarga el proyecto:** Asegúrate de tener todos los archivos de Elektra en una carpeta (ej. `C:\Users\fnora\Desktop\Elektra`).
2. **Prepara el entorno de Python:** Se recomienda utilizar un entorno local.
3. **Instala las dependencias:** Abre una ventana de terminal (CMD o PowerShell) en la carpeta de Elektra y ejecuta:
   ```bash
   pip install -r requirements_web.txt
   ```
   *Nota: El archivo `requirements_web.txt` incluye enlaces específicos para descargar la versión de PyTorch con soporte para GPU (CUDA 11.8). Si tienes una conexión lenta, este paso puede tardar algunos minutos, ya que descargará alrededor de 2.5 GB.*

## 4. Iniciar Elektra

El sistema cuenta con un ejecutable simplificado:
1. Haz doble clic en el archivo **`Iniciar_Elektra.bat`**.
2. Aparecerá una ventana negra (consola) indicando que el servidor se está iniciando. **No cierres esta ventana** mientras quieras usar Elektra.
3. Automáticamente se abrirá tu navegador web por defecto mostrando la interfaz gráfica de Elektra. Si no se abre, puedes acceder manualmente entrando en `http://localhost:8000`.

## 5. Uso del Sistema

### 5.1. La Interfaz Principal
* **Panel Izquierdo:** Muestra el estado en tiempo real de los 4 agentes (Alpha, Beta, Gamma, Delta), el modelo asignado a cada uno y su puntuación de *fitness* (calidad de respuesta). También puedes ver el **Log Evolutivo** donde se narran los cruces y mutaciones entre agentes.
* **Panel Central (Chat):** Es el registro de tus conversaciones y las respuestas de Elektra.
* **Caja de Entrada:** Ubicada en la parte inferior. Puedes:
  * Escribir un problema en formato texto.
  * Adjuntar una o varias imágenes / PDFs usando el botón del clip (Elektra cuenta con OCR local para extraer fórmulas matemáticas complejas).
  * Usar el botón del micrófono para dictar el problema por voz.
* **Selector de Generaciones:** Permite elegir cuántas vueltas (iteraciones) dará el algoritmo evolutivo (1, 3 o 5). A mayor número, mejor calidad de la respuesta final, pero mayor tiempo de espera.

### 5.2. Personalización de Modelos
Puedes cambiar qué modelo de Inteligencia Artificial "conduce" a cada agente.
1. Haz clic en el nombre de un agente en el panel izquierdo (ej. "Alpha").
2. Se abrirá un menú desplegable.
3. Elige el modelo deseado (los gratuitos aparecerán primero).

### 5.3. El Proceso de Resolución
Cuando envías un problema, Elektra iniciará su ciclo:
1. **Iniciando Agentes:** Los 4 agentes leerán tu problema (y analizarán tus imágenes con OCR) y cada uno propondrá una solución independiente.
2. **Evaluando y Evolucionando:** Elektra evaluará las respuestas. Las mejores se cruzarán (*crossover*) y las peores mutarán, iterando según el número de generaciones que hayas elegido.
3. **Sintetizando Respuesta Final:** El Orquestador recogerá las mejores ideas resultantes de la evolución y redactará un veredicto maestro.

### 5.4. Log Automático en HTML (Trazabilidad)
Para que no te pierdas el hilo de pensamiento de Elektra, al terminar la primera generación de agentes, se abrirá automáticamente en tu navegador una pestaña secundaria llamada **"Elektra Log"** (`elektra_log.html`).
* Esta página se actualizará **por sí sola** en tiempo real a medida que avancen las generaciones.
* En ella podrás inspeccionar minuciosamente qué propuso cada agente de forma individual y cómo evolucionaron sus respuestas.
* Una vez el proceso haya finalizado, la página de log dejará de auto-recargarse y la podrás guardar o imprimir.

## 6. Resolución de Problemas Comunes

* **"No detecta la GPU durante el OCR":** Verifica que instalaste los requerimientos completos y que tu tarjeta NVIDIA tiene los drivers actualizados. Puedes reinstalar Torch forzando CUDA con el comando que está dentro de `requirements_web.txt`.
* **"Los agentes no responden (se corta a la mitad)":** Verifica que la aplicación de Ollama para Windows esté corriendo en segundo plano en tu PC y que tu cuenta esté correctamente conectada a la nube.
* **"La interfaz web dice 'Reconectando...'":** Asegúrate de no haber cerrado accidentalmente la ventana negra (`Iniciar_Elektra.bat`). Si la cerraste, simplemente vuelve a ejecutar el archivo.

---
*Manual generado automáticamente para la versión local de Elektra. Todos los derechos reservados.*
