def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html')]
    start_response(status, headers)

    get_params = environ.get('QUERY_STRING', 'no GET data')

    post_data = ''
    if environ['REQUEST_METHOD'] == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(length).decode('utf-8')
        if not post_data:
            post_data = 'no POST data'
    else:
        post_data = 'no POST data'

    html = f"""
    <html>
      <h1>WSGI Response</h1>
      <h2>GET Parameters:</h2>
      <p>{get_params}</p>
      <h2>POST Parameters:</h2>
      <p>{post_data}</p>
    </html>
    """

    return [html.encode('utf-8')]

# для тестирования одинаковые объемы данных с nginx
# from whitenoise import WhiteNoise

# def application(environ, start_response):
#     path = environ.get('PATH_INFO')
#     if path == '/static/sample.html':
#         start_response('200 OK', [('Content-Type', 'text/html')])
#         return [b"<html><body><h1>Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sed ligula nec dui cursus finibus nec eu mauris. Vivamus convallis metus ut est faucibus, a ornare augue condimentum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Ut a sem eget massa sodales maximus vitae pharetra urna. Donec sollicitudin neque id mauris semper bibendum. Mauris convallis est eget ante vestibulum egestas. Sed nec viverra purus. Suspendisse non magna placerat purus aliquam accumsan. Interdum et malesuada fames ac ante ipsum primis in faucibus. Suspendisse potenti. Donec sed augue vel sem gravida pellentesque. Cras a molestie est. Nullam vitae leo vel ipsum maximus ornare. Phasellus vel dignissim enim. Sed volutpat hendrerit convallis. Integer tincidunt tempus sollicitudin. Vestibulum congue enim nec odio aliquet, vitae hendrerit dolor vestibulum. Suspendisse blandit, nisl eget vestibulum facilisis, lectus metus faucibus purus, a accumsan urna metus eu ipsum. Aenean vitae mauris hendrerit, eleifend risus ornare, auctor odio. Vivamus a libero ligula. Duis vitae tincidunt erat. Aenean non magna efficitur, volutpat lectus congue, tincidunt mi. Praesent convallis vel felis ut mattis. Donec id nisi augue. Proin elementum orci vitae justo pharetra faucibus. Vivamus id metus in felis auctor interdum a ut libero. Proin imperdiet tortor sit amet viverra blandit.</h1></body></html>"]
#     else:
#         start_response('200 OK', [('Content-Type', 'text/html')])
#         return [b"<html><body><h1>Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sed ligula nec dui cursus finibus nec eu mauris. Vivamus convallis metus ut est faucibus, a ornare augue condimentum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Ut a sem eget massa sodales maximus vitae pharetra urna. Donec sollicitudin neque id mauris semper bibendum. Mauris convallis est eget ante vestibulum egestas. Sed nec viverra purus. Suspendisse non magna placerat purus aliquam accumsan. Interdum et malesuada fames ac ante ipsum primis in faucibus. Suspendisse potenti. Donec sed augue vel sem gravida pellentesque. Cras a molestie est. Nullam vitae leo vel ipsum maximus ornare. Phasellus vel dignissim enim. Sed volutpat hendrerit convallis. Integer tincidunt tempus sollicitudin. Vestibulum congue enim nec odio aliquet, vitae hendrerit dolor vestibulum. Suspendisse blandit, nisl eget vestibulum facilisis, lectus metus faucibus purus, a accumsan urna metus eu ipsum. Aenean vitae mauris hendrerit, eleifend risus ornare, auctor odio. Vivamus a libero ligula. Duis vitae tincidunt erat. Aenean non magna efficitur, volutpat lectus congue, tincidunt mi. Praesent convallis vel felis ut mattis. Donec id nisi augue. Proin elementum orci vitae justo pharetra faucibus. Vivamus id metus in felis auctor interdum a ut libero. Proin imperdiet tortor sit amet viverra blandit.</h1></body></html>"]

# application = WhiteNoise(application, root='/Users/sofia/Projects/ask_taukaeva/static')