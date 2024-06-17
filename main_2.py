import fitz
import os
import json
import re


def extract_text_from_pdf(pdf_path):
    """Функция извлечения текста из исходного PDF."""
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    return text


def get_type_of_message(pdf_path, status, local_list):
    """Ссылаясь на status.json определяет статус письма."""
    extracted_text = extract_text_from_pdf(pdf_path)
    start_index = extracted_text.find("Вид документа:")
    if start_index != -1:
        text_after_phrase = extracted_text[start_index + len("Вид документа:"):]
        for key in status:
            if key in text_after_phrase:
                local_list.append(f'Тип письма: {status[key]}')
    return local_list


def get_polych(pdf_path, local_list):
    """Функция по поиску адресата письма."""
    extracted_text = extract_text_from_pdf(pdf_path)
    search_polych = extracted_text.find("Получатель:")
    if search_polych != -1:
        get_polychatel = extracted_text[search_polych + len("Получатель:"):]
        parts = get_polychatel.split()
        if any(word.startswith(' ООО') or word.startswith(' ИП') for word in parts):
            next_50_characters = get_polychatel[:50]
            local_list.append(f'Получатель: {next_50_characters}')
        else:
            if len(parts) >= 3:
                local_list.append(f'Получатель: {" ".join(parts[:3])}')
            else:
                local_list.append(f'Получатель: {" ".join(parts)}')
    return local_list


def get_date(pdf_path, local_list):
    """Функция по поиску даты."""
    extracted_text = extract_text_from_pdf(pdf_path)
    search_polych = extracted_text.find("Получатель:")
    if search_polych != -1:
        get_polychatel = extracted_text[search_polych + len("Получатель:"):]
        date_pattern = r'\b\d{2}\.\d{2}\.\d{4}\b'
        matches = re.findall(date_pattern, get_polychatel)
        if matches:
            local_list.append(f'Дата: {matches[0]}')
    return local_list


def get_message(pdf_path, local_list):
    """Функция по поиску статьи если есть постановление, если его нет, то ничего не выдает."""
    extracted_text = extract_text_from_pdf(pdf_path)
    #start_pattern = r"(?i)руководств[уяе].*?:"
    start_pattern = r"(?i)(руководствуясь|Руководствуясь|РУКОВОДСТВУЯСЬ|Руководствуясь|РУКОВОДСТВУЯСЬ|Руководствуясь|РУКОВОДСТВУЯСЬ|Руководствуясь|РУКОВОДСТВУЯСЬ)"
    end_pattern = "ПОСТАНОВИЛ:"
    start_match = re.search(start_pattern, extracted_text)
    end_match = extracted_text.find(end_pattern, start_match.end() if start_match else 0)
    if start_match and end_match != -1:
        start = start_match.end()
        message = extracted_text[start:end_match]
        message = message.replace('\n', '')  # потому что в ответе почему-то выдает "Текст\n"
        local_list.append(f'Руководствуясь: {message}')
    return local_list


def get_postanovlenie(pdf_path, local_list):
    """Функция по поиску постановления, если его нет, то ничего не выдает."""
    extracted_text = extract_text_from_pdf(pdf_path)
    phrase_to_find = "ПОСТАНОВИЛ:"
    start = extracted_text.find(phrase_to_find)
    if start != -1:
        start = start + len(phrase_to_find)
        end = extracted_text.find(".", start)
        if end != -1:
            text_after_postanovil = extracted_text[start:end].strip()
            if text_after_postanovil not in ['', '1']:
                local_list.append(f' Постановил: {text_after_postanovil}')
            start = end + 1
            end = extracted_text.find(".", start)
            if end != -1:
                local_list.append(f'Постановил: {extracted_text[start:end].strip()}')
    return local_list


if __name__ == "__main__":
    file_path_pdf = r'C:\Dev\text recognising\pdf\piev_24201140359731.pdf'  # путь до файла
    with open('status.json', 'r', encoding='utf-8') as json_file:
        status = json.load(json_file)
    local_list = []
    local_list = get_type_of_message(file_path_pdf, status, local_list)
    local_list = get_polych(file_path_pdf, local_list)
    local_list = get_date(file_path_pdf, local_list)
    local_list = get_message(file_path_pdf, local_list)
    local_list = get_postanovlenie(file_path_pdf, local_list)
    print(local_list)


"""Если нужно сделать сортировку по всем PDF в папке."""
# if __name__ == "__main__":
#     global_list = []
#     file_path_pdf = r'C:\Dev\text recognising\pdf'  # Пропиши свой путь
#     with open('status.json', 'r', encoding='utf-8') as json_file:
#         status = json.load(json_file)
#     for file_name in os.listdir(file_path_pdf):
#         if file_name.endswith('.pdf'):
#             local_list = []
#             sample_pdf_path = os.path.join(file_path_pdf, file_name)
#             local_list = get_type_of_message(sample_pdf_path, status, local_list)
#             local_list = get_polych(sample_pdf_path, local_list)
#             local_list = get_date(sample_pdf_path, local_list)
#             local_list = get_message(sample_pdf_path, local_list)
#             local_list = get_postanovlenie(sample_pdf_path, local_list)
#             global_list.append(local_list)
#             # print(local_list) # отладка
#      print(global_list)