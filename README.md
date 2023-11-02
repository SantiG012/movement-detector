## Create virtualenv
```
python3 -m venv venv
```

## Activate virtualenv
```
source venv/bin/activate
```

## Create requirements.txt
```
pip freeze > requirements.txt
```

## Install dependencies
```
pip install -r requirements.txt
```

## Run
```
python3 recognizeBodyExpressionInRealTime.py
```

## Docker run  pulsar
```
docker run -it -e PULSAR_PREFIX_xxx=yyy \
    -p 6650:6650  -p 8080:8080 \
    --mount source=pulsardata,target=/pulsar/data \
    --mount source=pulsarconf,target=/pulsar/conf apachepulsar/pulsar:2.11.0 \
    sh -c "bin/apply-config-from-env.py conf/standalone.conf && bin/pulsar standalone"
```

