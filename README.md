# Video Labeling & Reviewing Tool
## How To Guide

### 1. Initialize conda environment  
```bash
conda create --name labeling
conda activate labeling
conda install pip
```

### 2. pip install requirements
```bash
pip install -r requirements.txt
```

### 3. execute main.py
```bash
python main.py --xlsx_from Annotations.xlsx
```

xlsx file should be in this format;
| Video ID | Start | End | Duration | Category   | Audio | Sentence_1              | Sentence_2      | Sentence_3        |
|----------|-------|-----|----------|------------|-------|-------------------------|-----------------|-------------------|
| {ID}     | 3     | 6   | 3        | (category) | etc   | ...      | ...  | ...    |
| {ID}     | 6     | 11  | 5        | (category) | etc   | ... | ... | ... |
| ...     |

### 4. Download Videos From Youtube Based on Video_ID (only required on first run)
When prompted, press y  
(It does not download the videos that has limited access (e.g. Age restricted videos which require login))

### 5. Edit Captions
When video screen appears, you could edit sentences.
Then, your xlsx file will contain before-and-after details of sentences.
| Video ID | Start | End | Duration | Category   | Audio | Sentence_1              | Sentence_2      | Sentence_3        | Reviewed_Category | Reviewed_Audio | Reviewed_Sentence_1 | Reviewed_Sentence_2 | Reviewed_Sentence_3 | Status |
|----------|-------|-----|----------|------------|-------|-------------------------|-----------------|-------------------|-------------------|----------------|----------------------|---------------------|----------------------|--------|
| {ID}     | 3     | 6   | 3        | (category) | etc   | ...                     | ...             | ...               | ...               | ...            | ...                  | ...                 | ...                  | ...    |
| {ID}     | 6     | 11  | 5        | (category) | etc   | ...                     | ...             | ...               | ...               | ...            | ...                  | ...                 | ...                  | ...    |
| ...      | ...   | ... | ...      | ...        | ...   | ...                     | ...             | ...               | ...               | ...            | ...                  | ...                 | ...                  | ...    |

(The status column will show ‘Error’ when there are no videos available, such as when the videos have limited access (e.g., age-restricted videos that require a login).)
