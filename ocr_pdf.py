import os
import dotenv
import pytesseract
from pytesseract import image_to_string
from pdf2image import convert_from_path

from ai_module import *
from prompt import *


dotenv.load_dotenv()
pytesseract.pytesseract.tesseract_cmd = str(os.getenv("TESSERACT_EXE"))

def extrair_dados_pdf(caminho_pdf):

    # Converte todas as páginas do PDF para imagens
    paginas = convert_from_path(caminho_pdf)

    #Gera lista com o texto completo.
    texto_completo = []
    for i, pagina in enumerate(paginas):
        text = image_to_string(pagina, lang='eng')
        texto_completo.append(text.replace("\n",""))
    
    #Junta o texto em uma unica string
    texto_completo = " ".join(texto_completo)
    print (f"O Texto foi recuperado por meio de metodos OCR, então é possivel que haja erros gramaticos, os corrija antes de gerar o conteudo: {texto_completo}")



texto = extrair_dados_pdf('THE-VERY-HUNGRY-CATERPILLAR.pdf')

print (texto)
resposta = chat_ia(prompt_geracao_perguntas(texto))
print (resposta)