# Prompt do Parser, ele analisa, corrige e organiza o texto extraído do PDF em tópicos e sub-tópicos.
def prompt_parser():
  return """Sua tarefa é:
  1. Analisar o texto fornecido pelo usuário, que pode conter resumos, listas de exercícios, tópicos de aula ou anotações de professor.  
  2. Identificar os **principais temas (tópicos)** e seus **subtemas (subtópicos)** com base na estrutura e no conteúdo.  
  3. Eliminar repetições e combinar conteúdos semelhantes.  
  4. Criar **sínteses explicativas curtas e objetivas** sobre o que o aluno deve entender ou fazer para resolver questões relacionadas a cada tema ou subtema.  
  5. Retornar o resultado **exclusivamente** em formato JSON, na seguinte estrutura:  

  ```json
  [
    {
      "Topico": "NOME DO TÓPICO PRINCIPAL",
      "Conteudo": "Resumo explicativo geral do tópico.",
      "Subtopicos": [
        {
          "Nome": "NOME DO SUBTÓPICO",
          "Conteudo": "Síntese explicativa ou instrução de aprendizado referente a este subtema."
        }
      ]
    }
  ]

  Regras Importantes:

  O JSON deve conter apenas tópicos e subtemas únicos (sem repetições).
  O campo "Conteudo" deve conter exemplos do professor, de forma clara, direta e útil para estudo ou resolução de exercícios.
  Se um tópico não tiver subdivisões, retorne apenas "Topico" e "Conteudo".
  Se houver subdivisões claras (ex: fórmulas, propriedades, casos, exemplos), insira-as como "Subtopicos".
  Não adicione nenhum texto fora do JSON.
  Preserve a clareza e a coerência lógica da hierarquia.
  Organize ele de forma que facilite o estudo e a revisão dos conteúdos apresentados no texto original.

  Exemplo de Saída Esperada:

  Saída JSON:
  ```json
  [
    {
      "Topico": "Medidas Descritivas",
      "Conteudo": "Resumem um conjunto de dados por meio de medidas centrais e de dispersão.",
      "Subtopicos": [
        {"Nome": "Média", "Conteudo": "Soma dos valores dividida pela quantidade de elementos."},
        {"Nome": "Mediana", "Conteudo": "Valor central de um conjunto ordenado."},
        {"Nome": "Moda", "Conteudo": "Valor que mais se repete nos dados."},
        {"Nome": "Variância", "Conteudo": "Mede o grau de dispersão dos dados em relação à média."},
        {"Nome": "Desvio Padrão", "Conteudo": "Raiz quadrada da variância, representa a dispersão média."}
      ]
    },
    {
      "Topico": "Distribuição de Poisson",
      "Conteudo": "Modela a probabilidade de um número de eventos ocorrer em um intervalo fixo.",
      "Subtopicos": [
        {"Nome": "Taxa de Ocorrência (λ)", "Conteudo": "Número médio de eventos em um intervalo."},
        {"Nome": "Cálculo de Probabilidade", "Conteudo": "Usa a fórmula P(x) = (λ^x * e^-λ) / x!."}
      ]
    },
    {
      "Topico": "Banco de Dados",
      "Conteudo": "Ferramentas de manipulação e execução de consultas SQL.",
      "Subtopicos": [
        {"Nome": "Views", "Conteudo": "Consultas salvas que se comportam como tabelas virtuais."},
        {"Nome": "Stored Procedures", "Conteudo": "Blocos de código SQL armazenados no banco para execução automática."}
      ]
    }
]"""

# Prompt para gerar as atividades detalhadas a partir da trilha criada
def prompt_atividades():
  def prompt_atividades():
    return """ Sua tarefa é gerar o conteúdo detalhado de cada atividade a partir da TRILHA fornecida em JSON.

  ### Instruções:
  1. Para cada item da trilha, identifique o tipo de atividade (Quiz, Flashcard, Audio ou CacaPalavras).
  2. Gere os dados completos da atividade, preenchendo o campo “Detalhes” conforme o tipo.
  3. Retorne o resultado **somente em formato JSON**, seguindo a estrutura abaixo.

  ### Estrutura de Saída Final:
  [
    {
      "Codigo": "Mesmo código da trilha original (ex: DB001)",
      "Topico": "Tema principal",
      "Subtopico": "Conceito abordado",
      "Atividade": "Flashcard | Quiz | Audio | CacaPalavras",
      "Conteudo": "Resumo breve do conceito trabalhado",
      "Detalhes": {
        "Flashcard": {
          "Frente": "Pergunta ou conceito para memorizar",
          "Verso": "Resposta ou explicação resumida"
        },
        "Quiz": {
          "Pergunta": "Pergunta clara e direta sobre o tema",
          "Alternativas": [
            {"Texto": "Alternativa correta", "Correta": true, "Explicacao": "Justificativa do porquê está correta"},
            {"Texto": "Alternativa incorreta 1", "Correta": false, "Explicacao": "Motivo do erro"},
            {"Texto": "Alternativa incorreta 2", "Correta": false, "Explicacao": "Motivo do erro"},
            {"Texto": "Alternativa incorreta 3", "Correta": false, "Explicacao": "Motivo do erro"}
          ]
        },
        "Audio": {
          "Titulo": "Tema central da conversa",
          "SSML": "<speak> ... </speak>"
        },
        "CacaPalavras": {
          "Tema": "Assunto central",
          "Palavras": ["Palavra1", "Palavra2", "Palavra3", "Palavra4"]
        }
      }
    }
  ]

  ### Regras:
  - Mantenha consistência entre os “Códigos” e tópicos da trilha original.
  - Cada atividade deve conter apenas o tipo correspondente em “Detalhes”.
  - As perguntas e explicações devem ser curtas, claras e com tom pedagógico.
  - Para atividades do tipo Audio, gere o conteúdo em SSML válido:
    - Use a tag raiz <speak>.
    - Estruture em parágrafos (<p>) e sentenças (<s>) quando apropriado.
    - Inclua pausas com <break time=\"...\"/> e marqueções de prosódia com <prosody rate=\"...\" pitch=\"...\"> se necessário.
    - Use <emphasis> para destacar termos importantes.
    - Produza SSML em português (pt-BR) e mantenha cada SSML com duração curta (30-90s aproximadamente).
    - Insira apenas a string SSML no campo "SSML" sem metadados adicionais.
    - Retorne Marktime em milissegundos (ms) para pausas, e onde cada visema é pronunciada.
  - Nos demais tipos, siga os formatos especificados.
  - Retorne **somente o JSON**, sem explicações adicionais.

  Agora gere as atividades detalhadas para a seguinte trilha:
  """

# Prompt de criação da trilha de aprendizado
# Ele define quais atividades que o usuário irá receber.

def prompt_trilha():
  return """Sua tarefa é criar uma TRILHA DE APRENDIZADO adaptada ao perfil do usuário e ao tema solicitado.

### Objetivo:
Gerar uma sequência de aproximadamente 10 atividades diversificadas (quiz, flashcard, áudio e caça-palavras) que abordem progressivamente os principais tópicos e subtemas do conteúdo informado.

### Instruções:
1. Leia atentamente o PERFIL DO USUÁRIO e o TEMA fornecido.
2. Escolha os tópicos e subtemas relevantes ao tema, evitando repetições.
3. Selecione tipos de atividade variados e adequados ao perfil.
4. Gere um CÓDIGO único para cada atividade (ex: DB001, STAT005), com base na sigla do tema e sequência numérica.
5. Retorne o resultado **somente em formato JSON**, seguindo a estrutura abaixo.

### Estrutura de Saída:
[
  {
    "Codigo": "ID único da atividade (ex: DB001)",
    "Topico": "Tema principal da atividade",
    "Subtopico": "Conceito específico abordado",
    "Atividade": "Flashcard | Quiz | Audio | CacaPalavras",
    "Conteudo": "Breve descrição ou resumo do conceito a ser trabalhado"
  }
]

### Regras:
- Não repita tópicos ou subtemas.
- Use linguagem clara, didática e envolvente.
- Combine níveis de dificuldade (fácil a difícil), mas sem informar o nível explicitamente.
- Inclua tópicos fundamentais e complementares do tema.
- Não adicione explicações fora do JSON.

Agora, gere a trilha personalizada com base nas seguintes informações:

**Perfil do usuário:**
[SUBSTITUIR-PERFIL-USUARIO]

**Tema:**
[SUBSTITUIR-TEMA]"""