from rbtree import rbtree

class PopularProductsService(object):
    
    def __init__(self, products):
        """ A service that finds the most popular products
        within a list of shops.
        
        Parameters
        ----------
        products : list of Products
        
        """
        # Mapping from shop id to list of products within the shop.
        # The products are sorted by popularity in descending order.
        self._products_by_shop = {}
        
        # Filter the out of stock products.
        products = filter(lambda p: p.quantity > 0, products)
        
        for p in products:
            products = self._get_products_by_shop(p.shop_id)
            products[p.popularity] = p
    
    def _get_products_by_shop(self, shop_id):
        """ Returns a list of products for the `shop id`, ordered by popularity.
        
            Parameters
            ----------
            shop_id : string
                The id of the shop for which to get the products.
            
            Returns
            -------
            products : bst of Products
                A red-black tree of Products, ordered by Product.popularity, in descending order.
        
        """
        
        # Check if a mapping for the shop is missing.
        if shop_id not in self._products_by_shop:
            # Map the shop to an empty rbtree.
            self._products_by_shop[shop_id] = rbtree(
                cmp = PopularProductsService._duplicate_reverse_order_comparer)
        
        # Return the products for the shop.
        return self._products_by_shop[shop_id]
    
    def find_popular_products(self, shop_ids, count):
        """ Finds the most popular products within the specified shops.
        
        Parameters
        ----------
        shop_ids : list of strings
            Ids of the shops included in the search.
        count : int
            The max number of products to return.
        
        Returns
        -------
        products : list of Products
            The list of most popular products.
        
        """
        # Get the list of sorted products by popularity for each shop specified.
        products_per_shop = [self._get_products_by_shop(id).values() for id in shop_ids]
        
        # Get an iterator for each list of products.
        iterators = [iter(products) for products in products_per_shop]
        
        # Create a ad-hoc iterator,
        # feeded with products iterators for the specified shops.
        it = PopularProductsIterator(zip(shop_ids, iterators), count)
        
        # List the result.
        return list(it)
    
    @staticmethod
    def _duplicate_reverse_order_comparer(x, y):
        """ A reverse order comparer that allows duplicate entries.
        If two items are equal it declares the first one larger.
        
        """
        x = cmp(x, y)
        if(x == 0):
            return 1
        return -x


class PopularProductsIterator(object):
    
    def __init__(self, shops, count):
        """ Iterates products by popularity from multiple shops.
        
            Parameters
            ----------
            shops : list of tuples
                First item is id of the shop,
                second item is an iterator to its products, ordered by Product.popularity.
            count : int
                The max number of products to return.
            
        """
        # Mappings from shop id to an iterator to its products.
        self._shops = dict(shops)
        
        # Mappings from shop id to its current most popular product.
        self._most_popular_in_shop = {}
        
        # The number of products left to return.
        self._count = count
        
        # Initialize the current most popular product per shop.
        for shop_id in self._shops.keys():
            self._next_most_popular_in_shop(shop_id)

    def _next_most_popular_in_shop(self, shop_id):
        """ Moves to the next most popular product for a shop.
        
        """
        try:
            # Gets next most popular product for the shop
            # and assigns it as its current most popular.
            self._most_popular_in_shop[shop_id] = self._shops[shop_id].next()
        # No more products in the shop.
        except StopIteration:
            
            # Remove the taken product.
            if shop_id in self._most_popular_in_shop:
                del self._most_popular_in_shop[shop_id]
            
            # Remove the empty shop.
            del self._shops[shop_id]
    
    def __iter__(self):
        return self
    
    def next(self):
        """ Return the next most popular product with the shops.
        
            Returns
            -------
            product : Product
                
        """
        # If max number of products are returned
        # OR
        # if there are no more products to return,
        # signal stop iteration.
        if self._count == 0 or not bool(self._most_popular_in_shop):
            raise StopIteration
        
        # Find the most popular product within the shops.
        p = max(self._most_popular_in_shop.values(), key = lambda p: p.popularity)
        
        # Mark the product as taken,
        # and move to the next one in the shop.
        self._next_most_popular_in_shop(p.shop_id)
        
        # Decrease the remaining products to return.
        self._count -= 1
        return p
    

class Product(object):
    
    def __init__(self, id, shop_id, title, popularity, quantity):
        
        # Id of the product.
        self.id = id
        
        # Id of the product's shop.
        self.shop_id = shop_id
        
        # Title of the product.
        self.title = title
        
        # Popularity rating of the product.
        self.popularity = popularity
        
        # Product quantity in stock.
        self.quantity = quantity
    
    def __str__(self):
        return "Product: id:{0}, shop_id:{1}, title:{2}, populariy:{3}, quantity:{4}".format(
            self.id, self.shop_id, self.title, self.popularity, self.quantity)

    def serialize(self):
        return {
            'id': self.id,
            'shop_id': self.shop_id,
            'title': self.title,
            'popularity': self.popularity,
            'quantity': self.quantity
        }