import os
import json
from openai import OpenAI
from mendable import ChatApp
from dotenv import load_dotenv

load_dotenv()
mendable_chat = ChatApp()
client = OpenAI()


def list_files_in_folder(folder_path):
    """
    List all files in the given folder.

    :param folder_path: Path to the folder
    :return: List of file names
    """
    files = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            files.append(entry)
    return files


def get_references(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": 'Your task is to, given a text, look for the chapter "References" and for each reference mentioned, get the source, the date, the title and the link. If you can\'t find the information, just write "Unknown".\n\nPresent the result as a JSON with the following structure:\n\n[\n{"source": {source}, \n"date": {year},\n"title": {title of the mentioned document},\n"url": {link to the source}\n}\n]',
            },
            {"role": "user", "content": f"{text}"},
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    answer = response.choices[0].message.content

    # Check if `answer` if a JSON
    try:
        answer = json.loads(answer)
    except:
        print("The answer is not a JSON")

    return answer


def add_sources(references):
    for reference in references:
        url = reference["url"]
        print("URL: ", url)

        if url == "Unknown":
            continue

        try:
            mendable_chat.add("url", url)
            print("Added source to Mendable: ", url)
        except Exception as e:
            print("Error adding source to Mendable: ", e)
    return None


def get_citations(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": 'Your task is to, given a text, get the parts of the text mentioning specific sources. Those parts are the ones that have a citation (e.g., (ScienceDirect, 2023)).\n\nFor each part, identify the sentence and the citation source.\n\nPresent the result as a JSON with the following structure:\n\n[\n{"sentence": {sentence text without the source}, \n"source": {source in the style (source, date)}\n}\n]',
            },
            {"role": "user", "content": f"{text}"},
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    answer = response.choices[0].message.content

    # Check if `answer` if a JSON
    try:
        answer = json.loads(answer)
    except:
        print("The answer is not a JSON")

    return answer


def answer_question_mendable(citation):
    return mendable_chat.query(citation)


def verify_citations(citations):
    count_true = 0
    citations_to_verify = []

    for citation in citations:
        answer = answer_question_mendable(citation["sentence"])
        print(f"Citation: {citation['sentence']}\nAnswer: {answer}")

        # if answer == "True":
        if "True" in answer:
            count_true += 1
        else:
            citations_to_verify.append(citation["sentence"])

    return count_true, citations_to_verify


def find_missing_sources(references):
    missing_sources = []

    for reference in references:
        if reference["url"] == "Unknown":
            missing_sources.append(reference)

    return missing_sources


def generate_report(count_true, citations_to_verify, missing_sources):
    citations_to_verify_str = (
        "\n".join(f"* {citation}" for citation in citations_to_verify)
        if citations_to_verify
        else "* All citations are correct."
    )

    score = round(count_true / len(citations) * 100, 2)

    report = f"""
# Accuracy Report

Score: {score}

Number of facts verified:

{len(citations)}

Facts that need to be verified:

{citations_to_verify_str}

Mentioned sources that are missing:

{missing_sources}

---

Powered by mendable.ai
"""
    return report


def write_report(report, filename, path="./scores"):
    full_path = os.path.join(path, filename)

    os.makedirs(path, exist_ok=True)

    with open(full_path, "w") as file:
        file.write(report)


# Main code
reports = list_files_in_folder("./reports")

for report in reports:
    base_name = os.path.splitext(report)[0]
    filename = base_name + "_score.md"

    report_path = os.path.join("./reports", report)
    with open(report_path, "r") as file:
        text = file.read()

    print("Extracting references from GPT Researcher report....")
    references = get_references(text)
    print("References extracted from GPT Researcher report!")

    print("Adding sources to Mendable....")
    add_sources(references)
    print("Sources added to Mendable!")

    print("Verifying citations....")
    citations = get_citations(text)
    count_true, citations_to_verify = verify_citations(citations)
    missing_sources = find_missing_sources(references)
    print("Citations verified!")

    print("Generating report....")
    report = generate_report(count_true, citations_to_verify, missing_sources)
    print("Report generated!")

    print("Writing report....")
    write_report(report, filename)
    print("Report written!")
