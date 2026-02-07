import tsPlugin from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import pluginCypress from 'eslint-plugin-cypress'
import pluginImport from 'eslint-plugin-import'
import sonarjs from 'eslint-plugin-sonarjs'
import pluginVitest from 'eslint-plugin-vitest'
import pluginVue from 'eslint-plugin-vue'
import pluginVueA11y from 'eslint-plugin-vuejs-accessibility'
import globals from 'globals'

export default [
  // Global ignores
  {
    ignores: [
      '**/*.d.ts',
      '**/.cache',
      '**/.pnpm',
      '**/.vite',
      '**/coverage',
      '**/cypress/downloads',
      '**/cypress/screenshots',
      '**/cypress/videos',
      '**/dist',
      '**/node_modules',
      '**/pnpm-lock.yaml',
      '**/public',
      '.venv',
      'scripts/**',
      'vue_app/src/api/*'
    ]
  },

  // Base TypeScript files
  {
    files: ['**/*.{ts,mts,tsx}'],
    ignores: ['**/*.{test,spec}.{ts,tsx}', '**/cypress/**'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      import: pluginImport,
      sonarjs
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      ...(sonarjs.configs?.recommended &&
      typeof sonarjs.configs.recommended === 'object' &&
      'rules' in sonarjs.configs.recommended
        ? sonarjs.configs.recommended.rules
        : {}),
      // Type safety
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'separate-type-imports' }
      ],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'typeLike',
          format: ['PascalCase']
        },
        {
          selector: 'interface',
          format: ['PascalCase'],
          custom: {
            regex: '^I[A-Z]',
            match: false
          }
        }
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      // Code quality
      '@typescript-eslint/array-type': ['error', { default: 'array-simple' }],
      '@typescript-eslint/consistent-type-definitions': ['error', 'interface'],
      // Import organization
      'import/first': 'error',
      'import/newline-after-import': 'error',
      'import/no-cycle': 'error',
      'import/no-duplicates': 'error',
      'import/no-self-import': 'error',
      'import/no-useless-path-segments': 'error',
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          pathGroups: [
            {
              pattern: '@/**',
              group: 'internal'
            }
          ],
          alphabetize: {
            order: 'asc',
            caseInsensitive: true
          },
          'newlines-between': 'always'
        }
      ],
      // General best practices
      'array-callback-return': 'error',
      eqeqeq: ['error', 'always', { null: 'ignore' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-constructor-return': 'error',
      'no-debugger': 'warn',
      'no-else-return': ['error', { allowElseIf: false }],
      'no-lonely-if': 'error',
      'no-promise-executor-return': 'error',
      'no-var': 'error',
      'object-shorthand': ['error', 'always'],
      'prefer-arrow-callback': 'error',
      'prefer-const': 'error',
      'prefer-destructuring': [
        'warn',
        {
          array: false,
          object: true
        }
      ],
      'prefer-template': 'warn',
      'require-atomic-updates': 'error',
      // SonarJS
      'sonarjs/cognitive-complexity': ['warn', 20],
      'sonarjs/no-duplicate-string': ['warn', { threshold: 4 }],
      'sonarjs/no-identical-functions': 'warn',
      'sonarjs/pseudo-random': 'off',
      'sonarjs/slow-regex': 'error',
      'sonarjs/todo-tag': 'warn'
    }
  },

  // TypeScript files with type-aware linting (requires tsconfig project)
  {
    files: ['vue_app/src/**/*.{ts,mts,tsx}', '*.config.{ts,mts}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: ['./tsconfig.app.json', './tsconfig.node.json']
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin
    },
    rules: {
      // Type-aware rules (require parserOptions.project)
      '@typescript-eslint/consistent-type-exports': [
        'error',
        { fixMixedExportsWithInlineTypeSpecifier: true }
      ],
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/await-thenable': 'error',
      '@typescript-eslint/no-unnecessary-condition': 'warn',
      '@typescript-eslint/no-redundant-type-constituents': 'warn',
      '@typescript-eslint/prefer-nullish-coalescing': 'warn',
      '@typescript-eslint/prefer-optional-chain': 'error',
      '@typescript-eslint/prefer-reduce-type-parameter': 'error',
      '@typescript-eslint/prefer-return-this-type': 'error',
      '@typescript-eslint/promise-function-async': 'warn',
      '@typescript-eslint/require-array-sort-compare': ['error', { ignoreStringArrays: true }],
      '@typescript-eslint/strict-boolean-expressions': [
        'warn',
        {
          allowString: true,
          allowNumber: true,
          allowNullableObject: true
        }
      ],
      '@typescript-eslint/no-confusing-void-expression': 'error',
      '@typescript-eslint/no-unnecessary-type-assertion': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error'
    }
  },

  // Vue files - use spread syntax to properly apply Vue configs
  ...pluginVue.configs['flat/essential'],
  ...pluginVue.configs['flat/strongly-recommended'],
  ...pluginVue.configs['flat/recommended'],

  // Vue files with TypeScript support and custom rules
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue']
      },
      globals: {
        ...globals.browser
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      import: pluginImport,
      sonarjs,
      'vuejs-accessibility': pluginVueA11y
    },
    rules: {
      // TypeScript rules for Vue
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      // Import organization
      'import/first': 'error',
      'import/newline-after-import': 'error',
      'import/no-cycle': 'error',
      'import/no-duplicates': 'error',
      'import/no-self-import': 'error',
      'import/no-useless-path-segments': 'error',
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          pathGroups: [
            {
              pattern: '@/**',
              group: 'internal'
            }
          ],
          alphabetize: {
            order: 'asc',
            caseInsensitive: true
          },
          'newlines-between': 'always'
        }
      ],
      // SonarJS
      'sonarjs/cognitive-complexity': ['warn', 20],
      'sonarjs/no-duplicate-string': ['warn', { threshold: 4 }],
      'sonarjs/no-identical-functions': 'warn',
      'sonarjs/pseudo-random': 'off',
      'sonarjs/slow-regex': 'error',
      'sonarjs/todo-tag': 'warn',
      // Vue 3 Composition API best practices
      'vue/block-lang': ['error', { script: { lang: 'ts' } }],
      'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
      'vue/component-api-style': ['error', ['script-setup']],
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/component-options-name-casing': ['error', 'PascalCase'],
      'vue/custom-event-name-casing': ['error', 'camelCase'],
      'vue/define-emits-declaration': ['error', 'type-based'],
      'vue/define-macros-order': [
        'error',
        {
          order: ['defineOptions', 'defineProps', 'defineEmits', 'defineSlots']
        }
      ],
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/html-button-has-type': 'error',
      'vue/html-self-closing': [
        'error',
        {
          html: {
            void: 'always',
            normal: 'always',
            component: 'always'
          },
          svg: 'always',
          math: 'always'
        }
      ],
      'vue/multi-word-component-names': [
        'error',
        {
          ignores: ['default', 'index', 'App']
        }
      ],
      'vue/no-boolean-default': ['warn', 'default-false'],
      'vue/no-duplicate-attr-inheritance': 'error',
      'vue/no-empty-component-block': 'warn',
      'vue/no-multiple-objects-in-class': 'error',
      'vue/no-ref-object-reactivity-loss': 'error',
      'vue/no-required-prop-with-default': 'error',
      'vue/no-root-v-if': 'error',
      'vue/no-setup-props-reactivity-loss': 'error',
      'vue/no-static-inline-styles': 'off', // Allow inline styles for dynamic styling
      'vue/no-template-target-blank': 'error',
      'vue/no-this-in-before-route-enter': 'error',
      'vue/no-undef-components': [
        'warn',
        {
          ignorePatterns: ['^q-', '^router-']
        }
      ],
      'vue/no-undef-properties': 'off', // Disabled - causes false positives with auto-imports
      'vue/no-unused-emit-declarations': 'error',
      'vue/no-unused-properties': 'warn',
      'vue/no-unused-refs': 'warn',
      'vue/no-unused-vars': 'error',
      'vue/no-use-v-else-with-v-for': 'error',
      'vue/no-useless-mustaches': 'error',
      'vue/no-useless-template-attributes': 'error',
      'vue/no-useless-v-bind': 'error',
      'vue/no-v-html': 'error',
      'vue/no-v-text-v-html-on-component': 'error',
      'vue/padding-line-between-blocks': 'warn',
      'vue/prefer-define-options': 'error',
      'vue/prefer-separate-static-class': 'warn',
      'vue/prefer-true-attribute-shorthand': 'error',
      'vue/require-default-prop': 'warn',
      'vue/require-emit-validator': 'warn',
      'vue/require-explicit-slots': 'warn',
      'vue/require-macro-variable-name': [
        'error',
        {
          defineProps: 'props',
          defineEmits: 'emit',
          defineSlots: 'slots',
          useSlots: 'slots',
          useAttrs: 'attrs'
        }
      ],
      'vue/require-prop-comment': 'off',
      'vue/require-typed-ref': 'error',
      'vue/v-for-delimiter-style': ['error', 'in'],
      'vue/v-on-event-hyphenation': ['error', 'always', { autofix: true }],
      'vue/valid-define-options': 'error',
      // Accessibility
      ...pluginVueA11y.configs.recommended.rules,
      'vuejs-accessibility/no-autofocus': 'warn'
    }
  },

  // Vue files with type-aware linting
  {
    files: ['vue_app/src/**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
        project: null // Disable type-aware linting for Vue files due to tsconfig issues
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin
    },
    rules: {
      // Note: Type-aware rules disabled for Vue files
      // Enable them once tsconfig properly includes .vue files
    }
  },

  // Vue composables - relax some rules
  {
    files: ['vue_app/src/composables/**/*.ts'],
    rules: {
      'require-atomic-updates': 'off' // False positives in Vue composables with async/await
    }
  },

  // Clipboard utilities - allow deprecated execCommand (still needed for fallback)
  {
    files: ['vue_app/src/utils/clipboard.ts'],
    rules: {
      'sonarjs/deprecation': 'off' // document.execCommand is deprecated but needed for fallback
    }
  },

  // Allow v-html in TextView.vue for markdown and diff rendering (trusted content)
  {
    files: ['vue_app/src/views/TextView.vue'],
    rules: {
      'vue/no-v-html': 'off'
    }
  },

  // Generated TypeScript files - relax rules
  {
    files: [
      '**/components.d.ts',
      '**/typed-router.d.ts',
      '**/env.d.ts',
      '**/auto-imports.d.ts',
      '**/vuetify-import.d.ts',
      'vite.config.d.ts',
      'vitest.config.d.ts'
    ],
    rules: {
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/consistent-type-imports': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'off'
    }
  },

  // Config files
  {
    files: ['*.config.{js,ts,mjs,mts}', 'vite.config.*', 'vitest.config.*'],
    languageOptions: {
      globals: {
        ...globals.node
      }
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      'no-console': 'off'
    }
  },

  // Vitest test files - relaxed rules
  {
    files: ['**/*.{test,spec}.{js,ts,jsx,tsx}', 'vue_app/**/__tests__/**/*.{js,ts,jsx,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: ['./tsconfig.vitest.json']
      },
      globals: {
        ...globals.node,
        // Add Vitest globals if using globals: true in vitest.config
        afterAll: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        beforeEach: 'readonly',
        describe: 'readonly',
        expect: 'readonly',
        it: 'readonly',
        suite: 'readonly',
        test: 'readonly',
        vi: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      import: pluginImport,
      vitest: pluginVitest
    },
    rules: {
      ...pluginVitest.configs.recommended.rules,
      // Relaxed TypeScript rules for tests
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-floating-promises': 'off',
      '@typescript-eslint/no-misused-promises': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/no-unnecessary-condition': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      '@typescript-eslint/strict-boolean-expressions': 'off',
      // Relaxed import rules for tests
      'import/newline-after-import': 'off',
      'import/no-cycle': 'off',
      'import/order': 'off',
      // Relaxed code quality for tests
      'no-console': 'off',
      'prefer-template': 'off',
      // Relaxed SonarJS for tests
      'sonarjs/cognitive-complexity': 'off',
      'sonarjs/no-duplicate-string': 'off',
      'sonarjs/no-identical-functions': 'off',
      'sonarjs/slow-regex': 'off',
      'sonarjs/todo-tag': 'off',
      // Vitest-specific rules
      'vitest/consistent-test-it': ['error', { fn: 'it', withinDescribe: 'it' }],
      'vitest/expect-expect': 'warn',
      'vitest/no-disabled-tests': 'warn',
      'vitest/no-focused-tests': 'error',
      'vitest/prefer-to-be': 'error',
      'vitest/prefer-to-have-length': 'error',
      'vitest/valid-expect': 'error'
    }
  },

  // Cypress files - most relaxed rules
  {
    files: ['cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}', 'cypress/support/**/*.{js,ts,jsx,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        ...globals.browser,
        cy: 'readonly',
        Cypress: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      import: pluginImport,
      cypress: pluginCypress
    },
    rules: {
      ...pluginCypress.configs.recommended.rules,
      // Relaxed TypeScript rules for E2E tests
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/no-unused-expressions': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      '@typescript-eslint/prefer-nullish-coalescing': 'off',
      '@typescript-eslint/prefer-optional-chain': 'off',
      // Relaxed import rules for E2E tests
      'import/first': 'off',
      'import/newline-after-import': 'off',
      'import/no-cycle': 'off',
      'import/no-duplicates': 'off',
      'import/order': 'off',
      // Relaxed code quality for E2E tests
      'array-callback-return': 'off',
      'no-console': 'off',
      'no-debugger': 'off',
      'no-unused-expressions': 'off',
      'prefer-const': 'off',
      'prefer-template': 'off',
      // Relaxed SonarJS for E2E tests
      'sonarjs/cognitive-complexity': 'off',
      'sonarjs/no-duplicate-string': 'off',
      'sonarjs/no-identical-functions': 'off',
      'sonarjs/slow-regex': 'off',
      'sonarjs/todo-tag': 'off'
    }
  },

  // Apply skip formatting last (removes conflicting formatting rules)
  skipFormatting
]
