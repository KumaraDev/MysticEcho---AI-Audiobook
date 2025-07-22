import os
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

# Wasabi/S3 configuration
WASABI_ACCESS_KEY = os.environ.get("WASABI_ACCESS_KEY")
WASABI_SECRET_KEY = os.environ.get("WASABI_SECRET_KEY")
WASABI_BUCKET = os.environ.get("WASABI_BUCKET", "mystic-echo-audiobooks")
WASABI_REGION = os.environ.get("WASABI_REGION", "us-east-1")
WASABI_ENDPOINT = os.environ.get("WASABI_ENDPOINT", "https://s3.wasabisys.com")

# Initialize S3 client for Wasabi
s3_client = None
if WASABI_ACCESS_KEY and WASABI_SECRET_KEY:
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=WASABI_ENDPOINT,
            aws_access_key_id=WASABI_ACCESS_KEY,
            aws_secret_access_key=WASABI_SECRET_KEY,
            region_name=WASABI_REGION
        )
        logging.info("Wasabi S3 client initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Wasabi S3 client: {e}")
else:
    logging.warning("Wasabi credentials not found in environment variables")

def save_project_backup(project):
    """
    Save project content to Wasabi cloud storage
    """
    if not s3_client:
        raise Exception("Cloud storage not configured")
    
    try:
        # Create file key with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_key = f"projects/{project.user_id}/{project.id}/backup_{timestamp}.txt"
        
        # Upload content to Wasabi
        s3_client.put_object(
            Bucket=WASABI_BUCKET,
            Key=file_key,
            Body=project.content.encode('utf-8'),
            ContentType='text/plain',
            Metadata={
                'project_id': str(project.id),
                'project_title': project.title,
                'user_id': str(project.user_id),
                'timestamp': timestamp
            }
        )
        
        # Update project storage path
        project.storage_path = file_key
        
        logging.info(f"Project {project.id} backed up to Wasabi: {file_key}")
        return file_key
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            # Try to create bucket if it doesn't exist
            try:
                s3_client.create_bucket(Bucket=WASABI_BUCKET)
                logging.info(f"Created bucket: {WASABI_BUCKET}")
                return save_project_backup(project)  # Retry
            except Exception as create_error:
                logging.error(f"Failed to create bucket: {create_error}")
                raise Exception(f"Storage bucket error: {create_error}")
        else:
            logging.error(f"Wasabi upload error: {e}")
            raise Exception(f"Failed to save to cloud storage: {e}")
    
    except Exception as e:
        logging.error(f"Backup error: {e}")
        raise Exception(f"Failed to backup project: {e}")

def load_project_backup(project, backup_key=None):
    """
    Load project content from Wasabi cloud storage
    """
    if not s3_client:
        raise Exception("Cloud storage not configured")
    
    try:
        key = backup_key or project.storage_path
        if not key:
            raise Exception("No backup key provided")
        
        response = s3_client.get_object(Bucket=WASABI_BUCKET, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        logging.info(f"Project {project.id} loaded from Wasabi: {key}")
        return content
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            raise Exception("Backup file not found")
        else:
            logging.error(f"Wasabi download error: {e}")
            raise Exception(f"Failed to load from cloud storage: {e}")
    
    except Exception as e:
        logging.error(f"Load backup error: {e}")
        raise Exception(f"Failed to load project backup: {e}")

def list_project_backups(project):
    """
    List all backups for a project
    """
    if not s3_client:
        return []
    
    try:
        prefix = f"projects/{project.user_id}/{project.id}/"
        
        response = s3_client.list_objects_v2(
            Bucket=WASABI_BUCKET,
            Prefix=prefix
        )
        
        backups = []
        if 'Contents' in response:
            for obj in response['Contents']:
                backups.append({
                    'key': obj['Key'],
                    'last_modified': obj['LastModified'],
                    'size': obj['Size']
                })
        
        return sorted(backups, key=lambda x: x['last_modified'], reverse=True)
        
    except Exception as e:
        logging.error(f"List backups error: {e}")
        return []

def delete_project_files(project):
    """
    Delete all project files from cloud storage
    """
    if not s3_client:
        logging.warning("Cloud storage not configured - cannot delete files")
        return
    
    try:
        prefix = f"projects/{project.user_id}/{project.id}/"
        
        # List all objects with the prefix
        response = s3_client.list_objects_v2(
            Bucket=WASABI_BUCKET,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            # Delete all objects
            delete_keys = [{'Key': obj['Key']} for obj in response['Contents']]
            
            s3_client.delete_objects(
                Bucket=WASABI_BUCKET,
                Delete={'Objects': delete_keys}
            )
            
            logging.info(f"Deleted {len(delete_keys)} files for project {project.id}")
        
    except Exception as e:
        logging.error(f"Delete project files error: {e}")

def upload_file(file_path, s3_key, content_type='application/octet-stream'):
    """
    Upload a file to Wasabi storage
    """
    if not s3_client:
        raise Exception("Cloud storage not configured")
    
    try:
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(
                file,
                WASABI_BUCKET,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
        
        logging.info(f"File uploaded to Wasabi: {s3_key}")
        return s3_key
        
    except Exception as e:
        logging.error(f"File upload error: {e}")
        raise Exception(f"Failed to upload file: {e}")

def generate_download_url(s3_key, expiration=3600):
    """
    Generate a presigned URL for downloading a file
    """
    if not s3_client:
        raise Exception("Cloud storage not configured")
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': WASABI_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration
        )
        
        return url
        
    except Exception as e:
        logging.error(f"Generate download URL error: {e}")
        raise Exception(f"Failed to generate download URL: {e}")
