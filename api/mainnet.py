from flask_restx import Namespace, Resource, fields
from flask import request

# Create a namespace for products
main_ns = Namespace('Mainnet', description='Mainnet related operations', path="/api/v2")

# Mainnet Model
mainnet_payment_model = main_ns.model('Payment', {
    'amount': fields.Integer(required=True, description='Amount to pay'),
    'crypto_name': fields.String(required=True, description='Fiat USDT, USDC'),
    'callback_url': fields.String(required=True, description='Callback URL'),
})

mainnet_payout_model = main_ns.model('Payout', {
    'amount': fields.Integer(required=True, description='Amount to send'),
    'destination': fields.String(required=True, description='Destination wallet address'),
    'fee': fields.String(required=True, description='transaction fee'),
})

mainnet_transaction_model = main_ns.model('Transaction', {
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

mainnet_payment_callback_model = main_ns.model('PaymentCallback', {
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
    "transactions": fields.List(fields.Nested(mainnet_transaction_model))
})

pays = []

@main_ns.route('/<string:crypto_name>/payment_request')
@main_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@main_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True) 
class PaymentProcess(Resource):    
    @main_ns.expect(mainnet_payment_model)
    @main_ns.marshal_with(mainnet_payment_model, code=200)
    def post(self):
        """Make a payment"""
        api_key = request.headers.get('X-BlockX-Api-Key')
        if len(api_key) > 0:
            pay = main_ns.payload
            pays.append(pay)
            return pay, 200
        else:
            return {'message': 'Unauthorized', 'status': 'failure'}, 401

@main_ns.route('/payment_notification')
class PaymentCallback(Resource):    
    @main_ns.expect(mainnet_payment_callback_model)
    @main_ns.marshal_with("",code=202)
    def post(self):
        """Payment callback"""
        pay = main_ns.payload
        pays.append(pay)
        return pay, 202
    
@main_ns.route('/<string:crypto_name>/payout')
@main_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header with Bearer token',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@main_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True) 
class Payout(Resource):    
    @main_ns.expect(mainnet_payout_model)
    @main_ns.marshal_with("",code=200)
    def post(self, crypto_name):
        """Payout"""
        pay = main_ns.payload
        pays.append(pay)
        return pay, 200
    

@main_ns.route('/transactions/<string:crypto_name>/<string:wallet_address>')
@main_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@main_ns.param('crypto_name', "Crypto name [BNB-USDT, BNB-USDC]", required=True)   
@main_ns.param('wallet_address', "Wallet address", required=True)   
class WalletTransaction(Resource):
    @main_ns.doc(responses={200: 'Success', 401: 'Unauthorized'}) 
    def get(self, crypto_name, wallet_address):
        """Wallet transactions"""
        # Retrieve the API key from the headers
        api_key = request.headers.get('X-BlockX-Api-Key')
        if not api_key:
            return {'message': 'API key is required', 'status': 'error'}, 200
        return {wallet_address, crypto_name}, 200


@main_ns.route('/tx-info/<string:trans_id>/<string:invoice_id>')
@main_ns.doc(params={
    'Authorization': {
        'description': 'Authorization header within (e.g. {"X-BlockX-Api-Key": "xxxx"})',
        'in': 'header',  # Specify that it's in the header
        'type': 'string',
        'required': True
    }
})
@main_ns.param('trans_id', "Transaction id", required=True)   
@main_ns.param('invoice_id', "Invoice/Order/Item id", required=True)   
class Transaction(Resource):
    @main_ns.doc(responses={200: 'Success', 401: 'Unauthorized'}) 
    def get(self, crypto_name, wallet_address):
        """Get Payment info"""
        # Retrieve the API key from the headers
        api_key = request.headers.get('X-BlockX-Api-Key')
        if not api_key:
            return {'message': 'API key is required', 'status': 'error'}, 200
        return {wallet_address, crypto_name}, 200