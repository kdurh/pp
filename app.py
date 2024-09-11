import requests
import logging
import io
import gzip
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, Response)

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
logger = logging.getLogger(__name__)

@app.route('/')
def proxy():
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    target_host = request.headers.get('X-Forwarded-Host')
    
    if not target_host:
        return Response("Missing Forward-Host header", status=400)
    
    # Build the full URL
    full_url = f"{scheme}://{target_host}"

    excluded_headers = ['host', 'x-forwarded-proto', 'x-forwarded-host', 'x-forwarded-for',
                            'x-forwarded-tlsversion', 'x-original-url', 'x-waws-unencoded-url',
                            'x-client-ip', 'x-client-port', 'x-site-deployment-id', 'x-appservice-proto',
                            'x-arr-ssl', 'x-arr-log-id', 'client-ip', 'disguised-host', 
                            'was-default-hostname']
    # Prepare headers: Exclude 'Host' header
    headers = {key: value for key, value in request.headers if key.lower() not in excluded_headers}
    
    for key, value in request.headers:
        logger.debug(f'Request headers key : {key} | value : {value}')
    for key, value in headers.items():
        logger.debug(f'Headers key : {key} | value : {value}')
    # Forward the request to the target URL
    try:
        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=request.get_data(),
            allow_redirects=False,
            stream=True
        )
        # logger.debug(f'Response status code: {response.status_code}')
        # logger.debug(f'Response headers: {response.headers}')
        # logger.debug(f'Response body: {response.text[:1000]}')
        # logger.debug(f'response encoding : {response.encoding}')

        filtered_headers = {k: v for k, v in response.headers.items() 
                            if k.lower() not in ['content-encoding', 'transfer-encoding']}

        return Response(
            response=response.text,
            status=response.status_code,
            headers=dict(filtered_headers)
        )
    except requests.RequestException as e:
        return Response(f"Error: {e}", status=500)

if __name__ == '__main__':
   app.run()
