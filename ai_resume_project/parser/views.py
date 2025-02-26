from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from .validators import validate_file_size, validate_file_extension
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from .utils import read_uploaded_file
# Create your views here.
def home(request):
    return render (request, "index.html")

def upload_resume(request: HttpRequest):
    if request.method == "POST" and request.FILES.get("file"):
        file: Uploadedfile = request.FILES["file"]
        try:
            ext: str = validate_file_extension(file)
            validate_file_size(file)
            file_content = read_uploaded_file(file, ext)
            print("file content>>", file_content)
        except ValidationError as err:
            return JsonResponse({"error": err.message})
        return JsonResponse({"error": "Invalid Request"}, status=400)
                             