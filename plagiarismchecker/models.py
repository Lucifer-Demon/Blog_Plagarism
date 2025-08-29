# D:\Program\Plagiarsim-Checker-main\plagiarismchecker\models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings # Important
from django.contrib.auth.models import User
from django.utils import timezone

# My custom user model!
# This inherits from Django's built-in AbstractUser,
# giving me all the standard user fields (username, password, etc.)
# and allowing me to add my own.
class CustomUser(AbstractUser):
    # I already included first_name, last_name, and email in my CustomUserCreationForm,
    # so I'm explicitly defining them here to make sure they're part of my CustomUser model.
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Add related_name and related_query_name to resolve clashes
    # These fields are inherited from AbstractUser, but we explicitly define them
    # here to set unique related_name/related_query_name for reverse relationships.
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="plagiarismchecker_customuser_groups", # Unique related_name for groups
        related_query_name="plagiarismchecker_customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="plagiarismchecker_customuser_user_permissions", # Unique related_name for user_permissions
        related_query_name="plagiarismchecker_customuser_permission",
    )

    def __str__(self):
        #represent the user when you see them in the Django admin
        return self.username

# My existing model for reference documents
class ReferenceDocument(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True) # Make content optional as it will be filled from file
    document_file = models.FileField(upload_to='documents/', blank=True, null=True) # New field for file uploads

    def __str__(self):
        return self.title

class PlagiarismHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query_text = models.TextField()
    result_percentage = models.FloatField()
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} checked at {self.checked_at}"

# A document that belongs to a user-defined training dataset
class DatasetDocument(models.Model):
    dataset_name = models.CharField(max_length=100, default='default', db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    source_file = models.FileField(upload_to='dataset_docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.dataset_name}] {self.title}"


class TrainedDatasetModel(models.Model):
    dataset_name = models.CharField(max_length=100, unique=True)
    vectorizer_path = models.CharField(max_length=500)
    matrix_path = models.CharField(max_length=500)
    doc_index_path = models.CharField(max_length=500)
    trained_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Model({self.dataset_name}) @ {self.trained_at}"

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('pending', 'Pending Review'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey('BlogCategory', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            self.slug = base_slug
            
            # Check if slug already exists and make it unique
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
                
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            self.slug = base_slug
            
            # Check if slug already exists and make it unique
            counter = 1
            while BlogCategory.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
