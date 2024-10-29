from transformers import pipeline
import torch
import os

from prompt import *
from util.helpers import *
from vetor import *

def chat_ia(contexto):

  pipe = pipeline("text-generation", model="microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)

  outputs = pipe(
      contexto,
      max_new_tokens=500,

      do_sample=False, #Gera mais de uma resposta caso esteja "True", permitindo usar o parametro "temperature".
      #temperature=1, #0.0 = 0 Menor, 1 = Limite / Quanto maior, mais aleatório.
  )

  return outputs[0]["generated_text"][-1]["content"]