/**
 * Vuetify plugin configuration with Material Design theme
 */

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
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
