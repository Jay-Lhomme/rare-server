from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from views import create_comment, get_all_comments, get_single_comment, delete_comment, update_comment
from views.user import create_user, login_user, get_all_users, get_single_user, get_all_users_management, update_user
from views.post import get_all_posts, get_single_post, create_post, update_post, delete_post


class HandleRequests(BaseHTTPRequestHandler):
    """Handles the requests to this server"""

    def parse_url(self):
        """Parse the url into the resource and id"""
        path_params = self.path.split('/')
        resource = path_params[1]
        if '?' in resource:
            param = resource.split('?')[1]
            resource = resource.split('?')[0]
            pair = param.split('=')
            key = pair[0]
            value = pair[1]
            return (resource, key, value)
        else:
            id = None
            try:
                id = int(path_params[2])
            except (IndexError, ValueError):
                pass
            return (resource, id)

    def _set_headers(self, status):
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        """Sets the OPTIONS headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def do_GET(self):
        self._set_headers(200)
        response = {}
        
        parsed = self.parse_url()
        
        if '?' not in self.path:
            ( resource, id ) = parsed
            if resource == "users":
                if id is not None:
                    response = f"{get_single_user(id)}"
                else:
                    response = f"{get_all_users()}"
            elif resource == "users_management":
                response = f"{get_all_users_management()}"
        self.wfile.write(json.dumps(response).encode())        
        """Handle Get requests to the server"""

        self._set_headers(200)
        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url()

        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            (resource, id) = parsed

            if resource == "comments":
                if id is not None:
                    response = get_single_comment(id)
                else:
                    response = get_all_comments()

            if resource == "posts":
                if id is not None:
                    response = get_single_post(id)

                else:
                    response = get_all_posts()

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = json.loads(self.rfile.read(content_len))
        response = ''
        resource, _ = self.parse_url()

        if resource == 'login':
            response = login_user(post_body)
        if resource == 'register':
            response = create_user(post_body)

        new_post = None

        if resource == "posts":
            new_post = create_post(post_body)

        self.wfile.write(json.dumps(new_post).encode())

        new_comment = None
        if resource == 'comments':
            new_comment = create_comment(post_body)

        self.wfile.write(json.dumps(new_comment).encode())

        # self.wfile.write(response.encode())
        return response

    def do_PUT(self):
        """Handles PUT requests to the server"""

        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        
        #Parse the URL
        (resource, id) = self.parse_url()
        #Update a single user
        if resource == "users":
            success = update_user(id, post_body)
            if success:
                self._set_headers(204)
            else:
                self._set_headers(404)
            self.wfile.write("".encode())    

        self._set_headers(204)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        (resource, id) = self.parse_url()

        success = False

        if resource == "comments":
            success = update_comment(id, post_body)
        self.wfile.write("".encode())
        if resource == "posts":

            success = update_post(id, post_body)
        self.wfile.write("".encode())

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

    def do_DELETE(self):
        """Handles DELETE requests to the server"""
        self._set_headers(204)

        (resource, id) = self.parse_url()

        if resource == "comments":
            delete_comment(id)

        if resource == "posts":
            delete_post(id)

        self.wfile.write("".encode())

def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()

if __name__ == "__main__":
    main()
