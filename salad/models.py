from django.db import models
from core.utils import UUIDMixin
from django.utils import timezone
from account.models import Account

def upload_location(instance, filename):
    """Generate dynamic upload path for media files."""
    ext = filename.split(".")[-1]
    model_name = instance.__class__.__name__.lower()
    return f"{model_name}/{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
class Ingredient(UUIDMixin):
    CATEGORY_CHOICES = (
        ('base', 'Base'),
        ('vegetable', 'Vegetable'),
        ('topping', 'Topping'),
        ('dressing', 'Dressing'),
        ('extra', 'Extra'),
    )
    name = models.CharField(max_length=250, null=True, blank=True, help_text="Ingredient name")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price per kg")
    calories = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Calories per 100gram")  # Store numeric value
    weight = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, help_text="Weight in kilograms (kg)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True, help_text="Ingredient category")
    description = models.TextField(null=True, blank=True, help_text="Ingredient description")  # Store string info like "5 kcal per 100g"
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, help_text="Image of the ingredient")
    available = models.BooleanField(default=True, help_text="Is available?")

    

    class Meta:
        db_table = 'salad_ingredient'
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name or "Unnamed Ingredient"



class SaladType(models.TextChoices):
    MOST_LOVED = 'most_loved', 'Most Loved Salad'
    POPULAR_PICK = 'popular_pick', 'Popular Salad Pick'

class Salad(UUIDMixin):
    name = models.CharField(max_length=250, null=True, blank=True, help_text="Salad name")
    description = models.TextField(null=True, blank=True, help_text="Salad description")
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, help_text="Image of the salad")
    ingredients = models.ManyToManyField(Ingredient, related_name='salads', help_text="Ingredients in the salad")
    calories = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Salad price")
    available = models.BooleanField(default=True, help_text="Is salad available?")
    salad_type = models.CharField(max_length=20, choices=SaladType.choices, help_text="Salad type")

    def calculate_total_calories(self):
        """Calculate total calories from ingredients."""
        return round(sum(ingredient.get_calories_per_100g() for ingredient in self.ingredients.all()), 2)

    def save(self, *args, **kwargs):
        self.calories = self.calculate_total_calories()
        super().save(*args, **kwargs)

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def average_rating(self):
        if self.reviews.exists():
            return round(self.reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0

    class Meta:
        db_table = 'salad'
        verbose_name = "Salad"
        verbose_name_plural = "Salads"

    def __str__(self):
        return self.name or "Unnamed Salad"

class Review(UUIDMixin):
    salad = models.ForeignKey(Salad, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Account, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(help_text="Rating between 1 and 5")
    comment = models.TextField(blank=True, help_text="Review comment")

    class Meta:
        db_table = 'salad_review'
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review for {self.salad.name} by {self.reviewer.username}"


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    CANCELED = 'canceled', 'Canceled'

class Order(UUIDMixin):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='orders', help_text="The user who placed the order")
    ingredients = models.ManyToManyField(Ingredient, related_name='orders', help_text="Ingredients in the custom order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price of the order")
    total_calories = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total calories of the order")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, help_text="Status of the order")


    class Meta:
        db_table = 'order'
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} ({self.status})"
    
class Testimonial(UUIDMixin):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='testimonials', help_text="User providing the testimonial")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating between 1 and 5")
    comment = models.TextField(help_text="User's testimonial or feedback about the service")
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, help_text="Optional image associated with the testimonial")

    class Meta:
        db_table = 'testimonial'
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.user.username} ({self.rating} stars)"