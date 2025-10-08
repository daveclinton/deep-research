import requests
import subprocess
import chromadb
from typing import List, Dict, Any
import time


class BrightDataClient:
    """Client for interacting with Bright Data API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.brightdata.com/dca/trigger"

    def fetch_research_data(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Fetch research data using Bright Data API"""
        payload = {
            "query": query,
            "limit": limit,
            "format": "structured"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            print(f"📡 Fetching research data for: {query}")
            response = requests.post(
                self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(
                f"✅ Successfully fetched {len(data.get('results', []))} results")
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Bright Data API error: {e}")
            return {"error": str(e), "results": []}


class OllamaProcessor:
    """Handler for local Ollama model operations"""

    def __init__(self, model: str = "llama2"):
        self.model = model
        self._check_ollama_available()

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is installed and accessible"""
        try:
            result = subprocess.run(
                ['ollama', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                print(
                    "❌ Ollama not found. Please install Ollama from https://ollama.ai/")
                return False
            print(f"✅ Ollama is available. Using model: {self.model}")
            return True
        except Exception as e:
            print(f"❌ Ollama check failed: {e}")
            return False

    def summarize_content(self, content: str, max_length: int = 2000) -> str:
        """Summarize content using local Ollama model"""
        if not content.strip():
            return "No content available for summarization"

        # Truncate content to avoid context limits
        truncated_content = content[:max_length]

        prompt = f"""
        Please provide a concise summary of the following content. 
        Focus on key points, main ideas, and important findings.
        
        Content:
        {truncated_content}
        
        Summary:
        """

        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Summarization error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "Summarization timed out after 2 minutes"
        except Exception as e:
            return f"Summarization failed: {str(e)}"

    def analyze_research_topic(self, query: str) -> str:
        """Generate research questions and angles for a topic"""
        prompt = f"""
        For the research topic: "{query}"
        
        Please provide:
        1. Key sub-topics to investigate
        2. Important questions to answer
        3. Potential sources to explore
        4. Expected findings or insights
        
        Format your response in a structured way.
        """

        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Analysis error: {result.stderr}"

        except Exception as e:
            return f"Research analysis failed: {str(e)}"


class ResearchKnowledgeBase:
    """Vector database for storing and retrieving research data"""

    def __init__(self, persist_directory: str = "./research_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="research_data",
            metadata={"description": "Stored research articles and findings"}
        )

    def store_research(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Store research documents in the knowledge base"""
        if not documents:
            print("⚠️ No documents to store")
            return

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"💾 Stored {len(documents)} research documents")
        except Exception as e:
            print(f"❌ Error storing research: {e}")

    def search_similar(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for similar research content"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {"documents": [], "metadatas": [], "ids": []}

    def get_all_documents(self) -> Dict[str, Any]:
        """Retrieve all stored research documents"""
        try:
            # ChromaDB doesn't have a direct "get all" method, so we use a broad search
            results = self.collection.query(
                query_texts=["research"],
                n_results=1000  # Large number to get all documents
            )
            return results
        except Exception as e:
            print(f"❌ Error retrieving documents: {e}")
            return {"documents": [], "metadatas": [], "ids": []}


class DeepResearchAgent:
    """Main research agent that orchestrates the entire research process"""

    def __init__(self, bright_data_api_key: str, ollama_model: str = "llama2"):
        self.bright_data_client = BrightDataClient(bright_data_api_key)
        self.ollama_processor = OllamaProcessor(ollama_model)
        self.knowledge_base = ResearchKnowledgeBase()

    def conduct_research(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Conduct comprehensive research on a given query"""
        print(f"🔍 Starting research on: {query}")

        # Step 1: Fetch data from Bright Data
        research_data = self.bright_data_client.fetch_research_data(
            query, limit)

        if "error" in research_data:
            return {"error": research_data["error"], "summaries": []}

        results = research_data.get("results", [])
        if not results:
            return {"error": "No research results found", "summaries": []}

        # Step 2: Process and store research data
        summaries = []
        documents = []
        metadatas = []
        ids = []

        for i, item in enumerate(results):
            content = item.get('content', '')
            title = item.get('title', f'Result {i+1}')
            source = item.get('source', 'Unknown')

            if content:
                # Step 3: Generate AI summary
                print(f"🤖 Summarizing result {i+1}/{len(results)}...")
                summary = self.ollama_processor.summarize_content(content)

                summaries.append({
                    "title": title,
                    "source": source,
                    "summary": summary,
                    "original_content": content[:500] + "..." if len(content) > 500 else content
                })

                # Prepare for knowledge base storage
                documents.append(content)
                metadatas.append({
                    "title": title,
                    "source": source,
                    "query": query,
                    "timestamp": time.time()
                })
                ids.append(f"doc_{int(time.time())}_{i}")

        # Store in knowledge base
        if documents:
            self.knowledge_base.store_research(documents, metadatas, ids)

        # Step 4: Generate overall research insights
        print("💡 Generating overall research insights...")
        all_content = " ".join([item.get('content', '')
                               for item in results if item.get('content')])
        overall_insights = self.ollama_processor.summarize_content(
            all_content[:3000])

        return {
            "query": query,
            "total_sources": len(results),
            "summaries": summaries,
            "overall_insights": overall_insights,
            "raw_data": research_data
        }

    def get_research_history(self) -> Dict[str, Any]:
        """Retrieve all previous research from knowledge base"""
        return self.knowledge_base.get_all_documents()

    def search_previous_research(self, query: str) -> Dict[str, Any]:
        """Search through previous research findings"""
        return self.knowledge_base.search_similar(query)
