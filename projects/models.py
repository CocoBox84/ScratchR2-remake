from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    CATEGORY_CHOICES = [
        ("featured", "Featured"),
        ("all", "All"),
        ("animations", "Animations"),
        ("art", "Art"),
        ("games", "Games"),
        ("music", "Music"),
        ("stories", "Stories"),
        ("tutorials", "Tutorials"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="all"
    )


    title = models.CharField(max_length=255, default="Untitled")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    data = models.BinaryField(blank=True, null=True)
    created_at = models.CharField()
    updated_at = models.CharField()
    shared_at = models.CharField()
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    isShared = models.CharField(max_length=5, default="false")
    isTrashed = models.CharField(max_length=5, default="false")

    instructions = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    loves = models.ManyToManyField(User, related_name="loved_projects", blank=True)
    favorites = models.ManyToManyField(User, related_name="favorited_projects", blank=True)
    remixes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    parent = models.ForeignKey("self", null=True, blank=True,
                               related_name="children", on_delete=models.SET_NULL)

    def love_count(self):
        return self.loves.count()

    def favorite_count(self):
        return self.favorites.count()

    def __str__(self):
        return self.title or f"Project {self.id}"

    
class BackpackItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="backpack_items")
    type = models.CharField(max_length=20)  # "sprite", "costume", "sound", "script"
    name = models.CharField(max_length=255, blank=True)
    asset_id = models.CharField(max_length=64, blank=True)  # for md5 assets
    data = models.JSONField(null=True, blank=True)          # for sprite JSON blobs
    scripts = models.JSONField(null=True, blank=True)       # for script block arrays
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        d = {
            "id": self.id,
            "type": self.type,
            "name": self.name,
        }
        if self.asset_id:
            d["md5"] = self.asset_id
        if self.data:
            d["body"] = self.data
        if self.scripts is not None:
            d["scripts"] = self.scripts
        return d

class Message(models.Model):
    MESSAGE_TYPES = [
        ("love", "Love"),
        ("favorite", "Favorite"),
        ("studio_invite", "Studio Invite"),
        ("studio_activity", "Studio Activity"),
        ("forum_post", "Forum Post"),
        ("comment", "Comment"),
        ("remix", "Remix"),
        ("staff_alert", "Scratch Team Alert")
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="actions")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    # Metadata

    title = models.CharField(max_length=255, blank=True)
    text = models.TextField(blank=True)
    link = models.URLField(blank=True)


    def __str__(self):
        return f"{self.actor} {self.type}d {self.project} for {self.recipient}"


from django.contrib.auth.models import User

def unread_messages_count(self):
    return self.messages.filter(read=False).count()

preferred_language = "en"

User.add_to_class("unread_messages_count", property(unread_messages_count))
User.add_to_class("preferred_language", preferred_language)
