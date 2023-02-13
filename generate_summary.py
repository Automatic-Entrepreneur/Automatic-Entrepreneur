from data_util import attribute_map, extract_data
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import typing
from CompaniesHouse.CompanyInfo import CompanyInfo

def get_text(company_id: str) -> tuple[str, str]:

    company = CompanyInfo(company_id)
    text = company.getlongtext(2021)

    return text[:2000], text

def generate_summary(text: str, debug=False) -> str:

    if debug:
        return "The directors present their annual report and financial statements for the year ended 31 December 2020. The principal activity of the company and group continued to be that of computer software development. Ordinary dividends were paid amounting to £2,377,000. The directors do not recommend payment of a further dividend. Taylor Associates were appointed auditor to the group. A resolution proposing that they be re-appointed will be put at a General Meeting."

    summarizer = pipeline('summarization', model="philschmid/bart-large-cnn-samsum")
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

def answer_question(text: str, questions: str, debug=False) -> str:

    if debug:
        return [{"q": "Who bought the company this year?", "a": "Withani Limited"}]

    model = pipeline('question-answering',
                     model="deepset/roberta-base-squad2",
                     tokenizer="deepset/roberta-base-squad2")
    q = {
    'question': questions,
    'context': [text]*len(questions)
    }

    ans = model(q)

    return [{"q": j, "a": i["answer"]} for j,i in zip(questions, ans) if i["score"] > 0.5]

questions = ['Who bought the company this year?',
             'How do they make money?',
             'Why did the total headcount change?',
             'How is the company helping fight climate change?'],


if __name__ == "__main__":

    company_id = "03824658"

    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(CEO_text)
    QA_answers = answer_questions(QA_text, questions)
    
    print(f"{QA_answers}\n\nCEO summary:\n\n{CEO_summary}")

    # output:
    '''
    {"q": "Who bought the company this year?", "a": "Withani Limited"}

    CEO summary:

    The directors present their annual report and financial statements for the year ended 31
    December 2020. The principal activity of the company and group continued to be that of
    computer software development. Ordinary dividends were paid amounting to £2,377,000. The
    directors do not recommend payment of a further dividend. Taylor Associates were appointed
    auditor to the group. A resolution proposing that they be re-appointed will be put at a
    General Meeting.
    '''