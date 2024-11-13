# How to run codes in `Preprocess` folder
1. Put `reference` folder (pdf files and json file) in `Preprocess` folder
   * After step 1., the structure will be like:
        ```
        Preprocess
        ├── reference (provided by the official)
        │   ├── faq
        │   │   └── pid_map_content.json
        │   ├── finance
        │   │   ├── 0.pdf
        │   │   ├── 1.pdf
        │   │   ├── ...
        │   │   └── 1034.pdf
        │   └── insurance 
        │       ├── 1.pdf
        │       ├── 2.pdf
        │       ├── ...
        │       └── 643.pdf
        ├── data_preprocess.py
        └── README.md
        ```
2. Run `python3 data_preprocess.py --source_path="./reference"`
   * After step 2., `faq`, `insurance` and `finance` folder will be in `Preprocess` folder.
   * The structure will be like:
        ```
        Preprocess
        ├── faq
        │   └── pid_map_content.json
        ├── finance
        │   ├── 0.txt
        │   ├── 1.txt
        │   ├── ...
        │   └── 1034.txt
        ├── insurance 
        │   ├── 1.txt
        │   ├── 2.txt
        │   ├── ...
        │   └── 643.txt
        ├── reference (provided by the official)
        │   ├── faq
        │   │   └── pid_map_content.json
        │   ├── finance
        │   │   ├── 0.pdf
        │   │   ├── 1.pdf
        │   │   ├── ...
        │   │   └── 1034.pdf
        │   └── insurance 
        │       ├── 1.pdf
        │       ├── 2.pdf
        │       ├── ...
        │       └── 643.pdf
        ├── data_preprocess.py
        └── README.md
        ```
3. Check txt files in `faq`, `insurance` and `finance` folder, remove unusual characters, sort the order of the characters if the order is not correct, and move these three folder to `Model/` folder.
4. After step3, remove blank space in txt files in `finance` folder, and move these files to `Model/` folder, and rename the folder name to `finance_noBlank`. 