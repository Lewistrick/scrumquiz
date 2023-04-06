from hashlib import sha256


class Question:
    def __init__(self, question: str, answers: list[str], correct_ids: list[int]):
        self.question = question
        self.answers = answers
        self.correct_ids = correct_ids

    def __hash__(self):
        hashable_text = self.question + "/".join(self.answers) + str(self.correct_ids)
        return int(sha256(hashable_text.encode()).hexdigest(), 16)

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
