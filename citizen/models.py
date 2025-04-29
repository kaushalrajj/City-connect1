from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your models here.

class ward_no(models.Model):
    name = models.CharField(max_length=3)

    def __str__(self):
        return self.name

class dept(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class status(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    host = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    dept = models.ForeignKey(dept, on_delete = models.SET_NULL, null = True)
    ward_no = models.ForeignKey(ward_no, on_delete = models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    created = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(status, on_delete= models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        # Custom logic before saving
        if not self.status:
            self.status = status.objects.get(name="Pending")  # Set default status if not provided
        super(Post, self).save(*args, **kwargs)

    def get_vote_count(self):
        """Get the total vote count (upvotes - downvotes)"""
        votes = self.votes.aggregate(total=Sum('value'))
        return votes['total'] or 0

    def get_upvote_count(self):
        """Get the count of upvotes"""
        return self.votes.filter(value=1).count()

    def get_downvote_count(self):
        """Get the count of downvotes"""
        return self.votes.filter(value=-1).count()

class Vote(models.Model):
    """Model to store votes on posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(default=0)  # 1 for upvote, -1 for downvote
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only vote once per post
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username}'s vote on post {self.post.id}"