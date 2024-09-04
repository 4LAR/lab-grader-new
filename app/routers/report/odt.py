from fastapi import UploadFile, File, Form, HTTPException
from odf.opendocument import load
from odf.text import P
from odf import text, draw
from xml.etree import ElementTree as ET

from typing import Annotated
import os
import re

from globals import config
from globals import read_config
from globals import parse_student_info
from globals import fix_full_name
from globals import transform_name_format

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

    ############################################################################

    try:
        lab_config = read_config(f"courses/{course_id}.yaml", lab_id)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Error reading course file: File not found")
    print(lab_config)
    reports = [s.lower() for s in lab_config["report"]]
    print(reports)

    teacher_name = lab_config['staff'][1]['name']
    teacher_name = fix_full_name(teacher_name)
    teacher_name_with_space, teacher_name_without_space = transform_name_format(teacher_name)
    teacher_title = lab_config['staff'][0]['title']
    teacher_title_no_spaces = teacher_title.replace(" ", "")
    
    print(teacher_name)
    print(teacher_name)
    print(teacher_name_with_space)
    print(teacher_name_without_space)

    print(teacher_title)
    print(teacher_title_no_spaces)

    ############################################################################

    file_path = os.path.join(config.get("reports")["path"], file.filename)

    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    doc = load(file_path)
    xml_content = doc.xml()

    # Парсим XML и извлекаем текст
    root = ET.fromstring(xml_content)
    text_elements = root.findall('.//text:p', namespaces={'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'})

    extracted_text = []
    for elem in text_elements:
        text = ''.join(elem.itertext())
        if len(text) > 0:
            extracted_text.append(text)

    title_page = []
    # Регулярное выражение для поиска "Санкт-Петербург" и года
    target_pattern = re.compile(r"Санкт-Петербург\s+\d{4}", re.IGNORECASE)

    # Ищем титульный лист
    for i, text in enumerate(extracted_text):
        if target_pattern.search(text):
            title_page = extracted_text[:i]
            extracted_lower_text = [s.lower() for s in extracted_text[:i]]
            extracted_lower_text = [s.lower() for s in extracted_text[i + 1:]]
            break
    else:
        raise HTTPException(status_code=400, detail="Failed to detect cover page")
    error_list = []

    ############################################################################

    # проверяем титульник
    student_info = parse_student_info(" ".join(title_page))
    print(student_info)

    # проверяем основной отчёт (заголовки)
    for report in reports:
        find_flag = False
        for line in extracted_lower_text:
            if line.find(report) != -1:
                find_flag = True
                break
        if not find_flag:
            error_list.append(report)

    # os.remove(file.filename)

    # return {"checklist": reports, "errors": error_list, "title": title_page, "body": extracted_text}
    return {"checklist": reports, "errors": error_list}
