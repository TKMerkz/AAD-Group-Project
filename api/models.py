from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
class User(AbstractUser):
    #To determine whether or not a user is a customer, we can use this flag
    is_customer = models.BooleanField(default=False)
    
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,primary_key=True)
    first_name = models.CharField(max_length=28)
    last_name = models.CharField(max_length=28)
    charge_code = models.CharField(max_length=16)
    pays_vat = models.BooleanField(default=False)
    allowed_chemicals = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    department_id = models.ForeignKey(
      'Department',
      on_delete=models.PROTECT,
      null=True
    )
    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    


class Department(models.Model):
    name = models.CharField(max_length=56)
    head_id = models.ForeignKey(
      'Customer',
      on_delete=models.PROTECT
    )


class Item(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=3, decimal_places=2)
    quantity = models.PositiveIntegerField()
    warning_quantity = models.PositiveIntegerField()
    is_chemical = models.BooleanField()
    pack_size = models.PositiveSmallIntegerField()
    for_sale = models.BooleanField(default=True)


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        TO_ORDER = 'TO', _('To Order')
        ON_ORDER = 'ON', _('On Order')
        CANCELLED = 'CA', _('Cancelled')
        COMPLETED = 'CO', _('Completed')

    item_id = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT
    )
    datetime = models.DateTimeField()
    staff_id = models.ForeignKey(
        'Staff',
        on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=2,
        choices=OrderStatus.choices,
        default=OrderStatus.TO_ORDER
    )


class Return(models.Model):
    class ReturnReason(models.TextChoices):
        DAMAGED = 'DA', _('Damaged')
        NOT_NEEDED = 'NN', _('Not Needed')
        WRONG_ITEM = 'WI', _('Wrong Item')

    datetime = models.DateTimeField()
    staff_id = models.ForeignKey(
        'Staff',
        on_delete=models.PROTECT
    )
    customer_id = models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT
    )
    sale_item_id = models.ForeignKey(
        'SaleItem',
        on_delete=models.PROTECT
    )
    reason = models.CharField(
        max_length=2,
        choices=ReturnReason.choices
    )
    quantity = models.PositiveIntegerField()


class Sale(models.Model):
    datetime = models.DateTimeField()
    customer_id = models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT
    )


class SaleItem(models.Model):
    sale_id = models.ForeignKey(
        'Sale',
        on_delete=models.CASCADE
    )
    item_id = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT
    )
    price_at_sale = models.DecimalField(max_digits=3, decimal_places=2),
    quantity = models.PositiveIntegerField()
    returned_quantity = models.PositiveIntegerField()


class Staff(models.Model):
    class StaffAccessLevel(models.TextChoices):
        TRAINEE = 'TR', _('Trainee')
        BASIC = 'BA', _('Basic')
        MANAGER = 'MA', _('Manager')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,primary_key=True)
    first_name = models.CharField(max_length=28)
    last_name = models.CharField(max_length=28)
    login_code = models.CharField(max_length=16)
    access_level = models.CharField(
        max_length=2,
        choices=StaffAccessLevel.choices,
        default=StaffAccessLevel.TRAINEE
    )
    enabled = models.BooleanField(default=True)
    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)


class StockCheck(models.Model):
    datetime = models.DateTimeField()
    staff_id = models.ForeignKey(
        'Staff',
        on_delete=models.PROTECT
    )


class StockCheckItem(models.Model):
    stock_check_id = models.ForeignKey(
      'StockCheck',
      on_delete=models.CASCADE
    )
    item_id = models.ForeignKey(
      'Item',
      on_delete=models.PROTECT
    )
    observed_quantity = models.PositiveIntegerField()
    expected_quantity = models.PositiveIntegerField()

#When a user is created, we create their profile based on what user type they are
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created: 
        if instance.is_customer:  
            userType = Customer.objects.create(user=instance)

        else:
            userType = Staff.objects.create(user=instance)

