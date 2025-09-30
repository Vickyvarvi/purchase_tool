from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import PurchaseRequest, PurchaseOrder
from .forms import ExcelUploadForm, PurchaseRequestForm, PurchaseOrderForm
import pandas as pd


# -------------------- HOME --------------------
def home(request):
    pr_count = PurchaseRequest.objects.count()
    po_count = PurchaseOrder.objects.count()
    return render(request, 'prpo/home.html', {
        'pr_count': pr_count,
        'po_count': po_count,
    })


# -------------------- BULK UPLOAD --------------------
def bulk_upload(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_excel(request.FILES['file'])
            df_cols = {col.lower(): col for col in df.columns}
            created, errors = 0, []

            if form.cleaned_data.get('upload_type') == 'pr':
                mapping = {
                    'pr_number': ['pr_number', 'pr no', 'pr no.', 'pr'],
                    'requested_by': ['requested_by', 'requestor', 'requested by'],
                    'department': ['department'],
                    'item_description': ['description', 'item_description', 'item desc'],
                    'mfr_part_no': ['mfr_part_no', 'mpn', 'part no'],
                    'quantity': ['qty', 'quantity'],
                    'unit': ['unit'],
                    'required_date': ['required_date', 'needed_by', 'required date'],
                    'notes': ['notes']
                }
                for _, row in df.iterrows():
                    data = {}
                    for field, candidates in mapping.items():
                        for cand in candidates:
                            if cand.lower() in df_cols:
                                data[field] = row[df_cols[cand.lower()]]
                                break
                    try:
                        PurchaseRequest.objects.create(**data)
                        created += 1
                    except Exception as e:
                        errors.append(str(e))

            else:  # upload_type == 'po'
                mapping = {
                    'po_number': ['po_number', 'po no', 'po'],
                    'supplier': ['supplier'],
                    'po_date': ['po_date', 'order_date', 'po date'],
                    'item_description': ['description', 'item_description'],
                    'mfr_part_no': ['mfr_part_no', 'mpn'],
                    'quantity': ['qty', 'quantity'],
                    'unit_price': ['unit_price', 'unit price', 'price'],
                    'total_price': ['total_price', 'total']
                }
                for _, row in df.iterrows():
                    data = {}
                    for field, candidates in mapping.items():
                        for cand in candidates:
                            if cand.lower() in df_cols:
                                data[field] = row[df_cols[cand.lower()]]
                                break
                    try:
                        PurchaseOrder.objects.create(**data)
                        created += 1
                    except Exception as e:
                        errors.append(str(e))

            messages.success(request, f'Created {created} records. Errors: {len(errors)}')
            return redirect('home')
    else:
        form = ExcelUploadForm()
    return render(request, 'prpo/bulk_upload.html', {'form': form})


# -------------------- LIST VIEWS --------------------
def pr_list(request):
    qs = PurchaseRequest.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 25)
    page = request.GET.get('page')
    objs = paginator.get_page(page)
    return render(request, 'prpo/list_table.html', {'objects': objs, 'model': 'pr'})


def po_list(request):
    qs = PurchaseOrder.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 25)
    page = request.GET.get('page')
    objs = paginator.get_page(page)
    return render(request, 'prpo/list_table.html', {'objects': objs, 'model': 'po'})


# -------------------- CREATE VIEWS --------------------
def pr_create(request):
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase Request created successfully!')
            return redirect('list_pr')
    else:
        form = PurchaseRequestForm()
    return render(request, 'prpo/pr_single_form.html', {'form': form})


def po_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase Order created successfully!')
            return redirect('list_po')
    else:
        form = PurchaseOrderForm()
    return render(request, 'prpo/po_single_form.html', {'form': form})
