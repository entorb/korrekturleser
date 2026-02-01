<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth'
import { useTextStore } from '@/stores/text'
import { api } from '@/services/apiClient'
import { TextRequest } from '@/api'
import { getAvailableModes, getModeDescriptions } from '@/config/modes'
import { html } from 'diff2html'
import { createTwoFilesPatch } from 'diff'
import { marked } from 'marked'
import { copyToClipboard as copyText, readFromClipboard } from '@/utils/clipboard'
import 'diff2html/bundles/css/diff2html.min.css'

const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()
const textStore = useTextStore()

const isProcessing = ref(false)

// Auto-generated from ImproveRequest.mode enum
const modes = getAvailableModes()
const modeDescriptions = getModeDescriptions()

// Show disclaimer for Gemini provider
const showDisclaimer = computed(() => {
  return textStore.selectedProvider === 'Gemini'
})

onMounted(async () => {
  globalThis.addEventListener('keydown', handleKeyPress)
  // Initialize providers and models
  await fetchProvidersAndModels()
})

async function fetchProvidersAndModels() {
  try {
    const response = await api.config.getConfigApiConfigGet(textStore.selectedProvider || undefined)
    textStore.setAvailableModels(response.models)
    textStore.setAvailableProviders(response.providers)
    // Set first model as default if not already set
    if (!textStore.selectedModel && response.models.length > 0) {
      textStore.setModel(response.models[0]!)
    }
    // Set first provider as default if not already set
    if (!textStore.selectedProvider && response.providers.length > 0) {
      textStore.setProvider(response.providers[0]!)
    }
  } catch (err) {
    console.error('Failed to fetch models:', err)
    textStore.setError('Fehler beim Laden der Modelle')
  }
}

// Show diff for correct and improve modes only
const showDiff = computed(() => {
  return (
    textStore.outputText &&
    (textStore.selectedMode === TextRequest.mode.CORRECT ||
      textStore.selectedMode === TextRequest.mode.IMPROVE)
  )
})

// Show markdown rendering for summarize mode
const showMarkdown = computed(() => {
  return textStore.outputText && textStore.selectedMode === TextRequest.mode.SUMMARIZE
})

// Convert markdown to HTML
const markdownHtml = computed(() => {
  if (!showMarkdown.value) return ''
  return marked(textStore.outputText)
})

function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    goToStats()
  }
}

function handleTextareaKeydown(event: KeyboardEvent) {
  if (
    event.key === 'Enter' &&
    (event.ctrlKey || event.metaKey) // ctrl+enter or command+enter
  ) {
    event.preventDefault()
    if (textStore.inputText && !isProcessing.value) {
      handleProcessText()
    }
  }
}

function generateDiff(original: string, improved: string): string {
  const patch = createTwoFilesPatch('', '', original, improved, '', '', {
    context: 3
  })

  const diffHtml = html(patch, {
    drawFileList: false,
    matching: 'words',
    outputFormat: 'side-by-side',
    renderNothingWhenEmpty: false
  })

  return diffHtml
}

onUnmounted(() => {
  globalThis.removeEventListener('keydown', handleKeyPress)
})

async function handleProcessText() {
  if (!textStore.inputText) return

  isProcessing.value = true
  textStore.setError(null)
  textStore.setOutputText('')
  textStore.setDiffHtml('')

  try {
    const result = await api.text.improveTextApiTextPost({
      text: textStore.inputText,
      mode: textStore.selectedMode,
      model: textStore.selectedModel || null,
      provider: textStore.selectedProvider || null
    })

    textStore.setOutputText(result.text_ai)
    textStore.setLastResult(result)

    if (
      textStore.selectedMode === TextRequest.mode.CORRECT ||
      textStore.selectedMode === TextRequest.mode.IMPROVE
    ) {
      const diffHtml = generateDiff(textStore.inputText + '\n\n', result.text_ai + '\n\n')
      textStore.setDiffHtml(diffHtml)
    }
  } catch (err) {
    textStore.setError(err instanceof Error ? err.message : 'Fehler bei der Textverarbeitung')
    console.error('Text processing error:', err)
  } finally {
    isProcessing.value = false
  }
}

async function handleCopyToClipboard() {
  try {
    await copyText(textStore.outputText)
    $q.notify({ type: 'positive', message: 'Kopiert!' })
  } catch {
    $q.notify({ type: 'negative', message: 'Kopieren fehlgeschlagen' })
  }
}

async function pasteFromClipboard() {
  try {
    const text = await readFromClipboard()
    textStore.setInputText(text)
  } catch (err) {
    console.error('Failed to paste:', err)
  }
}

function goToStats() {
  router.push({ name: 'stats' })
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

async function handleProviderChange() {
  // When provider changes, fetch new models for that provider
  try {
    const response = await api.config.getConfigApiConfigGet(textStore.selectedProvider || undefined)
    // Update available models from response
    textStore.setAvailableModels(response.models)
    // Reset selected model to first available model from new provider
    if (response.models.length > 0) {
      textStore.setModel(response.models[0]!)
    }
  } catch (err) {
    console.error('Failed to fetch models:', err)
    textStore.setError('Fehler beim Laden der Modelle')
  }
}
</script>

<template>
  <q-page-container>
    <q-header
      elevated
      class="bg-primary"
    >
      <q-toolbar>
        <q-toolbar-title>KI Korrekturleser</q-toolbar-title>

        <span class="q-mr-md">{{ authStore.user?.user_name }}</span>

        <q-btn
          flat
          round
          dense
          icon="bar_chart"
          @click="goToStats"
        >
          <q-tooltip>Statistik (Esc)</q-tooltip>
        </q-btn>

        <q-btn
          flat
          round
          dense
          icon="logout"
          @click="handleLogout"
        >
          <q-tooltip>Abmelden</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page class="q-pa-md">
      <!-- Google Disclaimer -->
      <q-banner
        v-if="showDisclaimer"
        class="bg-warning text-dark q-mb-md"
        rounded
      >
        <template #avatar>
          <q-icon
            name="warning"
            color="orange-9"
          />
        </template>
        Die Google Gemini KI wird deine Eingaben zum Trainieren verwenden. Nur für Texte verwenden,
        die keine persönlichen oder geheimen Daten enthalten (z.B. Namen vorher entfernen).
      </q-banner>

      <q-card>
        <q-card-section>
          <!-- Text Areas -->
          <div class="row q-col-gutter-md">
            <div :class="textStore.outputText ? 'col-6' : 'col-12'">
              <div class="row items-center justify-between q-mb-sm">
                <q-icon
                  name="account_circle"
                  size="md"
                >
                </q-icon>
                Mein Text
                <q-btn
                  flat
                  round
                  dense
                  size="sm"
                  icon="content_paste"
                  @click="pasteFromClipboard"
                >
                  <q-tooltip>Einfügen</q-tooltip>
                </q-btn>
              </div>
              <q-input
                v-model="textStore.inputText"
                type="textarea"
                placeholder="Text hier eingeben..."
                outlined
                :disable="isProcessing"
                :input-style="{ minHeight: '360px' }"
                @keydown="handleTextareaKeydown"
              />
            </div>

            <div
              v-if="textStore.outputText"
              class="col-6"
            >
              <div class="row items-center justify-between q-mb-sm">
                <q-icon
                  name="auto_fix_high"
                  size="md"
                >
                </q-icon>
                KI Text
                <q-btn
                  flat
                  round
                  dense
                  size="sm"
                  icon="content_copy"
                  @click="handleCopyToClipboard"
                >
                  <q-tooltip>Kopieren</q-tooltip>
                </q-btn>
              </div>
              <q-input
                v-if="!showMarkdown"
                v-model="textStore.outputText"
                type="textarea"
                placeholder="KI-verbesserter Text erscheint hier..."
                outlined
                :input-style="{ minHeight: '360px' }"
              />
              <q-card
                v-else
                bordered
                class="q-pa-md"
                style="min-height: 360px"
              >
                <div
                  v-html="markdownHtml"
                  class="markdown-content"
                />
              </q-card>
            </div>
          </div>

          <!-- Mode Selector and KI Button -->
          <div class="row q-col-gutter-sm q-mt-md">
            <div class="col-grow">
              <q-select
                v-model="textStore.selectedMode"
                :options="modes"
                label="Modus"
                outlined
                emit-value
                map-options
              >
                <template #option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ modeDescriptions[scope.opt] || scope.opt }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
                <template #selected>
                  {{ modeDescriptions[textStore.selectedMode] || textStore.selectedMode }}
                </template>
              </q-select>
            </div>
            <div>
              <q-btn
                round
                color="primary"
                icon="auto_fix_high"
                :loading="isProcessing"
                :disable="!textStore.inputText"
                @click="handleProcessText"
                size="lg"
              >
                <q-tooltip>KI verarbeiten</q-tooltip>
              </q-btn>
            </div>
          </div>

          <!-- Error Message -->
          <q-banner
            v-if="textStore.error"
            class="bg-negative text-white q-mt-md"
            rounded
          >
            {{ textStore.error }}
          </q-banner>

          <!-- Diff Display -->
          <q-card
            v-if="showDiff && textStore.diffHtml"
            bordered
            class="q-mt-lg"
          >
            <q-card-section>
              <div
                v-html="textStore.diffHtml"
                class="diff-container"
              />
            </q-card-section>

            <!-- Result Info -->
            <q-card-section
              v-if="textStore.lastResult"
              class="text-caption text-grey-7"
            >
              LLM: {{ textStore.lastResult.provider }} | Model: {{ textStore.lastResult.model }} |
              Tokens:
              {{ textStore.lastResult.tokens_used }}
            </q-card-section>
          </q-card>

          <!-- LLM Provider and Model Select -->
          <div class="row q-col-gutter-md q-mt-md">
            <div class="col-6">
              <q-select
                v-model="textStore.selectedProvider"
                :options="textStore.availableProviders"
                label="KI"
                outlined
                dense
                :disable="textStore.availableProviders.length === 0"
                @update:model-value="handleProviderChange"
              />
            </div>
            <div class="col-6">
              <q-select
                v-model="textStore.selectedModel"
                :options="textStore.availableModels"
                label="Modell"
                outlined
                dense
                :disable="textStore.availableModels.length === 0"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-page>
  </q-page-container>
</template>

<style>
.d2h-code-line-ctn {
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

.d2h-code-line {
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

.d2h-code-side-line {
  overflow-x: hidden !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
}
</style>
