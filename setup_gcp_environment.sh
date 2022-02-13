#!/bin/sh
source env.sh
gcloud config set project $PROJECT_NAME
gcloud services enable compute.googleapis.com cloudfunctions.googleapis.com cloudbuild.googleapis.com datastore.googleapis.com
gcloud config set compute/region $REGION
gcloud iam service-accounts create $SA_NAME
gcloud projects add-iam-policy-binding $PROJECT_NAME --member="serviceAccount:$SA_NAME@$PROJECT_NAME.iam.gserviceaccount.com" --role=roles/datastore.user
gcloud projects add-iam-policy-binding $PROJECT_NAME --member="serviceAccount:$SA_NAME@$PROJECT_NAME.iam.gserviceaccount.com" --role=roles/storage.objectCreator
gsutil mb -l $REGION gs://$BUCKET_NAME
gsutil lifecycle set bucket-lifecycle.json gs://$BUCKET_NAME
gcloud app create --region=$REGION
gcloud datastore databases create --region $REGION
gcloud datastore indexes create index.yaml