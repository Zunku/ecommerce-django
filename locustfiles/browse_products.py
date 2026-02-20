from locust import HttpUser, task, between
from random import randint
class WebsiteUser(HttpUser):
    # Locus will wait between 1 to 5 between each task
    wait_time = between(1, 5)
    
    # number = Weight/Priority. The higher the most common
    @task(2)
    def view_products(self):
        collection_id = randint(1,200)
        # name Test name, group all URLs
        self.client.get(
            f'/store/products/?collection_id={collection_id}', 
            name='/store/products/'
        )
    
    @task(4)
    def view_product(self):
        product_id = randint(2,700)
        self.client.get(
            f'/store/products/{product_id}',
            name='/store/products/:id'
        )
        
    @task(1)
    def add_to_cart(self):
        product_id = randint(2,11)
        self.client.post(
            f'/store/carts/{self.cart_id}/cartitems/',
            name='/store/carts/cartitems',
            # Sending data to the endpoint
            json={'product_id': product_id, 'quantity':1}
        )
    
    @task()
    def say_hello(self):
        self.client.get('/playground/slow/')
    
    # This is a life cycle hook, it's called every time a new user starts browsing our website
    def on_start(self):
        # Creating a cart for the user
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']
        
        # Obtaining product_id's dinamicaly, to avoid indexing non-existent products
        response = self.client.get("/store/products/")
        products = response.json()
        self.products = [p["id"] for p in products["results"]]