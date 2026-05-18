import pandas as pd
import requests
from pathlib import Path
import os
import argparse


def download_files(excel_file, transcript_dir, audio_dir, download_audio=False):
    # Create directories if they don't exist
    os.makedirs(transcript_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    # === READ THE EXCEL ===
    df = pd.read_excel(excel_file)

    transcript_downloaded = 0
    transcript_skipped = 0
    audio_downloaded = 0
    audio_skipped = 0
    transcript_failed = 0
    audio_failed = 0

    # === LOOP THROUGH EACH ROW ===
    for _, row in df.iterrows():
        rec_id = row["rec_id"]
        rec_url = row["rec_url"]
        transcript_url = row["transcript_url"]

        # Convert rec_id to string
        if isinstance(rec_id, float) and rec_id.is_integer():
            rec_id = int(rec_id)

        rec_id = str(rec_id)

        txt_filename = f"{rec_id}.txt"
        audio_filename = f"{rec_id}.wav"

        audio_path = Path(audio_dir) / audio_filename
        transcript_path = Path(transcript_dir) / txt_filename

        # === Download Transcript ===
        try:
            if not transcript_path.exists():
                print(f"Downloading transcript: {txt_filename}")

                resp = requests.get(transcript_url, timeout=60)
                resp.raise_for_status()

                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(resp.text)

                transcript_downloaded += 1
                print(f"Saved transcript: {transcript_path}")

            else:
                transcript_skipped += 1
                print(f"Transcript already exists: {transcript_path}")

        except Exception as e:
            transcript_failed += 1
            print(f"Failed to download transcript for {rec_id}: {e}")

        # === Download Audio ===
        if download_audio:
            try:
                if not audio_path.exists():
                    print(f"Downloading audio: {audio_filename}")

                    resp = requests.get(rec_url, stream=True, timeout=120)
                    resp.raise_for_status()

                    with open(audio_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    audio_downloaded += 1
                    print(f"Saved audio: {audio_path}")

                else:
                    audio_skipped += 1
                    print(f"Audio already exists: {audio_path}")

            except Exception as e:
                audio_failed += 1
                print(f"Failed to download audio for {rec_id}: {e}")

    # === SUMMARY ===
    print("\n===== DOWNLOAD SUMMARY =====")
    print(f"Transcripts downloaded : {transcript_downloaded}")
    print(f"Transcripts skipped    : {transcript_skipped}")
    print(f"Transcripts failed     : {transcript_failed}")
    print(f"Audio files downloaded : {audio_downloaded}")
    print(f"Audio files skipped    : {audio_skipped}")
    print(f"Audio files failed     : {audio_failed}")
    print("=============================")
    print("\nAll downloads complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download transcripts and audio files from Excel sheet")
    parser.add_argument("--excel_file", type=str, required=True, help="Path to input Excel file")
    parser.add_argument("--transcript_dir", type=str, required=True, help="Directory to save transcript files")
    parser.add_argument("--audio_dir", type=str, required=True, help="Directory to save audio files")
    parser.add_argument("--download_audio", action="store_true", help="Enable audio download")

    args = parser.parse_args()

    download_files(
        excel_file=args.excel_file,
        transcript_dir=args.transcript_dir,
        audio_dir=args.audio_dir,
        download_audio=args.download_audio,
    )