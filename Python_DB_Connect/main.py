import json
import http.server
import socketserver
from token import JWTManager
from db import DataBaseAgent
from urllib.parse import urlparse, parse_qs
from bin import Bin

jwt_agent = JWTManager("1234", "HS256")
dba = DataBaseAgent("oka", "oka_user", "3haziran", "nst-dev.neocortexbe.com", "42013")
message_bin = Bin(1, "messages", dba)

# Define the handler to manage GET requests
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Initialize data
        self.data = None

        # Initialize respond for the http code
        self.response = 200

        # Parse the URL and query string
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        # Get the data from the parameters
        # This indicates that the message sent is to everybody
        is_to_everybody = params.get("is_to_everybody")
        # The message id which we want to update or delete
        message_id = params.get("message_id")
        # The username of the user who is sending or reading what we received
        receiver = params.get("receiver")
        # The username of the user who is sending or reading
        source = params.get("source")
        # The data that isn't suitable for the other tags
        data = params.get("data")

        if parsed_url.path == "/read":
            # Get the ids of the source and the receiver who are tried to be inspected
            source_id = dba.execute_on_db(f"select id from users where user_name = '{source[0]}'")
            receiver_id = dba.execute_on_db(f"select id from users where user_name = '{receiver[0]}'")
            # Get the related content of the source and the receiver
            self.data = dba.execute_on_db(
                f"select * from messages where (receiver = {receiver_id[0].get("id")} or is_to_everybody = True or source = {source_id[0].get("id")}) and status = True order by id ASC")
            self.data = [self.data[i]["content"] for i in range(len(self.data))]

        elif parsed_url.path == "/write":
            # Get the ids of the source and the receiver
            source_id = dba.execute_on_db(f"select id from users where user_name = '{source[0]}'")
            receiver_id = dba.execute_on_db(f"select id from users where user_name = '{receiver[0]}'")
            # Add a new row to the messages database initialized with the values from the parameters
            self.data = dba.execute_on_db(
                f"insert into messages (content, receiver, is_to_everybody, source, status) values ('{data[0]}', '{receiver_id[0].get("id")}', '{is_to_everybody[0]}', '{source_id[0].get("id")}', True) returning content")

        elif parsed_url.path == "/update_message":
            # Update the messages content to the data parameter
            self.data = dba.execute_on_db(
                f"update messages set content = '{data[0]}' where id = {message_id[0]} returning id")
            self.data = self.data[0]["id"]

        elif parsed_url.path == "/delete_message":
            # Add the message to the bin
            self.data = dba.execute_on_db(f"update messages set status = False where id = {message_id[0]} returning id")
            if self.data:
                self.data = self.data[0]["id"]

                message_bin.add(self.data)

                # Empty the bin if necessary
                message_bin.update()

        self.send_data_in_json(self.data, self.response)

    def do_POST(self):
        # Initialize data
        self.data = None

        # Initialize respond for the http code
        self.response = 200

        # Parse the URL
        parsed_url = urlparse(self.path)

        # Get the raw data and parse it
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode('utf-8')
        json_data = json.loads(post_data)

        # Get the data from the params
        username = json_data.get("username")
        password = json_data.get("password")

        if parsed_url.path == "/sign_up":
            if dba.is_in_db("users", f"user_name = '{username}'"):
                self.data = "The same USERNAME already exists!"
                self.response = 409
            else:
                self.data = dba.execute_on_db(f"insert into users (user_name, password) values ('{username}', '{password}') returning id")
                self.data = self.data[0]["id"]

        elif parsed_url.path == "/login":
            if dba.is_in_db("users",
                             f"user_name = '{username}' and password = '{password}'"):
                self.data = True
            else:
                self.data = False
                self.response = 401

        self.send_data_in_json(self.data, self.response)

    def send_data_in_json(self, data, response):
        # Turn the data to json format
        data = {"data": data}

        # Respond to client
        self.send_response(response)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        data = json.dumps(data)

        self.wfile.write(bytes(data, "utf-8"))

# Set up the server
PORT = 8080
with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()