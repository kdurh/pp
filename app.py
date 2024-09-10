import requests

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, Response)

app = Flask(__name__)


@app.route('/')
def proxy():
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    target_host = request.headers.get('X-Forwarded-Host')
    
    if not target_host:
        return Response("Missing Forward-Host header", status=400)
    
    # Build the full URL
    full_url = f"{scheme}://{target_host}"

    # Prepare headers: Exclude 'Host' header
    headers = {key: value for key, value in request.headers if key not in ['X-Forwarded-Proto','X-Forwarded-Host']}
    # return Response("full_url : " + full_url, status=200);

    # Forward the request to the target URL
    try:
        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=request.get_data(),
            allow_redirects=False
        )
    except requests.RequestException as e:
        return Response(f"Error: {e}", status=500)

    # Return the response from the target URL
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )
@app.route('/index')
def index():
   print('Request for index page received')
   return render_template('index.html')


# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

# @app.route('/hello', methods=['POST'])
# def hello():
#    name = request.form.get('name')

#    if name:
#        print('Request for hello page received with name=%s' % name)
#        return render_template('hello.html', name = name)
#    else:
#        print('Request for hello page received with no name or blank name -- redirecting')
#        return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
