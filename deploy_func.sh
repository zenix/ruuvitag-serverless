#!/bin/sh
source env.sh
gcloud functions deploy ingest_http \
  --runtime python38 \
  --trigger-http \
  --allow-unauthenticated \
  --service-account $SA_NAME@$PROJECT_NAME.iam.gserviceaccount.com \
  --memory 512MB \
  --region=$REGION \
  --set-env-vars BUCKET_NAME=$BUCKET_NAME,TOKEN=$TOKEN