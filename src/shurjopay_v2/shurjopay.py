import requests
import json
import datetime
import webbrowser
import logging
import os

# from .callbackHandler import *
# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)
# define file handler and set formatter
log_fileName = 'LOG/{:%Y-%m-%d}.log'.format(datetime.datetime.now())
os.makedirs(os.path.dirname(log_fileName), exist_ok=True)
file_handler = logging.FileHandler(log_fileName, mode="a", encoding=None, )
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(funcName)s  %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)


class ShurjoPay(object):
    _POST_DEFAULT_ADDRESS = "https://sandbox.shurjopayment.com"
    _TOKEN_END_POINT = "/api/get_token"
    _VERIFICATION_END_POINT = "/api/verification"
    _PAYMENT_STATUS_END_POINT = "/api/payment-status"
    _SANDBOX_USERNAME = "sp_sandbox"
    _SANDBOX_PASSWORD = "pyyk97hu&6u6"
    # _DEFAULT_RETURN_URL = "http://0.0.0.0:8000/en/sharedfarm/test_return_url"
    # _DEFAULT_CANCEL_URL = "http://0.0.0.0:8000/en/sharedfarm/test_return_url"
    _DEFAULT_RETURN_URL = "http://0.0.0.0:8008/return"
    _DEFAULT_CANCEL_URL = "http://0.0.0.0:8008/cancel"
    _DEFAULT_CLIENT_IP = "192.168.0.99"

    def __init__(self, prefix, currency, return_url=None, cancel_url=None, client_ip=None, username=None, password=None,
                 post_address=None, ):
        """

        :param prefix: Any string not more than 5 characters. It distinguishes the stores of a merchant.
        :param currency: ISO format,(only BDT and USD are allowed).
        :param return_url: Merchant should provide a GET Method return url to verify users initiated transaction status.
        :param cancel_url: Merchant should provide a cancel url to redirect the user if user cancels the transaction in midway.
        :param client_ip: User's ip
        :param username: Merchant Username provided by shurjopay.
        :param password: Merchant Password provided by shurjopay.
        :param post_address: Live shurjopay version 2 URL.
        """
        self.sandbox = False
        if post_address:
            self.root_address = post_address
            pass
        else:
            self.sandbox = True
            self.root_address = self._POST_DEFAULT_ADDRESS
            pass
        if client_ip:
            self.client_ip = client_ip
            pass
        else:
            self.client_ip = self._DEFAULT_CLIENT_IP
            pass
        if return_url:
            self.return_url = return_url
            pass
        else:
            self.return_url = self._DEFAULT_RETURN_URL
            pass
        if cancel_url:
            self.cancel_url = cancel_url
            pass
        else:
            self.cancel_url = self._DEFAULT_CANCEL_URL
            pass
        if username and password:

            self.username = username
            self.password = password
            pass
        else:
            self.username = self._SANDBOX_USERNAME
            self.password = self._SANDBOX_PASSWORD
            pass
        self.prefix = prefix
        self.currency = currency

        # declaration of token info
        self._token = None
        self._store_id = None
        self._execute_url = None
        self._expires_in = None
        self._token_type = None
        self._token_create_time = None
        self.set_sp_token()

        pass

    def set_sp_token(self):
        try:
            payload = {
                "username": self.username,
                "password": self.password
            }
            logger.info(f"url: {self.root_address + self._TOKEN_END_POINT}, payload:{payload}")
            response = requests.post(self.root_address + self._TOKEN_END_POINT, data=payload)
            # {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvc2FuZGJveC5zaHVyam9wYXltZW50LmNvbVwvYXBpXC9sb2dpbiIsImlhdCI6MTYzNTE0NTIxMywiZXhwIjoxNjM1MTQ4ODEzLCJuYmYiOjE2MzUxNDUyMTMsImp0aSI6IlVZZ1FkRWtSS2ZnNEJybHoiLCJzdWIiOjEsInBydiI6IjgwNWYzOWVlZmNjNjhhZmQ5ODI1YjQxMjI3ZGFkMGEwNzZjNDk3OTMifQ.cPXzg0UqeMD_6hVxqF1oKnzkwaJeRIn1gaEejAPz100', 'store_id': 1, 'execute_url': 'https://sandbox.shurjopayment.com/api/secret-pay', 'token_type': 'Bearer', 'sp_code': '200', 'massage': 'Ok', 'TokenCreateTime': '2021-10-25 01:00:13pm', 'expires_in': 3600}

            response_json = response.json()
            # set token information
            logger.info(f"response: {response_json}")
            if int(response_json["sp_code"]) == 200:
                self._token = response_json["token"]
                self._store_id = response_json["store_id"]
                self._execute_url = response_json["execute_url"]
                self._expires_in = response_json["expires_in"]
                self._token_type = response_json["token_type"]
                self._token_create_time = datetime.datetime.strptime(response_json["TokenCreateTime"],
                                                                     "%Y-%m-%d %I:%M:%S%p")

                pass
            else:
                raise Exception(response_json)
            return True
        except Exception as e:
            logger.exception(e)
            pass

    def _check_token_validity(self):
        if self.sandbox:
            return True
        else:
            if (self._token_create_time + datetime.timedelta(milliseconds=self._expires_in)) > datetime.datetime.now():
                return True
            else:
                return False

    def get_token(self):
        return self._token

    def checkout_web(self, amount, order_id, customer_name, customer_phone, customer_address, customer_city):
        """

        :param amount:
        :param order_id:
        :param customer_name:
        :param customer_phone:
        :param customer_address:
        :param customer_city:
        :return:
        """
        try:

            _headers = {'content-type': 'application/json', 'Authorization': f'{self._token_type} {self._token}'}
            _payloads = {
                "token": self._token,
                "store_id": self._store_id,
                "prefix": self.prefix,
                "currency": self.currency,
                "return_url": self.return_url,
                "cancel_url": self.cancel_url,
                "amount": amount,
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_address": customer_address,
                "customer_city": customer_city,
                "client_ip": self.client_ip
            }
            if self._check_token_validity():
                logger.info(f'url: {self._execute_url}, header:{_headers}, payload: {_payloads}')
                response = requests.post(self._execute_url, headers=_headers, data=json.dumps(_payloads))
                response_json = response.json()
                # driver =
                # r_response = requests.get(response_json["checkout_url"])
                # print(r_response.history)
                logger.info(f"response: {response_json}")
                webbrowser.open(response_json["checkout_url"])
                # wait_for_request('', 8008, self._token)
            else:
                logger.warning(f"is_token_expired: {self._check_token_validity()}")
            pass
        except Exception as e:
            logger.exception(e)
        pass

    def checkout(self, amount, order_id, customer_name, customer_phone, customer_address, customer_city):
        """

        :param amount: Transaction Amount
        :param order_id: Provide a Unique ORDER ID
        :param customer_name: Customer Full Name
        :param customer_phone: Customer Active Contact Number
        :param customer_address: Customer Address
        :param customer_city: Customer City
        :return:
        """
        try:

            _headers = {'content-type': 'application/json', 'Authorization': f'{self._token_type} {self._token}'}
            _payloads = {
                "token": self._token,
                "store_id": self._store_id,
                "prefix": self.prefix,
                "currency": self.currency,
                "return_url": self.return_url,
                "cancel_url": self.cancel_url,
                "amount": amount,
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_address": customer_address,
                "customer_city": customer_city,
                "client_ip": self.client_ip
            }
            if self._check_token_validity():
                logger.info(f'url: {self._execute_url}, header:{_headers}, payload: {_payloads}')
                response = requests.post(self._execute_url, headers=_headers, data=json.dumps(_payloads))
                response_json = response.json()
                logger.info(f"response: {response_json}")
                return response_json
            else:
                logger.warning(f"is_token_expired: {self._check_token_validity()}")
                return {"message": "token expired!"}
        except Exception as e:
            logger.exception(e)
        pass

    def verifty(self, order_id):
        """

        :param order_id: For verification, merchants must use order_id that is sent from shurjoPay during call back.
        :return:
        """
        try:
            _headers = {'content-type': 'application/json', 'Authorization': f'{self._token_type} {self._token}'}
            _payloads = {
                "order_id": order_id,
            }
            if self._check_token_validity():
                logger.info(f'url: {self.root_address}, header:{_headers}, payload: {_payloads}')
                response = requests.post(self.root_address + self._VERIFICATION_END_POINT, headers=_headers,
                                         data=json.dumps(_payloads))
                response_json = response.json()
                logger.info(f"response: {response_json}")
                return response_json
            else:
                logger.warning(f"is_token_expired: {self._check_token_validity()}")
                return {"message": "token expired!"}
        except Exception as e:
            logger.exception(e)
        pass

    def check_status(self, order_id):
        """

        :param order_id:For transaction status, merchants must use order_id that is sent from shurjoPay during callback.
        :return:
        """
        try:
            _headers = {'content-type': 'application/json', 'Authorization': f'{self._token_type} {self._token}'}
            _payloads = {
                "order_id": order_id,
            }
            if self._check_token_validity():
                logger.info(f'url: {self.root_address}, header:{_headers}, payload: {_payloads}')
                response = requests.post(self.root_address + self._PAYMENT_STATUS_END_POINT, headers=_headers,
                                         data=json.dumps(_payloads))
                response_json = response.json()
                logger.info(f"response: {response_json}")
                return response_json
            else:
                logger.warning(f"is_token_expired: {self._check_token_validity()}")
                return {"message": "token expired!"}
        except Exception as e:
            logger.exception(e)
        pass
