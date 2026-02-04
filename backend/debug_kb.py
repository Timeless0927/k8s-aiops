import sys
import os

# Add backend to sys.path
sys.path.append(os.getcwd())

from plugins.builtins.knowledge_plugin.tools import search_knowledge, _load_insights

print("--- DEBUGGING KNOWLEDGE BASE ---")

# 1. Check if Insights Load
insights = _load_insights()
print(f"Loaded {len(insights)} insights.")
for i in insights:
    print(f" - [{i.get('id')}] Topic: {i.get('topic')} | Tags: {i.get('tags')}")

# 2. Test Search
query = "TestAlert"
print(f"\nSearching for '{query}'...")
result = search_knowledge(query, category="insights")
print("RESULT:")
print(result)

query2 = "pod-123"
print(f"\nSearching for '{query2}'...")
result2 = search_knowledge(query2, category="insights")
print("RESULT:")
print(result2)
