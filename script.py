import json

def trim_json_results(input_path: str, output_path: str, keep_ratio: float = 0.5):
    with open(input_path, "r", encoding="utf-8") as f:
        full_data = json.load(f)

    # Trim the "results" list
    all_results = full_data.get("results", [])
    half_length = int(len(all_results) * keep_ratio)
    trimmed_results = all_results[:half_length]

    # Update the original structure with fewer results
    full_data["results"] = trimmed_results
    full_data["meta"]["results"]["total"] = len(trimmed_results)

    # Write to new file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2)

    print(f"✅ Trimmed file saved to {output_path} with {len(trimmed_results):,} results.")


if __name__ == "__main__":
    trim_json_results(
        r"C:\Users\REESAV\Desktop\misogi-assignments\day-11[advance-RAG]\medical_ai_assistant\data\drug-event.json",
        r"C:\Users\REESAV\Desktop\misogi-assignments\day-11[advance-RAG]\medical_ai_assistant\data\drug-event-half.json"
    )
