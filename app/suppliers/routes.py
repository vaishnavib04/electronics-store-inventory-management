
import re

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Supplier
from app.suppliers import suppliers_bp


@suppliers_bp.route("/")
@login_required
def list_suppliers():
    suppliers = db.session.execute(
        db.select(Supplier).order_by(Supplier.name)
    ).scalars().all()

    return render_template(
        "suppliers/list.html",
        suppliers=suppliers,
    )


@suppliers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_supplier():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact_person = request.form.get("contact_person", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        errors = []

        if not name:
            errors.append("Supplier name is required.")
        elif len(name) > 150:
            errors.append("Supplier name must be 150 characters or fewer.")

        if len(contact_person) > 100:
            errors.append("Contact person must be 100 characters or fewer.")

        if len(phone) > 30:
            errors.append("Phone number must be 30 characters or fewer.")
        elif phone and not re.fullmatch(r"[0-9+\-() .]{7,30}", phone):
            errors.append("Enter a valid phone number.")

        if len(email) > 150:
            errors.append("Email must be 150 characters or fewer.")
        elif email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Enter a valid email address.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "suppliers/form.html",
                supplier=None,
                form_data=request.form,
            ), 400

        supplier = Supplier(
            name=name,
            contact_person=contact_person or None,
            phone=phone or None,
            email=email or None,
            address=address or None,
        )

        try:
            db.session.add(supplier)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Unable to save the supplier. Please try again.", "error")
            return render_template(
                "suppliers/form.html",
                supplier=None,
                form_data=request.form,
            ), 500

        flash("Supplier added successfully.", "success")
        return redirect(url_for("suppliers.list_suppliers"))

    return render_template(
        "suppliers/form.html",
        supplier=None,
        form_data={},
    )


@suppliers_bp.route("/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
def edit_supplier(supplier_id):
    supplier = db.get_or_404(Supplier, supplier_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact_person = request.form.get("contact_person", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        errors = []

        if not name:
            errors.append("Supplier name is required.")
        elif len(name) > 150:
            errors.append("Supplier name must be 150 characters or fewer.")

        if len(contact_person) > 100:
            errors.append("Contact person must be 100 characters or fewer.")

        if len(phone) > 30:
            errors.append("Phone number must be 30 characters or fewer.")
        elif phone and not re.fullmatch(r"[0-9+\-() .]{7,30}", phone):
            errors.append("Enter a valid phone number.")

        if len(email) > 150:
            errors.append("Email must be 150 characters or fewer.")
        elif email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Enter a valid email address.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "suppliers/form.html",
                supplier=supplier,
                form_data=request.form,
            ), 400

        supplier.name = name
        supplier.contact_person = contact_person or None
        supplier.phone = phone or None
        supplier.email = email or None
        supplier.address = address or None

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Unable to update the supplier. Please try again.", "error")
            return render_template(
                "suppliers/form.html",
                supplier=supplier,
                form_data=request.form,
            ), 500

        flash("Supplier updated successfully.", "success")
        return redirect(url_for("suppliers.list_suppliers"))

    return render_template(
        "suppliers/form.html",
        supplier=supplier,
        form_data={},
    )
