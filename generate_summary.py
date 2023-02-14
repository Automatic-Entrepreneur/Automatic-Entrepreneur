from data_util import attribute_map, extract_data
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import typing
from CompaniesHouse.CompanyInfo import CompanyInfo

def get_text(company_id: str) -> tuple[str, str]:

    company = CompanyInfo(company_id)
    text = company.getlongtext(2021)

    return text[:2000], text

    return (
        '''2021 was a year of strong growth for Softwire, both in terms of revenue and headcount. A partial management buyout took place in March, with Softwire becoming wholly owned by Withani Limited. Withani is 100% owned by the previous shareholders and the new management team. Demand for our products and services remains strong and our business strategy continues to focus on the following areas.
 - Provision of high-value consultancy services at an early stage in the project lifecycle to help our customers define their IT and software strategy and requirements.
 - A product design service to prototype, validate and refine customer requirements to allow them to be demonstrated to stakeholders at an early stage in the project lifecycle.
 - User interface and user experience design services
 - Provision of high quality bespoke software development services to a broad range of customers.
 - Apprenticeship training services for software developers provided under the government accredited apprenticeship training scheme.
 - Training and provision of software developers on a temp-to-hire basis
The company remains attractive to employees and we continue to have high staff retention and no trouble hiring high-calibre new recruits''',
        '''Softwire is a privately owned software development company based in London. We are specialists in the delivery of software consultancy and bespoke, custom-built software solutions along with offering expert software development training.
Softwire focuses on providing an exceptional level of service to a manageable number of customers. Our commitment to customer satisfaction is second to none - not least because repeat business is an important source of our revenue.
We aim to be a complete technology partner for our clients, from initial consultancy and design phases right through to deployment and ongoing support, and we have partnerships with trusted third parties for services such as web hosting which we believe are best outsourced to established specialists in those fields.
We have experience of a vast range of markets and technologies and are always seeking to broaden our horizons even further. A can-do attitude prevails and, when asked by our clients if we can help with their new requirements, the answer is usually yes.
We are happy to undertake work on a fixed-price, fixed-timescale basis - so our customers can be confident of what they're getting when, and at what price. We offer genuine value for money to our clients. We believe the quality of our staff, software and service to be first-rate in our industry.
Our track record in these key areas has earned us both an impressive reputation and a loyal customer base who respect and trust us.

2021 was a year of strong growth for Softwire, both in terms of revenue and headcount. A partial management buyout took place in March, with Softwire becoming wholly owned by Withani Limited. Withani is 100% owned by the previous shareholders and the new management team. Demand for our products and services remains strong and our business strategy continues to focus on the following areas.
 - Provision of high-value consultancy services at an early stage in the project lifecycle to help our customers define their IT and software strategy and requirements.
 - A product design service to prototype, validate and refine customer requirements to allow them to be demonstrated to stakeholders at an early stage in the project lifecycle.
 - User interface and user experience design services
 - Provision of high quality bespoke software development services to a broad range of customers.
 - Apprenticeship training services for software developers provided under the government accredited apprenticeship training scheme.
 - Training and provision of software developers on a temp-to-hire basis
The company remains attractive to employees and we continue to have high staff retention and no trouble hiring high-calibre new recruits

The group's main trading risk is, as every year, the ongoing identification of organisations who wish to consume our services. The group has a dedicated sales team whose main function is of course to address this risk.  A further risk is maintaining the ability to attract and retain talented staff capable of delivering our services effectively.
The quality of the environment in which we live is an important concern for the group and its employees and the group aims to minimise adverse impacts on the environment wherever this is practical. The group complies with all laws and regulations relating to the environment, in many cases exceeding their minimum requirements.
The group has offset all carbon emissions it was responsible for during 2021 (including allowances for upstream and downstream emissions) as part of its ongoing Net Zero strategy, focussing on high-quality carbon capture schemes to maximise impact. 
During the year the group made charitable donations in a total amount of around £79,000 which includes employees volunteering days for charitable purposes. The company also delivered a further £32,000 of pro bono work.
The group has experienced strong growth in 2021, and anticipates that this will continue in 2022.  The group has weathered the effects of the COVID-19 pandemic, and despite uncertainty in the economy arising from the war in Ukraine or otherwise, is on a financially sound footing, and well placed to take advantage of opportunities that arise.'''
    )

def generate_summary(text: str) -> str:
    summarizer = pipeline('summarization', model="philschmid/bart-large-cnn-samsum")
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

def answer_question(text: str, question: str) -> str:
    model = pipeline('question-answering',
                     model="deepset/roberta-base-squad2",
                     tokenizer="deepset/roberta-base-squad2")
    q = {
    'question': question,
    'context': text
    }

    ans = model(q)

    if ans["score"] > 0.5:
        return ans["answer"]
    return ans["answer"]
    return "Information not known"


if __name__ == "__main__":

    company_id = "03824658"

    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(CEO_text)
    QA_answer = answer_question(QA_text, "Who bought Softwire?")
    
    print(f"Who bought Softwire? {QA_answer}\n\nCEO summary:\n\n{CEO_summary}")

    # output:
    '''
    Who bought Softwire? Withani Limited

    CEO summary:

    The directors present their annual report and financial statements for the year ended 31
    December 2020. The principal activity of the company and group continued to be that of
    computer software development. Ordinary dividends were paid amounting to £2,377,000. The
    directors do not recommend payment of a further dividend. Taylor Associates were appointed
    auditor to the group. A resolution proposing that they be re-appointed will be put at a
    General Meeting.
    '''
