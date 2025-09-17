class GroqClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GroqClient, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Initialize the Groq client here
        self.api_key = None  # Set your API key
        self.base_url = "https://api.groq.com"  # Example base URL

    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_data(self, endpoint):
        # Implement the logic to get data from the Groq API
        pass

    def post_data(self, endpoint, data):
        # Implement the logic to post data to the Groq API
        pass

    # Add more methods as needed for Groq client functionalities