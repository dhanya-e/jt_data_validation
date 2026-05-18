# jt_data_validation

Data pre-processing code

## Stage 1: Data Download

### Folder Structure

The data directory must follow the standard directory structure below.

    data/<data_vendor>/<language>/
    |
    |-- data_excel/
    |   |-- delivery_data_<duration>_<date_of_delivery>.xlsx
    |   |-- Meta_Data_<duration>_<date_of_delivery>.xlsx
    |
    |-- dataset_<duration>_<date_of_delivery>/
        |
        |-- audio/
        |   |-- <recording_id>.wav
        |
        |-- transcripts/
            |-- <recording_id>.json

    ### Example structure:

        data/JT/Hindi/
        |
        |-- data_excel/
        |   |-- Final_delivery_data_55hrs_18March2026.xlsx
        |   |-- Meta_Data_55hrs_18March2026.xlsx
        |
        |-- dataset_55hrs_18March2026/
            |
            |-- audio/
            |   |-- 310000.wav
            |   |-- 310001.wav
            |
            |-- transcripts/
                |-- 310000.txt
                |-- 310000.txt
    
- Download audio and transcript JSON files from the excel sheet shared by the data vendor (placed in above path).  
- The Excel file contains the follwoing fields:
    - rec_id
    - rec_url
    - transcript_url


## Stage 2: Convert to mono, sampling rate = 16KHz

## Stage 3: Validate ground truth transcripts and extract ground truth to .txt files
- Folders
```
|--fullAudio_gt
    |-- 189518.txt
        
|--segmented_gt
    |-- 189518.txt

Contents in 189518.txt
rec_id  seg_i       spk_id  speaker_role    start_time  end_time    ground truth trancript
189518	189518_0001	spk0	Asha Worker	    1.117	    2.677	    कह देली जा
189518	189518_0002	spk1	Patient	        3.131	    5.571	    ऐ दीदी का कहतानी
189518	189518_0003	spk0	Asha Worker	    5.670	    8.150	    देखा मने का तोहरा दिक्कत बा तोन बतावा
189518	189518_0004	spk1	Patient     	9.130	    12.210	    दिक्कत इ हे बा की गेछी हमार देहवावा
```

## To execute, run:
```
bash scripts/dataset_prep.sh
```
