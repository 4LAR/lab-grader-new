from fastapi import UploadFile, File, Form, HTTPException
from odf.opendocument import load
from odf.text import P
from odf import text, draw
from xml.etree import ElementTree as ET

from typing import Annotated
import os

from globals import config
from globals import read_config

def read_odt(file_path):
    document = OpenDocumentText(file_path)
    paragraphs = []

    for element in document.getElementsByType(P):
        paragraphs.append(element.firstChild.data)

    return paragraphs

async def odt(
    course_id: Annotated[str, Form()],
    lab_id: Annotated[str, Form()],
    student_fio: Annotated[str, Form()],
    group_number: Annotated[str, Form()],
    file: UploadFile = File(...)
):
    """
    Проверка odt файла на корректность
    """
    if not file.filename.endswith('.odt'):
        raise HTTPException(status_code=400, detail="File type not supported. Please upload an ODT file")

    try:
        lab_config = read_config(f"courses/{course_id}.yaml")
    except FileNotFoundError:
            raise HTTPException(status_code=404, detail={"Ошибка": list_of_common_errors[0]})

    file_path = os.path.join(config.get("reports")["path"], file.filename)
    print(file_path)
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    doc = load(file_path)
    xml_content = doc.xml()
    # print(xml_content)

    # Парсим XML и извлекаем текст
    root = ET.fromstring(xml_content)
    text_elements = root.findall('.//text:p', namespaces={'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'})

    extracted_text = []
    for elem in text_elements:
        text = ''.join(elem.itertext())
        if len(text) > 0:
            extracted_text.append(text)

    print(extracted_text)

    title_page = []
    target = "Санкт-Петербург 2022"
    if target in extracted_text:
        index = extracted_text.index(target)
        title_page = extracted_text[:index - 1]
        extracted_text = extracted_text[index + 1:]
    else:
        raise HTTPException(status_code=400, detail="Failed to detect cover page")

    error_list = []



    # os.remove(file.filename)

    return {"title": title_page, "body": extracted_text}
