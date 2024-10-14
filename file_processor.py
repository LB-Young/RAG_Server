import PyPDF2
import docx
from llm_client import LLMClient
import re
from difflib import SequenceMatcher
import os

class FileProcessor:
    def __init__(self):
        self.file_contents = {}

    def process_file(self, file_path):
        filename = os.path.basename(file_path)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_extension == 'txt':
            content = self.process_txt(file_path)
        elif file_extension == 'pdf':
            content = self.process_pdf(file_path)
        elif file_extension == 'docx':
            content = self.process_docx(file_path)
        else:
            return []

        self.file_contents[filename] = content
        return self.split_into_chunks(content)

    def process_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def process_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return ''.join(page.extract_text() for page in reader.pages)

    def process_docx(self, file_path):
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

    def split_into_chunks(self, content):
        return [content[i:i+500] for i in range(0, len(content), 500)]

    def get_relevant_chunks(self, query):
        all_chunks = []
        for content in self.file_contents.values():
            all_chunks.extend(self.split_into_chunks(content))

        similarities = [SequenceMatcher(None, query.lower(), chunk.lower()).ratio() for chunk in all_chunks]
        sorted_chunks = [x for _, x in sorted(zip(similarities, all_chunks), key=lambda pair: pair[0], reverse=True)]
        
        return '\n'.join(sorted_chunks[:10])

    def needs_full_content(self, query):
        judge_retirval_mode_prompt_template = "我现在有一个参考内容的集合，用户提问：“{}”。请判断当前问题是否需要参考完整内容，如果需要，请返回“True”，否则返回“False”。一般情况下，用户提问为“总结类”问题的时候会需要完整的参考内容。"
        prompt = judge_retirval_mode_prompt_template.format(query)
        answer = LLMClient().ado_requests(prompt)

        print("judge_retirval_mode answer:", answer)
        total_content_length = sum(len(content) for content in self.file_contents.values())
        return "True" in answer and total_content_length <= 10000

    def get_context(self, query):
        if self.needs_full_content(query):
            return '\n'.join(self.file_contents.values())
        else:
            return self.get_relevant_chunks(query)

    def remove_file_content(self, filename):
        if filename in self.file_contents:
            del self.file_contents[filename]
