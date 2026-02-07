# Vue App - Copilot Coding Guidelines

Modern Vue 3 + TypeScript 2025 best practices for this project. Follow these patterns to maintain consistency and simplicity.

## Store Architecture (Pinia)

### ✅ DO: Direct State Mutations

```typescript
export const useTextStore = defineStore('text', () => {
  const inputText = ref('')
  const outputText = ref('')

  return { inputText, outputText, clearAll }
})

// Usage
store.inputText = 'new value'
```

### ❌ DON'T: Setter Functions

```typescript
// Avoid this pattern - it's verbose and unnecessary
function setInputText(text: string) {
  inputText.value = text
}

store.setInputText('value')
```

### Store Pattern Rules

1. **Expose refs directly** - Pinia auto-unwraps them in templates
2. **Only use functions for complex operations** (clearAll, clearOutput)
3. **Return minimal interface** - only what's needed
4. **Keep computed properties** for derived state

Example:

```typescript
export const useTextStore = defineStore('text', () => {
  const selectedMode = ref<TextRequest.mode>(TextRequest.mode.CORRECT)
  const inputText = ref('')
  const outputText = ref('')
  const error = ref<string | null>(null)

  function clearOutput() {
    outputText.value = ''
    error.value = null
  }

  return { selectedMode, inputText, outputText, error, clearOutput }
})
```

## Error Handling

### ✅ DO: Minimal Error Handling

```typescript
try {
  const response = await api.text.improveTextApiTextPost({ text })
  textStore.outputText = response.text_ai
} catch (err) {
  textStore.error = err instanceof Error ? err.message : 'Operation failed'
}
```

### ❌ DON'T: Over-Catch or Log

```typescript
// Avoid logging in catch blocks - error is already captured in UI
try {
  // ...
} catch (err) {
  console.error('Failed to process:', err) // ❌ Remove this
  textStore.error = 'Failed'
}

// Avoid catching what you don't handle
try {
  const data = await fetch(url) // ❌ Unnecessary try-catch
  return data
} catch {
  // Not handling anything specific
}
```

### Error Handling Rules

1. **Catch only where you handle** - don't catch and re-throw without adding value
2. **No console.error in catch** - errors go to UI/database only
3. **Provide user-facing messages** in local language (German)
4. **Use API error response directly** when available
5. **Let framework errors bubble** - only catch business logic errors

## Type Guards & Nullability

### ✅ DO: Modern Null Checks

```typescript
// Use nullish coalescing
const token = tokenManager.get()
if (token == null) return ''

// Use optional chaining with nullish coalescing
options.onEscape?.()

// Destructure with defaults
const { exp = null } = payload ?? {}

// Inline checks
const isExpired = payload?.exp != null && payload.exp < Date.now()
```

### ❌ DON'T: Over-Engineer Type Guards

```typescript
// Avoid creating helper functions for simple checks
const hasValue = (value: string | null | undefined): value is string =>
  typeof value === 'string' && value.trim().length > 0

store.setModel(hasValue(model) ? model : null)

// Instead:
store.selectedModel = model?.trim() ?? ''
```

### Null Check Rules

1. **Use `== null`** (checks both null and undefined)
2. **Use `?.`** for optional access
3. **Use `??`** for nullish coalescing (not `||`)
4. **Avoid type guard functions** - use inline checks
5. **Check before use** - not after assignment

## Composables & Functions

### ✅ DO: Simple, Focused Composables

```typescript
export function useTextProcessing() {
  const textStore = useTextStore()
  const isProcessing = ref(false)

  const showDiff = computed(
    () =>
      textStore.outputText &&
      (textStore.selectedMode === TextRequest.mode.CORRECT ||
        textStore.selectedMode === TextRequest.mode.IMPROVE)
  )

  async function processText() {
    isProcessing.value = true
    try {
      const result = await api.text.improveTextApiTextPost(payload)
      textStore.outputText = result.text_ai
    } catch (err) {
      textStore.error = err instanceof Error ? err.message : 'Error'
    } finally {
      isProcessing.value = false
    }
  }

  return { isProcessing, showDiff, processText }
}
```

### ❌ DON'T: Over-Abstract Functions

```typescript
// Don't create helper functions for simple operations
function transferAiTextToInput() {
  textStore.inputText = textStore.outputText
  textStore.outputText = ''
}

// Do it inline in the view or composable
const handleTransfer = () => {
  textStore.inputText = textStore.outputText
  textStore.outputText = ''
}
```

### Composable Rules

1. **One responsibility per composable** - not kitchen-sink helpers
2. **Return only used values** - not the entire store
3. **Keep logic in composable** - views should be dumb
4. **Use arrow functions** where possible
5. **Minimal comments** - code should be self-explanatory

## Component Scripts (setup)

### ✅ DO: Streamlined Script Setup

```typescript
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTextStore } from '@/stores/text'

const router = useRouter()
const textStore = useTextStore()
const modes = getAvailableModes()

const canSubmit = computed(() => !!textStore.inputText)

onMounted(() => fetchProvidersAndModels())

async function handleCopyToClipboard() {
  await copyToClipboard(textStore.outputText)
}
</script>
```

### ❌ DON'T: Complex Component Logic

```typescript
// Avoid storing intermediate state
const username = ref('') // Unused dummy field
const secret = ref('')

// Avoid unnecessary wrapper functions
async function handleLogin() {
  try {
    await authStore.login(secret.value)
    await router.replace({ name: 'text' })
  } catch (error) {
    console.error('Login failed:', error) // ❌ Remove
  }
}

// Use form @submit directly instead
```

### Component Rules

1. **Import only what's used** - not entire stores/utils
2. **Extract complex logic to composables** - keep component simple
3. **No computed that stores state** - computed is read-only
4. **Direct router calls in handlers** - don't wrap unnecessarily
5. **Remove unused comments** - especially error logs

## API Client & Services

### ✅ DO: Simple API Wrapper

```typescript
// src/services/apiClient.ts
export const tokenManager = {
  get(): string | null {
    return localStorage.getItem('access_token')
  },
  set(token: string): void {
    localStorage.setItem('access_token', token)
  },
  clear(): void {
    localStorage.removeItem('access_token')
  }
}

OpenAPI.TOKEN = async () => {
  const token = tokenManager.get()
  return token != null && !isTokenExpired(token) ? token : ''
}

export const api = {
  auth: AuthenticationService,
  config: ConfigurationService,
  text: TextOperationsService,
  statistics: StatisticsService
}
```

### ❌ DON'T: Duplicated Logic

```typescript
// Don't add redundant interceptors
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      tokenManager.clear() // Already done in OpenAPI.TOKEN
      globalThis.location.replace('/login')
    }
  }
)
```

## Utility Functions

### ✅ DO: Concise Utils

```typescript
// src/utils/jwt.ts
export function decodeJwt(token: string): JwtPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3 || parts[1] == null) return null
    const decoded = atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded) as JwtPayload
  } catch {
    return null
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token)
  if (payload == null || payload.exp == null) return true
  return payload.exp * 1000 < Date.now()
}
```

### ❌ DON'T: Over-Engineered Utilities

```typescript
// Avoid defensive programming with multiple checks
if (token === null || token.length === 0) return  // ❌ Just use !token or token == null
if (typeof payload.exp !== 'number' || Number.isNaN(payload.exp))  // ❌ Redundant
```

## Router & Navigation

### ✅ DO: Simple Route Guards

```typescript
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta['requiresAuth'] !== false

  if (!authStore.isAuthenticated && tokenManager.get() != null) {
    authStore.loadUserFromToken()
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'text' })
  } else {
    next()
  }
})
```

### ❌ DON'T: Separate Navigation Functions

```typescript
function goToStats() {
  router.push({ name: 'stats' })
}

// Just call router.push directly in template:
@click="router.push({ name: 'stats' })"
```

## Testing

### ✅ DO: Direct State Access in Tests

```typescript
it('updates input text', () => {
  const store = useTextStore()
  store.inputText = 'Hello world'
  expect(store.inputText).toBe('Hello world')
})
```

### ❌ DON'T: Test Setter Methods

```typescript
// This pattern is gone
store.setInputText('Hello world')
```

## Key Principles

1. **Simplicity First** - remove abstraction layers that don't add value
2. **Convention over Configuration** - follow Vue 3 Composition API patterns
3. **Minimal Comments** - write clear code, not commented code
4. **No Defensive Programming** - catch errors where they matter
5. **Direct is Better** - prefer `store.value = x` over `store.setValue(x)`
6. **Use Modern TypeScript** - leverage `==`, `?.`, `??` operators
7. **Keep Views Dumb** - business logic goes in stores/composables
8. **One Way to Do It** - consistency matters more than personal preference

## Checklist Before Submitting Code

- [ ] Store uses direct mutations, not setters
- [ ] No console.error/warn in catch blocks
- [ ] No over-engineered type guards
- [ ] Nullish coalescing used (`??`, not `||`)
- [ ] Optional chaining used (`?.`)
- [ ] Error messages are user-facing
- [ ] No unused comments
- [ ] Composables are focused (one responsibility)
- [ ] Views are minimal and readable
- [ ] Tests use direct state access
- [ ] Imports are only what's used
- [ ] No defensive null checks before use

## Resources

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [TypeScript 5.x Handbook](https://www.typescriptlang.org/docs/)
- Project: `shared/` folder for business logic
- Project: `fastapi_app/` for backend validation patterns
