![shurjoPay](shurjoPay.png)
# ShurjoPay

shurjopay python integration steps
## Prerequisite
To integrate ShurjoPay you need few credentials to access shurjopay:
```
:param prefix: Any string not more than 5 characters. It distinguishes the stores of a merchant.
:param currency: ISO format,(only BDT and USD are allowed).
:param return_url: Merchant should provide a GET Method return url to verify users initiated transaction status. 
:param cancel_url: Merchant should provide a cancel url to redirect the user if he/she cancels the transaction in midway. 
:param client_ip: User's ip
:param username: Merchant Username provided by shurjopay.
:param password: Merchant Password provided by shurjopay.
:param post_address: Live shurjopay version 2 URL.
```


> 📝 **NOTE** For shurjoPay version 2 live engine integration all necessary credential will be given to merchant after subscription completed on shurjoPay gateway.

---

## Installation

Use the package manager ```pip``` to install Shuropay python package
```
pip install shurjopay-V2
```
To install Python package from github, you need to clone that repository.

   ```
   git clone https://github.com/smukhidev/sp2-python.git
   ```

Then just run the setup.py file from that directory,

   ```
   sudo python setup.py install
   ```
## Usage
```
from shurjopay_v2.shurjopay import ShurjoPay

#initialize with the test credentials

testpay = shurjoPay.ShurjoPay(prefix="NOC", currency="BDT", return_url=[URL],cancel_url=[URL], client_ip=[IP],  username=[USERNAME], password=[PASSWORD], post_address=[SURJOPAY_URL])
testpay.checkout(1, "xyz123456789", "demo", "01682803595", "N/a", "dhaka")
testpay.check_status(order_id="NOC6188d03129212")

```
In return url controller to verify and get the sp order_id
```
from shurjopay_v2.shurjopay import ShurjoPay

#initialize with the test credentials

verifypayment = shurjoPay.ShurjoPay(prefix="NOC", currency="BDT", return_url=[URL],cancel_url=[URL], client_ip=[IP],  username=[USERNAME], password=[PASSWORD], post_address=[SURJOPAY_URL])
verifypayment.verify(order_id="NOC6188d03129212")

```
### ShurjoPay
You can use the ShurjoPay class as an instance, within a class or by subclassing. The general usage flow is as follows:

- Create a ShurjoPay instance with these parameters
    ```
    :param prefix: Any string not more than 5 characters. It distinguishes the stores of a merchant.
    :param currency: ISO format,(only BDT and USD are allowed).
    :param return_url: Merchant should provide a GET Method return url to verify users initiated transaction status. 
    :param cancel_url: Merchant should provide a cancel url to redirect the user if he/she cancels the transaction in midway. 
    :param client_ip: User's ip
    :param username: Merchant Username provided by shurjopay.
    :param password: Merchant Password provided by shurjopay.
    :param post_address: Live shurjopay version 2 URL.
    ```
  - Initialize the payment transaction with the checkout() functions 
    - Arguments: 
        ```
        :param amount: Transaction Amount [float] 
        :param order_id: Provide a Unique ORDER ID [string]
        :param customer_name: Customer Full Name [string]
        :param customer_phone: Customer Active Contact Number [string]
        :param customer_address: Customer Address [string]
        :param customer_city: Customer City [string]
        ```
    - Response : a `JSON` response with dynamic checkout_url will be provided. Example response
      ```
      { 
        'checkout_url': 'https://sandbox.securepay.shurjopayment.com/spaycheckout/?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvc2FuZGJveC5zaHVyam9wYXltZW50LmNvbVwvYXBpXC9sb2dpbiIsImlhdCI6MTYzNjM1MzYyMCwiZXhwIjoxNjM2MzU3MjIwLCJuYmYiOjE2MzYzNTM2MjAsImp0aSI6Ikt1MW1salZFQlBmaHdBRW8iLCJzdWIiOjEsInBydiI6IjgwNWYzOWVlZmNjNjhhZmQ5ODI1YjQxMjI3ZGFkMGEwNzZjNDk3OTMifQ.AVChXtT-g5De5OmenIucKvWF0PXx4x23PBjQFMsukJk&order_id=NOC6188d03129212',
        'amount': 1,
        'currency': 'BDT',
        'sp_order_id': 'NOC6188d03129212',
        'customer_order_id': 'xyz123456789',
        'customer_name': 'demo',
        'customer_address': 'N/a',
        'customer_city': 'dhaka',
        'customer_phone': '01682803595',
        'customer_email': None,
        'client_ip': '192.168.0.99',
        'intent': 'sale',
        'transactionStatus': 'Initiated'
      }
      ```

- This ```ceckout_url``` will return an HTML shurjopay form you need to render this in your application for your users to complete the transaction.

    ![spform](sp.png)
- After the transaction initialized customer action status will be sent through the return_url/cancel_url with a ```query string```  ```?order_id=[SpOrderId]``` merchant should store the id for future use.
- Use verify() to verify the transaction. This call is required only once for each transaction that initialized
  - Arguments:
  ```
  :param order_id: For verification, merchants must use order_id that is sent from shurjoPay during callback.
  ```
  - Response `JSON`
- Use check_status() to check the customer transaction status.
    - Arguments:
  ```
  :param order_id:For transaction status, merchants must use order_id that is sent from shurjoPay during callback.
  ```
    - Response `JSON`
