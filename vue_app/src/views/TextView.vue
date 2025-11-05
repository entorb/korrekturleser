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
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
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

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(textStore.outputText)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText()
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
  <v-app>
    <v-app-bar
      color="primary"
      prominent
    >
      <v-app-bar-title>KI Korrekturleser</v-app-bar-title>

      <v-spacer />

      <span class="mr-4">{{ authStore.user?.user_name }}</span>

      <v-btn
        icon
        @click="goToStats"
        title="Statistik (Esc)"
      >
        <v-icon>mdi-cog</v-icon>
      </v-btn>

      <v-btn
        icon
        @click="handleLogout"
        title="Abmelden"
      >
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-card>
          <v-card-text>
            <!-- Text Areas -->
            <v-row>
              <v-col :cols="textStore.outputText ? 6 : 12">
                <div class="d-flex justify-space-between align-center mb-2">
                  <v-icon
                    title="Mein Text"
                    size="large"
                    >mdi-account-outline</v-icon
                  >
                  <v-btn
                    icon
                    size="small"
                    @click="pasteFromClipboard"
                    title="Einfügen"
                  >
                    <v-icon>mdi-content-paste</v-icon>
                  </v-btn>
                </div>
                <v-textarea
                  v-model="textStore.inputText"
                  placeholder="Text hier eingeben..."
                  variant="outlined"
                  :disabled="isProcessing"
                  rows="15"
                  @keydown="handleTextareaKeydown"
                />
              </v-col>

              <v-col
                v-if="textStore.outputText"
                cols="6"
              >
                <div class="d-flex justify-space-between align-center mb-2">
                  <v-icon
                    title="KI Text"
                    size="large"
                    >mdi-robot-outline</v-icon
                  >
                  <v-btn
                    icon
                    size="small"
                    @click="copyToClipboard"
                    title="Kopieren"
                  >
                    <v-icon>mdi-content-copy</v-icon>
                  </v-btn>
                </div>
                <v-textarea
                  v-if="!showMarkdown"
                  v-model="textStore.outputText"
                  placeholder="KI-verbesserter Text erscheint hier..."
                  variant="outlined"
                  rows="15"
                />
                <v-card
                  v-else
                  variant="outlined"
                  class="pa-4"
                  style="min-height: 360px"
                >
                  <div
                    v-html="markdownHtml"
                    class="markdown-content"
                  />
                </v-card>
              </v-col>
            </v-row>

            <!-- Mode Selector and KI Button -->
            <div class="d-flex gap-2 mb-4">
              <v-select
                v-model="textStore.selectedMode"
                :items="modes"
                label="Modus"
                variant="outlined"
                class="flex-grow-1"
              >
                <template #item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="modeDescriptions[item.value] || item.value"
                  />
                </template>
                <template #selection="{ item }">
                  {{ modeDescriptions[item.value] || item.value }}
                </template>
              </v-select>
              <v-btn
                icon
                color="primary"
                :loading="isProcessing"
                :disabled="!textStore.inputText"
                @click="handleProcessText"
                title="KI verarbeiten"
                style="height: 56px; width: 56px"
              >
                <v-icon>mdi-robot</v-icon>
              </v-btn>
            </div>

            <!-- Error Message -->
            <v-alert
              v-if="textStore.error"
              type="error"
              variant="tonal"
              class="mt-4"
            >
              {{ textStore.error }}
            </v-alert>

            <!-- Diff Display -->
            <v-card
              v-if="showDiff && textStore.diffHtml"
              class="mt-6"
            >
              <v-card-text>
                <div
                  v-html="textStore.diffHtml"
                  style="overflow-x: auto"
                />
              </v-card-text>

              <!-- Result Info -->
              <div
                v-if="textStore.lastResult"
                class="text-caption text-medium-emphasis mt-2"
              >
                Modell: {{ textStore.lastResult.model }} | Token verbraucht:
                {{ textStore.lastResult.tokens_used }}
              </div>
            </v-card>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>
