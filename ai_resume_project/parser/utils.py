from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
import pymupdf
import boto3
import json

def read_uploaded_file(file_object: UploadedFile, file_extension: str)-> str:
    with pymupdf.open(stream=file_object.read(), filetype=file_extension) as document:
        text = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
            
    return text

ai_credentials_options = {
    "region_name": settings.GEN_AI_REGION,
    "aws_access_key_id": settings.GEN_AI_ACCESS_KEY,
    "aws_secret_access_key": settings.GEN_AI_SECRET_KEY
}

prompt_data = """
You are an bot designed to act as a professional for parsing resumes. You are given a resume and your job is extract the following information from the resume:

1. applicant_name: ""
2. highest_level_of_education: ""
3. area_of_study: ""
4. institution: ""
5. introduction: ""
6. skills: string {}
7. english_proficiency_level: ""
8. experiences: [{"employer_name":"", role:"", duration: ""}]

Give the extracted info in JSON format only
Note: if the is not present, leave the field blank
Give 
""" 
def extract_resume_info(text: str):
    try:
        bedrock = boto3.client("bedrock-runtime", **ai_credentials_options)
        payload = {
            "prompt": "[INST]" + prompt_data + "Resume Content::" + text + "[INST]",
            "max_gen_len": 1024,
            "temperature": 0.5,
            "top_p": 0.9
        }
        body = json.dumps(payload)
        model_id = "meta.llama2-70b-chat-v1"
        
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())
        response_text: str = response_body["generation"]
        print("response", response_text)
    except Exception as e:
        raise ValidationError(f"Something went wrong: {e}, 500")