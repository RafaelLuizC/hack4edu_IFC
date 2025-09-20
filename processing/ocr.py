import os
import dotenv
import pytesseract

from pdf2image import convert_from_path
from pytesseract import image_to_string
from PyPDF2 import PdfReader
from processing.extrator_ppc import gerar_json_fatias

def extrair_dados_ocr(caminho_pdf):
    
    dotenv.load_dotenv()
    pytesseract.pytesseract.tesseract_cmd = str(os.getenv("TESSERACT_EXE"))

    paginas = convert_from_path(caminho_pdf) # Converte todas as páginas do PDF para imagens

    conteudo_paginas = [] #Gera lista com o texto completo.

    for i, pagina in enumerate(paginas):
        text = image_to_string(pagina, lang='por')
        conteudo_paginas.append({"pagina": i + 1, "conteudo": text.replace("\n", " ")}) #Preciso atualizar essa parte.

    fatias = gerar_json_fatias(conteudo_paginas,300) #Gera as fatias do texto.

    return fatias
