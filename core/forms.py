from django import forms

from .models import Applicant


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            "full_name",
            "monthly_income",
            "loan_amount",
            "credit_history_years",
            "existing_debt",
            "missed_payments",
            "employment_years",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Give every input Bootstrap's "form-control" look
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["full_name"].widget.attrs["placeholder"] = "Hamza Khan"
        self.fields["credit_history_years"].widget.attrs["step"] = "0.1"
        self.fields["employment_years"].widget.attrs["step"] = "0.1"
