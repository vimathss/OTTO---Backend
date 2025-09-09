"""
Vector Store Manager - Gerenciador de armazenamento de vetores para o OTTO

Este módulo gerencia diferentes vector stores para diferentes conjuntos de dados,
permitindo armazenamento e recuperação eficiente de embeddings de documentos.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

class VectorStoreManager:
    """Gerencia diferentes vector stores para diferentes conjuntos de dados."""
    
    def __init__(self, base_dir: str = "./vector_stores"):
        self.base_dir = base_dir
        self.stores = {}
        self.embeddings = None
        
        # Garantir que o diretório base existe
        os.makedirs(base_dir, exist_ok=True)
        
        # Inicializar modelo de embeddings (compartilhado entre stores)
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """Inicializa o modelo de embeddings."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(f"Erro ao inicializar modelo de embeddings: {e}")
            raise RuntimeError("Não foi possível inicializar o modelo de embeddings")
    
    def get_store(self, name: str) -> Any:
        """Obtém um vector store pelo nome, carregando-o se necessário."""
        if name not in self.stores:
            self._load_store(name)
        return self.stores.get(name)
    
    def _load_store(self, name: str) -> None:
        """Carrega um vector store do disco."""
        store_dir = os.path.join(self.base_dir, name)
        
        if os.path.exists(store_dir):
            try:
                from langchain_community.vectorstores import Chroma
                self.stores[name] = Chroma(
                    persist_directory=store_dir,
                    embedding_function=self.embeddings
                )
                print(f"Vector store '{name}' carregado com sucesso")
            except Exception as e:
                print(f"Erro ao carregar vector store '{name}': {e}")
                self.stores[name] = None
        else:
            print(f"Vector store '{name}' não existe")
            self.stores[name] = None
    
    def create_or_load(self, name: str, documents_dir: Optional[str] = None) -> Any:
        """Cria um novo vector store ou carrega um existente."""
        store_dir = os.path.join(self.base_dir, name)
        
        # Se já existe, apenas carregar
        if os.path.exists(store_dir):
            return self.get_store(name)
        
        # Se não existe e não temos documentos, retornar erro
        if not documents_dir:
            raise ValueError(f"Vector store '{name}' não existe e nenhum diretório de documentos foi fornecido")
        
        # Criar novo vector store
        try:
            # Carregar documentos
            documents = self._load_documents(documents_dir)
            
            if not documents:
                raise ValueError(f"Nenhum documento encontrado em '{documents_dir}'")
            
            # Criar vector store
            from langchain_community.vectorstores import Chroma
            os.makedirs(store_dir, exist_ok=True)
            
            self.stores[name] = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=store_dir
            )
            
            # Persistir
            self.stores[name].persist()
            print(f"Vector store '{name}' criado com sucesso")
            
            return self.stores[name]
        except Exception as e:
            print(f"Erro ao criar vector store '{name}': {e}")
            raise
    
    def _load_documents(self, documents_dir: str) -> List[Document]:
        """Carrega documentos de um diretório."""
        documents = []
        
        # Verificar se o diretório existe
        if not os.path.exists(documents_dir):
            print(f"Diretório '{documents_dir}' não existe")
            return documents
        
        # Carregar PDFs
        try:
            from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
            pdf_loader = DirectoryLoader(documents_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, recursive=True)
            pdf_docs = pdf_loader.load()
            documents.extend(pdf_docs)
            print(f"Carregados {len(pdf_docs)} documentos PDF")
        except Exception as e:
            print(f"Erro ao carregar PDFs: {e}")
        
        # Carregar DOCXs
        try:
            from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
            docx_loader = DirectoryLoader(documents_dir, glob="**/*.docx", loader_cls=Docx2txtLoader, recursive=True)
            docx_docs = docx_loader.load()
            documents.extend(docx_docs)
            print(f"Carregados {len(docx_docs)} documentos DOCX")
        except Exception as e:
            print(f"Erro ao carregar DOCXs: {e}")
        
        # Carregar TXTs
        try:
            from langchain_community.document_loaders import DirectoryLoader, TextLoader
            txt_loader = DirectoryLoader(documents_dir, glob="**/*.txt", loader_cls=TextLoader, recursive=True)
            txt_docs = txt_loader.load()
            documents.extend(txt_docs)
            print(f"Carregados {len(txt_docs)} documentos TXT")
        except Exception as e:
            print(f"Erro ao carregar TXTs: {e}")
        
        # Carregar CSVs
        try:
            from langchain_community.document_loaders import CSVLoader
            import glob
            
            csv_files = glob.glob(os.path.join(documents_dir, "**/*.csv"), recursive=True)
            csv_docs = []
            
            for csv_file in csv_files:
                try:
                    loader = CSVLoader(file_path=csv_file)
                    csv_docs.extend(loader.load())
                except Exception as csv_e:
                    print(f"Erro ao carregar CSV {csv_file}: {csv_e}")
            
            documents.extend(csv_docs)
            print(f"Carregados {len(csv_docs)} documentos CSV")
        except Exception as e:
            print(f"Erro ao carregar CSVs: {e}")

        # Carregar JSONs
        try:
            import glob
            import json
            from langchain_core.documents import Document

            json_files = glob.glob(os.path.join(documents_dir, "**/*.json"), recursive=True)
            json_docs = []

            for json_file in json_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Se for lista de registros, converte cada um para um Document
                    if isinstance(data, list):
                        for item in data:
                            # Cria um texto legível para busca
                            text_parts = [f"{k}: {v}" for k, v in item.items()]
                            text = "\n".join(text_parts)
                            json_docs.append(Document(page_content=text, metadata={"source": json_file}))
                    elif isinstance(data, dict):
                        text_parts = [f"{k}: {v}" for k, v in data.items()]
                        text = "\n".join(text_parts)
                        json_docs.append(Document(page_content=text, metadata={"source": json_file}))

                except Exception as json_e:
                    print(f"Erro ao carregar JSON {json_file}: {json_e}")

            documents.extend(json_docs)
            print(f"Carregados {len(json_docs)} documentos JSON")

        except Exception as e:
            print(f"Erro ao carregar JSONs: {e}")

        # Dividir documentos em chunks
        if documents:
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100,
                    length_function=len,
                    separators=["\n\n", "\n", " ", ""]
                )
                documents = text_splitter.split_documents(documents)
                print(f"Documentos divididos em {len(documents)} chunks")
            except Exception as e:
                print(f"Erro ao dividir documentos: {e}")
        
        return documents
    
    def get_main_store(self) -> Any:
        """Obtém o vector store principal."""
        return self.get_store("main")
    
    def add_documents(self, name: str, documents: List[Document]) -> None:
        """Adiciona documentos a um vector store existente."""
        store = self.get_store(name)
        if store:
            store.add_documents(documents)
            store.persist()
        else:
            raise ValueError(f"Vector store '{name}' não existe")
