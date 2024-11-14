from flask_restx import Namespace, Resource, fields
from flask import request
# Create a namespace for products
test_ns = Namespace('Testnet', description='Testnet payment related operations', path="/api/v1")

# Testnet Model
testnet_payment_model = test_ns.model('Payment', {
    'amount': fields.Integer(required=True, description='Amount to pay'),
    'crypto_name': fields.String(required=True, description='Fiat USDT, USDC'),
    'callback_url': fields.String(required=True, description='Callback URL'),
})

testnet_payout_model = test_ns.model('Payout', {
    'amount': fields.Integer(required=True, description='Amount to send'),
    'destination': fields.String(required=True, description='Destination wallet address'),
    'fee': fields.String(required=True, description='transaction fee'),
})

testnet_transaction_model = test_ns.model('Transaction', {
    'txid': fields.String(required=True, description='transaction hash ID'),
    'date': fields.String(required=True, description='Transaction created date'),
    'amount_crypto': fields.String(required=True, description='amount in crypto'),
    'crypto': fields.String(required=True, description='Crypto name'),
    'trigger': fields.String(required=True, description='Is the callback trigger true or false a boolean value'),
    'fee_fiat': fields.String(required=True, description='transaction fee in fiat'),
    'amount_fiat_without_fee': fields.String(required=True, description='transaction amount without fee in fiat'),
    'amount_fiat': fields.String(required=True, description='transaction amount in fiat'),
    'amount_crypto': fields.String(required=True, description='transaction amount in crypto'),
    
})

testnet_payment_callback_model = test_ns.model('PaymentCallback', {
    "external_id": fields.String(required=True, description='Invoice or order Id'),
    "crypto": fields.String(required=True, description='Crypto Name, example BNB_USDT, BNB_USDC'),
    "addr": fields.String(required=True, description='wallet address'),
    "fiat": fields.String(required=True, description='Fiat. example USD'),
    "balance_fiat": fields.String(required=True, description='Fiat Balance'),
    "balance_crypto": fields.String(required=True, description='Crypto Balance'),
    "paid": fields.String(required=True, description='Payment status true or false'),
    "status": fields.String(required=True, description='Payment status process. PAID, UNPAID, PARTIAL, OVERPAID'),
    "fee_percent": fields.String(required=True, description='Transaction fee percent'),
    "fee_fixed": fields.String(required=True, description='Transaction fee'),
    "fee_policy": fields.String(required=True, description='Transaction fee policy'),
    "overpaid_fiat": fields.String(required=True, description='Overpaid amount in fiat'),
    "transactions": fields.List(fields.Nested(testnet_transaction_model))
})

pays = []

@test_ns.route('/<string:crypto_name>/payment_request')
@test_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@test_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True) 
class PaymentProcess(Resource):    
    @test_ns.expect(testnet_payment_model)
    @test_ns.marshal_with(testnet_payment_model, code=200)
    def post(self):
        """Make a payment"""
        api_key = request.headers.get('X-BlockX-Api-Key')
        if len(api_key) > 0:
            pay = test_ns.payload
            pays.append(pay)
            return pay, 200
        else:
            return {'message': 'Unauthorized', 'status': 'failure'}, 401

@test_ns.route('/payment_notification')
class PaymentCallback(Resource):    
    @test_ns.expect(testnet_payment_callback_model)
    @test_ns.marshal_with("",code=202)
    def post(self):
        """Payment callback"""
        pay = test_ns.payload
        pays.append(pay)
        return pay, 202

@test_ns.route('/<string:crypto_name>/payout')
@test_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header with Bearer token',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@test_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True) 
class Payout(Resource):    
    @test_ns.expect(testnet_payout_model)
    @test_ns.marshal_with("",code=200)
    def post(self, crypto_name):
        """Payout"""
        pay = test_ns.payload
        pays.append(pay)
        return pay, 200

@test_ns.route('/transactions/<string:crypto_name>/<string:wallet_address>')
@test_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@test_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True)   
@test_ns.param('wallet_address', "Wallet address", required=True)   
class WalletTransaction(Resource):
    @test_ns.doc(responses={200: 'Success', 401: 'Unauthorized'}) 
    def get(self, crypto_name, wallet_address):
        """Wallet transactions"""
        # Retrieve the API key from the headers
        api_key = request.headers.get('X-BlockX-Api-Key')
        if not api_key:
            return {'message': 'API key is required', 'status': 'error'}, 200
        return {wallet_address, crypto_name}, 200


@test_ns.route('/tx-info/<string:trans_id>/<string:invoice_id>')
@test_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@test_ns.param('trans_id', "Transaction id", required=True)   
@test_ns.param('invoice_id', "Invoice/Order/Item id", required=True)   
class Transaction(Resource):
    @test_ns.doc(responses={200: 'Success', 401: 'Unauthorized'}) 
    def get(self, crypto_name, wallet_address):
        """Get Payment info"""
        # Retrieve the API key from the headers
        api_key = request.headers.get('X-BlockX-Api-Key')
        if not api_key:
            return {'message': 'API key is required', 'status': 'error'}, 200
        return {wallet_address, crypto_name}, 200