import os
import json
import re
import argparse

# ===============================
# Argument Parser
# ===============================
parser = argparse.ArgumentParser(description="Generate segmented ground-truth transcript files.")
parser.add_argument("--transcript_folder", type=str, required=True, help="Folder containing transcript JSON/TXT files")
parser.add_argument("--output_folder", type=str, required=True, help="Folder to save segmented output files")

args = parser.parse_args()

# ===============================
# Paths
# ===============================
transcript_folder = args.transcript_folder
output_folder = args.output_folder

os.makedirs(output_folder, exist_ok=True)

# ===============================
# Iterate over transcript files
# ===============================
results_all = []
csv_results = []

for text_file in os.listdir(transcript_folder):

    if not text_file.lower().endswith(".txt"):
        continue

    transcript_path = os.path.join(transcript_folder, text_file)

    base_name = os.path.splitext(text_file)[0]

    print(f"Processing: {transcript_path}")

    # ===============================
    # Load transcript JSON
    # ===============================
    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ===============================
    # Map speaker_id -> role
    # ===============================
    speaker_roles = {
        spk["id"]: spk["role"].strip()
        for spk in data["metadata"]["speakers"]
    }

    # ===============================
    # Extract NSP labels dynamically
    # ===============================
    nsp_labels = data["annotations"]["labels"]["NSP"]

    # Add custom labels
    nsp_labels += [
        '<FAN_NOISE >','<FAN_NOISE<HORN>','<NOISE',
        'NOISE>','<NOISE>','<FAN_',
        '<Overlap_ speech>','<overlap_speech>',
        '<overlapping>','<PAGE _FLAPPING>',
        '<OVERLAPPING_ SPEECH>',
        '<OVERLAP _SPEECH>',
        '<OVERLAPING _SPEECH>',
        '<overlapping><inaudible>',
        '\u200c',
        'CHILD_CRYING>',
        '<CHILD_CRYING',
        'OVERLAPPING_SPEECH>',
        '<CHILD_CRYING',
        '<BACKGROUND_NOISE><OVERLAPPING_SPEECH>',
        'FAN_NOISE>',
        'BACKGROUND_NOISE>',
        'BACKGROUND_CONVERSATION>',
        '<OVERLAPPING _SPEECH>',
        '<Overlap _speech>',
        '<Overlap speech>',
        'inaudible',
        '<Overlapping_Speech>',
        '<inaudible>',
        '<BACKGROUND_NOISE> <INAUDIBLE> ',
        '<BACKGROUND CONVERSATION>',
        '<UNINTELLIGIBLE>',
        '<BACKGROUND_NOISE',
        '<BACKGROUND_NOISE>>',
        '<BACKGROUND_NO',
        '<Blank>',
        '<OVERLAPPING_SPEECH><BACKGROUND_NO<FAN_NOISE>',
        'INAUDIBLE',
        '<overlap _speech>',
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

        pattern = "|".join(
            re.escape(label) for label in nsp_labels
        )

        cleaned = re.sub(pattern, "", text).strip()

        cleaned = re.sub(r'<[^>]*>', '', cleaned)

        cleaned = re.sub(r"[<>_]", " ", cleaned)

        cleaned = re.sub(
            r'[|।\.\?,!;:"\'\-–—\(\)\[\]]+',
            ' ',
            cleaned
        )

        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned.strip()

    # ===============================
    # Extract segments
    # ===============================
    segments = data["transcriptions"]

    # ===============================
    # Write output
    # ===============================
    output_file = os.path.join(
        output_folder,
        f"{base_name}.txt"
    )

    with open(output_file, "w", encoding="utf-8") as f_out:

        for i, seg in enumerate(segments, start=1):

            start_ms = seg["start_time"]
            end_ms = seg["end_time"]

            speaker_id = seg["speaker_id"]

            speaker_role = speaker_roles.get(
                speaker_id,
                "Unknown"
            )

            gt_text = seg["transcript"]

            clean_gt = clean_transcript(gt_text)

            seg_filename = f"{base_name}_{i:04d}.wav"

            f_out.write(
                f"{base_name}\t"
                f"{seg_filename[:-4]}\t"
                f"{speaker_id}\t"
                f"{speaker_role}\t"
                f"{start_ms:.3f}\t"
                f"{end_ms:.3f}\t"
                f"{clean_gt}\n"
            )

    print(f"Saved: {output_file}")