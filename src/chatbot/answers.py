"""Answer management module for the data quality chatbot."""


class AnswerManager:
    """Manages user answers for the chatbot questions."""

    def __init__(self):
        self.answers = {}

    def add_answer(self, question, answer):
        """Stores the answer for a given question."""
        self.answers[question] = answer

    def get_answers(self):
        """Returns all the stored answers."""
        return self.answers
