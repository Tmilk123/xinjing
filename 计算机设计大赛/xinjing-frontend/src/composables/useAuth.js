import { reactive, computed } from 'vue'
import { api } from '../services/api.js'

function hasValidUserId(user) {
  return Number.isInteger(Number(user?.id)) && Number(user.id) > 0
}

function hasValidSession(payload) {
  return !!payload?.token && hasValidUserId(payload?.user)
}

const state = reactive({
  user: null,
  profile: null,
  token: null,
})

const saved = localStorage.getItem('xinjing_auth')
if (saved) {
  try {
    const parsed = JSON.parse(saved)
    if (hasValidSession(parsed)) {
      state.user = parsed.user
      state.profile = parsed.profile
      state.token = parsed.token
    } else {
      localStorage.removeItem('xinjing_auth')
    }
  } catch {
    localStorage.removeItem('xinjing_auth')
  }
}

function persist() {
  localStorage.setItem(
    'xinjing_auth',
    JSON.stringify({
      user: state.user,
      profile: state.profile,
      token: state.token,
    })
  )
}

export function useAuth() {
  const isLoggedIn = computed(() => !!state.token && hasValidUserId(state.user))
  const currentUser = computed(() => state.user)
  const userProfile = computed(() => state.profile)
  const userId = computed(() => (hasValidUserId(state.user) ? Number(state.user.id) : null))
  const displayName = computed(() => state.profile?.nickname || state.user?.username || '')

  async function login(username, password) {
    try {
      const data = await api.post('/auth/login', { username, password })
      state.token = data.access_token
      state.user = data.user

      // api.get() reads token from localStorage, persist first.
      persist()

      try {
        state.profile = await api.get(`/users/${data.user.id}/profile`)
      } catch {
        state.profile = null
      }

      persist()
      return { ok: true }
    } catch (e) {
      return { ok: false, message: e.message }
    }
  }

  async function register({
    username,
    password,
    nickname = '',
    email = '',
    phone = '',
    gender = '',
    age_range = '',
  }) {
    try {
      await api.post('/auth/register', { username, password, nickname, email, phone, gender, age_range })
      return await login(username, password)
    } catch (e) {
      return { ok: false, message: e.message }
    }
  }

  async function updateProfile(fields) {
    if (!state.user) return
    try {
      const updated = await api.put(`/users/${state.user.id}/profile`, fields)
      state.profile = updated
      persist()
    } catch (e) {
      console.error('updateProfile failed:', e)
    }
  }

  function logout() {
    state.user = null
    state.profile = null
    state.token = null
    localStorage.removeItem('xinjing_auth')
  }

  return {
    isLoggedIn,
    currentUser,
    userProfile,
    userId,
    displayName,
    login,
    register,
    updateProfile,
    logout,
  }
}
