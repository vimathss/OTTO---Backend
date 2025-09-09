"""
Script para correção de redação - Versão com acesso à base de conhecimento

Este script implementa uma ferramenta de correção de redação que acessa
documentos específicos sobre correção de redação.
"""

import os
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ajustar o caminho para importar módulos corretamente


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("redacao.log"),
        logging.StreamHandler()
    ]
)

# Importar componentes do OTTO
from core.llm_manager import LLMManager
from core.vector_store import VectorStoreManager

def main():
    """Função principal para correção de redação."""
    print("\n" + "=" * 50)
    print("🤖 OTTO - Correção de Redação")
    print("=" * 50)
    print("Digite 'sair' para encerrar.")
    print("=" * 50 + "\n")
    
    # Inicializar componentes
    try:
        print("Inicializando componentes...")
        llm_manager = LLMManager()
        vector_store_manager = VectorStoreManager()
        
        # Verificar se existe um vector store específico para redação
        redacao_store_name = "redacao_knowledge"
        redacao_docs_dir = "./data/redacao"
        
        # Criar diretório se não existir
        os.makedirs(redacao_docs_dir, exist_ok=True)
        
        # Criar ou carregar vector store específico para redação
        print("Carregando base de conhecimento sobre redação...")
        redacao_store = vector_store_manager.create_or_load(redacao_store_name, redacao_docs_dir)
        
        # Solicitar texto da redação
        print("\nPor favor, cole o texto completo da redação que deseja corrigir:")
        texto_redacao = ""
        
        # Capturar múltiplas linhas até encontrar uma linha com apenas "FIM"
        print("(Digite 'FIM' em uma linha separada quando terminar)")
        
        while True:
            linha = input()
            if linha.strip() == "FIM":
                break
            if linha.lower() == "sair":
                print("\nOperação cancelada.")
                return
            texto_redacao += linha + "\n"
        
        if not texto_redacao.strip():
            print("\nNenhum texto fornecido. Operação cancelada.")
            return
        
        # Solicitar tema da redação (opcional)
        tema = input("\nQual é o tema da redação? (opcional, pressione Enter para pular): ")
        
        # Recuperar conhecimento relevante sobre correção de redação
        print("\nBuscando critérios e exemplos de correção...")
        docs = redacao_store.similarity_search(
            "critérios correção redação ENEM exemplos", 
            k=5
        )
        
        # Extrair conteúdo dos documentos
        conhecimento_redacao = "\n\n".join([doc.page_content for doc in docs])
        
        # Se não encontrou documentos específicos, usar critérios padrão
        if not conhecimento_redacao.strip():
            conhecimento_redacao = """
            Critérios de Avaliação da Redação do ENEM:

            Competência 1: Demonstrar domínio da norma padrão da língua escrita.
            Competência 2: Compreender a proposta de redação e aplicar conceitos das várias áreas de conhecimento para desenvolver o tema, dentro dos limites estruturais do texto dissertativo-argumentativo.
            Competência 3: Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista.
            Competência 4: Demonstrar conhecimento dos mecanismos linguísticos necessários para a construção da argumentação.
            Competência 5: Elaborar proposta de intervenção para o problema abordado, respeitando os direitos humanos.

            Cada competência vale de 0 a 200 pontos, totalizando 1000 pontos.
            """
        
        # Construir prompt para correção
        print("\nAnalisando redação...")
        
        prompt = f"""
        Você é um especialista rigoroso em correção de redações do ENEM. Analise a redação abaixo seguindo rigorosamente os critérios oficiais de correção.

        TEXTO DA REDAÇÃO:
        {texto_redacao}

        {f"TEMA DA REDAÇÃO: {tema}" if tema else ""}

        CRITÉRIOS DE AVALIAÇÃO E EXEMPLOS DE REDAÇÕES NOTA MÁXIMAS COM COMENTÁRIOS DE CORRETORES:
        {conhecimento_redacao}

        Forneça uma análise detalhada seguindo este formato:
        1. Competência 1 (Domínio da norma culta): [nota 0-200] - [justificativa detalhada]
        2. Competência 2 (Compreensão do tema): [nota 0-200] - [justificativa detalhada]
        3. Competência 3 (Organização de argumentos): [nota 0-200] - [justificativa detalhada]
        4. Competência 4 (Construção da argumentação): [nota 0-200] - [justificativa detalhada]
        5. Competência 5 (Proposta de intervenção): [nota 0-200] - [justificativa detalhada]

        NOTA FINAL: [soma das notas]

        FEEDBACK GERAL:
        [Resumo dos pontos fortes]
        [Resumo dos pontos a melhorar]
        [Sugestões específicas para aprimoramento]

        Seja educativo, construtivo e específico no feedback, apontando exemplos concretos do texto.

        Caso o texto não esteja em formato dissertativo-argumentativo ou não seja uma redação, informe que a redação não atende aos requisitos e que o usuario deve tentar novamente com um texto adequado.
        """
        
        # Gerar correção
        resultado = llm_manager.generate(prompt, temperature=0.2)
        
        # Mostrar resultado
        print("\n" + "=" * 50)
        print("RESULTADO DA CORREÇÃO:")
        print("=" * 50 + "\n")
        print(resultado)
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"\nErro ao corrigir redação: {e}")

if __name__ == "__main__":
    main()
