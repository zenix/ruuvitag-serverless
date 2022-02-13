# Ruuvitag GCP Serverless
This solution is for Ruuvitag has two purposes:
* Provide low-cost solution for storing and viewing Ruuritag data. (Mostly free tier)
* Provide example how to leverage GCP Serverless offering to make low-cost services.

This solution uses following Google Cloud Services (make sure your region supports these!):
* Cloud Functions 
* Cloud Firestore in Datastore Mode
* Cloud Storage

This solution expects that Ruuvi Station mobile software is used broadcast data to this solution.
Make sure to activate backgroun scanning from the applicaion: Ruuvi Station -> menu -> App Settings -> Background Scanning

You can use some old mobilephone to send data at home. Just leavit to charger 24/7.

## Installation

1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. Install [gsutil](https://cloud.google.com/storage/docs/gsutil_install)
3. Create Google Cloud Project from [GCP Console](https://console.cloud.google.com/)
4. Copy [env.sh.template](env.sh.template)  as [env.sh](env.sh) and edit correct values
```
export REGION=europe-west3 # edit your GCP region 
export BUCKET_NAME=images123 # edit some unique bucket name
export PROJECT_NAME=ruuvi-hobby #  edit your project name
export SA_NAME=sa-ruuvi # This is Service Account that function is using to interact with Cloud Storage and Datastore
export TOKEN=12345 # This is from Ruuvi Station -> menu -> App Setting -> Data Forwarding Settings -> Device Identifier
```
5. Run script to setup environment [./setup_gcp_environment.sh](setup_gcp_environment.sh)
6. Run script to deploy the solution [./deploy_func.sh](deploy_func.sh)
7. Deployment will output function URL.
8. Add URL of the solution to Ruuvi Station (Ruuvi Station -> menu -> App Settins -> Data Forwarding Settings )

How to access the solution after Ruuvi Station has inserted some values?
```
    https://<regions><project-nam>.cloudfunctions.net/ingest_http?days=2&token=token123&metric=temperature
```
URL Parameters
* token = This is your device identifier from the Ruuvi Station
* days = This will determine start day for the chart. It's counted from current date 
* metric = One of: temperature, humidity, batteryLevel, pressure


## Notes
1. Images will be deleted from the bucket every day.
2. You can't access images without authentication (logged in to GCP Console is enough)
3. Why my Chart Page is ugly? Because I did not style it.
4. It's lacking some None / empty checks. Sure, I trust that you can insert proper URL parameters.
