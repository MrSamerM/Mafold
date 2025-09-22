import pypandoc
import docx2md
from io import BytesIO #This library converts the in memory in bytes
from pptx2md import convert, ConversionConfig
import pdfplumber
import tempfile
import pandas as pd
import os

class Txt:
    def __init__(self,file):
        self.file=file
    
    async def convert_to_md (self):
         raw_bytes = await self.file.read() #read file
         md_text = raw_bytes.decode("utf-8") #encode it
         converted = pypandoc.convert_text(md_text, to="md", format="markdown",extra_args=["--standalone"])
         return converted
    
class Docx:
    def __init__(self,file):
        self.file = file
    
    async def convert_to_md(self):
        raw_bytes = await self.file.read()
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(raw_bytes)
            tmp.flush()
        try:
            md_text =docx2md.do_convert(tmp.name)
        finally:
            os.remove(tmp.name)
        return md_text

class Ppx:
    def __init__(self,file):
        self.file=file
    
    async def convert_to_md (self):
        raw_bytes = await self.file.read()

        with tempfile.NamedTemporaryFile(suffix=".pptx",delete=False) as tmp:
            tmp.write(raw_bytes)
            tmp.flush()
        
        tmp_md = tempfile.NamedTemporaryFile(suffix=".md", delete=False)
        tmp_md.close()

        tmp_img_dir = tempfile.TemporaryDirectory()
        try:
            config = ConversionConfig(
                pptx_path=tmp.name,
                output_path=tmp_md.name,
                image_dir=tmp_img_dir.name,
                disable_notes=True
                )
            markdown = convert(config)
            with open(tmp_md.name, "r", encoding="utf-8") as f:
                markdown = f.read()
        finally:
            os.remove(tmp.name)
            os.remove(tmp_md.name)
            tmp_img_dir.cleanup()
        return markdown

class Csv:
    def __init__(self, file):
        self.file = file

    async def convert_to_md(self):
        raw_bytes = await self.file.read()
        buffer = BytesIO(raw_bytes)
        df = pd.read_csv(buffer)
        md_text = df.to_markdown(tablefmt="grid")
        return md_text
    
class Xls:
    def __init__(self, file):
        self.file = file

    async def convert_to_md(self):
        raw_bytes = await self.file.read()
        buffer = BytesIO(raw_bytes)
        df = pd.read_excel(buffer)
        md_text = df.to_markdown(tablefmt="grid")
        return md_text
    
class Pdf:
    def __init__(self, file):
        self.file = file

    async def convert_to_md(self):
        raw_bytes = await self.file.read()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(raw_bytes)
            tmp.flush()
        try:
            md_text = ""
            with pdfplumber.open(tmp.name) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        md_text += f"\n--- Page {i} ---\n{page_text}\n"
        finally:
            os.remove(tmp.name)
        return md_text

def get_converter(input_file):
    filename = input_file.filename
    ext = filename.split(".")[-1].lower()

    if ext == "txt":
        return Txt(input_file)
    elif ext == "docx":
        return Docx(input_file)
    elif ext == "pptx":
        return Ppx(input_file)
    elif ext == "csv":
        return Csv(input_file)
    elif ext == "xls" or ext== 'xlsx':
        return Xls(input_file)
    elif ext == "pdf":
        return Pdf(input_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")