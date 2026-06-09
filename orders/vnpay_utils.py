import hashlib
import hmac
import urllib.parse
from django.conf import settings
from datetime import datetime

class VNPay:
    def __init__(self, tmn_code, hash_secret, return_url, vnpay_url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.return_url = return_url
        self.vnpay_url = vnpay_url
        self.requestData = {}

    def get_payment_url(self, order_id, amount, order_desc, ip_address):
        self.requestData['vnp_Version'] = '2.1.0'
        self.requestData['vnp_Command'] = 'pay'
        self.requestData['vnp_TmnCode'] = self.tmn_code
        self.requestData['vnp_Amount'] = str(int(amount) * 100)
        self.requestData['vnp_CurrCode'] = 'VND'
        self.requestData['vnp_TxnRef'] = str(order_id)
        self.requestData['vnp_OrderInfo'] = order_desc
        self.requestData['vnp_OrderType'] = 'billpayment'
        self.requestData['vnp_Locale'] = 'vn'
        self.requestData['vnp_ReturnUrl'] = self.return_url
        self.requestData['vnp_IpAddr'] = ip_address
        self.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')

        inputData = sorted(self.requestData.items())
        queryString = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self._hash(queryString)
        return self.vnpay_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def _hash(self, queryString):
        hashValue = hmac.new(
            self.hash_secret.encode('utf-8'),
            queryString.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return hashValue

    def validate_response(self, request_data):
        vnp_SecureHash = request_data.get('vnp_SecureHash')
        if not vnp_SecureHash:
            return False
            
        data = request_data.dict() if hasattr(request_data, 'dict') else request_data.copy()
        if 'vnp_SecureHash' in data:
            data.pop('vnp_SecureHash')
        if 'vnp_SecureHashType' in data:
            data.pop('vnp_SecureHashType')

        inputData = sorted(data.items())
        queryString = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    queryString = queryString + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    queryString = str(key) + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self._hash(queryString)
        return hashValue == vnp_SecureHash
