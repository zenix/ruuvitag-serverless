import io
import os
from datetime import datetime, timedelta
from google.cloud import datastore
import pandas as pd
from pytz import timezone
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib
import asyncio

bucket_name = os.environ.get('BUCKET_NAME')
token = os.environ.get('TOKEN')

def ingest_http(request):

    from flask import abort
    if request.method == 'POST' and request.headers['content-type'] == 'application/json':
        json_payload = request.get_json(silent=True)
        if json_payload["deviceId"] == token:
            datastore_client = datastore.Client()
            for tag in json_payload['tags']:
                key = datastore_client.key('sensordata')
                entity = filll_entity(datastore.Entity(key=key), json_payload, tag)
                datastore_client.put(entity)
            return "ok"
    elif request.method == 'GET' and request.args.get('token') == token:

        days = request.args.get('days')
        metric = request.args.get('metric')

        after_date, date_end = figure_out_date_interval(days)

        result = query_data(after_date, metric)

        image_data = asyncio.run(generate_images(result, days, metric))
        image_names = [image_name for (image_name, image_data) in image_data]
        asyncio.run(upload_images(image_data))

        return generate_response(after_date, date_end, image_names)

    return abort(403)


def figure_out_date_interval(days):
    date_end = datetime.now(timezone('Europe/Helsinki'))
    date_start = timedelta(days=1 if days is None or 0 else int(days))
    after_date = date_end - date_start
    return after_date, date_end


def generate_response(after_date, date_end, image_names):
    image_html = ''.join(['%s</br><img src="https://storage.cloud.google.com/%s/%s"/><br/>' %
                          (image_name,bucket_name ,image_name) for image_name in image_names])
    date_start_formatted = after_date.strftime('%H:%M %d %b %Y')
    date_end_formatted = date_end.strftime('%H:%M %d %b %Y')
    return '%s - %s <br/> %s' % (date_start_formatted, date_end_formatted, image_html)


def filll_entity(entity, json_payload, tag):
    entity['id'] = tag['id']
    entity['name'] = tag['name']
    entity['humidity'] = tag['humidity']
    entity['pressure'] = tag['pressure']
    entity['temperature'] = tag['temperature']
    entity['txPower'] = tag['txPower']
    entity['voltage'] = tag['voltage']
    entity['batteryLevel'] = json_payload['batteryLevel']
    entity['updateAt'] = tag['updateAt']
    entity['rssi'] = tag['rssi']
    return entity


async def generate_images(result, days, metric):
    df = pd.DataFrame(result)
    data_filtered = df[[metric, 'updateAt', 'name']]
    data_filtered.loc[:, 'updateAt'] = pd.to_datetime(data_filtered.loc[:, 'updateAt'], format='%Y-%m-%dT%H:%M:%S%z')
    matplotlib.use('Agg')
    grouped_by_name = data_filtered.groupby('name')
    plt.figure()
    image_data = [generate_image(group, metric, name, days) for name, group in grouped_by_name]
    del df, data_filtered, grouped_by_name
    return image_data


def generate_image(group, metric, name, days):
    data_filtered = group[[metric, 'updateAt']]
    plot = data_filtered.plot(x='updateAt', y=metric)
    plot.xaxis.set_major_formatter(DateFormatter("%a %H:%M"))
    image_buffer = io.BytesIO()
    plot.get_figure().savefig(image_buffer, format='JPEG')
    image_name = '%s_%s_%s.jpg' % (name, metric, days)
    return image_name, image_buffer


async def upload_images(image_data):
    import asyncio
    from functools import partial
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    loop = asyncio.get_running_loop()
    tasks = []
    for (image_name, image_buffer) in image_data:
        blob = bucket.blob(image_name)
        image_buffer.seek(0)
        tasks.append(loop.run_in_executor(None, partial(blob.upload_from_file, image_buffer)))

    await asyncio.gather(*tasks)


def query_data(after_date, metric):
    query = datastore.Client().query(kind='sensordata', order=['updateAt'], projection=('updateAt', 'name', metric))
    query.add_filter('updateAt', '>', after_date.isoformat())
    return list(query.fetch())