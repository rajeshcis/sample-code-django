"""Django model."""

import logging
from datetime import datetime
from decimal import Decimal
import os
import twitter
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from form_utils.fields import FakeEmptyFieldFile
from .models import ImageSpecField
from .processors import ResizeToFill
from modeltranslation.utils import build_localized_fieldname

from .managers import IPManager
from .utils import get_logo_path
from .uploads import move_file
from .validators import validate_uri

logger = logging.getLogger(settings.CUSTOM_LOGGER)

IP_I18N_FIELDS = ('company_name', 'address1', 'address2', 'contact_name', 'description')


class IP(models.Model):
    """IP model with custom model manager and various properties."""

    objects = IPManager()

    I18N_FIELDS = IP_I18N_FIELDS

    company_name = models.CharField(max_length=128, verbose_name=_("Company Name"))
    disabled = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    address1 = models.CharField(max_length=100, verbose_name=_("Address1"))
    address2 = models.CharField(max_length=100, verbose_name=_("Address2"))
    email = models.EmailField()
    contact_name = models.CharField(max_length=50, verbose_name=_("Contact Name"))
    contact_number = models.CharField(max_length=30)

    sms_contact = models.CharField(max_length=30, blank=True, null=True,
                                   verbose_name=_("SMS Contact"))

    logo = models.ImageField(upload_to=get_logo_path)
    logo_m = ImageSpecField(
        [ResizeToFill(180, 180)],
        source='logo',
        format='JPEG',
        options={'quality': 90},)

    description = models.TextField(max_length=3072, verbose_name=_("Description"))
    fb_fan_page = models.URLField(blank=True, null=True)
    facebook_username = models.CharField(max_length=100, blank=True, null=True)
    twitter_username = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    post_url = models.SlugField(max_length=100, blank=True, null=True, validators=[validate_uri])

    managers = models.ManyToManyField(User, blank=True, related_name='ip_manages')

    default_ticket_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                             validators=[MinValueValidator(Decimal('0.0'))],
                                             verbose_name=_("Fixed fee per ticket"))
    default_ticket_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                        validators=[
                                                            MinValueValidator(Decimal('0.0')),
                                                            MaxValueValidator(Decimal('100.0'))
                                                        ],
                                                        verbose_name=_("% of ticket sales charged"))

    class Meta:
        """Meta objects."""

        ordering = map(lambda (lang_code, __): build_localized_fieldname('company_name', lang_code),
                       settings.LANGUAGES)

    def __unicode__(self):
        """Return company name for object."""
        return self.company_name

    @models.permalink
    def get_absolute_url(self):
        """Return absolute url."""
        if self.post_url:
            return 'vanity_url_catcher', (), {'event_slug': self.post_url}
        return 'ip_detail', (), {'ip_id': self.id}

    @property
    def valid_events(self):
        """Return valid events."""
        return self.events.filter(session_earliest_starts__gte=datetime.now())

    @property
    def logo_m_url(self):
        """Return logo url."""
        return getattr(self.logo_m, 'url', None)

    @property
    def get_twitter_feed(self):
        """Return twitter feeds."""
        tweets = cache.get("tweets_%s" % self.id)
        if tweets:
            return tweets
        if not self.twitter_username:
            return None
        try:
            tweets = twitter.Api().GetUserTimeline(self.twitter_username)
            if tweets:
                tweets = tweets[:settings.TWITTER_BLOCK_ITEMS]
                cache.set("tweets_%s" % self.id, tweets, settings.TWITTER_BLOCK_CACHE_EXPIRY)
                return tweets
        except:
            pass
        return None


@receiver(post_save, sender=IP)
def move_ip_logo(sender, instance, **kwargs):
    """Post save signal for move ip logo."""
    if instance.id and not isinstance(instance.logo, FakeEmptyFieldFile) and instance.logo:
        segments = instance.logo.name.split(os.sep)
        if segments[0] != 'ip':
            move_file(move_ip_logo, IP, sender, instance, 'logo')


@receiver(post_save, sender=IP)
def invalidate_ips_cache(sender, instance, **kwargs):
    """Post save signal for invalidate."""
    from common.utils import cache_utils
    cache_utils.invalidate_ip(instance.id)
