# Project Plan: Cybersecurity Research Assistant

**Core Goal:** To create an AI-powered chatbot that assists cybersecurity researchers by providing quick access to and insights from a vast knowledge base of vulnerabilities, attack patterns, and other relevant cybersecurity information.

**Key Technologies:** NVIDIA Agent Intelligence toolkit, LLMs (potentially NVIDIA NeMo), RAG Pipelines, Vector Databases, Embedding Models.

---

## Phase 1: Data Foundation

This phase focuses on gathering, cleaning, and structuring the data that will form the knowledge base of your assistant.

### Stage 1: Data Acquisition & Initial Collection

*   **Substage 1.1: Identify Core Data Sources**
    *   **Current:**
        *   NVD CVE Data (National Vulnerability Database)
        *   MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)
    *   **To Do:**
        *   Ensure current data sources are up-to-date.
        *   **Consider Additional Sources (for future enhancement):**
            *   MITRE CAPEC (Common Attack Pattern Enumeration and Classification)
            *   MITRE CWE (Common Weakness Enumeration)
            *   Security Blogs & Threat Reports (e.g., KrebsOnSecurity, FireEye, Mandiant)
            *   Academic Research Papers (e.g., from arXiv, IEEE, ACM specific to cybersecurity)
            *   Vendor Advisories
            *   Exploit Database (Exploit-DB)

*   **Substage 1.2: Data Fetching/Downloading**
    *   **Current:** Existing scripts or manual processes for NVD JSON feeds and ATT&CK STIX data.
    *   **To Do:**
        *   Automate downloads for easy data refresh.
        *   Store raw downloaded data in a structured way (e.g., `data/raw/nvd/`, `data/raw/attack-stix/`).

*   **Substage 1.3: Initial Storage**
    *   **Current:** Raw data in `nvd_filtered_minimal/` and `attack-stix/enterprise-attack/`.
    *   **To Do:** Maintain this organized structure. Create similar directories for new data sources.

### Stage 2: Data Preprocessing & Cleaning (Leveraging `preprocessing.py`)

*   **Substage 2.1: Text Extraction**
    *   **Current:** `preprocessing.py` handles CVEs (ID, description) and ATT&CK patterns (name, description).
    *   **To Do:**
        *   Review warning messages from `preprocessing.py` and refine parsing logic if needed.
        *   Develop extraction scripts for new data sources.

*   **Substage 2.2: Data Cleaning**
    *   **Current:** `preprocessing.py` includes HTML tag removal and whitespace normalization for ATT&CK.
    *   **To Do:**
        *   Ensure similar cleaning for CVE descriptions (whitespace normalization).
        *   Consider other cleaning: removing irrelevant special characters, standardizing encodings, handling boilerplate text.

*   **Substage 2.3: Format Standardization**
    *   **Current:** `preprocessing.py` outputs to `data/preprocessed/cves.txt` and `data/preprocessed/attack_patterns.txt` (`ID: Description` or `Name: Description`, separated by `\n\n`).
    *   **To Do:** This format is suitable for chunking. Ensure each "document" has a clear identifier and text.

*   **Substage 2.4: Content Enrichment (Optional but high-impact)**
    *   **To Do (Consider for later iterations):**
        *   Link CVEs to ATT&CK techniques.
        *   Map CVEs to CWEs.
        *   Add timestamps/source info for traceability.

*   **Substage 2.5: Quality Checks**
    *   **To Do:**
        *   Periodically review preprocessed text for anomalies.
        *   Check for high numbers of "No description available" entries.
        *   Ensure formatting consistency.

---

## Phase 2: Knowledge Base Construction (Focus on Chunking)

This phase transforms your preprocessed text into a format suitable for AI models, particularly for Retrieval Augmented Generation (RAG).

### Stage 3: Data Chunking

*   **Substage 3.1: Define Chunking Strategy**
    *   **Considerations:** Chunk size, overlap, metadata.
    *   **Strategies:**
        *   **CVEs:**
            *   Option 1 (Simple): Each CVE description as one chunk.
            *   Option 2 (Long descriptions): Split by paragraphs or use sentence splitter.
        *   **ATT&CK Patterns:**
            *   Option 1 (Simple): Each technique description as one chunk.
            *   Option 2 (Recommended): Paragraph-based splitting, Recursive Character Splitting (e.g., LangChain), or Sentence Splitting (NLTK/spaCy) followed by grouping.

*   **Substage 3.2: Implement Chunking Logic**
    *   **To Do:**
        *   Create `chunk_data.py`.
        *   Script to read preprocessed files, extract ID/Name and text, apply chunking strategy.
        *   Example (simple, assuming `\n\n` separation):
            ```python
            # In chunk_data.py (conceptual)
            def load_and_chunk_file(filepath, source_type):
                chunks_with_metadata = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                entries = content.split("\n\n") 
                for entry in entries:
                    if not entry.strip():
                        continue
                    
                    parts = entry.split(":", 1)
                    identifier = parts[0].strip()
                    text_content = parts[1].strip() if len(parts) > 1 else "No description available."

                    chunks_with_metadata.append({
                        "id": identifier,
                        "source": source_type, 
                        "text": text_content,
                    })
                return chunks_with_metadata
            ```
        *   Example (advanced chunking with LangChain):
            ```python
            # Conceptual addition to chunk_data.py
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            # text_splitter = RecursiveCharacterTextSplitter(
            #     chunk_size=500, 
            #     chunk_overlap=50 
            # )
            # ... inside your loop ...
            # sub_chunks = text_splitter.split_text(text_content)
            # for i, sub_chunk in enumerate(sub_chunks):
            #     chunks_with_metadata.append({
            #         "id": f"{identifier}_part_{i+1}",
            #         "original_id": identifier,
            #         "source": source_type,
            #         "text": sub_chunk
            #     })
            ```

*   **Substage 3.3: Metadata Association**
    *   **To Do:** Ensure each chunk stores: chunk text, original identifier, source type, optional original file name/section.

*   **Substage 3.4: Chunk Overlap**
    *   **To Do:** Configure text splitters for overlap (e.g., 10-20% of chunk size) to preserve context.

*   **Substage 3.5: Output Format for Chunks**
    *   **To Do:**
        *   Store chunked data (e.g., JSONL file: `data/chunked/all_chunks.jsonl`).
        *   Example line: `{"id": "CVE-2023-12345", "source": "CVE", "text": "The vulnerability description chunk..."}`

### Stage 4: Embedding Generation

*   **Substage 4.1: Choose an Embedding Model**
    *   **To Do:**
        *   **NVIDIA NeMo Embeddings:** (e.g., `NV-EmbedQA`).
        *   Open-source Sentence Transformers (e.g., `all-MiniLM-L6-v2`).
        *   Consider models specialized for technical/security text.

*   **Substage 4.2: Generate Embeddings for Chunks**
    *   **To Do:**
        *   Script to load chunked data.
        *   Generate vector embedding for each chunk's text.
        *   Leverage NVIDIA GPUs for speed.

*   **Substage 4.3: Store Embeddings**
    *   **To Do:** Store embeddings with chunk text and metadata, typically handled by the vector database or temporarily on disk.

### Stage 5: Vector Indexing & Retrieval

*   **Substage 5.1: Select a Vector Database/Library**
    *   **To Do:**
        *   FAISS
        *   Milvus, Weaviate, Pinecone
        *   LangChain/LlamaIndex Vector Stores
        *   Consider options accelerated with NVIDIA hardware.

*   **Substage 5.2: Index Embeddings**
    *   **To Do:** Load chunks and embeddings into the chosen vector database to create a searchable index.

*   **Substage 5.3: Implement Retrieval Logic**
    *   **To Do:**
        *   Develop a function: takes user query -> embeds query -> queries vector DB -> returns top-K similar chunks.
        *   This is core to the RAG pipeline.

---

## Phase 3: Agent Development & Integration

### Stage 6: Agent/Chatbot Development (NVIDIA Agent Intelligence Toolkit)

*   **Substage 6.1: Set up NVIDIA Agent Toolkit Environment**
    *   **To Do:** Install, configure, and familiarize with the toolkit.

*   **Substage 6.2: Design Agent Architecture (RAG)**
    *   **To Do:**
        1.  User query input.
        2.  Optional query rephrasing/keyword extraction.
        3.  Query embedding.
        4.  Vector store query for relevant chunks (context).
        5.  Query + context fed to LLM via prompt.
        6.  LLM generates response.

*   **Substage 6.3: Integrate LLM**
    *   **To Do:**
        *   **NVIDIA NeMo LLMs:** Prioritize (e.g., NeMo GPT models). Deploy with NVIDIA Triton Inference Server.
        *   Alternatively, other LLMs compatible with the Agent Toolkit.

*   **Substage 6.4: Connect to Vector Store for Retrieval**
    *   **To Do:** Integrate retrieval logic (Stage 5.3) into the agent's workflow.

*   **Substage 6.5: Develop Prompt Engineering Strategies**
    *   **To Do:** Craft prompts instructing LLM on using retrieved context. Example:
        `"Based on the following cybersecurity information: \n{context}\n\n Answer the question: {query}"`

*   **Substage 6.6: Implement Conversation Management**
    *   **To Do:** Manage conversation history for multi-turn interactions if needed.

*   **Substage 6.7: User Interface**
    *   **To Do:**
        *   Start with CLI for testing.
        *   Later, a basic web UI (Streamlit, Gradio, Flask) for user-friendliness.

---

## Phase 4: Evaluation & Iteration

### Stage 7: Evaluation & Iteration

*   **Substage 7.1: Define Evaluation Metrics**
    *   **To Do:**
        *   **Retrieval:** Precision@K, Recall@K.
        *   **Generation:** Relevance, accuracy, coherence, helpfulness.
        *   **End-to-End:** Task success rate.

*   **Substage 7.2: Create Test Datasets/Queries**
    *   **To Do:** Prepare realistic cybersecurity researcher questions.

*   **Substage 7.3: Perform Evaluation**
    *   **To Do:** Test system with queries; use automated and human evaluation.

*   **Substage 7.4: Iterate**
    *   **To Do:** Based on results, revisit previous stages (data, preprocessing, chunking, embeddings, retrieval, agent logic, prompts).

---

## Meeting the Scoring Criteria

*   **Real-World Novel Application:**
    *   Focus on solving specific researcher pain points.
    *   User-friendliness via clear UI and accurate answers.
    *   Novelty via unique data combinations or advanced analytical features.
*   **Technology Integration:**
    *   **NVIDIA Agent Toolkit:** Central.
    *   **NVIDIA NeMo:** For embeddings and/or LLMs.
    *   **NVIDIA Triton Inference Server:** For model deployment.
    *   **NVIDIA GPUs:** For training, embedding, inference.