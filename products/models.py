import os
from faker import Faker
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Address

fake = Faker(['en-US', 'en_US', 'en_US', 'en-US'])
Faker.seed(0)


def get_fake_description():
    word_list = ['fit', 'breathable', 'sleek', 'cotton', 'sleeve', 'round', 'printed', 'is', 'slim', 'regular', 'look', 'Give your wardrobe a quick upgrade with this classy',
                 'stripes', 'comfort', 'classic', 'a', 'the', 'and', 'made from', 'hue', 'clothing', 'fabric']
    return fake.paragraph(nb_sentences=6, ext_word_list=word_list)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(email='deleteduser@slicks.com')[0]


def path_and_rename(instance, filename):
    # saves filename with uqid of product instead of original uploaded name
    path = 'img/prod'
    ext = filename.split('.')[-1]
    # get filename
    if instance.uqid:
        filename = '{}.{}'.format(instance.uqid, ext)
    # return the whole path to the file
    return os.path.join(path, filename)


class Product(models.Model):
    shirts = 1
    tshirts = 2
    sweatshirts = 3
    jackets = 4
    tanktops = 5
    blazers = 6
    dress = 7
    jeans = 8
    shorts = 9
    trackpants = 10
    trousers = 11


    clothing_categories = [
        # (name saved in database, human readable)
        (shirts, 'Shirts'),
        (tshirts, 'Tshirts'),
        (sweatshirts, 'Sweatshirts'),
        (jackets, 'Jackets'),
        (tanktops, 'Tanktops'),
        (blazers, 'Blazers'),
        (dress, 'Dress'),
        (jeans, 'Jeans'),
        (shorts, 'Shorts'),
        (trackpants, 'Track Pants'),
        (trousers, 'Trousers'),


    ]

    clothing_brands = [
        ('network', 'Network'),
        ('mufti', 'Mufti'),
        ('anthem', 'Anthem'),
        ('blue saint', 'Blue Saint'),
        ('dennis lingo', 'Dennis Lingo'),
        ('balista', 'Balista'),
        ('hue', 'Hue'),
        ('harbour', 'Harbour'),
        ('flyrs', 'Flyrs'),
        ('up', 'UP')
    ]

    type_choices = [
        ('clothes', 'clothes'),
        ('watches', 'watches'),
        ('shoes', 'shoes'),
        ('lingerie','lingerie'),
        ('beauty', 'beauty')
    ]
    size_xsm = 'xsm'
    size_sm = 'sm'
    size_m = 'm'
    size_l = 'l'
    size_xl = 'xl'

    size_choices = [
        (size_xsm, 'XSM'),
        (size_sm, 'S'),
        (size_m, 'M'),
        (size_l, 'L'),
        (size_xl, 'XL')
    ]

    # uqid is uuid for products
    uqid = models.UUIDField(unique=True, blank=False,
                            null=False, default=uuid.uuid4, editable=False)
    brand = models.CharField(blank=True, null=True,
                             max_length=70, choices=clothing_brands)
    name = models.CharField(blank=False, null=False, max_length=150)
    img1 = models.ImageField(upload_to=path_and_rename)
    # for now only one img is required, rest optional
    # adding img field here as a join would be slow ?
    img2 = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    img3 = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    # maybe add limit for min and max values in future
    price = models.PositiveIntegerField()
    description = models.TextField()
    category = models.IntegerField(
        blank=True, null=True, choices=clothing_categories)
    composition = models.CharField(max_length=120)
    type = models.CharField(choices=type_choices, max_length=15)

    # adding available quantities for given size here, maybe separate table would have been better.
    sm_quant = models.PositiveIntegerField(default=0)
    m_quant = models.PositiveIntegerField(default=0)
    l_quant = models.PositiveIntegerField(default=0)
    xl_quant = models.PositiveIntegerField(default=0)
     
    
    def __str__(self):
        if(self.brand):
            return self.brand + ' ' + self.name
        else:
            return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='wlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "product"]


class Order(models.Model):

    waitingconfirmation = 1
    confirmed = 2
    processed = 3
    shipped = 4
    delivered = 5
    cancelled = 6
    order_status_choices = [
        (waitingconfirmation, 'waiting confirmation'),
        (confirmed, 'confirmed'),
        (processed, 'processed'),
        (shipped, 'shipped'),
        (delivered, 'delivered'),
        (cancelled, 'cancelled')
    ]

    payment_status_choices = [
        (1, 'pending'),
        (2, 'success'),
        (3, 'failed')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET(
        get_sentinel_user), related_name='orders')
    total_quant = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()  # includes shipping cost
    shipping_cost = models.PositiveIntegerField()
    payment_status = models.PositiveIntegerField(
        blank=True, choices=payment_status_choices, default=1)
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True)
    status = models.PositiveIntegerField(
        blank=True, choices=order_status_choices, default=waitingconfirmation)
    ordered_at = models.DateTimeField(auto_now_add=True)

    # related to razorpay

    def __str__(self):
        return 'Order No. ' + str(self.id)

    class Meta:
        ordering = ['-ordered_at']
    


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=5, choices=Product.size_choices, default='XSM')
    quant = models.PositiveSmallIntegerField()
    # ordering price for 1 quantity...if price of product changes in future
    item_price = models.PositiveIntegerField()

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ["order", "product", "size"]

    


class Cart(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='cart', null=True)

    total_quant = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)

    def set_total_price_and_quant(self):
        items = self.items.all()
        tot_price = 0
        tot_quant = 0
        for item in items:
            tot_price += (item.product.price * item.quant)
            tot_quant += item.quant
        self.total_price = tot_price
        self.total_quant = tot_quant

    def __str__(self):
        return "Cart No." + str(self.id)

    # def get_total_quant(self):
    #     # todo
    #     tot_quant = 0
    #     items = self.items.all().only('quant')
    #     for item in items:
    #         tot_quant += item.quant
    #     return tot_quant


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=5, choices=Product.size_choices,default='XSM')
    quant = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ["cart", "product", "size"]
