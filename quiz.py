from pathlib import Path

from loguru import logger

from prompter import Prompter
from question import Question


class Quiz:
    resfile = Path("results.csv")

    def __init__(self, questions: list[Question], prompter: Prompter):
        self.questions = questions
        self.prompter = prompter
        self.results = self.read_results()

    @property
    def nq(self) -> int:
        return len(self.questions)

    def has_correct_answer(self, question: Question) -> bool:
        return self.results.get(hash(question), False)

    def read_results(self) -> dict[int, bool]:
        """Read results from a file. Returns result (bool) for each question hash.

        File contains question hash and result (0/1) for each answered question, e.g.:
        369720:1
        499656:0
        535056:1

        This method returns a dictionary with question hash as key and result (bool),
        e.g.: {369720: True, 499656: False, 535056: True}
        """
        if not self.resfile.is_file():
            return {}

        lines = [line.split(":") for line in self.resfile.read_text().splitlines()]
        results: dict[int, bool] = {}
        for line in lines:
            if len(line) != 2 or not all(x.isdigit() for x in line):
                logger.warning(f"Invalid line in results file: {line}")
                continue
            results[int(line[0])] = bool(int(line[1]))

        # If all answers were correct, empty results.
        if all(results.get(hash(q), False) for q in self.questions):
            logger.success("All answers were correct. Emptying previous results.")
            self.resfile.unlink()

        return results

    def take(self) -> float:
        """Take the quiz and return the percentage of correct answers."""
        score = 0
        for qi, question in enumerate(self.questions, 1):
            # Skip if this question was already answered correctly.
            if self.has_correct_answer(question):
                continue
            result = self.prompter.ask(question)
            self.record_result(question, result)
            score += result
            logger.info(f"Progress: {qi}/{self.nq} ({100*qi/self.nq:.2f}%)")
            logger.info(f"Current score: {score}/{qi} ({100*score/qi:.2f}%)")

        logger.info(f"Done! You answered {score} questions correctly.")

        return score / self.nq

    def record_result(self, question: Question, result: bool):
        # Set or overwrite the result in the dictionary
        self.results[hash(question)] = result

        # Write the result to a file
        with self.resfile.open("a") as handle:
            handle.write(f"{hash(question)}:{int(result)}\n")
