from loguru import logger

from prompter import Prompter
from question import Question


class Quiz:
    def __init__(self, questions: list[Question], prompter: Prompter):
        self.questions = questions
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

        logger.info(f"Done! You answered {score} questions correctly.")
        return score / self.nq
