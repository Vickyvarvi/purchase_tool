from django.db import models

class PurchaseRequest(models.Model):
    # General Info
    plant = models.CharField(max_length=100)
    storage_location = models.CharField(max_length=100, blank=True, null=True)
    pr_number = models.CharField(max_length=50, unique=True)  # Auto/Text unique ID
    pr_date = models.DateField()
    requested_by = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    priority = models.CharField(
        max_length=20,
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Urgent", "Urgent")],
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=[("Draft", "Draft"), ("Submitted", "Submitted"), ("Approved", "Approved"), ("Rejected", "Rejected")],
        default="Draft"
    )

    # Item Details
    item_description = models.TextField()
    item_code = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    uom = models.CharField(max_length=20)  # pcs, kg, box, etc.
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    estimated_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    currency = models.CharField(
        max_length=10,
        choices=[("USD", "USD"), ("INR", "INR"), ("EUR", "EUR"), ("GBP", "GBP")],
        default="USD"
    )

    # Supplier Details
    preferred_supplier = models.CharField(max_length=100, blank=True, null=True)
    supplier_part_number = models.CharField(max_length=100, blank=True, null=True)

    # Delivery Info
    delivery_date = models.DateField()
    delivery_address = models.TextField()

    # Budget & Justification
    budget_code = models.CharField(max_length=50)
    justification = models.TextField()
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)

    # Approval Info
    approver = models.CharField(max_length=100)
    approval_status = models.CharField(
        max_length=20,
        choices=[("Approved", "Approved"), ("Rejected", "Rejected"), ("Pending", "Pending")],
        default="Pending"
    )
    approval_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # Audit trail
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-calculate Estimated Total = Quantity × Estimated Unit Price"""
        if self.estimated_unit_price:
            self.estimated_total = self.quantity * self.estimated_unit_price
        else:
            self.estimated_total = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PR-{self.pr_number} | {self.item_description[:30]}"


class PurchaseOrder(models.Model):
    # --- General Info ---
    po_number = models.CharField(max_length=50, unique=True)  # Auto/manual unique ID
    po_date = models.DateField()
    buyer_name = models.CharField(max_length=100)
    buyer_department = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("Draft", "Draft"), ("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected"), ("Sent", "Sent")],
        default="Draft"
    )
    currency = models.CharField(
        max_length=10,
        choices=[("USD", "USD"), ("INR", "INR"), ("EUR", "EUR"), ("GBP", "GBP")],
        default="USD"
    )
    po_reference_document = models.FileField(upload_to="po_references/", blank=True, null=True)

    # --- Supplier Info ---
    supplier_name = models.CharField(max_length=100)
    supplier_contact_person = models.CharField(max_length=100, blank=True, null=True)
    supplier_email = models.EmailField()
    supplier_phone = models.CharField(max_length=50, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)

    # --- Item / Line Details ---
    item_no = models.CharField(max_length=50)
    item_description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    uom = models.CharField(max_length=20)  # pcs, kg, meters
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    item_currency = models.CharField(
        max_length=10,
        choices=[("USD", "USD"), ("INR", "INR"), ("EUR", "EUR"), ("GBP", "GBP")],
        default="USD"
    )

    # --- Delivery Info ---
    delivery_date_expected = models.DateField()
    delivery_address = models.TextField()
    inco_terms = models.CharField(
        max_length=20,
        choices=[("FOB", "FOB"), ("CIF", "CIF"), ("EXW", "EXW")],
        blank=True, null=True
    )
    delivery_method = models.CharField(
        max_length=50,
        choices=[("Courier", "Courier"), ("Freight", "Freight"), ("Air", "Air"), ("Sea", "Sea")],
        blank=True, null=True
    )

    # --- Payment & Terms ---
    payment_terms = models.CharField(max_length=50)  # e.g. Net 30, Advance
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    # --- Approval & Workflow ---
    approved_by = models.CharField(max_length=100)
    approval_status = models.CharField(
        max_length=20,
        choices=[("Approved", "Approved"), ("Rejected", "Rejected"), ("Pending", "Pending")],
        default="Pending"
    )
    approval_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # --- Notes & Attachments ---
    attachments = models.FileField(upload_to="po_attachments/", blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    supplier_notes = models.TextField(blank=True, null=True)

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-calculate totals: Total Price per line and Total PO Amount"""
        self.total_price = self.quantity * self.unit_price

        base_total = self.total_price
        if self.tax_amount:
            base_total += self.tax_amount
        if self.discount:
            base_total -= self.discount

        self.total_amount = base_total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO-{self.po_number} | {self.supplier_name} | {self.item_description[:25]}"


# Create your models here.
