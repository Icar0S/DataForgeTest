import json

with open("storage/vectorstore/documents.json", encoding="utf-8") as f:
    data = json.load(f)

print(f'Documentos: {len(data["documents"])}')
print(f'Chunks keys: {len(data.get("chunks", {}))}')

total = sum(len(chunks) for chunks in data.get("chunks", {}).values())
print(f"Total de chunks: {total}")

# Show sample
sample_doc_id = list(data.get("chunks", {}).keys())[0]
sample_chunks = data["chunks"][sample_doc_id]
print(f"\nSample document chunks: {len(sample_chunks)}")
