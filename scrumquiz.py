import argparse
import random
import string
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from loguru import logger

# Location of repo with questions
repo = "Professional-Scrum-Developer-I-PSD-I-Practice-Tests-Exams-Questions-Answers"
quiz_link = f"https://raw.githubusercontent.com/Ditectrev/{repo}/master/README.md"

# Location of questions file (locally)
d = Path(__file__).parent
f = d / "quiz.md"

# Exact line containing the first question
first_q_line = "### When can Product Backlog Refinement occur?"


class Question:
    def __init__(self, question: str, answers: list[str], correct_ids: list[int]):
        self.question = question
        self.answers = answers
        self.correct_ids = correct_ids

    @classmethod
    def from_lines(cls, lines: list[str]):
        """Creates a question from a list of text lines."""
        if not lines[0].startswith("### "):
            raise ValueError("Invalid question line: " + lines[0])
        question = lines[0].removeprefix("###").strip()
        answers = []
        curr_idx = 0
        correct_ids = []
        for line_raw in lines[1:]:
            line = line_raw.strip()
            if line.startswith("- [ ] "):
                answers.append(line.removeprefix("- [ ] "))
            elif line.startswith("- [x] "):
                answers.append(line.removeprefix("- [x] "))
                correct_ids.append(curr_idx)
            else:
                continue
            curr_idx += 1
        if not answers or not correct_ids:
            raise ValueError("No answers or correct_ids")
        question = cls(question, answers, correct_ids)
        return question


class Prompter(ABC):
    """A base class that can be used to prompt a question and gather user response."""

    @abstractmethod
    def ask(self, question: Question) -> bool:
        """Ask (show) a question and record the user's answer.

        Return whether the user responded correctly.
        """
        ...


class ShufflePrompter(Prompter):
    """A Prompter that randomly shuffles the answers for a question."""

    def ask(self, question: Question):
        logger.warning(question.question)
        answer_order = list(range(len(question.answers)))
        random.shuffle(answer_order)
        answer_letters = random.sample(string.ascii_uppercase, len(question.answers))
        corr_letters = set()
        for idx in answer_order:
            letter = answer_letters[idx]
            logger.info(f"({letter}) {question.answers[idx]}")
            if idx in question.correct_ids:
                corr_letters.add(letter)

        guess = set(input("Give all letters with correct answers, e.g. 'ABC' >>> "))
        if guess == corr_letters:
            logger.success("That's correct!")
            return True

        corr_str = "answers were" if len(corr_letters) > 1 else "answer was"
        logger.error(f"Wrong! The correct {corr_str}: " + "".join(corr_letters))
        return False


class Quiz:
    def __init__(self, questions: list[Question], prompter: Prompter):
        self.questions = questions
        random.shuffle(self.questions)
        self.prompter = prompter

    @property
    def nq(self) -> int:
        return len(self.questions)

    def take(self) -> int:
        score = 0
        for qi, question in enumerate(self.questions, 1):
            result = self.prompter.ask(question)
            score += result
            logger.info(f"Progress: {qi}/{self.nq} ({100*qi/self.nq:.2f}%)")
            logger.info(f"Current score: {score}/{qi} ({100*score/qi:.2f}%)")

        return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update questions (use github to download file)",
    )
    args = parser.parse_args()

    if args.update or not f.exists():
        if args.update:
            logger.info("Updating questions...")
        else:
            logger.info("Downloading questions for the first time...")
        resp = requests.get(quiz_link)
        resp.raise_for_status()
        with f.open("wb") as handle:
            handle.write(resp.content)

    questions: list[Question] = []

    with f.open(encoding="utf-8") as lines:
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

    quiz = Quiz(questions=questions, prompter=ShufflePrompter())
    quiz.take()
