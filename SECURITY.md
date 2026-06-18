# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| latest release | ✅ Full support |
| latest - 1 | ✅ Security fixes only |
| older | ❌ No support |

---

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Vulnerabilities disclosed publicly before a fix is available put all FLAIR users at risk.

### How to report

Use **GitHub Private Vulnerability Reporting** — available directly in each repo:

```
https://github.com/flair-security/{repo}/security/advisories/new
```

Or contact the maintainers via the organisation security email (configured in each repo's GitHub Settings → Security).

### What to include

- Affected component (`flair-agent`, `flair-core`, `flair-ui`, etc.)
- FLAIR version and platform (Linux kernel version, Windows version, Kubernetes version)
- Description of the vulnerability and its potential impact
- Steps to reproduce — as detailed as possible
- Proof of concept if available (optional but appreciated)

---

## Response timeline

| Step | Target |
|---|---|
| Acknowledgement | 48 hours |
| Initial assessment | 5 business days |
| Fix — Critical (CVSS ≥ 9.0) | 7 days |
| Fix — High (CVSS 7.0–8.9) | 30 days |
| Fix — Medium/Low | Next scheduled release |

---

## Disclosure policy

FLAIR follows **coordinated disclosure**:

1. Reporter submits via private advisory
2. Maintainers acknowledge and assess severity
3. Fix is developed on a private branch
4. Fix is released and tagged
5. Security advisory is published with CVE assignment (if applicable)
6. Reporter is credited in the advisory (unless they prefer anonymity)

We do not offer a bug bounty programme at this time.

---

## Scope

### In scope

- `flair-agent` — eBPF capture logic, capabilities handling, local buffer
- `flair-agent-windows` — ETW capture bypass, privilege escalation via Npcap
- `flair-agent-k8s` — sidecar privilege escalation, Kubernetes API access abuse
- `flair-core` — REST API, authentication (OIDC, mTLS), agent enrollment, flow storage
- `flair-ui` — XSS, authentication bypass, data exposure in the browser
- `flair-helm` — insecure default values, privilege escalation via chart config
- `flair-rules` — malicious rule injection leading to incorrect scoring

### Out of scope

- Vulnerabilities in third-party dependencies (report to the upstream project — we track via Dependabot)
- Issues requiring physical access to the host machine
- Social engineering attacks
- Denial of service via resource exhaustion (known limitation of self-hosted tools)
- Issues in the local dev environment (`docker-compose.dev.yml`) — not intended for production

---

## Security design principles

FLAIR is built with these security properties by design:

- **No `--tls-verify=false`** anywhere in the codebase — enforced by Semgrep in CI
- **mTLS between agents and flair-core** — mutual certificate authentication, TLS 1.3 minimum
- **OIDC for human authentication** — no username/password stored in flair-core
- **Non-root agents** — `CAP_NET_ADMIN` and `CAP_SYS_PTRACE` only, documented in Helm chart
- **Audit logs** — every state-changing action produces a structured JSON log entry
- **Flow data retention** — configurable via admin UI, never hardcoded
- **SBOM generated on every release** — software bill of materials available in GitHub Releases

---

## Known limitations

- eBPF on Docker Desktop (Windows/Mac) captures flows inside the Docker VM, not the host OS — expected behaviour, not a vulnerability
- TLS 1.2 support is configurable for environments that cannot upgrade — TLS 1.3 is strongly recommended and the default
- JA3 fingerprinting is computed from the first packet only — encrypted tunnels inside TLS are not inspected
