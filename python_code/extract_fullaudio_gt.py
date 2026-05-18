import os
import json
import re
import argparse
import pandas as pd
from pathlib import Path

# ===============================
# Argument Parser
# ===============================
parser = argparse.ArgumentParser(description="Process transcript JSON files and merge results into Excel.")
parser.add_argument("--transcript_folder", type=str, required=True, help="Path to transcript JSON folder")
parser.add_argument("--output_folder", type=str, required=True, help="Path to save cleaned transcript txt files")
parser.add_argument("--master_xlsx", type=str, required=True, help="Path to master Excel file")
parser.add_argument("--output_excel", type=str, required=True, help="Path to save merged Excel output")

args = parser.parse_args()

# ===============================
# Paths from arguments
# ===============================
transcript_folder = args.transcript_folder
output_folder = args.output_folder
master_xlsx = args.master_xlsx
output_excel = args.output_excel

os.makedirs(output_folder, exist_ok=True)

# ===============================
# Iterate over transcript files
# ===============================
results = []

for text_file in os.listdir(transcript_folder):

    if not text_file.lower().endswith(".txt"):
        continue

    transcript_path = os.path.join(transcript_folder, text_file)
    base_name = os.path.splitext(text_file)[0]

    print(f"transcript_path {transcript_path}")

    # --- Load transcript JSON ---
    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- Extract NSP labels dynamically ---
    nsp_labels = data["annotations"]["labels"]["NSP"]

    # Add custom labels
    nsp_labels += [
        '<overlapping speech >','<backgroud speech>','<FAN_NOISE >',
        '<FAN_NOISE<HORN>','<NOISE','NOISE>','<NOISE>','<FAN_',
        '<Overlap_ speech>','<overlap_speech>','<overlapping>',
        '<PAGE _FLAPPING>','<OVERLAPPING_ SPEECH>',
        '<OVERLAP _SPEECH>','<OVERLAPING _SPEECH>',
        '<overlapping><inaudible>', '\u200c',
        'CHILD_CRYING>', '<CHILD_CRYING',
        'OVERLAPPING_SPEECH>','<CHILD_CRYING',
        '<BACKGROUND_NOISE><OVERLAPPING_SPEECH>',
        'FAN_NOISE>', 'BACKGROUND_NOISE>',
        'BACKGROUND_CONVERSATION>',
        '<OVERLAPPING _SPEECH>', '<Overlap _speech>',
        '<Overlap speech>', 'inaudible',
        '<Overlapping_Speech>','<inaudible>',
        '<BACKGROUND_NOISE> <INAUDIBLE> ',
        '<BACKGROUND CONVERSATION>',
        '<UNINTELLIGIBLE>','<BACKGROUND_NOISE',
        '<BACKGROUND_NOISE>>', '<BACKGROUND_NO',
        '<Blank>',
        '<OVERLAPPING_SPEECH><BACKGROUND_NO<FAN_NOISE>',
        'INAUDIBLE','<overlap _speech>',
        '<FAN_NOISE',
        '<FAN_NOISE<FAN_NOISE>',
        '<FAN_NOISE<HORN>',
        '<OVERLAPPING_SPEECH',
        '<BACKGROUND_NOISE',
        '<KNOCKING_ON_A_SURFACE>',
        '<DOG_BARKING',
        '<Coughing>',
        '<HORN>',
        '<Laughing>',
        '<LIP_SMACKING>',
        '<MUSIC_PLAYING>',
        '<TRAFFIC_NOISE>',
        '<FAN_NOISE>',
        '<BACKGROUND_CONVERSATI ON>',
        '<PHONE_RINGING>'
    ]

    # ===============================
    # Clean transcript function
    # ===============================
    def clean_transcript(text):

        pattern = "|".join(re.escape(label) for label in nsp_labels)

        cleaned = re.sub(pattern, "", text).strip()
        cleaned = re.sub(r'<[^>]*>', '', cleaned)
        cleaned = re.sub(r"[<>_]", " ", cleaned)
        cleaned = re.sub(r'[|।\.\?,!;:"\'\-–—\(\)\[\]]+', '', cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned

    # ===============================
    # Extract segments
    # ===============================
    segments = data["transcriptions"]

    gt_text_all = ""

    for i, seg in enumerate(segments, start=1):

        gt_text = seg["transcript"]

        if gt_text == "" or gt_text.lower() == "blank":
            continue

        clean_gt = clean_transcript(gt_text)

        gt_text_all += clean_gt + " "

    # ===============================
    # Write cleaned transcript
    # ===============================
    output_path = os.path.join(output_folder, f"{base_name}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gt_text_all.strip())

    print(f"output file {output_path}")

    # ===============================
    # Detect numbers and non-Hindi chars
    # ===============================
    numbers = re.findall(r"\d", gt_text_all)

    non_hindi = re.findall(
        r"[^\u0900-\u097F\s.,!?;:()\[\]\"'’“”-]",
        gt_text_all
    )

    print(f"non-hindi characters\n{numbers}\n{non_hindi}")

    results.append({
        "rec_hash": base_name,
        "NonHindi_Chars": non_hindi,
        "Numbers": numbers,
    })

# ===============================
# Merge with master Excel
# ===============================
df_results = pd.DataFrame(results)

df_master = pd.read_excel(master_xlsx)

# ===============================
# Build rec_hash
# ===============================
def build_rec_hash(row):

    rec_id = row["rec_id"]

    if isinstance(rec_id, float) and rec_id.is_integer():
        rec_id = int(rec_id)

    rec_id = str(rec_id).strip()

    return f"{rec_id}"

df_master["rec_hash"] = df_master.apply(build_rec_hash, axis=1)

# ===============================
# Merge
# ===============================
merged = df_master.merge(
    df_results,
    on="rec_hash",
    how="left"
)

# ===============================
# Save Excel
# ===============================
merged.to_excel(output_excel, index=False)

print(f"Output saved to: {output_excel}")