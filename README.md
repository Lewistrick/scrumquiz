# Scrum Quiz

## Get started
- Install Python 3.6 or higher
- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment
    - On Windows: `.venv\Scripts\activate`
    - On Linux: `source .venv\bin\activate`
- Install dependencies: `python -m pip install -r requirements.txt`
- Run the script: `python scrumquiz.py`

## Acknowledgements
- Many thanks to Ditectrev for compiling a [list of questions](https://github.com/Ditectrev/Professional-Scrum-Developer-I-PSD-I-Practice-Tests-Exams-Questions-Answers)!

## Notes
- A results.csv file is created that contains the results for each question.
- Questions with correct answers are skipped.
- If all questions are answered correctly, the file is removed.

## Extra options
- For a complete overview of all options, use the `-h` command line argument.
- If you want to redownload the questions, use `--update`.
    - When the questions file doesn't exist, it will automatically be downloaded.
- By default, questions are in random order. If you don't want that, use the `--ordered` option.
- Use the `-n <n_questions>` argument to set the number of questions asked.
