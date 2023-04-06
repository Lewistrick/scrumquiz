import random
import string
from abc import ABC, abstractmethod

from loguru import logger

from question import Question


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

    def __init__(self):
        logger.info(
            " ".join(
                (
                    "Using shuffle prompter.",
                    "Answers for each question will be shuffled.",
                    "Each answer will be a random letter.",
                    "You can give answers in both lower- and uppercase;"
                    "only letters will be recorded.",
                )
            )
        )

    def ask(self, question: Question):
        answer_letters = random.sample(string.ascii_uppercase, len(question.answers))
        answer_letters = self.print_question(question, answer_letters)

        corr_letters = {answer_letters[i] for i in question.correct_ids}
        guessed_letters = self.record_input()

        if guessed_letters == corr_letters:
            logger.success("That's correct!")
            return True

        corr_str = "answers were" if len(corr_letters) > 1 else "answer was"
        logger.error(f"Wrong! The correct {corr_str}: " + "".join(corr_letters))
        return False

    def print_question(self, question: Question, answer_letters: list[str]):
        logger.warning(question.question)
        answer_order = list(range(len(question.answers)))
        random.shuffle(answer_order)
        for idx in answer_order:
            letter = answer_letters[idx]
            logger.info(f"({letter}) {question.answers[idx]}")

    def record_input(self):
        while True:
            guess = input("Give all letters with correct answers, e.g. 'ABC' >>> ")
            guessed_letters = {ch for ch in guess.upper() if ch.isalpha()}
            if guessed_letters:
                break
            logger.warning("No input recorded. Try again.")
        return guessed_letters
