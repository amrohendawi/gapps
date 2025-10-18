from flask import (
    jsonify,
    request,
)
from . import api
from app.models import *
from flask_login import current_user
from app.utils.authorizer import Authorizer
from app.utils.decorators import login_required


@api.route("/tenants/<string:id>/vendors", methods=["GET"])
@login_required
def get_vendors(id):
    """Get all vendors for a tenant - list third-party service providers and suppliers"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    vendors = result["extra"]["tenant"].vendors.all()
    return jsonify([vendor.as_dict() for vendor in vendors])


@api.route("/vendors/<string:id>", methods=["GET"])
@login_required
def get_vendor(id):
    """Get detailed information about a vendor - retrieve vendor profile and metadata"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    return jsonify(vendor.as_dict())


@api.route("/tenants/<string:id>/vendors", methods=["POST"])
@login_required
def create_vendor(id):
    """Create a new vendor - add third-party supplier or service provider to tenant"""
    result = Authorizer(current_user).can_user_manage_tenant(id)
    data = request.get_json()
    vendor = Vendor(
        name=data.get("name"),
        description=data.get("description"),
        contact_email=data.get("contact_email"),
        vendor_contact_email=data.get("vendor_contact_email"),
        location=data.get("location"),
        criticality=data.get("criticality"),
        review_cycle=int(data.get("review_cycle", 12)),
        disabled=data.get("disabled", False),
        notes=data.get("notes"),
        start_date=data.get("start_date"),
    )
    result["extra"]["tenant"].vendors.append(vendor)
    db.session.commit()
    return jsonify(vendor.as_dict())


@api.route("/vendors/<string:id>", methods=["PUT"])
@login_required
def update_vendor(id):
    """Update vendor information - modify vendor details, status, contacts, or criticality"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    data = request.get_json()
    for field in [
        "description",
        "status",
        "contact_email",
        "vendor_contact_email",
        "location",
        "start_date",
        "end_date",
        "criticality",
        "review_cycle",
        "notes",
    ]:
        setattr(vendor, field, data.get(field))
    db.session.commit()
    return jsonify(vendor.as_dict())


@api.route("/vendors/<string:id>/applications", methods=["GET"])
@login_required
def get_vendor_applications(id):
    """Get all applications provided by a vendor - list software/services from this vendor"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    return jsonify([application.as_dict() for application in vendor.apps.all()])


@api.route("/vendors/<string:id>/applications", methods=["POST"])
@login_required
def create_vendor_application(id):
    """Create a new application for a vendor - add software or service provided by vendor"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    data = request.get_json()
    app = vendor.create_app(
        name=data.get("name"),
        description=data.get("description"),
        contact_email=data.get("contact_email"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        criticality=data.get("criticality"),
        review_cycle=data.get("review_cycle"),
        notes=data.get("notes"),
        category=data.get("category"),
        business_unit=data.get("business_unit"),
        is_on_premise=data.get("is_on_premise"),
        is_saas=data.get("is_saas"),
        owner_id=current_user.id,
    )
    return jsonify(app.as_dict())


@api.route("/vendors/<string:id>/categories", methods=["GET"])
@login_required
def get_vendor_categories(id):
    """Get all categories for vendor's applications - list app categories used by this vendor"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    return jsonify(vendor.get_categories())


@api.route("/vendors/<string:id>/assessments", methods=["GET"])
@login_required
def get_vendor_assessments(id):
    """Get all assessments for a vendor - list security assessments and questionnaires"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    return jsonify([assessment.as_dict() for assessment in vendor.get_assessments()])


@api.route("/vendors/<string:id>/bus", methods=["GET"])
@login_required
def get_vendor_business_units(id):
    """Get all business units for vendor - list organizational units using this vendor"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    return jsonify(vendor.get_bus())


@api.route("/tenants/<string:id>/vendors", methods=["GET"])
@login_required
def get_vendors_for_tenant(id):
    """Get all vendors for a tenant - list all third-party suppliers (same as get_vendors)"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    vendors = Vendor.query.filter(
        Vendor.tenant_id == result["extra"]["tenant"].id
    ).all()
    return jsonify([vendor.as_dict() for vendor in vendors])


@api.route("/tenants/<string:id>/applications", methods=["GET"])
@login_required
def get_apps_for_tenant(id):
    """Get all applications for a tenant - list all software and services across all vendors"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    applications = VendorApp.query.filter(
        VendorApp.tenant_id == result["extra"]["tenant"].id
    ).all()
    return jsonify([application.as_dict() for application in applications])


@api.route("/tenants/<string:id>/assessments", methods=["GET"])
@login_required
def get_assessments_for_tenant(id):
    """Get all assessments for a tenant - list all vendor security assessments"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    assessments = Assessment.query.filter(
        Assessment.tenant_id == result["extra"]["tenant"].id
    ).all()
    return jsonify([assessment.as_dict() for assessment in assessments])


@api.route("/tenants/<string:id>/risks", methods=["GET"])
@login_required
def get_risks_for_tenant(id):
    """Get all risks for a tenant - list risk register entries"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    data = []
    for risk in RiskRegister.query.filter(RiskRegister.tenant_id == id).all():
        data.append(risk.as_dict())
    return jsonify(data)


@api.route("/vendors/<string:id>/notes", methods=["PUT"])
@login_required
def update_notes_for_vendor(id):
    """Update notes for a vendor - add or modify internal vendor documentation"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    vendor = result["extra"]["vendor"]
    data = request.get_json()
    vendor.notes = data.get("data")
    db.session.commit()
    return jsonify(vendor.as_dict())


@api.route("/vendors/<string:id>/assessments", methods=["POST"])
@login_required
def create_assessment_for_vendor(id):
    """Create a new assessment for a vendor - initiate security questionnaire or review"""
    result = Authorizer(current_user).can_user_access_vendor(id)
    data = request.get_json()

    assessment = result["extra"]["vendor"].create_assessment(
        name=data.get("name"),
        description=data.get("description"),
        due_date=data.get("due_date"),
        clone_from=data.get("clone_from"),
        owner_id=current_user.id,
    )
    return jsonify(assessment.as_dict())


@api.route("/applications/<string:id>", methods=["PUT"])
@login_required
def update_application(id):
    """Update application details - modify vendor application properties"""
    result = Authorizer(current_user).can_user_access_application(id)
    app = result["extra"]["application"]
    data = request.get_json()
    for key, value in data.items():
        setattr(app, key, value)
    db.session.commit()
    return jsonify(app.as_dict())


@api.route("/tenants/<string:id>/risks", methods=["POST"])
@login_required
def create_risk(id):
    """Create a new risk - add entry to risk register"""
    result = Authorizer(current_user).can_user_manage_tenant(id)
    data = request.get_json()
    risk = result["extra"]["tenant"].create_risk(
        title=data.get("title"),
        description=data.get("description"),
        remediation=data.get("remediation"),
        tags=data.get("tags"),
        assignee=data.get("assignee"),
        enabled=data.get("enabled"),
        status=data.get("status"),
        risk=data.get("risk"),
        priority=data.get("priority"),
        vendor_id=data.get("vendor_id"),
    )

    db.session.add(risk)
    db.session.commit()
    return jsonify(risk.as_dict())


@api.route("/tenants/<string:tid>/risks/<string:rid>", methods=["PUT"])
@login_required
def update_risk(tid, rid):
    """Update risk details - modify risk register entry"""
    result = Authorizer(current_user).can_user_manage_risk(rid)
    data = request.get_json()
    risk = result["extra"]["risk"]

    # Update the risk using the model's update method
    print(data)
    risk.update(**data)

    # Add audit log entry
    risk.tenant.add_log(
        message=f"Updated risk: {risk.title}",
        namespace="risks",
        action="update",
        user_id=current_user.id,
    )

    return jsonify(risk.as_dict())


@api.route("/tenants/<string:tid>/risks/<string:rid>", methods=["DELETE"])
@login_required
def delete_risk(tid, rid):
    """Delete a risk - remove entry from risk register"""
    result = Authorizer(current_user).can_user_manage_risk(rid)
    risk = result["extra"]["risk"]
    db.session.delete(risk)
    db.session.commit()
    return jsonify({"message": "ok"})


@api.route("/tenants/<string:id>/risk-managers", methods=["PUT"])
@login_required
def set_risk_managers_for_tenant(id):
    """Set risk managers for tenant - assign users who can manage risks"""
    result = Authorizer(current_user).can_user_manage_tenant(id)
    tenant = result["extra"]["tenant"]
    data = request.get_json()

    # remove all risk managers
    mappings = UserRole.get_mappings_for_role_in_tenant("riskmanager", tenant.id)
    for mapping in mappings:
        db.session.delete(mapping)
    db.session.commit()

    for email in data:
        if user := User.find_by_email(email):
            current_roles = tenant.get_roles_for_member(user)
            if "riskmanager" not in current_roles:
                current_roles.append("riskmanager")
                tenant.set_roles_for_user(user, list_of_role_names=current_roles)
    return jsonify({"message": "ok"})


@api.route("/tenants/<string:id>/risk-viewers", methods=["PUT"])
@login_required
def set_risk_viewers_for_tenant(id):
    """Set risk viewers for tenant - assign users who can view (not edit) risks"""
    result = Authorizer(current_user).can_user_manage_tenant(id)
    tenant = result["extra"]["tenant"]
    data = request.get_json()

    # remove all risk viewers
    mappings = UserRole.get_mappings_for_role_in_tenant("riskviewer", tenant.id)
    for mapping in mappings:
        db.session.delete(mapping)
    db.session.commit()

    for email in data:
        if user := User.find_by_email(email):
            current_roles = tenant.get_roles_for_member(user)
            if "riskviewer" not in current_roles:
                current_roles.append("riskviewer")
                tenant.set_roles_for_user(user, list_of_role_names=current_roles)
    return jsonify({"message": "ok"})


@api.route("/tenants/<string:id>/vendors", methods=["PUT"])
@login_required
def set_vendors_for_tenant(id):
    """Set vendor users for tenant - assign users with vendor role (external collaborators)"""
    result = Authorizer(current_user).can_user_manage_tenant(id)
    tenant = result["extra"]["tenant"]
    data = request.get_json()

    # remove all risk vendors
    mappings = UserRole.get_mappings_for_role_in_tenant("vendor", tenant.id)
    for mapping in mappings:
        db.session.delete(mapping)
    db.session.commit()

    for email in data:
        if user := User.find_by_email(email):
            tenant.set_roles_for_user(user, list_of_role_names=["vendor"])
    return jsonify({"message": "ok"})
