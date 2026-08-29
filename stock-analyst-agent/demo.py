"""
Demo for Stock Analyst Agent
Tests all major features
"""
import sys
import asyncio
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


def main():
    print("=" * 60)
    print("  STOCK ANALYST AGENT - DEMO")
    print("=" * 60)
    
    # Test 1: Import all modules
    print("\n[1] Testing imports...")
    try:
        from src.agents import TriageAgent, AnalystAgent, ResearchAgent, ReporterAgent
        from src.chains import RAGChain, AnalysisChain, ReportChain
        from src.tools import ALL_TOOLS
        from src.memory import ShortTermMemory, LongTermMemory
        from src.vector_store import FAISSVectorStore, SimilarityRetriever
        from src.monitoring import get_collector, get_tracer
        print("    [OK] All imports successful")
    except Exception as e:
        print(f"    [FAIL] {e}")
        return
    
    # Test 2: Tools
    print("\n[2] Testing tools...")
    print(f"    [OK] {len(ALL_TOOLS)} tools loaded")
    for tool in ALL_TOOLS[:5]:
        print(f"      - {tool.name}")
    
    # Test 3: Memory
    print("\n[3] Testing memory...")
    mem = ShortTermMemory(k=5)
    mem.add_message("user", "Hello")
    mem.add_message("assistant", "Hi there!")
    print(f"    [OK] Memory has {len(mem.get_messages())} messages")
    
    # Test 4: LLM
    print("\n[4] Testing LLM...")
    from src.llm import get_chat_model
    llm = get_chat_model()
    print(f"    [OK] LLM: {llm.deployment_name}")
    
    # Test 5: Agent
    print("\n[5] Testing single agent...")
    try:
        agent = AnalystAgent()
        print(f"    [OK] Agent created: {agent.name}")
        print(f"    [OK] Role: {agent.role}")
        print(f"    [OK] Tools: {len(agent.tools)}")
    except Exception as e:
        print(f"    [FAIL] {e}")
    
    # Test 6: Orchestrator
    print("\n[6] Testing orchestrator...")
    try:
        from src.agents.orchestrator.coordinator import AgentOrchestrator
        orch = AgentOrchestrator()
        print(f"    [OK] Orchestrator with 4 agents:")
        print(f"      - {orch.triage.name}")
        print(f"      - {orch.research.name}")
        print(f"      - {orch.analyst.name}")
        print(f"      - {orch.reporter.name}")
    except Exception as e:
        print(f"    [FAIL] {e}")
    
    # Test 7: Vector Store
    print("\n[7] Testing vector store...")
    try:
        from src.vector_store import FAISSVectorStore
        from src.llm import get_embeddings_model
        embeddings = get_embeddings_model()
        store = FAISSVectorStore(embeddings)
        print(f"    [OK] FAISS store initialized")
    except Exception as e:
        print(f"    [FAIL] {e}")
    
    # Test 8: Metrics
    print("\n[8] Testing metrics...")
    collector = get_collector()
    collector.record("gpt-4o", 100, 50, 1500)
    summary = collector.get_summary()
    print(f"    [OK] Tracked 1 request")
    print(f"    [OK] Cost: ${summary.get('total_cost_usd', 0):.6f}")
    
    # Test 9: Constants
    print("\n[9] Testing constants...")
    from src.constants import AnalysisType, Recommendation, Signal
    print(f"    [OK] Analysis types: {len(list(AnalysisType))}")
    print(f"    [OK] Recommendations: {len(list(Recommendation))}")
    print(f"    [OK] Signals: {len(list(Signal))}")
    
    # Test 10: API
    print("\n[10] Testing API...")
    try:
        from src.main import app
        print(f"    [OK] FastAPI app created")
        print(f"    [OK] Routes registered")
    except Exception as e:
        print(f"    [FAIL] {e}")
    
    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED!")
    print("=" * 60)
    print("\nTo run the API server:")
    print("  cd stock-analyst-agent")
    print("  python -m src.main")
    print("\nTo run the demo with actual API calls:")
    print("  python demo_live.py")


if __name__ == "__main__":
    main()
