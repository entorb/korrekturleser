<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTextStore } from '@/stores/text'
import { api } from '@/services/apiClient'
import { ImproveRequest } from '@/api'
import { getAvailableModes, getModeDescriptions } from '@/config/modes'
import { html } from 'diff2html'
import { createTwoFilesPatch } from 'diff'
import { marked } from 'marked'
import { copyToClipboard as copyText, readFromClipboard } from '@/utils/clipboard'
import 'diff2html/bundles/css/diff2html.min.css'

const router = useRouter()
const authStore = useAuthStore()
const textStore = useTextStore()

const isProcessing = ref(false)

// Auto-generated from ImproveRequest.mode enum
const modes = getAvailableModes()
const modeDescriptions = getModeDescriptions()

// Show diff for correct and improve modes only
const showDiff = computed(() => {
  return (
    textStore.outputText &&
    (textStore.selectedMode === ImproveRequest.mode.CORRECT ||
      textStore.selectedMode === ImproveRequest.mode.IMPROVE)
  )
})

// Show markdown rendering for summarize mode
const showMarkdown = computed(() => {
  return textStore.outputText && textStore.selectedMode === ImproveRequest.mode.SUMMARIZE
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

onMounted(() => {
  globalThis.addEventListener('keydown', handleKeyPress)
})

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
    const result = await api.text.improveTextApiPost({
      text: textStore.inputText,
      mode: textStore.selectedMode
    })

    textStore.setOutputText(result.text_ai)
    textStore.setLastResult(result)

    if (
      textStore.selectedMode === ImproveRequest.mode.CORRECT ||
      textStore.selectedMode === ImproveRequest.mode.IMPROVE
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
  } catch (err) {
    console.error('Failed to copy:', err)
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
          icon="settings"
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
                style="overflow-x: auto"
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
        </q-card-section>
      </q-card>
    </q-page>
  </q-page-container>
</template>
