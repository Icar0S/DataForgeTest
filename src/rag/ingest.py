"""RAG document ingestion and processing."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from llama_index import (
    Document,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex,
)
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter
from llama_index.embeddings import OpenAIEmbedding

from .config import RAGConfig


class DocumentIngestor:
    """Handles document ingestion and indexing for RAG."""

    def __init__(self, config: RAGConfig):
        """Initialize the document ingestor.
        
        Args:
            config: RAG configuration object
        """
        self.config = config
        self.storage_path = Path(config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        embed_model = OpenAIEmbedding()
        
        # Configure text splitting
        text_splitter = TokenTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        node_parser = SimpleNodeParser(text_splitter=text_splitter)
        
        # Create service context
        self.service_context = ServiceContext.from_defaults(
            embed_model=embed_model,
            node_parser=node_parser,
        )
        
        # Load or create index
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.storage_path)
            )
            self.index = load_index_from_storage(
                storage_context,
                service_context=self.service_context
            )
        except:
            self.index = VectorStoreIndex(
                [],
                service_context=self.service_context
            )
    
    def add_document(self, content: str, metadata: Dict) -> str:
        """Add a document to the index.
        
        Args:
            content: Document text content
            metadata: Document metadata (filename, size, etc)
            
        Returns:
            str: Document ID
        """
        doc_id = str(uuid.uuid4())
        metadata["doc_id"] = doc_id
        
        document = Document(
            text=content,
            metadata=metadata
        )
        
        self.index.insert(document)
        self.index.storage_context.persist(str(self.storage_path))
        
        return doc_id
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index.
        
        Args:
            doc_id: Document ID to remove
            
        Returns:
            bool: True if document was found and removed
        """
        try:
            self.index.delete(doc_id)
            self.index.storage_context.persist(str(self.storage_path))
            return True
        except:
            return False
    
    def list_documents(self) -> List[Dict]:
        """List all indexed documents.
        
        Returns:
            List of document metadata dicts
        """
        docs = []
        for node in self.index.docstore.docs.values():
            if node.metadata.get("doc_id"):
                docs.append(node.metadata)
        return docs
    
    def reindex(self) -> None:
        """Rebuild the entire index from stored documents."""
        docs = self.list_documents()
        
        # Clear existing index
        self.index = VectorStoreIndex(
            [],
            service_context=self.service_context
        )
        
        # Re-add all documents
        for doc in docs:
            content = doc.pop("content", "")
            if content:
                self.add_document(content, doc)
                
    def get_relevant_context(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """Get relevant document chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of chunks to return (default: config.top_k)
            
        Returns:
            List of dicts with text and metadata
        """
        if top_k is None:
            top_k = self.config.top_k
            
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        
        context = []
        for node in nodes:
            context.append({
                "text": node.text,
                "metadata": node.metadata
            })
            
        return context