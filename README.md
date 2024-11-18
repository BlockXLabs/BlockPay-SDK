# Blockx Pay Callback Server Sample

Create A flask app to receive Blockx Pay payment request notification

---
## Requirements

- Python 3.8+ (Python 3.8 or newer is recommended)
- pip (Python package manager)
- virtualenv (optional, for virtual environment management)

### Setup Instructions
- #### Clone the Repository

      $ python3 -m venv venv
      $ source venv/bin/activate  # On Windows use `venv\Scripts\activate`

- #### Install Project Dependencies

  Install required Python packages from the requirements.txt file.

      $ pip install -r requirements.txt

- #### Set Up Environment Variables

  Create a .env file in the root directory to securely manage environment variables.

        touch .env

 Populate .env with necessary environment variables. Example:

        API_KEY=xxx
        CALLBACK_URL="project_url"
        BACKEND_SERVER="https://www.pay-main-fullnode.blockxnet.com"


- #### Running the Server

    To start the server:

        python3 app.py

- #### Running the Server in background

    To start the server:

         nohup python3 app.py &

## Open web browser
    http://127.0.0.1:3000/app