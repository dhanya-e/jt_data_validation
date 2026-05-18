#!/bin/bash

set -e

# Download audio and json transcript file from excel shared by JT
# if transcript has issues - formatting issues, numbers not expanded, ask JT team to correct.
# to re-check, download only transcripts (download_audio=False)
cd /home/dhanyae/JT_data_validation/
# download audio and corresponding GT json from excel shared by Joshtalks
data_dir=/home/dhanyae/data/JoshTalks/
delivery_date=35hrs_13April2026_to_30April2026
out_datadir=$data_dir/annotated_data_${delivery_date}

mkdir -p "$out_datadir"

python python_code/download_audio_json.py \
  --excel_file $data_dir/annotation_excel/IISC_Healthcare_Annotation_${delivery_date}.xlsx \
  --transcript_dir $out_datadir/transcript_json \
  --audio_dir $out_datadir/audio \
  --download_audio


# Convert audio to mono, sampling rate - 16Khz
inpdir=$data_dir/annotated_data_${delivery_date}/audio
outdir=$data_dir/annotated_data_${delivery_date}/audio_mono

mkdir -p "$outdir"

for f in "$inpdir"/*.wav; do
  ffmpeg -y -i "$f" -ac 1 -ar 16000 -vn "${outdir}/$(basename "$f")"
done

# Extract the ground truth transcript for the entire audio from the trnscript json
# check for non-hindi characters - numbers, English words, symbols
python python_code/extract_fullaudio_gt.py \
  --transcript_folder $out_datadir/transcript_json \
  --output_folder $out_datadir/fullAudio_gt \
  --master_xlsx $data_dir/annotation_excel/IISC_Healthcare_Annotation_${delivery_date}.xlsx \
  --output_excel $out_datadir/output.xlsx

# Extract the ground truth transcript segment by segment from the trnscript json
python python_code/extract_segment_gt.py \
  --transcript_folder $out_datadir/transcript_json \
  --output_folder $out_datadir/segmented_gt