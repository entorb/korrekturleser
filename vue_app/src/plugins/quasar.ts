/**
 * Quasar plugin configuration
 */

import { Notify, Dialog, Loading } from 'quasar'
import iconSet from 'quasar/icon-set/material-icons'

// Import Quasar css
import 'quasar/dist/quasar.css'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'

export default {
  plugins: {
    Notify,
    Dialog,
    Loading
  },
  iconSet,
  config: {
    notify: {
      position: 'top' as const,
      timeout: 2500
    }
  }
}
