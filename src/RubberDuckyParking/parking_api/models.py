from django.db import models
from django import forms
from django.contrib.auth.models import User


class ParkingSizesTable(models.Model):
    """
    Helps characterize the different sizes of parking spots. One to One relationship with Location.
    """
    name = models.CharField(max_length=20)              # i.e standard, or small rv, or compact, or large bus
    description = models.CharField(max_length=100)       # standard parking lot found at most places
    min_width = models.FloatField()                   # stored in ft, i.e. "9" means nine feet long
    min_length = models.FloatField()                  # stored in ft, i.e. "18" means eighteen feet long

    class Meta:
        verbose_name = "Parking Space Size"
        verbose_name_plural = "Parking Space Sizes"

    def __str__(self):
        return f"{self.name}: {round(self.min_length, 1)}ft x {round(self.min_width, 1)}ft"


class BaseUser(User):
    '''
        This is the user that all other user models will inherit
        It is based off of django's default user model
    '''
    avatar = models.ImageField(blank=True)


class Host(BaseUser):
    pass


class Attendant(BaseUser):
    """
    The person that scans in Users as they arrive. Attendant and Host might be the same person, however for larger lots
    the host could have one or many attendants that are the 'gatekeepers' for the lot.
    """
    pass


class Vehicle(models.Model):
    """
    For keeping track of owners car, confirming the transaction, and verifying that a parked car should/shouldn't be there
    """
    year = models.IntegerField(default=2015)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)# TODO should i make these choices or free entry and have the browser handle validation or no validation?
    color = models.CharField(max_length=10)  # TODO make a text choice field?
    license = models.CharField(max_length=8)  # most states dont allow over 8 characters.
    description = models.CharField(max_length=100, default="")  # allows the user to give nicknames to their car
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.year} {self.color} {self.make}: {self.license}"


class Location(models.Model):
    """
    The address of a parking lot, dirt lot, driveway, etc.
    A Host can host (have) multiple locations
    """
    name = models.CharField(max_length=100)             # i.e. "My right driveway"
    description = models.CharField(max_length=500)      # i.e. "the right side of a two car wide driveway
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10, default="20500")          # i.e. 84093-3541
    state = models.CharField(max_length=3)
    host_id = models.ForeignKey(Host, default=1, on_delete=models.CASCADE)     # Host can have many parking locations

    def __str__(self):
        return f"{self.name} at {self.address}"


class ParkingSpot(models.Model):
    """
    This is an individual parking spot, that is at a location.
    A location can have many types of parking spots.
    """
    uid = models.IntegerField(default=1)
    parking_size = models.ForeignKey(ParkingSizesTable, on_delete=models.CASCADE, default=1,
                                     verbose_name="Parking Size")  # TODO maybe change the on delete behavior
    actual_width = models.FloatField(default=9.0)
    actual_length = models.FloatField(default=18.0)
    price = models.FloatField(default=5.0)      # cost per hour
    #  TODO could make it possible to have a price for a whole day, a range of time, or per hour
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)
    notes = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"Parking Spot {self.uid}"

    class Meta:
        verbose_name_plural = "Parking Spots"


class Transactions(models.Model):
    """
    Record the individual rents that happen
    """
    date = models.DateTimeField()
    user_charge = models.DecimalField(max_digits=8, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2)
    host_income = models.DecimalField(max_digits=8, decimal_places=2)
    host_id = models.ForeignKey(Host, default=1, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, default=1, on_delete=models.CASCADE)
    spot_id = models.ForeignKey(ParkingSpot, default=1, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, default=1, on_delete=models.CASCADE)
    hash_str = models.CharField(max_length=100)  # used to make the QR Code
    # TOOD dont use the vehicle in the hash str so it can change

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.date.strftime('%c')} --USER: {self.user_id} --HOST: {self.host_id} --CHARGE: {self.user_charge}$"


class LocationImage(models.Model):
    """
    Used to save multiple pictures of the parking spaces, etc.
    https://stackoverflow.com/questions/40218080/how-to-add-multiple-images-to-the-django
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/location/", blank=True)

    class Meta:
        verbose_name_plural = "Images"

    def __str__(self):
        return f"Image of {self.location.name}"
