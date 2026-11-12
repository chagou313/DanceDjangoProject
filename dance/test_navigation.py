from django.contrib.auth.models import AnonymousUser, User
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse


class ResponsiveNavigationTests(SimpleTestCase):
    def render_home(self, user=None):
        request = RequestFactory().get(reverse("home"))
        request.user = user or AnonymousUser()
        return render_to_string(
            "dance/home.html",
            {"user": request.user},
            request=request,
        )

    def test_home_renders_accessible_collapsible_navigation(self):
        content = self.render_home()

        self.assertIn('class="nav-toggle"', content)
        self.assertIn('aria-controls="primary-navigation"', content)
        self.assertIn('aria-expanded="false"', content)
        self.assertIn('id="primary-navigation"', content)
        self.assertIn('--navbar-height:', content)
        self.assertIn('@media (max-width: 1200px)', content)

    def test_home_mobile_layout_prevents_narrow_grid_overflow(self):
        content = self.render_home()

        self.assertIn('grid-template-columns: minmax(0, 1fr);', content)
        self.assertIn('overflow-x: hidden;', content)

    def test_authenticated_mobile_menu_contains_session_actions(self):
        user = User(username="layout-user")

        content = self.render_home(user)

        self.assertIn('class="mobile-session-actions"', content)
        self.assertIn("layout-user", content)
        self.assertIn(reverse("logout"), content)

    def test_navigation_script_supports_escape_and_outside_click(self):
        content = self.render_home()

        self.assertIn("event.key === 'Escape'", content)
        self.assertIn("!navbar.contains(event.target)", content)
