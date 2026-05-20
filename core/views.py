from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelform_factory
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Announcement, AuditLog, CertificateRequest, Complaint, Feedback, Household, Resident


SYSTEM_NAME = "Brgy San Isidro Surigao City, Surigao del Norte, Philippines Information Management System"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@12345"

ResidentForm = modelform_factory(
    Resident,
    fields=[
        "first_name",
        "middle_name",
        "last_name",
        "birthdate",
        "address",
        "purok",
        "civil_status",
        "occupation",
        "contact_number",
        "is_male",
        "is_senior_citizen",
        "is_pwd",
        "is_registered_voter",
        "photo",
        "household",
    ],
)
HouseholdForm = modelform_factory(Household, fields=["house_number", "purok", "family_head", "address"])
AnnouncementForm = modelform_factory(Announcement, fields=["title", "category", "message", "is_published"])
CertificateForm = modelform_factory(CertificateRequest, fields=["resident", "document_type", "purpose", "status", "remarks", "digital_signature"])
UserCertificateForm = modelform_factory(CertificateRequest, fields=["resident", "document_type", "purpose"])
ComplaintForm = modelform_factory(Complaint, fields=["complainant", "title", "incident_location", "description", "status", "hearing_date", "evidence"])
UserComplaintForm = modelform_factory(Complaint, fields=["complainant", "title", "incident_location", "description", "evidence"])
FeedbackForm = modelform_factory(Feedback, fields=["resident", "rating", "message"])

ADMIN_MODELS = {
    "residents": {
        "model": Resident,
        "form": ResidentForm,
        "title": "Resident Management",
        "subtitle": "Add, edit, delete, search, upload photos, and view complete resident profiles.",
        "fields": ["full_name", "purok", "civil_status", "occupation", "contact_number"],
        "search": ["first_name", "middle_name", "last_name", "purok", "contact_number"],
    },
    "households": {
        "model": Household,
        "form": HouseholdForm,
        "title": "Household Management",
        "subtitle": "Manage family heads, members, house numbers, and household statistics.",
        "fields": ["house_number", "family_head", "purok", "address"],
        "search": ["house_number", "family_head", "purok"],
    },
    "certificates": {
        "model": CertificateRequest,
        "form": CertificateForm,
        "title": "Certificate Requests",
        "subtitle": "Approve, reject, print, and prepare barangay certificates.",
        "fields": ["resident", "document_type", "purpose", "status"],
        "search": ["purpose", "remarks", "resident__first_name", "resident__last_name"],
    },
    "announcements": {
        "model": Announcement,
        "form": AnnouncementForm,
        "title": "Announcement Management",
        "subtitle": "Post events, emergencies, barangay meetings, and programs.",
        "fields": ["title", "category", "is_published", "posted_at"],
        "search": ["title", "message"],
    },
    "complaints": {
        "model": Complaint,
        "form": ComplaintForm,
        "title": "Blotter / Complaint Management",
        "subtitle": "Record complaints, incident reports, status tracking, and scheduled hearings.",
        "fields": ["title", "complainant", "incident_location", "status"],
        "search": ["title", "incident_location", "description"],
    },
    "feedback": {
        "model": Feedback,
        "form": FeedbackForm,
        "title": "Feedback",
        "subtitle": "Review resident ratings for barangay services.",
        "fields": ["resident", "rating", "created_at"],
        "search": ["message"],
    },
}


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("user_dashboard")
    return login_view(request)


def register_view(request):
    ensure_default_admin()
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        AuditLog.objects.create(user_name=user.username, action="registered a resident account")
        return redirect("user_dashboard")
    return HttpResponse(auth_page(request, "Create Account", "Sign up as a resident to access requests, complaints, announcements, and feedback.", "Sign Up", form=form, alt_link="/login/", alt_text="Already have an account? Log in"))


def login_view(request):
    ensure_default_admin()
    error = ""
    next_url = request.POST.get("next") or request.GET.get("next")
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user and user.is_active:
            login(request, user)
            AuditLog.objects.create(user_name=user.username, action="logged in")
            if safe_next(request, next_url):
                return redirect(next_url)
            return redirect("admin_dashboard" if user.is_staff or user.is_superuser else "user_dashboard")
        error = "Invalid username or password."
    return HttpResponse(auth_page(request, "Log In", "Access the Brgy San Isidro information management system.", "Log In", error=error, alt_link="/register/", alt_text="Create resident account"))


def admin_login_view(request):
    ensure_default_admin()
    error = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user and user.is_active and (user.is_staff or user.is_superuser):
            login(request, user)
            AuditLog.objects.create(user_name=user.username, action="logged in as admin")
            return redirect("admin_dashboard")
        error = "Admin access only. Use the default admin or another staff account."
    return HttpResponse(auth_page(request, "Admin Login", "Default admin: admin / Admin@12345", "Admin Log In", error=error, alt_link="/login/", alt_text="Resident login"))


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(user_name=request.user.username, action="logged out")
    logout(request)
    return redirect("login")


@login_required(login_url="/login/")
def user_dashboard(request):
    return HttpResponse(page(request, "user", user_dashboard_content(request)))


@login_required(login_url="/login/")
def user_profile(request):
    return HttpResponse(page(request, "profile", profile_content(request)))


@login_required(login_url="/login/")
def user_requests(request):
    return user_create_or_list(request, UserCertificateForm, CertificateRequest, "requests", "Online Document Requests", "Request Barangay Clearance, Certificate of Residency, or Indigency Certificate.")


@login_required(login_url="/login/")
def user_complaints(request):
    return user_create_or_list(request, UserComplaintForm, Complaint, "complaints", "Complaint Submission", "Submit complaints, concerns, evidence, and track status.")


@login_required(login_url="/login/")
def user_feedback(request):
    return user_create_or_list(request, FeedbackForm, Feedback, "feedback", "Feedback", "Rate barangay services as Excellent, Good, or Poor.")


def admin_required(view_func):
    return user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url="/admin-login/")(view_func)


@login_required(login_url="/login/")
def announcements(request):
    rows = Announcement.objects.filter(is_published=True).order_by("-posted_at")
    return HttpResponse(page(request, "announcements", public_announcements_content(rows)))


@login_required(login_url="/login/")
def contact(request):
    return HttpResponse(page(request, "contact", contact_content()))


@admin_required
def admin_dashboard(request):
    ensure_default_admin()
    return HttpResponse(page(request, "admin", admin_dashboard_content()))


@admin_required
def admin_list(request, section):
    config = get_section(section)
    objects = config["model"].objects.all().order_by("-id")
    query = request.GET.get("q", "").strip()
    if query:
        objects = search_objects(objects, config["search"], query)
    content = topbar(config["title"], config["subtitle"], f"/manage/{section}/add/", "Add New") + table_content(section, config, objects, query)
    return HttpResponse(page(request, section, content))


@admin_required
def admin_add(request, section):
    config = get_section(section)
    form = config["form"](request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        AuditLog.objects.create(user_name=request.user.username, action=f"added {section}", record_name=str(obj))
        return redirect("admin_list", section=section)
    return HttpResponse(page(request, section, form_content(request, f"Add {config['title']}", form, f"/manage/{section}/")))


@admin_required
def admin_edit(request, section, pk):
    config = get_section(section)
    obj = get_object_or_404(config["model"], pk=pk)
    form = config["form"](request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        AuditLog.objects.create(user_name=request.user.username, action=f"edited {section}", record_name=str(obj))
        return redirect("admin_list", section=section)
    return HttpResponse(page(request, section, form_content(request, f"Edit {config['title']}", form, f"/manage/{section}/")))


@admin_required
def admin_delete(request, section, pk):
    config = get_section(section)
    obj = get_object_or_404(config["model"], pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        AuditLog.objects.create(user_name=request.user.username, action=f"deleted {section}", record_name=name)
        return redirect("admin_list", section=section)
    content = topbar("Delete Record", f"Confirm delete: {escape(str(obj))}") + f"""
    <section class="card">
      <p>This action will permanently delete the selected record.</p>
      <form method="post" class="form-grid">
        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
        <button class="btn danger" type="submit">Delete</button>
        <a class="btn secondary" href="/manage/{section}/">Cancel</a>
      </form>
    </section>"""
    return HttpResponse(page(request, section, content))


@admin_required
def reports(request):
    return HttpResponse(page(request, "reports", reports_content()))


@admin_required
def settings(request):
    return HttpResponse(page(request, "settings", settings_content()))


def ensure_default_admin():
    User = get_user_model()
    user, created = User.objects.get_or_create(username=ADMIN_USERNAME, defaults={"email": "admin@sanisidro.gov.ph"})
    if created or not user.is_staff or not user.is_superuser:
        user.is_staff = True
        user.is_superuser = True
        user.set_password(ADMIN_PASSWORD)
        user.save()


def user_create_or_list(request, form_class, model, active, title, subtitle):
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        AuditLog.objects.create(user_name=request.user.username, action=f"submitted {title.lower()}", record_name=str(obj))
        return redirect(f"user_{active}")
    objects = model.objects.all().order_by("-id")[:25]
    content = topbar(title, subtitle) + f"""
    <section class="grid two">
      <div class="card"><h2>New Entry</h2>{form_html(request, form, "Submit")}</div>
      <div class="card"><h2>Recent Records</h2>{simple_list(objects)}</div>
    </section>"""
    return HttpResponse(page(request, active, content))


def get_section(section):
    if section not in ADMIN_MODELS:
        raise KeyError(section)
    return ADMIN_MODELS[section]


def search_objects(objects, fields, query):
    from django.db.models import Q

    conditions = Q()
    for field in fields:
        conditions |= Q(**{f"{field}__icontains": query})
    return objects.filter(conditions)


def page(request, active, content):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{SYSTEM_NAME}</title>
  <style>{styles()}</style>
</head>
<body>
  <div class="shell">
    {sidebar(request, active)}
    <main>
      {content}
      <div class="footer">{SYSTEM_NAME}</div>
    </main>
  </div>
</body>
</html>"""


def sidebar(request, active):
    user_label = escape(request.user.username) if request.user.is_authenticated else "Guest"
    public_links = [("announcements", "/announcements/", "Announcements"), ("contact", "/contact/", "Hotlines")]
    user_links = [("user", "/user/dashboard/", "Dashboard"), ("profile", "/user/profile/", "Profile"), ("requests", "/user/requests/", "Requests"), ("complaints", "/user/complaints/", "Complaints"), ("feedback", "/user/feedback/", "Feedback")]
    admin_links = [("admin", "/admin-dashboard/", "Dashboard"), ("residents", "/manage/residents/", "Residents"), ("households", "/manage/households/", "Households"), ("certificates", "/manage/certificates/", "Certificates"), ("announcements", "/manage/announcements/", "Announcements"), ("complaints", "/manage/complaints/", "Complaints"), ("reports", "/reports/", "Reports"), ("settings", "/settings/", "Settings")]
    groups = [("Public", public_links), ("Resident", user_links)]
    if request.user.is_staff or request.user.is_superuser:
        groups.append(("Admin", admin_links))
    html = []
    for title, links in groups:
        html.append(f'<div class="nav-title">{title}</div>')
        for key, href, label in links:
            html.append(f'<a class="{"active" if active == key else ""}" href="{href}"><span>{label[:1]}</span>{label}</a>')
    return f"""
    <aside class="sidebar">
      <div class="brand"><div class="seal">SI</div><div><strong>Brgy San Isidro</strong><small>Surigao City, Surigao del Norte</small></div></div>
      <div class="userbox">Signed in as <strong>{user_label}</strong></div>
      <nav>{''.join(html)}</nav>
      <a class="logout" href="/logout/">Log out</a>
    </aside>"""


def topbar(title, subtitle, href="", action=""):
    button = f'<a class="btn" href="{href}">+ {action}</a>' if href else ""
    return f"""
    <div class="topbar hero-bar">
      <div><div class="kicker">Brgy San Isidro</div><h1>{title}</h1><p>{subtitle}</p></div>
      <div class="actions">{button}</div>
    </div>"""


def admin_dashboard_content():
    stats = [
        ("Residents", Resident.objects.count(), "People", "blue"),
        ("Households", Household.objects.count(), "Homes", "green"),
        ("Male", Resident.objects.filter(is_male=True).count(), "M", "blue"),
        ("Female", Resident.objects.filter(is_male=False).count(), "F", "green"),
        ("Senior Citizens", Resident.objects.filter(is_senior_citizen=True).count(), "SC", "gold"),
        ("PWD", Resident.objects.filter(is_pwd=True).count(), "PWD", "teal"),
        ("Users", get_user_model().objects.count(), "Users", "blue"),
        ("Pending Requests", CertificateRequest.objects.filter(status="pending").count(), "Queue", "red"),
    ]
    cards = "".join(f'<div class="stat-card {color}"><div><span>{label}</span><strong>{value}</strong><small>{note}</small></div><em>{note[:2]}</em></div>' for label, value, note, color in stats)
    logs = "".join(f"<li>{escape(log.user_name)} {escape(log.action)} <small>{log.created_at:%Y-%m-%d %H:%M}</small></li>" for log in AuditLog.objects.order_by("-created_at")[:8]) or "<li>No activity yet.</li>"
    return topbar("Admin Dashboard", "Monitor residents, households, certificates, complaints, reports, and activity logs.") + f"""
    <section class="stats">{cards}</section>
    <section class="grid two">
      <div class="card panel-card"><h2>Population Analytics</h2><p>Live summary from resident records.</p>{bars()}</div>
      <div class="card panel-card"><h2>Recent Activity</h2><p>Latest account and record activity.</p><ul class="activity-list">{logs}</ul></div>
    </section>"""


def user_dashboard_content(request):
    return topbar("Resident Dashboard", "Request certificates, submit complaints, read announcements, send feedback, and access emergency hotlines.") + """
    <section class="grid cards">
      <a class="card action-card" href="/user/requests/"><h2>Document Requests</h2><p>Barangay Clearance, Residency, and Indigency Certificate.</p></a>
      <a class="card action-card" href="/user/complaints/"><h2>Submit Complaint</h2><p>Send concerns and monitor complaint status.</p></a>
      <a class="card action-card" href="/announcements/"><h2>Announcements</h2><p>Read events, meetings, programs, and emergency alerts.</p></a>
      <a class="card action-card" href="/user/feedback/"><h2>Feedback</h2><p>Rate services as Excellent, Good, or Poor.</p></a>
      <a class="card action-card" href="/contact/"><h2>Emergency Hotlines</h2><p>Police, fire station, barangay desk, and health center.</p></a>
    </section>"""


def profile_content(request):
    return topbar("My Profile", "Manage your resident account and password security.") + f"""
    <section class="grid two">
      <div class="card"><h2>Account</h2><p>Username: <strong>{escape(request.user.username)}</strong></p><p>Email: {escape(request.user.email or "Not set")}</p></div>
      <div class="card green"><h2>Security</h2><p>You are logged in securely. Use logout when finished on a shared computer.</p></div>
    </section>"""


def public_announcements_content(rows):
    cards = "".join(f'<article class="card"><h2>{escape(row.title)}</h2><span class="chip">{row.get_category_display()}</span><p>{escape(row.message)}</p></article>' for row in rows) or '<div class="card"><p>No announcements posted.</p></div>'
    return topbar("Announcements", "Events, emergencies, barangay meetings, and programs.") + f'<section class="grid cards">{cards}</section>'


def contact_content():
    rows = [("Barangay Desk", "0999-111-2222"), ("Police", "117"), ("Fire Station", "160"), ("Health Center", "0918-555-0198")]
    body = "".join(f"<tr><td>{label}</td><td><strong>{number}</strong></td></tr>" for label, number in rows)
    return topbar("Emergency Hotlines", "Quick access numbers for urgent concerns.") + f'<section class="card"><table><tbody>{body}</tbody></table></section>'


def reports_content():
    return topbar("Reports and Analytics", "Printable resident, population, senior citizen, voter, and monthly reports.") + f"""
    <section class="grid two">
      <div class="card"><h2>Report Summary</h2><ul><li>Total residents: {Resident.objects.count()}</li><li>Senior citizens: {Resident.objects.filter(is_senior_citizen=True).count()}</li><li>Registered voters: {Resident.objects.filter(is_registered_voter=True).count()}</li><li>Complaints: {Complaint.objects.count()}</li></ul><button class="btn" onclick="window.print()">Print / Export PDF</button></div>
      <div class="card"><h2>Population Chart</h2>{bars()}</div>
    </section>"""


def settings_content():
    return topbar("Settings", "User account management, audit trail, and system access.") + f"""
    <section class="grid cards">
      <div class="card"><h2>Default Admin</h2><p>Username: <strong>{ADMIN_USERNAME}</strong></p><p>Password: <strong>{ADMIN_PASSWORD}</strong></p></div>
      <div class="card"><h2>User Accounts</h2><p>Residents can sign up. Admins can manage records and use Django admin for advanced user control.</p></div>
      <div class="card"><h2>Audit Trail</h2><p>Login, logout, add, edit, and delete actions are saved.</p></div>
    </section>"""


def table_content(section, config, objects, query):
    headers = "".join(f"<th>{field.replace('_', ' ').title()}</th>" for field in config["fields"]) + "<th>Actions</th>"
    rows = ""
    for obj in objects:
        cells = "".join(f"<td>{escape(display_value(obj, field))}</td>" for field in config["fields"])
        rows += f'<tr>{cells}<td><a class="link" href="/manage/{section}/{obj.pk}/edit/">Edit</a> <a class="link danger-text" href="/manage/{section}/{obj.pk}/delete/">Delete</a></td></tr>'
    rows = rows or f'<tr><td colspan="{len(config["fields"]) + 1}">No records found.</td></tr>'
    return f"""
    <section class="card">
      <form class="searchbar" method="get"><input name="q" value="{escape(query)}" placeholder="Search records"><button class="btn" type="submit">Search</button></form>
      <div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>
    </section>"""


def display_value(obj, field):
    value = getattr(obj, field)
    if callable(value):
        value = value()
    if hasattr(obj, f"get_{field}_display"):
        value = getattr(obj, f"get_{field}_display")()
    return str(value)


def form_content(request, title, form, cancel_url):
    return topbar(title, "Complete the fields below, then save the record.") + f'<section class="card">{form_html(request, form, "Save")}<a class="link" href="{cancel_url}">Cancel</a></section>'


def form_html(request, form, submit):
    csrf = get_token(request) if request else ""
    fields = "".join(form_field(field) for field in form)
    enctype = ' enctype="multipart/form-data"'
    return f'<form method="post"{enctype} class="form-grid"><input type="hidden" name="csrfmiddlewaretoken" value="{csrf}">{form.errors.as_ul() if form.errors else ""}{fields}<button class="btn" type="submit">{submit}</button></form>'


def form_field(field):
    return f'<label>{field.label}{field}{field.errors.as_ul() if field.errors else ""}</label>'


def simple_list(objects):
    rows = "".join(f"<li>{escape(str(obj))}</li>" for obj in objects) or "<li>No records yet.</li>"
    return f'<ul class="clean">{rows}</ul>'


def bars():
    residents = max(Resident.objects.count(), 1)
    male = round((Resident.objects.filter(is_male=True).count() / residents) * 100)
    female = round((Resident.objects.filter(is_male=False).count() / residents) * 100)
    senior = round((Resident.objects.filter(is_senior_citizen=True).count() / residents) * 100)
    pwd = round((Resident.objects.filter(is_pwd=True).count() / residents) * 100)
    data = [("Male", male), ("Female", female), ("Senior", senior), ("PWD", pwd)]
    return "".join(f'<div class="bar"><span><strong>{label}</strong><em>{value}%</em></span><div class="track"><div style="width:{value}%"></div></div></div>' for label, value in data)


def auth_page(request, title, subtitle, button_label, form=None, error="", alt_link="/", alt_text="Back"):
    csrf = get_token(request)
    next_url = escape(request.POST.get("next") or request.GET.get("next") or "")
    if form:
        fields = "".join(form_field(field) for field in form)
        errors = form.errors.as_ul() if form.errors else ""
    else:
        fields = '<label>Username<input name="username" required></label><label>Password<input name="password" type="password" required></label>'
        errors = f"<ul><li>{escape(error)}</li></ul>" if error else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>{styles()}</style></head>
<body class="auth-body">
  <section class="auth-card">
    <div class="auth-info">
      <div>
        <div class="seal">SI</div>
        <div class="auth-label">Official Barangay Portal</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div class="portal-card">
        <h2>San Isidro Information System</h2>
        <p>Surigao City, Surigao del Norte, Philippines</p>
        <div class="feature-pills">
          <span>Residents</span>
          <span>Certificates</span>
          <span>Complaints</span>
          <span>Reports</span>
        </div>
      </div>
      <div class="auth-meta">
        <strong>Fast access for barangay services</strong>
        <small>{SYSTEM_NAME}</small>
      </div>
    </div>
    <form method="post" class="auth-form">
      <div class="form-brand">
        <span>Official Portal</span>
        <h2>San Isidro Information System</h2>
        <p>Log in or create an account to continue.</p>
      </div>
      <input type="hidden" name="csrfmiddlewaretoken" value="{csrf}">
      <input type="hidden" name="next" value="{next_url}">
      {errors}{fields}
      <button class="btn" type="submit">{button_label}</button>
      <div class="auth-links"><a href="{alt_link}">{alt_text}</a><a href="/admin-login/">Admin login</a></div>
      <p class="muted">Default admin: <strong>{ADMIN_USERNAME}</strong> / <strong>{ADMIN_PASSWORD}</strong></p>
    </form>
  </section>
</body></html>"""


def safe_next(request, next_url):
    return bool(next_url) and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure())


def styles():
    return """
    :root{--blue:#155eef;--blue-dark:#123d8c;--green:#18a957;--teal:#0e9384;--gold:#d98f00;--red:#d92d20;--ink:#102033;--muted:#667085;--line:#d9e2ec;--soft:#f5f9fc;--white:#fff;--shadow:0 16px 40px rgba(16,32,51,.08)}
    *{box-sizing:border-box}
    html{-webkit-text-size-adjust:100%}
    body{margin:0;font-family:Arial,Helvetica,sans-serif;color:var(--ink);background:radial-gradient(circle at top left,rgba(21,94,239,.12),transparent 320px),linear-gradient(180deg,#eef6ff 0,#f7fbf8 360px,#f5f9fc 100%);line-height:1.5}
    a{text-decoration:none;color:inherit}
    .shell{min-height:100vh;display:grid;grid-template-columns:300px minmax(0,1fr)}
    .sidebar{background:linear-gradient(180deg,#0f3478 0,#123d8c 50%,#0f766e 100%);color:white;padding:24px 18px;position:sticky;top:0;height:100vh;overflow:auto;border-right:1px solid rgba(255,255,255,.12)}
    .brand{display:flex;gap:12px;align-items:center;margin-bottom:18px}
    .seal{width:48px;height:48px;min-width:48px;border-radius:14px;background:white;color:var(--blue-dark);display:grid;place-items:center;font-weight:900;box-shadow:0 10px 24px rgba(0,0,0,.16)}
    .brand strong{display:block;line-height:1.15}.brand small{display:block;color:#c8ddff;line-height:1.25}
    .userbox{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:14px;margin-bottom:18px;box-shadow:0 10px 26px rgba(0,0,0,.08)}
    .nav-title{color:#a9c7f7;font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin:18px 8px 8px}
    nav a{display:flex;gap:12px;align-items:center;color:#eaf2ff;padding:12px 12px;border-radius:10px;font-size:14px;min-height:44px;font-weight:700}
    nav a.active,nav a:hover{background:rgba(255,255,255,.16);box-shadow:inset 0 0 0 1px rgba(255,255,255,.1)}
    nav span{width:22px;text-align:center;font-weight:800}
    .logout{display:block;margin-top:18px;background:rgba(255,255,255,.14);padding:11px;border-radius:8px;text-align:center;font-weight:800}
    main{min-width:0;padding:34px;max-width:1480px;width:100%;margin:0 auto}
    .topbar{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;margin-bottom:24px}
    .hero-bar{background:linear-gradient(135deg,rgba(255,255,255,.92),rgba(239,248,245,.86));border:1px solid rgba(217,226,236,.9);border-radius:14px;padding:24px 26px;box-shadow:var(--shadow);position:relative;overflow:hidden}
    .hero-bar:after{content:"";position:absolute;right:-60px;top:-80px;width:240px;height:240px;background:radial-gradient(circle,rgba(24,169,87,.18),transparent 65%);pointer-events:none}
    .kicker{color:var(--green);font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.08em}
    h1{margin:4px 0 8px;font-size:clamp(26px,4vw,44px);line-height:1.08;max-width:980px}
    h2{margin:0 0 12px;font-size:20px;line-height:1.2}
    p{margin:0 0 8px;color:var(--muted)}
    .grid{display:grid;gap:16px}.two{grid-template-columns:minmax(0,1.1fr) minmax(280px,.9fr)}.cards{grid-template-columns:repeat(3,minmax(0,1fr))}
    .stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin-bottom:22px}
    .card{background:rgba(255,255,255,.96);border:1px solid rgba(217,226,236,.9);border-radius:10px;padding:20px;box-shadow:var(--shadow);min-width:0}
    .card strong{display:block;font-size:32px;line-height:1.1}.blue{border-top:4px solid var(--blue)}.green{border-top:4px solid var(--green)}.gold{border-top:4px solid var(--gold)}.teal{border-top:4px solid var(--teal)}.red{border-top:4px solid var(--red)}
    .action-card:hover{border-color:var(--blue);transform:translateY(-1px)}
    .stat-card{position:relative;display:flex;justify-content:space-between;gap:12px;align-items:flex-start;background:rgba(255,255,255,.97);border:1px solid rgba(217,226,236,.92);border-radius:14px;padding:20px;min-height:136px;box-shadow:var(--shadow);overflow:hidden}
    .stat-card:before{content:"";position:absolute;inset:0 0 auto;height:5px;background:var(--blue)}
    .stat-card.green:before{background:var(--green)}.stat-card.gold:before{background:var(--gold)}.stat-card.teal:before{background:var(--teal)}.stat-card.red:before{background:var(--red)}
    .stat-card span{display:block;font-size:15px;color:var(--ink);margin-bottom:7px}.stat-card strong{display:block;font-size:42px;line-height:1;font-weight:900}.stat-card small{display:block;margin-top:9px;color:var(--muted);font-weight:700}
    .stat-card em{font-style:normal;display:grid;place-items:center;min-width:46px;height:46px;border-radius:14px;background:#eef6ff;color:var(--blue-dark);font-size:13px;font-weight:900}
    .panel-card{border-radius:14px}.panel-card h2{font-size:23px}.activity-list{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:10px}.activity-list li{background:#f7fbff;border:1px solid #e6eef7;border-left:4px solid var(--green);border-radius:8px;padding:10px 12px;color:var(--muted)}.activity-list small{display:block;color:#7b8797;font-size:12px;margin-top:2px}
    .btn{border:0;border-radius:8px;background:linear-gradient(135deg,var(--blue),#0f766e);color:white;padding:10px 15px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;min-height:44px;white-space:nowrap;box-shadow:0 8px 18px rgba(21,94,239,.18)}
    .btn.secondary{background:var(--green)}.btn.danger{background:var(--red)}.link{color:var(--blue);font-weight:800}.danger-text{color:var(--red)}
    .searchbar{display:flex;gap:10px;margin-bottom:14px}
    .form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .form-grid label,.auth-form label{display:grid;gap:6px;font-weight:800}
    .form-grid input,.form-grid select,.form-grid textarea,.searchbar input,.auth-form input{width:100%;border:1px solid var(--line);border-radius:8px;min-height:44px;padding:10px 12px;font:inherit;background:white;outline:none}
    .form-grid input:focus,.form-grid select:focus,.form-grid textarea:focus,.searchbar input:focus,.auth-form input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(21,94,239,.12)}
    .form-grid textarea{min-height:116px;resize:vertical}
    .form-grid input[type=checkbox]{width:auto;min-height:auto;justify-self:start;transform:scale(1.15)}
    .form-grid button{grid-column:1/-1}
    .table-wrap{width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:8px}
    table{width:100%;border-collapse:collapse;min-width:720px;background:white}
    th,td{text-align:left;border-bottom:1px solid var(--line);padding:12px;font-size:14px;vertical-align:top}
    th{background:#f0f6ff;color:var(--blue-dark);position:sticky;top:0}
    tr:last-child td{border-bottom:0}.clean{padding-left:18px;color:var(--muted)}
    .chip{display:inline-block;background:#eef6ff;color:var(--blue-dark);padding:4px 9px;border-radius:999px;font-size:12px;font-weight:800;margin-bottom:8px}
    .bar{margin-top:18px;margin-bottom:16px}.bar span{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:14px}.bar strong{font-size:16px;color:var(--ink)}.track{height:12px;background:#e7eef7;border-radius:999px;overflow:hidden}.track div{height:100%;background:linear-gradient(90deg,var(--blue),var(--green))}
    .footer{text-align:center;color:var(--muted);font-size:13px;margin-top:28px}
    .auth-body{min-height:100vh;display:grid;place-items:center;padding:22px;background:linear-gradient(140deg,#eaf3ff 0,#f5fbf7 52%,#edf8f5 100%)}
    .auth-card{width:min(1040px,100%);display:grid;grid-template-columns:minmax(0,1fr) minmax(330px,430px);background:white;border:1px solid rgba(217,226,236,.9);border-radius:14px;overflow:hidden;box-shadow:0 28px 80px rgba(16,32,51,.16)}
    .auth-info{position:relative;background:linear-gradient(145deg,#123d8c 0,#155eef 48%,#11845b 100%);color:white;padding:40px;display:flex;flex-direction:column;justify-content:space-between;gap:28px;min-height:540px;overflow:hidden}
    .auth-info:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px),linear-gradient(180deg,rgba(255,255,255,.07) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(135deg,rgba(0,0,0,.7),transparent 72%);pointer-events:none}
    .auth-info>*{position:relative;z-index:1}.auth-info p,.auth-info small{color:#e7f1ff}.auth-label{display:inline-flex;margin:30px 0 16px;padding:7px 10px;border:1px solid rgba(255,255,255,.28);border-radius:999px;background:rgba(255,255,255,.12);font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.portal-card{border:1px solid rgba(255,255,255,.26);background:rgba(255,255,255,.13);backdrop-filter:blur(8px);border-radius:12px;padding:18px;max-width:560px}.portal-card h2{margin:0 0 6px;color:white;font-size:25px}.portal-card p{margin-bottom:14px}.feature-pills{display:flex;gap:8px;flex-wrap:wrap}.feature-pills span{background:rgba(255,255,255,.17);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:6px 9px;font-size:12px;font-weight:800}.auth-meta{display:grid;gap:6px}.auth-meta strong{font-size:16px}.auth-form{padding:40px;display:grid;gap:16px;align-content:center}
    .form-brand{margin-bottom:8px}.form-brand span{color:var(--green);font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.form-brand h2{font-size:28px;margin:3px 0 6px;color:var(--ink)}.form-brand p{font-size:14px}
    .auth-links{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}.auth-links a{color:var(--blue);font-weight:800}
    .muted{color:var(--muted);font-size:13px}ul.errorlist,.auth-form ul{color:var(--red);background:#fff4f2;border-radius:8px;padding:10px 12px 10px 28px;margin:0}
    @media(max-width:1180px){.shell{grid-template-columns:260px minmax(0,1fr)}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}main{padding:26px}}
    @media(max-width:900px){.shell{grid-template-columns:1fr}.sidebar{position:static;height:auto}.sidebar nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px}.nav-title{grid-column:1/-1}.two{grid-template-columns:1fr}main{padding:22px}.auth-card{grid-template-columns:1fr}.auth-info{min-height:260px}.hero-bar{padding:20px}}
    @media(max-width:620px){.auth-body{padding:0;place-items:stretch}.auth-card{border-radius:0;min-height:100vh}.auth-info{padding:24px;min-height:320px}.auth-label{margin:18px 0 12px}.portal-card{padding:14px}.portal-card h2{font-size:21px}.feature-pills span{font-size:11px}.auth-form{padding:24px}.sidebar{padding:18px 12px}.sidebar nav{grid-template-columns:1fr}.brand{align-items:flex-start}.topbar{display:block;margin-bottom:18px}.actions{margin-top:12px}.stats,.cards,.form-grid{grid-template-columns:1fr}main{padding:16px}.card{padding:15px}.searchbar{flex-direction:column}.btn{width:100%}h1{font-size:28px}table{min-width:640px}th,td{padding:10px;font-size:13px}}
    @media print{.sidebar,.btn,.searchbar,.footer{display:none}.shell{display:block}main{padding:0}.card{box-shadow:none;border:1px solid #ccc}}
    """
