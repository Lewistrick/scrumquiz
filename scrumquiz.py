import argparse
import random
from pathlib import Path

import requests
from loguru import logger

from prompter import ShufflePrompter
from question import Question
from quiz import Quiz

# Location of repo with questions
repo = "Professional-Scrum-Developer-I-PSD-I-Practice-Tests-Exams-Questions-Answers"
quiz_link = f"https://raw.githubusercontent.com/Ditectrev/{repo}/master/README.md"

# Location of questions file (locally)
d = Path(__file__).parent
f = d / "quiz.md"

# Exact line containing the first question
first_q_line = "### When can Product Backlog Refinement occur?"


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update questions (use github to download file)",
    )
    parser.add_argument(
        "--ordered",
        action="store_true",
        help="Ask the questions fixed order (default: shuffle)",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=10,
        help="Number of questions to ask (default: 10)",
    )
    args = parser.parse_args()
    return args


def downlad_questions(quiz_link: str, targetfile: Path):
    logger.debug("Downloading questions...")
    resp = requests.get(quiz_link)
    resp.raise_for_status()
    with targetfile.open("wb") as handle:
        handle.write(resp.content)


def parse_questions(
    questions_file: Path,
    first_q_line: str,
    shuffle: bool,
    n: int | None,
) -> list[Question]:
    questions: list[Question] = []

    with questions_file.open(encoding="utf-8") as lines:
        # read until the first question
        for line in lines:
            if line.strip() == first_q_line:
                break

        # parse the questions
        curr_q_lines = [line.strip()]
        for line in lines:
            if line.startswith("### "):
                questions.append(Question.from_lines(curr_q_lines))
                curr_q_lines = [line]
            else:
                curr_q_lines.append(line)
        questions.append(Question.from_lines(curr_q_lines))
        logger.debug(f"Read {len(questions)} questions")

    if shuffle:
        random.shuffle(questions)

    if n:
        questions = questions[:n]

    return questions


if __name__ == "__main__":
    args = read_arguments()

    if args.update or not f.exists():
        downlad_questions(quiz_link, f)

    questions = parse_questions(f, first_q_line, shuffle=not args.ordered, n=args.n)

    quiz = Quiz(questions=questions, prompter=ShufflePrompter())
    score = quiz.take()

    logger.info(f"Done! Your final score is {score} / {len(quiz.questions)})")
