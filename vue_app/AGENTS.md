# Vue App - Copilot Coding Guidelines

Modern Vue 3 + TypeScript 2025 best practices. ESLint and Prettier handle formatting - this guide covers architectural decisions.

## Store Architecture (Pinia)

**Direct mutations, not setters:**

```typescript
// ✅ DO
store.inputText = 'new value'

// ❌ DON'T
function setInputText(text: string) {
  inputText.value = text
}
```

**Return minimal interface:**

```typescript
export const useTextStore = defineStore('text', () => {
  const inputText = ref('')
  const outputText = ref('')

  function clearOutput() {
    outputText.value = ''
    error.value = null
  }

  return { inputText, outputText, clearOutput }
})
```

## Error Handling

**Minimal, user-facing only:**

```typescript
// ✅ DO
try {
  const response = await api.text.improveTextApiTextPost({ text })
  textStore.outputText = response.text_ai
} catch (err) {
  textStore.error = err instanceof Error ? err.message : 'Operation failed'
}

// ❌ DON'T
console.error('Failed:', err) // No logging in catch
```

## Nullability

**Use modern operators:**

```typescript
// ✅ DO
if (token == null) return ''
options.onEscape?.()
const value = model?.trim() ?? ''

// ❌ DON'T
if (!token || token.length === 0) return '' // Over-defensive
```

## Composables

**One responsibility, focused:**

```typescript
// ✅ DO
export function useTextProcessing() {
  const textStore = useTextStore()
  const isProcessing = ref(false)

  async function processText() {
    /* ... */
  }

  return { isProcessing, processText }
}

// ❌ DON'T
function transferAiTextToInput() {
  // Too simple for helper
  textStore.inputText = textStore.outputText
}
```

## Components

**Keep views dumb, extract logic:**

```typescript
// ✅ DO
<script setup lang="ts">
const textStore = useTextStore()
const { isProcessing, processText } = useTextProcessing()

const canSubmit = computed(() => !!textStore.inputText)
</script>

// ❌ DON'T
const username = ref('')  // Unused state
async function handleLogin() {
  console.error('Login failed')  // No logging
}
```

## Code Quality

**Keep functions simple:**

- Cognitive complexity < 20
- Extract repeated strings (4+ occurrences) to constants
- Types use PascalCase, no "I" prefix

**Accessibility:**

- Buttons need `type="button"` or `type="submit"`
- Icon-only buttons need `aria-label`
- Form inputs need labels

## Key Principles

1. **Direct is better** - `store.value = x` not `store.setValue(x)`
2. **Catch only where you handle** - no empty catches
3. **Modern TypeScript** - use `==`, `?.`, `??`
4. **Views are dumb** - logic in stores/composables
5. **One way to do it** - consistency over preference

## Checklist

- [ ] Direct store mutations, no setters
- [ ] No console.error/warn in catch
- [ ] Use `??` and `?.` operators
- [ ] Error messages user-facing (German)
- [ ] Composables focused (one responsibility)
- [ ] Views minimal, logic extracted
- [ ] Buttons have `type` attribute
- [ ] Icon buttons have `aria-label`
- [ ] Run `pnpm check` before commit
