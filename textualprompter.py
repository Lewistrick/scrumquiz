from typing import Iterable, TypeVar

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header, Static

T = TypeVar("T")

from prompter import Prompter
from question import Question


class AnswerGrid(Static):
    CSS_PATH = "quiz.css"

    def __init__(self, answers, toggled, *args, **kwargs):
        self.answers: list[str] = answers
        self.toggled: set[int] = toggled
        super().__init__(*args, **kwargs)

    def on_button_pressed(self, event: Button.Pressed):
        if not event.button.has_class("answer"):
            return
        id = int(event.button.id.removeprefix("ans"))
        if id in self.toggled:
            self.toggled.remove(id)
            event.button.remove_class("toggled")
        else:
            self.toggled.add(id)
            event.button.add_class("toggled")

    def compose(self) -> ComposeResult:
        for i, answer in enumerate(self.answers, 1):
            classes = "answer"
            if i in self.toggled:
                classes += " toggled"
            yield Button(f"{i}. {answer}", classes=classes, id=f"ans{i}")


class QuizPanel(Container):
    def __init__(self, question, answers, toggled, *args, **kwargs):
        self.question = question
        self.answers = answers
        self.toggled = toggled
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static(self.question, classes="question")
        yield AnswerGrid(self.answers, self.toggled, classes="answergrid")
        yield Container(Button("Submit", classes="submit", id="submit"))


class ProgressPanel(Container):
    def __init__(self, *args, **kwargs):
        self.n_questions = 0
        self.n_answered = 0
        self.n_correct = 0
        super().__init__(*args, **kwargs)

    @property
    def progress_str(self) -> str:
        if self.n_questions == 0:
            return "To see your progress, answer at least one question."
        prog = self.n_answered / self.n_questions * 100
        return f"{self.n_answered}/{self.n_questions} ({prog:.2f}%)"

    @property
    def score_str(self) -> str:
        if self.n_answered == 0:
            return "To see your score, answer at least one question."
        perc = self.n_correct / self.n_answered * 100
        return f"{self.n_correct}/{self.n_answered} ({perc:.2f}%)"

    def compose(self) -> ComposeResult:
        yield Static(f"Progress:\n{self.progress_str}", classes="status")
        yield Static(f"Score:\n{self.score_str}", classes="status")


class TextualApp(App):
    """A Textual App to manage a question."""

    CSS_PATH = "quiz.css"
    BINDINGS = [
        (".", "toggle_dark", "Toggle dark mode"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self):
        self.question = "Instead of this line of text, a question should be shown."
        self.answers = [f"Answe{'r'*(i+1)}" for i in range(1, 8)]
        self.toggled = {2, 4}
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(Static("Scrum Quiz"))
        yield Footer()
        yield Horizontal(
            QuizPanel(self.question, self.answers, self.toggled),
            ProgressPanel(),
        )

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def to_rows(self, elements: Iterable[T], n_cols: int = 3) -> list[list[T]]:
        rows: list[list[T]] = []
        row: list[T] = []
        for element in elements:
            row.append(element)
            if len(row) == n_cols:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        return rows

    def show_question(self, question: Question):
        self.question = question.question
        self.answers = question.answers

    def toggle_answer(self, idx: int):
        ...


class TextualPrompter(Prompter):
    """A Prompter that uses textual to show a question.

    Assumes a maximum of 6 answers for a question.
    """

    def __init__(self):
        self.screen = TextualApp()
        self.screen.run()

    def ask(self, question: Question) -> bool:
        self.screen.show_question(question)


if __name__ == "__main__":
    # Experiment with TextualPrompter

    questions = [
        Question(
            question="What is the capital of France?",
            answers=["Paris", "London", "Athens", "Kobnhavn"],
            correct_ids=[0],
        ),
        Question(
            question="What is the capital of Germany?",
            answers=["Hamburg", "Berlin", "Amsterdam", "Kobnhavn"],
            correct_ids=[1],
        ),
    ]

    prompter = TextualPrompter()
    for question in questions:
        result = prompter.ask(question)
        print(result)
