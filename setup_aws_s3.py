#!/usr/bin/env python3
"""
AWS S3 Setup Script for Django Project
This script helps you set up AWS S3 for your Django project.
"""

import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

def create_s3_bucket(bucket_name, region='us-east-1'):
    """Create an S3 bucket with proper configuration"""
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists!")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                pass
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Create bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ Successfully created bucket '{bucket_name}' in region '{region}'")
        
        # Configure bucket for static website hosting (optional)
        try:
            s3_client.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            print(f"✅ Configured bucket '{bucket_name}' for static website hosting")
        except Exception as e:
            print(f"⚠️  Could not configure static website hosting: {e}")
        
        # Set bucket policy for public read access (for public media)
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'PublicReadGetObject',
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': 's3:GetObject',
                    'Resource': f'arn:aws:s3:::{bucket_name}/media/public/*'
                }
            ]
        }
        
        try:
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=str(bucket_policy).replace("'", '"')
            )
            print(f"✅ Set public read policy for media/public/* in bucket '{bucket_name}'")
        except Exception as e:
            print(f"⚠️  Could not set bucket policy: {e}")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your AWS credentials.")
        print("   You can do this by:")
        print("   1. Installing AWS CLI: pip install awscli")
        print("   2. Running: aws configure")
        print("   3. Or setting environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False

def create_iam_user_for_s3(bucket_name):
    """Create an IAM user with S3 access for the bucket"""
    try:
        iam_client = boto3.client('iam')
        
        # Create IAM user
        user_name = f"{bucket_name}-s3-user"
        try:
            iam_client.create_user(UserName=user_name)
            print(f"✅ Created IAM user: {user_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"✅ IAM user '{user_name}' already exists")
            else:
                raise e
        
        # Create access key
        response = iam_client.create_access_key(UserName=user_name)
        access_key = response['AccessKey']
        
        print(f"✅ Created access key for user '{user_name}'")
        print(f"   Access Key ID: {access_key['AccessKeyId']}")
        print(f"   Secret Access Key: {access_key['SecretAccessKey']}")
        
        # Create policy for S3 access
        policy_name = f"{bucket_name}-s3-policy"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
        
        try:
            iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=str(policy_document).replace("'", '"')
            )
            print(f"✅ Created IAM policy: {policy_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"✅ IAM policy '{policy_name}' already exists")
            else:
                raise e
        
        # Attach policy to user
        try:
            iam_client.attach_user_policy(
                UserName=user_name,
                PolicyArn=f"arn:aws:iam::{iam_client.get_user()['User']['Arn'].split(':')[4]}:policy/{policy_name}"
            )
            print(f"✅ Attached policy '{policy_name}' to user '{user_name}'")
        except Exception as e:
            print(f"⚠️  Could not attach policy: {e}")
        
        return access_key
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your AWS credentials.")
        return None
    except Exception as e:
        print(f"❌ Error creating IAM user: {e}")
        return None

def main():
    print("🚀 AWS S3 Setup for Django Project")
    print("=" * 50)
    
    # Get bucket name
    bucket_name = input("Enter your S3 bucket name (e.g., my-django-app-media): ").strip()
    if not bucket_name:
        print("❌ Bucket name is required!")
        return
    
    # Validate bucket name
    if not bucket_name.replace('-', '').replace('.', '').isalnum():
        print("❌ Bucket name must contain only letters, numbers, hyphens, and dots!")
        return
    
    # Get region
    region = input("Enter AWS region (default: us-east-1): ").strip() or 'us-east-1'
    
    print(f"\n📋 Configuration:")
    print(f"   Bucket Name: {bucket_name}")
    print(f"   Region: {region}")
    
    # Create bucket
    print(f"\n🔧 Creating S3 bucket...")
    if create_s3_bucket(bucket_name, region):
        print(f"\n✅ S3 bucket setup completed!")
        
        # Ask if user wants to create IAM user
        create_user = input("\nDo you want to create an IAM user for S3 access? (y/n): ").strip().lower()
        if create_user in ['y', 'yes']:
            print(f"\n🔧 Creating IAM user...")
            access_key = create_iam_user_for_s3(bucket_name)
            if access_key:
                print(f"\n📝 Environment Variables for your Django project:")
                print(f"   USE_S3=True")
                print(f"   AWS_ACCESS_KEY_ID={access_key['AccessKeyId']}")
                print(f"   AWS_SECRET_ACCESS_KEY={access_key['SecretAccessKey']}")
                print(f"   AWS_STORAGE_BUCKET_NAME={bucket_name}")
                print(f"   AWS_S3_REGION_NAME={region}")
        
        print(f"\n🎉 Setup completed! Your Django project is ready to use S3!")
        print(f"\n📚 Next steps:")
        print(f"   1. Add the environment variables to your Render deployment")
        print(f"   2. Run: python manage.py collectstatic")
        print(f"   3. Deploy your application")
        
    else:
        print(f"\n❌ Setup failed! Please check your AWS credentials and try again.")

if __name__ == "__main__":
    main() 