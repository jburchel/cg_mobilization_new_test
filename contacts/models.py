from django.db import models
import logging

logger = logging.getLogger(__name__)

class Contact(models.Model):
   
    STATE = (
        ('al', 'AL'), ('ak', 'AK'), ('az', 'AZ'), ('ar', 'AR'), ('ca', 'CA'),('co', 'CO'),('ct', 'CT'),('de', 'DE'), ('fl', 'FL'), ('ga', 'GA'),
        ('hi', 'HI'), ('id', 'ID'), ('il', 'IL'), ('in', 'IN'), ('ia', 'IA'), ('ks', 'KS'), ('ky', 'KY'), ('la', 'LA'), ('me', 'ME'),
        ('md', 'MD'), ('ma', 'MA'), ('mi', 'MI'), ('mn', 'MN'), ('ms', 'MS'), ('mo', 'MO'), ('mt', 'MT'), ('ne', 'NE'), ('nv', 'NV'),
        ('nh', 'NH'), ('nj', 'NJ'), ('nm', 'NM'), ('ny', 'NY'), ('nc', 'NC'), ('nd', 'ND'), ('oh', 'OH'), ('ok', 'OK'), ('or', 'OR'),
        ('pa', 'PA'), ('ri', 'RI'), ('sc', 'SC'), ('sd', 'SD'), ('tn', 'TN'), ('tx', 'TX'), ('ut', 'UT'), ('vt', 'VT'), ('va', 'VA'),
        ('wa', 'WA'), ('wv', 'WV'), ('wi', 'WI'), ('wy', 'WY'),('dc', 'DC')
    )
    
    PREFERRED_CONTACT_METHODS = (
        ('email', 'Email'),('phone', 'Phone'),('text', 'Text'),('Facebook Messanger', 
        'Facebook Messanger'),('whatsapp', 'Whatsapp'),('groupme', 'Groupme'),('signal', 'Signal'),('other', 'Other')
    )
    
    church_name = models.CharField(max_length=100, null=True, blank=True)  
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='contact_images/', null=True, blank=True)
    preferred_contact_method = models.CharField(max_length=100, choices=PREFERRED_CONTACT_METHODS)
    phone = models.CharField(max_length=20)
    email = models.EmailField()    
    street_address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, choices=STATE, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    initial_notes = models.TextField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True,null=True, blank=True)
    date_modified = models.DateField(auto_now=True,null=True, blank=True)

    def get_name(self):
        logger.debug(f"get_name called for contact {self.id}")
        logger.debug(f"Has 'church' attribute: {hasattr(self, 'church')}")
        logger.debug(f"Has 'people' attribute: {hasattr(self, 'people')}")
        
        if hasattr(self, 'church'):
            name = self.church.church_name
        elif hasattr(self, 'people'):
            name = f"{self.people.first_name} {self.people.last_name}".strip()
        else:
            name = self.church_name or f"{self.first_name} {self.last_name}".strip() or "Unnamed Contact"
        
        logger.debug(f"Returned name: {name}")
        return name

    def __str__(self):
        return self.get_name()
    
class Church(Contact):
    COLOR = (
        ('RED', 'RED'),('YELLOW', 'YELLOW'), ('BLUE', 'BLUE'),('GREEN', 'GREEN')
    )
    
    CHURCH_PIPELINE_CHOICES = (
        ('UNKNOWN', 'UNKNOWN'), ('COLD UNCONTACTED', 'COLD UNCONTACTED'), ('COLD CONTACTED', 'COLD CONTACTED'),
        ('REPEATED FOLLOWUP', 'REPEATED FOLLOWUP'), ('WARM UNCONTACTED', 'WARM UNCONTACTED'), ('WARM CONTACTED', 'WARM CONTACTED'),
        ('MET', 'MET'), ('MISSION VISION', 'MISSION VISION'), ('EN42', 'EN42')
    )
    
    PRIORITY = (
        ('URGENT', 'URGENT'), ('HIGH', 'HIGH'), ('MEDIUM', 'MEDIUM'), ('LOW', 'LOW')
    )
    
    ASSIGNED_TO_CHOICES = (
        ('BILL JONES', 'BILL JONES'), ('JASON MODOMO', 'JASON MODOMO'), ('KEN KATAYAMA', 'KEN KATAYAMA'), ('MATTHEW RULE', 'MATTHEW RULE'),
        ('CHIP ATKINSON', 'CHIP ATKINSON'), ('RACHEL LIVELY', 'RACHEL LIVELY'), ('JIM BURCHEL', 'JIM BURCHEL'), ('JILL WALKER', 'JILL WALKER'),
        ('KARINA RAMPIN', 'KARINA RAMPIN'), ('UNASSIGNED', 'UNASSIGNED')        
    )
    
    SOURCE = (
        ('WEBFORM', 'WEBFORM'), ('INCOMING CALL', 'INCOMING CALL'), ('EMAIL', 'EMAIL'), ('SOCIAL MEDIA', 'SOCIAL MEDIA'),
        ('COLD CALL', 'COLD CALL'),('PERSPECTIVES', 'PERSPECTIVES'),('REFERAL', 'REFERAL'),('OTHER', 'OTHER'), ('UNKNOWN', 'UNKNOWN')
    )
    
    virtuous = models.BooleanField(default=False)    
    senior_pastor_first_name = models.CharField(max_length=100)
    senior_pastor_last_name = models.CharField(max_length=100)
    senior_pastor_phone = models.CharField(max_length=20, null=True, blank=True)
    senior_pastor_email = models.EmailField(null=True, blank=True)
    missions_pastor_first_name = models.CharField(max_length=100, null=True, blank=True)
    missions_pastor_last_name = models.CharField(max_length=100, null=True, blank=True)
    mission_pastor_phone = models.CharField(max_length=20, null=True, blank=True)
    mission_pastor_email = models.EmailField(null=True, blank=True)
    primary_contact_first_name = models.CharField(max_length=100)
    primary_contact_last_name = models.CharField(max_length=100)
    primary_contact_phone = models.CharField(max_length=20)
    primary_contact_email = models.EmailField()
    website = models.URLField(null=True, blank=True)
    denomination = models.CharField(max_length=100, null=True, blank=True)
    congregation_size = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=10, choices=COLOR, default='GREEN')
    church_pipeline = models.CharField(max_length=100, choices=CHURCH_PIPELINE_CHOICES, default='UNKNOWN')
    priority = models.CharField(max_length=10, choices=PRIORITY, default='MEDIUM')
    assigned_to = models.CharField(max_length=100, choices=ASSIGNED_TO_CHOICES, default='UNASSIGNED')
    source = models.CharField(max_length=100, choices=SOURCE, default='UNKNOWN')
    referred_by = models.CharField(max_length=100, null=True, blank=True)    
    info_given = models.TextField(null=True, blank=True)
    reason_closed = models.TextField(null=True, blank=True)  
    year_founded = models.IntegerField(null=True, blank=True)
    date_closed = models.DateField(null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.church_name}".strip()
    
    class Meta:
        verbose_name = "Church"
        verbose_name_plural = "Churches"

class People(Contact):
    MARITAL_STATUS = (
        ('single', 'Single'),('married', 'Married'),('divorced', 'Divorced'),('widowed', 'Widowed'),('separated', 'Separated'), ('unknown', 'Unknown'),
    )
    
    COLOR = (
        ('red', 'Red'),('yellow', 'Yellow'),('blue', 'Blue'),('green', 'Green'),('unknown', 'Unknown'),
    )
    
    PEOPLE_PIPELINE = (
        ('contacted','Contacted'), ('mission-vision', 'Mission Vision'),('conversations', 'Conversations'),
        ('potential-recruit', 'Potential Recruit'),('handed-off', 'Handed Off')
    )
    
    PRIORITY = (
        ('urgent', 'Urgent'),('high', 'High'), ('medium', 'Medium'), ('low', 'Low')
    )
    
    ASSIGNED_TO = (
        ('BILL JONES', 'BILL JONES'), ('JASON MODOMO', 'JASON MODOMO'), ('KEN KATAYAMA', 'KEN KATAYAMA'), ('MATTHEW RULE', 'MATTHEW RULE'),
        ('CHIP ATKINSON', 'CHIP ATKINSON'), ('RACHEL LIVELY', 'RACHEL LIVELY'), ('JIM BURCHEL', 'JIM BURCHEL'), ('JILL WALKER', 'JILL WALKER'),
        ('KARINA RAMPIN', 'KARINA RAMPIN'), ('UNASSIGNED', 'UNASSIGNED')        
    )
    
    SOURCE = (
        ('WEBFORM', 'WEBFORM'), ('INCOMING CALL', 'INCOMING CALL'), ('EMAIL', 'EMAIL'), ('SOCIAL MEDIA', 'SOCIAL MEDIA'),
        ('COLD CALL', 'COLD CALL'),('PERSPECTIVES', 'PERSPECTIVES'),('REFERAL', 'REFERAL'),('OTHER', 'OTHER'), ('UNKNOWN', 'UNKNOWN')
    )
    
    affiliated_church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Affiliated Church")
    virtuous = models.BooleanField(default=False)
    home_country = models.CharField(max_length=100, null=True, blank=True)
    spouse_recruit = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=100, choices=MARITAL_STATUS, null=True, blank=True)
    color = models.CharField(max_length=100, choices=COLOR, null=True, blank=True)
    people_pipeline = models.CharField(max_length=100, choices=PEOPLE_PIPELINE, null=True, blank=True)
    priority = models.CharField(max_length=100, choices=PRIORITY, null=True, blank=True)
    assigned_to = models.CharField(max_length=100, choices=ASSIGNED_TO, null=True, blank=True)
    source = models.CharField(max_length=100, choices=SOURCE, null=True, blank=True)
    referred_by = models.CharField(max_length=100, null=True, blank=True)
    info_given = models.TextField(null=True, blank=True)
    desired_service = models.TextField(null=True, blank=True)
    reason_closed = models.TextField(null=True, blank=True)
    date_closed = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() 
        
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Person'
        verbose_name_plural = 'People'
