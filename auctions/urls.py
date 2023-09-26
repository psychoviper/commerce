from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:list_id>", views.listing, name="listing"),
    path("<int:list_id>/closed", views.cdlisting, name="cdlisting"),
    path("watch", views.watch, name="watch"),
    path("closed", views.closed, name="closed"),
    path("<int:listing_id>/add", views.add, name="add"),
    path("<int:listing_id>/remove", views.remove, name="remove"),
    path("<int:listing_id>/bidding", views.bidding, name="bidding"),
    path("create", views.create, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>/close", views.close, name="close")
]
