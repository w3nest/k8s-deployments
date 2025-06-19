# Keycloak Realm w3nest (old youwol)

<note level="warning" title="Use import to create realm">
This page explain the creation of the `w3nest` realm in keycloak.
It is faster and safer to import keycloak exported configuration to create it.
</note>

---

## **🔑 What are Keycloak Clients?**  

In **Keycloak**, a **client** represents an **application** or **service** that interacts with Keycloak 
for **authentication and authorization**. Clients can be frontend apps, backend services, or even other APIs.


### **📌 Types of Clients**

Keycloak supports different types of clients based on how they authenticate and interact with users:  

| Client Type         | Description                                                                                                      |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Confidential**    | Used by **backend services** (e.g., APIs). Requires a **client secret** to authenticate.                         |
| **Public**          | Used by **frontend apps** (e.g., SPAs, mobile apps). No client secret, relies on **PKCE** or **redirect flows**. |
| **Bearer-Only**     | Used by **backend APIs** that do not authenticate users directly but require a valid token from another service. |
| **Service Account** | Used for **machine-to-machine authentication**. The client itself acts as a user with special permissions.       |


### **🔧 What Can a Client Do?**

A Keycloak client can:
1. **Authenticate users** (login & logout).
2. **Issue tokens** (Access Token, ID Token, Refresh Token).
3. **Enforce role-based access control (RBAC)**.
4. **Integrate with OpenID Connect (OIDC) & SAML** for SSO.
5. **Impersonate users** (if configured).


### **🛠️ Example Clients in a System**

| Client Name              | Purpose                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| `web-app-client`         | Handles login/logout for a **frontend application** (public client).                       |
| `mobile-app-client`      | Used by a **mobile app** for authentication (public client with PKCE).                     |
| `auth-service`           | A backend service responsible for **user authentication** (confidential client).           |
| `accounts-backend-admin` | Manages **user creation, impersonation, and admin tasks** (service account client).        |
| `payments-api`           | A **protected backend API** that only accepts authenticated requests (bearer-only client). |

### **🚀 Keycloak Clients in Action**

When a user logs into your app:
1. The **frontend app** (`web-app-client`) redirects them to Keycloak.
2. Keycloak authenticates the user and issues a **token**.
3. The frontend app uses this token to call the **backend API** (`auth-service`).
4. The backend validates the token and allows access.


### **🔒 Security Considerations**

- **Use Confidential Clients** for backend services (never expose secrets in frontend apps).
- **Enable PKCE** for public clients to prevent token interception.
- **Restrict access** using **client roles and scopes**.

---

## **🔧 Keycloak Client Configuration**  

When configuring a **Keycloak client**, you define:  
✅ **How it authenticates** (confidential, public, etc.)  
✅ **What permissions it has** (roles)  
✅ **What user data it can access** (scopes)  


### **1️⃣ Basic Client Configuration**

Here’s a **sample configuration** for a backend service (`auth-service`):  

| Setting                 | Value                       | Description                                                            |
| ----------------------- | --------------------------- | ---------------------------------------------------------------------- |
| **Client ID**           | `auth-service`              | Unique identifier for the client.                                      |
| **Client Type**         | `Confidential`              | Requires a client secret for authentication.                           |
| **Access Type**         | `Bearer-Only`               | This service only accepts tokens, doesn’t authenticate users directly. |
| **Root URL**            | `https://api.example.com`   | The backend service URL.                                               |
| **Valid Redirect URIs** | `https://app.example.com/*` | Allowed URLs for redirection after authentication.                     |
| **Web Origins**         | `+`                         | Defines which web apps can call this client (CORS settings).           |


### **2️⃣ Client Roles (Authorization)**  

Roles define what **permissions** a client has. They can be **realm roles** (global) or **client roles** (specific to a client).

**👤 Example Roles for `auth-service`**

| Role Name         | Description                      | Assigned To        |
| ----------------- | -------------------------------- | ------------------ |
| `read-users`      | Can read user data               | Frontend apps      |
| `manage-users`    | Can create, update, delete users | Admin dashboard    |
| `impersonate`     | Can act as another user          | Admin-only service |
| `manage-sessions` | Can check user session details   | Auth service       |

---

### **3️⃣ Client Scopes (Token Claims)**

Scopes define what **data is included in tokens** (like user profile info, roles, etc.).

✔️ **Control token size** → Only include necessary claims.  
✔️ **Enhance security** → Restrict access to sensitive user attributes.  
✔️ **Improve flexibility** → Different clients can have different levels of access.  

There are **three types** of client scopes in Keycloak:

1. **Default Scopes**  
   - Automatically **added** to tokens unless explicitly removed.  
   - Examples: `profile`, `email`, `roles`, `web-origins`.  

2. **Optional Scopes**  
   - Must be **explicitly requested** when obtaining a token (via the `scope` parameter in the authentication request).  
   - Examples: `offline_access`, `address`, `phone`.  

3. **Dedicated Scopes** (Custom Scopes)  
   - Specific to a particular client, providing fine-grained access control.  
   - Created and mapped manually by the admin.  



**🛠️ Default & Optional Scopes**

For instance:

| Scope Name       | Type     | Description                                       |
| ---------------- | -------- | ------------------------------------------------- |
| `openid`         | Default  | Enables OpenID Connect authentication.            |
| `profile`        | Default  | Includes name, username, and other basic details. |
| `email`          | Default  | Provides access to the user’s email address.      |
| `roles`          | Default  | Adds user roles to the token.                     |
| `groups`         | Optional | Adds group membership details.                    |
| `offline_access` | Optional | Allows long-lived refresh tokens.                 |

If a client has **default scopes** `profile`, `email`, and **optional scopes** `offline_access`, a request like:

```bash
curl -X POST "http://keycloak.example.com/auth/realms/demo/protocol/openid-connect/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=my-client" \
     -d "client_secret=XXXXXX" \
     -d "grant_type=password" \
     -d "username=john" \
     -d "password=doe" \
     -d "scope=offline_access"
```

- Without specifying `scope`, the token will **only** include **default scopes** (`profile`, `email`).  
- If `scope=offline_access` is **explicitly added**, the token will include it.  


### **🔗 Example Custom Scope: `custom-claims`**

You can define a **custom scope** that includes specific attributes in the token.

Example **Group Mapper**:  
- **Name**: `member_of`
- **Claim Name**: `member_of`
- **Claim Type**: `String` (or `JSON`)
- **Source**: `Group Membership`

💡 *This will add a `"member_of": ["youwol-users"]` field in the access token.*


### **4️⃣ Token Example**

Here’s what an **Access Token** might look like after applying scopes:

```json
{
  "sub": "123456789",
  "preferred_username": "johndoe",
  "email": "johndoe@example.com",
  "realm_access": {
    "roles": ["read-users", "manage-users"]
  },
  "resource_access": {
    "auth-service": {
      "roles": ["manage-sessions"]
    }
  },
  "member_of": ["w3nest-users"]
}
```

---

## 📌 Default Clients Created by Keycloak

when you create a new **realm** in Keycloak, it automatically creates some **default clients**. 
These built-in clients provide essential functionality for managing the realm and user authentication.

**1️⃣ `account` (for User Account Management)**
- Allows users to access and manage their own profiles.
- Exposes the **Keycloak Account Console** (`/realms/{realm}/account`).
- Typically used in browser-based authentication flows.

**2️⃣ `account-console` (for User Profile UI)**
- Provides the web-based UI for users to manage their profiles.
- Linked to the `account` client.

**3️⃣ `admin-cli` (for Admin API Access)**
- Used for **programmatic access** to the Keycloak Admin API.
- Grants admin privileges via `client_credentials` grant type.
- Requires a client secret for authentication.

**4️⃣ `broker` (for Identity Brokering)**
- Used internally when federating users from external identity providers (like Google, GitHub, etc.).
- Handles authentication requests when using external identity providers.

**5️⃣ `realm-management` (for Realm Administration)**
- Provides various roles to manage the realm (`manage-users`, `view-clients`, etc.).
- Used internally when delegating realm admin permissions.

**6️⃣ `security-admin-console` (for Keycloak Admin Console)**
- Used to log in and access the **Keycloak Admin UI** (`/admin/{realm}/console`).
- Typically used with browser-based authentication.

<note level="warning" title="Should You Modify These Clients?">

- 🚫 **Do not delete them** unless you are absolutely sure.
- ✅ You **can modify roles/mappers** if needed (e.g., adding extra claims).
- 🔧 If you need a client for **custom authentication**, 
  it’s best to **create a new client** instead of modifying these.

</note>


## 📌 W3Nest Clients Configuration

The service `accounts` uses 2 keycloak clients:

*  **`oidc-token-generator`**: generates ID tokens from either: 
   *  username & password when creating guest session
   *  authentication code during authentication flow from web-browser.

*  **`admin-cli`**: required for admin tasks (create temp users, list users, etc). This is the default keycloak client
   generated when the real is created.

The K8s cluster secrets must be updated with their client secret:
*  `oidc-token-generator` maps to `openid-app-secret.openid_client_secret`
*  `admin-cli` maps to `keycloak-admin-secret.keycloak_admin_client_secret`

<note level="info" title="`oidc-token-generator`"  expandable="true">

**General Settings**

*  **Client Type** OpenID Connect
*  **Client ID** `oidc-token-generator`
*  **Always display in UI** set to `off`
*  **Description**: Client used for generating ID tokens from username/password

**Capability config**

*  **Client authentication** set to `on`
*  **Authorization** set to `off`
*  **Authentication flow**: `Standard flow`, `Direct access grants`

**Login settings**

*  Provide `Valid redirect URIs` & `Web origins` (e.g. `/*` but not to do )

Click **create**.

**Scopes**

*  Already included: `acr`, `offline_access`, `openid`
*  **Should add the `memberof` mapper**:
    *  Click `oidc-token-generator-dedicated`
    *  Already included `Client ID`, `Client Host`, `Client IP Address`
    *  Add mapper -> By configuration
    *  `Group Membership`
    *  **Token Claim Name**: `memberof`
    *  **Enable** `Full group path`, `Add to ID token`, `Add to access token`, `Add to userinfo`
*  **Should add the `upn` mapper**:
    *  Click `oidc-token-generator-dedicated`
    *  Already included `Client ID`, `Client Host`, `Client IP Address`
    *  Add mapper -> From predefined mapper -> `upn`
    *  Set `User Attribute` to `email` 
    *  **Enable** `Add to ID token`, `Add to access token`, `Add to userinfo`

</note>


<note level="warning" title="Dedicated admin client(s)">
At some point we should not use `admin-cli` but one ore more different clients for better security and granularity.
*E.g.* `accounts-backend-admin`.


<note level="info" title="`accounts-backend-admin`"  expandable="true">
Some note when migrating to dedicated client for accounts' admin tasks. 
The next configuration target the user creation for guests.

**General Settings**

*  **Client Type** OpenID Connect
*  **Client ID** `accounts-backend-admin`
*  **Always display in UI** set to `off`

**Capability config**

*  **Client authentication** set to `on`
*  **Authorization** set to `off`
*  **Authentication flow**: `Direct access grants` & `Service accounts roles`
  
**Login settings**

*  No URLs

Click **create**.

**Scopes**

*  Already included: `acr`, `offline_access`, `openid`
*  **Add `roles`**

**Service accounts roles**:
    
*  Add `manage-users`
</note>
</note>