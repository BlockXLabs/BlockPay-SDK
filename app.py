from flask import Flask, url_for, render_template_string
from flask import request
from flask import redirect
from flask import render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_restx import Api
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

from api.testnet import test_ns
from api.mainnet import main_ns

load_dotenv()
api_key = os.getenv('API_KEY')

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/'
CORS(app)
socketio = SocketIO(app)

backend_server = os.getenv('BACKEND_SERVER')
callback_endpoint = os.getenv('CALLBACK_URL')

user_rooms = {}

@app.context_processor
def inject_theme():
    return {'theme': request.cookies.get('theme', 'light')}

@app.route('/api/payment_notification', methods=("GET", "POST"))
def payment_notification():
    if request.method == 'GET':
        wallet = request.args.get('wallet')
        amount = request.args.get('amount')
        invoice_id = request.args.get('invoice_id')
        crypto = request.args.get('crypto')
        # if len(amount) > 0 and len(wallet) > 0:
        if amount is not None:
            if request.args.get('invoice_id') is not None:
                invoice_id = request.args.get('invoice_id')
                invoice_url = f"{backend_server}/api/v1/invoices/{invoice_id}"
                headers = {'X-BlockX-Api-Key': api_key}
                invoice_response = requests.get(invoice_url,headers=headers)
                if invoice_response.status_code == 200:
                    inv_data = invoice_response.json()
                    if len(inv_data["invoices"]) > 0:
                        status = inv_data["invoices"][0]["status"]
            return render_template("wallet/payment_notifier.j2",crypto=crypto, invoice_id=invoice_id, wallet=wallet, amount=amount, status=status)
        return render_template("wallet/payment_notifier.j2")
    req = request.get_json(force=True)
    addr = req["addr"]
    room = addr
    socketio.emit("notification", {'message': 'New event', "response_data": req}, room=room)
    print('Notification sent!')
    return "success", 202

@socketio.on('connect')
def handle_connect():
    invoice_id = request.args.get('invoice_id')
    wallet_id = request.args.get('wallet')
    if wallet_id:
        join_room(wallet_id)
        print("join_room connect", join_room)
        print(f"User wallet {wallet_id} connected with invoice ID {invoice_id}")
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    wallet_id = request.args.get('wallet')
    if wallet_id:
        leave_room(wallet_id)
        print(f"User wallet {wallet_id} disconnected")
    print('Client disconnected')

@app.route("/app", methods=("GET", "POST"))
def payment_request_view():
    if request.method == 'POST':
        crypto_name = f"BNB-{request.form['currency']}"
        external_id = request.form['invoice_id']
        amount = request.form['amount']
        fiat = "USD"
        callback_url = f"{callback_endpoint}/api/payment_notification"
        headers = { 'X-BlockX-Api-Key': api_key }
        payment_payload = {
            "amount": amount,
            "fiat": fiat,
            "external_id": external_id,
            "callback_url": callback_url
        }
        payment_request_url = f"{backend_server}/api/v1/{crypto_name}/payment_request"
        payment_request_response = requests.post(payment_request_url,headers=headers, json=payment_payload)
        res_body = payment_request_response.json()
        # check the res_body["status"] if it is success or error
        if res_body["status"] == "success":
            # Load the callback web page. wait for client to send the funds
            wallet_address = res_body["wallet"]
            payment_amount = res_body["amount"]
            crypto = request.form['currency']
            msg = f"Payment request is successful. Send {payment_amount} to this wallet address {wallet_address}"
            return redirect(url_for("payment_notification",invoice_id=external_id, crypto=crypto, wallet=wallet_address, amount=payment_amount))
        else:
            msg = res_body["message"]
            error_message = f"Payment not successful. {msg}"
            return error_message, 400
    return render_template("wallet/process_payment.j2")


@socketio.on('message')
def handle_message(data):
    print('Received message: ' + data)
    # Emit a response back to the client
    emit('response', {'data': 'Message received!'})
    
# @app.route('/notify')
# def notify():
#     socketio.emit('notification', {'message': 'New event'})
#     return 'Notification sent!'

@app.get('/payment/notify')
def payment_notify():
    return render_template("wallet/payment_notifier.j2")

@app.get('/')
def home():
    return "API is Alive and Running 🚀"

api = Api(
    app,
    version='1.0',
    title='Blockx Pay API Documentation',
    # description='Blockx Payment Gateway',
    description='''
    BlockX Payment Gateway
    
    
    Public Node Baseurl 
    Public node on Test net - https://pay-test-publicnode.blockxnet.com/api/v1/
    Public node on Main net - https://pay-main-publicnode.blockxnet.com/api/v1/
    
    Full Node Baseurl
    Full node on Test net -  https://pay-test-fullnode.blockxnet.com/api/v1/
    Full node on Main net - https://pay-main-fullnode.blockxnet.com/api/v1/
    
    Supported token are BNB-USDT, BNB-USDC
    
    For more questions like to request for the API Key contact this emaill address nick54321@gmail.com
    ''',
    doc='/swagger' 
)

# Register the namespaces
api.add_namespace(test_ns)
api.add_namespace(main_ns)
    
# Redocly route for API documentation
@app.route('/docs')
def redoc():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
          <title>My API Docs</title>
          <!-- Redoc CDN -->
          <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
        </head>
        <body>
          <redoc spec-url='/swagger.json'></redoc>
          <script>
            Redoc.init('/swagger.json', {}, document.querySelector('redoc'))
          </script>
        </body>
        </html>
    ''') 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)