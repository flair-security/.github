# CLAUDE.md — flair-ui

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Angular 20+ (standalone, zoneless), TypeScript 5.8+, D3.js v7, Tailwind CSS 4, Node.js 22 LTS  
**Role**: Web UI — network topology visualisation, alert dashboard, rule management, audit trail  
**Licence**: BSL-1.1

---

## Build & test commands

```bash
# Install
npm ci

# Dev server
npm start

# Production build
npm run build

# Unit tests (Jest + Angular Testing Library)
npm test
npm run test:watch

# E2E tests (Playwright)
npx playwright test
npx playwright test --ui     # interactive mode
npx playwright test e2e/us-*.spec.ts   # specific US

# Lint
npm run lint
npm run lint:fix

# Type check
npx tsc --noEmit
```

---

## Repo structure

```
flair-ui/
  src/
    app/
      core/             ← singleton services, guards, interceptors
      shared/           ← reusable components, pipes, directives
      features/
        topology/       ← D3.js network graph, force simulation
        alerts/         ← alert list, detail panel
        rules/          ← rule editor, live preview
        audit/          ← audit trail viewer
        settings/       ← OIDC config, agent list
      layout/           ← shell, nav, sidebar
    environments/       ← environment.ts / environment.prod.ts
    assets/
  e2e/                  ← Playwright specs (per US)
```

---

## Key services owned

```typescript
@Injectable({ providedIn: 'root' })
export class FlairApiService {
  getTopology(filter: TopologyFilter): Observable<Graph>
  getAlerts(page: PageParams): Observable<Page<Alert>>
  acknowledgeAlert(id: string): Observable<void>
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  login(): void               // redirect to OIDC
  logout(): void
  currentUser$: Observable<User | null>
  hasRole(role: string): boolean
}

@Injectable({ providedIn: 'root' })
export class TopologyService {
  renderGraph(container: ElementRef, data: Graph): D3Simulation
  highlightPath(pathId: string): void
}
```

---

## TypeScript rules (strict)

- No `any` — use `unknown` and narrow
- No `!` non-null assertion — use optional chaining or explicit null check
- Standalone components only — no NgModules
- Signals are primary state management — BehaviorSubject only for cross-component streams
- Template control flow: `@if`, `@for`, `@switch` (not `*ngIf`/`*ngFor`)
- Zoneless Angular: `bootstrapApplication` with `provideExperimentalZonelessChangeDetection()`
- Observables from services — signals inside components

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-angular-security | all US |
| 1 (always) | skill-ac-traceability | all US |
| 2 | skill-ux-ui-design | visual / UX changes |
| 2 | skill-api-design | API shape changes |
| 3 | skill-devops-cicd | CI / Docker changes |

---

## Repo-specific rules

- CSP header enforced in nginx config — no `unsafe-inline` scripts
- All API calls go through `FlairApiService` — no raw `HttpClient` in components
- D3.js mutations go through `TopologyService` — no D3 in components directly
- Every new route has a `CanActivate` guard checking `AuthService.hasRole()`
- Playwright tests use `data-testid` attributes — no CSS class selectors
