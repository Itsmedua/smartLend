from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ApplicantForm
from .ml import predict_risk
from .models import Applicant


@login_required
def dashboard(request):
    stats = Applicant.objects.aggregate(
        total=Count("id"),
        high_risk=Count("id", filter=Q(risk_label="High risk")),
        pending=Count("id", filter=Q(decision="pending")),
    )
    recent = Applicant.objects.select_related("created_by")[:5]
    return render(request, "core/dashboard.html", {"stats": stats, "recent": recent})


@login_required
def applicant_create(request):
    if request.method == "POST":
        form = ApplicantForm(request.POST)
        if form.is_valid():
            applicant = form.save(commit=False)
            applicant.created_by = request.user

            # Ask the model for the risk score and the "why"
            result = predict_risk(
                monthly_income=applicant.monthly_income,
                loan_amount=applicant.loan_amount,
                credit_history_years=applicant.credit_history_years,
                existing_debt=applicant.existing_debt,
                missed_payments=applicant.missed_payments,
                employment_years=applicant.employment_years,
            )
            applicant.risk_probability = result["probability"]
            applicant.risk_label = result["label"]
            applicant.explanation = result["explanation"]
            applicant.save()
            return redirect("applicant_result", pk=applicant.pk)
    else:
        form = ApplicantForm()
    return render(request, "core/applicant_form.html", {"form": form})


@login_required
def applicant_result(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    return render(request, "core/result.html", {"applicant": applicant})


@login_required
def applicant_list(request):
    applicants = Applicant.objects.select_related("created_by")
    query = request.GET.get("q", "").strip()
    if query:
        applicants = applicants.filter(full_name__icontains=query)
    return render(request, "core/applicant_list.html",
                  {"applicants": applicants, "query": query})


@login_required
@require_POST
def applicant_decide(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    decision = request.POST.get("decision")
    allowed = {"approved", "referred", "rejected"}
    if decision in allowed:
        applicant.decision = decision
        applicant.decided_at = timezone.now()
        applicant.save(update_fields=["decision", "decided_at"])
        messages.success(request, f"{applicant.full_name}: marked as {decision}.")
    else:
        messages.error(request, "That decision isn't valid.")
    return redirect("applicant_result", pk=applicant.pk)
