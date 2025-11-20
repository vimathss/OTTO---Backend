# OTTO - Um assistente para professores, uma revolução para a educação

<img src="utils/OTTO LOGO - SOMBRA.png" alt="Logo do Projeto" width="200px"/>

---

> **Trabalho de Conclusão de Curso** — Técnico em Desenvolvimento de Sistemas integrado ao Ensino Médio — **ETEC de Hortolândia, 2025**  
> Orientação: Prof. Priscila Batista Martins

---


## Sobre o Projeto

O OTTO é uma ferramenta baseada em inteligência artificial desenvolvida para apoiar professores em todas as fases do processo educacional, incluindo:

*   **Pré-aula:** Preparação, planejamento e organização de materiais.
*   **Durante a aula:** Tarefas pontuais, dinâmicas e interações em tempo real.
*   **Pós-aula:** Geração de relatórios, feedbacks e análises de desempenho.

O projeto integra um chatbot de inteligência artificial generativa, capaz de responder perguntas, esclarecer dúvidas e executar comandos programados para facilitar o cotidiano pedagógico e organizacional do professor.

O software conta com uma interface desenvolvida em React com TypeScript e um backend em Python, incorporando bibliotecas especializadas no desenvolvimento de agentes de IA. Além disso, o OTTO possui um robô físico baseado no ESP32-S3-Korvo-1, ideal para reconhecimento de voz, possibilitando interação por comandos falados e tirando respostas de dúvidas pontuais.

[**Assista um pitch sobre o projeto**](https://youtu.be/zmzvQPjzUSs?si=NwREw9gygy0esaBw)

## Funcionamento do Back-end

O backend do OTTO, construído com **Python** e **FastAPI**, atua como o cérebro do assistente, orquestrando a comunicação entre o frontend e os serviços de inteligência artificial.

### Arquitetura RAG (Retrieval-Augmented Generation)

O coração do sistema é a arquitetura RAG, que permite ao OTTO responder perguntas com base em uma base de conhecimento específica (documentos da escola, BNCC, etc.), e não apenas no conhecimento pré-treinado do modelo de linguagem.

1.  **Ingestão de Dados:** Documentos (PDFs, TXTs) são processados, divididos em pequenos trechos (chunks) e convertidos em representações numéricas (embeddings) usando o modelo `sentence-transformers/all-MiniLM-L6-v2`.
2.  **Vector Store:** Os embeddings são armazenados no **ChromaDB**, que funciona como um banco de dados vetorial.
3.  **Busca (Retrieval):** Ao receber uma pergunta do usuário, o sistema busca no ChromaDB os trechos de documentos mais relevantes para aquela pergunta.
4.  **Geração (Generation):** O **OTTO** combina a pergunta do usuário, o histórico da conversa (recuperado do Firebase) e os trechos relevantes (contexto RAG), e envia ao **LLM do Gemini** para gerar uma resposta precisa e contextualizada.

## Estrutura do Projeto

O projeto segue uma estrutura modular para facilitar a manutenção e a expansão:

| Pasta/Arquivo | Descrição |
| :--- | :--- |
| `core/` | Contém os componentes centrais de IA e persistência. |
| `core/agent.py` | **Orquestrador Principal (OTTOAgent)**. Coordena a memória, o RAG e o LLM para gerar a resposta final. |
| `core/llm_manager.py` | Gerencia a comunicação com a **Google Gemini API**, formatando prompts e tratando o histórico. |
| `core/vector_store.py` | Gerencia o **ChromaDB**, responsável pela ingestão de dados e busca de contexto (RAG). |
| `core/memory_manager.py` | Gerencia o histórico de conversas no **Firebase Firestore**. |
| `funcoes/` | Contém as funções específicas do OTTO (chat, correção de redação). |
| `utils/ingestao.py` | Script para processar documentos e popular o ChromaDB. |
| `main.py` | Arquivo principal da **API FastAPI**, define os endpoints (`/chat`, `/redacao`) e inicializa todos os componentes. |
| `requirements.txt` | Lista de dependências Python. |

## Funcionalidades do Projeto

O OTTO oferece as seguintes funcionalidades principais:

1.  **Chat Conversacional Contextualizado:** Respostas baseadas em uma base de conhecimento específica (RAG) e com manutenção do histórico de conversas (Firebase).
2.  **Correção de Redação:** Ferramenta especializada para análise e feedback construtivo em redações, seguindo critérios rigorosos.
3.  **API REST:** Comunicação limpa e tipada com o frontend React/TypeScript via endpoints FastAPI.

## Recursos Utilizados

O projeto OTTO utiliza um conjunto de tecnologias modernas para garantir desempenho e escalabilidade:

| Categoria | Recurso | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python | Linguagem principal do backend e da lógica de IA. |
| **Framework Web** | FastAPI | Framework de alta performance para a construção da API REST. |
| **Modelo de Linguagem** | Google Gemini API | Modelo de IA generativa utilizado para as respostas e processamento de linguagem natural. |
| **Banco de Dados Vetorial** | ChromaDB | Utilizado para armazenar e buscar embeddings de documentos na arquitetura RAG. |
| **Embeddings** | Sentence Transformers | Modelo `all-MiniLM-L6-v2` para a criação de representações vetoriais de texto. |
| **Memória/Persistência** | Firebase Firestore | Banco de dados NoSQL para o gerenciamento e persistência do histórico de conversas. |
| **Frontend** | React / TypeScript | Tecnologias utilizadas para a interface do usuário. |
| **Bibliotecas de IA** | LangChain Community | Componentes de código aberto para facilitar a construção de aplicações com LLMs. |

## Informações adicionais

- Status: **Em andamento**  
- Ano: **2025**

## Autores

*   Cristiano Secco Júnior
*   Daniel Ayron de Oliveira
*   Paulo Eduardo Ferreira Junior
*   Vicente Matheus Collin Pedroso
