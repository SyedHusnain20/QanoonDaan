import pickle
import os
from config import CHUNKS_STORE

print("=" * 50)
print("🔍 QanoonDaan Database Diagnostic")
print("=" * 50)

if not os.path.exists(CHUNKS_STORE):
    print(f"❌ ERROR: {CHUNKS_STORE} not found!")
else:
    with open(CHUNKS_STORE, "rb") as f:
        chunks = pickle.load(f)
    
    # Count chunks per PDF
    sources = {}
    for c in chunks:
        src = c["source"]
        sources[src] = sources.get(src, 0) + 1
        
    print(f"\n📚 Total chunks in database: {len(chunks)}")
    print("\n📄 PDFs currently indexed:")
    for src, count in sorted(sources.items()):
        print(f"   - {src}  ({count} chunks)")
        
    print("\n" + "=" * 50)
    print("📝 Analysis:")
    
    # Check for PPC
    ppc_found = any("penal" in src.lower() or "ppc" in src.lower() for src in sources.keys())
    if not ppc_found:
        print("⚠️  WARNING: No file containing 'penal' or 'ppc' was found in the database!")
        print("   This is exactly why Section 365/368/369 lookups are failing.")
        print("   You need to ingest the Pakistan Penal Code PDF into your vector store.")
    else:
        print("✅ PPC document is present in the database.")
        
    # Check for Labor laws
    labor_found = any("wage" in src.lower() or "labor" in src.lower() or "labour" in src.lower() or "industrial" in src.lower() for src in sources.keys())
    if not labor_found:
        print("⚠️  WARNING: No labor/wage-related acts found in the database!")
        print("   This is why the 'boss not paying salary' question is failing.")