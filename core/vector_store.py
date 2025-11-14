import os
from typing import List, Any, Optional, Dict
from langchain_core.documents import Document

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader


class VectorStoreManager:
    """Gerencia diferentes vector stores para diferentes conjuntos de dados."""

    def __init__(self, base_dir: str = "./vector_stores"):
        self.base_dir = base_dir
        self.stores: dict[str, Any] = {}
        self.embeddings = None

        os.makedirs(base_dir, exist_ok=True)
        self._initialize_embeddings()

    def _initialize_embeddings(self) -> None:
        """Inicializa o modelo de embeddings."""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            raise RuntimeError(f"Não foi possível inicializar o modelo de embeddings: {e}")

    def get_store(self, name: str) -> Any:
        """Obtém um vector store pelo nome, carregando-o se necessário."""
        if name not in self.stores:
            self._load_store(name)
        return self.stores.get(name)

    def _load_store(self, name: str) -> None:
        """Carrega um vector store existente do disco."""
        store_dir = os.path.join(self.base_dir, name)
        if os.path.exists(store_dir):
            try:
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
            store = self.get_store(name)
            if store:
                return store

        if not documents_dir:
            raise ValueError(f"Vector store '{name}' não existe e nenhum diretório de documentos foi fornecido")

        documents = self._load_documents(documents_dir)
        if not documents:
            raise ValueError(f"Nenhum documento encontrado em '{documents_dir}'")

        try:
            self.stores[name] = Chroma.from_documents(
                documents=documents,
                embedding_function=self.embeddings,  # ✅ nome atualizado
                persist_directory=store_dir
            )
            print(f"Vector store '{name}' criado com sucesso com {len(documents)} documentos")
            return self.stores[name]
        except Exception as e:
            raise RuntimeError(f"Erro ao criar vector store '{name}': {e}")

    def _load_documents(self, documents_dir: str) -> List[Document]:
        """Carrega e divide documentos de um diretório."""
        documents: List[Document] = []

        if not os.path.exists(documents_dir):
            print(f"Diretório '{documents_dir}' não existe")
            return documents

        # Carregadores
        loaders = [
            ("PDF", DirectoryLoader(documents_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, recursive=True)),
            ("DOCX", DirectoryLoader(documents_dir, glob="**/*.docx", loader_cls=Docx2txtLoader, recursive=True)),
            ("TXT", DirectoryLoader(documents_dir, glob="**/*.txt", loader_cls=TextLoader, recursive=True))
        ]

        for tipo, loader in loaders:
            try:
                loaded = loader.load()
                documents.extend(loaded)
                print(f"Carregados {len(loaded)} documentos {tipo}")
            except Exception as e:
                print(f"Erro ao carregar {tipo}s: {e}")

        # CSV e JSON são manuais
        import glob, json
        csv_docs, json_docs = [], []

        try:
            for csv_file in glob.glob(os.path.join(documents_dir, "**/*.csv"), recursive=True):
                loader = CSVLoader(file_path=csv_file)
                csv_docs.extend(loader.load())
            documents.extend(csv_docs)
            print(f"Carregados {len(csv_docs)} documentos CSV")
        except Exception as e:
            print(f"Erro ao carregar CSVs: {e}")

        try:
            for json_file in glob.glob(os.path.join(documents_dir, "**/*.json"), recursive=True):
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        text = "\n\n".join([f"{k}: {v}" for k, v in item.items()])
                        json_docs.append(Document(page_content=text, metadata={"source": json_file}))
                elif isinstance(data, dict):
                    text = "\n\n".join([f"{k}: {v}" for k, v in data.items()])
                    json_docs.append(Document(page_content=text, metadata={"source": json_file}))
            documents.extend(json_docs)
            print(f"Carregados {len(json_docs)} documentos JSON")
        except Exception as e:
            print(f"Erro ao carregar JSONs: {e}")

        # Dividir documentos
        if documents:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                length_function=len
            )
            documents = splitter.split_documents(documents)
            print(f"Documentos divididos em {len(documents)} chunks")

        return documents

    def search(
    self,
    collection_name: str,
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Busca semântica em uma collection."""
        try:
            store = self.get_store(collection_name)
            if store is None:
                return {"success": False, "error": f"Collection '{collection_name}' não encontrada"}

            results_with_scores = store.similarity_search_with_score(
                query=query,
                k=n_results,
                filter=filter_metadata
            )

            formatted = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "distance": score
                }
                for doc, score in results_with_scores
            ]

            return {"success": True, "results": formatted}

        except Exception as e:
            print(f"Erro na busca semântica: {e}")
            return {"success": False, "error": str(e)}

