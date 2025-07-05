# AWS S3 Setup Guide for Django Project

This guide will help you set up AWS S3 for your Django project to handle file uploads in the cloud.

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **Python Dependencies**: The required packages are already in your `requirements.txt`:
   - `django-storages>=1.13.2`
   - `boto3>=1.26.0`

## Step 1: Set Up AWS Credentials

### Option A: Using AWS CLI (Recommended)
```bash
pip install awscli
aws configure
```

### Option B: Environment Variables
Set these environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_DEFAULT_REGION=us-east-1
```

## Step 2: Create S3 Bucket

### Option A: Using the Setup Script (Easiest)
```bash
cd "Website 1.4nh"
python setup_aws_s3.py
```

### Option B: Manual Setup
1. Go to AWS S3 Console
2. Create a new bucket with a unique name
3. Choose your preferred region
4. Configure bucket settings:
   - Block all public access: **Uncheck** (for public media files)
   - Bucket versioning: Optional
   - Encryption: Default (SSE-S3)

## Step 3: Configure Environment Variables

Add these environment variables to your deployment platform (Render):

```
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Step 4: Test the Setup

1. **Local Testing**:
   ```bash
   cd "Website 1.4nh/Website/myproject"
   python manage.py collectstatic
   python manage.py runserver
   ```

2. **Upload a file** through your Django admin or forms to test S3 integration

## Step 5: Deploy to Render

1. **Add Environment Variables** in your Render dashboard:
   - Go to your service settings
   - Add the environment variables listed in Step 3

2. **Deploy** your application

3. **Run collectstatic** after deployment:
   ```bash
   python manage.py collectstatic --noinput
   ```

## File Storage Structure

Your S3 bucket will be organized as follows:

```
your-bucket-name/
├── static/           # Static files (CSS, JS, images)
├── media/
│   ├── public/       # Public media files (profile pictures, etc.)
│   └── private/      # Private media files (payment proofs, etc.)
```

## Security Considerations

1. **IAM User**: Create a dedicated IAM user with minimal S3 permissions
2. **Bucket Policy**: Only allow public read access to `media/public/*`
3. **CORS**: Configure CORS if needed for cross-origin requests
4. **Encryption**: Enable server-side encryption for sensitive files

## Troubleshooting

### Common Issues:

1. **"No credentials found"**
   - Ensure AWS credentials are properly configured
   - Check environment variables are set correctly

2. **"Access Denied"**
   - Verify IAM user has proper S3 permissions
   - Check bucket policy allows the required operations

3. **"Bucket not found"**
   - Verify bucket name is correct
   - Ensure bucket exists in the specified region

4. **"Static files not loading"**
   - Run `python manage.py collectstatic`
   - Check `STATICFILES_STORAGE` setting

### Debug Commands:

```bash
# Test S3 connection
python -c "import boto3; s3 = boto3.client('s3'); print(s3.list_buckets())"

# Check environment variables
python -c "import os; print('USE_S3:', os.environ.get('USE_S3')); print('BUCKET:', os.environ.get('AWS_STORAGE_BUCKET_NAME'))"
```

## Cost Optimization

1. **Lifecycle Rules**: Set up lifecycle rules to move old files to cheaper storage
2. **CDN**: Use CloudFront for better performance and lower costs
3. **Monitoring**: Set up billing alerts to monitor usage

## Migration from Local Storage

If you have existing files in local storage:

1. **Backup** your current media files
2. **Upload** files to S3 using the setup script or manually
3. **Update** database records if needed
4. **Test** thoroughly before switching to S3

## Support

For additional help:
- AWS S3 Documentation: https://docs.aws.amazon.com/s3/
- Django Storages Documentation: https://django-storages.readthedocs.io/
- Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html 