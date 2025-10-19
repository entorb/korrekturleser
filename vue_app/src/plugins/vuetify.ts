/**
 * Vuetify plugin configuration with Material Design theme
 * Using SVG icons with tree-shaking for smaller bundle size
 */

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import type { IconSet } from 'vuetify'

// Import only the icons we use (tree-shaking for smaller bundle size)
import {
  mdiAccountOutline,
  mdiArrowLeft,
  mdiCalendar,
  mdiChartBar,
  mdiChevronLeft,
  mdiChevronRight,
  mdiClockOutline,
  mdiCloseCircle,
  mdiCog,
  mdiContentCopy,
  mdiContentPaste,
  mdiLogout,
  mdiMenuDown,
  mdiPageFirst,
  mdiPageLast,
  mdiPound,
  mdiRobot,
  mdiRobotOutline,
  mdiSend
} from '@mdi/js'
import { h } from 'vue'
import type { IconProps } from 'vuetify'

// Icon map - all icons used in the application
const iconMap: Record<string, string> = {
  'mdi-account-outline': mdiAccountOutline,
  'mdi-arrow-left': mdiArrowLeft,
  'mdi-calendar': mdiCalendar,
  'mdi-chart-bar': mdiChartBar,
  'mdi-chevron-left': mdiChevronLeft,
  'mdi-chevron-right': mdiChevronRight,
  'mdi-clock-outline': mdiClockOutline,
  'mdi-close-circle': mdiCloseCircle,
  'mdi-cog': mdiCog,
  'mdi-content-copy': mdiContentCopy,
  'mdi-content-paste': mdiContentPaste,
  'mdi-logout': mdiLogout,
  'mdi-menu-down': mdiMenuDown,
  'mdi-page-first': mdiPageFirst,
  'mdi-page-last': mdiPageLast,
  'mdi-pound': mdiPound,
  'mdi-robot': mdiRobot,
  'mdi-robot-outline': mdiRobotOutline,
  'mdi-send': mdiSend
}

// Custom SVG icon set with only the icons we need
const customSvgIconSet: IconSet = {
  component: (props: IconProps) => {
    const iconName = props.icon as string

    // Check if icon exists in our map
    if (!iconMap[iconName]) {
      console.error(
        `Icon "${iconName}" not found in icon map. Add it to vue_app/src/plugins/vuetify.ts`,
        '\nAvailable icons:',
        Object.keys(iconMap)
      )
      throw new Error(`Unknown icon: ${iconName}`)
    }

    const path = iconMap[iconName]

    return h(
      'svg',
      {
        class: 'v-icon__svg',
        xmlns: 'http://www.w3.org/2000/svg',
        viewBox: '0 0 24 24',
        role: 'img',
        'aria-hidden': 'true',
        style: {
          width: '1em',
          height: '1em',
          fill: 'currentColor'
        }
      },
      [h('path', { d: path })]
    )
  }
}

export default createVuetify({
  icons: {
    defaultSet: 'customSvg',
    sets: {
      customSvg: customSvgIconSet
    }
  }
  // theme: {
  //   defaultTheme: 'light',
  //   themes: {
  //     light: {
  //       colors: {
  //         primary: '#667eea',
  //         secondary: '#764ba2',
  //         error: '#d32f2f',
  //         info: '#2196F3',
  //         success: '#4CAF50',
  //         warning: '#FB8C00'
  //       }
  //     }
  //   }
  // }
})
