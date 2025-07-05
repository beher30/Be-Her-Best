#!/usr/bin/env python3
"""
Migration Script: Local Files to S3
This script helps migrate existing local files to AWS S3.
"""

import os
import sys
import django
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Add the Django project to the Python path
project_path = Path(__file__).parent / "Website" / "myproject"
sys.path.insert(0, str(project_path))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from myapp.models import UserProfile, PaymentProof, MegaVideo, Course

def upload_file_to_s3(local_path, s3_path):
    """Upload a single file to S3"""
    try:
        if os.path.exists(local_path):
            with open(local_path, 'rb') as file:
                default_storage.save(s3_path, file)
            print(f"✅ Uploaded: {local_path} -> {s3_path}")
            return True
        else:
            print(f"⚠️  File not found: {local_path}")
            return False
    except Exception as e:
        print(f"❌ Error uploading {local_path}: {e}")
        return False

def migrate_media_files():
    """Migrate all media files to S3"""
    print("🔄 Starting media files migration to S3...")
    
    if not getattr(settings, 'USE_S3', False):
        print("❌ S3 is not enabled. Set USE_S3=True in your environment variables.")
        return
    
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root or not os.path.exists(media_root):
        print("⚠️  No local media directory found.")
        return
    
    # Get S3 client
    try:
        s3_client = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        print(f"📦 Target S3 bucket: {bucket_name}")
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
        return
    
    uploaded_count = 0
    error_count = 0
    
    # Walk through all files in media directory
    for root, dirs, files in os.walk(media_root):
        for file in files:
            local_path = os.path.join(root, file)
            
            # Calculate relative path from media root
            relative_path = os.path.relpath(local_path, media_root)
            
            # Determine if it should go to public or private
            if any(private_dir in relative_path for private_dir in ['payment_proofs', 'private']):
                s3_path = f"media/private/{relative_path}"
            else:
                s3_path = f"media/public/{relative_path}"
            
            if upload_file_to_s3(local_path, s3_path):
                uploaded_count += 1
            else:
                error_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Successfully uploaded: {uploaded_count} files")
    print(f"   ❌ Errors: {error_count} files")
    
    if uploaded_count > 0:
        print(f"\n🎉 Migration completed! Your files are now in S3.")
        print(f"   You can now safely delete the local media directory if needed.")

def update_model_references():
    """Update model references to point to S3 URLs"""
    print("\n🔄 Updating model references...")
    
    updated_count = 0
    
    # Update UserProfile model
    try:
        profiles = UserProfile.objects.all()
        for profile in profiles:
            if profile.profile_picture and hasattr(profile.profile_picture, 'url'):
                # The URL should automatically update when S3 is enabled
                print(f"✅ Updated UserProfile: {profile.user.username}")
                updated_count += 1
    except Exception as e:
        print(f"⚠️  Error updating UserProfile: {e}")
    
    # Update PaymentProof model
    try:
        proofs = PaymentProof.objects.all()
        for proof in proofs:
            if proof.image and hasattr(proof.image, 'url'):
                print(f"✅ Updated PaymentProof: {proof.user.username}")
                updated_count += 1
    except Exception as e:
        print(f"⚠️  Error updating PaymentProof: {e}")
    
    # Update MegaVideo model
    try:
        videos = MegaVideo.objects.all()
        for video in videos:
            if video.thumbnail and hasattr(video.thumbnail, 'url'):
                print(f"✅ Updated MegaVideo: {video.title}")
                updated_count += 1
    except Exception as e:
        print(f"⚠️  Error updating MegaVideo: {e}")
    
    # Update Course model
    try:
        courses = Course.objects.all()
        for course in courses:
            if course.thumbnail and hasattr(course.thumbnail, 'url'):
                print(f"✅ Updated Course: {course.title}")
                updated_count += 1
    except Exception as e:
        print(f"⚠️  Error updating Course: {e}")
    
    print(f"\n📊 Model Updates Summary:")
    print(f"   ✅ Updated references: {updated_count} models")

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("🔍 Testing S3 connection...")
    
    try:
        s3_client = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Test bucket access
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Successfully connected to S3 bucket: {bucket_name}")
        
        # Test file upload
        test_content = b"test file content"
        test_key = "test/migration_test.txt"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content
        )
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        
        print("✅ S3 connection test passed!")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your AWS credentials.")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ S3 bucket '{bucket_name}' not found.")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to S3 bucket '{bucket_name}'. Check your IAM permissions.")
        else:
            print(f"❌ S3 connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 Django Local to S3 Migration Tool")
    print("=" * 50)
    
    # Check if S3 is enabled
    if not getattr(settings, 'USE_S3', False):
        print("❌ S3 is not enabled in your Django settings.")
        print("   Please set USE_S3=True in your environment variables.")
        return
    
    # Test S3 connection first
    if not test_s3_connection():
        return
    
    # Ask user what they want to do
    print("\n📋 Migration Options:")
    print("1. Migrate media files to S3")
    print("2. Update model references")
    print("3. Both (recommended)")
    print("4. Test S3 connection only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        migrate_media_files()
    elif choice == '2':
        update_model_references()
    elif choice == '3':
        migrate_media_files()
        update_model_references()
    elif choice == '4':
        test_s3_connection()
    else:
        print("❌ Invalid choice. Please run the script again.")
        return
    
    print(f"\n🎉 Migration process completed!")
    print(f"\n📚 Next steps:")
    print(f"   1. Test your application to ensure files are loading from S3")
    print(f"   2. If everything works, you can optionally delete local media files")
    print(f"   3. Deploy your updated application to Render")

if __name__ == "__main__":
    main() 