# 訂閱項目小助手 / Python backend

## 原始碼和 DEMO

最新版本請參見 <https://github.com/pan-subscribe-manager/backend-python>，這裡的程式碼均僅供參考。部署到雲端的版本亦請參見上述版本。

## 後端特色

- 使用 FastAPI 框架，提供 Swagger UI 介面。
- 支援 Multi-tenant（多租戶）模式
  - 依使用者 ID 隔開 Methods/Subscriptions/etc.
- 使用 Pydantic 來驗證輸入資料。
- 採 RESTful API best practice 架構設計 API interfaces
- 使用 Dependency Injection 注入資料庫連線。

## 後端架構

目前後端的架構如下：

- auth: 負責管理 JWT token、OAuth 流程、密碼雜湊等等的模組。
- controllers: 直接面對使用者的 API 業務邏輯。
  - auth: 負責處理使用者登入、註冊等等的 API。
  - user: 負責管理使用者資料的 API。
  - method: 負責管理付款方式的 API。
  - subscription: 負責管理訂閱項目的 API。
- dependencies: 用來注入到 Controller 的 FastAPI Dependencies。
  - db_session: 負責管理資料庫連線的 Dependency。
  - pagination: 分頁相關的 parameters。
  - user: 負責管理使用者相關的 parameters。
- models: 資料庫的 SQLAlchemy 模型。
  - base: 基底類別。
  - method: 付款方式的模型。
  - subscription: 訂閱項目的模型。
  - user: 使用者的模型。
- database: 資料庫的連線模組。

## 開發說明

1. 安裝 `rye` 套件管理器，然後執行 `rye sync` 預備依賴。
2. 使用以下命令啟動 Uvicorn 伺服器 (開發模式)：

   ```bash
   FC_DEBUG=1 FC_DATABASE_URI="postgresql://<username>:<password>@<host>:<password>/<db>" FC_SECRET_KEY="<密鑰，隨機產生即可>" rye run uvicorn finance_control_be:app
   ```

啟動後可以到 `http://127.0.0.1/docs` 查看每個 API 的具體使用說明。這裡簡介使用說明：

1. 使用 `/internal/users/initialize` API 初始化資料庫。
2. 先使用 `/auth/login` API 登入，取得 JWT token。
3. 將 access token 以 `Bearer <token>` 的方式放到 HTTP Header `Authorization` 中，即可使用其他 API。
