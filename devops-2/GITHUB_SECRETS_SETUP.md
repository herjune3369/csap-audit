# GitHub Secrets 설정 가이드

## AWS 자격 증명 설정

### 1. GitHub 저장소에서 Secrets 설정

1. GitHub 저장소로 이동
2. Settings 탭 클릭
3. 왼쪽 메뉴에서 "Secrets and variables" → "Actions" 클릭
4. "New repository secret" 버튼 클릭

### 2. 필요한 Secrets 추가

#### AWS_ACCESS_KEY_ID
```
Name: AWS_ACCESS_KEY_ID
Value: [AWS 액세스 키 ID]
```

#### AWS_SECRET_ACCESS_KEY
```
Name: AWS_SECRET_ACCESS_KEY
Value: [AWS 시크릿 액세스 키]
```

### 3. AWS IAM 사용자 생성 (필요한 경우)

#### 1) AWS IAM 콘솔에서 새 사용자 생성
```bash
# AWS CLI로 IAM 사용자 생성
aws iam create-user --user-name github-actions-devops-2
```

#### 2) 필요한 정책 연결
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::terraform-state-junheo-20250611",
                "arn:aws:s3:::terraform-state-junheo-20250611/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:*"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-northeast-2:*:table/terraform-state-lock"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "rds:*",
                "elasticloadbalancing:*",
                "iam:*",
                "cloudwatch:*",
                "sns:*"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 3) 액세스 키 생성
```bash
aws iam create-access-key --user-name github-actions-devops-2
```

### 4. 선택적 Secrets

#### SLACK_WEBHOOK_URL (선택사항)
```
Name: SLACK_WEBHOOK_URL
Value: [Slack 웹훅 URL]
```

## 환경 설정

### GitHub Environments 설정

#### 1. Development 환경
1. Settings → Environments → "New environment"
2. Environment name: `development`
3. Protection rules 설정 (선택사항)

#### 2. Staging 환경
1. Settings → Environments → "New environment"
2. Environment name: `staging`
3. Protection rules 설정 (선택사항)

#### 3. Production 환경
1. Settings → Environments → "New environment"
2. Environment name: `production`
3. Protection rules 설정 (권장)

## 테스트 방법

### 1. Secrets 설정 확인
```bash
# 워크플로우에서 AWS 자격 증명 확인
aws sts get-caller-identity
```

### 2. S3 백엔드 접근 확인
```bash
# S3 버킷 접근 확인
aws s3 ls s3://terraform-state-junheo-20250611
```

### 3. DynamoDB 테이블 접근 확인
```bash
# DynamoDB 테이블 확인
aws dynamodb describe-table --table-name terraform-state-lock
```

## 문제 해결

### 일반적인 오류

#### 1. "NoCredentialProviders" 오류
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY가 올바르게 설정되었는지 확인
- GitHub Secrets에서 값이 올바르게 저장되었는지 확인

#### 2. "Access Denied" 오류
- IAM 사용자에게 필요한 권한이 부여되었는지 확인
- S3 버킷과 DynamoDB 테이블에 대한 접근 권한 확인

#### 3. "Bucket does not exist" 오류
- S3 버킷 이름이 올바른지 확인
- 버킷이 지정된 리전에 존재하는지 확인

## 보안 권장사항

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **정기적 키 로테이션**: 액세스 키를 정기적으로 교체
3. **환경별 분리**: 개발/스테이징/프로덕션 환경별로 다른 자격 증명 사용
4. **모니터링**: AWS CloudTrail을 통한 API 호출 모니터링 