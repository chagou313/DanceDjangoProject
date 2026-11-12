# Responsive Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复导航栏在桌面端被压缩换行和遮挡首页的问题，并为中小屏幕提供可访问的折叠菜单。

**Architecture:** 保留 `templates/dance/base.html` 作为全站导航的单一实现，通过统一的 CSS 高度变量、桌面压缩断点与 `1200px` 折叠断点控制布局。少量原生 JavaScript 只负责菜单开关与关闭事件；Django 模板继续负责登录态内容。回归测试通过 Django Test Client 验证最终渲染结构和关键样式契约。

**Tech Stack:** Django templates, CSS media queries, vanilla JavaScript, Django `TestCase`

---

### Task 1: Add navigation regression tests

**Files:**
- Create: `dance/test_navigation.py`
- Test: `dance/test_navigation.py`

- [ ] **Step 1: Write failing tests for the responsive navigation contract**

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ResponsiveNavigationTests(TestCase):
    def test_home_renders_accessible_collapsible_navigation(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="nav-toggle"')
        self.assertContains(response, 'aria-controls="primary-navigation"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, 'id="primary-navigation"')
        self.assertContains(response, '--navbar-height:')
        self.assertContains(response, '@media (max-width: 1200px)')

    def test_authenticated_mobile_menu_contains_session_actions(self):
        user = User.objects.create_user(username="layout-user", password="secret123")
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="mobile-session-actions"')
        self.assertContains(response, "layout-user")
        self.assertContains(response, reverse("logout"))

    def test_navigation_script_supports_escape_and_outside_click(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "event.key === 'Escape'")
        self.assertContains(response, "!navbar.contains(event.target)")
```

- [ ] **Step 2: Run tests and verify the expected failure**

Run: `python3 manage.py test dance.test_navigation -v 2`

Expected: FAIL because `.nav-toggle`, `#primary-navigation`, the responsive height variable, and menu script are absent.

- [ ] **Step 3: Commit the failing tests**

```bash
git add dance/test_navigation.py
git commit -m "test: specify responsive navigation behavior"
```

### Task 2: Implement stable desktop navigation and mobile menu

**Files:**
- Modify: `templates/dance/base.html:10-366`
- Modify: `templates/dance/base.html:460-558`
- Modify: `templates/dance/base.html:616-629`
- Test: `dance/test_navigation.py`

- [ ] **Step 1: Add a shared height variable and prevent desktop text wrapping**

Add the shared variable and apply it to the fixed header, content offset, and messages:

```css
:root {
    --navbar-height: 88px;
}

.navbar {
    min-height: var(--navbar-height);
    padding: 1rem 2rem;
}

.logo,
.nav-links > li,
.nav-links > li > a,
.auth-buttons,
.auth-buttons > * {
    white-space: nowrap;
    flex-shrink: 0;
}

.container {
    padding-top: var(--navbar-height);
}

.messages {
    top: calc(var(--navbar-height) + 1rem);
}
```

- [ ] **Step 2: Add the menu button and identify the controlled navigation**

Insert the button after the logo and identify the existing list:

```html
<button class="nav-toggle" type="button" aria-label="打开导航菜单"
        aria-controls="primary-navigation" aria-expanded="false">
    <i class="fas fa-bars" aria-hidden="true"></i>
</button>
<ul class="nav-links" id="primary-navigation">
```

Inside the list, add a login-aware mobile-only action group so mobile users retain authentication controls:

```html
<li class="mobile-session-actions">
    {% if user.is_authenticated %}
        <span class="mobile-username"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'logout' %}"><i class="fas fa-sign-out-alt"></i> 退出登录</a>
    {% else %}
        <a href="{% url 'login' %}"><i class="fas fa-sign-in-alt"></i> 登录</a>
        <a href="{% url 'register' %}"><i class="fas fa-user-plus"></i> 注册</a>
    {% endif %}
</li>
```

- [ ] **Step 3: Add medium-desktop compression and the 1200px collapsed layout**

```css
.nav-toggle,
.mobile-session-actions {
    display: none;
}

@media (max-width: 1450px) {
    .navbar { padding-inline: 1.25rem; }
    .logo { font-size: 1.5rem; letter-spacing: 2px; gap: 0.55rem; }
    .nav-links { gap: 1.25rem; }
    .nav-links a { font-size: 0.95rem; }
    .auth-buttons { gap: 0.6rem; }
    .btn { padding: 0.6rem 1.1rem; }
}

@media (max-width: 1200px) {
    :root { --navbar-height: 74px; }
    .navbar { padding: 0.75rem 1.25rem; }
    .nav-container { position: relative; }
    .nav-toggle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        margin-left: auto;
        color: #F5E7B2;
        background: rgba(212, 175, 55, 0.08);
        border: 1px solid rgba(212, 175, 55, 0.5);
        border-radius: 0.75rem;
        cursor: pointer;
    }
    .nav-links {
        display: none;
        position: absolute;
        top: calc(100% + 0.75rem);
        left: 0;
        right: 0;
        max-height: calc(100vh - var(--navbar-height) - 1rem);
        overflow-y: auto;
        padding: 0.75rem;
        flex-direction: column;
        gap: 0.25rem;
        background: rgba(15, 15, 20, 0.98);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 0 0 1rem 1rem;
        box-shadow: 0 16px 30px rgba(0, 0, 0, 0.45);
    }
    .nav-links.is-open { display: flex; }
    .nav-links > li > a { display: flex; padding: 0.8rem 1rem; }
    .nav-dropdown .dropdown-menu { display: none; }
    .auth-buttons { display: none; }
    .mobile-session-actions { display: grid; gap: 0.25rem; border-top: 1px solid rgba(212, 175, 55, 0.25); }
    .mobile-username { padding: 0.8rem 1rem; color: #E8D59B; }
}
```

Replace the old `768px` rule that hides `.nav-links`; retain only smaller logo/button sizing there.

- [ ] **Step 4: Add the interaction script**

Add before `</body>`:

```javascript
const navbar = document.querySelector('.navbar');
const navToggle = document.querySelector('.nav-toggle');
const primaryNavigation = document.getElementById('primary-navigation');

function closeNavigation() {
    primaryNavigation.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', '打开导航菜单');
}

navToggle.addEventListener('click', function() {
    const isOpen = primaryNavigation.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
    navToggle.setAttribute('aria-label', isOpen ? '关闭导航菜单' : '打开导航菜单');
});

primaryNavigation.addEventListener('click', function(event) {
    if (event.target.closest('a')) closeNavigation();
});

document.addEventListener('click', function(event) {
    if (!navbar.contains(event.target)) closeNavigation();
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeNavigation();
        navToggle.focus();
    }
});

window.addEventListener('resize', function() {
    if (window.innerWidth > 1200) closeNavigation();
});
```

- [ ] **Step 5: Run focused tests and make them pass**

Run: `python3 manage.py test dance.test_navigation -v 2`

Expected: 3 tests PASS.

- [ ] **Step 6: Commit the implementation without including unrelated working-tree changes**

```bash
git add templates/dance/base.html
git commit -m "fix: make site navigation responsive"
```

### Task 3: Verify Django and the rendered page

**Files:**
- Verify: `templates/dance/base.html`
- Verify: `templates/dance/home.html`

- [ ] **Step 1: Run the project checks and focused tests**

Run: `python3 manage.py check && python3 manage.py test dance.test_navigation -v 2`

Expected: system check reports no issues and all responsive navigation tests pass.

- [ ] **Step 2: Verify the running page at three viewport classes**

Open `http://127.0.0.1:8000/` and inspect at approximately `1440px`, `1024px`, and `390px` wide.

Expected:

- `1440px`: one-line desktop navigation; no split Chinese labels or tall logout pill.
- `1024px`: compact header with menu button; opening the menu exposes all page and session links.
- `390px`: menu fits the viewport and scrolls vertically if needed; no horizontal page overflow.
- All widths: the complete hero heading appears below the fixed header.

- [ ] **Step 3: Confirm only planned files were added to implementation commits**

Run: `git show --stat --oneline HEAD && git status --short`

Expected: the latest implementation commit contains `templates/dance/base.html`; pre-existing unrelated working-tree changes remain present and uncommitted/staged exactly as before.
