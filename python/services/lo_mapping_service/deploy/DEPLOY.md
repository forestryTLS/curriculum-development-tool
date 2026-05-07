# Note: this documentation was compiled by an AI Tool

# Lambda Deployment Guide

End-to-end PowerShell commands to deploy both Lambda functions for the lo_mapping_service.

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- Your IAM user can run `aws lambda create-function`
- The Lambda execution role exists and has Lambda + SageMaker as trusted services
- The `.env` file at `python/services/lo_mapping_service/.env` is filled in with all required values
- The `DYNAMODB_STATUS_INDEX` line in `.env` has no inline comment

## 1. Set up PowerShell variables

```powershell
# Load all .env values into the current PowerShell session
$ENV_FILE = "e:\Forestry\MAP\curriculum-development-tool\python\services\lo_mapping_service\.env"
Get-Content $ENV_FILE | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=([^#]*)') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}

# Hardcoded paths and the Lambda execution role ARN
$ROLE_ARN = "arn:aws:iam::368677659554:role/service-role/SageMaker-SmallTLEFDeveloper"
$DEPLOY   = "e:\Forestry\MAP\curriculum-development-tool\python\services\lo_mapping_service\deploy"
$HANDLERS = "e:\Forestry\MAP\curriculum-development-tool\python\services\lo_mapping_service\app\lambda_handlers"

# Pull values out of env into PowerShell variables for easy reference
$REGION         = $env:AWS_REGION
$ACCESS_KEY     = $env:ACCESS_KEY
$SECRET_KEY     = $env:SECRET_KEY
$TABLE_NAME     = $env:LO_MAPPING_DYNAMODB_REQUESTS_TABLE
$STATUS_INDEX   = $env:DYNAMODB_STATUS_INDEX
$HF_MODEL_ID    = $env:HF_MODEL_ID
$HF_IMAGE_URI   = $env:HF_IMAGE_URI
$OUTPUT_S3_URI  = $env:OUTPUT_S3_URI
$SAGEMAKER_ROLE = $env:IAM_ROLE_ARN
```

Verify the values loaded:

```powershell
Write-Host "REGION:         $REGION"
Write-Host "TABLE_NAME:     $TABLE_NAME"
Write-Host "HF_MODEL_ID:    $HF_MODEL_ID"
Write-Host "SAGEMAKER_ROLE: $SAGEMAKER_ROLE"
Write-Host "ROLE_ARN:       $ROLE_ARN"
```

If any are blank, that value is missing from `.env`.

## 2. Zip both Lambda handlers

```powershell
Compress-Archive -Path "$HANDLERS\lambda_handler_start_batch_tranform_job.py" `
  -DestinationPath "$DEPLOY\start-batch-transform-job.zip" -Force

Compress-Archive -Path "$HANDLERS\lambda_handler_process_batch_transform_inference_results.py" `
  -DestinationPath "$DEPLOY\process-batch-transform-results.zip" -Force
```

## 3. Deploy `start-batch-transform-job` Lambda

Build the env JSON in memory, write to a temp file (NOT the project), deploy, delete:

```powershell
$tmpFile = [System.IO.Path]::GetTempFileName()
$json = [PSCustomObject]@{
    Variables = [PSCustomObject]@{
        ACCESS_KEY                         = $ACCESS_KEY
        SECRET_KEY                         = $SECRET_KEY
        IAM_ROLE_ARN                       = $SAGEMAKER_ROLE
        HF_MODEL_ID                        = $HF_MODEL_ID
        HF_IMAGE_URI                       = $HF_IMAGE_URI
        HF_TASK                            = "text-generation"
        INSTANCE_TYPE                      = "ml.g5.2xlarge"
 t       INSTANCE_COUNT                     = "1"
        OUTPUT_S3_URI                      = $OUTPUT_S3_URI
        JOB_NAME_PREFIX                    = "hf-batch-transform"
        MODEL_NAME_PREFIX                  = "hf-batch-transform-model"
        LO_MAPPING_DYNAMODB_REQUESTS_TABLE = $TABLE_NAME
        DYNAMODB_STATUS_INDEX              = $STATUS_INDEX
    }
} | ConvertTo-Json -Depth 3 -Compress

[System.IO.File]::WriteAllText($tmpFile, $json, (New-Object System.Text.UTF8Encoding $false))

aws lambda create-function `
  --function-name start-batch-transform-job `
  --runtime python3.12 `
  --role $ROLE_ARN `
  --handler lambda_handler_start_batch_tranform_job.lambda_handler `
  --zip-file fileb://$DEPLOY\start-batch-transform-job.zip `
  --region $REGION `
  --timeout 300 `
  --environment file://$tmpFile

Remove-Item $tmpFile
```

## 4. Deploy `process-batch-transform-results` Lambda

```powershell
$tmpFile = [System.IO.Path]::GetTempFileName()
$json = [PSCustomObject]@{
    Variables = [PSCustomObject]@{
        ACCESS_KEY            = $ACCESS_KEY
        SECRET_KEY            = $SECRET_KEY
        DYNAMODB_TABLE        = $TABLE_NAME
        START_JOB_LAMBDA_NAME = "start-batch-transform-job"
        STATUS_INDEX          = $STATUS_INDEX
        JOB_NAME_PREFIX       = "hf-batch-transform"}
} | ConvertTo-Json -Depth 3 -Compress

[System.IO.File]::WriteAllText($tmpFile, $json, (New-Object System.Text.UTF8Encoding $false))

aws lambda create-function `
  --function-name process-batch-transform-results `
  --runtime python3.12 `
  --role $ROLE_ARN `
  --handler lambda_handler_process_batch_transform_inference_results.lambda_handler `
  --zip-file fileb://$DEPLOY\process-batch-transform-results.zip `
  --region $REGION `
  --timeout 300 `
  --environment file://$tmpFile

Remove-Item $tmpFile
```

## 5. Verify both Lambdas exist

```powershell
aws lambda get-function --function-name start-batch-transform-job --region $REGION
aws lambda get-function --function-name process-batch-transform-results --region $REGION
```

Both should return JSON with `Configuration` blocks. If you see them, the Lambdas are deployed.

## 6. Wire EventBridge to invoke `process-batch-transform-results`

The second Lambda is meant to be triggered by EventBridge when SageMaker batch transform jobs change state. Create the EventBridge rule:

```powershell
# Create the rule. PowerShell strips inner double quotes when passing string vars to
# native executables, so we write the pattern to a temp file and use file:// instead.
$tmpPattern = [System.IO.Path]::GetTempFileName()
$pattern = '{"source":["aws.sagemaker"],"detail-type":["SageMaker Transform Job State Change"]}'
[System.IO.File]::WriteAllText($tmpPattern, $pattern, (New-Object System.Text.UTF8Encoding $false))

aws events put-rule `
  --name sagemaker-transform-job-state-change `
  --event-pattern file://$tmpPattern `
  --region $REGION

Remove-Item $tmpPattern

# Get the Lambda ARN
$LAMBDA_ARN = (aws lambda get-function --function-name process-batch-transform-results --region $REGION --query 'Configuration.FunctionArn' --output text)

# Add the Lambda as a target
aws events put-targets `
  --rule sagemaker-transform-job-state-change `
  --targets "Id=1,Arn=$LAMBDA_ARN" `
  --region $REGION

# Allow EventBridge to invoke the Lambda
aws lambda add-permission `
  --function-name process-batch-transform-results `
  --statement-id eventbridge-invoke `
  --action lambda:InvokeFunction `
  --principal events.amazonaws.com `
  --source-arn "arn:aws:events:${REGION}:368677659554:rule/sagemaker-transform-job-state-change" `
  --region $REGION
```

## Re-deploys

If you need to update an existing Lambda's code or env vars, use `update-function-code` and `update-function-configuration` instead of `create-function`:

```powershell
# Update code
aws lambda update-function-code `
  --function-name start-batch-transform-job `
  --zip-file fileb://$DEPLOY\start-batch-transform-job.zip `
  --region $REGION

# Update env vars (rebuild $tmpFile first as in step 3)
aws lambda update-function-configuration `
  --function-name start-batch-transform-job `
  --environment file://$tmpFile `
  --region $REGION
```

## Troubleshooting

- **`The role defined for the function cannot be assumed by Lambda.`** The role's trust policy does not include `lambda.amazonaws.com`. Admin needs to add it.
- **`Expected: '=', received: ''` on `--environment`.** The temp JSON file has a UTF-8 BOM. Make sure you used `[System.IO.File]::WriteAllText` with `(New-Object System.Text.UTF8Encoding $false)`, not `Out-File`.
- **`Function not found`** when FastAPI tries to invoke the Lambda. The Lambda was not deployed, or the name in `routes.py` does not match the deployed function name (`start-batch-transform-job`).
- **`AccessDeniedException`** at runtime. The Lambda execution role is missing the runtime permission for whichever AWS service it failed on (DynamoDB, S3, SageMaker, etc.). Admin needs to add it.