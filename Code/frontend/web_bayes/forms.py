from django.forms import *

from models import *

class EdgeForm(ModelForm):
    class Meta:
        model = Edge
    
    
