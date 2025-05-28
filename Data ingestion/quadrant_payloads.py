import os
import glob
import json
import uuid 


def create_payloads(
    summary_dir="Summary_dump",
    metadata_dir="Metadata_dump",
    output_file="qdrant_payloads.jsonl"
):
    summary_files = glob.glob(os.path.join(summary_dir, "*_summary.txt"))

    # Only create directory if one is specified in the output path
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as out_file:
        for summary_path in summary_files:
            point_id = str(uuid.uuid4())
            file_base = os.path.basename(summary_path).replace("_summary.txt", "")
            metadata_path = os.path.join(metadata_dir, f"{file_base}.json")

            if not os.path.exists(metadata_path):
                print(f"⚠️ Skipping: {file_base} — Metadata not found.")
                continue

            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = f.read().strip()

            payload = {
                "id": point_id,
                "summary": summary,
                "metadata_path": metadata_path,
                "file_name": file_base
            }

            out_file.write(json.dumps(payload) + "\n")
            print(f"✅ Payload added for: {file_base}")

    print(f"\n🎉 Payloads saved to: {output_file}")

if __name__ == "__main__":
    create_payloads()
