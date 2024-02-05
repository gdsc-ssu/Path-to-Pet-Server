from fastapi import HTTPException
from google.cloud import storage
from google.oauth2 import service_account
import uuid
import os
from dotenv import load_dotenv
import shutil
from copy import deepcopy

load_dotenv()

UPLOADS_DIR = '/home/everythinginssu/Path-to-Pet-Server/data'
# UPLOADS_DIR = '/Users/ggona/Documents/GitHub/Google Solution Challenge 2023/Path-to-Pet-Server/data'

# GCS 버킷 이름과 GCP 프로젝트 ID를 설정
# Credentials 객체 생성
credentials = service_account.Credentials.from_service_account_file(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
GCS_BUCKET_NAME = 'path_to_pet_bucket'
GCP_PROJECT_ID = 'hardy-thinker-412419'

# GCS에 연결하는 클라이언트 생성
storage_client = storage.Client(credentials=credentials, project=GCP_PROJECT_ID)

def upload_file(file, breed, is_dog, is_searching=False):
    # GCS에 업로드할 파일 이름 설정
    key = uuid.uuid1()

    file_name = f"{key}-{file.filename}"
    if is_dog and not is_searching:
        destination_blob_name = f"dog/{breed.value}/{file_name}"
    elif not is_dog and not is_searching:
        destination_blob_name = f"cat/{breed.value}/{file_name}"
    else:
        destination_blob_name = f"searching/{breed.value}/{file_name}"

    tmp_file = deepcopy(file)
    # GCS 버킷 객체 가져오기
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    # GCS에 파일 업로드
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file.file)

    # 업로드된 파일의 로컬 경로 설정
    file_path = os.path.join(UPLOADS_DIR, destination_blob_name)

    path_elements = file_path.split('/')
    directory_path = '/'.join(path_elements[:-1])
    os.makedirs(directory_path, exist_ok=True)

    # 업로드된 파일을 로컬 디렉토리에 저장
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(tmp_file.file, file_object)

    # 업로드한 파일의 GCS URL 반환
    gcs_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{destination_blob_name}"
    return gcs_url

def delete_file(url):
    destination_blob_name = url.split(f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/")[1]
    # GCS 버킷 객체 가져오기
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    # GCS에서 파일 삭제
    blob = bucket.blob(destination_blob_name)
    try:
        blob.delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file from GCS: {str(e)}")

    file_path = os.path.join(UPLOADS_DIR, destination_blob_name)
    os.remove(file_path)
