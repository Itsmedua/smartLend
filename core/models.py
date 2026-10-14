from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Applicant(models.Model):
    """One loan application plus the risk result and the officer's decision."""

    DECISION_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("referred", "Referred"),
        ("rejected", "Rejected"),
    ]

    # What the officer types in
    full_name = models.CharField(max_length=120)
    monthly_income = models.PositiveBigIntegerField(
        "Monthly income (PKR)", validators=[MinValueValidator(1)])
    loan_amount = models.PositiveBigIntegerField(
        "Loan amount (PKR)", validators=[MinValueValidator(1)])
    credit_history_years = models.FloatField(
        "Credit history (years)", validators=[MinValueValidator(0)])
    existing_debt = models.PositiveBigIntegerField("Existing debt (PKR)", default=0)
    missed_payments = models.PositiveSmallIntegerField("Missed payments", default=0)
    employment_years = models.FloatField(
        "Years in current job", validators=[MinValueValidator(0)])

    # What the system works out
    risk_probability = models.FloatField(null=True, blank=True)
    risk_label = models.CharField(max_length=20, blank=True)
    explanation = models.JSONField(default=list, blank=True)

    # What the officer decides (this is our audit trail)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, default="pending")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="applicants")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.risk_label or 'not scored'})"

    @property
    def risk_percent(self):
        if self.risk_probability is None:
            return None
        return round(self.risk_probability * 100)
