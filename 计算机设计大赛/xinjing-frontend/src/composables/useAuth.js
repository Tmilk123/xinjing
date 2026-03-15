import { reactive, computed } from 'vue'
import { usersDb, userProfilesDb } from '../services/db.js'

// 全局单例状态
const state = reactive({
  user:    null,   // users 表字段（不含 password_hash）
  profile: null,   // user_profiles 表字段
  token:   null,
})

// 初始化：从 localStorage 恢复登录状态
const saved = localStorage.getItem('xinjing_auth')
if (saved) {
  try {
    const parsed  = JSON.parse(saved)
    state.user    = parsed.user
    state.profile = parsed.profile
    state.token   = parsed.token
  } catch {}
}

function persist() {
  localStorage.setItem('xinjing_auth', JSON.stringify({
    user: state.user, profile: state.profile, token: state.token,
  }))
}

export function useAuth() {
  const isLoggedIn  = computed(() => !!state.token)
  const currentUser = computed(() => state.user)
  const userProfile = computed(() => state.profile)

  /** 当前用户 id */
  const userId = computed(() => state.user?.id ?? null)

  /** 显示名：优先昵称，其次用户名 */
  const displayName = computed(() =>
    state.profile?.nickname || state.user?.username || ''
  )

  // ── 登录 ──────────────────────────────────────────────
  function login(username, password) {
    const user = usersDb.authenticate(username, password)
    if (!user) return { ok: false, message: '用户名或密码错误' }

    const profile = userProfilesDb.findByUserId(user.id)
    const token   = btoa(`${username}:${Date.now()}`)

    state.user    = user
    state.profile = profile
    state.token   = token
    persist()
    return { ok: true }
  }

  // ── 注册 ──────────────────────────────────────────────
  function register({ username, password, nickname = '', email = '', phone = '',
                       gender = '', age_range = '' }) {
    try {
      const user = usersDb.create({ username, password, email, phone })
      const profile = userProfilesDb.create({
        user_id: user.id, nickname: nickname || username,
        gender, age_range,
      })
      const token = btoa(`${username}:${Date.now()}`)
      state.user    = user
      state.profile = profile
      state.token   = token
      persist()
      return { ok: true }
    } catch (e) {
      return { ok: false, message: e.message }
    }
  }

  // ── 更新档案 ───────────────────────────────────────────
  function updateProfile(fields) {
    if (!state.user) return
    const updated = userProfilesDb.update(state.user.id, fields)
    state.profile = updated
    persist()
  }

  // ── 登出 ──────────────────────────────────────────────
  function logout() {
    state.user    = null
    state.profile = null
    state.token   = null
    localStorage.removeItem('xinjing_auth')
  }

  return { isLoggedIn, currentUser, userProfile, userId, displayName,
           login, register, updateProfile, logout }
}
