from flask import Flask
from flask_babel import Babel, gettext
from ArgumentsExtrator.ArgumentsExtractor import ArgumentsExtractor
from SolutionGenerator.SolutionGenerator import SolutionGenerator
from SolutionGenerator.SolutionMapping import SolutionMapping
import pandas as pd

# Initialize Flask App and Babel
app = Flask(__name__)

# Configure Babel for the default language (e.g., Chinese)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_Hans'

# Initialize Babel
babel = Babel(app)


class Solution:
    @staticmethod
    def get_solution_by_text(question_text, knowledgepoint_id, solution_template_dict):
        if knowledgepoint_id not in solution_template_dict:
            return gettext("No solution found for this knowledge point.")  # Use gettext for translation

        args_extractor = ArgumentsExtractor()
        args_dict = args_extractor.extract_args_final(question_text, knowledgepoint_id)

        solution_mapping = SolutionMapping()
        generator = solution_mapping.getKnowledgePoint(knowledgepoint_id)

        if generator is None:
            return gettext("No solution generator available for this knowledge point.")

        solution_template = solution_template_dict[knowledgepoint_id]
        solution = generator().get_solution(solution_template, args_dict)
        print("knowledgepoint_id: " + str(knowledgepoint_id))
        print(solution)
        return solution


def main():
    with app.app_context():  # Flask Babel needs an app context
        question_df = pd.read_csv("EachQuestion.csv")
        question_df = question_df.astype({"knowledge_point_id": int})
        question_df = question_df[question_df['knowledge_point_id'].isin(range(45,46))]
        template_df = pd.read_csv("SolutionTemplate_translated_Chinese.csv")

        # Create dictionary mapping knowledge_point_id to template text
        template_dict = dict(zip(template_df['knowledge_point_id'], template_df['template_text_zh-Hans']))

        # Generate solutions and apply Flask-Babel's gettext function to translate
        question_df['question_solution'] = question_df.apply(
            lambda row: Solution.get_solution_by_text(
                row['translated_question_text'], row['knowledge_point_id'], template_dict),
            axis=1
        )

        # Save the DataFrame with the solutions to a CSV file
        question_df.to_csv('Question_Translation_with_Solutions.csv', index=False)


if __name__ == "__main__":
    main()
