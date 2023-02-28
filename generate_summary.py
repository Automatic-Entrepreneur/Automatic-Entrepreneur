from data_util import attribute_map, extract_data

try:
    from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
except:
    pass
import typing
from CompaniesHouse.CompanyInfo import CompanyInfo


def get_text(company_id: str) -> tuple[str, str]:
    company = CompanyInfo(company_id)
    text = company.getLongText(2021)

    return text[:2000], text


def generate_summary(text: str, debug=False) -> str:
    if debug:
        return "The directors present their annual report and financial statements for the year ended 31 December 2020. The principal activity of the company and group continued to be that of computer software development. Ordinary dividends were paid amounting to GBP 2,377,000. The directors do not recommend payment of a further dividend. Taylor Associates were appointed auditor to the group. A resolution proposing that they be re-appointed will be put at a General Meeting."
    # TODO: maybe test https://huggingface.co/philschmid/flan-t5-base-samsum
    summarizer = pipeline("summarization", model="philschmid/flan-t5-base-samsum")
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0][
        "summary_text"
    ]


def answer_question(
        text: str, questions: list[str], debug=False
) -> list[dict[str, str]]:
    if debug:
        return [{"q": "Who bought the company this year?", "a": "Withani Limited"}]
    model = pipeline(
        "question-answering",
        model="deepset/roberta-base-squad2",
        tokenizer="deepset/roberta-base-squad2",
    )
    q = {"question": questions, "context": [text] * len(questions)}

    ans = model(q)

    return [
        {"q": j, "a": i["answer"]} for j, i in zip(questions, ans) if i["score"] > 0.05
    ]


questions = [
    "Who bought {x} this year?",
    "How does {x} make money?",
    "Why did {x}'s total headcount change?",
    "How is {x} helping fight climate change?",
    "What environmental initiatives is {x} envolved with?",
    "What social initiatives is {x} envolved with?",
    "What are {x}'s main risks?",
    "What are {x}'s main strengths?",
    "Has {x} made any charitable donations (and how much)?",
    "How has {x} been affected by the COVID-19 pandemic?",
    "What is {x}'s largest expense?",
]


def get_questions(name):
    return [i.format(x=name) for i in questions]


if __name__ == "__main__":
    company_id = "03824658"

    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(CEO_text)
    QA_answers = answer_question(QA_text, get_questions("Softwire"))

    print(f"{QA_answers}\n\nCEO summary:\n\n{CEO_summary}")

    # output:
    """
    {"q": "Who bought the company this year?", "a": "Withani Limited"}

    CEO summary:

    The directors present their annual report and financial statements for the year ended 31
    December 2020. The principal activity of the company and group continued to be that of
    computer software development. Ordinary dividends were paid amounting to GBP 2,377,000. The
    directors do not recommend payment of a further dividend. Taylor Associates were appointed
    auditor to the group. A resolution proposing that they be re-appointed will be put at a
    General Meeting.
    """
