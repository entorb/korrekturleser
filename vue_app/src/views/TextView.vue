<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { TextRequest } from '@/api'
import { useClipboard } from '@/composables/useClipboard'
import { useConfig } from '@/composables/useConfig'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'
import { useMarkdown } from '@/composables/useMarkdown'
import { useTextProcessing } from '@/composables/useTextProcessing'
import { getAvailableModes, getModeDescriptions } from '@/config/modes'
import { useAuthStore } from '@/stores/auth'
import { useTextStore } from '@/stores/text'
import 'diff2html/bundles/css/diff2html.min.css'

const router = useRouter()
const authStore = useAuthStore()
const textStore = useTextStore()

const modes = getAvailableModes()
const modeDescriptions = getModeDescriptions()

const { isProcessing, showDiff, showMarkdown, processText, transferAiTextToInput, resetInput } =
  useTextProcessing()

const { showDisclaimer, fetchProvidersAndModels, handleProviderChange } = useConfig()

const { handleTextareaKeydown } = useKeyboardShortcuts({
  onEscape: () => router.push({ name: 'stats' }),
  onCtrlEnter: processText
})

const { copyToClipboard, pasteFromClipboard } = useClipboard()
const { markdownHtml } = useMarkdown(() => textStore.outputText, showMarkdown)

const canSubmit = computed(
  () =>
    !!textStore.inputText &&
    !isProcessing.value &&
    (textStore.selectedMode !== TextRequest.mode.CUSTOM || !!textStore.customInstruction)
)

onMounted(() => fetchProvidersAndModels())

async function handleCopyToClipboard() {
  await copyToClipboard(textStore.outputText)
}

async function handlePasteFromClipboard() {
  const text = await pasteFromClipboard()
  if (text) {
    textStore.inputText = text
  }
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
          icon="bar_chart"
          @click="router.push({ name: 'stats' })"
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
            <!-- User Input -->
            <div :class="textStore.outputText ? 'col-6' : 'col-12'">
              <div class="row items-center justify-between q-mb-sm">
                <q-icon
                  name="account_circle"
                  size="md"
                >
                </q-icon>
                Mein Text
                <q-btn
                  color="primary"
                  dense
                  icon="delete"
                  round
                  size="sm"
                  @click="resetInput"
                >
                  <q-tooltip>Empty</q-tooltip>
                </q-btn>

                <q-btn
                  color="primary"
                  dense
                  icon="arrow_downward"
                  round
                  size="sm"
                  @click="handlePasteFromClipboard"
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
                @keydown="(e: KeyboardEvent) => handleTextareaKeydown(e, canSubmit)"
              />
            </div>

            <!-- AI Output -->
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
                  color="primary"
                  dense
                  icon="turn_left"
                  round
                  size="sm"
                  @click="transferAiTextToInput"
                >
                  <q-tooltip>Übertragen</q-tooltip>
                </q-btn>
                <q-btn
                  color="primary"
                  dense
                  icon="arrow_upward"
                  round
                  size="sm"
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
                  class="markdown-content"
                  v-html="markdownHtml"
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
              <q-input
                v-if="textStore.selectedMode === 'custom'"
                v-model="textStore.customInstruction"
                label="Anweisung"
                placeholder="Deine Anweisung..."
                outlined
                class="q-mt-sm"
                @keydown="(e: KeyboardEvent) => handleTextareaKeydown(e, canSubmit)"
              />
            </div>
            <div>
              <q-btn
                round
                color="primary"
                icon="auto_fix_high"
                :loading="isProcessing"
                :disable="!textStore.inputText"
                size="lg"
                @click="processText"
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
                class="diff-container"
                v-html="textStore.diffHtml"
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
/* Diff container optimization */
.diff-container {
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  font-size: 12px;
}

/* Code lines: full width and proper wrapping */
.diff-container .d2h-code-side-line {
  width: 100% !important;
  max-width: 100% !important;
  padding: 2px 4px !important;
  overflow-x: hidden !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
}

/* Table cells: full width */
.diff-container .d2h-code-side-line td {
  width: 100% !important;
}

/* Text wrapping for code content */
.d2h-code-line-ctn,
.d2h-code-line {
  white-space: pre-wrap !important;
  word-break: break-all !important;
}
</style>
