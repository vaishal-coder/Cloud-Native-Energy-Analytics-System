#!/bin/bash
# Script to create Lambda layer with dependencies

echo "Creating Lambda Layer with Dependencies"
echo "========================================"

# Create directory structure
mkdir -p lambda-layer/python

# Install dependencies
pip install -r ../lambda/requirements.txt -t lambda-layer/python/

# Create zip file
cd lambda-layer
zip -r ../lambda-layer.zip .
cd ..

echo ""
echo "Lambda layer created: lambda-layer.zip"
echo ""
echo "Upload to AWS:"
echo "  aws lambda publish-layer-version \\"
echo "    --layer-name energy-analytics-dependencies \\"
echo "    --zip-file fileb://lambda-layer.zip \\"
echo "    --compatible-runtimes python3.9 python3.10 python3.11"
echo ""
echo "Then attach to Lambda function in AWS Console or update deploy.py"
