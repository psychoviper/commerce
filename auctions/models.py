from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listings(models.Model):
    title=models.CharField(max_length=64)
    description=models.CharField(max_length=200, blank=True, default="Regret")
    bid=models.DecimalField(decimal_places=2, max_digits=10)
    current_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='latest_bid', null=True, blank=True)
    image=models.ImageField(null=True, blank=True, upload_to="uploads/")
    category=models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_of_item', blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name="listing")
    active=models.BooleanField(default=True)
    comments = models.ManyToManyField('Comment', related_name="comments_of_item", blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} : {self.description} price {self.bid}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    listings = models.ManyToManyField(Listings, related_name="watchlist_listings", blank=True)

class Bid(models.Model):
    item=models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="amount")
    bid=models.IntegerField(blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name="money")

    def __str__(self):
        return f"{self.item}  {self.user} price {self.bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_of_comment")
    comment = models.CharField(max_length=256)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.date_posted}"


class Category(models.Model):
    name = models.CharField(max_length=64)
    listing = models.ManyToManyField(Listings, related_name="category_listings", blank=True)

    def __str__(self):
        return f"{self.name}"