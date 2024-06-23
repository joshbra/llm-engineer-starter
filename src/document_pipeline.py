import os
from pathlib import Path

from tqdm import tqdm
from src.pdf import DocumentAI
import pandas as pd
from pypdf import PdfReader, PdfWriter
from langchain_core.output_parsers import PydanticOutputParser
from src.models import MedicalRecord
from langchain_core.prompts import PromptTemplate


import vertexai.preview.generative_models as generative_models
from langchain_google_vertexai import ChatVertexAI

from src.prompt import SYSTEM_INSTRUCTIONS


def generate(input: str) -> MedicalRecord:
    # medical data contains terms that may be blocked, so block none
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    }

    # build our parser (into MedicalRecords), prompt and LLM
    parser = PydanticOutputParser(pydantic_object=MedicalRecord)
    prompt = PromptTemplate(template=f"{SYSTEM_INSTRUCTIONS}\n{{format_instructions}}\n{{query}}",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    llm = ChatVertexAI(model_name="gemini-1.5-flash-001", project=os.getenv("GCP_PROJECT_ID"), location="europe-west2", 
                       max_tokes=2048, temperature=0.1, safety_settings=safety_settings
                    )
    chain = prompt | llm | parser
    result = chain.invoke({"query": input})
    return result



def split_pdf(file_path: Path) -> list[Path]:
    """DocumentAI has an upload limit for sync OCR, so split our document into single pages"""

    reader = PdfReader(file_path)
    file_name = str(file_path).replace(".pdf", "")
    files = []

    for page_num, page in tqdm(enumerate(reader.pages, 1), "Splitting PDF"):
        writer = PdfWriter()
        writer.add_page(page)
        file = f"{file_name}_page_{page_num}.pdf"
        with open(file, "wb") as pdf:
            writer.write(pdf)
            files.append(Path(file))

    return files


def extract_text_from_pdf(file_path: Path) -> pd.DataFrame:
    documents = []
    document_ai = DocumentAI()
    records = []

    # split our PDF to avoid upload limits (not using batch)
    files = split_pdf(file_path=file_path)

    # OCR our PDF pages and add to our documents collection
    for file in tqdm(files, "Performing OCR on docs"):
        document = document_ai(file)
        documents.append(document.text)

    # generate our medical record with all our pages as context
    print("Generating MedicalRecord")
    records.append(generate("".join(documents)))
    
    # convert our documents into a DataFrame, sorted by date (year)
    df = pd.DataFrame()
    for record in records:
        df = pd.concat([df, pd.DataFrame.from_records(record.dict()["events"])])
    df = df.sort_values(by="date", key=lambda s: s.str[-4:])
    pd.set_option('display.max_colwidth', 60)

    return df
    

    