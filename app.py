import streamlit as st
import os
import base64
from datetime import datetime
from research_agent import DeepResearchAgent


st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("./assets/bright-data-logo.png", "rb") as brightdata_logo:
    brightdata_logo = base64.b64encode(brightdata_logo.read()).decode()
    title_hmtl = f"""
    <div>
        <img src="data:image/png;base64,{brightdata_logo}" style="height: 60px; width:150px;"/>
        <h1 style="margin: 0; padding: 0; font-size: 2.5rem; font-weight: bold;">
            <span style="font-size:2.5rem;">🔎</span> Deep Research Agent with
            <span style="color: #0000FF;">Bright Data</span> & 
            <span style="color: #8564ff;">Llama</span>
        </h1>
    </div>
    """
    st.markdown(title_hmtl, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'research_agent' not in st.session_state:
        st.session_state.research_agent = None
    if 'research_history' not in st.session_state:
        st.session_state.research_history = []
    if 'current_research' not in st.session_state:
        st.session_state.current_research = None


def setup_sidebar():
    """Configure the sidebar with settings and controls"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.subheader("🔑 API Settings")
        bright_data_api = st.text_input(
            "Bright Data API Key:",
            type="password",
            value=os.getenv("BRIGHT_DATA_API_KEY", ""),
            help="Get your API key from Bright Data dashboard"
        )
        st.subheader("🤖 AI Model")
        ollama_model = st.selectbox(
            "Ollama Model:",
            ["llama2", "mistral", "llama2:13b", "llama2:70b", "codellama"],
            index=0,
            help="Select the Ollama model to use for summarization"
        )

        st.subheader("🔍 Research Settings")
        sources_limit = st.slider(
            "Number of sources:",
            min_value=5,
            max_value=50,
            value=20,
            help="Number of research sources to collect"
        )

        st.markdown("---")

        # Research History
        st.subheader("📚 Research History")
        if st.button("View Research History", use_container_width=True):
            view_research_history()

        st.markdown("---")
        st.markdown("### 📖 Resources")
        st.markdown("- [Bright Data Docs](https://brightdata.com/)")
        st.markdown("- [Ollama Guide](https://ollama.ai/)")
        st.markdown("- [Streamlit Docs](https://docs.streamlit.io/)")

        return bright_data_api, ollama_model, sources_limit


def view_research_history():
    """Display previous research sessions"""
    if st.session_state.research_agent:
        try:
            history = st.session_state.research_agent.get_research_history()
            if history and history.get('documents'):
                st.subheader("📖 Research History")
                for i, (doc, metadata) in enumerate(zip(history['documents'], history['metadatas'])):
                    with st.expander(f"Research {i+1}: {metadata.get('query', 'Unknown')}"):
                        st.write(
                            f"**Source:** {metadata.get('source', 'Unknown')}")
                        st.write(f"**Content Preview:** {doc[:200]}...")
        except Exception as e:
            st.error(f"Error loading research history: {e}")


def main():
    """Main application function"""
    initialize_session_state()

    st.markdown('<div class="main-header">🔎 Local Deep Research Agent</div>',
                unsafe_allow_html=True)
    st.markdown(
        "### Automated research powered by **Bright Data** & **Local AI**")

    bright_data_api, ollama_model, sources_limit = setup_sidebar()

    if bright_data_api and not st.session_state.research_agent:
        try:
            st.session_state.research_agent = DeepResearchAgent(
                bright_data_api_key=bright_data_api,
                ollama_model=ollama_model
            )
            st.sidebar.success("✅ Research Agent Initialized!")
        except Exception as e:
            st.error(f"Failed to initialize research agent: {e}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Research Topic")
        research_query = st.text_area(
            "Enter your research topic:",
            height=100,
            placeholder="Example: AI use cases in healthcare\nLatest developments in quantum computing\nSustainable energy solutions 2024...",
            value="AI use cases in healthcare"
        )

    with col2:
        st.subheader("🚀 Actions")
        run_research = st.button(
            "Start Research",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.research_agent
        )

        if st.button("Clear Results", use_container_width=True):
            st.session_state.current_research = None
            st.rerun()

    if run_research and research_query:
        if not st.session_state.research_agent:
            st.error("Please configure your API key in the sidebar")
            return

        with st.spinner("🔍 Conducting deep research... This may take a few minutes."):
            try:
                research_result = st.session_state.research_agent.conduct_research(
                    query=research_query,
                    limit=sources_limit
                )

                if "error" in research_result:
                    st.error(f"Research failed: {research_result['error']}")
                else:
                    st.session_state.current_research = research_result
                    st.session_state.research_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "query": research_query,
                        "result": research_result
                    })

            except Exception as e:
                st.error(f"Research error: {str(e)}")

    if st.session_state.current_research:
        research_data = st.session_state.current_research

        st.markdown("---")
        st.markdown(
            f'<div class="success-box">✅ Research Complete! Found {research_data["total_sources"]} sources</div>', unsafe_allow_html=True)

        st.subheader("💡 Overall Research Insights")
        st.markdown(
            f'<div class="summary-box">{research_data["overall_insights"]}</div>', unsafe_allow_html=True)

        st.subheader("📋 Source Summaries")

        for i, summary in enumerate(research_data["summaries"]):
            with st.expander(f"Source {i+1}: {summary['title']}", expanded=i == 0):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.markdown("**AI Summary:**")
                    st.info(summary['summary'])

                with col_b:
                    st.markdown("**Source Info:**")
                    st.write(f"🔗 **Source:** {summary['source']}")
                    st.write(
                        f"📝 **Content Preview:** {summary['original_content'][:200]}...")

        with st.expander("📊 View Raw Research Data"):
            st.json(research_data["raw_data"])

    elif not st.session_state.current_research:
        st.markdown("---")
        st.info("""
        ### 🚀 Getting Started
        
        1. **Configure API Keys**: Enter your Bright Data API key in the sidebar
        2. **Set Research Parameters**: Choose your model and number of sources
        3. **Enter Research Topic**: Type your research question in the text area
        4. **Start Research**: Click the 'Start Research' button to begin
        
        The agent will:
        - Fetch relevant data using Bright Data
        - Process and summarize with local Ollama models
        - Provide structured insights and source summaries
        - Store research in local knowledge base
        """)


if __name__ == "__main__":
    main()
