<script setup>
import { ref, computed, nextTick } from 'vue'

// ─── 聊天 ──────────────────────────────────────────────────
const messages = ref([
  {
    role: 'assistant',
    text: '你好呀～我是心镜的数字陪伴助手。今天感觉怎么样？可以跟我说说最近的状态，或者直接点下面的今日任务开始哦 💙',
    time: '10:00',
  }
])
const input = ref('')
const loading = ref(false)
const chatRef = ref(null)

const botResponses = {
  '我感觉还好':     '很开心听到你感觉还好！保持这种平和的状态很重要。今天有什么让你感到愉快的事情吗？',
  '最近压力很大':   '我理解，压力大的时候真的很难受。能跟我说说，是什么事情让你压力最大呢？我在认真听。',
  '睡眠不好':       '睡眠不好会让整个人都很疲惫。我可以给你分享一些帮助入睡的方法，你愿意试试吗？',
  '心情比较低落':   '谢谢你愿意告诉我。心情低落的时候，不必独自承受。能说说是什么让你感到低落吗？',
  '想聊聊心事':     '当然，我在这里，随时都在。请放心，这里是一个安全的空间，你可以说任何想说的话。',
}

async function sendMessage(text) {
  if (!text?.trim() || loading.value) return
  const t = text.trim()
  messages.value.push({
    role: 'user', text: t,
    time: new Date().toLocaleTimeString('zh', { hour: '2-digit', minute: '2-digit' }),
  })
  input.value = ''
  loading.value = true
  await nextTick(); scrollToBottom()
  await new Promise(r => setTimeout(r, 1200))
  const reply = botResponses[t] || '我听到了，谢谢你愿意分享。能多说一点吗？我想更了解你的感受。'
  messages.value.push({
    role: 'assistant', text: reply,
    time: new Date().toLocaleTimeString('zh', { hour: '2-digit', minute: '2-digit' }),
  })
  loading.value = false
  await nextTick(); scrollToBottom()
  // 在回复后推荐今日任务
  showTask.value = true
}

function scrollToBottom() {
  if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
}

const quickReplies = ['我感觉还好', '最近压力很大', '睡眠不好', '心情比较低落', '想聊聊心事']

// ─── 近况描述任务 ──────────────────────────────────────────
const taskStarted = ref(false)
const showTask = ref(false)
const taskRecording = ref(false)
const taskTime = ref(0)
let taskTimer = null

function startTask() {
  taskStarted.value = true
  taskRecording.value = true
  taskTime.value = 0
  taskTimer = setInterval(() => {
    taskTime.value++
    if (taskTime.value >= 60) endTask()
  }, 1000)
}
function endTask() {
  clearInterval(taskTimer)
  taskRecording.value = false
  sendMessage('我刚完成了今日近况描述，分享了最近一件印象深刻的事情。')
}
const fmtTask = t => `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`

// ─── 推荐任务卡 ────────────────────────────────────────────
const recommendedTasks = [
  { icon: '🧠', title: '今日认知重构', desc: '识别并挑战一个消极想法，用更平衡的视角重新看待它', tag: '认知行为', color: 'bg-blue-50 border-blue-100' },
  { icon: '🧘', title: '5分钟正念冥想', desc: '闭眼、放松、专注呼吸，跟随引导音频进入平静状态', tag: '正念减压', color: 'bg-purple-50 border-purple-100' },
  { icon: '✍️', title: '感恩日记', desc: '写下今天三件让你感到感激的小事，培养积极视角', tag: '情绪记录', color: 'bg-amber-50 border-amber-100' },
]

// ─── 干预工具 ──────────────────────────────────────────────
const activeIntervention = ref(null)
const breathingPhase = ref('')
let breathingInterval = null

const interventions = [
  { icon: '🫁', title: '呼吸放松', desc: '4-7-8 呼吸法', color: 'bg-blue-50', action: 'breathing' },
  { icon: '🧘', title: '正念减压', desc: '5分钟冥想', color: 'bg-green-50', action: 'mindfulness' },
  { icon: '📔', title: '情绪记录', desc: '写下感受', color: 'bg-amber-50', action: 'journal' },
  { icon: '🌙', title: '睡前安抚', desc: '助眠音效', color: 'bg-purple-50', action: 'sleep' },
]

function handleIntervention(action) {
  if (action === 'breathing') {
    activeIntervention.value = 'breathing'
    let phase = 0
    const phases = ['🫁 吸气 4秒', '⏸ 屏住 7秒', '💨 呼气 8秒']
    breathingPhase.value = phases[0]
    breathingInterval = setInterval(() => {
      phase = (phase + 1) % 3
      breathingPhase.value = phases[phase]
    }, 4000)
  } else {
    activeIntervention.value = action
  }
}
function stopIntervention() {
  activeIntervention.value = null
  clearInterval(breathingInterval)
  breathingPhase.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-hero-gradient">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <div class="text-center mb-7">
        <h1 class="text-3xl font-bold text-gray-800 mb-1">情绪陪伴</h1>
        <p class="text-gray-400 text-sm">数字人 AI 陪伴 · 随时倾听 · 守护心理健康</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[1fr_240px] gap-5">

        <!-- ─ 中间：数字人 + 对话 ──────────────────────── -->
        <div class="bg-white rounded-3xl shadow-card flex flex-col overflow-hidden" style="height: 720px">

          <!-- 数字人区域 -->
          <div class="relative bg-gradient-to-b from-warm-pink to-white pt-5 pb-3 px-5 border-b border-gray-100">
            <div class="flex items-end justify-center gap-4">
              <!-- 数字人主体 -->
              <div class="relative">
                <!-- 光晕 -->
                <div class="absolute inset-0 rounded-full blur-2xl opacity-30 bg-pink-300"></div>
                <!-- 头像主体 -->
                <div class="relative w-20 h-20 rounded-full bg-gradient-to-br from-primary to-teal-brand flex items-center justify-center shadow-lg border-4 border-white">
                  <span class="text-3xl">🤖</span>
                </div>
                <!-- 在线状态 -->
                <span class="absolute bottom-1 right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></span>
              </div>
              <!-- 信息 -->
              <div class="pb-2">
                <div class="font-bold text-gray-800">心镜数字陪伴</div>
                <div class="text-xs text-green-500 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 bg-green-400 rounded-full inline-block"></span> 在线 · AI 陪伴模式
                </div>
              </div>
            </div>

            <!-- 今日任务引导 -->
            <div v-if="!taskStarted" class="mt-3 bg-amber-50 border border-amber-100 rounded-xl p-3 flex items-center gap-3">
              <span class="text-2xl">🎯</span>
              <div class="flex-1">
                <div class="text-xs font-bold text-amber-700">今日近况描述任务</div>
                <div class="text-xs text-amber-600">用1分钟讲述最近一件印象深刻的事，帮助系统更好地了解你</div>
              </div>
              <button class="text-xs bg-amber-400 text-white px-3 py-1.5 rounded-full font-medium hover:bg-amber-500 flex-shrink-0" @click="startTask">
                开始
              </button>
            </div>

            <!-- 录制进行中 -->
            <div v-else-if="taskRecording" class="mt-3 bg-red-50 border border-red-100 rounded-xl p-3 flex items-center gap-3">
              <span class="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse flex-shrink-0"></span>
              <div class="flex-1">
                <div class="text-xs font-bold text-red-700">正在采集近况描述...</div>
                <div class="text-xs text-red-500">请自然说话，系统正在分析声学特征</div>
              </div>
              <span class="font-mono text-red-600 font-bold flex-shrink-0">{{ fmtTask(taskTime) }}</span>
              <button class="text-xs bg-red-500 text-white px-3 py-1.5 rounded-full font-medium" @click="endTask">完成</button>
            </div>
          </div>

          <!-- 消息气泡区 -->
          <div ref="chatRef" class="flex-1 overflow-y-auto p-5 space-y-4">
            <div
              v-for="(msg, i) in messages" :key="i"
              class="flex gap-3"
              :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
            >
              <!-- 头像 -->
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 mt-0.5"
                :class="msg.role === 'assistant' ? 'bg-gradient-to-br from-primary to-teal-brand' : 'bg-gray-200'"
              >
                <span>{{ msg.role === 'assistant' ? '🤖' : '👤' }}</span>
              </div>
              <!-- 气泡 -->
              <div :class="msg.role === 'user' ? 'items-end' : 'items-start'" class="flex flex-col gap-1 max-w-xs lg:max-w-md">
                <div
                  class="px-4 py-3 rounded-2xl text-sm leading-relaxed"
                  :class="msg.role === 'user'
                    ? 'bg-primary text-white rounded-tr-sm'
                    : 'bg-warm-cream text-gray-700 rounded-tl-sm border border-warm-pink'"
                >{{ msg.text }}</div>
                <div class="text-[10px] text-gray-400 px-1">{{ msg.time }}</div>
              </div>
            </div>

            <!-- 打字指示 -->
            <div v-if="loading" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-teal-brand flex items-center justify-center text-sm">🤖</div>
              <div class="bg-warm-cream rounded-2xl rounded-tl-sm px-4 py-3 border border-warm-pink">
                <div class="flex gap-1.5 items-center">
                  <div v-for="j in 3" :key="j" class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" :style="{ animationDelay: j * 0.15 + 's' }"></div>
                </div>
              </div>
            </div>

            <!-- 推荐任务（对话后显示） -->
            <div v-if="showTask && messages.length >= 3" class="bg-blue-50 rounded-2xl p-4 border border-blue-100">
              <div class="text-xs font-bold text-primary mb-2">💡 根据你的状态，今日推荐</div>
              <div class="space-y-2">
                <div
                  v-for="task in recommendedTasks" :key="task.title"
                  class="flex items-center gap-3 p-2.5 bg-white rounded-xl border cursor-pointer hover:shadow-sm transition-all"
                  :class="task.color"
                  @click="sendMessage(`我想尝试「${task.title}」练习`)"
                >
                  <span class="text-lg">{{ task.icon }}</span>
                  <div class="flex-1">
                    <div class="text-xs font-bold text-gray-700">{{ task.title }}</div>
                    <div class="text-[10px] text-gray-400 line-clamp-1">{{ task.desc }}</div>
                  </div>
                  <span class="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full flex-shrink-0">{{ task.tag }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 快速回复 -->
          <div class="px-5 pb-2">
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="reply in quickReplies" :key="reply"
                class="text-xs bg-warm-pink text-primary px-3 py-1.5 rounded-full hover:bg-primary hover:text-white transition-colors border border-warm-pink"
                @click="sendMessage(reply)"
              >{{ reply }}</button>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="p-4 border-t border-gray-100">
            <div class="flex gap-2 items-end">
              <textarea
                v-model="input"
                class="flex-1 border border-gray-200 rounded-2xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:border-primary transition-colors bg-warm-cream"
                rows="1"
                placeholder="输入消息，或选择上方快捷回复..."
                @keydown.enter.exact.prevent="sendMessage(input)"
              ></textarea>
              <button
                class="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-teal-brand flex items-center justify-center text-white hover:opacity-90 transition-opacity flex-shrink-0"
                @click="sendMessage(input)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- ─ 右侧：干预工具 + 任务 ─────────────────────── -->
        <div class="space-y-4">

          <!-- 干预工具 -->
          <div class="bg-white rounded-2xl shadow-card p-4">
            <h3 class="font-bold text-gray-800 text-sm mb-3">情绪干预训练</h3>

            <!-- 呼吸练习 -->
            <div v-if="activeIntervention === 'breathing'" class="text-center py-4">
              <div class="relative w-20 h-20 mx-auto mb-3">
                <div class="absolute inset-0 rounded-full bg-primary/20 animate-ping"></div>
                <div class="relative w-20 h-20 rounded-full bg-gradient-to-br from-primary to-teal-brand flex items-center justify-center text-white text-xs font-bold text-center leading-tight px-2">
                  {{ breathingPhase }}
                </div>
              </div>
              <p class="text-xs text-gray-500 mb-2">4-7-8 呼吸放松练习</p>
              <button class="text-xs text-gray-400 hover:text-gray-600 underline" @click="stopIntervention">停止练习</button>
            </div>

            <div v-else-if="activeIntervention === 'mindfulness'" class="text-center py-3">
              <div class="text-4xl mb-2">🧘</div>
              <p class="text-xs text-gray-600 mb-2 leading-relaxed">闭上眼睛，放松身体<br/>专注于当下的呼吸...</p>
              <button class="text-xs text-gray-400 hover:text-gray-600 underline" @click="stopIntervention">结束冥想</button>
            </div>

            <div v-else-if="activeIntervention === 'journal'" class="space-y-2">
              <textarea class="w-full border border-gray-200 rounded-xl p-2.5 text-xs resize-none focus:outline-none focus:border-primary bg-warm-cream" rows="4" placeholder="写下你今天的感受..."></textarea>
              <div class="flex gap-2">
                <button class="flex-1 text-xs py-2 btn-primary" @click="stopIntervention">保存</button>
                <button class="text-xs py-2 px-3 btn-outline" @click="stopIntervention">取消</button>
              </div>
            </div>

            <div v-else-if="activeIntervention === 'sleep'" class="text-center py-3">
              <div class="text-4xl mb-2 animate-pulse">🌙</div>
              <p class="text-xs text-gray-600 mb-2">播放睡前引导音频...</p>
              <div class="flex items-center gap-2 bg-gray-50 rounded-xl p-2.5 mb-2">
                <button class="w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center text-xs">▶</button>
                <div class="flex-1 h-1.5 bg-gray-200 rounded-full">
                  <div class="h-1.5 bg-primary rounded-full w-1/3"></div>
                </div>
                <span class="text-[10px] text-gray-400">3:21</span>
              </div>
              <button class="text-xs text-gray-400 hover:text-gray-600 underline" @click="stopIntervention">停止</button>
            </div>

            <div v-else class="grid grid-cols-2 gap-2">
              <button
                v-for="item in interventions" :key="item.action"
                class="p-3 rounded-xl text-left hover:shadow-sm transition-all duration-200"
                :class="item.color"
                @click="handleIntervention(item.action)"
              >
                <div class="text-xl mb-1">{{ item.icon }}</div>
                <div class="font-semibold text-xs text-gray-700">{{ item.title }}</div>
                <div class="text-[10px] text-gray-500 mt-0.5">{{ item.desc }}</div>
              </button>
            </div>
          </div>

          <!-- 今日推荐任务（右侧静态版） -->
          <div class="bg-white rounded-2xl shadow-card p-4">
            <h3 class="font-bold text-gray-800 text-sm mb-3">今日康复任务</h3>
            <div class="space-y-2">
              <div
                v-for="task in recommendedTasks" :key="task.title"
                class="p-3 rounded-xl border cursor-pointer hover:shadow-sm transition-all"
                :class="task.color"
                @click="sendMessage(`我想了解「${task.title}」怎么做`)"
              >
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-base">{{ task.icon }}</span>
                  <span class="text-xs font-bold text-gray-700">{{ task.title }}</span>
                  <span class="ml-auto text-[10px] text-gray-400">{{ task.tag }}</span>
                </div>
                <p class="text-[10px] text-gray-500 leading-relaxed">{{ task.desc }}</p>
              </div>
            </div>

            <!-- 参考平台 -->
            <div class="mt-3 pt-3 border-t border-gray-50">
              <div class="text-[10px] text-gray-400 mb-1.5">📚 参考循证方法</div>
              <div class="flex flex-wrap gap-1">
                <span class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">MoodGym CBT</span>
                <span class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">暂停实验室</span>
                <span class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">MBSR 正念</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-1 { overflow: hidden; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
</style>
