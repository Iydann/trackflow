import { ref } from 'vue'

const user = ref(null)
const callbacks = []

const auth = {
  user,
  onUserChange: null,

  login: (name) => {
    user.value = { name }
    if (auth.onUserChange) auth.onUserChange(user.value)
    callbacks.forEach((cb) => cb(user.value))
  },

  logout: () => {
    user.value = null
    if (auth.onUserChange) auth.onUserChange(null)
    callbacks.forEach((cb) => cb(null))
  },

  subscribe: (callback) => {
    callbacks.push(callback)
    return () => {
      const idx = callbacks.indexOf(callback)
      if (idx > -1) callbacks.splice(idx, 1)
    }
  }
}

export default auth
