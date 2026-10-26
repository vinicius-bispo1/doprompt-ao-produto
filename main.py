# Importa a função que encapsula a comunicação com Gemini e a classificação.
from ai_client import classificar_mensagem

# Define a função que conduz a interação pelo terminal.


def main():
    # Apresenta o nome do programa.
    print("=== Classificador de mensagens ===")
    # Explica como encerrar a aplicação.
    print("Digite 'sair' para encerrar.\n")

    # Repete a solicitação de mensagens até o usuário escolher sair.
    while True:
        # Lê a entrada do terminal e remove espaços no começo e no final.
        mensagem = input("Mensagem: ").strip()

        # Reconhece a palavra de saída sem diferenciar letras maiúsculas.
        if mensagem.lower() == "sair":
            # Encerra o while e, portanto, a interação.
            break
        # Detecta entrada vazia antes de chamar o classificador.
        if not mensagem:
            # Pede que seja digitado algum conteúdo.
            print("Digite uma mensagem válida.\n")
            # Reinicia o loop para perguntar por uma nova mensagem.
            continue

        # Executa a classificação dentro de um bloco que trata possíveis erros.
        try:
            # Chama a função do módulo ai_client e recebe categoria e status
            # do cache em um dicionário.
            resultado = classificar_mensagem(mensagem)
            # Exibe a categoria retornada pelo Gemini ou pelo cache.
            print(f"Categoria: {resultado['categoria']}")
            # Exibe se a categoria foi recuperada do cache ("sim") ou não.
            print(f"Usou cache? {resultado['cache']}\n")
        # Trata especificamente TimeoutError, se for esse o tipo recebido.
        except TimeoutError as erro:
            # Explica que a chamada excedeu o tempo permitido e exibe o detalhe.
            print(f"A chamada demorou demais: {erro}\n")
        # Trata os demais erros para manter o programa interativo em execução.
        except Exception as erro:
            # Informa a falha ocorrida sem encerrar o loop principal.
            print(f"Não foi possível classificar: {erro}\n")


# Verifica se este arquivo foi executado diretamente, e não importado por outro.
if __name__ == "__main__":
    # Inicia a aplicação de terminal quando main.py é executado diretamente.
    main()
