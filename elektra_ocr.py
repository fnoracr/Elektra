import os
import subprocess
import tempfile
import shutil

def run_local_ocr(file_path: str) -> str:
    """
    Ejecuta Nougat OCR en un archivo local (PDF o imagen).
    Si es una imagen, la convierte a PDF temporalmente ya que la CLI
    de Nougat solo admite PDFs.
    """
    if not os.path.exists(file_path):
        return f"[Error] Archivo no encontrado: {file_path}"
        
    out_dir = tempfile.mkdtemp()
    temp_pdf_path = None
    
    try:
        print(f"  👁️ Iniciando OCR local en {os.path.basename(file_path)}. Esto puede tardar varios segundos/minutos...")
        
        # Si no es PDF, convertir la imagen a PDF temporalmente
        target_path = file_path
        if not file_path.lower().endswith(".pdf"):
            from PIL import Image
            try:
                img = Image.open(file_path).convert("RGB")
                fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
                os.close(fd)
                img.save(temp_pdf_path, format="PDF")
                target_path = temp_pdf_path
            except Exception as e:
                return f"[Error OCR] No se pudo convertir la imagen a PDF: {e}"

        # nougat <file> -o <out_dir>
        result = subprocess.run(
            ["nougat", target_path, "-o", out_dir, "--markdown", "--no-skipping"],
            capture_output=True, text=True, encoding="utf-8"
        )
        
        # Buscar el archivo .mmd o .md generado
        for f in os.listdir(out_dir):
            if f.endswith((".mmd", ".md")):
                with open(os.path.join(out_dir, f), "r", encoding="utf-8") as mmd:
                    return mmd.read()
                    
        return f"[Error OCR] No se generó salida.\nDetalles: {result.stderr[:500]}"
    except FileNotFoundError:
        return (
            "[Error] 'nougat' no está instalado o no está en el PATH.\n"
            "Instálalo ejecutando: pip install nougat-ocr\n"
        )
    except Exception as e:
        return f"[Error OCR] Excepción durante el proceso: {e}"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except:
                pass

