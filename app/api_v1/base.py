from flask import (
    jsonify,
    request,
    current_app,
    abort,
    render_template,
    session,
)
from . import api
from app import models, db
from flask_login import current_user
from app.utils.decorators import login_required
from app.email import send_email
from app.utils.authorizer import Authorizer
from app.utils import misc
import arrow


"""
Helper endpoints
"""


@api.route("/health", methods=["GET"])
def get_health():
    """Check API health status - returns OK if the API is responsive"""
    return jsonify({"message": "ok"})


@api.route("/feature-flags", methods=["GET"])
@login_required
def get_feature_flags():
    """Get list of enabled feature flags for the current application instance"""
    return jsonify(current_app.config["FEATURE_FLAGS"])


@api.route("/users/exist", methods=["POST"])
def does_user_exist():
    """Check if a user exists by email address - useful for validation before user creation"""
    data = request.get_json()
    if not data.get("email"):
        abort(404)
    user = models.User.find_by_email(data.get("email"))
    if not user:
        abort(404)
    return jsonify({"message": True})


@api.route("/email-check", methods=["GET"])
@login_required
def check_email():
    """Test email configuration and send a test email (admin only)"""
    if not current_user.super:
        abort(403)
    link = current_app.config["HOST_NAME"]
    title = f"{current_app.config['APP_NAME']}: Email Check"
    content = "Email health check is successful"
    response = send_email(
        title,
        recipients=[current_user.email],
        text_body=render_template(
            "email/basic_template.txt",
            title=title,
            content=content,
            button_link=link,
        ),
        html_body=render_template(
            "email/basic_template.html",
            title=title,
            content=content,
            button_link=link,
            button_label="Continue",
        ),
        async_send=False,
    )
    return jsonify({"message": "Email health attempt", "success": response})


@api.route("/session", methods=["GET"])
@login_required
def get_session():
    """Get current user session data including tenant context"""
    data = {"tenant-id": session.get("tenant-id")}
    return jsonify(data)


@api.route("/session/<string:id>", methods=["PUT"])
@login_required
def set_session(id):
    """Set active tenant context for current user session - switches user to a different tenant workspace"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    session["tenant-id"] = result["extra"]["tenant"].id
    return jsonify({"message": "ok"})


@api.route("/session/delete", methods=["GET", "DELETE"])
@login_required
def delete_session():
    """Clear all session data and log out current user"""
    session.clear()
    return jsonify({"message": "ok"})


"""
User endpoints
"""


@api.route("/admin/users", methods=["GET"])
@login_required
def get_users():
    """List all users across all tenants (platform admin only) - useful for user management and auditing"""
    Authorizer(current_user).can_user_manage_platform()
    data = []
    for user in models.User.query.all():
        data.append(user.as_dict())
    return jsonify(data)


@api.route("/admin/users", methods=["POST"])
@login_required
def create_admin_user():
    """Create new platform admin user with super privileges - requires existing admin access"""
    Authorizer(current_user).can_user_manage_platform()
    data = request.get_json()

    tenant = models.Tenant.get_default_tenant()
    if not tenant:
        abort(403, "Default tenant not found. Contact your administrator.")

    response, user = tenant.add_member(
        user_or_email=data.get("email"), send_notification=True
    )
    user.super = True
    db.session.commit()

    return jsonify(response)


@api.route("/users/<string:id>", methods=["GET"])
@login_required
def get_user(id):
    """Get detailed information about a specific user by their ID"""
    result = Authorizer(current_user).can_user_manage_user(id)
    return jsonify(result["extra"]["user"].as_dict())


@api.route("/users/<string:uid>", methods=["PUT"])
@login_required
def update_user(uid):
    """Update user details like username, email, and name"""
    result = Authorizer(current_user).can_user_manage_user(uid)
    data = request.get_json()
    user = result["extra"]["user"]

    user.username = data.get("username")
    user.email = data.get("email")
    user.first_name = data.get("first_name")
    user.last_name = data.get("last_name")
    user.license = data.get("license", user.license)
    user.trial_days = int(data.get("trial_days", user.trial_days))

    if current_user.super and "is_active" in data:
        user.is_active = data.get("is_active")
    if current_user.super and "super" in data:
        user.super = data.get("super")
    if current_user.super and "can_user_create_tenant" in data:
        user.can_user_create_tenant = data.get("can_user_create_tenant")
    if current_user.super and "tenant_limit" in data:
        user.tenant_limit = int(data.get("tenant_limit"))

    if data.get("email_confirmed") is True and not current_user.email_confirmed_at:
        user.email_confirmed_at = str(arrow.utcnow)

    if data.get("email_confirmed") is False:
        user.email_confirmed_at = None

    db.session.commit()
    return jsonify({"message": user.as_dict()})


@api.route("/users/<string:id>", methods=["DELETE"])
@login_required
def delete_user(id):
    """Deactivate a user account - sets is_active to false instead of permanently deleting"""
    result = Authorizer(current_user).can_user_manage_user(id)
    result["extra"]["user"].is_active = False
    db.session.commit()
    return jsonify({"message": "ok"})


@api.route("/users/<string:id>/send-confirmation", methods=["POST"])
@login_required
def send_user_confirmation(id):
    """Send email confirmation link to a user who needs to verify their email address"""
    result = Authorizer(current_user).can_user_send_email_confirmation(id)
    result["extra"]["user"].send_email_confirmation()
    return jsonify({"message": "ok"})


@api.route("/users/<string:id>/verify-confirmation-code", methods=["POST"])
@login_required
def verify_user_confirmation(id):
    """Verify user email confirmation code - marks email as confirmed if code matches"""
    result = Authorizer(current_user).can_user_verify_email_confirmation(id)
    data = request.get_json()
    if data.get("code", "").strip() != result["extra"]["user"].email_confirm_code:
        abort(403, "Invalid confirmation code")

    result["extra"]["user"].email_confirmed_at = str(arrow.utcnow())
    db.session.commit()
    return jsonify({"message": "ok"})


@api.route("/users/<string:uid>/password", methods=["PUT"])
@login_required
def change_password(uid):
    """Change user password - validates password complexity and updates hashed password"""
    result = Authorizer(current_user).can_user_manage_user(uid)
    user = result["extra"]["user"]
    data = request.get_json()
    password = data.get("password")
    password2 = data.get("password2")
    if not misc.perform_pwd_checks(password, password_two=password2):
        abort(422, "Invalid password")
    user.set_password(password, set_pwd_change=True)
    db.session.commit()
    return jsonify({"message": "Successfully updated the password"})


@api.route("/token", methods=["GET"])
@login_required
def generate_api_token():
    """Generate API authentication token for programmatic access - default expiration 600 seconds (10 minutes)"""
    expiration = int(request.args.get("expiration", 600))
    token = current_user.generate_auth_token(expiration=expiration)
    return jsonify({"token": token, "expires_in": expiration})


"""
Tenant endpoints
"""


@api.route("/tenants/<string:tid>", methods=["GET"])
@login_required
def get_tenant(tid):
    """Get detailed information about a specific tenant including settings and members"""
    result = Authorizer(current_user).can_user_access_tenant(tid)
    return jsonify(result["extra"]["tenant"].as_dict())


@api.route("/tenants/<string:id>", methods=["DELETE"])
@login_required
def delete_tenant(id):
    """Delete a tenant and all associated data - requires tenant admin privileges"""
    result = Authorizer(current_user).can_user_admin_tenant(id)
    result["extra"]["tenant"].delete()
    return jsonify({"message": "ok"})


@api.route("/tenants/<string:tid>/info", methods=["GET"])
@login_required
def get_tenant_info(tid):
    """Get tenant usage statistics and information including member count and resource limits"""
    result = Authorizer(current_user).can_user_access_tenant(tid)
    return jsonify(result["extra"]["tenant"].get_tenant_info())


@api.route("/tenants/<string:tid>", methods=["PUT"])
@login_required
def update_tenant(tid):
    """Update tenant settings like contact email, approved domains, and authentication options"""
    result = Authorizer(current_user).can_user_admin_tenant(tid)
    tenant = result["extra"]["tenant"]
    data = request.get_json()
    if data.get("contact_email"):
        tenant.contact_email = data.get("contact_email")

    if data.get("magic_link_login") in [True, False]:
        tenant.magic_link_login = data.get("magic_link_login")

    if "approved_domains" in data:
        approved_domains = data.get("approved_domains")
        # Convert to comma sep string
        if isinstance(approved_domains, list):
            tenant.approved_domains = ", ".join(approved_domains)
        elif isinstance(approved_domains, str):
            tenant.approved_domains = approved_domains

    if any(
        key in data for key in ["license", "storage_cap", "user_cap", "project_cap"]
    ):
        Authorizer(current_user).can_user_manage_platform()
        tenant.license = data.get("license", tenant.license)
        tenant.storage_cap = str(data.get("storage_cap", tenant.storage_cap))
        tenant.user_cap = int(data.get("user_cap", tenant.user_cap))
        tenant.project_cap = int(data.get("project_cap", tenant.project_cap))

    db.session.commit()
    return jsonify(result["extra"]["tenant"].as_dict())


@api.route("/tenants", methods=["GET"])
@login_required
def get_tenants():
    """List all tenants the current user has access to - returns tenant details for workspace switching"""
    data = []
    for tenant in current_user.get_tenants():
        data.append(tenant.as_dict())
    return jsonify(data)


@api.route("/tenants", methods=["POST"])
@login_required
def add_tenant():
    """Create a new tenant workspace - requires permission to create tenants"""
    result = Authorizer(current_user).can_user_create_tenants()
    data = request.get_json()
    try:
        tenant = models.Tenant.create(
            current_user,
            data.get("name"),
            data.get("contact_email"),
            approved_domains=data.get("approved_domains"),
            init_data=True,
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    return jsonify(tenant.as_dict())


@api.route("/users/<string:uid>/tenants", methods=["GET"])
@login_required
def get_tenants_for_user(uid):
    """Get list of tenants a specific user belongs to - useful for managing user access"""
    result = Authorizer(current_user).can_user_read_tenants_of_user(uid)
    data = []
    for tenant in result["extra"]["user"].get_tenants():
        data.append({"id": tenant.id, "name": tenant.name})
    return jsonify(data)


@api.route("/tenants/<string:tid>/users", methods=["GET"])
@login_required
def get_users_for_tenant(tid):
    """Get all members of a specific tenant including their roles and permissions"""
    result = Authorizer(current_user).can_user_access_tenant(tid)
    return jsonify(result["extra"]["tenant"].get_members())


@api.route("/users/<string:uid>/tenants/<string:tid>/roles", methods=["GET"])
@login_required
def get_roles_for_user_in_tenant(uid, tid):
    """Get user's roles within a specific tenant - shows permissions and access level"""
    result = Authorizer(current_user).can_user_access_tenant(tid)
    if not (user := models.User.query.get(uid)):
        abort(404)
    return jsonify(user.all_roles_by_tenant(result["extra"]["tenant"]))


@api.route("/users/<string:uid>/tenants/<string:tid>", methods=["PUT"])
@login_required
def update_user_in_tenant(uid, tid):
    """Update user details and roles within a specific tenant - manages user permissions"""
    result = Authorizer(current_user).can_user_manage_user_roles_in_tenant(uid, tid)
    data = request.get_json()

    user = result["extra"]["user"]
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.license = data.get("license", user.license)
    user.trial_days = int(data.get("trial_days", user.trial_days))

    if roles := data.get("roles"):
        result["extra"]["tenant"].patch_roles_for_member(result["extra"]["user"], roles)

    db.session.commit()
    return jsonify({"message": "ok"})


@api.route("/users/<string:uid>/tenants/<string:tid>", methods=["DELETE"])
@login_required
def delete_user_in_tenant(uid, tid):
    """Remove a user from a tenant - revokes their access without deleting the user account"""
    result = Authorizer(current_user).can_user_manage_user_roles_in_tenant(uid, tid)
    result["extra"]["tenant"].remove_member(result["extra"]["user"])
    return jsonify({"message": "ok"})


@api.route("/tenants/<string:id>/users", methods=["POST"])
@login_required
def add_user_to_tenant(id):
    """Add a user to a tenant by email - sends invitation and assigns roles"""
    result = Authorizer(current_user).can_user_admin_tenant(id)
    data = request.get_json()
    response, user = result["extra"]["tenant"].add_member(
        user_or_email=data.get("email"),
        attributes={"roles": data.get("roles", [])},
        send_notification=True,
    )
    return jsonify(response)


@api.route("/tenants/<string:id>/chat", methods=["POST"])
@login_required
def post_ai_conversation(id):
    """Send a message to the AI assistant within a tenant context - enables AI-powered interactions"""
    result = Authorizer(current_user).can_user_chat_in_tenant(id)
    data = request.get_json()
    # print(data.get("messages"))
    return jsonify(
        {"source": "server", "message": "We are still in beta! Coming soon!"}
    )


@api.route("/tenants/<string:tid>/tags", methods=["GET"])
@login_required
def get_tags_for_tenant(tid):
    """Get all tags available in a tenant - tags help categorize and organize resources"""
    result = Authorizer(current_user).can_user_read_tenant(tid)
    data = []
    for tag in result["extra"]["tenant"].tags.all():
        data.append(tag.as_dict())
    return jsonify(data)


@api.route("/tenants/<string:tid>/labels", methods=["GET"])
@login_required
def get_labels_for_tenant(tid):
    """Get all labels available in a tenant - labels provide additional metadata for items"""
    result = Authorizer(current_user).can_user_read_tenant(tid)
    data = []
    for label in result["extra"]["tenant"].labels.all():
        data.append(label.as_dict())
    return jsonify(data)


@api.route("/logs")
@login_required
def get_logs():
    """Get system-wide activity logs (platform admin only) - useful for auditing and troubleshooting"""
    Authorizer(current_user).can_user_manage_platform()
    return jsonify(models.Logs.get(as_dict=True, limit=500))


@api.route("/tenants/<string:id>/logs")
@login_required
def get_logs_for_tenant(id):
    """Get activity logs for a specific tenant - tracks user actions and system events"""
    result = Authorizer(current_user).can_user_access_tenant(id)
    return jsonify(result["extra"]["tenant"].get_logs(as_dict=True, limit=500))
