# Importa funções para consultar variáveis de ambiente, como a chave da API.
import os
# Importa o carregador de variáveis a partir de um arquivo local .env.
from dotenv import load_dotenv
# Importa o cliente oficial da biblioteca Google Gen AI.
from google import genai
# Importa classes usadas para configurar as requisições e a geração do Gemini.
from google.genai import types

# Carrega os valores definidos em .env para que os.getenv possa acessá-los.
load_dotenv()

# Obtém a chave da API Gemini; retorna None se não estiver configurada.
API_KEY = os.getenv("GEMINI_API_KEY")
# Lê o modelo selecionado por configuração ou aplica o valor padrão.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
# Identifica a versão das instruções, permitindo distinguir alterações futuras.
PROMPT_VERSION = "v1"

# Valida a presença da credencial antes de tentar criar o cliente.
if not API_KEY:
    # Falha explicitamente na inicialização se não houver uma chave de API.
    raise RuntimeError(
        # Informa onde configurar o valor esperado.
        "GEMINI_API_KEY não foi configurada no arquivo .env"
    )

# Cria o cliente usado para enviar chamadas à API do Gemini.
client = genai.Client(
    # Passa a chave que autentica as requisições feitas pelo cliente.
    api_key=API_KEY,
    # Define opções HTTP, incluindo o tempo máximo de espera da chamada.
    http_options=types.HttpOptions(timeout=50000),
)

# Cria um cache em memória; os dados ficam disponíveis somente enquanto o
# processo está executando e são apagados ao encerrar o programa.
cache = {}


# Define a operação de classificação: recebe uma mensagem e retorna sua
# categoria junto com a informação de uso do cache.
def classificar_mensagem(mensagem):
    # Remove espaços em branco das extremidades da mensagem recebida.
    mensagem = mensagem.strip()

    # Impede que uma mensagem vazia seja enviada ao serviço.
    if not mensagem:
        # Indica ao chamador que a entrada fornecida não é válida.
        raise ValueError("A mensagem não pode ficar vazia.")

    # Usa texto, modelo e versão do prompt para identificar unicamente uma
    # classificação no cache e evitar reutilização após mudar modelo/instruções.
    chave = (mensagem, MODEL, PROMPT_VERSION)

    # Verifica se a classificação dessa combinação já foi calculada.
    if chave in cache:
        # Devolve a categoria armazenada e indica que o cache foi utilizado.
        return {
            # Lê a categoria previamente guardada para esta chave.
            "categoria": cache[chave],
            # O valor textual é apresentado diretamente pelo programa principal.
            "cache": "sim",
        }

    # Constrói as instruções que serão enviadas ao modelo. O bloco abaixo é
    # texto de prompt, não código Python: seus marcadores e linhas são parte
    # intencional da solicitação enviada ao Gemini.
    prompt = f"""
Classifique a mensagem em uma categoria:
- acesso_conta
- problema_pagamento
- duvida_produto
- outros

Retorne apenas o nome da categoria.

Versão do prompt: {PROMPT_VERSION}
Mensagem: {mensagem}
"""

    # Trata falhas ocorridas durante a comunicação com o serviço Gemini.
    try:
        # Solicita ao modelo uma classificação com base no prompt construído.
        resposta = client.models.generate_content(
            # Seleciona o modelo configurado no início deste módulo.
            model=MODEL,
            # Envia o texto de instruções e a mensagem que será classificada.
            contents=prompt,
            # Define os parâmetros que limitam/controlam o texto gerado.
            config=types.GenerateContentConfig(
                # Reduz a variação da geração; não garante respostas idênticas.
                temperature=0,
                # Limita o tamanho da resposta a 30 tokens.
                max_output_tokens=30,
            ),
        )
    # Captura falhas da API/biblioteca para acrescentar contexto à exceção.
    except Exception as erro:
        # Relança o erro com uma mensagem amigável, preservando a causa original.
        raise RuntimeError(
            # Sugere pontos iniciais para investigar a falha da chamada.
            "Erro ao consultar o Gemini. "
            "Verifique a conexão, o timeout e a configuração da API."
        ) from erro

    # Extrai o texto retornado; se for None, substitui por string vazia; remove
    # espaços e padroniza em minúsculas para comparar com as categorias.
    categoria = (resposta.text or "").strip().lower()

    # Lista explicitamente as únicas respostas aceitas pela aplicação.
    categorias_validas = {
        # Categoria para questões de acesso a contas.
        "acesso_conta",
        # Categoria para questões de cobrança ou pagamento.
        "problema_pagamento",
        # Categoria para dúvidas sobre o produto.
        "duvida_produto",
        # Categoria genérica para os demais assuntos.
        "outros",
    }

    # Garante que a resposta do modelo corresponda a uma categoria permitida.
    if categoria not in categorias_validas:
        # Interrompe o processamento e inclui a resposta inválida no erro.
        raise ValueError(
            f"Categoria inválida retornada pela IA: {categoria!r}"
        )

    # Salva somente respostas validadas para reutilizá-las em chamadas futuras
    # com a mesma mensagem, modelo e versão do prompt.
    cache[chave] = categoria

    # Devolve a classificação e marca que ela veio de uma chamada nova à API.
    return {
        # Campo consumido pelo programa principal para exibir a classificação.
        "categoria": categoria,
        # Distingue este resultado de um resultado obtido anteriormente do cache.
        "cache": "não",
    }
