import jwt

class JWTManager:
    def __init__(self, key, algorithm):
        self.key = key
        self.algorithm = algorithm

    def encode(self, payload):
        return jwt.encode(payload, self.key, self.algorithm)

    def decode(self, token):
        return jwt.decode(token, self.key, self.algorithm)