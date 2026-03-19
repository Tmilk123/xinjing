<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../services/api.js'

const mounted = ref(false)
const loading = ref(false)
const loadError = ref('')
const records = ref([])

const maxVal = 27
const chartWidth = 500
const chartHeight = 160

function formatDateText(value) {
  if (!value) return '--'
  const text = String(value)
  if (text.length >= 10) return text.slice(0, 10)
  const parsed = new Date(text)
  if (!Number.isNaN(parsed.getTime())) {
    const y = parsed.getFullYear()
    const m = String(parsed.getMonth() + 1).padStart(2, '0')
    const d = String(parsed.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  return text
}

function toTypeCode(value) {
  const text = String(value || '').toLowerCase()
  if (text.includes('phq')) return 'phq9'
  if (text.includes('sds')) return 'sds'
  if (text.includes('ais')) return 'ais'
  if (text.includes('pss')) return 'pss'
  return text || 'unknown'
}

function toScaleLabel(typeCode, fallback) {
  if (fallback) return String(fallback)
  if (typeCode === 'phq9') return 'PHQ-9'
  if (typeCode === 'sds') return 'SDS'
  if (typeCode === 'ais') return 'AIS'
  if (typeCode === 'pss') return 'PSS'
  return 'Assessment'
}

function textClassByColor(color) {
  if (color === '#22c55e') return 'text-green-500'
  if (color === '#eab308') return 'text-yellow-500'
  if (color === '#f97316') return 'text-orange-500'
  if (color === '#ef4444' || color === '#dc2626') return 'text-red-500'
  return 'text-blue-500'
}

function bgClassByColor(color) {
  if (color === '#22c55e') return 'bg-green-50'
  if (color === '#eab308') return 'bg-yellow-50'
  if (color === '#f97316') return 'bg-orange-50'
  if (color === '#ef4444' || color === '#dc2626') return 'bg-red-50'
  return 'bg-blue-50'
}

function moodByScore(score) {
  if (score <= 4) return '🙂'
  if (score <= 9) return '😐'
  if (score <= 14) return '😟'
  return '😢'
}

function toRecord(row) {
  const info = row?.report_json || {}
  const typeCode = toTypeCode(info.type || row.report_type)
  const score = Number(info.total ?? 0)
  const safeScore = Number.isFinite(score) ? score : 0
  const color = typeof info.color === 'string' && info.color ? info.color : '#3B9EE8'
  const level = typeof info.level === 'string' && info.level ? info.level : 'Unrated'
  const confidence = Number(info.confidence_score)
  const tags = []
  if (typeof info.desc === 'string' && info.desc.trim()) tags.push(info.desc.trim().slice(0, 18))
  if (Number.isFinite(confidence)) tags.push(`Confidence ${Math.round(confidence * 100)}%`)
  if (!tags.length) tags.push('DB record')

  return {
    id: row.id,
    sessionId: row.session_id,
    date: formatDateText(info.date || row.created_at),
    createdAtTs: Date.parse(row.created_at || info.date || '') || Date.now(),
    typeCode,
    type: toScaleLabel(typeCode, info.scale),
    score: safeScore,
    level,
    color,
    levelColor: `${textClassByColor(color)} ${bgClassByColor(color)}`,
    mood: moodByScore(safeScore),
    tags,
  }
}

async function loadRecordsFromDb() {
  loading.value = true
  loadError.value = ''
  try {
    const rows = await api.get('/reports?limit=200')
    records.value = (rows || [])
      .map(toRecord)
      .sort((a, b) => b.createdAtTs - a.createdAtTs)
  } catch (err) {
    loadError.value = err?.message || 'Failed to load assessment data'
    records.value = []
    console.error('loadRecordsFromDb failed:', err)
  } finally {
    loading.value = false
  }
}

const totalAssessments = computed(() => records.value.length)
const thisMonthAssessments = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()
  return records.value.filter((r) => {
    const d = new Date(r.createdAtTs)
    return d.getFullYear() === y && d.getMonth() === m
  }).length
})

const latestRecord = computed(() => records.value[0] || null)
const currentLevel = computed(() => latestRecord.value?.level || 'N/A')
const currentLevelClass = computed(() => textClassByColor(latestRecord.value?.color))
const currentLevelTrend = computed(() => {
  const latest = latestRecord.value
  if (!latest) return 'No assessment record'
  const sameType = records.value.filter((r) => r.typeCode === latest.typeCode)
  if (sameType.length < 2) return 'No comparison data'
  const prev = sameType[1]
  if (latest.score < prev.score) return 'Improved from last time'
  if (latest.score > prev.score) return 'Worse than last time'
  return 'Same as last time'
})
const currentLevelTrendClass = computed(() => {
  if (currentLevelTrend.value.includes('Improved')) return 'text-green-500'
  if (currentLevelTrend.value.includes('Worse')) return 'text-orange-500'
  return 'text-gray-400'
})

const latestPhqRecord = computed(() => records.value.find((r) => r.typeCode === 'phq9') || null)
const latestPhqScore = computed(() => (latestPhqRecord.value ? latestPhqRecord.value.score : '--'))
const latestPhqDashArray = computed(() => {
  const score = latestPhqRecord.value?.score ?? 0
  const circ = 113
  const ratio = Math.max(0, Math.min(score / maxVal, 1))
  return `${(circ * ratio).toFixed(0)} ${circ}`
})
const phqDeltaText = computed(() => {
  const phqRows = records.value.filter((r) => r.typeCode === 'phq9')
  if (phqRows.length < 2) return 'No comparison data'
  const delta = phqRows[0].score - phqRows[1].score
  if (delta < 0) return `↓ ${Math.abs(delta)} points lower`
  if (delta > 0) return `↑ ${delta} points higher`
  return '= no change'
})
const phqDeltaClass = computed(() => {
  if (phqDeltaText.value.includes('lower')) return 'text-green-500'
  if (phqDeltaText.value.includes('higher')) return 'text-orange-500'
  return 'text-gray-400'
})

const totalAssessmentsDashArray = computed(() => {
  const circ = 113
  const ratio = Math.max(0, Math.min(totalAssessments.value / 12, 1))
  return `${(circ * ratio).toFixed(0)} ${circ}`
})

const trendRecords = computed(() =>
  records.value
    .filter((r) => r.typeCode === 'phq9')
    .slice()
    .sort((a, b) => a.createdAtTs - b.createdAtTs)
    .slice(-6)
)

const trendData = computed(() => trendRecords.value.map((r) => r.score))
const trendDates = computed(() => trendRecords.value.map((r) => r.date.slice(5)))

function scoreToY(score) {
  return chartHeight - (score / maxVal) * chartHeight
}

const trendPoints = computed(() => {
  const values = trendData.value
  if (!values.length) return []
  const step = values.length > 1 ? chartWidth / (values.length - 1) : 0
  return values.map((score, idx) => ({
    x: Number((idx * step).toFixed(2)),
    y: Number(scoreToY(score).toFixed(2)),
    value: score,
  }))
})

const trendPointsAttr = computed(() => trendPoints.value.map((p) => `${p.x},${p.y}`).join(' '))

const svgFill = computed(() => {
  if (!trendPoints.value.length) return ''
  const first = trendPoints.value[0]
  const lines = trendPoints.value.slice(1).map((p) => `L${p.x},${p.y}`).join(' ')
  return `M${first.x},${first.y} ${lines} L${chartWidth},${chartHeight} L0,${chartHeight} Z`
})

const latestTrendPoint = computed(() => trendPoints.value[trendPoints.value.length - 1] || null)

onMounted(async () => {
  setTimeout(() => { mounted.value = true }, 200)
  await loadRecordsFromDb()
})

// ─── 雷达图（中心 150,150 半径 88�?───────────────────────────
const RADAR_N  = 5
const RADAR_CX = 150
const RADAR_CY = 150
const RADAR_R  = 88

const radarDims = [
  { label: 'Emotion', value: 72, color: '#3B9EE8', icon: '🙂', desc: 'Emotional stability' },
  { label: 'Sleep', value: 58, color: '#2EC4B6', icon: '🌙', desc: 'Sleep and recovery' },
  { label: 'Social', value: 81, color: '#4ade80', icon: '👥', desc: 'Social engagement' },
  { label: 'Stress', value: 55, color: '#F5873A', icon: '🧠', desc: 'Stress resilience' },
  { label: 'Cognition', value: 68, color: '#a78bfa', icon: '📚', desc: 'Attention and clarity' },
]

function polyStr(scale) {
  return Array.from({ length: RADAR_N }, (_, i) => {
    const a = ((-90 + i * 360 / RADAR_N) * Math.PI) / 180
    return `${(RADAR_CX + RADAR_R * scale * Math.cos(a)).toFixed(1)},${(RADAR_CY + RADAR_R * scale * Math.sin(a)).toFixed(1)}`
  }).join(' ')
}

const radarDataPoints = computed(() =>
  radarDims.map((d, i) => {
    const a = ((-90 + i * 360 / RADAR_N) * Math.PI) / 180
    const s = d.value / 100
    return {
      ...d,
      cx:  (RADAR_CX + RADAR_R * s * Math.cos(a)).toFixed(1),
      cy:  (RADAR_CY + RADAR_R * s * Math.sin(a)).toFixed(1),
      ax:  (RADAR_CX + RADAR_R * Math.cos(a)).toFixed(1),
      ay:  (RADAR_CY + RADAR_R * Math.sin(a)).toFixed(1),
      bx:  (RADAR_CX + RADAR_R * 1.22 * Math.cos(a)).toFixed(1),
      by:  (RADAR_CY + RADAR_R * 1.22 * Math.sin(a)).toFixed(1),
      lx:  (RADAR_CX + RADAR_R * 1.47 * Math.cos(a)).toFixed(1),
      ly:  (RADAR_CY + RADAR_R * 1.47 * Math.sin(a)).toFixed(1),
    }
  })
)

// ─── AI 暖心结语 ─────────────────────────────────────────────
const aiRemarks = [
  { text: 'You are continuously tracking your mental state. That consistency is valuable.', tag: 'Consistency', tagColor: 'text-blue-500' },
  { text: 'Fluctuation is normal. Keep recording and observe the long-term trend.', tag: 'Growth', tagColor: 'text-teal-600' },
  { text: 'When score rises, start with sleep routine and low-pressure social activity.', tag: 'Action', tagColor: 'text-orange-500' },
]
const remarkIdx = ref(Math.floor(Math.random() * aiRemarks.length))

// ─── 综合评分 ────────────────────────────────────────────────
const overallScore = computed(() => Math.round(radarDims.reduce((s, d) => s + d.value, 0) / radarDims.length))
const overallLevel = computed(() => {
  const s = overallScore.value
  if (s >= 75) return { label: 'Good', color: '#4ade80', bg: '#f0fdf4', desc: 'Dimensions are balanced' }
  if (s >= 55) return { label: 'Stable', color: '#3B9EE8', bg: '#eff6ff', desc: 'Still has room to improve' }
  return { label: 'Needs Attention', color: '#F5873A', bg: '#fff7ed', desc: 'Adjustment is recommended' }
})
</script>

<template>
  <div class="min-h-screen" style="background: linear-gradient(160deg, #F0F7FF 0%, #FFF5FB 50%, #F0FFF8 100%)">
    <div class="max-w-7xl mx-auto px-6 py-10">

      <!-- ── 页头 ───────────────────────────────────────────── -->
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
        <div>
          <h1 class="text-3xl font-black text-gray-800 mb-1">数据分析</h1>
          <p class="text-gray-400 text-sm">追踪情绪变化趋势，了解您的心理健康状态</p>
        </div>
        <div class="flex items-center gap-3 px-5 py-3 rounded-2xl border bg-white/80 backdrop-blur shadow-sm border-white">
          <div class="w-3 h-3 rounded-full animate-pulse" :style="{background: overallLevel.color}"></div>
          <span class="text-sm font-semibold text-gray-700">综合状态：</span>
          <span class="text-sm font-bold" :style="{color: overallLevel.color}">{{ overallLevel.label }}</span>
          <span class="text-xs text-gray-400">{{ overallLevel.desc }}</span>
        </div>
      </div>

      <!-- ── 汇总卡�?─────────────────────────────────────── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
        <!-- 累计测评 -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-white/80 flex items-center gap-4">
          <div class="relative w-14 h-14 flex-shrink-0">
            <svg viewBox="0 0 44 44" class="w-14 h-14 -rotate-90">
              <circle cx="22" cy="22" r="18" fill="none" stroke="#e5e7eb" stroke-width="3.5"/>
              <circle cx="22" cy="22" r="18" fill="none" stroke="#3B9EE8" stroke-width="3.5"
                stroke-linecap="round"
                :stroke-dasharray="mounted ? totalAssessmentsDashArray : '0 113'"
                class="transition-all duration-1000"/>
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-lg font-black text-primary">{{ totalAssessments }}</span>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-700 leading-tight">累计测评次数</div>
            <div class="text-xs text-green-500 mt-0.5 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
              本月 {{ thisMonthAssessments }} 次            </div>
          </div>
        </div>
        <!-- 当前等级 -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-white/80 flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-yellow-50 border border-yellow-100 flex flex-col items-center justify-center flex-shrink-0">
            <span class="text-xl">⚡</span>
          </div>
          <div>
            <div class="text-xl font-black leading-tight" :class="currentLevelClass">{{ currentLevel }}</div>
            <div class="text-xs text-gray-400">当前风险等级</div>
            <div class="text-xs mt-0.5" :class="currentLevelTrendClass">{{ currentLevelTrend }}</div>
          </div>
        </div>
        <!-- PHQ-9 分数 -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-white/80 flex items-center gap-4">
          <div class="relative w-14 h-14 flex-shrink-0">
            <svg viewBox="0 0 44 44" class="w-14 h-14 -rotate-90">
              <circle cx="22" cy="22" r="18" fill="none" stroke="#e5e7eb" stroke-width="3.5"/>
              <circle cx="22" cy="22" r="18" fill="none" stroke="#2EC4B6" stroke-width="3.5"
                stroke-linecap="round"
                :stroke-dasharray="mounted ? latestPhqDashArray : '0 113'"
                class="transition-all duration-1000 delay-200"/>
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-base font-black text-teal-brand">{{ latestPhqScore }}</span>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-700 leading-tight">最近 PHQ-9</div>
            <div class="text-xs text-gray-400">满分 27 分</div>
            <div class="text-xs mt-0.5" :class="phqDeltaClass">{{ phqDeltaText }}</div>
          </div>
        </div>
        <!-- 持续关注 -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-white/80 flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-orange-50 border border-orange-100 flex flex-col items-center justify-center flex-shrink-0">
            <span class="text-xl">🔥</span>
          </div>
          <div>
            <div class="text-xl font-black text-orange-brand leading-tight">21天</div>
            <div class="text-xs text-gray-400">持续关注天数</div>
            <div class="text-xs text-primary mt-0.5">继续保持</div>
          </div>
        </div>
      </div>

      <!-- ── 趋势 + 雷达 ─────────────────────────────────── -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-7">

        <!-- PHQ-9 趋势折线 -->
        <div class="lg:col-span-3 bg-white rounded-3xl shadow-sm border border-white/80 p-6">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="font-bold text-gray-800">PHQ-9 趋势追踪</h3>
              <p class="text-xs text-gray-400 mt-0.5">近 6 次评估得分变化</p>
            </div>
            <div class="flex gap-1.5">
              <button class="text-xs bg-primary/10 text-primary px-3 py-1.5 rounded-full font-medium">近1月</button>
              <button class="text-xs text-gray-400 hover:text-primary px-3 py-1.5 rounded-full transition-colors">近3月</button>
            </div>
          </div>

          <div class="relative">
            <!-- Y�?-->
            <div class="absolute left-0 top-0 bottom-6 flex flex-col justify-between text-xs text-gray-300 w-8 text-right pr-1">
              <span>27</span><span>18</span><span>9</span><span>0</span>
            </div>
            <div class="ml-10 relative">
              <!-- Zone 背景�?-->
              <svg class="absolute inset-0 w-full h-40" viewBox="-10 -10 520 180" preserveAspectRatio="none">
                <rect x="-10" y="-10" width="520" height="58"  fill="#fef2f2" fill-opacity="0.5"/><!-- 重度 -->
                <rect x="-10" y="48"  width="520" height="48"  fill="#fff7ed" fill-opacity="0.5"/><!-- 中度 -->
                <rect x="-10" y="96"  width="520" height="32"  fill="#fefce8" fill-opacity="0.5"/><!-- 轻度 -->
                <rect x="-10" y="128" width="520" height="42"  fill="#f0fdf4" fill-opacity="0.5"/><!-- 正常 -->
              </svg>
              <!-- 折线�?-->
              <div class="h-40 relative">
                <svg class="w-full h-full" viewBox="-10 -10 520 180" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#3B9EE8" stop-opacity="0.3"/>
                      <stop offset="100%" stop-color="#3B9EE8" stop-opacity="0"/>
                    </linearGradient>
                  </defs>
                  <!-- 水平参考线 -->
                  <line x1="-10" y1="0"   x2="510" y2="0"   stroke="#fca5a5" stroke-width="0.5" stroke-dasharray="4 4"/>
                  <line x1="-10" y1="48"  x2="510" y2="48"  stroke="#fdba74" stroke-width="0.5" stroke-dasharray="4 4"/>
                  <line x1="-10" y1="96"  x2="510" y2="96"  stroke="#fde047" stroke-width="0.5" stroke-dasharray="4 4"/>
                  <line x1="-10" y1="128" x2="510" y2="128" stroke="#86efac" stroke-width="0.5" stroke-dasharray="4 4"/>
                  <!-- 填充�?-->
                  <path v-if="svgFill" :d="svgFill" fill="url(#lineGrad)"/>
                  <!-- 折线 -->
                  <polyline
                    v-if="trendPointsAttr"
                    :points="trendPointsAttr"
                    fill="none" stroke="#3B9EE8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <!-- 数据�?-->
                  <circle v-for="(pt,i) in trendPoints" :key="i"
                    :cx="pt.x" :cy="pt.y"
                    r="5" fill="#3B9EE8" stroke="white" stroke-width="2"/>
                  <!-- 最新值标�?-->
                  <text
                    v-if="latestTrendPoint"
                    :x="latestTrendPoint.x"
                    :y="latestTrendPoint.y - 12"
                    text-anchor="middle"
                    font-size="11"
                    fill="#3B9EE8"
                    font-weight="bold"
                  >{{ latestTrendPoint.value }}分</text>
                </svg>
                <div v-if="!trendPoints.length" class="absolute inset-0 flex items-center justify-center text-sm text-gray-400">
                  暂无 PHQ-9 趋势数据
                </div>
              </div>
              <!-- X轴日�?-->
              <div class="flex justify-between text-xs text-gray-400 mt-2">
                <span
                  v-for="(d, i) in trendDates"
                  :key="`${d}-${i}`"
                  :class="i === trendDates.length - 1 ? 'text-primary font-semibold' : ''"
                >{{ d }}</span>
              </div>
            </div>
          </div>

          <!-- 图例 -->
          <div class="flex flex-wrap gap-x-4 gap-y-1 mt-4 pt-4 border-t border-gray-50 text-xs text-gray-400">
            <span class="flex items-center gap-1.5"><span class="w-3 h-2 rounded bg-green-100 inline-block border border-green-200"></span>正常 (0-4)</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-2 rounded bg-yellow-50 inline-block border border-yellow-200"></span>轻度 (5-9)</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-2 rounded bg-orange-50 inline-block border border-orange-200"></span>中度 (10-14)</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-2 rounded bg-red-50 inline-block border border-red-200"></span>重度 (15+)</span>
          </div>
        </div>

        <!-- ── 雷达：心理健康星�?── -->
        <div class="lg:col-span-2 bg-white rounded-3xl shadow-sm border border-white/80 p-6 flex flex-col">
          <div class="mb-3">
            <h3 class="font-bold text-gray-800 flex items-center gap-2">
              <span class="text-lg">🌐</span> 心理健康星图
            </h3>
            <p class="text-xs text-gray-400 mt-0.5">五维度综合能量评估</p>
          </div>

          <!-- SVG 雷达�?-->
          <div class="flex justify-center flex-1 items-center">
            <svg viewBox="0 0 300 300" class="w-full max-w-[260px]">
              <defs>
                <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#3B9EE8" stop-opacity="0.45"/>
                  <stop offset="100%" stop-color="#2EC4B6" stop-opacity="0.1"/>
                </radialGradient>
                <linearGradient id="strokeGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#3B9EE8"/>
                  <stop offset="100%" stop-color="#2EC4B6"/>
                </linearGradient>
                <filter id="radarGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>

              <!-- 区域背景圈（外→内：橙、黄、绿�?-->
              <polygon :points="polyStr(1)"   fill="#FFF7ED" fill-opacity="0.5" stroke="#FED7AA" stroke-width="1"/>
              <polygon :points="polyStr(0.7)" fill="#FEFCE8" fill-opacity="0.6" stroke="#FDE68A" stroke-width="1"/>
              <polygon :points="polyStr(0.4)" fill="#F0FDF4" fill-opacity="0.7" stroke="#BBF7D0" stroke-width="1"/>

              <!-- 轴线 -->
              <line v-for="pt in radarDataPoints" :key="'ax'+pt.label"
                :x1="RADAR_CX" :y1="RADAR_CY" :x2="pt.ax" :y2="pt.ay"
                stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3 3"/>

              <!-- 数据多边形（带发光） -->
              <polygon
                :points="radarDataPoints.map(p=>`${p.cx},${p.cy}`).join(' ')"
                fill="url(#radarFill)"
                stroke="url(#strokeGrad)"
                stroke-width="2.5"
                stroke-linejoin="round"
                filter="url(#radarGlow)"
              />

              <!-- 数据�?+ 分值徽�?-->
              <g v-for="pt in radarDataPoints" :key="'pt'+pt.label">
                <!-- 连接线到徽章 -->
                <line :x1="pt.cx" :y1="pt.cy" :x2="pt.bx" :y2="pt.by" :stroke="pt.color" stroke-width="1" stroke-opacity="0.3"/>
                <!-- 数据圆点 -->
                <circle :cx="pt.cx" :cy="pt.cy" r="5" fill="white" :stroke="pt.color" stroke-width="2.5"/>
                <!-- 分值徽�?-->
                <circle :cx="pt.bx" :cy="pt.by" r="13" fill="white" :stroke="pt.color" stroke-width="1.5" stroke-opacity="0.7"/>
                <text :x="pt.bx" :y="pt.by" text-anchor="middle" dominant-baseline="middle" font-size="8" font-weight="bold" :fill="pt.color">{{ pt.value }}</text>
              </g>

              <!-- 维度标签 -->
              <text v-for="pt in radarDataPoints" :key="'lb'+pt.label"
                :x="pt.lx"
                :y="pt.ly"
                text-anchor="middle" dominant-baseline="middle"
                font-size="10" fill="#4b5563" font-family="PingFang SC, sans-serif" font-weight="500"
              >{{ pt.label }}</text>

              <!-- 中心综合评分 -->
              <circle cx="150" cy="150" r="20" fill="white" stroke="#e5e7eb" stroke-width="1.5"/>
              <text x="150" y="146" text-anchor="middle" font-size="14" font-weight="900" fill="#3B9EE8" font-family="PingFang SC, sans-serif">{{ overallScore }}</text>
              <text x="150" y="159" text-anchor="middle" font-size="7" fill="#9ca3af" font-family="PingFang SC, sans-serif">综合</text>
            </svg>
          </div>
        </div>
      </div>

      <!-- ── 心理能量地图 ─────────────────────────────────── -->
      <div class="bg-white rounded-3xl shadow-sm border border-white/80 p-6 mb-7">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="font-bold text-gray-800 flex items-center gap-2">
              <span class="text-lg">🗺️</span> 心理能量地图
            </h3>
            <p class="text-xs text-gray-400 mt-0.5">各维度当前能量状态 · 点击可查看详情</p>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-400">
            <span class="w-2.5 h-2.5 rounded-full bg-green-300 inline-block"></span>充足
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-300 inline-block ml-2"></span>一般            <span class="w-2.5 h-2.5 rounded-full bg-orange-300 inline-block ml-2"></span>偏低
          </div>
        </div>

        <!-- 5个能量柱（移动端2+2+1，桌�?列） -->
        <div class="grid grid-cols-5 gap-4">
          <div
            v-for="(dim, i) in radarDims" :key="dim.label"
            class="flex flex-col items-center group cursor-default"
          >
            <!-- 能量柱容�?-->
            <div class="w-full aspect-[3/4] relative rounded-2xl overflow-hidden mb-3"
                 :style="`background: ${dim.color}12; border: 1.5px solid ${dim.color}25`">

              <!-- 分区背景（低/�?高） -->
              <div class="absolute inset-0 flex flex-col">
                <div class="flex-1" :style="`background: ${dim.color}05`"></div><!-- 高区 -->
                <div class="h-[40%]" :style="`background: ${dim.color}08`"></div><!-- 中区 -->
                <div class="h-[30%]" :style="`background: ${dim.color}0A`"></div><!-- 低区 -->
              </div>

              <!-- 能量填充（从底部升起�?-->
              <div
                class="absolute bottom-0 left-0 right-0 rounded-b-2xl transition-all duration-1000"
                :style="{
                  height: mounted ? dim.value + '%' : '0%',
                  transitionDelay: (i * 100) + 'ms',
                  background: `linear-gradient(to top, ${dim.color}, ${dim.color}60)`,
                }"
              >
                <!-- 顶部光泽 -->
                <div class="absolute top-0 left-0 right-0 h-3 rounded-t-lg opacity-50"
                     :style="`background: linear-gradient(to bottom, white, transparent)`"></div>
                <!-- 液面涟漪效果 -->
                <div class="absolute top-0 left-0 right-0 h-1.5"
                     :style="`background: ${dim.color}; border-radius: 50% 50% 0 0 / 100% 100% 0 0`"></div>
              </div>

              <!-- 图标（居中浮于液面） -->
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-2xl drop-shadow-sm select-none">{{ dim.icon }}</span>
              </div>

              <!-- 分值标注（右上角） -->
              <div class="absolute top-2 right-2 text-[11px] font-black px-1.5 py-0.5 rounded-lg bg-white/80"
                   :style="`color: ${dim.color}`">{{ dim.value }}</div>

              <!-- 刻度�?-->
              <div class="absolute left-1.5 right-1.5 border-t border-dashed border-white/40" :style="{bottom: '70%'}"></div>
              <div class="absolute left-1.5 right-1.5 border-t border-dashed border-white/40" :style="{bottom: '40%'}"></div>
            </div>

            <!-- 维度标签 -->
            <div class="text-center">
              <div class="text-xs font-semibold text-gray-700 leading-snug">{{ dim.label }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5 leading-tight">{{ dim.desc }}</div>
              <!-- 能量级别 -->
              <div class="mt-1.5 text-[10px] font-medium px-2 py-0.5 rounded-full"
                   :style="`background: ${dim.color}15; color: ${dim.color}`">
                {{ dim.value >= 70 ? '高' : dim.value >= 50 ? '中' : '低' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 底部总结 -->
        <div class="mt-6 pt-5 border-t border-gray-50 flex flex-wrap gap-3 items-center">
          <span class="text-xs text-gray-500">综合能量：</span>
          <div class="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-1000 delay-500"
              :style="`width: ${mounted ? overallScore : 0}%; background: linear-gradient(to right, #3B9EE8, #2EC4B6, #4ade80)`"
            ></div>
          </div>
          <span class="text-xs font-bold text-primary">{{ overallScore }}/100</span>
          <span class="text-xs px-2.5 py-1 rounded-full font-medium" :style="`background: ${overallLevel.bg}; color: ${overallLevel.color}`">{{ overallLevel.label }}</span>
        </div>
      </div>

      <!-- ── 历史评估记录 ─────────────────────────────────── -->
      <div class="bg-white rounded-3xl shadow-sm border border-white/80 p-6 mb-7">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-bold text-gray-800 flex items-center gap-2"><span class="text-lg">📋</span> 历史评估记录</h3>
          <RouterLink to="/screening" class="text-sm text-primary font-medium hover:underline no-underline flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            新建评估
          </RouterLink>
        </div>

        <div v-if="loading" class="py-10 text-center text-sm text-gray-400">正在加载历史评估记录...</div>
        <div v-else-if="loadError" class="py-10 text-center text-sm text-red-400">{{ loadError }}</div>
        <div v-else-if="!records.length" class="py-10 text-center text-sm text-gray-400">暂无历史评估记录</div>
        <div v-else class="space-y-3">
          <div v-for="r in records" :key="r.id"
               class="flex items-center gap-4 p-4 rounded-2xl border border-gray-50 hover:border-primary/15 hover:bg-blue-50/30 transition-all duration-200 group">
            <!-- 情绪 + 日期 -->
            <div class="flex-shrink-0 text-center w-16">
              <div class="text-2xl mb-0.5">{{ r.mood }}</div>
              <div class="text-[10px] text-gray-400 leading-tight">{{ r.date.slice(5) }}</div>
            </div>
            <!-- 分隔�?-->
            <div class="w-px h-10 bg-gray-100 flex-shrink-0"></div>
            <!-- 信息 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <span class="text-sm font-bold text-gray-800">{{ r.type }}</span>
                <span class="text-sm font-black" :class="r.score >= 10 ? 'text-orange-500' : r.score >= 5 ? 'text-yellow-500' : 'text-green-500'">{{ r.score }}分</span>
                <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="r.levelColor">{{ r.level }}</span>
              </div>
              <div class="flex flex-wrap gap-1">
                <span v-for="tag in r.tags" :key="tag" class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{{ tag }}</span>
              </div>
            </div>
            <!-- 操作 -->
            <RouterLink :to="`/report/${r.id}`"
              class="flex-shrink-0 text-xs text-primary border border-primary/20 px-3 py-1.5 rounded-xl hover:bg-primary/5 transition-colors no-underline opacity-0 group-hover:opacity-100">
              查看报告 →            </RouterLink>
          </div>
        </div>
      </div>

      <!-- ── AI 暖心结语 ─────────────────────────────────── -->
      <div class="relative rounded-3xl overflow-hidden" style="background: linear-gradient(135deg, #EFF6FF 0%, #FFF5FB 50%, #F0FDF9 100%); border: 1px solid #DBEAFE;">
        <!-- 装饰性背�?-->
        <div class="absolute top-0 right-0 w-64 h-64 rounded-full bg-gradient-to-br from-primary/5 to-teal-brand/5 -translate-y-1/2 translate-x-1/2"></div>
        <div class="absolute bottom-0 left-0 w-40 h-40 rounded-full bg-rose-soft/10 translate-y-1/2 -translate-x-1/2"></div>
        <div class="absolute top-4 right-12 text-5xl opacity-8 select-none">💙</div>
        <div class="absolute bottom-4 left-16 text-4xl opacity-8 select-none">🌸</div>

        <div class="relative p-7">
          <!-- 头部 -->
          <div class="flex items-center gap-3 mb-5">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-teal-brand flex items-center justify-center text-2xl shadow-md">🤖</div>
            <div>
              <div class="font-bold text-gray-800 flex items-center gap-2">
                心镜 · AI 暖心结语
                <span class="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">每日更新</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                      :class="aiRemarks[remarkIdx].tagColor.replace('text-', 'bg-').replace('-500','-100').replace('-600','100') + ' ' + aiRemarks[remarkIdx].tagColor">
                  # {{ aiRemarks[remarkIdx].tag }}
                </span>
              </div>
              <p class="text-xs text-gray-400 mt-0.5">基于您的近期数据生成</p>
            </div>
          </div>

          <!-- 结语文字 -->
          <div class="bg-white/60 backdrop-blur rounded-2xl px-6 py-5 mb-5 border border-white">
            <p class="text-gray-700 leading-relaxed text-[15px]">{{ aiRemarks[remarkIdx].text }}</p>
          </div>

          <!-- 操作�?-->
          <div class="flex items-center gap-3">
            <button
              class="text-sm text-gray-500 border border-gray-200 bg-white/70 px-4 py-2 rounded-xl hover:bg-white hover:text-primary hover:border-primary/30 transition-all flex items-center gap-2"
              @click="remarkIdx = (remarkIdx + 1) % aiRemarks.length"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              换一条            </button>
            <RouterLink to="/companion" class="text-sm bg-gradient-to-r from-primary to-teal-brand text-white px-5 py-2 rounded-xl hover:opacity-90 transition-opacity no-underline flex items-center gap-2 shadow-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
              与心镜对话            </RouterLink>
            <div class="ml-auto text-xs text-gray-400 flex items-center gap-1.5">
              <span v-for="(_, j) in aiRemarks" :key="j"
                class="w-1.5 h-1.5 rounded-full transition-colors duration-200"
                :class="j === remarkIdx ? 'bg-primary' : 'bg-gray-200'"
              ></span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.no-underline { text-decoration: none; }
</style>


