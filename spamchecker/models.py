from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom manager to handle user creation and superuser creation.
    
    Methods:
        create_user(phone_number, password, **extra_fields):
            Creates and returns a regular user with a phone number and password.
        
        create_superuser(phone_number, password, **extra_fields):
            Creates and returns a superuser with elevated permissions.
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and return a regular user with phone number and password.

        Args:
            phone_number (str): The phone number of the user.
            password (str, optional): The password for the user.
            **extra_fields: Additional fields to be saved with the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the phone number is not provided.
        """
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)  # Encrypts the password
        user.save(using=self._db)  # Saves the user to the database
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and return a superuser with elevated permissions.

        Args:
            phone_number (str): The phone number of the superuser.
            password (str, optional): The password for the superuser.
            **extra_fields: Additional fields to be saved with the superuser.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)  # Superusers should be staff
        extra_fields.setdefault('is_superuser', True)  # Superusers have all permissions
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser):
    """
    Custom user model where phone number is the unique identifier instead of a username.

    Attributes:
        salutation (CharField): The salutation of the user (e.g., Mr., Mrs., Dr.).
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        occupation (CharField): The user's occupation.
        phone_number (CharField): The unique phone number of the user.
        country_code (CharField): The country code associated with the phone number.
        email (EmailField): The email of the user (optional).
        password (CharField): The encrypted password of the user.
        date_joined (DateTimeField): The date and time when the user registered.
    """
    salutation = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    country_code = models.CharField(max_length=5)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Ensure that the user's information is also stored in GlobalContact.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().save(*args, **kwargs)
        global_contact, created = GlobalContact.objects.get_or_create(
            phone_number=self.phone_number,
            defaults={
                'name': f"{self.first_name} {self.last_name}",
                'is_registered_user': True,
                'country_code': self.country_code,
                'email': self.email
            }
        )
        if not created:
            global_contact.name = f"{self.first_name} {self.last_name}"
            global_contact.is_registered_user = True
            global_contact.country_code = self.country_code
            global_contact.email = self.email
            global_contact.user = self  # Link the User to the GlobalContact
            global_contact.save()

    def set_password(self, raw_password):
        """
        Set the user's password using Django's built-in password hasher.

        Args:
            raw_password (str): The raw password to be hashed.
        """
        super().set_password(raw_password)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.country_code} {self.phone_number})"

class GlobalContact(models.Model):
    """
    Centralized contact table to store user and contact information for global access.

    Attributes:
        phone_number (CharField): The unique phone number being tracked.
        name (CharField): The name associated with the phone number.
        country_code (CharField): The country code associated with the phone number.
        is_registered_user (BooleanField): True if the number belongs to a registered user.
        spam_count (IntegerField): The number of times this number has been marked as spam.
        total_reports (IntegerField): The total number of reports for this number.
        email (EmailField): The email associated with the number (if it belongs to a user).
        last_updated (DateTimeField): The last time this record was updated.
        user (ForeignKey): Link to the User table, if the contact is a registered user.
    """
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    country_code = models.CharField(max_length=5)
    is_registered_user = models.BooleanField(default=False)
    spam_count = models.IntegerField(default=0)
    total_reports = models.IntegerField(default=0)
    email = models.EmailField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='global_contacts')

    def spam_likelihood(self):
        """
        Calculate the spam likelihood of this number.

        Returns:
            float: The ratio of spam_count to total_reports.
        """
        if self.total_reports == 0:
            return 0
        return self.spam_count / self.total_reports

    def __str__(self):
        return f"{self.name} ({self.country_code} {self.phone_number})"

class Contact(models.Model):
    """
    Table to store user-specific contacts uploaded from their phonebook.

    Attributes:
        contact_owner (ForeignKey): Reference to the user who owns this contact.
        name (CharField): The name of the contact.
        phone_number (CharField): The phone number of the contact.
        country_code (CharField): The country code associated with the phone number.
        date_added (DateTimeField): The date when the contact was added.
    """
    contact_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    country_code = models.CharField(max_length=5)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.country_code} {self.phone_number})"

class SpamReport(models.Model):
    """
    Table to track spam reports made by users for specific phone numbers.

    Attributes:
        reporter (ForeignKey): The user who reported the spam.
        phone_number (CharField): The phone number being reported as spam.
        country_code (CharField): The country code associated with the phone number.
        reason (CharField): The reason for reporting the number as spam.
        date_reported (DateTimeField): The date when the report was created.
    """
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spam_reports")
    phone_number = models.CharField(max_length=15)
    country_code = models.CharField(max_length=5)
    reason = models.CharField(max_length=255) 
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return a readable representation of the SpamReport.
        """
        return f"Report by {self.reporter} for {self.phone_number} ({self.country_code}) on {self.date_reported}"


