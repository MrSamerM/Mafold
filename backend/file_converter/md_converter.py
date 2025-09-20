import pypandoc
from docx2md import convert as convert_doc
from io import BytesIO #This library converts the in memory in bytes
from pptx2md import convert as convert_ppx, ConversionConfig
import tempfile
import pandas as pd
import os

class Txt:
    def __init__(self,file):
        self.file=file
    
    async def convert_to_md (self):
         raw_bytes = await self.file.read() #read file
         md_text = raw_bytes.decode("utf-8") #encode it
         converted = pypandoc.convert_text(md_text, to="md", format="markdown",extra_args=["--standalone"]) #convert to md
         return converted
    
class Docx:
    def __init__(self,file):
        self.file=file
    
    async def convert_to_md (self):
        raw_bytes = await self.file.read()
        buffer = BytesIO(raw_bytes) #this treats it like a file that you can read and write into
        return convert_doc(buffer)

class Ppx:
    def __init__(self,file):
        self.file=file
    
    async def convert_to_md (self):
        raw_bytes = await self.file.read()

        with tempfile.NamedTemporaryFile(suffix=".pptx") as tmp:
            tmp.write(raw_bytes)
            tmp.flush()
            config = ConversionConfig(disable_notes=True)
            markdown = convert_ppx(tmp.name, config)

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
    

def get_converter(input_file):
    filename = input_file.filename  # works for FastAPI UploadFile
    ext = filename.split(".")[-1].lower() #the last of the split

    if ext == "txt":
        return Txt(input_file)
    elif ext == "docx":
        return Docx(input_file)
    elif ext == "pptx":
        return Ppx(input_file)
    elif ext == "csv":
        return Csv(input_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")