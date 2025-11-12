<template>
  <aside
    :style="{ width: sidebarWidth, transition: 'width 220ms cubic-bezier(.2,.9,.2,1)' }"
    :class="[collapsed ? 'p-2 min-w-[64px]' : 'p-4 min-w-[280px]', 'flex flex-col bg-gray-100 border-r', 'sticky top-[72px] self-start h-[calc(100vh-72px)]']"
  >
  <nav class="flex flex-col gap-2 mt-1">
      <Button
        v-for="(item, index) in navigationItems"
        :key="index"
        variant="ghost"
        @click="navigate(item.path)"
        :class="[ 'flex items-center gap-3 w-full text-left rounded-md', collapsed ? 'justify-center py-3' : 'px-3 py-2', isActive(item.path) ? 'bg-white font-bold' : 'hover:bg-white/60' ]"
      >
        <component :is="item.icon" class="w-5 h-5 text-gray-600" />
        <span v-if="!collapsed" class="flex-1 text-gray-700">{{ item.label }}</span>
      </Button>
    </nav>

    <!-- Dev-cuma buat seed data, ntar dihapus -->
    <div v-if="isDev && !collapsed" class="mt-3 flex flex-col gap-1">
      <button @click="clearAllData" class="text-xs text-red-500 hover:underline text-left font-semibold">Clear All Data</button>
      <button @click="seedDummy" class="text-xs text-gray-500 hover:underline text-left">Test add demo Process items</button>
      <button @click="seedHistoryDummy" class="text-xs text-gray-500 hover:underline text-left">Test add demo History items</button>
    </div>

  <ScrollArea class="flex-1 overflow-auto mt-3">
      <div>
        <h2 v-if="!collapsed" class="text-sm font-bold text-gray-500 mb-2">Process</h2>

        <div class="mt-0">
          <div v-for="item in processItems" :key="item.id" class="relative group">
            <div class="w-full transition-all duration-150 rounded-md" :class="isActive(item.path) ? 'bg-white font-bold' : 'group-hover:bg-white/60 group-hover:translate-x-1'">
              <Button
                variant="ghost"
                @click="navigate(item.path)"
                :class="[ 'flex items-center gap-3 w-full text-left rounded-md transition-all duration-150', collapsed ? 'py-3 justify-center' : 'px-3 py-2' ]"
              >
                <component is="BarChart3Icon" class="w-5 h-5 text-gray-600 transition-transform duration-150 group-hover:scale-110" />
                <span v-if="!collapsed" class="flex-1 text-gray-700">{{ item.name }}</span>
              </Button>
            </div>
          </div>
        </div>

        <h2 v-if="!collapsed" class="text-sm font-bold text-gray-500 mt-4">History</h2>

        <div class="mt-2 space-y-1">
          <div
            v-for="h in historyItems"
            :key="h.id"
            class="relative"
          >
            <div class="flex items-center gap-3 rounded-md" :class="collapsed ? 'justify-center' : ''">
              <Button
                variant="ghost"
                @click="navigate(h.path)"
                :class="[ 'flex-1 text-left rounded-md', collapsed ? 'py-3 justify-center' : 'px-3 py-2', isActive(h.path) ? 'bg-white font-bold' : 'hover:bg-white/60' ]"
              >
                <component is="BarChart3Icon" class="w-5 h-5 text-gray-600" />
                <span v-if="!collapsed" class="flex-1 text-gray-700 truncate">{{ h.name }}</span>
              </Button>

              <!-- three-dot menu (hidden when collapsed) -->
              <button
                v-if="!collapsed"
                @click.stop="toggleHistoryMenu(h.id, $event)"
                class="ml-2 p-1 rounded hover:bg-gray-100 text-gray-500 history-menu-button"
                aria-haspopup="true"
                :aria-expanded="openHistoryMenuId === h.id"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zm6 0a2 2 0 11-4 0 2 2 0 014 0zM18 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </button>
            </div>

            <!-- dropdown menu -->
            <div v-if="openHistoryMenuId === h.id" ref="menuRef" class="absolute right-0 mt-1 z-50 w-44 bg-white border rounded-md shadow-lg overflow-hidden sidebar-history-menu">
              <button @click="shareHistory(h)" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Bagikan</button>
              <button @click="downloadHistory(h)" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Unduh laporan</button>
              <div class="border-t" />
              <button @click="deleteHistory(h)" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Hapus</button>
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>

    <Button variant="ghost" @click="collapsed = !collapsed" :class="[ 'flex items-center gap-3 w-full text-left rounded-md px-3 py-2', collapsed ? 'justify-center' : '' ]">
      <component is="ChevronLeftIcon" :class="{ 'transform rotate-180': collapsed }" class="w-5 h-5 text-gray-600" />
      <span v-if="!collapsed" class="flex-1 text-gray-700">Collapse</span>
    </Button>
    <div class="w-full h-4" />
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from './Button.vue'
import ScrollArea from './ScrollArea.vue'
import { HomeIcon, UploadIcon, UserIcon, BarChart3Icon, ChevronLeftIcon } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const processItems = ref([])
const historyItems = ref([])

const isDev = import.meta.env?.DEV === true

const navigationItems = [
  { icon: HomeIcon, label: 'Home', path: '/' },
  { icon: UploadIcon, label: 'Upload video', path: '/upload' },
  { icon: UserIcon, label: 'Profile', path: '/profile' }
]

const sidebarWidth = computed(() => (collapsed.value ? '64px' : '280px'))

const isActive = (path) => route.path === path

const navigate = (path) => {
  router.push(path)
}

const loadProcessItems = () => {
  try {
    const raw = localStorage.getItem('trackflow_processes') || '[]'
    processItems.value = JSON.parse(raw)
  } catch {
    processItems.value = []
  }
}

const clearAllData = () => {
  if (confirm('Clear semua data Process & History?')) {
    localStorage.removeItem('trackflow_processes')
    localStorage.removeItem('trackflow_history')
    loadProcessItems()
    loadHistoryItems()
  }
}

const seedDummy = () => {
  // Create 5 demo items
  const items = Array.from({ length: 5 }, (_, i) => ({ id: i + 1, name: `Demo Process ${i + 1}`, path: `/process/${i + 1}` }))
  try {
    localStorage.setItem('trackflow_processes', JSON.stringify(items))
  } catch (e) {
    // ignore
  }
  loadProcessItems()
}

const seedHistoryDummy = () => {
  // Create 10 demo history items
  const items = Array.from({ length: 10 }, (_, i) => ({ id: i + 1, name: `History Item ${i + 1}`, path: `/history/${i + 1}` }))
  try {
    localStorage.setItem('trackflow_history', JSON.stringify(items))
  } catch (e) {
    // ignore
  }
  loadHistoryItems()
}

const handleStorageChange = (e) => {
  if (e.key === 'trackflow_processes') {
    loadProcessItems()
  }
  if (e.key === 'trackflow_history') {
    loadHistoryItems()
  }
}

const loadHistoryItems = () => {
  try {
    const raw = localStorage.getItem('trackflow_history') || '[]'
    historyItems.value = JSON.parse(raw)
  } catch {
    historyItems.value = []
  }
}

// history menu state & handlers
const openHistoryMenuId = ref(null)
const menuRef = ref(null)

const toggleHistoryMenu = (id, e) => {
  openHistoryMenuId.value = openHistoryMenuId.value === id ? null : id
}

const closeHistoryMenu = () => {
  openHistoryMenuId.value = null
}

const onDocumentClick = (e) => {
  // If click is inside a menu or on a menu button, ignore
  const el = e.target
  if (el.closest && (el.closest('.sidebar-history-menu') || el.closest('.history-menu-button'))) {
    return
  }
  closeHistoryMenu()
}

const shareHistory = async (h) => {
  const url = `${location.origin}${h.path}`
  try {
    if (navigator.share) {
      await navigator.share({ title: h.name, text: h.name, url })
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(url)
      alert('Link copied to clipboard')
    } else {
      window.prompt('Copy this link', url)
    }
  } catch (err) {
    console.error('Share failed', err)
  }
  closeHistoryMenu()
}

const downloadHistory = (h) => {
  const data = JSON.stringify(h, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `history-${h.id}.json`
  document.body.appendChild(a)
  a.click()
  a.remove()
  closeHistoryMenu()
}

const deleteHistory = (h) => {
  const ok = confirm(`Hapus history "${h.name}" ?`)
  if (!ok) return
  try {
    const raw = localStorage.getItem('trackflow_history') || '[]'
    const arr = JSON.parse(raw)
    const filtered = arr.filter((x) => String(x.id) !== String(h.id))
    localStorage.setItem('trackflow_history', JSON.stringify(filtered))
    loadHistoryItems()
  } catch (err) {
    console.error(err)
  }
  closeHistoryMenu()
}

onMounted(() => {
  loadProcessItems()
  loadHistoryItems()
  window.addEventListener('storage', handleStorageChange)
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
  document.removeEventListener('click', onDocumentClick)
})
</script>
