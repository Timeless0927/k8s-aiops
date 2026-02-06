# PRD 018: System Settings & Localization

## 1. Overview
Enhance the "System Settings" module to support dynamic configuration of critical components (LLM, Monitoring, Notifications) without service restarts, and provide a localized (Chinese) user interface for better accessibility.

## 2. Goals
- **Dynamic Config**: Allow admins to update Prometheus/Loki/Grafana URLs and OpenAI keys at runtime.
- **Improved UX**: Group settings by category (LLM, Monitoring, Automation) with collapsible sections.
- **Security**: Mask sensitive fields (API Keys, Secrets) with toggle visibility.
- **Localization**: Full Chinese translation for Settings, Plugins, and Alert Monitoring interfaces.
- **Feedback**: Immediate visual feedback for "Test Connection" actions.

## 3. Specifications

### 3.1 Backend
- **Config Manager**: `MonitoringConfigManager` and `LLMConfigManager` to load settings from DB with fallback to Env vars.
- **Plugins**: Update `prometheus_plugin` and `loki_plugin` to fetch URLs dynamically from `MonitoringConfigManager`.
- **API**: Ensure `GET /settings` returns categorized data (or metadata to support frontend grouping).

### 3.2 Frontend
- **Settings Page**:
    - **Grouping**: Use Accordion UI for 'LLM', 'Monitoring', 'Notification', 'Automation'.
    - **Controls**:
        - Text Input for standard URLs.
        - Password Input + Eye Icon for keys/secrets.
        - Toggle Switch for boolean values (`enable_auto_fix`).
    - **Localization**: Mapped English keys to Chinese labels (e.g., `openai_api_key` -> `OpenAI API 密钥`).
- **Plugin Dashboard**: Translated headers, status labels, and button text to Chinese.
- **Global Alerts**: Translated "All Systems Operational" banner.

## 4. Workflows
1.  **User modifies Prometheus URL**:
    - User saves change in UI -> Backend updates DB -> Plugin reads new URL on next execution (No Restart).
2.  **User tests LLM Connection**:
    - User clicks "Test" -> UI shows "Testing..." -> Backend validates Key/URL -> UI displays Success/Error banner.

## 5. Definition of Done
- [x] Settings persist to DB and take effect immediately.
- [x] Sensitive keys are masked in UI.
- [x] All Settings/Plugin pages are in Chinese.
- [x] "Enable Auto Fix" uses a Toggle Switch.
- [x] Code pushed to checks passed.
