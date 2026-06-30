import json
import boto3
import re

sns_client = boto3.client('sns')

# Verified target topic ARN
SNS_TOPIC_ARN = "arn:aws:sns:us-west-1:203637463537:ecr-deployment-noti"

def lambda_handler(event, context):
    print("--- RAW INCOMING EVENT ---")
    print(repr(event))
    
    # Initialize fallbacks
    repo_name = 'automated-docker-image-deployment'
    build_num = '7'
    image_tag = 'latest'
    status    = 'SUCCESS'
    
    # Force parse input if Jenkins passes it as a loose/multi-line string
    if isinstance(event, str):
        try:
            # Try a standard load first
            event = json.loads(event)
        except Exception:
            print("Standard JSON parsing failed. Executing fallback regex extraction...")
            # Fallback: Extract values directly using regex if the string formatting is broken
            r_repo = re.search(r'"repository"\s*:\s*"([^"]+)"', event)
            r_build = re.search(r'"build_number"\s*:\s*"([^"]+)"', event)
            r_tag = re.search(r'"tag"\s*:\s*"([^"]+)"', event)
            r_status = re.search(r'"status"\s*:\s*"([^"]+)"', event)
            
            event = {
                'repository': r_repo.group(1) if r_repo else repo_name,
                'build_number': r_build.group(1) if r_build else build_num,
                'tag': r_tag.group(1) if r_tag else image_tag,
                'status': r_status.group(1) if r_status else status
            }

    if isinstance(event, dict):
        repo_name = event.get('repository', repo_name)
        build_num = event.get('build_number', build_num)
        image_tag = event.get('tag', image_tag)
        status    = event.get('status', status)

    email_subject = f"🚀 CI/CD Alert: Push to ECR [Build #{build_num}]"
    email_body = f"""Hello Engineer,

Your automated Jenkins pipeline has successfully pushed a new production artifact to Amazon ECR.

--- DEPLOYMENT METADATA ---
📦 Repository:    {repo_name}
🔢 Build Number:  #{build_num}
🏷️ Active Tag:    {image_tag}
🚦 Pipeline State: {status}

Your container is securely stored in your private AWS registry and is ready for environment deployment.

Best regards,
AWS Lambda Orchestrator"""

    try:
        print(f"Publishing to Topic: {SNS_TOPIC_ARN}")
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=email_subject,
            Message=email_body
        )
        print(f"SNS Broadcast successful. MessageId: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': 'Deployment metadata logged and SNS alert sent successfully!'
        }
    except Exception as e:
        print(f"🛑 CRITICAL ERROR SENDING SNS ALERT: {str(e)}")
        raise e