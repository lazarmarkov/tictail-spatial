Thoughts
========


There are three main problems to solve:
* Find all shops within a distance.
* Filter shops by tags. 
* Find _n_ most popular products within a set of shops.  
  
  
Find all shops within a distance
--------------------------------

To find shops within a certain distance, we must perform a spatial search.  
More concisely, we must perform a two-dimensional circular range search.  

It turns out that range searches can be enabled by organizing the data into a tree, like:  
  * k-d tree
  * R*-tree 
  * R-tree

Any of those trees can be used to achieve logarithmic time complexity (on average) for a range search.

There are robust implementations of
[r-tree](https://pypi.python.org/pypi/Rtree/) and
[k-d tree](http://docs.scipy.org/doc/scipy-0.14.0/reference/spatial.html) 
for python. We will be using a __k-d tree__ as a basis.



Filter shops by tags
--------------------

To quickly get the list of shops by a tag,
we will use a __hash map__. It will have __tags as keys__ and __list of shops as values__.
  
This way, we could __find the list of shops__ that have a certain tag in __O(1) time__.

The _list of shops_ will be implemented as a __hash set__.
This allows to __check in O(1) time if a shop is tagged__ with a certain tag.

As a result, checking if a shop is tagged with atleast 1 out of _k_ tags
takes __O(_k_) time__. And so, to check _l_ shops against _k_ tags takes __O(l*k)__ time.


Finding the most popular products within a set of shops
-------------------------------------------------------

For each shop we will keep a __sorted list of products by popularity__.  
At each iteration, we will examine the __head of each list__, taking only the product with the highest popularity.
