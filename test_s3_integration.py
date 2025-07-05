#!/usr/bin/env python3
"""
S3 Integration Test Script
This script tests the S3 integration for your Django project.
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
from django.core.files.base import ContentFile

def test_s3_settings():
    """Test S3 configuration settings"""
    print("🔍 Testing S3 Settings...")
    
    # Check if S3 is enabled
    use_s3 = getattr(settings, 'USE_S3', False)
    print(f"   USE_S3: {use_s3}")
    
    if not use_s3:
        print("   ⚠️  S3 is not enabled. Set USE_S3=True to enable S3 storage.")
        return False
    
    # Check AWS credentials
    aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key else '❌ Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_key else '❌ Not set'}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {bucket_name or '❌ Not set'}")
    
    if not all([aws_access_key, aws_secret_key, bucket_name]):
        print("   ❌ Missing required AWS configuration.")
        return False
    
    # Check storage backend
    default_storage_class = default_storage.__class__.__name__
    print(f"   Default Storage: {default_storage_class}")
    
    if 'S3Boto3Storage' not in default_storage_class:
        print("   ⚠️  Default storage is not S3. Check your settings.")
        return False
    
    print("   ✅ S3 settings look good!")
    return True

def test_s3_connection():
    """Test direct S3 connection"""
    print("\n🔍 Testing S3 Connection...")
    
    try:
        s3_client = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Test bucket access
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"   ✅ Successfully connected to bucket: {bucket_name}")
        
        # List a few objects to test permissions
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        object_count = len(response.get('Contents', []))
        print(f"   ✅ Found {object_count} objects in bucket")
        
        return True
        
    except NoCredentialsError:
        print("   ❌ AWS credentials not found.")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"   ❌ Bucket '{bucket_name}' not found.")
        elif error_code == 'AccessDenied':
            print(f"   ❌ Access denied to bucket '{bucket_name}'.")
        else:
            print(f"   ❌ S3 connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_file_upload():
    """Test file upload through Django storage"""
    print("\n🔍 Testing File Upload...")
    
    try:
        # Create a test file
        test_content = b"This is a test file for S3 integration."
        test_filename = "test_s3_integration.txt"
        
        # Upload using Django storage
        file_obj = ContentFile(test_content)
        saved_path = default_storage.save(f"test/{test_filename}", file_obj)
        
        print(f"   ✅ File uploaded successfully: {saved_path}")
        
        # Check if file exists
        if default_storage.exists(saved_path):
            print(f"   ✅ File exists in storage: {saved_path}")
            
            # Get file URL
            file_url = default_storage.url(saved_path)
            print(f"   ✅ File URL: {file_url}")
            
            # Read file content
            with default_storage.open(saved_path, 'rb') as f:
                content = f.read()
                if content == test_content:
                    print(f"   ✅ File content matches original")
                else:
                    print(f"   ⚠️  File content mismatch")
            
            # Clean up test file
            default_storage.delete(saved_path)
            print(f"   ✅ Test file cleaned up")
            
            return True
        else:
            print(f"   ❌ File not found after upload")
            return False
            
    except Exception as e:
        print(f"   ❌ File upload error: {e}")
        return False

def test_media_urls():
    """Test media URL generation"""
    print("\n🔍 Testing Media URLs...")
    
    try:
        # Test public media URL
        public_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/public/"
        print(f"   ✅ Public media URL: {public_url}")
        
        # Test private media URL
        private_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/private/"
        print(f"   ✅ Private media URL: {private_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ URL generation error: {e}")
        return False

def main():
    print("🚀 S3 Integration Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: S3 Settings
    if test_s3_settings():
        tests_passed += 1
    
    # Test 2: S3 Connection
    if test_s3_connection():
        tests_passed += 1
    
    # Test 3: File Upload
    if test_file_upload():
        tests_passed += 1
    
    # Test 4: Media URLs
    if test_media_urls():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   ✅ Passed: {tests_passed}/{total_tests} tests")
    
    if tests_passed == total_tests:
        print(f"\n🎉 All tests passed! Your S3 integration is working correctly.")
        print(f"\n📚 You can now:")
        print(f"   1. Upload files through your Django application")
        print(f"   2. Access files via S3 URLs")
        print(f"   3. Deploy to Render with confidence")
    else:
        print(f"\n⚠️  Some tests failed. Please check your S3 configuration.")
        print(f"\n📚 Troubleshooting:")
        print(f"   1. Verify AWS credentials are set correctly")
        print(f"   2. Check bucket name and region")
        print(f"   3. Ensure IAM user has proper S3 permissions")
        print(f"   4. Review the AWS_S3_SETUP.md guide")

if __name__ == "__main__":
    main() 