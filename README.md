# OTTO – Back-End  
<img src="src/assets/OTTO LOGO Branca.png" alt="Logo do Projeto" width="200px"/>

---

> **Trabalho de Conclusão de Curso** — Técnico em Desenvolvimento de Sistemas integrado ao Ensino Médio  
> **ETEC de Hortolândia, 2025**  
> Orientação: Profa. Priscila Batista Martins  

---

## Sobre o Projeto  

O **OTTO – Um Assistente para Professores, uma Revolução para a Educação** é um sistema baseado em **inteligência artificial** que apoia professores em todas as fases do processo educacional.  

O **back-end** do OTTO foi desenvolvido em **Python**, estruturado em módulos responsáveis por organizar dados, funções e a lógica central do agente. Ele é responsável por processar as perguntas do **front-end** com inteligência artificial, e gerenciando toda a base de conhecimento, memória e funcionalidades.  

### Estrutura principal  

- **CORE** → Gerencia os componentes principais (LLM, memória e agente).  
- **DATA** → Armazena os arquivos e documentos de conhecimento (PDF, JSON, CSV, etc.).  
- **FUNÇÕES** → Separa as funcionalidades (ex: chat principal e correção de redações).  
- **MEMORY** → Guarda o histórico de conversas em arquivos JSON.  
- **UTILS** → Funções auxiliares como ingestão de documentos e criação de vector stores.  
- **VECTOR_STORES** → Repositório de dados já processados em formato vetorial.  
- **MAIN.py** → Responsável por disponibilizar os endpoints de comunicação com o front-end.  

---

## Tecnologias Utilizadas  

- **Python 3**  
- **API do Gemini (LLM)**  
- **Bibliotecas Python** (definidas no `requirements.txt`)  
- **Vector Stores (FAISS)** para busca contextual  
- **JSON** para gerenciamento de memória  
- **HTTP Endpoints** para comunicação com o front-end  

---

## Conexão com o Front-End  

O arquivo **main.py** disponibiliza endpoints de API para:  
- Chat principal  
- Correção de redação  

Essas funções podem ser acessadas via **requisições HTTP** enviadas pelo front-end em **React + TypeScript**.  

---

## Próximos Passos (em desenvolvimento...)

- Finalizar e otimizar as funções de **chat** e **correção de redações** para integração completa com o front-end.  
- Desenvolver novas funcionalidades como:  
  - Geração de planos de aula  
  - Correção de provas e lista de exercícios 

---

## Autores  

- **Cristiano Secco Júnior**  
- **Daniel Ayron de Oliveira**  
- **Paulo Eduardo Ferreira Junior**  
- **Vicente Matheus Collin Pedroso**  
