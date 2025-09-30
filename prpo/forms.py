from django import forms
from .models import PurchaseRequest, PurchaseOrder


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = '__all__'
        widgets = {
        'required_date': forms.DateInput(attrs={'type': 'date'})
    }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        widgets = {
        'po_date': forms.DateInput(attrs={'type': 'date'})
}


class ExcelUploadForm(forms.Form):
    file = forms.FileField()
    model_choice = forms.ChoiceField(choices=(('pr', 'PurchaseRequest'), ('po', 'PurchaseOrder')))